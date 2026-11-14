import json
from pathlib import Path
import struct
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
import zipfile

from blockwerk import core
from blockwerk.profiles import ProfileManager, inspect_mod, version_matches
from blockwerk.servers import ServerStore, normalize_address, write_server_file


class ModServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.service = core.LauncherService(self.root)
        self.profiles = ProfileManager(self.service)

    def jar(self, name="demo.jar", loader="fabric", minecraft="1.20.x"):
        path = self.root / name
        with zipfile.ZipFile(path, "w") as archive:
            if loader == "fabric":
                archive.writestr("fabric.mod.json", json.dumps({"id": "demo", "name": "Demo", "depends": {"minecraft": minecraft, "fabric-api": "*"}}))
            elif loader == "forge":
                archive.writestr("META-INF/mods.toml", 'modLoader="javafml"\n[[mods]]\nmodId="demo"\ndisplayName="Demo"\n[[dependencies.demo]]\nmodId="minecraft"\nmandatory=true\nversionRange="[1.20,1.21)"\n')
            elif loader == "quilt":
                archive.writestr("quilt.mod.json", json.dumps({"quilt_loader": {"id": "demo", "metadata": {"name": "Demo"}, "depends": [{"id": "minecraft", "versions": minecraft}]}}))
            elif loader == "neoforge":
                archive.writestr("META-INF/neoforge.mods.toml", 'modLoader="javafml"\n[[mods]]\nmodId="demo"\ndisplayName="Demo"\n')
        return path

    def test_profiles_are_isolated_and_share_only_account_settings(self):
        first = self.profiles.create("Fabric", "1.20.1", "fabric")
        second = self.profiles.create("Forge", "1.20.1", "forge")
        child = self.profiles.service(first["id"])
        self.assertNotEqual(child.game_root, self.profiles.service(second["id"]).game_root)
        self.assertIs(child.accounts, self.service.accounts)
        self.assertIs(child.settings, self.service.settings)
        self.assertTrue(child.allow_custom_versions)
        with self.assertRaises(core.LauncherError):
            self.profiles.folder("../../escape")

    def test_loader_installation_uses_chosen_version_and_java(self):
        profile = self.profiles.create("Forge", "1.20.1", "forge", "47.4.28")
        child = Mock()
        child.game_root = self.root / "test-minecraft"
        child.settings.java_path = "test-java"
        child.version_metadata.return_value = {}
        adapter = Mock()
        adapter.install.return_value = "1.20.1-forge-47.4.28"
        with patch.object(self.profiles, "service", return_value=child), patch.object(self.profiles, "loader_versions", return_value=["47.4.28"]), patch("blockwerk.profiles.mod_loader.get_mod_loader", return_value=adapter):
            result = self.profiles.install(profile["id"], threading.Event(), lambda _: None, lambda *_: None)
        self.assertEqual(result["installed"], "1.20.1-forge-47.4.28")
        self.assertEqual(adapter.install.call_args.kwargs["loader_version"], "47.4.28")
        self.assertEqual(adapter.install.call_args.kwargs["java"], "test-java")

    def test_all_four_mod_metadata_formats_are_recognized(self):
        for loader in ("fabric", "forge", "quilt", "neoforge"):
            with self.subTest(loader=loader):
                info = inspect_mod(self.jar(loader + ".jar", loader))
                self.assertIn(loader, info["loaders"])
                self.assertEqual(info["id"], "demo")

    def test_fabric_uses_official_profile_json_without_running_java_installer(self):
        profile = self.profiles.create("Fabric", "1.20.1", "fabric", "0.16.14")
        child = Mock()
        child.game_root = self.root / "fabric-minecraft"
        child.settings.java_path = "test-java"
        child.version_metadata.return_value = {}
        adapter = Mock()
        adapter.get_installed_version.return_value = "fabric-loader-0.16.14-1.20.1"
        response = Mock()
        response.json.return_value = {"id": "fabric-loader-0.16.14-1.20.1", "inheritsFrom": "1.20.1"}
        with patch.object(self.profiles, "service", return_value=child), patch.object(self.profiles, "loader_versions", return_value=["0.16.14"]), patch("blockwerk.profiles.mod_loader.get_mod_loader", return_value=adapter), patch("blockwerk.profiles.requests.get", return_value=response) as request:
            result = self.profiles.install(profile["id"], threading.Event(), lambda _: None, lambda *_: None)
        self.assertEqual(result["installed"], "fabric-loader-0.16.14-1.20.1")
        self.assertIn("meta.fabricmc.net/v2/versions/loader/1.20.1/0.16.14/profile/json", request.call_args.args[0])
        adapter.install.assert_not_called()

    def test_inherited_custom_profile_prepares_and_starts_offline(self):
        import hashlib
        import sys
        profile = self.profiles.create("Custom", "1.20.1", "custom")
        service = self.profiles.service(profile["id"])
        base = service.game_root / "versions" / "1.20.1"
        base.mkdir(parents=True)
        jar = b"CLIENT FIXTURE"
        (base / "1.20.1.jar").write_bytes(jar)
        core.atomic_json(base / "1.20.1.json", {"id": "1.20.1", "type": "release", "libraries": [],
            "mainClass": "net.minecraft.client.main.Main", "minecraftArguments": "--username ${auth_player_name} --gameDir ${game_directory}",
            "downloads": {"client": {"sha1": hashlib.sha1(jar).hexdigest()}}})
        version = "custom-loader-1.20.1"
        core.atomic_json(service.game_root / "versions" / version / (version + ".json"),
                         {"id": version, "inheritsFrom": "1.20.1", "jar": "1.20.1", "libraries": []})
        java = self.root / ("java.exe" if sys.platform == "win32" else "java")
        java.touch()
        java.chmod(0o755)
        self.service.settings.java_path = str(java)
        with patch.object(core.install, "install_minecraft_version"), patch.object(core.requests.sessions.Session, "request", side_effect=AssertionError("No network")):
            service.prepare_local_version(version, threading.Event(), lambda _: None, lambda *_: None)
        with patch.object(core.subprocess, "Popen", return_value=Mock(wait=Mock(return_value=0))) as process:
            service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        self.assertIn("net.minecraft.client.main.Main", process.call_args.args[0])
        receipt = json.loads(service.receipt_path(version).read_text(encoding="utf-8"))
        self.assertTrue(any(row["path"].endswith("1.20.1.json") for row in receipt["files"]))

    def test_version_ranges_reject_known_mismatches_and_keep_unknowns_unknown(self):
        for rule in ("1.20.1", "1.20.x", ">=1.20 <1.21", "[1.20,1.21)", "~1.20.0", ["1.19.x", "1.20.x"]):
            self.assertIs(version_matches("1.20.1", rule), True, rule)
        self.assertIs(version_matches("1.21", "[1.20,1.21)"), False)
        self.assertIs(version_matches("1.20.1", "[1.20.1]"), True)
        self.assertIsNone(version_matches("1.20.1", "an-unknown-rule"))

    def test_wrong_loader_or_minecraft_version_is_rejected_before_copy(self):
        profile = self.profiles.create("Fabric", "1.20.1", "fabric")
        for file in (self.jar("wrong-loader.jar", "forge"), self.jar("wrong-version.jar", "fabric", "1.19.x")):
            with self.assertRaises(core.LauncherError):
                self.profiles.add_mods(profile["id"], [file])
        self.assertFalse(self.profiles.mod_folder(profile["id"]).exists())

    def test_mod_enable_disable_and_sync_preserve_source(self):
        profile = self.profiles.create("Fabric", "1.20.1", "fabric")
        file = self.jar()
        self.profiles.add_mods(profile["id"], [file])
        target = self.root / "game-instance"
        self.profiles.sync_mods(profile["id"], target)
        self.assertTrue((target / "mods" / "demo.jar").exists())
        self.profiles.toggle_mod(profile["id"], "demo.jar")
        self.profiles.sync_mods(profile["id"], target)
        self.assertFalse((target / "mods" / "demo.jar").exists())
        self.assertTrue((self.profiles.mod_folder(profile["id"]) / "demo.jar.disabled").exists())
        self.assertTrue(file.exists())
        self.profiles.toggle_mod(profile["id"], "demo.jar.disabled")
        self.profiles.sync_mods(profile["id"], target)
        self.assertTrue((target / "mods" / "demo.jar").exists())
        self.assertIn("fabric-api", self.profiles.mods(profile["id"])[0]["hint"])

    def test_uppercase_jar_extension_is_normalized_and_synced(self):
        profile = self.profiles.create("Fabric", "1.20.1", "fabric")
        self.profiles.add_mods(profile["id"], [self.jar("Demo.JAR")])
        self.assertEqual(self.profiles.mods(profile["id"])[0]["file"], "Demo.jar")
        target = self.root / "uppercase-game"
        self.profiles.sync_mods(profile["id"], target)
        self.assertTrue((target / "mods" / "Demo.jar").is_file())

    def test_invalid_jar_and_zip_metadata_bomb_are_rejected(self):
        bad = self.root / "bad.jar"
        bad.write_bytes(b"not a zip")
        with self.assertRaises(core.LauncherError):
            inspect_mod(bad)
        with zipfile.ZipFile(bad, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("fabric.mod.json", "x" * (1024 * 1024 + 1))
        with self.assertRaises(core.LauncherError):
            inspect_mod(bad)

    def test_profile_offline_launch_uses_normal_local_directory(self):
        profile = self.profiles.create("Fabric", "1.20.1", "fabric")
        profile["installed"] = "fabric-loader-0.16.14-1.20.1"
        core.atomic_json(self.profiles.folder(profile["id"]) / "profile.json", profile)
        child = Mock()
        child.settings.offline_name = "Spieler"
        child.root = self.root / "child"
        child.launch.return_value = 0
        with patch.object(self.profiles, "service", return_value=child), patch.object(self.profiles, "sync_mods") as sync:
            self.profiles.launch(profile["id"], threading.Event(), Mock(), Mock(), Mock(), offline=True, community_servers=[])
        self.assertEqual(sync.call_args.args[1], child.game_directory.return_value)
        child.game_directory.assert_called_once_with(self.profiles.read(profile["id"])["installed"], child.settings.offline_name)
        self.assertEqual(child.launch.call_args.kwargs["community_servers"], [])

    def test_unlimited_servers_duplicates_removal_and_persistence(self):
        store = ServerStore(self.root)
        for number in range(5):
            store.add("Server " + str(number), "server" + str(number) + ".example.org")
        store.add("Sixth", "sixth.example.org")
        self.assertEqual(len(ServerStore(self.root).list()), 6)
        first = store.list()[0]
        store.remove(first["id"])
        with self.assertRaises(core.LauncherError):
            store.add("Duplicate", "SERVER1.EXAMPLE.ORG:25565")
        store.add("Replacement", "replacement.example.org")
        self.assertEqual(len(store.list()), 6)

    def test_server_addresses_support_ipv6_and_reject_urls_and_invalid_ports(self):
        self.assertEqual(normalize_address("[::1]:25566"), "[::1]:25566")
        self.assertEqual(normalize_address("EXAMPLE.ORG:25565"), "example.org")
        for value in ("https://example.org", "user@host", "host:0", "host:65536", "host:port", "a\nb"):
            with self.assertRaises(core.LauncherError):
                normalize_address(value)

    def test_servers_dat_is_a_valid_named_list_with_five_entries(self):
        path = self.root / "servers.dat"
        rows = [{"name": "Server " + str(i), "address": "server" + str(i) + ".example.org"} for i in range(5)]
        write_server_file(path, rows)
        raw = path.read_bytes()
        position = 0
        def take(count):
            nonlocal position
            value = raw[position:position + count]
            position += count
            return value
        def string():
            return take(struct.unpack(">H", take(2))[0]).decode("utf-8")
        self.assertEqual(take(3), b"\x0a\x00\x00")
        self.assertEqual(take(1), b"\x09")
        self.assertEqual(string(), "servers")
        self.assertEqual(take(1), b"\x0a")
        self.assertEqual(struct.unpack(">i", take(4))[0], 5)
        for row in rows:
            found = {}
            while True:
                tag = take(1)
                if tag == b"\x00":
                    break
                self.assertEqual(tag, b"\x08")
                key = string()
                found[key] = string()
            self.assertEqual(found, {"name": row["name"], "ip": row["address"]})
        self.assertEqual(take(1), b"\x00")
        self.assertEqual(position, len(raw))
        write_server_file(path, rows + [{"name": "6", "address": "six.example.org"}])

    def test_servers_dat_uses_java_modified_utf8_for_emoji(self):
        path = self.root / "emoji.dat"
        write_server_file(path, [{"name": "World 😀", "address": "localhost"}])
        self.assertIn(bytes.fromhex("eda0bdedb880"), path.read_bytes())


if __name__ == "__main__":
    unittest.main()
