import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock,patch
import zipfile
from PySide6.QtGui import QImage
from blockwerk import core
from blockwerk.skins import SkinStore,load_skin,starter_skin
from blockwerk.updates import UpdateManager,WEEK,RETRY,platform_key,https_url
from tools.update_bootstrap import apply_update


class SkinTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.store=SkinStore(self.root)
        self.store.ensure_starters()

    def test_three_original_skins_are_valid_and_selection_persists(self):
        rows=self.store.data()['items']
        self.assertEqual(len(rows),3)
        self.assertEqual(load_skin(self.store.path(rows[0]['id'])).size().width(),64)
        self.store.select(rows[1]['id'],'slim')
        selected=SkinStore(self.root).selected()
        self.assertEqual(selected['id'],rows[1]['id'])
        self.assertEqual(selected['variant'],'slim')

    def test_import_preserves_png_deduplicates_and_supports_legacy(self):
        file=self.root/'my-skin.png'
        image=starter_skin('#113355','#442211','#eedd44')
        image.save(str(file))
        raw=file.read_bytes()
        identifier=self.store.add(file)
        self.assertEqual(self.store.path(identifier).read_bytes(),raw)
        self.assertEqual(self.store.add(file),identifier)
        legacy=self.root/'legacy.png'
        image.copy(0,0,64,32).save(str(legacy))
        identifier=self.store.add(legacy,'slim')
        self.assertEqual(self.store.selected()['variant'],'classic')
        with self.assertRaises(core.LauncherError):self.store.select(identifier,'slim')

    def test_non_png_and_oversized_dimensions_are_rejected_before_decode(self):
        file=self.root/'bad.png'
        file.write_bytes(b'not png')
        with self.assertRaises(core.LauncherError):load_skin(file)
        file.write_bytes(b'\x89PNG\r\n\x1a\n'+b'\x00\x00\x00\x0dIHDR'+struct.pack('>II',100000,100000))
        with self.assertRaises(core.LauncherError):load_skin(file)

    def fake_game(self,formats):
        service=core.LauncherService(self.root/'game-data')
        base=service.game_root/'versions'/'1.20.1'
        base.mkdir(parents=True)
        core.atomic_json(base/'1.20.1.json',{'id':'1.20.1','type':'release'})
        with zipfile.ZipFile(base/'1.20.1.jar','w') as jar:
            jar.writestr('version.json',json.dumps({'pack_version':formats}))
            for model in ('wide','slim'):
                jar.writestr('assets/minecraft/textures/entity/player/'+model+'/alex.png',b'TEST-ONLY')
        return service

    def test_local_pack_uses_real_format_fields_and_preserves_existing_options(self):
        service=self.fake_game({'resource':15})
        game=self.root/'instance'
        game.mkdir()
        original='music:0.5\nresourcePacks:["vanilla","file/my-own-pack.zip"]\n'
        (game/'options.txt').write_text(original)
        target=self.store.local_pack(service,'1.20.1',game)
        self.assertEqual((game/'options.txt.blockwerk-before-skin').read_text(),original)
        self.assertIn('file/my-own-pack.zip',(game/'options.txt').read_text())
        self.assertIn('file/blockwerk-local-skin.zip',(game/'options.txt').read_text())
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(json.loads(archive.read('pack.mcmeta'))['pack']['pack_format'],15)
            self.assertIn('assets/minecraft/textures/entity/player/slim/alex.png',archive.namelist())

    def test_new_resource_major_minor_and_invalid_options_are_handled(self):
        service=self.fake_game({'resource_major':97,'resource_minor':1})
        game=self.root/'instance'
        target=self.store.local_pack(service,'1.20.1',game)
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(json.loads(archive.read('pack.mcmeta'))['pack']['min_format'],[97,1])
        (game/'options.txt').write_text('resourcePacks:broken\n')
        with self.assertRaises(core.LauncherError):self.store.local_pack(service,'1.20.1',game)
        self.assertEqual((game/'options.txt').read_text(),'resourcePacks:broken\n')

    def test_account_skin_requires_real_account_and_upload_is_never_implicit(self):
        service=core.LauncherService(self.root/'account')
        service.settings.client_id='09af2a7b-7b13-441a-81d8-1ced7aa8a88b'
        with patch('blockwerk.skins.requests.post') as upload:
            with self.assertRaises(core.LauncherError):self.store.apply_account(service,threading.Event())
        upload.assert_not_called()

    def test_explicit_account_upload_refreshes_license_and_uses_selected_variant(self):
        service=core.LauncherService(self.root/'account')
        service.settings.client_id='09af2a7b-7b13-441a-81d8-1ced7aa8a88b'
        profile={'id':'4a58994df2aa41d996a25c5e9f657177','name':'TestPlayer','access_token':'TEST-ONLY','refresh_token':'TEST-REFRESH'}
        account={'client_id':service.settings.client_id,'refresh_token':'TEST-REFRESH'}
        with patch.object(service.accounts,'read',return_value=account), \
             patch.object(core.microsoft_account,'complete_refresh',return_value=profile), \
             patch.object(core.microsoft_account,'get_store_information',return_value={'items':[{'name':'game_minecraft'}]}), \
             patch.object(service.accounts,'write'),patch('blockwerk.skins.requests.post',return_value=Mock(status_code=200)) as upload:
            self.store.apply_account(service,threading.Event())
        self.assertEqual(upload.call_args.kwargs['data']['variant'],'classic')
        self.assertEqual(upload.call_args.kwargs['headers']['Authorization'],'Bearer TEST-ONLY')


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.manager=UpdateManager(self.root/'data')
        self.publisher=self.root/'published'
        self.publisher.mkdir()

    def package(self,extra=None):
        file=self.publisher/'Blockwerk-Windows.zip'
        release={'app':'Blockwerk','version':'0.10.0','platform':platform_key(),
                 'owned_entries':['Blockwerk.exe','BlockwerkUpdater.exe','release.json','_internal']}
        with zipfile.ZipFile(file,'w') as archive:
            archive.writestr('Blockwerk-Windows/Blockwerk.exe',b'NEW-APP-TEST')
            archive.writestr('Blockwerk-Windows/BlockwerkUpdater.exe',b'HELPER-TEST')
            archive.writestr('Blockwerk-Windows/release.json',json.dumps(release))
            archive.writestr('Blockwerk-Windows/_internal/test.dat',b'NEW-DATA-TEST')
            if extra:archive.writestr(extra,b'PATH-TEST')
        asset={'filename':file.name,'size':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
        feed=self.publisher/'Blockwerk-Updates.json'
        core.atomic_json(feed,{'schema':1,'version':'0.10.0','assets':{platform_key():asset}})
        self.manager.set_source('local',str(feed))
        return file

    def install_folder(self):
        install=self.root/'Blockwerk'
        install.mkdir()
        (install/'Blockwerk.exe').write_bytes(b'OLD-APP-TEST')
        (install/'BlockwerkUpdater.exe').write_bytes(b'OLD-HELPER-TEST')
        core.atomic_json(install/'release.json',{'app':'Blockwerk','version':'0.7.0',
            'owned_entries':['Blockwerk.exe','BlockwerkUpdater.exe','release.json']})
        return install

    def test_weekly_checks_and_off_switch_persist(self):
        self.package()
        now=100*WEEK
        self.assertTrue(self.manager.due(now))
        self.manager.check(now)
        self.assertFalse(self.manager.due(now+WEEK-1))
        self.assertTrue(self.manager.due(now+WEEK))
        self.manager.set_automatic(False)
        self.assertFalse(UpdateManager(self.root/'data').due(now+2*WEEK))

    def test_failed_check_retries_after_hour_without_marking_success(self):
        self.package()
        (self.publisher/'Blockwerk-Updates.json').write_text('broken')
        now=100*WEEK
        with self.assertRaises(core.LauncherError):self.manager.check(now)
        self.assertEqual(self.manager.state['last_check'],0)
        self.assertFalse(self.manager.due(now+60))
        self.assertTrue(self.manager.due(now+RETRY))

    def test_local_download_checks_hash_and_cancel_keeps_old_app(self):
        file=self.package()
        info=self.manager.check()
        self.assertTrue(info['newer'])
        target=self.manager.download(info,threading.Event(),lambda _:None,lambda *_:None)
        self.assertEqual(target.read_bytes(),file.read_bytes())
        verified=target.read_bytes()
        file.write_bytes(b'changed')
        with self.assertRaises(core.LauncherError):self.manager.download(info,threading.Event(),lambda _:None,lambda *_:None)
        self.assertEqual(target.read_bytes(),verified)
        cancel=threading.Event();cancel.set()
        with self.assertRaises(core.Cancelled):self.manager.download(info,cancel,lambda _:None,lambda *_:None)
        self.assertFalse(list(target.parent.glob('*.part')))

    def test_no_downgrades_and_no_insecure_remote_url(self):
        self.package()
        feed=self.publisher/'Blockwerk-Updates.json'
        data=json.loads(feed.read_text());data['version']='0.6.0';core.atomic_json(feed,data)
        self.assertFalse(self.manager.check()['newer'])
        for url in ('http://example.org/feed.json','https://user:password@example.org/feed.json','file:///feed.json'):
            with self.assertRaises(core.LauncherError):https_url(url)

    def test_publisher_package_cannot_escape_local_update_directory(self):
        self.package()
        feed=self.publisher/'Blockwerk-Updates.json'
        data=json.loads(feed.read_text());data['assets'][platform_key()]['filename']='../escape.zip';core.atomic_json(feed,data)
        with self.assertRaises(core.LauncherError):self.manager.check()

    @unittest.skipUnless(sys.platform=='win32','Windows native staging')
    def test_verified_stage_and_helper_preserve_previous_app_and_external_data(self):
        self.package();info=self.manager.check()
        package=self.manager.download(info,threading.Event(),lambda _:None,lambda *_:None)
        install=self.install_folder()
        sentinel=self.root/'data'/'world-save.txt';sentinel.write_text('KEEP-WORLD-TEST')
        result=self.manager.stage_windows(info,package,threading.Event(),lambda _:None,install_dir=install)
        job=json.loads(Path(result['job']).read_text())
        applied=apply_update(job,restart=False)
        self.assertEqual((install/'Blockwerk.exe').read_bytes(),b'NEW-APP-TEST')
        self.assertEqual((Path(applied['backup'])/'Blockwerk.exe').read_bytes(),b'OLD-APP-TEST')
        self.assertEqual(sentinel.read_text(),'KEEP-WORLD-TEST')

    @unittest.skipUnless(sys.platform=='win32','Windows native staging')
    def test_unsafe_archive_and_mixed_app_folders_are_rejected(self):
        self.package('Blockwerk-Windows/../escaped.txt');info=self.manager.check()
        package=self.manager.download(info,threading.Event(),lambda _:None,lambda *_:None)
        install=self.install_folder()
        with self.assertRaises(core.LauncherError):self.manager.stage_windows(info,package,threading.Event(),lambda _:None,install_dir=install)
        self.assertEqual((install/'Blockwerk.exe').read_bytes(),b'OLD-APP-TEST')
        (install/'personal-file.txt').write_text('KEEP')
        with self.assertRaises(core.LauncherError):self.manager.stage_windows(info,package,threading.Event(),lambda _:None,install_dir=install)

    def test_helper_rolls_back_on_replacement_failure(self):
        install=self.install_folder()
        stage=self.root/'.Blockwerk-next-test'
        stage.mkdir()
        (stage/'Blockwerk.exe').write_bytes(b'NEW')
        core.atomic_json(stage/'release.json',{'app':'Blockwerk','version':'0.10.0','owned_entries':['Blockwerk.exe','release.json']})
        original=Path.rename
        def rename(path,target):
            if path==stage.resolve():raise OSError('TEST simulated rename failure')
            return original(path,target)
        with patch.object(Path,'rename',rename):
            with self.assertRaises(OSError):apply_update({'schema':1,'install_dir':str(install),'stage_dir':str(stage),'version':'0.10.0'},restart=False)
        self.assertEqual((install/'Blockwerk.exe').read_bytes(),b'OLD-APP-TEST')


if __name__=='__main__':unittest.main()
