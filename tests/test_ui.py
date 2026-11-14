import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from blockwerk.core import LauncherService
from blockwerk.ui import LauncherWindow, STYLE


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyleSheet(STYLE)
        font_root = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        for name in ("segoeui.ttf", "segoeuib.ttf", "seguisym.ttf"):
            QFontDatabase.addApplicationFont(str(font_root / name))

    def setUp(self):
        self.keyring_patch = patch("blockwerk.core.native_keyring", side_effect=RuntimeError("No real keychain in unit tests"))
        self.keyring_patch.start()
        self.addCleanup(self.keyring_patch.stop)
        self.temp = tempfile.TemporaryDirectory()
        # Missing-registration tests use an isolated publisher configuration.
        with patch('blockwerk.core.bundled_client_id', return_value=''):
            self.service = LauncherService(Path(self.temp.name))
        self.window = LauncherWindow(self.service, offline_preview=True)
        self.window.worlds_loaded = True
        self.window.versions = [{"id": "1.0", "type": "release"}, {"id": "1.21.11", "type": "release"},
                                {"id": "25w01a", "type": "snapshot"},
                                {"id": "1.14 Pre-Release 1", "type": "snapshot"}]
        self.window.populate_combo()
        self.window.render_versions()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def test_first_run_routes_login_to_account_without_browser_or_id_form(self):
        with patch("blockwerk.core.webbrowser.open") as browser, patch("blockwerk.ui.QMessageBox.information") as notice:
            self.window.play()
        self.assertEqual(self.window.stack.currentIndex(), 6)
        browser.assert_not_called()
        notice.assert_not_called()
        self.assertFalse(self.window.auth_start_button.isEnabled())
        self.assertIn("Projektbetreiber", self.window.auth_details.text())
        self.assertTrue(self.window.publisher_setup.isHidden())
        self.assertEqual(self.window.account_name.text(), "Nicht angemeldet")

    def test_only_releases_are_selectable_and_search_works(self):
        self.assertEqual(self.window.filter_combo.count(), 2)
        self.assertEqual(self.window.table.rowCount(), 2)
        self.window.search.setText("1.21")
        self.assertEqual(self.window.table.rowCount(), 1)
        self.window.table.selectRow(0)
        self.window.choose_table_version()
        self.assertEqual(self.window.version_combo.currentData(), "1.21.11")
        self.assertEqual(self.window.stack.currentIndex(), 0)

    def test_login_button_switches_from_offline_to_online_and_explains_missing_id(self):
        self.window.mode_combo.setCurrentIndex(1)
        with patch("blockwerk.core.webbrowser.open") as browser, patch("blockwerk.ui.QMessageBox.information") as notice:
            self.window.login()
        browser.assert_not_called()
        notice.assert_not_called()
        self.assertEqual(self.window.stack.currentIndex(), 6)
        self.assertFalse(self.service.settings.offline_mode)

    def test_offline_name_is_saved_without_account(self):
        self.window.mode_combo.setCurrentIndex(1)
        self.window.local_name_input.setText("MeinSpieler")
        self.assertTrue(self.window.save_local_name())
        self.assertEqual(self.service.settings.offline_name, "MeinSpieler")
        self.assertEqual(self.window.account_name.text(), "MeinSpieler")
        self.assertEqual(self.window.play_button.text(), "Offline starten  ▶")

    def test_login_with_valid_saved_id_starts_auth_task(self):
        self.service.settings.client_id = "09af2a7b-7b13-441a-81d8-1ced7aa8a88b"
        self.window.client_input.setText(self.service.settings.client_id)
        with patch.object(self.window, "run_task") as run:
            self.window.login()
        self.assertEqual(run.call_args.args[0], "login")

    def test_save_ram_and_public_app_id(self):
        self.window.client_input.setText("09af2a7b-7b13-441a-81d8-1ced7aa8a88b")
        self.window.memory_input.setValue(6144)
        self.window.save_settings()
        self.assertEqual(self.service.settings.memory_mb, 6144)
        self.assertTrue(self.service.settings.client_id)
        self.assertFalse(self.window.notice.isVisible())

    def test_busy_task_blocks_duplicate_actions_and_settings(self):
        self.window.set_busy(True)
        self.assertFalse(self.window.play_button.isEnabled())
        self.assertFalse(self.window.settings_content.isEnabled())
        self.assertFalse(self.window.logout_button.isEnabled())
        self.window.set_busy(False)
        self.assertTrue(self.window.play_button.isEnabled())

    def test_all_pages_render_at_minimum_window_size(self):
        self.window.resize(1040, 780)
        self.window.show()
        for index in range(10):
            self.window.navigate(index)
            self.app.processEvents()
            image = self.window.grab().toImage()
            self.assertFalse(image.isNull())
            self.assertEqual(image.width(), 1040)

    def test_skin_selection_and_variant_persist_without_account_upload(self):
        self.assertEqual(self.window.skin_list.count(),3)
        self.assertFalse(self.window.skin_online_button.isEnabled())
        with patch('blockwerk.skins.requests.post') as upload:
            self.window.skin_list.setCurrentRow(1)
            self.window.skin_variant.setCurrentIndex(1)
        upload.assert_not_called()
        self.assertEqual(self.window.skins.selected()['name'],'Waldläufer')
        self.assertEqual(self.window.skins.selected()['variant'],'slim')

    def test_weekly_check_is_launcher_only_and_defers_during_game(self):
        with patch.object(self.window.updates,'due',return_value=True), \
                patch.object(self.window,'check_updates') as check, \
                patch.object(self.window,'reload_versions') as catalog:
            self.window.set_busy(True)
            self.window.scheduled_update_check()
            check.assert_not_called()
            self.window.set_busy(False)
            self.window.scheduled_update_check()
            check.assert_called_once()
            catalog.assert_not_called()
        self.window.update_automatic.setChecked(False)
        self.assertFalse(self.window.updates.state['automatic'])

    def test_update_install_is_blocked_while_busy(self):
        self.window.update_package=Path(self.temp.name)/'package.zip'
        self.window.update_info={'available':True,'newer':True,'version':'0.8.0','notes':''}
        self.window.set_busy(True)
        with patch.object(self.window,'run_task') as task:
            self.window.install_update()
        task.assert_not_called()
        self.assertFalse(self.window.update_install_button.isEnabled())
        self.window.set_busy(False)

    def test_only_online_and_offline_modes_remain(self):
        self.window.select_offline_mode()
        self.assertEqual(self.window.mode_combo.currentIndex(), 1)
        self.assertEqual(self.window.mode_combo.count(), 2)
        self.assertFalse(self.service.settings.community_mode)
        self.assertTrue(self.service.settings.offline_mode)
        self.assertEqual(self.window.play_button.text(), "Offline starten  ▶")

    def test_server_add_button_stays_enabled_above_five(self):
        for number in range(12):
            self.window.servers.add(str(number), "s" + str(number) + ".example.org")
        self.window.refresh_servers()
        self.assertTrue(self.window.server_add_button.isEnabled())
        self.assertEqual(self.window.server_table.rowCount(), 12)

    def test_browser_link_is_available_only_during_login_and_cleared_on_cancel(self):
        self.service.settings.client_id = "09af2a7b-7b13-441a-81d8-1ced7aa8a88b"
        self.window.active_task = "login"
        self.window.set_busy(True)
        self.window.receive_auth_link("https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?state=TEST")
        self.assertTrue(self.window.auth_url)
        self.window.show_status("Microsoft und Xbox werden verbunden …")
        self.assertEqual(self.window.auth_progress.value(), 2)
        self.window.cancel()
        self.assertFalse(self.window.auth_url)
        self.assertIn("ABBRUCH", self.window.auth_badge.text())
        self.window.failed("login", "Anmeldung abgebrochen.")
        self.assertIn("abgebrochen", self.window.auth_details.text())

    def test_login_errors_stay_on_account_page_without_modal_or_false_success(self):
        self.service.settings.client_id = "09af2a7b-7b13-441a-81d8-1ced7aa8a88b"
        self.window.active_task = "login"
        self.window.set_busy(True)
        self.window.auth_url = "https://login.microsoftonline.com/TEST"
        with patch("blockwerk.ui.QMessageBox.warning") as dialog:
            self.window.failed("login", "Die Minecraft-API-Freigabe fehlt.")
        dialog.assert_not_called()
        self.assertEqual(self.window.stack.currentIndex(), 6)
        self.assertFalse(self.window.auth_url)
        self.assertEqual(self.window.username, "")
        self.assertIn("Freigabe fehlt", self.window.auth_details.text())
        self.assertTrue(self.window.auth_start_button.isEnabled())

    def test_success_shows_profile_and_returns_to_online_play(self):
        self.service.settings.client_id = "09af2a7b-7b13-441a-81d8-1ced7aa8a88b"
        self.window.active_task = "login"
        self.window.set_busy(True)
        self.window.finished("login", "TestPlayer")
        self.assertEqual(self.window.auth_heading.text(), "Angemeldet als TestPlayer")
        self.assertEqual(self.window.auth_progress.value(), 4)
        self.assertEqual(self.window.stack.currentIndex(), 6)
        self.window.choose_online_mode()
        self.assertEqual(self.window.mode_combo.currentIndex(), 0)
        self.assertEqual(self.window.stack.currentIndex(), 0)

    def test_operator_form_requires_explicit_opening(self):
        self.window.show()
        self.window.show_publisher_setup()
        self.assertEqual(self.window.stack.currentIndex(), 2)
        self.assertFalse(self.window.publisher_setup.isHidden())

    def test_snapshot_filter_is_available_on_play_and_versions_pages(self):
        self.window.version_kind_combo.setCurrentText("Snapshots")
        self.assertEqual(self.window.filter_combo.currentText(), "Snapshots")
        self.assertEqual(self.window.version_combo.count(), 2)
        self.assertEqual(self.window.table.rowCount(), 2)
        self.window.filter_combo.setCurrentText("Vollversionen")
        self.assertEqual(self.window.version_kind_combo.currentText(), "Vollversionen")
        self.assertEqual(self.window.version_combo.count(), 2)

    def test_world_button_selects_its_original_local_player_and_version(self):
        from test_worlds import world_fixture
        world_fixture(self.service.root / 'instances' / 'local' / 'Alex' / '1.0' / 'saves' / 'Original', version='1.0')
        self.window.worlds.official_root=Path(self.temp.name)/'absent'
        self.window.world_rows=self.window.worlds.scan()
        self.window.render_worlds()
        with patch.object(self.window,'run_task') as start:
            self.window.open_world()
        self.assertEqual(self.service.settings.offline_name,'Alex')
        self.assertEqual(self.window.launch_version(),'1.0')
        self.assertEqual(start.call_args.args[0],'world_launch')

    def test_new_world_uses_selected_snapshot_and_does_not_fabricate_a_save(self):
        self.window.version_kind_combo.setCurrentText('Snapshots')
        with patch.object(self.window,'run_task') as start:
            self.window.new_world()
        self.assertEqual(start.call_args.args[0],'world_launch')
        self.assertEqual(self.window.launch_version(),'25w01a')
        self.assertFalse(any(self.service.root.rglob('level.dat')))


if __name__ == "__main__":
    unittest.main()
