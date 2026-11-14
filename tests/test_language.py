import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from blockwerk.core import LauncherService, Settings, atomic_json
from blockwerk.ui import LauncherWindow
from blockwerk.i18n import set_language


class LanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.service=LauncherService(Path(self.temp.name))
        self.service.settings.offline_mode=True
        self.service.settings.language='en'
        self.window=LauncherWindow(self.service,offline_preview=True)
        self.window.worlds_loaded=True

    def tearDown(self):
        self.window.close();self.window.deleteLater();self.app.processEvents()
        set_language('de');self.temp.cleanup()
        self.app.blockwerk_window=None

    def test_english_pages_and_header_selector(self):
        self.assertEqual(self.window.language_combo.currentData(),'en')
        self.assertEqual(self.window.title_label.text(),'Play')
        self.assertEqual(self.window.play_button.text(),'Launch offline  ▶')
        self.window.resize(1040,780);self.window.show()
        for index,title in enumerate(['Play','Versions','Settings','About Blockwerk','Mods & Loaders','Server',
                                      'Microsoft account','Worlds','Skins','Launcher updates']):
            self.window.navigate(index);self.app.processEvents()
            self.assertEqual(self.window.title_label.text(),title)
            self.assertFalse(self.window.grab().isNull())
        self.assertEqual(self.window.update_check_button.text(),'Check now')

    def test_translated_categories_keep_canonical_settings_and_versions(self):
        self.window.versions=[{'id':'1.20.1','type':'release'},{'id':'23w31a','type':'snapshot'}]
        self.window.populate_combo()
        self.assertEqual(self.window.version_kind_combo.currentText(),'Releases')
        self.window.version_kind_combo.setCurrentText('Snapshots')
        self.assertEqual(self.window.version_combo.currentData(),'23w31a')
        self.window.filter_combo.setCurrentText('Releases')
        self.assertEqual(self.window.version_combo.currentData(),'1.20.1')
        self.assertEqual(self.service.settings.version_filter,'Vollversionen')

    def test_switch_persists_language_and_preserves_own_names_and_current_page(self):
        self.service.settings.offline_name='Welten'
        self.window.servers.add('Spielen','example.org')
        self.window.navigate(5)
        self.window.language_combo.setCurrentIndex(0)
        self.window=self.app.blockwerk_window
        self.assertEqual(self.window.title_label.text(),'Server')
        self.assertEqual(self.window.stack.currentIndex(),5)
        self.assertEqual(Settings.load(self.service.root).language,'de')
        self.assertEqual(self.window.account_name.text(),'Welten')
        self.assertEqual(self.window.server_table.item(0,0).text(),'Spielen')
        self.window.language_combo.setCurrentIndex(1)
        self.window=self.app.blockwerk_window
        self.assertEqual(Settings.load(self.service.root).language,'en')
        self.assertEqual(self.window.play_button.text(),'Launch offline  ▶')

    def test_language_switch_waits_for_active_game_or_download(self):
        self.window.set_busy(True)
        self.assertFalse(self.window.language_combo.isEnabled())
        self.window.language_combo.setCurrentIndex(0)
        self.assertEqual(self.service.settings.language,'en')
        self.window.set_busy(False)
        self.assertTrue(self.window.language_combo.isEnabled())

    def test_invalid_saved_language_falls_back_to_german(self):
        atomic_json(self.service.root/'settings.json',{'language':'invalid'})
        self.assertEqual(Settings.load(self.service.root).language,'de')
