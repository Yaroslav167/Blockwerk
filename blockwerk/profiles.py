"""Isolated mod profiles, four native loader adapters, and local JAR management."""
from __future__ import annotations
from .i18n import tr
import json
from pathlib import Path
import re
import shutil
import subprocess
import threading
import tomllib
import uuid
import zipfile
import requests

from minecraft_launcher_lib import mod_loader, runtime
from .core import (LauncherError, Cancelled, LauncherService, atomic_json,
                   is_release, safe_version_id, validate_java)

LOADERS = {"fabric": "Fabric", "forge": "Forge", "quilt": "Quilt", "neoforge": "NeoForge", "custom": "Eigener Installer"}


def version_matches(version: str, constraint) -> bool | None:
    """Conservative subset of Fabric/Quilt predicates and Maven version ranges."""
    if isinstance(constraint, list):
        values = [version_matches(version, value) for value in constraint]
        return True if True in values else None if None in values else False
    if not isinstance(constraint, str):
        return None
    value = constraint.strip()
    if value in ("", "*", ">=0"):
        return True
    def number(text):
        if not re.fullmatch(r"\d+(?:\.\d+)*", text):
            raise ValueError
        parts = tuple(int(p) for p in text.split("."))
        return parts + (0,) * max(0, 4 - len(parts))
    try:
        current = number(version)
        if "||" in value:
            return version_matches(version, value.split("||"))
        if value[0] in "[(" and value[-1] in ")]":
            inside = value[1:-1]
            if "," not in inside:
                return current == number(inside)
            lower, upper = (part.strip() for part in inside.split(",", 1))
            return ((not lower or current >= number(lower) if value[0] == "[" else not lower or current > number(lower))
                    and (not upper or current <= number(upper) if value[-1] == "]" else not upper or current < number(upper)))
        results = []
        for token in value.split():
            match = re.fullmatch(r"(>=|<=|>|<|=|~|\^)?(\d+(?:\.(?:\d+|x|\*))*)", token)
            if not match:
                return None
            operator, target = match.groups()
            if "x" in target or "*" in target:
                prefix = target.replace("*", "x").split("x", 1)[0].rstrip(".")
                results.append(version == prefix or version.startswith(prefix + "."))
                continue
            expected = number(target)
            if operator in ("~", "^"):
                parts = list(expected)
                bump = 1 if operator == "~" else 0
                parts[bump] += 1
                for pos in range(bump + 1, len(parts)):
                    parts[pos] = 0
                results.append(expected <= current < tuple(parts))
            else:
                results.append({">=": current >= expected, "<=": current <= expected,
                                ">": current > expected, "<": current < expected,
                                "=": current == expected, None: current == expected}[operator])
        return all(results)
    except (ValueError, IndexError):
        return None


def inspect_mod(file: Path) -> dict:
    result = {"name": file.name, "id": "", "loaders": [], "minecraft": None, "dependencies": []}
    try:
        with zipfile.ZipFile(file) as archive:
            def read(name):
                if archive.getinfo(name).file_size > 1024 * 1024:
                    raise LauncherError(tr("Mod-Metadaten sind ungewöhnlich groß: ") + file.name)
                return archive.read(name).decode("utf-8-sig")
            names = set(archive.namelist())
            if "fabric.mod.json" in names:
                data = json.loads(read("fabric.mod.json"))
                result.update(name=str(data.get("name", file.name)), id=str(data.get("id", "")))
                result["loaders"].append("fabric")
                depends = data.get("depends", {})
                result["minecraft"] = depends.get("minecraft")
                result["dependencies"] = [str(k) for k in depends if k not in ("minecraft", "java", "fabricloader")]
            if "quilt.mod.json" in names:
                data = json.loads(read("quilt.mod.json")).get("quilt_loader", {})
                result.update(name=str(data.get("metadata", {}).get("name", file.name)), id=str(data.get("id", "")))
                result["loaders"].append("quilt")
                for dependency in data.get("depends", []):
                    if isinstance(dependency, dict) and dependency.get("id") == "minecraft":
                        result["minecraft"] = dependency.get("versions")
            for name, loader in (("META-INF/mods.toml", "forge"), ("META-INF/neoforge.mods.toml", "neoforge")):
                if name not in names:
                    continue
                data = tomllib.loads(read(name))
                result["loaders"].append(loader)
                mods = data.get("mods", [])
                if mods:
                    result.update(name=str(mods[0].get("displayName", file.name)), id=str(mods[0].get("modId", "")))
                for entries in data.get("dependencies", {}).values():
                    for dependency in entries:
                        if dependency.get("modId") == "minecraft":
                            result["minecraft"] = dependency.get("versionRange")
                        elif dependency.get("mandatory", dependency.get("type") == "required"):
                            if dependency.get("modId") not in ("forge", "neoforge"):
                                result["dependencies"].append(str(dependency.get("modId", "")))
            if not result["loaders"] and "mcmod.info" in names:
                result["loaders"] = ["forge"]
    except (zipfile.BadZipFile, UnicodeError, ValueError, TypeError, KeyError, AttributeError):
        raise LauncherError(tr("Keine lesbare Mod-JAR oder ungültige Metadaten: ") + file.name) from None
    return result


class ProfileManager:
    def __init__(self, parent: LauncherService):
        self.parent = parent
        self.root = parent.root / "profiles"

    def folder(self, identifier: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{32}", identifier):
            raise LauncherError(tr("Ungültiges Mod-Profil."))
        return self.root / identifier

    def read(self, identifier: str) -> dict:
        try:
            data = json.loads((self.folder(identifier) / "profile.json").read_text(encoding="utf-8"))
            if data["id"] != identifier or data["loader"] not in LOADERS:
                raise ValueError
            if not isinstance(data["name"], str) or not data["name"].strip():
                raise ValueError
            safe_version_id(data["base"])
            if data.get("installed"):
                safe_version_id(data["installed"])
            return data
        except (OSError, ValueError, KeyError, TypeError):
            raise LauncherError(tr("Dieses Mod-Profil ist beschädigt.")) from None

    def list(self) -> list[dict]:
        if not self.root.exists():
            return []
        profiles = []
        for folder in self.root.iterdir():
            if folder.is_dir() and (folder / "profile.json").exists():
                try:
                    profiles.append(self.read(folder.name))
                except LauncherError:
                    pass
        return sorted(profiles, key=lambda item: item["name"].casefold())

    def create(self, name: str, base: str, loader: str, loader_version: str = "") -> dict:
        name = name.strip()
        if not name or len(name) > 60 or any(ord(c) < 32 for c in name):
            raise LauncherError(tr("Bitte einen Profilnamen mit 1–60 sichtbaren Zeichen wählen."))
        if loader not in LOADERS or not is_release({"id": base, "type": "release"}):
            raise LauncherError(tr("Bitte einen Loader und ein Minecraft-Release ab 1.0 auswählen."))
        identifier = uuid.uuid4().hex
        data = {"id": identifier, "name": name, "base": base, "loader": loader,
                "loader_version": loader_version, "installed": ""}
        self.folder(identifier).mkdir(parents=True)
        atomic_json(self.folder(identifier) / "profile.json", data)
        return data

    def service(self, identifier: str) -> LauncherService:
        self.read(identifier)
        service = LauncherService(self.folder(identifier), allow_custom_versions=True)
        service.settings = self.parent.settings
        service.accounts = self.parent.accounts
        return service

    def loader_versions(self, loader: str, base: str) -> list[str]:
        if loader == "custom":
            return []
        if loader not in LOADERS:
            raise LauncherError(tr("Unbekannter Loader."))
        adapter = mod_loader.get_mod_loader(loader)
        if not adapter.is_minecraft_version_supported(base):
            raise LauncherError(LOADERS[loader] + tr(" unterstützt Minecraft ") + base + tr(" nicht. Bitte eine passende Version wählen."))
        versions = adapter.get_loader_versions(base, False)
        return sorted(set(versions), key=lambda value: tuple(int(part) for part in re.findall(r"\d+", value)), reverse=True)

    def install(self, identifier: str, cancel: threading.Event, notify, progress) -> dict:
        data = self.read(identifier)
        service = self.service(identifier)
        service.prepare_local_version(data["base"], cancel, notify, progress)
        if cancel.is_set():
            raise Cancelled(tr("Loader-Installation abgebrochen."))
        if data["loader"] == "custom":
            installed = data.get("installed") or data["base"]
        else:
            versions = self.loader_versions(data["loader"], data["base"])
            selected = data["loader_version"] or (versions[0] if versions else "")
            if selected not in versions:
                raise LauncherError(tr("Diese Loader-Version ist nicht verfügbar. Bitte Versionen neu laden."))
            metadata = service.version_metadata(data["base"])
            java = service.settings.java_path or runtime.get_executable_path(metadata.get("javaVersion", {}).get("component", "jre-legacy"), service.game_root)
            if not java:
                raise LauncherError(tr("Kein Java für den Installer verfügbar."))
            notify(LOADERS[data["loader"]] + " " + selected + tr(" wird installiert …"))
            def status(text):
                if cancel.is_set():
                    raise Cancelled(tr("Loader-Installation abgebrochen."))
                notify(str(text))
            adapter = mod_loader.get_mod_loader(data["loader"])
            if data["loader"] == "fabric":
                # Fabric publishes ready-to-use launcher profiles. Fetching the
                # official profile avoids requiring a GUI/Java installer.
                installed = adapter.get_installed_version(data["base"], selected)
                response = requests.get("https://meta.fabricmc.net/v2/versions/loader/" + data["base"] + "/" + selected + "/profile/json")
                response.raise_for_status()
                profile = response.json()
                if profile.get("id") != installed or profile.get("inheritsFrom") != data["base"]:
                    raise LauncherError(tr("Fabric hat kein passendes Launcher-Profil geliefert."))
                safe_version_id(installed)
                atomic_json(service.game_root / "versions" / installed / (installed + ".json"), profile)
            else:
                try:
                    installed = adapter.install(data["base"], service.game_root,
                                loader_version=selected, java=java, callback={"setStatus": status})
                except subprocess.CalledProcessError as error:
                    details = []
                    for output in (error.stdout, error.stderr):
                        if output:
                            details.append(output.decode("utf-8", "replace") if isinstance(output, bytes) else str(output))
                    (self.folder(identifier) / "installer-error.log").write_text("\n".join(details), encoding="utf-8")
                    raise LauncherError("Der " + LOADERS[data["loader"]] + tr("-Installer ist fehlgeschlagen. Java und installer-error.log im Profilordner prüfen.")) from None
            data["loader_version"] = selected
        service.prepare_local_version(installed, cancel, notify, progress)
        data["installed"] = installed
        atomic_json(self.folder(identifier) / "profile.json", data)
        self.mod_folder(identifier).mkdir(parents=True, exist_ok=True)
        return data

    def installed_versions(self, identifier: str) -> list[str]:
        folder = self.service(identifier).game_root / "versions"
        if not folder.exists():
            return []
        return sorted(item.name for item in folder.iterdir() if item.is_dir() and (item / (item.name + ".json")).is_file())

    def adopt(self, identifier: str, installed: str, cancel, notify, progress) -> dict:
        data = self.read(identifier)
        if installed not in self.installed_versions(identifier):
            raise LauncherError(tr("Diese installierte Version wurde nicht gefunden."))
        service = self.service(identifier)
        raw = json.loads((service.game_root / "versions" / installed / (installed + ".json")).read_text(encoding="utf-8"))
        if raw.get("inheritsFrom") and raw["inheritsFrom"] != data["base"]:
            raise LauncherError(tr("Das installierte Profil muss direkt zur gewählten Minecraft-Basis passen."))
        service.prepare_local_version(installed, cancel, notify, progress)
        data["installed"] = installed
        atomic_json(self.folder(identifier) / "profile.json", data)
        return data

    def run_installer(self, identifier: str, file: Path) -> int:
        service = self.service(identifier)
        data = self.read(identifier)
        metadata = service.version_metadata(data["base"])
        java = service.settings.java_path or runtime.get_executable_path(metadata.get("javaVersion", {}).get("component", "jre-legacy"), service.game_root)
        if file.suffix.lower() == ".jar":
            if not java:
                raise LauncherError(tr("Bitte zuerst die Basisdateien des Profils installieren."))
            args = [validate_java(java), "-jar", str(file.resolve())]
        elif file.suffix.lower() == ".exe":
            import sys
            if sys.platform != "win32":
                raise LauncherError(tr("EXE-Installer laufen nur unter Windows."))
            args = [str(file.resolve())]
        else:
            raise LauncherError(tr("Unterstützt werden lokale JAR- und Windows-EXE-Installer."))
        service.game_root.mkdir(parents=True, exist_ok=True)
        return subprocess.Popen(args, cwd=service.game_root).wait()

    def mod_folder(self, identifier: str) -> Path:
        return self.folder(identifier) / "mods"

    def mods(self, identifier: str) -> list[dict]:
        data = self.read(identifier)
        folder = self.mod_folder(identifier)
        if not folder.exists():
            return []
        rows = []
        for file in sorted(folder.iterdir()):
            if not file.is_file() or not file.name.endswith((".jar", ".jar.disabled")):
                continue
            try:
                info = inspect_mod(file)
                compatible = version_matches(data["base"], info["minecraft"])
                info.update(file=file.name, enabled=file.name.endswith(".jar"),
                            hint="Version passt" if compatible is True else "Version passt nicht" if compatible is False else "Version/Abhängigkeiten manuell prüfen")
            except LauncherError as error:
                info = {"file": file.name, "name": file.name, "id": "", "loaders": [], "dependencies": [],
                        "enabled": file.name.endswith(".jar"), "hint": str(error)}
            rows.append(info)
        available = {row["id"] for row in rows if row["enabled"]}
        for row in rows:
            missing = [dependency for dependency in row["dependencies"] if dependency and dependency not in available]
            if missing:
                row["hint"] += " · prüfen: " + ", ".join(missing[:5])
        return rows

    def add_mods(self, identifier: str, files: list[Path]) -> int:
        data = self.read(identifier)
        destination = self.mod_folder(identifier)
        prepared = []
        for file in files:
            if file.suffix.lower() != ".jar" or not file.is_file():
                raise LauncherError(tr("Bitte Mod-Dateien im JAR-Format auswählen."))
            info = inspect_mod(file)
            loaders = info["loaders"]
            if data["loader"] != "custom" and loaders and data["loader"] not in loaders:
                if not (data["loader"] == "quilt" and "fabric" in loaders):
                    raise LauncherError(file.name + " passt zu " + ", ".join(loaders) + tr(", nicht zu ") + data["loader"] + ".")
            if version_matches(data["base"], info["minecraft"]) is False:
                raise LauncherError(file.name + tr(" ist laut Metadaten nicht für Minecraft ") + data["base"] + ".")
            target_name = file.stem + ".jar"
            if (destination / target_name).exists() or (destination / (target_name + ".disabled")).exists():
                raise LauncherError(tr("Diese Mod-Datei existiert bereits: ") + file.name)
            prepared.append((file, target_name))
        if len({name.casefold() for _, name in prepared}) != len(prepared):
            raise LauncherError(tr("Zwei ausgewählte Dateien haben denselben Namen."))
        destination.mkdir(parents=True, exist_ok=True)
        for file, target_name in prepared:
            shutil.copy2(file, destination / target_name)
        return len(prepared)

    def toggle_mod(self, identifier: str, filename: str) -> None:
        if Path(filename).name != filename or not filename.endswith((".jar", ".jar.disabled")):
            raise LauncherError(tr("Ungültige Mod-Datei."))
        source = self.mod_folder(identifier) / filename
        target = source.with_name(filename[:-9] if filename.endswith(".disabled") else filename + ".disabled")
        if target.exists():
            raise LauncherError(tr("Die Zieldatei existiert bereits."))
        source.rename(target)

    def sync_mods(self, identifier: str, game_directory: Path) -> None:
        source = self.mod_folder(identifier)
        target = game_directory / "mods"
        target.mkdir(parents=True, exist_ok=True)
        marker = game_directory / "blockwerk-managed-mods.json"
        try:
            previous = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = []
        enabled = sorted(file.name for file in source.glob("*.jar") if file.is_file())
        for name in previous:
            if isinstance(name, str) and Path(name).name == name and name.endswith(".jar") and name not in enabled:
                (target / name).unlink(missing_ok=True)
        for name in enabled:
            shutil.copy2(source / name, target / name)
        atomic_json(marker, enabled)

    def launch(self, identifier: str, cancel, notify, progress, started, *, offline=False, community_servers=None, world_folder=None) -> int:
        data = self.read(identifier)
        if not data.get("installed"):
            raise LauncherError(tr("Dieses Mod-Profil ist noch nicht installiert. Bitte unter Mods installieren."))
        service = self.service(identifier)
        directory = service.game_directory(data["installed"], service.settings.offline_name if offline else None)
        self.sync_mods(identifier, directory)
        return service.launch(data["installed"], cancel, notify, progress, started,
                              offline=offline, community_servers=community_servers, world_folder=world_folder)
