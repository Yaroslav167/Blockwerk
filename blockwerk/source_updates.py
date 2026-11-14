"""POSIX source updates. Standalone stdlib helper; never replaces personal data."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import uuid
import zipfile

MANIFEST = 'release-source.json'
PRESERVE = {'launcher-auth.json', 'update-source.json'}
DIRECTORIES = {'blockwerk', 'tools', 'tests', 'licenses', '.github'}
MAX_SOURCE = 64 * 1024 * 1024


def safe_relative(value):
    p = PurePosixPath(value)
    if (not isinstance(value, str) or '\\' in value or ':' in value or p.is_absolute()
            or '..' in p.parts or not p.parts or any(part.endswith((' ', '.')) for part in p.parts)):
        raise ValueError('Unsafe source path')
    if len(p.parts) > 1 and p.parts[0] not in DIRECTORIES:
        raise ValueError('Source archive includes a personal-data directory')
    if len(p.parts) == 1 and p.suffix not in ('.py', '.md', '.txt', '.json', '.sh', '.cmd', '.command', ''):
        raise ValueError('Unexpected source file')
    return Path(*p.parts)


def inventory(folder):
    file = folder / MANIFEST
    if file.stat().st_size > 256 * 1024:
        raise ValueError('Source manifest too large')
    data = json.loads(file.read_text(encoding='utf-8'))
    if data.get('app') != 'Blockwerk' or data.get('schema') != 1 or data.get('kind') != 'source':
        raise ValueError('Not a Blockwerk source release')
    files = data.get('files', {})
    if not isinstance(files, dict) or not files or len(files) > 4096:
        raise ValueError('Missing source inventory')
    for name, digest in files.items():
        safe_relative(name)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid source checksum')
    if not {'main.py', 'tools/bootstrap.py', 'start-linux.sh', 'start-macos.command'} <= files.keys():
        raise ValueError('Incomplete source package')
    return data


def regular_target(root, relative):
    target = root / safe_relative(relative)
    for part in [target, *target.parents]:
        if part == root:
            break
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            raise ValueError('Source update path contains a link')
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Source update escaped app folder')
    return target


def stage_source(install, package, version, digest, cancel):
    install = install.resolve()
    inventory(install)
    with package.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != digest.lower():
            raise ValueError('Update package changed after download')
    stage = install.parent / ('.Blockwerk-next-source-' + uuid.uuid4().hex)
    stage.mkdir()
    seen = set(); total = 0
    def write(name, size, reader, link=False):
        nonlocal total
        if cancel.is_set():raise InterruptedError('Source update canceled')
        path = PurePosixPath(name)
        if link or not name.startswith('Blockwerk/') or path.parts[0] != 'Blockwerk':
            raise ValueError('Unexpected source archive path')
        relative = name[len('Blockwerk/'):]
        target = stage / safe_relative(relative)
        if relative in seen or len(seen) >= 4096:raise ValueError('Duplicate or excessive files')
        seen.add(relative); total += size
        if not 0 <= size <= MAX_SOURCE or total > MAX_SOURCE:raise ValueError('Source archive too large')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('wb') as output:
            remaining = size
            while remaining:
                if cancel.is_set():raise InterruptedError('Source update canceled')
                chunk = reader.read(min(262144, remaining))
                if not chunk:raise ValueError('Incomplete source file')
                output.write(chunk); remaining -= len(chunk)
        target.chmod(0o755 if target.suffix in ('.sh', '.command') else 0o644)
    try:
        if zipfile.is_zipfile(package):
            with zipfile.ZipFile(package) as archive:
                if len(archive.infolist()) > 4096:raise ValueError('Too many files')
                for item in archive.infolist():
                    if item.is_dir():continue
                    with archive.open(item) as stream:
                        write(item.filename, item.file_size, stream, stat.S_ISLNK(item.external_attr >> 16) or bool(item.flag_bits & 1))
        else:
            with tarfile.open(package, 'r|gz') as archive:
                count = 0
                for item in archive:
                    count += 1
                    if count > 4096:raise ValueError('Too many files')
                    if item.isdir():continue
                    if not item.isfile():raise ValueError('Links and special files are forbidden')
                    with archive.extractfile(item) as stream:write(item.name, item.size, stream)
        data = inventory(stage)
        if data['version'] != version or seen != set(data['files']) | {MANIFEST}:
            raise ValueError('Source manifest and archive differ')
        for name, expected in data['files'].items():
            if hashlib.sha256((stage / name).read_bytes()).hexdigest() != expected:
                raise ValueError('Source file checksum mismatch')
        return stage
    except Exception:
        shutil.rmtree(stage)
        raise


def apply_source(job, restart=True):
    install = Path(job['install_dir']).resolve()
    stage = Path(job['stage_dir']).resolve()
    if (job.get('schema') != 1 or stage.parent != install.parent
            or not stage.name.startswith('.Blockwerk-next-source-') or stage == install):
        raise ValueError('Invalid source update job')
    old = inventory(install); new = inventory(stage)
    if new['version'] != job['version']:raise ValueError('Wrong update version')
    names = []
    for name in new['files']:
        target = regular_target(install, name)
        # Upgrade unchanged publisher defaults, while keeping operator overrides.
        if name in PRESERVE and target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != old['files'].get(name):
                continue
        names.append(name)
    names.append(MANIFEST)
    # Check everything before replacing a file. Preserve local source edits and unknown files.
    for name in names:
        target = regular_target(install, name)
        source = regular_target(stage, name)
        if name != MANIFEST and hashlib.sha256(source.read_bytes()).hexdigest() != new['files'][name]:
            raise ValueError('Staged source was modified')
        if target.exists() and name != MANIFEST:
            if name not in old['files'] or hashlib.sha256(target.read_bytes()).hexdigest() != old['files'][name]:
                raise ValueError('Local source edits detected; install manually')
    backup = install.parent / ('.Blockwerk-source-backup-' + uuid.uuid4().hex)
    backup.mkdir()
    changed = []
    try:
        for name in names:
            target = regular_target(install, name)
            existed = target.exists()
            if existed:
                saved = backup / name; saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, saved)
            target.parent.mkdir(parents=True, exist_ok=True)
            changed.append((name, existed))
            temporary = target.with_name(target.name + '.blockwerk-' + uuid.uuid4().hex + '.tmp')
            try:
                with (stage / name).open('rb') as source, temporary.open('xb') as output:
                    shutil.copyfileobj(source, output)
                temporary.chmod((stage / name).stat().st_mode & 0o777)
                temporary.replace(target)
            finally:temporary.unlink(missing_ok=True)
        if restart:
            script = 'start-macos.command' if job['platform'] == 'darwin' else 'start-linux.sh'
            subprocess.Popen(['/bin/sh', str(install / script)], cwd=install,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
    except Exception:
        for name, existed in reversed(changed):
            target = install / name
            if existed:shutil.copy2(backup / name, target)
            else:target.unlink(missing_ok=True)
        raise
    return {'installed': True, 'version': new['version'], 'backup': str(backup)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--apply', required=True)
    job = json.loads(Path(parser.parse_args().apply).read_text(encoding='utf-8'))
    try:
        deadline = time.monotonic() + 120
        while True:
            try:os.kill(job['pid'], 0)
            except ProcessLookupError:break
            if time.monotonic() >= deadline:raise TimeoutError('Launcher did not exit')
            time.sleep(.2)
        result = apply_source(job)
    except Exception as error:
        result = {'installed': False, 'error': type(error).__name__, 'message': str(error)}
        if not isinstance(error, TimeoutError):
            script = 'start-macos.command' if job.get('platform') == 'darwin' else 'start-linux.sh'
            previous = Path(job['install_dir']) / script
            if previous.is_file():
                try:
                    subprocess.Popen(['/bin/sh', str(previous)], cwd=previous.parent,
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        start_new_session=True)
                except OSError:pass
    Path(job['result_file']).write_text(json.dumps(result, indent=2), encoding='utf-8')
    return 0 if result['installed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
