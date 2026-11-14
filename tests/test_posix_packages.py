import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import threading
import unittest
import types
from unittest.mock import patch
import zipfile
from blockwerk.source_updates import stage_source, apply_source, MANIFEST
from blockwerk.updates import platform_key
from blockwerk.core import check_runtime_platform, LauncherError

ROOT = Path(__file__).resolve().parent.parent


def source(folder, version, body):
    files = {'main.py': body, 'tools/bootstrap.py': b'# bootstrap',
             'start-linux.sh': b'#!/bin/sh\n', 'start-macos.command': b'#!/bin/sh\n',
             'launcher-auth.json': b'{}', 'update-source.json': b'{}'}
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        path=folder/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    data={'schema':1,'app':'Blockwerk','kind':'source','version':version,
          'files':{n:hashlib.sha256(v).hexdigest() for n,v in files.items()}}
    (folder/MANIFEST).write_text(json.dumps(data),encoding='utf-8')


class PosixPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.install=self.root/'Blockwerk'
        source(self.install,'0.9.0',b'# old')

    def package(self, tar=False, extra=None):
        new=self.root/'publisher';source(new,'0.10.0',b'# new')
        target=self.root/('new.tar.gz' if tar else 'new.zip')
        if tar:
            with tarfile.open(target,'w:gz') as archive:
                for file in new.rglob('*'):
                    if file.is_file():archive.add(file,arcname='Blockwerk/'+file.relative_to(new).as_posix())
                if extra:
                    info=tarfile.TarInfo(extra);info.type=tarfile.SYMTYPE;info.linkname='/tmp/escape'
                    archive.addfile(info)
        else:
            with zipfile.ZipFile(target,'w') as archive:
                for file in new.rglob('*'):
                    if file.is_file():archive.write(file,'Blockwerk/'+file.relative_to(new).as_posix())
                if extra:archive.writestr(extra,'escape')
        return target,hashlib.sha256(target.read_bytes()).hexdigest()

    def stage(self, tar=False, extra=None):
        file,digest=self.package(tar,extra)
        return stage_source(self.install,file,'0.10.0',digest,threading.Event())

    def test_zip_and_tar_source_updates_preserve_private_data_and_config(self):
        for tar in (False,True):
            with self.subTest(tar=tar):
                source(self.install,'0.9.0',b'# old')
                (self.install/'launcher-auth.json').write_bytes(b'PRIVATE-CONFIG-TEST')
                (self.install/'update-source.json').write_bytes(b'PRIVATE-FEED-TEST')
                personal=self.install/'instances'/'world.dat'
                personal.parent.mkdir(exist_ok=True);personal.write_bytes(b'WORLD-TEST')
                stage=self.stage(tar)
                result=apply_source({'schema':1,'install_dir':str(self.install),'stage_dir':str(stage),
                                     'version':'0.10.0','platform':'darwin' if not tar else 'linux'},restart=False)
                self.assertEqual((self.install/'main.py').read_bytes(),b'# new')
                self.assertEqual((Path(result['backup'])/'main.py').read_bytes(),b'# old')
                self.assertEqual(personal.read_bytes(),b'WORLD-TEST')
                self.assertEqual((self.install/'launcher-auth.json').read_bytes(),b'PRIVATE-CONFIG-TEST')

    def test_archive_traversal_and_tar_links_are_rejected(self):
        for tar,extra in ((False,'Blockwerk/../escape.py'),(True,'Blockwerk/link.py')):
            with self.subTest(tar=tar):
                with self.assertRaises(ValueError):self.stage(tar,extra)
                self.assertFalse(list(self.root.glob('.Blockwerk-next-source-*')))
                self.assertEqual((self.install/'main.py').read_bytes(),b'# old')

    def test_local_edits_and_changed_staged_files_are_rejected(self):
        stage=self.stage();(self.install/'main.py').write_bytes(b'# local work')
        job={'schema':1,'install_dir':str(self.install),'stage_dir':str(stage),'version':'0.10.0'}
        with self.assertRaises(ValueError):apply_source(job,restart=False)
        self.assertEqual((self.install/'main.py').read_bytes(),b'# local work')
        source(self.install,'0.9.0',b'# old');(stage/'main.py').write_bytes(b'# changed')
        with self.assertRaises(ValueError):apply_source(job,restart=False)

    def test_failed_restart_restores_previous_files(self):
        stage=self.stage()
        job={'schema':1,'install_dir':str(self.install),'stage_dir':str(stage),'version':'0.10.0','platform':'linux'}
        with patch('blockwerk.source_updates.subprocess.Popen',side_effect=OSError('TEST')):
            with self.assertRaises(OSError):apply_source(job)
        self.assertEqual((self.install/'main.py').read_bytes(),b'# old')

    def test_unchanged_publisher_defaults_receive_new_app_id(self):
        stage=self.root/'.Blockwerk-next-source-defaults'
        source(stage,'0.10.0',b'# new')
        config=stage/'launcher-auth.json'
        config.write_text('{"client_id":"TEST-PUBLIC-CLIENT-ID"}')
        metadata=json.loads((stage/MANIFEST).read_text())
        metadata['files']['launcher-auth.json']=hashlib.sha256(config.read_bytes()).hexdigest()
        (stage/MANIFEST).write_text(json.dumps(metadata))
        apply_source({'schema':1,'install_dir':str(self.install),'stage_dir':str(stage),
                      'version':'0.10.0','platform':'linux'},restart=False)
        self.assertEqual((self.install/'launcher-auth.json').read_bytes(),config.read_bytes())

    def test_architecture_specific_feed_keys_and_runtime_fingerprints(self):
        for system,machine,expected in [('linux','aarch64','linux-arm64'),('darwin','arm64','darwin-arm64'),('darwin','x86_64','darwin-x86_64')]:
            with patch('blockwerk.updates.sys.platform',system),patch('blockwerk.updates.platform.machine',return_value=machine):
                self.assertEqual(platform_key(),expected)
        spec=importlib.util.spec_from_file_location('bootstrap',ROOT/'tools'/'bootstrap.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertNotEqual(module.fingerprint(b'a','arm64'),module.fingerprint(b'a','x86_64'))
        self.assertNotEqual(module.fingerprint(b'a','arm64'),module.fingerprint(b'b','arm64'))

    def test_linux_arm_requires_explicit_java_before_downloads(self):
        with patch('blockwerk.core.sys.platform','linux'),patch('blockwerk.core.platform.machine',return_value='aarch64'):
            with self.assertRaises(LauncherError):check_runtime_platform('')
            check_runtime_platform('/usr/lib/jvm/arm64/bin/java')

    def test_bootstrap_reuses_runtime_without_pip_on_second_start(self):
        spec=importlib.util.spec_from_file_location('bootstrap_test',ROOT/'tools'/'bootstrap.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        app=self.root/'Source folder with spaces';app.mkdir()
        (app/'requirements.txt').write_text('keyring==25.7.0\n')
        environment=self.root/'Data folder with spaces'
        def create_runtime(path):
            (path/'bin').mkdir(parents=True,exist_ok=True)
            (path/'bin'/'python').write_text('TEST-PYTHON')
        builder=types.SimpleNamespace(create=create_runtime)
        lock=types.SimpleNamespace(flock=lambda *args:None,LOCK_EX=1)
        with patch.object(module,'ROOT',app),patch.object(module,'data_root',return_value=environment), \
                patch.object(module.sys,'platform','linux'),patch.object(module.sys,'argv',['bootstrap','--check-platform','out.json']), \
                patch.dict('sys.modules',{'fcntl':lock}),patch.object(module.venv,'EnvBuilder',return_value=builder), \
                patch.object(module.platform,'platform',return_value='Linux TEST'), \
                patch.object(module.subprocess,'run',return_value=types.SimpleNamespace(returncode=0)) as run:
            self.assertEqual(module.main(),0)
            self.assertEqual(len(run.call_args_list),3)
            self.assertIn('-m',run.call_args_list[0].args[0])
            run.reset_mock()
            self.assertEqual(module.main(),0)
            self.assertEqual(len(run.call_args_list),1)
            self.assertIn(str(app/'main.py'),run.call_args.args[0])
        self.assertTrue((environment/'logs'/'launcher-start.log').is_file())

    def test_source_cancel_and_modified_download_leave_app_unchanged(self):
        file,digest=self.package()
        event=threading.Event();event.set()
        with self.assertRaises(InterruptedError):stage_source(self.install,file,'0.10.0',digest,event)
        file.write_bytes(b'changed')
        with self.assertRaises(ValueError):stage_source(self.install,file,'0.10.0',digest,threading.Event())
        self.assertEqual((self.install/'main.py').read_bytes(),b'# old')

    def test_minimum_os_requirements_match_qt_wheels(self):
        spec=importlib.util.spec_from_file_location('bootstrap_system',ROOT/'tools'/'bootstrap.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with patch.object(module.sys,'platform','darwin'),patch.object(module.platform,'mac_ver',return_value=('13.6',(),'')):
            with self.assertRaises(SystemExit):module.check_system()
        with patch.object(module.sys,'platform','linux'),patch.object(module.platform,'machine',return_value='aarch64'):
            with patch.object(module.platform,'libc_ver',return_value=('glibc','2.38')):
                with self.assertRaises(SystemExit):module.check_system()
            with patch.object(module.platform,'libc_ver',return_value=('glibc','2.39')):
                module.check_system()

    @unittest.skipIf(__import__('sys').platform=='win32','Executable bits require POSIX')
    def test_shell_scripts_remain_executable_after_update(self):
        stage=self.stage()
        self.assertTrue((stage/'start-linux.sh').stat().st_mode & 0o111)
