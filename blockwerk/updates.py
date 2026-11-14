"""Weekly launcher-only checks, verified downloads and staged Windows updates."""
from __future__ import annotations
from .i18n import tr
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import stat
import subprocess
import sys
import time
import threading
from urllib.parse import urlsplit
import uuid
import zipfile
import requests
from .core import LauncherError, Cancelled, VERSION, atomic_json

WEEK = 7 * 24 * 60 * 60
RETRY = 60 * 60
MAX_PACKAGE = 512 * 1024 * 1024
MAX_EXPANDED = 1536 * 1024 * 1024


def release_version(value):
    if not isinstance(value,str) or not re.fullmatch(r"\d{1,9}\.\d{1,9}\.\d{1,9}",value):
        raise LauncherError(tr("Die Update-Version ist ungültig."))
    return tuple(map(int,value.split('.')))


def platform_key():
    machine=platform.machine().lower()
    machine={"amd64":"x86_64","aarch64":"arm64"}.get(machine,machine)
    return sys.platform+"-"+machine


def https_url(value):
    if not isinstance(value,str) or len(value)>2048:
        raise LauncherError(tr("Die Updateadresse ist ungültig."))
    parsed=urlsplit(value)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise LauncherError(tr("Web-Updates benötigen eine HTTPS-Adresse ohne Anmeldedaten."))
    return value


def bundled_source():
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))
    try:
        data=json.loads((root/'update-source.json').read_text(encoding='utf-8'))
        if data.get('schema')!=1 or data.get('kind') not in ('local','https') or not isinstance(data.get('location'),str):
            raise ValueError
        if data['kind'] == 'local' and not data['location']:
            sibling = root.parent / 'Blockwerk-Updates.json'
            if sibling.is_file():return {'kind': 'local', 'location': str(sibling)}
        return {'kind':data['kind'],'location':data['location']}
    except FileNotFoundError:
        return {'kind':'local','location':''}
    except (OSError,ValueError,TypeError,AttributeError):
        raise LauncherError(tr("Die mitgelieferte Updatequelle ist ungültig.")) from None


class UpdateManager:
    def __init__(self, root: Path):
        self.root=root
        self.state_path=root/'updates-state.json'
        self.work=root/'updates'
        self.lock=threading.RLock()
        try:
            self.state=json.loads(self.state_path.read_text(encoding='utf-8'))
            if not isinstance(self.state,dict) or self.state.get('schema')!=1:
                raise ValueError
        except (OSError,ValueError):
            self.state={'schema':1,'automatic':True,'last_check':0,'last_attempt':0}
        source=self.state.get('source')
        self.source=source if isinstance(source,dict) and source.get('kind') in ('local','https') and isinstance(source.get('location'),str) else bundled_source()

    def save(self):
        with self.lock:
            self.state_path.parent.mkdir(parents=True,exist_ok=True)
            temporary=self.state_path.with_name('updates-state-'+uuid.uuid4().hex+'.tmp')
            try:
                temporary.write_text(json.dumps(self.state,ensure_ascii=False,indent=2),encoding='utf-8')
                temporary.replace(self.state_path)
            finally:temporary.unlink(missing_ok=True)

    def set_source(self,kind,location):
        if kind=='https':
            location=https_url(location.strip())
        elif kind=='local':
            path=Path(location).expanduser().resolve()
            if not path.is_file():
                raise LauncherError(tr("Bitte eine vorhandene Blockwerk-Update-JSON auswählen."))
            location=str(path)
        else:
            raise LauncherError(tr("Unbekannte Updatequelle."))
        with self.lock:
            self.source={'kind':kind,'location':location}
            self.state.update(source=self.source,last_check=0,last_attempt=0,last_error='')
            self.save()

    def set_automatic(self,enabled):
        with self.lock:
            self.state['automatic']=bool(enabled)
            self.save()

    def due(self,now=None):
        now=time.time() if now is None else now
        if not self.state.get('automatic',True) or not self.source.get('location'):
            return False
        try:
            checked=float(self.state.get('last_check',0));attempt=float(self.state.get('last_attempt',0))
        except (TypeError,ValueError):
            checked=attempt=0
        if not math.isfinite(checked):checked=0
        if not math.isfinite(attempt):attempt=0
        # A corrected system clock must not suppress updates indefinitely.
        return (now<checked or now-checked>=WEEK) and (now<attempt or now-attempt>=RETRY)

    def _manifest(self,source=None):
        source=dict(self.source) if source is None else source
        location=source['location']
        if not location:
            raise LauncherError(tr("Bitte einen Updateordner oder eine HTTPS-Updatequelle hinterlegen."))
        if source['kind']=='local':
            try:
                with Path(location).open('rb') as stream:
                    raw=stream.read(256*1024+1)
            except OSError:
                raise LauncherError(tr("Die lokale Updatequelle ist nicht erreichbar. Bitte den Updateordner prüfen oder neu auswählen.")) from None
        else:
            with requests.get(https_url(location),stream=True,timeout=(10,30)) as response:
                response.raise_for_status()
                https_url(response.url)
                chunks=[];total=0
                for part in response.iter_content(32768):
                    total+=len(part)
                    if total>256*1024:raise LauncherError(tr("Die Updatebeschreibung ist zu groß."))
                    chunks.append(part)
                raw=b''.join(chunks)
        if len(raw)>256*1024:
            raise LauncherError(tr("Die Updatebeschreibung ist zu groß."))
        try:
            return json.loads(raw)
        except (ValueError,UnicodeError):
            raise LauncherError(tr("Die Updatebeschreibung ist keine gültige JSON-Datei.")) from None

    def check(self,now=None):
        now=time.time() if now is None else now
        with self.lock:
            source=dict(self.source)
            self.state['last_attempt']=now
            self.save()
        try:
            data=self._manifest(source)
            if not isinstance(data,dict) or data.get('schema')!=1:
                raise LauncherError(tr("Dieses Updateformat wird nicht unterstützt."))
            version=data.get('version')
            newer=release_version(version)>release_version(VERSION)
            assets=data.get('assets',{})
            if not isinstance(assets,dict):raise LauncherError(tr("Die Update-Paketliste ist ungültig."))
            result={'version':version,'newer':newer,'notes':str(data.get('notes',''))[:4000],
                    'available':False,'platform':platform_key(),'source':source}
            if newer and result['platform'] in assets:
                asset=assets[result['platform']]
                if not isinstance(asset,dict) or not re.fullmatch(r'[a-fA-F0-9]{64}',str(asset.get('sha256',''))):
                    raise LauncherError(tr("Dem Update fehlt eine gültige SHA256-Prüfsumme."))
                size=asset.get('size')
                if type(size) is not int or not 0<size<=MAX_PACKAGE:
                    raise LauncherError(tr("Die Updategröße ist ungültig oder zu groß."))
                if source['kind']=='local':
                    filename=asset.get('filename','')
                    if not isinstance(filename,str) or not filename or Path(filename).name!=filename or any(c in filename for c in ('/','\\',':')):
                        raise LauncherError(tr("Das Updatepaket muss direkt im gewählten Updateordner liegen."))
                    file=(Path(source['location']).parent/filename).resolve()
                    if file.parent!=Path(source['location']).resolve().parent:
                        raise LauncherError(tr("Ungültiger Updatepaket-Pfad."))
                    package_source=str(file)
                else:
                    package_source=https_url(asset.get('url',''))
                result.update(available=True,asset=dict(asset),package_source=package_source)
            with self.lock:
                if self.source==source:
                    self.state.update(last_check=now,last_error='',latest=version)
                    self.save()
            return result
        except Exception:
            with self.lock:
                if self.source==source:
                    self.state['last_error']='Updateprüfung fehlgeschlagen. Vorhandene App bleibt verwendbar.'
                    self.save()
            raise

    def download(self,info,cancel,notify,progress):
        if not info.get('available') or not info.get('newer'):
            raise LauncherError(tr("Es steht kein passendes neues Update bereit."))
        release_version(info['version'])
        target_dir=self.work/info['version']
        target_dir.mkdir(parents=True,exist_ok=True)
        label=info['asset'].get('filename','')
        target=target_dir/('package.tar.gz' if isinstance(label,str) and label.endswith('.tar.gz') else 'package.zip')
        part=target_dir/('package-'+uuid.uuid4().hex+'.part')
        expected=info['asset']['size']
        digest=hashlib.sha256();total=0
        notify(tr("Launcher-Update wird heruntergeladen und geprüft …"))
        try:
            def write(chunks,output):
                nonlocal total
                for chunk in chunks:
                    if cancel.is_set():raise Cancelled(tr("Update-Download abgebrochen."))
                    if not chunk:continue
                    total+=len(chunk)
                    if total>expected or total>MAX_PACKAGE:raise LauncherError(tr("Das Updatepaket ist größer als angekündigt."))
                    output.write(chunk);digest.update(chunk);progress(total,expected)
            with part.open('wb') as output:
                if info['source']['kind']=='local':
                    with Path(info['package_source']).open('rb') as source:
                        write(iter(lambda:source.read(262144),b''),output)
                else:
                    with requests.get(https_url(info['package_source']),stream=True,timeout=(15,45)) as response:
                        response.raise_for_status();https_url(response.url)
                        write(response.iter_content(262144),output)
            if total!=expected or digest.hexdigest().lower()!=info['asset']['sha256'].lower():
                raise LauncherError(tr("Die Update-Prüfsumme stimmt nicht. Das Paket wird nicht installiert."))
            if cancel.is_set():raise Cancelled(tr("Update-Download abgebrochen."))
            part.replace(target)
            return target
        finally:
            part.unlink(missing_ok=True)

    def stage_windows(self,info,package: Path,cancel,notify,install_dir=None):
        if sys.platform!='win32' or (install_dir is None and not getattr(sys,'frozen',False)):
            raise LauncherError(tr("Automatische Installation gibt es für das portable Windows-Paket. Dieses Paket bitte manuell entpacken."))
        install=(install_dir or Path(sys.executable).parent).resolve()
        if self.root.resolve().is_relative_to(install):
            raise LauncherError(tr("Der Datenordner liegt im App-Ordner. Bitte das Update manuell installieren, damit deine Spieldaten erhalten bleiben."))
        if not (install/'Blockwerk.exe').is_file() or not (install/'release.json').is_file():
            raise LauncherError(tr("Dieser App-Ordner ist kein unterstütztes Blockwerk-Paket."))
        current=json.loads((install/'release.json').read_text(encoding='utf-8'))
        owned=current.get('owned_entries',[])
        if not owned or any(p.name not in owned for p in install.iterdir()):
            raise LauncherError(tr("Der App-Ordner enthält weitere Dateien. Bitte das Paket manuell in einen eigenen App-Ordner entpacken."))
        with package.open('rb') as stream:
            if hashlib.file_digest(stream,'sha256').hexdigest()!=info['asset']['sha256'].lower():
                raise LauncherError(tr("Das Updatepaket wurde nach dem Download verändert."))
        stage=install.parent/('.Blockwerk-next-'+uuid.uuid4().hex)
        prefix='Blockwerk-Windows/'
        try:
            with zipfile.ZipFile(package) as archive:
                members=[];seen=set();total=0
                for item in archive.infolist():
                    name=item.filename
                    path=PurePosixPath(name)
                    if ('\\' in name or not name.startswith(prefix) or path.is_absolute() or '..' in path.parts
                            or stat.S_ISLNK(item.external_attr>>16) or item.flag_bits&1):
                        raise LauncherError(tr("Das Updatearchiv enthält einen unzulässigen Dateipfad."))
                    relative=PurePosixPath(name[len(prefix):])
                    if relative.is_absolute():raise LauncherError(tr("Absoluter Pfad im Updatearchiv."))
                    if str(relative)=='.':continue
                    reserved={'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}
                    if any(':' in p or p.endswith((' ','.')) or p.split('.')[0].upper() in reserved for p in relative.parts):
                        raise LauncherError(tr("Ungültiger Windows-Pfad im Update."))
                    key=str(relative).casefold()
                    if key in seen:raise LauncherError(tr("Das Updatearchiv enthält doppelte Dateinamen."))
                    seen.add(key);total+=item.file_size
                    if total>MAX_EXPANDED or len(seen)>10000:
                        raise LauncherError(tr("Das entpackte Update ist zu groß."))
                    members.append((item,relative))
                if not {'blockwerk.exe','release.json','blockwerkupdater.exe'}<=seen:
                    raise LauncherError(tr("Im Updatepaket fehlen App-Dateien."))
                if archive.getinfo(prefix+'release.json').file_size>65536:
                    raise LauncherError(tr("Die Paketbeschreibung ist zu groß."))
                release=json.loads(archive.read(prefix+'release.json'))
                if release.get('app')!='Blockwerk' or release.get('version')!=info['version'] or release.get('platform')!=platform_key():
                    raise LauncherError(tr("Updatebeschreibung und App-Paket passen nicht zusammen."))
                stage.mkdir()
                notify(tr("Das geprüfte Update wird neben dem App-Ordner vorbereitet …"))
                for item,relative in members:
                    if cancel.is_set():raise Cancelled(tr("Update-Vorbereitung abgebrochen."))
                    destination=stage.joinpath(*relative.parts)
                    if item.is_dir():destination.mkdir(parents=True,exist_ok=True)
                    else:
                        destination.parent.mkdir(parents=True,exist_ok=True)
                        with archive.open(item) as source,destination.open('wb') as output:
                            shutil.copyfileobj(source,output)
            if cancel.is_set():raise Cancelled(tr("Update-Vorbereitung abgebrochen."))
            job_dir=self.work/'jobs'/uuid.uuid4().hex
            job_dir.mkdir(parents=True)
            helper=job_dir/'BlockwerkUpdater.exe'
            shutil.copy2(install/'BlockwerkUpdater.exe',helper)
            job=job_dir/'job.json'
            atomic_json(job,{'schema':1,'pid':os.getpid(),'install_dir':str(install),'stage_dir':str(stage),
                'version':info['version'],'result_file':str(self.work/'last-result.json')})
            return {'job':str(job),'helper':str(helper)}
        except Exception:
            if stage.exists() and stage.parent==install.parent and stage.name.startswith('.Blockwerk-next-'):
                shutil.rmtree(stage)
            raise

    def start_helper(self,job):
        if job.get('kind') == 'source':
            subprocess.Popen([sys.executable, job['helper'], '--apply', job['job']],
                cwd=Path(job['helper']).parent, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            return
        subprocess.Popen([job['helper'],'--apply',job['job']],cwd=Path(job['helper']).parent,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0,
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    def can_install(self):
        if sys.platform == 'win32':return bool(getattr(sys, 'frozen', False))
        return sys.platform in ('darwin', 'linux') and not getattr(sys, 'frozen', False) and (Path(__file__).resolve().parent.parent / 'release-source.json').is_file()

    def stage_update(self, info, package, cancel, notify):
        if sys.platform == 'win32':return self.stage_windows(info, package, cancel, notify)
        if not self.can_install():
            raise LauncherError(tr('Dieses Paket bitte manuell installieren.'))
        from . import source_updates
        install = Path(__file__).resolve().parent.parent
        notify(tr('Launcher-Update wird vorbereitet. Persönliche Daten bleiben erhalten …'))
        try:
            stage = source_updates.stage_source(install, Path(package), info['version'], info['asset']['sha256'], cancel)
        except InterruptedError:
            raise Cancelled(tr('Update-Vorbereitung abgebrochen.')) from None
        except (OSError, ValueError, zipfile.BadZipFile) as error:
            raise LauncherError(tr('Das Quellpaket konnte nicht geprüft werden. Bitte manuell installieren.')) from error
        job_dir = self.work / 'jobs' / uuid.uuid4().hex
        job_dir.mkdir(parents=True)
        helper = job_dir / 'source_update.py'
        shutil.copy2(Path(source_updates.__file__), helper)
        job = job_dir / 'job.json'
        atomic_json(job, {'schema': 1, 'pid': os.getpid(), 'install_dir': str(install),
            'stage_dir': str(stage), 'version': info['version'], 'platform': sys.platform,
            'result_file': str(self.work / 'last-result.json')})
        return {'kind': 'source', 'job': str(job), 'helper': str(helper)}
