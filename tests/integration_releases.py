"""Real metadata and command construction for EVERY release; never starts a game."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import re
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import requests
from minecraft_launcher_lib import command
from minecraft_launcher_lib._helper import download_file
from blockwerk.core import LauncherService, is_release, is_snapshot, filter_versions, minecraft_command


def main(kind="Vollversionen"):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        service = LauncherService(root)
        catalog, cached = service.list_versions()
        versions = filter_versions(catalog, kind)
        assert versions and not cached
        if kind == "Vollversionen":
            assert any(v['id'] == '1.0' for v in versions)
        assert all((is_snapshot if kind == "Snapshots" else is_release)(v) for v in versions)
        print('Official catalog:', len(versions), kind, flush=True)
        def verify(version):
            response = requests.get(version['url'])
            response.raise_for_status()
            assert hashlib.sha1(response.content).hexdigest() == version['sha1']
            metadata = response.json()
            assert metadata['id'] == version['id']
            assert metadata['type'] == ('snapshot' if kind == 'Snapshots' else 'release')
            base = service.game_root / 'versions' / version['id']
            base.mkdir(parents=True)
            (base / (version['id'] + '.json')).write_bytes(response.content)
            # Synthetic fields for argument-construction tests only. No process
            # is created and these fields are not a product login option.
            args = minecraft_command(version['id'], service.game_root, {
                'username': 'INTEGRATION_TEST_ONLY', 'uuid': '00000000000000000000000000000001',
                'token': 'TEST_NOT_A_CREDENTIAL', 'executablePath': 'java',
                'gameDirectory': str(root / 'isolated'), 'jvmArguments': ['-Xmx2048M'],
                'enableLoggingConfig': True})
            assert metadata['mainClass'] in args
            unresolved = sorted({name for arg in args for name in re.findall(r'\$\{([^}]+)\}', arg)})
            return version['id'], metadata, unresolved
        manifests = {}
        unresolved_versions = {}
        with ThreadPoolExecutor(max_workers=8) as executor:
            for future in as_completed([executor.submit(verify, version) for version in versions]):
                name, metadata, unresolved = future.result()
                manifests[name] = metadata
                if unresolved:
                    unresolved_versions[name] = unresolved
        assert not unresolved_versions, 'Unresolved argument placeholders: ' + str(unresolved_versions)
        print('Verified metadata and real command construction:', len(manifests), 'of', len(versions), 'passed')
        if kind == 'Snapshots':
            print('Snapshot metadata/commands only; actual world integration is documented in PRUEFBERICHT.md',flush=True)
            return
        client = manifests['1.0']['downloads']['client']
        jar = service.game_root / 'versions' / '1.0' / '1.0.jar'
        assert download_file(client['url'], str(jar), sha1=client['sha1'], minecraft_directory=service.game_root)
        assert hashlib.sha1(jar.read_bytes()).hexdigest() == client['sha1']
        print('Verified original Minecraft 1.0 client:', jar.stat().st_size, 'bytes; game not launched')


if __name__ == '__main__':
    main()
