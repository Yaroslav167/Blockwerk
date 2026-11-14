"""Publish a local/HTTPS launcher feed from finished archives; performs no upload."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from blockwerk.core import VERSION
from blockwerk.updates import https_url


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--base-url',help='Optional HTTPS directory containing these same published archives')
    args=parser.parse_args()
    root=Path(args.output_dir).resolve()
    if args.base_url:https_url(args.base_url)
    assets={}
    names={'win32-x86_64':'Blockwerk-Windows.zip','linux-x86_64':'Blockwerk-Linux-Quellpaket.tar.gz','linux-arm64':'Blockwerk-Linux-Quellpaket.tar.gz',
           'darwin-arm64':'Blockwerk-macOS-Quellpaket.zip','darwin-x86_64':'Blockwerk-macOS-Quellpaket.zip'}
    windows=root/names['win32-x86_64']
    with zipfile.ZipFile(windows) as archive:
        release=json.loads(archive.read('Blockwerk-Windows/release.json'))
        if release.get('version')!=VERSION or release.get('app')!='Blockwerk':
            raise SystemExit('Build/version mismatch; rebuild the Windows archive first')
    for key,name in names.items():
        file=root/name
        if not file.is_file():continue
        with file.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        item={'filename':name,'sha256':digest,'size':file.stat().st_size,'kind':'native' if key.startswith('win32') else 'source'}
        if args.base_url:item['url']=args.base_url.rstrip('/')+'/'+name
        assets[key]=item
    feed={'schema':1,'version':VERSION,'notes':'Eigene Microsoft-App-ID hinterlegt; Minecraft-API-Freigabe weiterhin offen, lokaler Modus bleibt erhalten.','assets':assets}
    target=root/'Blockwerk-Updates.json'
    temp=target.with_suffix('.tmp')
    temp.write_text(json.dumps(feed,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(target)
    print('Created update feed:',target)


if __name__=='__main__':main()
