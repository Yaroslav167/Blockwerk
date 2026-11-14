"""Original starter skins, unchanged PNG imports, account skins and local packs."""
from __future__ import annotations
from .i18n import tr
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import struct
import uuid
import zipfile

import requests
from PySide6.QtCore import QBuffer, QIODevice, QRect
from PySide6.QtGui import QColor, QImage, QPainter
from .core import LauncherError, Cancelled, atomic_json, microsoft_account, valid_client_id, validate_profile

PNG_LIMIT = 1024 * 1024
SKIN_API = "https://api.minecraftservices.com/minecraft/profile/skins"


def load_skin(path: Path) -> QImage:
    if not path.is_file() or path.stat().st_size > PNG_LIMIT:
        raise LauncherError(tr("Bitte eine Skin-PNG mit höchstens 1 MB auswählen."))
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise LauncherError(tr("Diese Datei ist keine gültige PNG-Skin-Datei."))
    width, height = struct.unpack(">II", header[16:24])
    if (width, height) not in ((64, 64), (64, 32)):
        raise LauncherError(tr("Java-Skins müssen 64 × 64 oder 64 × 32 Pixel groß sein."))
    image = QImage(str(path))
    if image.isNull() or (image.width(), image.height()) != (width, height):
        raise LauncherError(tr("Die Skin-PNG konnte nicht gelesen werden."))
    return image.convertToFormat(QImage.Format.Format_ARGB32)


def part_uv(kind: str, slim=False, overlay=False):
    # (side strip origin x, side strip y, width, height, depth).
    values = {"head": (32 if overlay else 0, 8, 8, 8, 8),
              "body": (16, 36 if overlay else 20, 8, 12, 4),
              "right_arm": (40, 36 if overlay else 20, 3 if slim else 4, 12, 4),
              "left_arm": (48 if overlay else 32, 52, 3 if slim else 4, 12, 4),
              "right_leg": (0, 36 if overlay else 20, 4, 12, 4),
              "left_leg": (0 if overlay else 16, 52, 4, 12, 4)}
    x, y, w, h, d = values[kind]
    return {"right": (x, y, d, h), "front": (x+d, y, w, h),
            "left": (x+d+w, y, d, h), "back": (x+2*d+w, y, w, h),
            "top": (x+d, y-d, w, d), "bottom": (x+d+w, y-d, w, d)}


def modern_skin(image: QImage) -> QImage:
    if image.height() == 64:
        return image.copy()
    result = QImage(64, 64, QImage.Format.Format_ARGB32)
    result.fill(0)
    paint = QPainter(result)
    paint.drawImage(0, 0, image)
    for source, target in (("right_arm", "left_arm"), ("right_leg", "left_leg")):
        old, new = part_uv(source), part_uv(target)
        for face, rect in new.items():
            origin = "left" if face == "right" else "right" if face == "left" else face
            patch = image.copy(QRect(*old[origin])).mirrored(True, False)
            paint.drawImage(QRect(*rect), patch)
    paint.end()
    return result


def arm_variant(image: QImage, source: str, target: str) -> QImage:
    result = modern_skin(image)
    if source == target:
        return result
    original = result.copy()
    paint = QPainter(result)
    for part in ("right_arm", "left_arm"):
        for outer in (False, True):
            before, after = part_uv(part, source == "slim", outer), part_uv(part, target == "slim", outer)
            paint.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            for face, rect in after.items():
                paint.drawImage(QRect(*rect), original.copy(QRect(*before[face])))
    paint.end()
    return result


def png_bytes(image: QImage) -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise LauncherError(tr("Die Skin-PNG konnte nicht gespeichert werden."))
    return bytes(buffer.data())


def starter_skin(shirt: str, trousers: str, accent: str) -> QImage:
    """Original procedural artwork, no Minecraft textures are redistributed."""
    image = QImage(64, 64, QImage.Format.Format_ARGB32)
    image.fill(0)
    paint = QPainter(image)
    for part in ("head", "body", "right_arm", "left_arm", "right_leg", "left_leg"):
        color = "#bd8b68" if part == "head" else trousers if "leg" in part else shirt
        for face, rect in part_uv(part).items():
            shade = QColor(color)
            if face in ("right", "left", "back"):
                shade = shade.darker(112)
            paint.fillRect(QRect(*rect), shade)
        if "leg" in part:
            x,y,w,h=part_uv(part)["front"]
            paint.fillRect(x,y+h-3,w,3,QColor("#293336"))
        if "arm" in part:
            for face in ("front","back","right","left"):
                x,y,w,h=part_uv(part)[face]
                paint.fillRect(x,y+h-3,w,3,QColor("#bd8b68"))
    paint.fillRect(8,8,8,2,QColor("#49372d"))
    paint.fillRect(8,0,8,8,QColor("#49372d"))
    paint.fillRect(24,8,8,8,QColor("#49372d"))
    paint.fillRect(8,10,1,2,QColor("#49372d"))
    paint.fillRect(15,10,1,2,QColor("#49372d"))
    for x in (10,13):
        paint.fillRect(x,11,1,1,QColor("#eef1df"))
        paint.fillRect(x,12,1,1,QColor("#293b42"))
    paint.fillRect(11,14,2,1,QColor("#8d5d48"))
    paint.fillRect(20,20,8,2,QColor(accent))
    paint.fillRect(23,22,2,10,QColor(accent))
    paint.fillRect(20,30,8,2,QColor("#3b3f35"))
    paint.fillRect(23,30,2,2,QColor("#e9cc6f"))
    paint.end()
    return image


class SkinStore:
    def __init__(self, root: Path):
        self.root = root / "skins"
        self.registry = self.root / "skins.json"

    def data(self):
        try:
            data=json.loads(self.registry.read_text(encoding="utf-8"))
            if data.get("schema")!=1 or not isinstance(data.get("items"),list):
                raise ValueError
            for row in data["items"]:
                if not re.fullmatch(r"[a-f0-9]{32}",row["id"]) or row["variant"] not in ("classic","slim") or not isinstance(row["name"],str):
                    raise ValueError
            return data
        except FileNotFoundError:
            return {"schema":1,"selected":"","items":[]}
        except (OSError,ValueError,KeyError,TypeError,AttributeError):
            raise LauncherError(tr("Die gespeicherte Skin-Auswahl ist beschädigt.")) from None

    def ensure_starters(self):
        data=self.data()
        if data["items"]:
            return
        self.root.mkdir(parents=True,exist_ok=True)
        for name,shirt,pants,accent in (("Blockwerk Scout","#4e91ba","#384e67","#c8df91"),
                ("Waldläufer","#577f45","#665342","#c4d08a"),("Sternwanderer","#7760a9","#343b5a","#9fdfe0")):
            identifier=uuid.uuid4().hex
            starter_skin(shirt,pants,accent).save(str(self.root/(identifier+".png")))
            data["items"].append({"id":identifier,"name":name,"variant":"classic"})
        data["selected"]=data["items"][0]["id"]
        atomic_json(self.registry,data)

    def path(self, identifier):
        if not re.fullmatch(r"[a-f0-9]{32}",identifier):
            raise LauncherError(tr("Ungültiger Skin."))
        return self.root/(identifier+".png")

    def selected(self):
        data=self.data()
        return next((r for r in data["items"] if r["id"]==data["selected"]),None)

    def select(self, identifier, variant=None):
        data=self.data()
        row=next((r for r in data["items"] if r["id"]==identifier),None)
        if row is None:
            raise LauncherError(tr("Dieser Skin ist nicht mehr vorhanden."))
        if variant is not None:
            if variant not in ("classic","slim") or (load_skin(self.path(identifier)).height()==32 and variant=="slim"):
                raise LauncherError(tr("Der alte 64 × 32-Skin unterstützt nur breite Arme."))
            row["variant"]=variant
        data["selected"]=identifier
        atomic_json(self.registry,data)

    def add(self, file: Path, variant="classic"):
        image=load_skin(file)
        if variant not in ("classic","slim"):
            raise LauncherError(tr("Bitte Classic oder Slim wählen."))
        if image.height()==32:
            variant="classic"
        raw=file.read_bytes()
        data=self.data()
        digest=hashlib.sha256(raw).digest()
        for row in data["items"]:
            path=self.path(row["id"])
            if path.is_file() and hashlib.sha256(path.read_bytes()).digest()==digest:
                self.select(row["id"])
                return row["id"]
        identifier=uuid.uuid4().hex
        self.root.mkdir(parents=True,exist_ok=True)
        self.path(identifier).write_bytes(raw)  # Original PNG remains unchanged.
        data["items"].append({"id":identifier,"name":file.stem[:60],"variant":variant})
        data["selected"]=identifier
        atomic_json(self.registry,data)
        return identifier

    def apply_account(self, service, cancel):
        row=self.selected()
        if row is None:
            raise LauncherError(tr("Bitte zuerst einen Skin auswählen."))
        file=self.path(row["id"])
        load_skin(file)
        client_id=valid_client_id(service.settings.client_id)
        account=service.accounts.read()
        if not account or account["client_id"]!=client_id:
            raise LauncherError(tr("Bitte zuerst dein Microsoft-Konto mit Minecraft Java verbinden."))
        if cancel.is_set():
            raise Cancelled(tr("Skin-Änderung abgebrochen."))
        profile=microsoft_account.complete_refresh(client_id,None,None,account["refresh_token"])
        validate_profile(profile)
        if cancel.is_set():
            raise Cancelled(tr("Skin-Änderung abgebrochen."))
        with file.open("rb") as image:
            response=requests.post(SKIN_API,headers={"Authorization":"Bearer "+profile["access_token"]},
                data={"variant":row["variant"]},files={"file":("skin.png",image,"image/png")},timeout=(15,45))
        if response.status_code==401:
            raise LauncherError(tr("Die Minecraft-Anmeldung ist abgelaufen. Bitte erneut anmelden."))
        if response.status_code not in (200,204):
            raise LauncherError(tr("Minecraft hat die Skin-Änderung abgelehnt. Prüfe Konto, Minecraft-Berechtigung und Skin-Datei."))
        service.accounts.write(profile,client_id)
        return row["name"]

    def local_pack(self, service, version: str, directory: Path):
        row=self.selected()
        if row is None:
            raise LauncherError(tr("Bitte zuerst einen Skin auswählen."))
        image=load_skin(self.path(row["id"]))
        metadata=service.version_metadata(version)
        jar_id=metadata.get("jar",version)
        client=service.game_root/"versions"/jar_id/(jar_id+".jar")
        try:
            with zipfile.ZipFile(client) as jar:
                info=json.loads(jar.read("version.json"))
                formats=info["pack_version"]
                major=formats.get("resource_major",formats.get("resource"))
                minor=formats.get("resource_minor",0)
                if not isinstance(major,int) or not isinstance(minor,int):
                    raise ValueError
                textures=[p for p in jar.namelist() if re.fullmatch(r"assets/minecraft/textures/entity/(?:player/(?:wide|slim)/[a-z_]+|steve|alex)\.png",p)]
        except (OSError,ValueError,KeyError,zipfile.BadZipFile):
            raise LauncherError(tr("Das lokale Skinpaket benötigt eine vollständig installierte Minecraft-Version mit version.json (gewöhnlich 1.14 oder neuer). Bitte zuerst Spieldateien herunterladen.")) from None
        if not textures:
            raise LauncherError(tr("Für diese Minecraft-Version wurden keine unterstützten Standard-Skin-Texturen gefunden."))
        options=directory/"options.txt"
        original=options.read_text(encoding="utf-8") if options.exists() else ""
        lines=original.splitlines()
        selected=[]
        for line in lines:
            if line.startswith("resourcePacks:"):
                try:
                    selected=json.loads(line.split(":",1)[1])
                    if not isinstance(selected,list) or not all(isinstance(p,str) for p in selected):raise ValueError
                except (ValueError,TypeError):
                    raise LauncherError(tr("Die Ressourcenpaket-Auswahl in options.txt ist nicht lesbar. Bitte zuerst im Spiel prüfen.")) from None
        packname="file/blockwerk-local-skin.zip"
        selected=[p for p in selected if p!=packname]+[packname]
        packmeta={"pack":{"pack_format":major,"description":"Blockwerk · lokaler Skin: "+row["name"],
                         "min_format":[major,minor],"max_format":[major,minor]}}
        packs=directory/"resourcepacks"
        packs.mkdir(parents=True,exist_ok=True)
        target=packs/"blockwerk-local-skin.zip"
        temporary=target.with_suffix(".tmp")
        wide=png_bytes(arm_variant(image,row["variant"],"classic"))
        slim=png_bytes(arm_variant(image,row["variant"],"slim"))
        with zipfile.ZipFile(temporary,"w",zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("pack.mcmeta",json.dumps(packmeta,ensure_ascii=False))
            for texture in textures:
                archive.writestr(texture,slim if "/slim/" in texture or texture=="assets/minecraft/textures/entity/alex.png" else wide)
        temporary.replace(target)
        if original and not (directory/"options.txt.blockwerk-before-skin").exists():
            shutil.copy2(options,directory/"options.txt.blockwerk-before-skin")
        lines=[line for line in lines if not line.startswith("resourcePacks:")]
        lines.append("resourcePacks:"+json.dumps(selected,separators=(",",":")))
        temp_options=options.with_suffix(".blockwerk-tmp")
        temp_options.write_text("\n".join(lines)+"\n",encoding="utf-8")
        temp_options.replace(options)
        return target
