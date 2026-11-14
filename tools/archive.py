"""Archive native build folders while preserving executable bits and symlinks."""
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    output = ROOT / 'dist'
    bundles = sorted(path for path in output.glob('Blockwerk-*') if path.is_dir())
    if not bundles:
        raise SystemExit('No native build found. Run tools/build.py first.')
    for bundle in bundles:
        destination = output / (bundle.name + '.tar.gz')
        with tarfile.open(destination, 'w:gz', dereference=False) as archive:
            archive.add(bundle, arcname=bundle.name)
        print(destination)


if __name__ == '__main__':
    main()
