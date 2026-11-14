"""Local Java world discovery, bounded NBT metadata and isolated play copies."""
from __future__ import annotations
from .i18n import tr

import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys
import threading
import uuid
import zlib

from minecraft_launcher_lib import utils
from .core import Cancelled, LauncherError, atomic_json

MAX_METADATA = 16 * 1024 * 1024


class NBTReader:
    def __init__(self, data):
        self.stream = io.BytesIO(data)
        self.remaining = 200000

    def read(self, count):
        if count < 0 or count > MAX_METADATA:
            raise ValueError("NBT size")
        data = self.stream.read(count)
        if len(data) != count:
            raise ValueError("Truncated NBT")
        return data

    def number(self, fmt):
        return struct.unpack(">" + fmt, self.read(struct.calcsize(fmt)))[0]

    def string(self):
        raw = self.read(self.number("H")).replace(b"\xc0\x80", b"\x00")
        return raw.decode("utf-8", "surrogatepass").encode("utf-16", "surrogatepass").decode("utf-16", "replace")

    def payload(self, tag, depth=0):
        self.remaining -= 1
        if depth > 64 or self.remaining < 0:
            raise ValueError("NBT complexity")
        if tag in (1, 2, 3, 4, 5, 6):
            return self.number({1: "b", 2: "h", 3: "i", 4: "q", 5: "f", 6: "d"}[tag])
        if tag == 8:
            return self.string()
        if tag in (7, 11, 12):
            count = self.number("i")
            if count < 0:
                raise ValueError("NBT array")
            self.read(count * {7: 1, 11: 4, 12: 8}[tag])
            return None  # World metadata does not need bulk arrays.
        if tag == 9:
            kind, count = self.number("B"), self.number("i")
            if not 0 <= count <= 100000 or (kind == 0 and count):
                raise ValueError("NBT list")
            return [self.payload(kind, depth + 1) for _ in range(count)]
        if tag == 10:
            result = {}
            while True:
                kind = self.number("B")
                if kind == 0:
                    return result
                name = self.string()
                result[name] = self.payload(kind, depth + 1)
        raise ValueError("Unknown NBT tag")


def world_metadata(path: Path) -> dict:
    with path.open("rb") as stream:
        compressed = stream.read(2) == b"\x1f\x8b"
        stream.seek(0)
        if compressed:
            with gzip.GzipFile(fileobj=stream) as data:
                raw = data.read(MAX_METADATA + 1)
        else:
            raw = stream.read(MAX_METADATA + 1)
    if len(raw) > MAX_METADATA:
        raise ValueError("World metadata too large")
    reader = NBTReader(raw)
    if reader.number("B") != 10:
        raise ValueError("NBT root is not a compound")
    reader.string()
    root = reader.payload(10)
    data = root.get("Data", root)
    if not isinstance(data, dict):
        raise ValueError("Missing world metadata")
    version = data.get(tr("Version"), {})
    if not isinstance(version, dict):
        version = {}
    name = str(data.get("LevelName") or path.parent.name)
    name = re.sub(r"§.", "", name)
    name = "".join(c for c in name if ord(c) >= 32)[:160] or path.parent.name
    return {"name": name, "last_played": max(0, int(data.get("LastPlayed", 0))),
            "minecraft_version": str(version.get(tr("Name"), ""))[:120], "snapshot": bool(version.get("Snapshot", 0)),
            "game_mode": "Hardcore" if data.get("hardcore") else {0: tr("Überleben"), 1: tr("Kreativ"), 2: tr("Abenteuer"), 3: tr("Zuschauer")}.get(data.get("GameType"), tr("Unbekannt"))}


def normalized_version(value: str) -> str:
    value = value.casefold().strip()
    value = re.sub(r"\s+snapshot\s+", "-snapshot-", value)
    return value


def is_link(path: Path) -> bool:
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def world_unlocked(world: Path) -> None:
    """Test the game's session lock without changing its contents."""
    lock = world / "session.lock"
    if not lock.exists():
        return
    try:
        with lock.open("rb") as stream:
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBRLCK, 1)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.lockf(stream.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                fcntl.lockf(stream.fileno(), fcntl.LOCK_UN)
    except OSError:
        raise LauncherError(tr("Diese Welt ist noch geöffnet oder gesperrt. Schließe Minecraft, bevor du eine Spielkopie erstellst.")) from None


class WorldManager:
    def __init__(self, service, profiles, official_root: Path | None = None):
        self.service, self.profiles = service, profiles
        self.official_root = official_root if official_root is not None else Path(utils.get_minecraft_directory())
        self.roots_file = service.root / "world-roots.json"
        self.imports_file = service.root / "world-imports.json"

    def extra_roots(self):
        try:
            data = json.loads(self.roots_file.read_text(encoding="utf-8"))
            if not isinstance(data, list) or not all(isinstance(p, str) for p in data):
                raise ValueError
            return [Path(p) for p in data]
        except FileNotFoundError:
            return []
        except (OSError, ValueError):
            raise LauncherError(tr("Die Liste zusätzlicher Weltordner ist beschädigt.")) from None

    def add_root(self, path: Path):
        path = path.resolve()
        if not path.is_dir():
            raise LauncherError(tr("Bitte einen vorhandenen Minecraft-, saves- oder Weltordner wählen."))
        roots = self.extra_roots()
        if path not in [p.resolve() for p in roots]:
            roots.append(path)
            atomic_json(self.roots_file, [str(p) for p in roots])

    def _game_roots(self):
        yield self.official_root, {"source": "Offizielles Minecraft", "profile_id": "", "launch_version": "", "mode": "", "player": ""}
        for root, profile_id, profile_name in [(self.service.root, "", "Vanilla")] + [
                (self.profiles.folder(p["id"]), p["id"], p["name"]) for p in self.profiles.list()]:
            label = "Blockwerk · " + profile_name
            yield root / "minecraft", {"source": label, "profile_id": profile_id, "launch_version": "", "mode": "", "player": ""}
            instances = root / "instances"
            if not instances.exists():
                continue
            for version in instances.iterdir():
                if not version.is_dir() or is_link(version):
                    continue
                if version.name in ("local", "community"):
                    for player in version.iterdir():
                        if not player.is_dir() or is_link(player):
                            continue
                        for game in player.iterdir():
                            if game.is_dir() and not is_link(game):
                                yield game, {"source": label, "profile_id": profile_id, "launch_version": game.name, "mode": version.name, "player": player.name}
                else:
                    yield version, {"source": label, "profile_id": profile_id, "launch_version": version.name, "mode": "online", "player": ""}
        for root in self.extra_roots():
            yield root, {"source": "Zusätzlicher Ordner", "profile_id": "", "launch_version": "", "mode": "", "player": ""}

    def scan(self, cancel: threading.Event | None = None) -> list[dict]:
        rows, seen = [], set()
        for root, origin in self._game_roots():
            if cancel and cancel.is_set():
                raise Cancelled(tr("Weltsuche abgebrochen."))
            if not root.is_dir():
                continue
            if (root / "level.dat").is_file() or (root / "level.dat_old").is_file():
                candidates = [root]
            else:
                saves = root / "saves" if (root / "saves").is_dir() else root
                try:
                    candidates = list(saves.iterdir())
                except OSError:
                    continue
            for world in candidates:
                if cancel and cancel.is_set():
                    raise Cancelled(tr("Weltsuche abgebrochen."))
                if not world.is_dir() or is_link(world) or world.name.startswith(".blockwerk-"):
                    continue
                level = world / "level.dat"
                if not level.is_file() and not (world / "level.dat_old").is_file():
                    continue
                path = world.resolve()
                key = os.path.normcase(str(path))
                if key in seen:
                    continue
                seen.add(key)
                row = dict(origin, id=hashlib.sha256(key.encode()).hexdigest()[:24], path=str(path),
                           folder=world.name, name=world.name, last_played=0, minecraft_version="", snapshot=False,
                           game_mode=tr("Unbekannt"), error="")
                try:
                    row.update(world_metadata(level))
                except (OSError, ValueError, UnicodeError, EOFError, struct.error, TypeError, OverflowError, zlib.error):
                    row["error"] = "Welt-Metadaten sind nicht lesbar. Im Minecraft-Einzelspielermenü prüfen."
                rows.append(row)
        return sorted(rows, key=lambda row: (-row["last_played"], row["name"].casefold()))

    def play_copy(self, row: dict, game_directory: Path, cancel: threading.Event,
                  notify, force_copy=False) -> str:
        raw_source = Path(row["path"])
        source = raw_source.resolve()
        if not source.is_dir() or not (source / "level.dat").is_file() or is_link(raw_source):
            raise LauncherError(tr("Diese Welt ist nicht mehr verfügbar oder muss in Minecraft wiederhergestellt werden."))
        saves = game_directory / "saves"
        saves.mkdir(parents=True, exist_ok=True)
        if saves.resolve().is_relative_to(source):
            raise LauncherError(tr("Der Zielordner darf nicht innerhalb der Quellwelt liegen."))
        if source.parent == saves.resolve() and not force_copy:
            return source.name
        world_unlocked(source)
        key = hashlib.sha256((str(source) + "\n" + str(saves.resolve())).encode()).hexdigest()
        try:
            mappings = json.loads(self.imports_file.read_text(encoding="utf-8"))
            if not isinstance(mappings, dict):
                raise ValueError
        except (OSError, ValueError):
            mappings = {}
        previous = mappings.get(key, "")
        if (isinstance(previous, str) and previous not in ("", ".", "..") and Path(previous).name == previous
                and (saves / previous).resolve().parent == saves.resolve() and not is_link(saves / previous)
                and (saves / previous / "level.dat").is_file()):
            notify(tr("Vorhandene Spielkopie wird geöffnet. Das Original bleibt erhalten."))
            return previous
        temporary = saves / (".blockwerk-import-" + uuid.uuid4().hex)
        target = saves / (source.name[:70].lstrip(".-") + "-Blockwerk-" + uuid.uuid4().hex[:8])
        notify(tr("Eine Spielkopie der Welt wird erstellt. Das Original bleibt erhalten …"))
        temporary.mkdir()
        try:
            count = 0
            for folder, directories, files in os.walk(source, followlinks=False):
                if cancel.is_set():
                    raise Cancelled(tr("Weltimport abgebrochen."))
                here = Path(folder)
                for name in directories + files:
                    if is_link(here / name):
                        raise LauncherError(tr("Diese Welt enthält eine Verknüpfung. Bitte eine vollständige Weltkopie ohne Verknüpfungen auswählen."))
                destination = temporary / here.relative_to(source)
                destination.mkdir(parents=True, exist_ok=True)
                for name in files:
                    if cancel.is_set():
                        raise Cancelled(tr("Weltimport abgebrochen."))
                    if name == "session.lock":
                        continue
                    shutil.copy2(here / name, destination / name)
                    count += 1
                    if count % 64 == 0:
                        notify(tr("Spielkopie: ") + str(count) + tr(" Dateien übertragen …"))
            temporary.rename(target)
        finally:
            if temporary.exists() and temporary.parent.resolve() == saves.resolve() and temporary.name.startswith(".blockwerk-import-"):
                shutil.rmtree(temporary)
        mappings[key] = target.name
        atomic_json(self.imports_file, mappings)
        return target.name
