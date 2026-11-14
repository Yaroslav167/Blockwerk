"""Unlimited favorites and non-destructive native Minecraft server-list imports."""
from __future__ import annotations
from .i18n import tr
import ipaddress
import json
from pathlib import Path
import re
import struct
import uuid
import shutil
import hashlib

from .core import LauncherError, atomic_json



def normalize_address(value: str) -> str:
    value = value.strip()
    if not value or len(value) > 255 or re.search(r'[\s/\\@?#"\x00-\x1f]', value):
        raise LauncherError(tr("Bitte eine Serveradresse wie spiel.example.org:25565 eingeben, ohne https://."))
    port = 25565
    if value.startswith("["):
        match = re.fullmatch(r"\[([^]]+)\](?::([0-9]+))?", value)
        if not match:
            raise LauncherError(tr("IPv6-Adressen bitte in eckige Klammern setzen."))
        try:
            host = "[" + str(ipaddress.IPv6Address(match[1])) + "]"
        except ValueError:
            raise LauncherError(tr("Ungültige IPv6-Adresse.")) from None
        if match[2]:
            port = int(match[2])
    else:
        if value.count(":") > 1:
            raise LauncherError(tr("IPv6-Adressen bitte in eckige Klammern setzen."))
        raw_host, separator, raw_port = value.partition(":")
        if separator:
            if not raw_port.isdigit():
                raise LauncherError(tr("Der Port muss eine Zahl sein."))
            port = int(raw_port)
        try:
            host = raw_host.rstrip(".").encode("idna").decode("ascii").lower()
        except UnicodeError:
            raise LauncherError(tr("Ungültiger Servername.")) from None
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.\-]*[a-z0-9])?", host) or ".." in host:
            raise LauncherError(tr("Ungültiger Servername."))
    if not 1 <= port <= 65535:
        raise LauncherError(tr("Der Port muss zwischen 1 und 65535 liegen."))
    return host if port == 25565 else host + ":" + str(port)


def checked_servers(items: list[dict]) -> list[dict]:
    if not isinstance(items, list):
        raise LauncherError(tr("Die Serverliste muss eine Liste sein."))
    result = []
    seen = set()
    for item in items:
        name = str(item.get("name", "")).strip()
        address = normalize_address(item.get("address", ""))
        if not name or len(name) > 80 or any(ord(char) < 32 for char in name):
            raise LauncherError(tr("Ein Servername muss 1–80 sichtbare Zeichen haben."))
        if address in seen:
            raise LauncherError(tr("Diese Serveradresse ist bereits gespeichert."))
        seen.add(address)
        result.append({"id": str(item.get("id") or uuid.uuid4().hex), "name": name, "address": address})
    return result


class ServerStore:
    def __init__(self, root: Path):
        self.path = root / "community-servers.json"

    def list(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            return checked_servers(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError, AttributeError):
            raise LauncherError(tr("Die gespeicherte Serverliste ist beschädigt.")) from None

    def add(self, name: str, address: str) -> None:
        rows = self.list()
        rows.append({"name": name, "address": address})
        atomic_json(self.path, checked_servers(rows))

    def remove(self, identifier: str) -> None:
        rows = self.list()
        if not any(row["id"] == identifier for row in rows):
            raise LauncherError(tr("Dieser Server ist nicht mehr vorhanden."))
        atomic_json(self.path, [row for row in rows if row["id"] != identifier])


def write_server_file(path: Path, items: list[dict]) -> None:
    rows = checked_servers(items)
    def string(value: str) -> bytes:
        # Java DataOutput.writeUTF uses modified UTF-8 (UTF-16 surrogate pairs),
        # including for emoji in a server's display name.
        utf16 = value.encode("utf-16-be", "surrogatepass")
        encoded = b"".join(chr(int.from_bytes(utf16[i:i + 2], "big")).encode("utf-8", "surrogatepass")
                           for i in range(0, len(utf16), 2)).replace(b"\x00", b"\xc0\x80")
        return struct.pack(">H", len(encoded)) + encoded
    data = b"\x0a\x00\x00"  # unnamed root compound
    data += b"\x09" + string("servers") + b"\x0a" + struct.pack(">i", len(rows))
    for row in rows:
        data += b"\x08" + string("name") + string(row["name"])
        data += b"\x08" + string("ip") + string(row["address"]) + b"\x00"
    data += b"\x00"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def prepare_server_file(path: Path, items: list[dict], legacy: Path | None = None) -> None:
    """Import new launcher favorites once; preserve native rows and unknown tags."""
    from .worlds import NBTReader, MAX_METADATA
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() and legacy and legacy.is_file() and legacy != path:
        shutil.copy2(legacy, path)  # Keep the retired mode's original list intact.
    marker = path.with_name('blockwerk-server-imports.json')
    try:
        imported = json.loads(marker.read_text(encoding='utf-8'))
        if not isinstance(imported,list) or not all(isinstance(v,str) for v in imported):raise ValueError
    except FileNotFoundError:
        imported=[]
    except (ValueError,OSError):
        raise LauncherError(tr('Die Server-Importhistorie ist beschädigt. Die Minecraft-Serverliste bleibt erhalten.')) from None
    rows=checked_servers(items)
    def identity(row):
        return hashlib.sha256(row['address'].encode('utf-8')).hexdigest()
    pending=[row for row in rows if identity(row) not in imported]
    if not pending:return
    # Capture each existing compound verbatim, including icons and mod-specific tags.
    if path.exists():
        with path.open('rb') as stream:raw=stream.read(MAX_METADATA+1)
    else:raw=b'\x0a\x00\x00\x09\x00\x07servers\x0a\x00\x00\x00\x00\x00'
    try:
        if len(raw)>MAX_METADATA:raise ValueError('size')
        reader=NBTReader(raw)
        if reader.number('B')!=10:raise ValueError('root')
        reader.string()
        entries=[];addresses=set();location=None
        while True:
            tag=reader.number('B')
            if tag==0:break
            name=reader.string()
            if name=='servers':
                if location is not None or tag!=9:raise ValueError('servers')
                start=reader.stream.tell()
                kind=reader.number('B');count=reader.number('i')
                if not 0<=count<=100000 or (kind!=10 and not (kind==0 and count==0)):raise ValueError('list')
                for _ in range(count):
                    pos=reader.stream.tell();value=reader.payload(10)
                    entries.append(raw[pos:reader.stream.tell()])
                    address=value.get('ip','')
                    try:addresses.add(normalize_address(address))
                    except (LauncherError,AttributeError):addresses.add(str(address))
                location=(start,reader.stream.tell())
            else:reader.payload(tag)
        if location is None or reader.stream.tell()!=len(raw):raise ValueError('structure')
    except (ValueError,UnicodeError,struct.error):
        raise LauncherError(tr('Die vorhandene servers.dat ist nicht lesbar. Sie wird nicht überschrieben; bitte im Spiel prüfen.')) from None
    additions=[row for row in pending if row['address'] not in addresses]
    if additions:
        # Use the same encoder as the standalone writer, then extract raw compounds.
        temporary=path.with_name('blockwerk-new-servers.tmp')
        try:
            write_server_file(temporary,additions)
            encoded=temporary.read_bytes()
        finally:temporary.unlink(missing_ok=True)
        payload=b'\x0a'+struct.pack('>i',len(entries)+len(additions))+b''.join(entries)+encoded[18:-1]
        start,end=location
        if path.exists():shutil.copy2(path,path.with_name('servers.dat.blockwerk-backup'))
        temporary=path.with_suffix('.blockwerk-tmp')
        temporary.write_bytes(raw[:start]+payload+raw[end:])
        temporary.replace(path)
    atomic_json(marker,sorted(set(imported)|{identity(row) for row in pending}))
