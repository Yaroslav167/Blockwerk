"""Optional: genuine Minecraft 1.0 install + Java + offline preflight.

Downloads game files and a runtime (roughly 100+ MB) into a temporary directory.
No Microsoft account is used. The game process is intercepted in this TEST only.
The installed Java runtime is actually executed with -version.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from minecraft_launcher_lib import install, runtime
from blockwerk import core


def main():
    with tempfile.TemporaryDirectory() as directory:
        service = core.LauncherService(Path(directory))
        service.list_versions()
        print('Installing original Minecraft 1.0 files and Java. No game launch.', flush=True)
        last = ['']
        def status(text):
            if not text.startswith('Download ') and text != last[0]:
                print(text, flush=True)
                last[0] = text
        service.prepare_local_version('1.0', threading.Event(), status, lambda *_: None)
        metadata = json.loads((service.game_root / 'versions' / '1.0' / '1.0.json').read_text(encoding='utf-8'))
        java = runtime.get_executable_path(metadata.get('javaVersion', {}).get('component', 'jre-legacy'), service.game_root)
        assert java
        checked = subprocess.run([java, '-version'], capture_output=True, text=True, timeout=30)
        assert checked.returncode == 0, checked.stderr
        print('Real downloaded Java runtime:', checked.stderr.splitlines()[0], flush=True)
        captured = Mock(wait=Mock(return_value=0))
        with patch.object(service.accounts, 'read', side_effect=AssertionError('No Microsoft account access')) , \
             patch.object(core.subprocess, 'Popen', return_value=captured) as popen, \
             patch.object(core.requests.sessions.Session, 'request', side_effect=AssertionError('Network forbidden')):
            assert service.launch('1.0', threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True) == 0
            args = popen.call_args.args[0]
            assert not any('${' in value for value in args)
        receipt = json.loads(service.receipt_path('1.0').read_text(encoding='utf-8'))
        print('Real files verified offline:', len(receipt['files']), flush=True)
        print('No network calls during offline validation; actual game process deliberately NOT started.', flush=True)


if __name__ == '__main__':
    main()
