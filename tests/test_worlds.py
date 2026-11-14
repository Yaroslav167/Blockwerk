import gzip
import json
from pathlib import Path
import struct
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from blockwerk import core
from blockwerk.profiles import ProfileManager
from blockwerk.worlds import WorldManager, world_metadata


def world_fixture(folder, name="Meine Welt", version="1.20.1", snapshot=False, played=1234567890000):
    folder.mkdir(parents=True, exist_ok=True)
    def string(value):
        encoded=value.encode("utf-8")
        return struct.pack(">H",len(encoded))+encoded
    data=b"\x0a\x00\x00\x0a"+string("Data")
    data+=b"\x08"+string("LevelName")+string(name)
    data+=b"\x04"+string("LastPlayed")+struct.pack(">q",played)
    data+=b"\x03"+string("GameType")+struct.pack(">i",1)
    data+=b"\x0a"+string("Version")+b"\x08"+string("Name")+string(version)
    data+=b"\x01"+string("Snapshot")+bytes([bool(snapshot)])+b"\x00\x00\x00"
    (folder/"level.dat").write_bytes(gzip.compress(data))
    return folder


class WorldTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.service=core.LauncherService(self.root/'blockwerk')
        self.profiles=ProfileManager(self.service)
        self.manager=WorldManager(self.service,self.profiles,self.root/'official')

    def test_real_gzip_nbt_metadata_fields_and_unicode_are_read(self):
        folder=world_fixture(self.root/'world',name="§aWelt ü 😀")
        row=world_metadata(folder/'level.dat')
        self.assertEqual(row['name'],'Welt ü 😀')
        self.assertEqual(row['game_mode'],'Kreativ')
        self.assertEqual(row['minecraft_version'],'1.20.1')
        self.assertEqual(row['last_played'],1234567890000)

    def test_official_all_local_players_community_and_mod_profiles_are_found(self):
        world_fixture(self.root/'official'/'saves'/'official')
        world_fixture(self.service.root/'instances'/'1.20.1'/'saves'/'online')
        world_fixture(self.service.root/'instances'/'local'/'Alex'/'1.20.1'/'saves'/'local')
        world_fixture(self.service.root/'instances'/'community'/'Sam'/'1.20.1'/'saves'/'community')
        profile=self.profiles.create('Fabric','1.20.1','fabric')
        world_fixture(self.profiles.folder(profile['id'])/'instances'/'local'/'Alex'/'fabric-test'/'saves'/'modded')
        rows=self.manager.scan()
        self.assertEqual(len(rows),5)
        self.assertEqual({r['folder'] for r in rows},{'official','online','local','community','modded'})
        self.assertEqual(next(r for r in rows if r['folder']=='modded')['profile_id'],profile['id'])

    def test_added_game_saves_or_world_folder_is_persistent_and_deduplicated(self):
        folder=world_fixture(self.root/'extra'/'saves'/'world')
        self.manager.add_root(self.root/'extra')
        self.manager.add_root(self.root/'extra'/'saves')
        self.manager.add_root(folder)
        other=WorldManager(self.service,self.profiles,self.root/'absent')
        self.assertEqual(len(other.scan()),1)
        self.assertEqual(len(other.extra_roots()),3)

    def test_corrupt_or_oversized_metadata_does_not_hide_other_worlds(self):
        first=world_fixture(self.root/'official'/'saves'/'bad')
        (first/'level.dat').write_bytes(b'broken')
        second=world_fixture(self.root/'official'/'saves'/'large')
        (second/'level.dat').write_bytes(gzip.compress(b'x'*(16*1024*1024+1)))
        world_fixture(self.root/'official'/'saves'/'good')
        rows=self.manager.scan()
        self.assertEqual(len(rows),3)
        self.assertEqual(sum(bool(r['error']) for r in rows),2)

    def test_play_copy_preserves_original_and_reuses_existing_play_copy(self):
        folder=world_fixture(self.root/'official'/'saves'/'Original')
        (folder/'region').mkdir()
        (folder/'region'/'r.0.0.mca').write_bytes(b'REGION-TEST')
        before=(folder/'level.dat').read_bytes()
        row=self.manager.scan()[0]
        target=self.root/'target-game'
        result=self.manager.play_copy(row,target,threading.Event(),lambda _:None)
        self.assertEqual((target/'saves'/result/'region'/'r.0.0.mca').read_bytes(),b'REGION-TEST')
        self.assertEqual((folder/'level.dat').read_bytes(),before)
        again=self.manager.play_copy(row,target,threading.Event(),lambda _:None)
        self.assertEqual(result,again)

    def test_same_instance_uses_original_unless_a_version_copy_is_requested(self):
        game=self.service.game_directory('1.20.1','Spieler')
        folder=world_fixture(game/'saves'/'World')
        row=self.manager.scan()[0]
        self.assertEqual(self.manager.play_copy(row,game,threading.Event(),lambda _:None),'World')
        copy=self.manager.play_copy(row,game,threading.Event(),lambda _:None,force_copy=True)
        self.assertNotEqual(copy,'World')
        self.assertTrue((folder/'level.dat').is_file())

    def test_cancel_removes_only_own_partial_copy_and_keeps_source(self):
        folder=world_fixture(self.root/'official'/'saves'/'World')
        row=self.manager.scan()[0]
        cancel=threading.Event()
        cancel.set()
        with self.assertRaises(core.Cancelled):
            self.manager.play_copy(row,self.root/'target',cancel,lambda _:None)
        self.assertTrue((folder/'level.dat').is_file())
        self.assertEqual(list((self.root/'target'/'saves').iterdir()),[])

    def test_recursive_target_and_locked_world_are_rejected(self):
        folder=world_fixture(self.root/'official'/'saves'/'World')
        row=self.manager.scan()[0]
        with self.assertRaises(core.LauncherError):
            self.manager.play_copy(row,folder/'nested',threading.Event(),lambda _:None)
        with patch('blockwerk.worlds.world_unlocked',side_effect=core.LauncherError('Locked')):
            with self.assertRaises(core.LauncherError):
                self.manager.play_copy(row,self.root/'target',threading.Event(),lambda _:None)

    def test_snapshot_category_and_prepared_snapshot_validation(self):
        versions=[{'id':'1.20.1','type':'release'},{'id':'23w14a','type':'snapshot'},{'id':'b1.7.3','type':'old_beta'}]
        self.assertEqual(core.filter_versions(versions,'Snapshots'),[versions[1]])
        self.assertEqual(len(core.filter_versions(versions,'Alle')),2)
        core.atomic_json(self.service.root/'versions-cache.json',versions)
        self.service.check_supported_version('23w14a')
        with self.assertRaises(core.LauncherError):
            self.service.check_supported_version('totally-invented-version')
        self.service.settings.version_filter='Snapshots'
        self.service.settings.save(self.service.root)
        self.assertEqual(core.Settings.load(self.service.root).version_filter,'Snapshots')

    def test_quick_play_only_for_supported_metadata_and_real_world_paths(self):
        game=self.root/'game'
        world_fixture(game/'saves'/'My World')
        options={}
        self.assertFalse(core.add_world_launch(options,{},game,'My World'))
        self.assertNotIn('quickPlaySingleplayer',options)
        metadata={'arguments':{'game':['--quickPlaySingleplayer','${quickPlaySingleplayer}']}}
        self.assertTrue(core.add_world_launch(options,metadata,game,'My World'))
        self.assertEqual(options['quickPlaySingleplayer'],'My World')
        with self.assertRaises(core.LauncherError):
            core.add_world_launch({},metadata,game,'../escape')


if __name__=='__main__':
    unittest.main()
