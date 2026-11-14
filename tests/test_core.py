from contextlib import ExitStack
import hashlib
import json
import os
import sys
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

import requests

from blockwerk import core

CLIENT_ID = "09af2a7b-7b13-441a-81d8-1ced7aa8a88b"  # Test fixture, not a real app registration.
PROFILE = {"name": "TestPlayer", "id": "4a58994df2aa41d996a25c5e9f657177",
           "access_token": "TEST-ACCESS-DO-NOT-LOG", "refresh_token": "TEST-REFRESH-DO-NOT-LOG"}


class CoreTests(unittest.TestCase):
    def setUp(self):
        core.platform.uname()  # Resolve Windows metadata before mocking Popen.
        self.keyring_patch = patch.object(core, "native_keyring", side_effect=RuntimeError("No real credential store in unit tests"))
        self.keyring_patch.start()
        self.addCleanup(self.keyring_patch.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.service = core.LauncherService(self.root)
        self.service.settings.client_id = CLIENT_ID

    def tearDown(self):
        self.temp.cleanup()

    def test_version_paths_accept_official_historical_names(self):
        for version in ("1.21.11", "26.4-snapshot-5", "1.14 Pre-Release 1", "3D Shareware v1.34", "rd-132211"):
            self.assertEqual(core.safe_version_id(version), version)
        for version in ("../escape", "a/../../b", r"a\b", "C:evil", "a\x00b", ".", "..", "a.", "a "):
            with self.subTest(version=version), self.assertRaises(core.LauncherError):
                core.safe_version_id(version)

    def test_settings_roundtrip_and_corruption_recovery(self):
        self.service.settings.memory_mb = 6144
        self.service.settings.save(self.root)
        self.assertEqual(core.Settings.load(self.root).memory_mb, 6144)
        (self.root / "settings.json").write_text("{bad", encoding="utf-8")
        self.assertEqual(core.Settings.load(self.root).memory_mb, 4096)
        core.atomic_json(self.root / "settings.json", {"memory_mb": -1, "client_id": []})
        self.assertEqual(core.Settings.load(self.root).memory_mb, 4096)
        self.assertEqual(core.Settings.load(self.root).client_id, "")

    def test_bad_app_ids_rejected(self):
        for value in ("", "an-email@example.com", "00000000-0000-0000-0000-000000000000"):
            with self.assertRaises(core.LauncherError):
                core.valid_client_id(value)

    def test_source_publisher_default_survives_legacy_empty_auth_config(self):
        publisher=self.root/'publisher-default'
        publisher.mkdir()
        core.atomic_json(publisher/'launcher-auth.json',{'schema':1,'client_id':''})
        core.atomic_json(publisher/'release-source.json',{'publisher_client_id':CLIENT_ID})
        with patch.object(core.sys,'_MEIPASS',str(publisher),create=True):
            self.assertEqual(core.bundled_client_id(),CLIENT_ID)

    @unittest.skipUnless(os.name == "nt", "Windows DPAPI")
    def test_account_storage_never_writes_plaintext_and_logout(self):
        self.service.accounts.write(PROFILE, CLIENT_ID)
        raw = self.service.accounts.path.read_bytes() if self.service.accounts.path.exists() else b""
        self.assertNotIn(PROFILE["refresh_token"].encode(), raw)
        self.assertNotIn(PROFILE["access_token"].encode(), raw)
        saved = self.service.accounts.read()
        self.assertEqual(saved["refresh_token"], PROFILE["refresh_token"])
        self.assertNotIn("access_token", saved)
        self.service.accounts.delete()
        self.assertIsNone(self.service.accounts.read())

    def test_dpapi_unavailable_keeps_session_only(self):
        with patch.object(core, "protect", side_effect=core.LauncherError("DPAPI unavailable")), patch.object(core, "native_keyring", side_effect=RuntimeError("Unavailable")):
            self.service.accounts.write(PROFILE, CLIENT_ID)
        self.assertTrue(self.service.accounts.session_only)
        self.assertFalse(self.service.accounts.path.exists())
        self.assertEqual(self.service.accounts.read()["name"], PROFILE["name"])
        # A new process has no saved account once an empty keyring is available.
        empty_keyring = Mock()
        empty_keyring.get_password.return_value = None
        with patch.object(core, "native_keyring", return_value=empty_keyring):
            self.assertIsNone(core.AccountStore(self.root).read())

    @unittest.skipUnless(os.name == "nt", "Windows DPAPI")
    def test_native_windows_dpapi_roundtrip_when_available(self):
        try:
            encrypted = core.protect(b"test secret")
        except core.LauncherError:
            self.skipTest("This restricted Windows profile does not provide DPAPI; session-only fallback verified separately")
        self.assertNotIn(b"test secret", encrypted)
        self.assertEqual(core.protect(encrypted, decrypt=True), b"test secret")

    def test_oauth_rejects_wrong_state_route_and_duplicate_codes(self):
        self.assertEqual(core.parse_callback("/callback?state=correct&code=one", "correct"), "one")
        for path in ("/callback?state=wrong&code=one", "/bad?state=correct&code=one",
                     "/callback?state=correct&state=wrong&code=one", "/callback?state=correct&code=one&code=two"):
            self.assertIsNone(core.parse_callback(path, "correct"))
        with self.assertRaises(core.LauncherError):
            core.parse_callback("/callback?state=correct&error=access_denied", "correct")

    def test_real_loopback_callback_pkce_and_no_secret(self):
        client_threads = []
        responses = []
        links = []

        def fake_browser(url):
            query = parse_qs(urlsplit(url).query)
            self.assertTrue(query["code_challenge"][0])
            self.assertEqual(query["code_challenge_method"], ["S256"])
            self.assertNotIn("client_secret", query)
            self.assertEqual(query["prompt"], ["select_account"])
            self.assertIn("/consumers/", url)
            def callback():
                responses.append(requests.get(core.REDIRECT_URI, params={"code": "test-code", "state": query["state"][0]}, timeout=5))
            thread = threading.Thread(target=callback)
            thread.start()
            client_threads.append(thread)
            return True

        with patch.object(core.webbrowser, "open", side_effect=fake_browser), \
             patch.object(core, "exchange_microsoft_login", return_value=PROFILE.copy()) as complete:
            result = core.browser_login(CLIENT_ID, threading.Event(), lambda _: None, links.append)
        for thread in client_threads:
            thread.join(5)
        self.assertEqual(result["name"], PROFILE["name"])
        self.assertEqual(responses[0].status_code, 200)
        self.assertEqual(responses[0].headers["Referrer-Policy"], "no-referrer")
        self.assertNotIn("test-code", responses[0].text)
        self.assertEqual(links[-1], "")
        self.assertTrue(links[0].startswith("https://login.microsoftonline.com/"))
        args = complete.call_args.args
        self.assertEqual(args[:2], (CLIENT_ID, "test-code"))
        self.assertGreaterEqual(len(args[2]), 43)

    def test_publisher_app_id_can_be_bundled_without_user_setup(self):
        config = self.root / "publisher"
        config.mkdir()
        core.atomic_json(config / "launcher-auth.json", {"schema": 1, "client_id": CLIENT_ID})
        with patch.object(core.sys, "_MEIPASS", str(config), create=True):
            self.assertEqual(core.LauncherService(self.root / "new-user").settings.client_id, CLIENT_ID)
            core.atomic_json(config / "launcher-auth.json", {"schema": 1, "client_id": "person@example.org"})
            with self.assertRaises(core.LauncherError):
                core.bundled_client_id()

    def test_cancel_after_browser_response_never_checks_or_saves_account(self):
        cancel = threading.Event()
        def response(*_):
            cancel.set()
            return PROFILE.copy()
        with patch.object(core, "browser_login", side_effect=response), patch.object(core, "validate_profile") as validate, patch.object(self.service.accounts, "write") as save:
            with self.assertRaises(core.Cancelled):
                self.service.login(cancel, lambda _: None)
        validate.assert_not_called()
        save.assert_not_called()

    def test_staged_microsoft_exchange_uses_pkce_and_never_a_secret(self):
        api = core.microsoft_account
        with patch.object(api, "get_authorization_token", return_value={"access_token": "MS-TEST", "refresh_token": "REFRESH-TEST"}) as token, \
             patch.object(api, "authenticate_with_xbl", return_value={"Token": "XBL-TEST", "DisplayClaims": {"xui": [{"uhs": "USERHASH-TEST"}]}}), \
             patch.object(api, "authenticate_with_xsts", return_value={"Token": "XSTS-TEST"}), \
             patch.object(api, "authenticate_with_minecraft", return_value={"access_token": "GAME-TEST"}), \
             patch.object(api, "get_profile", return_value={"id": PROFILE["id"], "name": "TestPlayer"}):
            result = core.exchange_microsoft_login(CLIENT_ID, "CODE-TEST", "VERIFIER-TEST", threading.Event(), lambda _: None)
        token.assert_called_once_with(CLIENT_ID, None, core.REDIRECT_URI, "CODE-TEST", "VERIFIER-TEST")
        self.assertEqual(result["refresh_token"], "REFRESH-TEST")
        self.assertEqual(result["access_token"], "GAME-TEST")

    def test_cancel_during_token_request_stops_before_xbox(self):
        cancel = threading.Event()
        def response(*_):
            cancel.set()
            return {"access_token": "MS-TEST", "refresh_token": "REFRESH-TEST"}
        with patch.object(core.microsoft_account, "get_authorization_token", side_effect=response), \
             patch.object(core.microsoft_account, "authenticate_with_xbl") as xbox:
            with self.assertRaises(core.Cancelled):
                core.exchange_microsoft_login(CLIENT_ID, "CODE", "VERIFIER", cancel, lambda _: None)
        xbox.assert_not_called()

    def test_invalid_grant_is_explained_without_raw_oauth_response(self):
        raw = {"error": "invalid_grant", "error_description": "DO-NOT-SHOW-TEST-SECRET"}
        with patch.object(core.microsoft_account, "get_authorization_token", return_value=raw):
            with self.assertRaises(core.LauncherError) as error:
                core.exchange_microsoft_login(CLIENT_ID, "CODE", "VERIFIER", threading.Event(), lambda _: None)
        self.assertIn("abgelaufen", str(error.exception))
        self.assertNotIn("DO-NOT-SHOW", str(error.exception))

    def test_login_cancelled_before_exchange(self):
        cancel = threading.Event()
        cancel.set()
        with patch.object(core.webbrowser, "open", return_value=True), \
             patch.object(core.microsoft_account, "complete_login") as complete:
            with self.assertRaises(core.Cancelled):
                core.browser_login(CLIENT_ID, cancel, lambda _: None)
            complete.assert_not_called()

    def test_entitlement_fails_closed(self):
        with patch.object(core.microsoft_account, "get_store_information", return_value={"items": []}):
            with self.assertRaises(core.LauncherError):
                core.validate_profile(PROFILE)
        with patch.object(core.microsoft_account, "get_store_information", return_value={"items": [{"name": "game_minecraft"}]}):
            core.validate_profile(PROFILE)

    def test_version_filters(self):
        versions = [{"id": "1.0", "type": "release"}, {"id": "25w01a", "type": "snapshot"},
                    {"id": "b1.0", "type": "old_beta"}]
        self.assertEqual(core.filter_versions(versions, "Releases"), [versions[0]])
        self.assertEqual(core.filter_versions(versions, "Alle", "25W"), [versions[1]])
        self.assertFalse(core.is_release({"id": "0.30", "type": "release"}))
        self.assertFalse(core.is_release({"id": "1.14 Pre-Release 1", "type": "release"}))
        self.assertTrue(core.is_release({"id": "26.3", "type": "release"}))

    def test_missing_account_never_installs_or_launches(self):
        with patch.object(core.install, "install_minecraft_version") as install, patch.object(core.subprocess, "Popen") as popen:
            with self.assertRaises(core.LauncherError):
                self.service.launch("1.0", threading.Event(), lambda _: None, lambda *_: None, lambda: None)
            install.assert_not_called()
            popen.assert_not_called()

    def mock_launch(self, include_jar=True, owns=True, wrong_checksum=False):
        self.service.accounts.write(PROFILE, CLIENT_ID)
        version = "1.14.4"
        base = self.service.game_root / "versions" / version
        base.mkdir(parents=True)
        jar = b"TEST CLIENT FIXTURE"
        core.atomic_json(base / (version + ".json"), {"id": version, "type": "release", "libraries": [],
            "downloads": {"client": {"sha1": hashlib.sha1(jar).hexdigest()}},
            "javaVersion": {"component": "jre-legacy"}})
        if include_jar:
            (base / (version + ".jar")).write_bytes(b"BAD" if wrong_checksum else jar)
        java = self.root / ("java.exe" if sys.platform == "win32" else "java")
        java.touch()
        java.chmod(0o755)
        if sys.platform == "linux" and core.platform.machine().lower() in ("arm64", "aarch64"):
            self.service.settings.java_path = str(java)
        stack = ExitStack()
        self.addCleanup(stack.close)
        mocks = {}
        mocks["refresh"] = stack.enter_context(patch.object(core.microsoft_account, "complete_refresh", return_value=PROFILE.copy()))
        mocks["entitlements"] = stack.enter_context(patch.object(core.microsoft_account, "get_store_information",
                    return_value={"items": [{"name": "product_minecraft"}]} if owns else {"items": []}))
        mocks["install"] = stack.enter_context(patch.object(core.install, "install_minecraft_version"))
        mocks["runtime"] = stack.enter_context(patch.object(core.runtime, "get_executable_path", return_value=str(java)))
        mocks["command"] = stack.enter_context(patch.object(core.command, "get_minecraft_command", return_value=[str(java), "test"]))
        mocks["popen"] = stack.enter_context(patch.object(core.subprocess, "Popen", return_value=Mock(wait=Mock(return_value=0))))
        return version, mocks

    def test_launch_uses_account_runtime_and_isolated_directory(self):
        version, mocks = self.mock_launch()
        started = Mock()
        log = []
        result = self.service.launch(version, threading.Event(), log.append, lambda *_: None, started)
        self.assertEqual(result, 0)
        self.assertEqual(mocks["refresh"].call_count, 2)
        mocks["install"].assert_called_once()
        arguments = mocks["command"].call_args.args
        self.assertEqual(arguments[0], version)
        self.assertEqual(arguments[2]["token"], PROFILE["access_token"])
        self.assertIn("-Xmx4096M", arguments[2]["jvmArguments"])
        self.assertEqual(mocks["popen"].call_args.kwargs["cwd"], self.service.game_directory(version))
        self.assertNotIn(PROFILE["access_token"], " ".join(log))
        started.assert_called_once()

    def test_unlicensed_account_cannot_install_or_launch(self):
        version, mocks = self.mock_launch(owns=False)
        with self.assertRaises(core.LauncherError):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None)
        mocks["install"].assert_not_called()
        mocks["popen"].assert_not_called()

    def test_missing_download_cannot_launch(self):
        version, mocks = self.mock_launch(include_jar=False)
        with self.assertRaises(core.LauncherError):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None)
        mocks["popen"].assert_not_called()

    def test_corrupt_download_cannot_launch(self):
        version, mocks = self.mock_launch(wrong_checksum=True)
        with self.assertRaises(core.LauncherError):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None)
        mocks["popen"].assert_not_called()

    def test_cancel_before_install(self):
        version, mocks = self.mock_launch()
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(core.Cancelled):
            self.service.launch(version, cancel, lambda _: None, lambda *_: None, lambda: None)
        mocks["install"].assert_not_called()
        mocks["popen"].assert_not_called()

    def prepare_test_install(self):
        version, mocks = self.mock_launch()
        self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None)
        for mock in mocks.values():
            mock.reset_mock()
        return version, mocks

    def test_offline_launch_makes_no_network_or_installation_requests(self):
        version, mocks = self.prepare_test_install()
        with patch.object(core.requests.sessions.Session, "request", side_effect=AssertionError("Network forbidden")):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        mocks["refresh"].assert_not_called()
        mocks["entitlements"].assert_not_called()
        mocks["install"].assert_not_called()
        mocks["runtime"].assert_not_called()
        mocks["popen"].assert_called_once()
        options = mocks["command"].call_args.args[2]
        self.assertEqual(options["uuid"], core.local_profile("Spieler")["id"])
        self.assertEqual(options["username"], "Spieler")
        self.assertEqual(options["token"], "0")

    def test_offline_missing_or_modified_file_never_launches(self):
        version, mocks = self.prepare_test_install()
        jar = self.service.game_root / "versions" / version / (version + ".jar")
        jar.write_bytes(b"CORRUPT SAME OR DIFFERENT SIZE")
        with self.assertRaises(core.LauncherError):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        mocks["popen"].assert_not_called()

    def test_runtime_bookkeeping_rewrite_does_not_invalidate_offline_files(self):
        version, mocks = self.mock_launch()
        marker = self.service.game_root / "runtime" / "jre-legacy" / "runtime.sha1"
        marker.parent.mkdir(parents=True)
        marker.write_text("before", encoding="utf-8")
        self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None)
        marker.write_text("rewritten by installer", encoding="utf-8")
        mocks["popen"].reset_mock()
        self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        mocks["popen"].assert_called_once()

    def test_offline_receipt_cannot_reference_files_outside_data_directory(self):
        version, mocks = self.prepare_test_install()
        receipt = json.loads(self.service.receipt_path(version).read_text(encoding="utf-8"))
        receipt["files"][0]["path"] = "../outside-file"
        core.atomic_json(self.service.receipt_path(version), receipt)
        with self.assertRaises(core.LauncherError):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        mocks["popen"].assert_not_called()

    def test_offline_missing_preparation_never_launches(self):
        version, mocks = self.mock_launch()
        with self.assertRaises(core.LauncherError):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        self.service.accounts.delete()
        with self.assertRaises(core.LauncherError):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        mocks["popen"].assert_not_called()

    def test_offline_works_after_logout_but_rejects_other_platform(self):
        version, mocks = self.prepare_test_install()
        self.service.accounts.delete()
        receipt = json.loads(self.service.receipt_path(version).read_text(encoding="utf-8"))
        receipt["account_id"] = "a-different-account"
        core.atomic_json(self.service.receipt_path(version), receipt)
        with patch.object(self.service.accounts, "read", side_effect=AssertionError("Offline must not read Microsoft account")):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        mocks["popen"].assert_called_once()
        mocks["popen"].reset_mock()
        receipt["platform"] = "different-os"
        core.atomic_json(self.service.receipt_path(version), receipt)
        with self.assertRaises(core.LauncherError):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True)
        mocks["popen"].assert_not_called()

    def test_local_profile_matches_java_offline_uuid_and_validates_names(self):
        self.assertEqual(core.local_profile("Notch")["id"], "b50ad385829d3141a2167e7d7539ba7f")
        self.assertNotEqual(core.local_profile("Notch")["id"], core.local_profile("notch")["id"])
        for name in ("ab", "../escape", "space name", "a" * 17, "CON"):
            with self.assertRaises(core.LauncherError):
                core.local_profile(name)

    def test_browser_falls_back_to_windows_default_handler(self):
        for error in (None, AttributeError("Browser module failed")):
            with patch.object(core.sys, "platform", "win32"), patch.object(core.webbrowser, "open", return_value=False, side_effect=error), patch.object(core.os, "startfile", create=True) as start:
                self.assertTrue(core.open_browser("https://login.microsoftonline.com/"))
                start.assert_called_once_with("https://login.microsoftonline.com/")

    def test_browser_reports_failure_when_both_methods_fail(self):
        with patch.object(core.sys, "platform", "win32"), patch.object(core.webbrowser, "open", return_value=False), patch.object(core.os, "startfile", create=True, side_effect=OSError("No handler")):
            self.assertFalse(core.open_browser("https://login.microsoftonline.com/"))

    def test_file_installation_does_not_require_account_or_client_id(self):
        version, mocks = self.mock_launch()
        self.service.accounts.delete()
        self.service.settings.client_id = ""
        with patch.object(self.service.accounts, "read", side_effect=AssertionError("No Microsoft account")):
            result = self.service.prepare_local_version(version, threading.Event(), lambda _: None, lambda *_: None)
        self.assertEqual(result, version)
        self.assertTrue(self.service.offline_available(version))
        mocks["refresh"].assert_not_called()
        mocks["entitlements"].assert_not_called()
        mocks["popen"].assert_not_called()

    def test_offline_catalog_does_not_call_network(self):
        core.atomic_json(self.root / "versions-cache.json", [{"id": "1.0", "type": "release"}, {"id": "25w01a", "type": "snapshot"}])
        with patch.object(core.requests.sessions.Session, "request", side_effect=AssertionError("No network")):
            versions, cached = self.service.list_versions(offline=True)
        self.assertTrue(cached)
        self.assertEqual([v["id"] for v in versions], ["1.0", "25w01a"])

    def test_offline_multiplayer_saves_favorites_without_account(self):
        version, mocks = self.prepare_test_install()
        rows = [{"name": "Local test", "address": "localhost:25565"}]
        with patch.object(self.service.accounts, "read", side_effect=AssertionError("No account")), patch.object(core.requests.sessions.Session, "request", side_effect=AssertionError("No launcher network")):
            self.service.launch(version, threading.Event(), lambda _: None, lambda *_: None, lambda: None, offline=True, community_servers=rows)
        directory = mocks["popen"].call_args.kwargs["cwd"]
        self.assertIn("local", directory.parts)
        self.assertTrue((directory / "servers.dat").is_file())
        self.assertNotIn("disableMultiplayer", mocks["command"].call_args.args[2])
        mocks["refresh"].assert_not_called()

    def test_unlisted_snapshot_launch_is_rejected(self):
        with patch.object(core.subprocess, "Popen") as popen:
            with self.assertRaises(core.LauncherError):
                self.service.launch("25w01a", threading.Event(), lambda _: None, lambda *_: None, lambda: None)
        popen.assert_not_called()

    def test_optional_unresolved_identity_flags_are_omitted(self):
        with patch.object(core.command, "get_minecraft_command", return_value=["java", "--clientId", "${clientid}", "--xuid", "${auth_xuid}", "--username", "Player"]):
            self.assertEqual(core.minecraft_command("1.21", self.root, {}), ["java", "--username", "Player"])
        with patch.object(core.command, "get_minecraft_command", return_value=["java", "${unknown_required_argument}"]):
            with self.assertRaises(core.LauncherError):
                core.minecraft_command("1.21", self.root, {})

    def test_platform_specific_data_directories(self):
        with patch.object(core.Path, "home", return_value=self.root), patch.dict(os.environ, {}, clear=True):
            with patch.object(core.sys, "platform", "darwin"):
                self.assertEqual(core.data_directory(), self.root / "Library" / "Application Support" / "Blockwerk")
            with patch.object(core.sys, "platform", "linux"):
                self.assertEqual(core.data_directory(), self.root / ".local" / "share" / "blockwerk")
            with patch.dict(os.environ, {"XDG_DATA_HOME": str(self.root / "custom")}):
                with patch.object(core.sys, "platform", "linux"):
                    self.assertEqual(core.data_directory(), self.root / "custom" / "blockwerk")

    def test_macos_and_linux_use_secure_keyring(self):
        for operating_system in ("darwin", "linux"):
            values = {}
            backend = Mock()
            backend.set_password.side_effect = lambda service, user, value: values.update({user: value})
            backend.get_password.side_effect = lambda service, user: values.get(user)
            backend.delete_password.side_effect = lambda service, user: values.pop(user, None)
            with patch.object(core.sys, "platform", operating_system), patch.object(core, "native_keyring", return_value=backend):
                store = core.AccountStore(self.root)
                store.write(PROFILE, CLIENT_ID)
                reloaded = core.AccountStore(self.root)
                self.assertEqual(reloaded.read()["id"], PROFILE["id"])
                self.assertTrue(reloaded.persistent)
                self.assertFalse(store.path.exists())
                reloaded.delete()
                self.assertIsNone(core.AccountStore(self.root).read())

    def test_linux_keyring_unavailable_uses_memory_only(self):
        with patch.object(core.sys, "platform", "linux"), patch.object(core, "native_keyring", side_effect=RuntimeError("locked")):
            store = core.AccountStore(self.root)
            store.write(PROFILE, CLIENT_ID)
            self.assertTrue(store.session_only)
            self.assertFalse(store.persistent)
            self.assertFalse(store.path.exists())
            self.assertEqual(store.read()["name"], PROFILE["name"])

    def test_cached_catalog_fallback(self):
        core.atomic_json(self.root / "versions-cache.json", [{"id": "1.0", "type": "release"}])
        with patch.object(core.requests, "get", side_effect=requests.ConnectionError):
            versions, cached = self.service.list_versions()
        self.assertTrue(cached)
        self.assertEqual(versions[0]["id"], "1.0")

    def test_auth_error_responses_are_never_shown_raw(self):
        secret = "secret-auth-payload"
        self.assertNotIn(secret, core.human_error(requests.HTTPError(secret)))
        self.assertNotIn(secret, core.human_error(KeyError(secret)))


if __name__ == "__main__":
    unittest.main()
