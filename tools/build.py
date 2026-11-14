"""Build a native portable bundle on Windows, macOS or Linux."""
from importlib import metadata
import json
from pathlib import Path
import os
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    work = Path(os.environ.get("BLOCKWERK_BUILD_DIR", str(ROOT / "build"))).resolve()
    output = Path(os.environ.get("BLOCKWERK_DIST_DIR", str(ROOT / "dist"))).resolve()
    work.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    target = "Blockwerk-Windows" if sys.platform == "win32" else "Blockwerk-macOS-" + platform.machine() if sys.platform == "darwin" else "Blockwerk-Linux-" + platform.machine()
    final = output / target
    if final.exists():
        raise SystemExit(str(final) + " already exists; choose a clean build destination.")
    for name in ("LGPL-3.0.txt", "GPL-3.0.txt"):
        if not (ROOT / "licenses" / name).is_file():
            raise SystemExit("Required license text missing: " + name)
    from PySide6.QtWidgets import QApplication
    from blockwerk.ui import app_icon
    app = QApplication.instance() or QApplication([])
    icon = work / ("blockwerk.ico" if sys.platform == "win32" else "blockwerk.png")
    app_icon().pixmap(64, 64).save(str(icon), "ICO" if sys.platform == "win32" else "PNG")
    # Keep unrelated bundled applications (e.g. Poppler's ICU) out of DLL
    # discovery. Qt uses Windows' own ICU; another icuuc.dll can break startup.
    environment = os.environ.copy()
    if sys.platform == "win32":
        windows = Path(os.environ.get("WINDIR", r"C:\Windows"))
        environment["PATH"] = os.pathsep.join([str(Path(sys.executable).parent), str(Path(sys.base_prefix)),
                                               str(windows / "System32"), str(windows)])
    environment["PYINSTALLER_CONFIG_DIR"] = str(work / "cache")
    extra_data = []
    # Codex's bundled Python ships an additional public certificate policy file
    # used by ssl.SSLContext. Preserve it when building with that runtime.
    supplemental_cas = Path(sys.base_prefix) / "Lib" / "codex-rejected-cas.pem"
    if supplemental_cas.is_file():
        extra_data = ["--add-data", str(supplemental_cas) + os.pathsep + "."]
    update_source=ROOT/'update-source.json'
    if os.environ.get('BLOCKWERK_LOCAL_UPDATE_FEED'):
        update_source=work/'update-source.json'
        update_source.write_text(json.dumps({'schema':1,'kind':'local',
            'location':str(Path(os.environ['BLOCKWERK_LOCAL_UPDATE_FEED']).resolve())},indent=2),encoding='utf-8')
    extra_data += ["--add-data", str(update_source) + os.pathsep + "."]
    hidden = []
    if sys.platform == "darwin":
        hidden = ["--hidden-import", "keyring.backends.macOS"]
    elif sys.platform.startswith("linux"):
        hidden = ["--hidden-import", "keyring.backends.SecretService"]
    icon_options = ["--icon", str(icon)] if sys.platform == "win32" else []
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
                    "--windowed", "--name", "Blockwerk", *icon_options, *hidden,
                    "--add-data", str(ROOT / "EINRICHTUNG.md") + os.pathsep + ".",
                    "--add-data", str(ROOT / "launcher-auth.json") + os.pathsep + ".",
                    "--exclude-module", "tkinter", "--exclude-module", "unittest",
                    "--distpath", str(output), "--workpath", str(work / "pyinstaller"),
                    "--specpath", str(work), *extra_data, str(ROOT / "main.py")], check=True, cwd=ROOT, env=environment)
    built = output / "Blockwerk"
    if sys.platform == "darwin":
        final.mkdir()
        (output / "Blockwerk.app").rename(final / "Blockwerk.app")
    else:
        built.rename(final)
    if sys.platform=='win32':
        helper_output=work/'updater-dist'
        subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--windowed',
            '--name','BlockwerkUpdater','--exclude-module','PySide6','--exclude-module','requests',
            '--distpath',str(helper_output),'--workpath',str(work/'updater-work'),
            '--specpath',str(work),str(ROOT/'tools'/'update_bootstrap.py')],check=True,cwd=ROOT,env=environment)
        shutil.copy2(helper_output/'BlockwerkUpdater.exe',final/'BlockwerkUpdater.exe')
    for name in ("README.md", "EINRICHTUNG.md", "AUTH-STATUS.md", "PLATTFORMEN.md", "MODS-UND-SERVER.md", "WELTEN-UND-SNAPSHOTS.md", "SKINS-UND-UPDATES.md", "START-HIER.txt", "PRUEFBERICHT.md", "LICENSE", "THIRD_PARTY.md"):
        shutil.copy2(ROOT / name, final / name)
    licenses = final / "licenses"
    licenses.mkdir(exist_ok=True)
    for dist in metadata.distributions():
        name = dist.metadata.get("Name", "unknown")
        for file in dist.files or []:
            if any(word in str(file).lower() for word in ("license", "copying", "notice")) and str(file).endswith((".txt", ".md", "LICENSE", "NOTICE", "COPYING")):
                source = Path(dist.locate_file(file))
                if source.is_file():
                    destination = licenses / name / str(file).replace("../", "").replace("..\\", "")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copy2(python_license, licenses / "Python-LICENSE.txt")
    for file in (ROOT / "licenses").glob("*.txt"):
        shutil.copy2(file, licenses / file.name)
    versions = sorted({d.metadata["Name"] + "==" + d.version for d in metadata.distributions() if d.metadata.get("Name")})
    (final / "BUILD-DEPENDENCIES.txt").write_text("\n".join(versions) + "\n", encoding="utf-8")
    from blockwerk.core import VERSION
    from blockwerk.updates import platform_key
    release={'app':'Blockwerk','schema':1,'version':VERSION,'platform':platform_key(),
             'owned_entries':sorted({p.name for p in final.iterdir()}|{'release.json'})}
    (final/'release.json').write_text(json.dumps(release,indent=2),encoding='utf-8')
    print("Built:", final)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
