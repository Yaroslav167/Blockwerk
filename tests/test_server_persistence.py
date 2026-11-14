from pathlib import Path
import tempfile
import unittest
from blockwerk.core import LauncherError, Settings, atomic_json
from blockwerk.servers import write_server_file, prepare_server_file, ServerStore
from blockwerk.worlds import NBTReader


def read(path):
    reader=NBTReader(path.read_bytes());reader.number('B');reader.string()
    return reader.payload(10)['servers']


class ServerPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.path=self.root/'servers.dat'

    def test_many_favorites_survive_restart(self):
        store=ServerStore(self.root)
        for i in range(30):store.add(str(i),f's{i}.example.org')
        prepare_server_file(self.path,store.list())
        self.assertEqual(len(read(self.path)),30)
        original=self.path.read_bytes()
        prepare_server_file(self.path,ServerStore(self.root).list())
        self.assertEqual(self.path.read_bytes(),original)

    def test_native_edits_deletions_icons_and_unknown_tags_survive_new_import(self):
        favorites=[{'name':'Favorite','address':'example.org'}]
        prepare_server_file(self.path,favorites)
        # Simulate deleting the favorite and saving a new server with an icon in Minecraft.
        write_server_file(self.path,[{'name':'In game 😀','address':'localhost'}])
        original=self.path.read_bytes()
        icon=b'\x08\x00\x04icon\x00\x05abcde'
        self.path.write_bytes(original[:-2]+icon+original[-2:])
        before=self.path.read_bytes()
        prepare_server_file(self.path,favorites)
        self.assertEqual(self.path.read_bytes(),before)
        prepare_server_file(self.path,favorites+[{'name':'New','address':'new.example.org'}])
        rows=read(self.path)
        self.assertEqual([r['ip'] for r in rows],['localhost','new.example.org'])
        self.assertEqual(rows[0]['name'],'In game 😀')
        self.assertEqual(rows[0]['icon'],'abcde')
        self.assertEqual(self.path.with_name('servers.dat.blockwerk-backup').read_bytes(),before)

    def test_legacy_list_is_copied_without_changing_original(self):
        legacy=self.root/'old'/'servers.dat'
        write_server_file(legacy,[{'name':'Old','address':'old.example.org'}])
        original=legacy.read_bytes()
        prepare_server_file(self.path,[{'name':'New','address':'new.example.org'}],legacy)
        self.assertEqual(len(read(self.path)),2)
        self.assertEqual(legacy.read_bytes(),original)

    def test_empty_list_saved_by_minecraft_accepts_new_favorites(self):
        self.path.write_bytes(b'\x0a\x00\x00\x09\x00\x07servers\x00\x00\x00\x00\x00\x00')
        prepare_server_file(self.path,[{'name':'New','address':'new.example.org'}])
        self.assertEqual(read(self.path)[0]['ip'],'new.example.org')

    def test_corrupt_native_list_is_not_overwritten(self):
        self.path.write_bytes(b'corrupt')
        with self.assertRaises(LauncherError):
            prepare_server_file(self.path,[{'name':'New','address':'new.example.org'}])
        self.assertEqual(self.path.read_bytes(),b'corrupt')

    def test_retired_mode_settings_migrate_to_offline(self):
        atomic_json(self.root/'settings.json',{'community_mode':True,'offline_mode':False})
        settings=Settings.load(self.root)
        self.assertTrue(settings.offline_mode)
        self.assertFalse(settings.community_mode)
