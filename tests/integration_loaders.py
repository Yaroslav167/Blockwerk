"""Optional real loader installs; downloads several GB, no game/server connection.

Run explicitly: python tests/integration_loaders.py
Uses a short temporary path to accommodate external Windows Java installers.
Installs all four loaders, imports genuine Fabric API, checks offline commands.
The game process is intercepted only in this test. Any loader failure is reported
and makes the script fail. A Windows execution sandbox can block Java path
resolution; use a normal local terminal for these external installers.
"""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import requests
from blockwerk import core
from blockwerk.profiles import ProfileManager


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="bwmods-") as directory:
        root = Path(directory)
        manager = ProfileManager(core.LauncherService(root))
        seed = core.LauncherService(root / "seed")
        cancel = threading.Event()
        def status(text):
            if not text.startswith("Download "):
                print(text, flush=True)
        progress = lambda *_: None
        for base in ("1.20.1", "1.20.4"):
            seed.prepare_local_version(base, cancel, status, progress)
        for loader, base in (("fabric", "1.20.1"), ("forge", "1.20.1"), ("quilt", "1.20.1"), ("neoforge", "1.20.4")):
            print("TEST", loader, base, flush=True)
            data = manager.create("Integration " + loader, base, loader)
            child = manager.service(data["id"])
            shutil.copytree(seed.game_root, child.game_root)
            try:
                data = manager.install(data["id"], cancel, status, progress)
                if loader == "fabric":
                    url = "https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api/0.92.2+1.20.1/fabric-api-0.92.2+1.20.1.jar"
                    response = requests.get(url, timeout=120)
                    response.raise_for_status()
                    file = root / "fabric-api-0.92.2+1.20.1.jar"
                    file.write_bytes(response.content)
                    manager.add_mods(data["id"], [file])
                with patch.object(core.subprocess, "Popen", return_value=Mock(wait=Mock(return_value=0))) as process, \
                     patch.object(core.requests.sessions.Session, "request", side_effect=AssertionError("Offline launcher made a network call")), \
                     patch.object(manager.parent.accounts, "read", side_effect=AssertionError("Local profile accessed Microsoft account")):
                    manager.launch(data["id"], cancel, status, progress, lambda: None, offline=True, community_servers=[])
                    assert not any("${" in arg for arg in process.call_args.args[0])
                    game = process.call_args.kwargs["cwd"]
                    assert (game / "servers.dat").is_file()
                    if loader == "fabric":
                        assert (game / "mods" / file.name).is_file()
                results.append({"loader": loader, "base": base, "installed": data["installed"], "status": "passed"})
            except Exception as error:
                results.append({"loader": loader, "base": base, "status": "failed", "error": str(error)})
                error_log = manager.folder(data["id"]) / "installer-error.log"
                if error_log.exists():
                    print(error_log.read_text(encoding="utf-8")[-6000:], flush=True)
            print(json.dumps(results[-1], ensure_ascii=False), flush=True)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        print("Actual game processes intercepted. No gameplay or server connection verified.")
    return int(any(result["status"] != "passed" for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
