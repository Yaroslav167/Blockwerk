"""POSIX source launcher: external, architecture-specific runtime and startup log."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import struct
import sys
import venv

ROOT = Path(__file__).resolve().parent.parent


def data_root():
    if os.environ.get('BLOCKWERK_DATA_DIR'):
        return Path(os.environ['BLOCKWERK_DATA_DIR']).expanduser().resolve()
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'Blockwerk'
    return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / 'blockwerk'


def fingerprint(requirements, machine=None):
    machine = machine or platform.machine()
    tag = f'{sys.implementation.cache_tag}-{sys.platform}-{machine}'
    return tag + '-' + hashlib.sha256(requirements).hexdigest()[:16]


def check_system():
    if struct.calcsize('P') != 8:
        raise SystemExit('Blockwerk requires 64-bit Python / 64-Bit-Python erforderlich.')
    if sys.platform == 'darwin':
        version = platform.mac_ver()[0]
        if version and int(version.split('.')[0]) < 14:
            raise SystemExit('Qt 6.12 requires macOS 14 or newer / macOS 14 oder neuer erforderlich.')
    elif sys.platform == 'linux':
        architecture = platform.machine().lower()
        if architecture not in ('x86_64', 'amd64', 'aarch64', 'arm64'):
            raise SystemExit('Supported Linux architectures: x86_64 and ARM64.')
        library, version = platform.libc_ver()
        minimum = (2, 39) if architecture in ('aarch64', 'arm64') else (2, 34)
        if library and (library != 'glibc' or tuple(map(int, version.split('.')[:2])) < minimum):
            raise SystemExit('Qt 6.12 requires glibc ' + '.'.join(map(str, minimum)) + '+ on this architecture.')


def main():
    if sys.platform not in ('darwin', 'linux'):
        raise SystemExit('Use start-windows.cmd on Windows.')
    if not (3, 12) <= sys.version_info[:2] < (3, 15):
        raise SystemExit('Blockwerk requires Python 3.12–3.14. Install Python 3.12 and retry. / Bitte Python 3.12 installieren.')
    check_system()
    if sys.platform == 'linux' and not any(os.environ.get(k) for k in ('DISPLAY', 'WAYLAND_DISPLAY', 'QT_QPA_PLATFORM')) and not any(k in sys.argv for k in ('--screenshot', '--check-platform', '--check-network', '--check-auth', '--check-updates', '--build-native')):
        raise SystemExit('No desktop session found. Start Blockwerk from your Linux desktop. / Keine Desktop-Sitzung gefunden.')
    root = data_root()
    building = '--build-native' in sys.argv[1:]
    requirements = ROOT / ('requirements-build.txt' if building else 'requirements.txt')
    dependency_bytes = (ROOT / 'requirements.txt').read_bytes() + (requirements.read_bytes() if building else b'')
    runtime = root / 'launcher-runtime' / fingerprint(dependency_bytes)
    python = runtime / 'bin' / 'python'
    ready = runtime / '.blockwerk-ready'
    log = root / 'logs' / 'launcher-start.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    # Pin the same base interpreter on restart, including Intel Python under Rosetta.
    environment = os.environ.copy()
    environment['BLOCKWERK_PYTHON'] = sys.executable
    if building:environment.setdefault('QT_QPA_PLATFORM', 'offscreen')
    import fcntl
    runtime.parent.mkdir(parents=True, exist_ok=True)
    # Serialize first-start setup without requiring a third-party lock library.
    with (runtime.parent / (runtime.name + '.lock')).open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if not python.is_file():
            print('Preparing Blockwerk runtime / Python-Umgebung wird eingerichtet …', flush=True)
            venv.EnvBuilder(with_pip=True).create(runtime)
        if not ready.is_file():
            print('Installing dependencies (internet required) / Abhängigkeiten werden installiert …', flush=True)
            with log.open('a', encoding='utf-8') as output:
                result = subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
                                         '-r', str(requirements)], stdout=output, stderr=subprocess.STDOUT)
            if result.returncode:
                raise SystemExit(f'Dependency installation failed. Details: {log}\nInstallation fehlgeschlagen; siehe Protokoll.')
            # The marker is written only after imports succeed; an interrupted install is retried.
            subprocess.run([str(python), '-c', 'import PySide6.QtWidgets, minecraft_launcher_lib, keyring'], check=True)
            ready.write_text(json.dumps({'python': sys.version, 'architecture': platform.machine()}), encoding='utf-8')
    with log.open('a', encoding='utf-8') as output:
        output.write('\nStarting Blockwerk: ' + platform.platform() + '\n'); output.flush()
        command = [str(python), str(ROOT / 'tools' / 'build.py')] if building else [str(python), str(ROOT / 'main.py'), *sys.argv[1:]]
        result = subprocess.run(command, cwd=ROOT,
                                env=environment, stdout=output, stderr=subprocess.STDOUT)
    if building and not result.returncode:print('Native build / Nativer Build: ' + str(ROOT / 'dist'))
    if result.returncode:
        print(f'Blockwerk exited with code {result.returncode}. Log: {log}', file=sys.stderr)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
