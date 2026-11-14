"""Opt-in real-server verification; no account and no game process required.

Run from the project folder: python tests/integration_downloads.py
Downloads one 27 KB historical client into a temporary directory, checks Mojang's
hash, checks representative manifests, and exercises library command generation.
This never launches Minecraft or creates an offline account.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import requests
from minecraft_launcher_lib import command
from minecraft_launcher_lib._helper import download_file
from blockwerk.core import LauncherService, safe_version_id, MANIFEST_URL


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        service = LauncherService(root)
        service.list_versions()
        versions = requests.get(MANIFEST_URL).json()['versions']
        assert versions
        for version in versions:
            safe_version_id(version["id"])
        print("Live Mojang catalog:", len(versions), "versions; all IDs supported")
        for kind in ("release", "snapshot", "old_alpha", "old_beta"):
            version = next(v for v in versions if v["type"] == kind)
            response = requests.get(version["url"])
            response.raise_for_status()
            assert hashlib.sha1(response.content).hexdigest() == version["sha1"]
            metadata = response.json()
            assert metadata["id"] == version["id"]
            assert metadata["downloads"]["client"]["url"].startswith("https://")
            print("Verified metadata:", kind, version["id"])
        version = next(v for v in versions if v["id"] == "rd-132211")
        response = requests.get(version["url"])
        response.raise_for_status()
        assert hashlib.sha1(response.content).hexdigest() == version["sha1"]
        metadata = response.json()
        game = service.game_root
        base = game / "versions" / version["id"]
        base.mkdir(parents=True)
        (base / (version["id"] + ".json")).write_bytes(response.content)
        info = metadata["downloads"]["client"]
        jar = base / (version["id"] + ".jar")
        assert download_file(info["url"], str(jar), sha1=info["sha1"], minecraft_directory=game)
        assert hashlib.sha1(jar.read_bytes()).hexdigest() == info["sha1"]
        print("Verified official historical client:", jar.stat().st_size, "bytes")
        # Synthetic credentials exercise argument construction only; never run this
        # command and never include an offline-account path in the application.
        arguments = command.get_minecraft_command(version["id"], game, {
            "username": "INTEGRATION_TEST", "uuid": "00000000000000000000000000000001",
            "token": "TEST_NOT_A_CREDENTIAL", "gameDirectory": str(root / "isolated"),
            "executablePath": "java.exe", "jvmArguments": ["-Xmx2048M"]})
        assert arguments[0] == "java.exe"
        assert "-Xmx2048M" in arguments
        assert metadata["mainClass"] in arguments
        print("Real library command generation: passed (game not launched)")


if __name__ == "__main__":
    main()
