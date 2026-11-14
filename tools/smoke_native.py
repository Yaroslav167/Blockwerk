"""Run the built app on the current target OS, using isolated test data only."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    bundles = [p for p in (ROOT / 'dist').glob('Blockwerk-*') if p.is_dir()]
    if len(bundles) != 1:raise SystemExit('Expected one native build')
    folder = bundles[0]
    executable = folder / ('Blockwerk.exe' if sys.platform == 'win32' else 'Blockwerk.app/Contents/MacOS/Blockwerk' if sys.platform == 'darwin' else 'Blockwerk')
    with tempfile.TemporaryDirectory(prefix='blockwerk-native-smoke-') as tmp:
        environment = os.environ.copy()
        environment['QT_QPA_PLATFORM'] = 'offscreen'
        environment['BLOCKWERK_DATA_DIR'] = tmp
        for language in ('de', 'en'):
            (Path(tmp) / 'settings.json').write_text(json.dumps({'language': language, 'offline_mode': True}), encoding='utf-8')
            for page in ('play', 'servers', 'worlds', 'skins', 'updates', 'microsoft', 'versions'):
                image = ROOT / 'dist' / f'smoke-{language}-{page}.png'
                subprocess.run([str(executable), '--screenshot', str(image), '--screenshot-page', page],
                               env=environment, check=True, timeout=45)
                if not image.is_file() or image.stat().st_size < 1000:raise RuntimeError('Missing screenshot')
        report = ROOT / 'dist' / 'platform-check.json'
        subprocess.run([str(executable), '--check-platform', str(report)], env=environment, check=True, timeout=30)
    print('Native startup and both languages verified; no game or account sign-in tested.')


if __name__ == '__main__':main()
