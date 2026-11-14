"""Standalone Windows updater. Uses only stdlib; runs outside the app folder."""
import argparse
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid


def wait_for_exit(pid,timeout=120):
    if not isinstance(pid,int) or pid<=0 or pid==os.getpid():
        raise ValueError('Invalid parent process')
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32]
    kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=kernel.OpenProcess(0x00100000,False,pid)
    if not handle:
        if ctypes.get_last_error()==87:return  # Process has already exited.
        raise OSError('The running launcher could not be checked')
    try:
        if kernel.WaitForSingleObject(handle,timeout*1000)!=0:
            raise TimeoutError('Launcher did not exit; update was not installed')
    finally:
        kernel.CloseHandle(handle)


def apply_update(job,restart=True):
    if not isinstance(job,dict) or job.get('schema')!=1:
        raise ValueError('Unknown update job')
    install_raw=Path(job['install_dir']);stage_raw=Path(job['stage_dir'])
    if not install_raw.is_absolute() or not stage_raw.is_absolute() or install_raw.is_symlink() or stage_raw.is_symlink():
        raise ValueError('Invalid update folders')
    install,stage=install_raw.resolve(),stage_raw.resolve()
    if (getattr(install,'is_junction',lambda:False)() or getattr(stage,'is_junction',lambda:False)()
            or install.parent!=stage.parent or not stage.name.startswith('.Blockwerk-next-')
            or install==stage or not install.is_dir() or not stage.is_dir()):
        raise ValueError('Update folders must be separate siblings')
    for folder in (install,stage):
        if not (folder/'Blockwerk.exe').is_file():
            raise ValueError('Missing launcher')
        release=json.loads((folder/'release.json').read_text(encoding='utf-8'))
        if release.get('app')!='Blockwerk':raise ValueError('Not a Blockwerk package')
        owned=release.get('owned_entries',[])
        if not owned or not isinstance(owned,list) or any(not isinstance(n,str) or Path(n).name!=n for n in owned):
            raise ValueError('Missing package inventory')
        if any(p.name not in owned for p in folder.iterdir()):
            raise ValueError('The app folder contains additional files; use a manual update')
    if release.get('version')!=job['version']:
        raise ValueError('Wrong staged version')
    backup=install.parent/('.Blockwerk-backup-'+uuid.uuid4().hex)
    install.rename(backup)
    try:
        stage.rename(install)
    except Exception:
        backup.rename(install)
        raise
    if restart:
        try:
            subprocess.Popen([str(install/'Blockwerk.exe')],cwd=install,
                stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        except Exception:
            # Preserve the rejected new package as well as restoring the old app.
            install.rename(stage)
            backup.rename(install)
            try:subprocess.Popen([str(install/'Blockwerk.exe')],cwd=install)
            except OSError:pass
            raise
    return {'installed':True,'version':job['version'],'backup':str(backup)}


def self_test():
    with tempfile.TemporaryDirectory(prefix='blockwerk-update-test-') as tmp:
        root=Path(tmp)
        install=root/'Blockwerk'
        stage=root/('.Blockwerk-next-'+uuid.uuid4().hex)
        install.mkdir();stage.mkdir()
        for folder,version in ((install,'0.7.0'),(stage,'0.7.1')):
            (folder/'Blockwerk.exe').write_bytes(version.encode())
            (folder/'release.json').write_text(json.dumps({'app':'Blockwerk','version':version,'owned_entries':['Blockwerk.exe','release.json']}))
        result=apply_update({'schema':1,'install_dir':str(install),'stage_dir':str(stage),'version':'0.7.1'},restart=False)
        assert (install/'Blockwerk.exe').read_bytes()==b'0.7.1'
        assert (Path(result['backup'])/'Blockwerk.exe').read_bytes()==b'0.7.0'
        return {'passed':True,'folder_replacement_verified':True,'previous_app_preserved':True,'real_app_started':False}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply')
    parser.add_argument('--self-test')
    args=parser.parse_args()
    if args.self_test:
        Path(args.self_test).write_text(json.dumps(self_test(),indent=2),encoding='utf-8')
        return 0
    if not args.apply:return 2
    job=json.loads(Path(args.apply).read_text(encoding='utf-8'))
    result_file=Path(job['result_file'])
    try:
        if sys.platform=='win32':wait_for_exit(job['pid'])
        result=apply_update(job)
    except Exception as error:
        result={'installed':False,'version':str(job.get('version','')),'error':type(error).__name__,
                'message':'Das Update konnte nicht installiert werden. Die vorherige App wurde soweit möglich wiederhergestellt.'}
        code=1
        previous=Path(job.get('install_dir',''))/'Blockwerk.exe'
        if not isinstance(error,TimeoutError) and previous.is_file():
            try:
                subprocess.Popen([str(previous)],cwd=previous.parent,
                    stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
            except OSError:pass
    else:code=0
    result_file.parent.mkdir(parents=True,exist_ok=True)
    result_file.write_text(json.dumps(result,indent=2),encoding='utf-8')
    return code


if __name__=='__main__':
    raise SystemExit(main())
