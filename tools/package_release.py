"""Package the finished native build and source, then publish a local feed."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile

EXCLUDED={'.git','__pycache__','.venv','build','dist','.pytest_cache'}
PRIVATE={'account.dpapi','settings.json','skins.json','updates-state.json','level.dat','worlds.json'}


def files_under(root):
    files=sorted(p for p in root.rglob('*') if p.is_file()
                 and not any(part in EXCLUDED for part in p.relative_to(root).parts))
    if not files or any(p.name in PRIVATE or p.suffix in ('.jar','.mca') for p in files):
        raise RuntimeError('Missing package or private/game data in package')
    return files


def source_mode(file):
    return 0o755 if file.suffix in ('.sh','.command') else 0o644


def zip_directory(output,root,name,prefix,source=False):
    files=files_under(root)
    target=output/name
    temporary=target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for file in files:
            path=prefix+'/'+file.relative_to(root).as_posix()
            info=zipfile.ZipInfo.from_file(file,path)
            info.create_system=3
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100000|(source_mode(file) if source else 0o644))<<16
            with file.open('rb') as reader,archive.open(info,'w') as writer:
                import shutil
                shutil.copyfileobj(reader,writer)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip():raise RuntimeError('Archive integrity failure')
        if source and not (archive.getinfo(prefix+'/start-macos.command').external_attr>>16)&0o111:
            raise RuntimeError('Missing executable permission')
    temporary.replace(target)
    print(name,len(files),'files',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--windows-dir',help='Optional separate finished native build folder')
    args=parser.parse_args()
    output=Path(args.output_dir).resolve()
    project=output/'Blockwerk-Projekt'
    # A managed source inventory enables non-destructive source updates on POSIX.
    sys.path.insert(0,str(project))
    from blockwerk.core import VERSION
    owned={file.relative_to(project).as_posix():hashlib.sha256(file.read_bytes()).hexdigest()
           for file in files_under(project) if file.name!='release-source.json'}
    publisher=json.loads((project/'launcher-auth.json').read_text(encoding='utf-8')).get('client_id','')
    (project/'release-source.json').write_text(json.dumps({'schema':1,'app':'Blockwerk',
        'kind':'source','version':VERSION,'publisher_client_id':publisher,'files':owned},indent=2),encoding='utf-8')
    native=Path(args.windows_dir).resolve() if args.windows_dir else output/'Blockwerk-Windows'
    zip_directory(output,native,'Blockwerk-Windows.zip','Blockwerk-Windows')
    zip_directory(output,project,'Blockwerk-Quellcode.zip','Blockwerk-Projekt',True)
    zip_directory(output,project,'Blockwerk-macOS-Quellpaket.zip','Blockwerk',True)
    name='Blockwerk-Linux-Quellpaket.tar.gz'
    temporary=output/(name+'.tmp')
    files=files_under(project)
    with tarfile.open(temporary,'w:gz') as archive:
        for file in files:
            info=archive.gettarinfo(str(file),'Blockwerk/'+file.relative_to(project).as_posix())
            info.mode=source_mode(file)
            info.uid=info.gid=0
            info.uname=info.gname=''
            with file.open('rb') as stream:archive.addfile(info,stream)
    with tarfile.open(temporary) as archive:
        if archive.getmember('Blockwerk/start-linux.sh').mode!=0o755 or len(archive.getmembers())!=len(files):
            raise RuntimeError('Linux archive integrity failure')
    temporary.replace(output/name)
    subprocess.run([sys.executable,str(project/'tools'/'create_update_feed.py'),'--output-dir',str(output)],check=True)
    names=['Blockwerk-Windows.zip','Blockwerk-Quellcode.zip',name,'Blockwerk-macOS-Quellpaket.zip','Blockwerk-Updates.json']
    sums=[]
    for name in names:
        with (output/name).open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        sums.append(digest+'  '+name)
    (output/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n',encoding='ascii')
    print('Archives, feed and checksums verified. Linux/macOS contain source.',flush=True)


if __name__=='__main__':main()
