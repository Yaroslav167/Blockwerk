"""Real Microsoft authentication, verified Minecraft installs, and process launch.

UI code never receives an access token. Persistent tokens use native secure stores.
"""
from __future__ import annotations
from .i18n import tr
from .i18n import source_text

import ctypes
from ctypes import wintypes
from dataclasses import asdict, dataclass, fields
from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from typing import Callable
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
import uuid
import webbrowser

import requests
from minecraft_launcher_lib import command, install, microsoft_account, runtime, utils

VERSION = "0.9.1"
REDIRECT_URI = "http://localhost:29147/callback"
MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"


class LauncherError(Exception):
    """A message safe to present without leaking authentication responses."""


class Cancelled(LauncherError):
    pass


def configure_network() -> None:
    """Apply bounded network waits to requests, including the launcher's library."""
    original = requests.sessions.Session.request
    if getattr(original, "_blockwerk_timeout", False):
        return

    def bounded(self, method, url, **kwargs):
        kwargs.setdefault("timeout", (15, 90))
        return original(self, method, url, **kwargs)

    bounded._blockwerk_timeout = True
    requests.sessions.Session.request = bounded


def data_directory() -> Path:
    override = os.environ.get("BLOCKWERK_DATA_DIR")
    if override:
        return Path(override).resolve()
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "Blockwerk"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Blockwerk"
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "blockwerk"


def is_release(version: dict) -> bool:
    if not isinstance(version, dict):
        return False
    identifier = version.get("id", "")
    return (version.get("type") == "release" and isinstance(identifier, str)
            and bool(re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", identifier))
            and tuple(map(int, identifier.split("."))) >= (1, 0))


def is_snapshot(version: dict) -> bool:
    if not isinstance(version, dict) or version.get("type") != "snapshot":
        return False
    try:
        safe_version_id(version["id"])
        return True
    except (LauncherError, TypeError, KeyError):
        return False


def validate_java(path: str) -> str:
    executable = Path(path).expanduser()
    names = ("java.exe", "javaw.exe") if sys.platform == "win32" else ("java",)
    if not executable.is_file() or executable.name.lower() not in names:
        raise LauncherError(tr("Bitte eine vorhandene Java-Programmdatei auswählen (Windows: java.exe/javaw.exe; Linux/macOS: bin/java)."))
    if sys.platform != "win32" and not os.access(executable, os.X_OK):
        raise LauncherError(tr("Die gewählte Java-Datei ist nicht ausführbar."))
    return str(executable.resolve())


def check_runtime_platform(java_path: str):
    # launcher-lib 8.0 maps Linux ARM to Mojang's x86 Linux runtime channel.
    if sys.platform.startswith('linux') and platform.machine().lower() in ('arm64', 'aarch64') and not java_path:
        raise LauncherError(tr('Linux ARM benötigt ein passendes ARM-Java. Bitte unter Einstellungen die Java-Datei auswählen. Minecraft und Mods müssen ARM unterstützen.'))


def local_profile(name: str) -> dict:
    name = name.strip()
    if not re.fullmatch(r"[A-Za-z0-9_]{3,16}", name):
        raise LauncherError(tr("Der lokale Spielername braucht 3–16 Zeichen: Buchstaben, Ziffern oder Unterstriche."))
    if name.upper() in {"CON", "PRN", "AUX", "NUL", *("COM" + str(i) for i in range(1, 10)), *("LPT" + str(i) for i in range(1, 10))}:
        raise LauncherError(tr("Dieser Spielername ist als Ordnername reserviert. Bitte einen anderen wählen."))
    # Java UUID.nameUUIDFromBytes("OfflinePlayer:" + name), not UUID3 with a
    # namespace. This is a local identity and never an authenticated account.
    digest = hashlib.md5(("OfflinePlayer:" + name).encode("utf-8")).digest()
    return {"name": name, "id": uuid.UUID(bytes=digest, version=3).hex}


def open_browser(url: str) -> bool:
    try:
        if webbrowser.open(url):
            return True
    except Exception:
        pass
    try:
        if sys.platform == "win32":
            os.startfile(url)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            opener = shutil.which("xdg-open")
            if not opener:
                return False
            subprocess.Popen([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def native_keyring():
    # Select native secure backends explicitly. Never auto-select an optional
    # plaintext keyrings.alt backend installed by another application.
    if sys.platform == "darwin":
        from keyring.backends.macOS import Keyring
    elif sys.platform.startswith("linux"):
        from keyring.backends.SecretService import Keyring
    else:
        raise LauncherError(tr("Kein nativer Schlüsselbund verfügbar."))
    return Keyring()


def minecraft_command(version: str, game_root: Path, options: dict) -> list[str]:
    arguments = command.get_minecraft_command(version, game_root, options)
    result = []
    index = 0
    while index < len(arguments):
        # Library 8.0 leaves these optional telemetry identity values unresolved
        # in current manifests. Omit the optional flag/value pair when unavailable.
        optional = {"--clientId": "${clientid}", "--xuid": "${auth_xuid}"}
        if (arguments[index] in optional and index + 1 < len(arguments)
                and arguments[index + 1] == optional[arguments[index]]):
            index += 2
            continue
        if "${" in arguments[index]:
            raise LauncherError(tr("Das Versionsmanifest enthält einen unbekannten Startparameter. Bitte den Launcher aktualisieren."))
        result.append(arguments[index])
        index += 1
    return result


def atomic_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


@dataclass
class Settings:
    language: str = "de"
    client_id: str = ""
    memory_mb: int = 4096
    selected_version: str = ""
    version_filter: str = "Vollversionen"
    java_path: str = ""
    offline_mode: bool = False
    offline_name: str = "Spieler"
    community_mode: bool = False
    selected_profile: str = ""

    @classmethod
    def load(cls, root: Path) -> "Settings":
        try:
            raw = json.loads((root / "settings.json").read_text(encoding="utf-8"))
            result = cls(**{f.name: raw[f.name] for f in fields(cls) if f.name in raw})
            result.memory_mb = int(result.memory_mb)
            result.language = result.language if result.language in ('de', 'en') else 'de'
            if not 1024 <= result.memory_mb <= 32768:
                result.memory_mb = 4096
            for key in ("client_id", "selected_version", "version_filter", "java_path", "offline_name", "selected_profile"):
                if not isinstance(getattr(result, key), str):
                    setattr(result, key, getattr(cls(), key))
            try:
                result.offline_name = local_profile(result.offline_name)["name"]
            except LauncherError:
                result.offline_name = "Spieler"
            result.offline_mode = result.offline_mode is True
            result.community_mode = result.community_mode is True
            if result.community_mode:
                result.offline_mode = True
            result.community_mode = False  # Migrate the retired third mode to Offline.
            result.version_filter = "Snapshots" if result.version_filter == "Snapshots" else "Vollversionen"
            return result
        except (OSError, ValueError, TypeError, AttributeError):
            return cls()

    def save(self, root: Path) -> None:
        atomic_json(root / "settings.json", asdict(self))


def valid_client_id(value: str) -> str:
    value = value.strip()
    try:
        parsed = uuid.UUID(value)
        if parsed.int == 0:
            raise ValueError
        return str(parsed)
    except (ValueError, AttributeError):
        raise LauncherError(tr("Bitte trage unter Einstellungen eine gültige Microsoft-App-ID (Client-ID) ein.")) from None


def bundled_client_id() -> str:
    """Public publisher configuration; never an account token or client secret."""
    folder = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    file = folder / "launcher-auth.json"
    if not file.exists():
        return ""
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        if data.get("schema") != 1 or not isinstance(data.get("client_id"), str):
            raise ValueError
        if data['client_id'].strip():return valid_client_id(data['client_id'])
        # Older POSIX updaters preserve the former empty launcher-auth.json.
        # New source releases carry the public publisher default in their inventory.
        manifest = folder / 'release-source.json'
        if manifest.is_file() and manifest.stat().st_size <= 256 * 1024:
            publisher = json.loads(manifest.read_text(encoding='utf-8')).get('publisher_client_id', '')
            if publisher:return valid_client_id(publisher)
        return ''
    except (OSError, ValueError, TypeError, AttributeError, LauncherError):
        raise LauncherError(tr("Die Launcher-Konfiguration launcher-auth.json ist ungültig. Bitte eine korrigierte Ausgabe von Blockwerk verwenden.")) from None


def safe_version_id(value: str) -> str:
    # Mojang has legitimate IDs such as "1.14 Pre-Release 1" and
    # "3D Shareware v1.34". Spaces inside a name are valid; paths are not.
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+ \-]{0,100}", value) or value.endswith((" ", ".")):
        raise LauncherError(tr("Ungültige Versionskennung."))
    return value


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def protect(data: bytes, decrypt: bool = False) -> bytes:
    if os.name != "nt":
        raise LauncherError(tr("Die sichere Kontospeicherung benötigt Windows."))
    buffer = ctypes.create_string_buffer(data)
    incoming = DATA_BLOB(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    outgoing = DATA_BLOB()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    function = crypt32.CryptUnprotectData if decrypt else crypt32.CryptProtectData
    function.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.c_void_p, ctypes.POINTER(DATA_BLOB),
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
    function.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    if not function(ctypes.byref(incoming), None, None, None, None, 1, ctypes.byref(outgoing)):
        raise LauncherError(tr("Windows konnte die gespeicherte Anmeldung nicht öffnen. Bitte erneut anmelden."))
    try:
        return ctypes.string_at(outgoing.pbData, outgoing.cbData)
    finally:
        kernel32.LocalFree(outgoing.pbData)


class AccountStore:
    def __init__(self, root: Path):
        self.path = root / "account.dpapi"
        self._session: dict | None = None
        self.session_only = False
        self.keyring_user = hashlib.sha256(str(root.resolve()).encode()).hexdigest()
        self._keyring_persistent = False

    @property
    def persistent(self) -> bool:
        return (self.path.exists() or self._keyring_persistent) and not self.session_only

    def read(self) -> dict | None:
        if self._session:
            return self._session.copy()
        try:
            if sys.platform == "win32":
                if not self.path.exists():
                    return None
                raw = protect(self.path.read_bytes(), decrypt=True)
            else:
                raw = native_keyring().get_password("Blockwerk", self.keyring_user)
                if not raw:
                    return None
                self._keyring_persistent = True
            result = json.loads(raw)
            if not all(isinstance(result.get(k), str) and result[k] for k in ("name", "id", "refresh_token", "client_id")):
                raise ValueError
            return result
        except Exception:
            raise LauncherError(tr("Die gespeicherte Anmeldung ist nicht verfügbar. Bitte abmelden und erneut anmelden.")) from None

    def write(self, profile: dict, client_id: str) -> None:
        saved = {k: profile[k] for k in ("name", "id", "refresh_token")}
        saved["client_id"] = client_id
        saved["license_verified"] = True
        try:
            if sys.platform != "win32":
                native_keyring().set_password("Blockwerk", self.keyring_user, json.dumps(saved))
                self._session = saved
                self._keyring_persistent = True
                self.session_only = False
                return
            encrypted = protect(json.dumps(saved).encode("utf-8"))
        except Exception:
            # Restricted Windows profiles may not have a DPAPI master key. Keep
            # the session usable, but never fall back to a plaintext token file.
            self.path.unlink(missing_ok=True)
            self._session = saved
            self.session_only = True
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_bytes(encrypted)
        temporary.replace(self.path)
        self._session = saved
        self.session_only = False

    def delete(self) -> None:
        if sys.platform == "win32":
            self.path.unlink(missing_ok=True)
        elif self._keyring_persistent:
            try:
                native_keyring().delete_password("Blockwerk", self.keyring_user)
            except Exception:
                raise LauncherError(tr("Der Schlüsselbund konnte die Anmeldung nicht entfernen. Bitte entsperren und erneut abmelden.")) from None
        self._session = None
        self.session_only = False
        self._keyring_persistent = False


def parse_callback(path: str, state: str) -> str | None:
    parsed = urlsplit(path)
    if parsed.path != "/callback":
        return None
    query = parse_qs(parsed.query)
    received = query.get("state", [""])
    if len(received) != 1 or not secrets.compare_digest(received[0], state):
        return None
    if "error" in query:
        raise LauncherError(tr("Die Microsoft-Anmeldung wurde abgelehnt oder abgebrochen."))
    code = query.get("code", [])
    if len(code) != 1 or not code[0]:
        return None
    return code[0]


def exchange_microsoft_login(client_id: str, code: str, verifier: str,
                             cancel: threading.Event, notify: Callable[[str], None]) -> dict:
    """Public library endpoints with cancellation and safe response validation."""
    def check():
        if cancel.is_set():
            raise Cancelled(tr("Anmeldung abgebrochen."))

    def text(data, field, message):
        if not isinstance(data, dict) or not isinstance(data.get(field), str) or not data[field]:
            raise LauncherError(message)
        return data[field]

    check()
    notify(tr("Microsoft und Xbox werden verbunden …"))
    token = microsoft_account.get_authorization_token(client_id, None, REDIRECT_URI, code, verifier)
    check()
    if isinstance(token, dict) and token.get("error") == "invalid_grant":
        raise LauncherError(tr("Diese Anmeldung ist abgelaufen oder wurde bereits verwendet. Bitte starte die Microsoft-Anmeldung erneut."))
    token_error = "Microsoft hat die Anmeldung nicht bestätigt. Der Projektbetreiber muss App-Registrierung, Kontotyp und Redirect-URI prüfen."
    access = text(token, "access_token", token_error)
    refresh = text(token, "refresh_token", token_error)
    xbl = microsoft_account.authenticate_with_xbl(access)
    check()
    xbox_error = "Xbox konnte dein Konto nicht verbinden. Öffne dein Xbox-Profil im offiziellen Launcher und prüfe gegebenenfalls die Microsoft-Familieneinstellungen."
    xbl_token = text(xbl, "Token", xbox_error)
    try:
        userhash = xbl["DisplayClaims"]["xui"][0]["uhs"]
        if not isinstance(userhash, str) or not userhash:
            raise ValueError
    except (KeyError, IndexError, TypeError, ValueError):
        raise LauncherError(xbox_error) from None
    xsts = microsoft_account.authenticate_with_xsts(xbl_token)
    check()
    xsts_token = text(xsts, "Token", xbox_error)
    minecraft = microsoft_account.authenticate_with_minecraft(userhash, xsts_token)
    check()
    if not isinstance(minecraft, dict) or not minecraft.get("access_token"):
        raise LauncherError(tr("Minecraft hat den Zugriff abgelehnt. Der Projektbetreiber muss die Minecraft-API-Freigabe der App prüfen; auch eine Dienststörung ist möglich. Bitte später erneut versuchen."))
    game_token = text(minecraft, "access_token", "Minecraft hat keine gültige Anmeldung geliefert. Bitte erneut versuchen.")
    profile = microsoft_account.get_profile(game_token)
    check()
    if isinstance(profile, dict) and profile.get("error") == "NOT_FOUND":
        raise microsoft_account.AccountNotOwnMinecraft()
    text(profile, "name", "Dein Minecraft-Java-Profil fehlt. Öffne Minecraft zuerst im offiziellen Launcher.")
    text(profile, "id", "Dein Minecraft-Java-Profil ist unvollständig. Öffne Minecraft zuerst im offiziellen Launcher.")
    return dict(profile, access_token=game_token, refresh_token=refresh)


def browser_login(client_id: str, cancel: threading.Event, notify: Callable[[str], None],
                  link_ready: Callable[[str], None] | None = None) -> dict:
    """Public-client OAuth with PKCE, random state and a loopback-only callback."""
    client_id = valid_client_id(client_id)
    if cancel.is_set():
        raise Cancelled(tr("Anmeldung abgebrochen."))
    login_url, state, verifier = microsoft_account.get_secure_login_data(client_id, REDIRECT_URI)
    # Use the Microsoft consumer tenant; an enterprise tenant cannot sign into Xbox.
    login_url = login_url.replace("/common/", "/consumers/")
    parsed = urlsplit(login_url)
    parameters = parse_qs(parsed.query)
    parameters["prompt"] = ["select_account"]
    login_url = urlunsplit(parsed._replace(query=urlencode(parameters, doseq=True)))
    result: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # Callback URLs contain one-time credentials; never log them.

        def do_GET(self):
            try:
                code = parse_callback(self.path, state)
                if code is None:
                    self.send_error(400, "Invalid callback")
                    return
                result["code"] = code
                page = "Microsoft hat geantwortet. Kehre zu Blockwerk zurück. Dort werden dein Xbox-Profil und Minecraft Java jetzt geprüft."
            except LauncherError as error:
                result["error"] = error
                page = "Die Anmeldung wurde abgebrochen. Kehre zu Blockwerk zurück, um es erneut zu versuchen."
            body = ("<!doctype html><meta charset='utf-8'><title>Blockwerk</title>"
                    "<body style='background:#111913;color:#ebf2e8;font:20px system-ui;padding:12vw'>"
                    "<h1>Blockwerk</h1><p>" + page + "</p></body>").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'")
            self.end_headers()
            self.wfile.write(body)

    try:
        server = HTTPServer(("127.0.0.1", 29147), Handler)
    except OSError:
        raise LauncherError(tr("Port 29147 ist belegt. Schließe andere Launcher-Anmeldungen und versuche es erneut.")) from None
    server.timeout = 0.4
    try:
        notify(tr("Bitte im Microsoft-Browserfenster anmelden …"))
        if link_ready:
            link_ready(login_url)
        if not open_browser(login_url) and not link_ready:
            raise LauncherError(tr("Der Browser konnte nicht geöffnet werden. Bitte einen Standardbrowser einrichten."))
        deadline = time.monotonic() + 300
        while not result:
            if cancel.is_set():
                raise Cancelled(tr("Anmeldung abgebrochen."))
            if time.monotonic() >= deadline:
                raise LauncherError(tr("Anmeldung nach 5 Minuten abgelaufen. Bitte erneut versuchen."))
            server.handle_request()
        if "error" in result:
            raise result["error"]
    finally:
        server.server_close()
        if link_ready:
            link_ready("")
    if cancel.is_set():
        raise Cancelled(tr("Anmeldung abgebrochen."))
    return exchange_microsoft_login(client_id, result["code"], verifier, cancel, notify)


def validate_profile(profile: dict) -> None:
    if not all(isinstance(profile.get(k), str) and profile[k] for k in ("name", "id", "access_token", "refresh_token")):
        raise LauncherError(tr("Microsoft hat kein vollständiges Minecraft-Java-Profil geliefert. Öffne Minecraft zuerst im offiziellen Launcher."))
    uuid.UUID(profile["id"])
    store = microsoft_account.get_store_information(profile["access_token"])
    # Online mode requires a genuine Minecraft entitlement.
    if not any(item.get("name") in ("game_minecraft", "product_minecraft") for item in store.get("items", [])):
        raise LauncherError(tr("Dieses Konto besitzt keine nutzbare Minecraft-Java-Lizenz. Prüfe Kauf oder Game Pass im offiziellen Launcher."))


def filter_versions(versions: list[dict], kind: str, search: str = "") -> list[dict]:
    kind = source_text(kind)
    predicate = is_snapshot if kind == "Snapshots" else (lambda v: is_release(v) or is_snapshot(v)) if kind == "Alle" else is_release
    return [v for v in versions if predicate(v)
            and search.casefold() in v["id"].casefold()]


def add_world_launch(options: dict, metadata: dict, directory: Path, folder: str | None) -> bool:
    if folder is None:
        return False
    if not folder or Path(folder).name != folder or folder in (".", "..") or any(c in folder for c in ("/", "\\", ":")) or any(ord(c) < 32 for c in folder):
        raise LauncherError(tr("Ungültiger Weltordner."))
    saves = (directory / "saves").resolve()
    world = saves / folder
    if not world.resolve().is_relative_to(saves) or not (world / "level.dat").is_file():
        raise LauncherError(tr("Die ausgewählte Welt liegt nicht im Spielordner."))
    if "${quickPlaySingleplayer}" not in json.dumps(metadata.get("arguments", {})):
        return False
    options.update(quickPlaySingleplayer=folder, quickPlayPath="quickPlay/blockwerk.json")
    return True


def human_error(error: Exception) -> str:
    if isinstance(error, LauncherError):
        return str(error)
    name = type(error).__name__
    messages = {
        "AzureAppNotPermitted": tr("Microsoft hat geantwortet, aber Blockwerk hat für diese App-Kennung keine Minecraft-API-Freigabe. Der Projektbetreiber muss die Freigabe abschließen. Dein Passwort behebt das nicht."),
        "AccountNotOwnMinecraft": tr("Dieses Microsoft-Konto hat kein Minecraft-Java-Profil. Prüfe Lizenz und Konto im offiziellen Launcher."),
        "InvalidRefreshToken": tr("Die gespeicherte Anmeldung ist abgelaufen. Bitte abmelden und erneut bei Microsoft anmelden."),
        "XSTSError": tr("Xbox Live hat die Anmeldung abgelehnt. Prüfe Xbox-Profil und bei Kinderkonten die Microsoft-Familieneinstellungen."),
        "FileOutsideMinecraftDirectory": tr("Ein Downloadpfad wurde aus Sicherheitsgründen abgelehnt."),
        "VersionNotFound": tr("Diese Version oder Java-Laufzeit ist auf den Downloadservern nicht verfügbar."),
        "InvalidChecksum": tr("Ein Download war unvollständig. Bitte erneut starten; die Installation wird geprüft."),
    }
    if name in messages:
        return messages[name]
    if isinstance(error, requests.RequestException):
        return tr("Der Online-Dienst ist nicht erreichbar oder hat die Anfrage abgelehnt. Prüfe deine Internetverbindung und versuche es erneut.")
    if isinstance(error, PermissionError):
        return tr("Kein Schreibzugriff. Prüfe den Blockwerk-Datenordner und freien Speicherplatz.")
    if isinstance(error, OSError):
        return tr("Datei oder Programm nicht verfügbar. Prüfe Speicherplatz und den eingestellten Java-Pfad.")
    return tr("Der Vorgang konnte nicht abgeschlossen werden (") + name + tr("). Bitte erneut versuchen.")


class LauncherService:
    def __init__(self, root: Path | None = None, allow_custom_versions: bool = False):
        configure_network()
        self.root = root or data_directory()
        self.root.mkdir(parents=True, exist_ok=True)
        self.settings = Settings.load(self.root)
        if not self.settings.client_id:
            self.settings.client_id = bundled_client_id()
        self.accounts = AccountStore(self.root)
        self.allow_custom_versions = allow_custom_versions

    def version_metadata(self, version: str) -> dict:
        safe_version_id(version)
        file = self.game_root / "versions" / version / (version + ".json")
        data = json.loads(file.read_text(encoding="utf-8"))
        if data.get("inheritsFrom"):
            safe_version_id(data["inheritsFrom"])
            from minecraft_launcher_lib._helper import inherit_json
            data = inherit_json(data, self.game_root)
        return data

    @property
    def game_root(self) -> Path:
        return self.root / "minecraft"

    def game_directory(self, version: str, local_name: str | None = None) -> Path:
        if local_name is not None:
            return self.root / "instances" / "local" / local_profile(local_name)["name"] / safe_version_id(version)
        return self.root / "instances" / safe_version_id(version)

    def check_supported_version(self, version: str):
        if self.allow_custom_versions or is_release({"id": version, "type": "release"}):
            return
        try:
            cached = json.loads((self.root / "versions-cache.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cached = []
        if isinstance(cached, list) and any(is_snapshot(v) and v["id"] == version for v in cached):
            return
        try:
            metadata = self.version_metadata(version)
            if metadata.get("id") == version and is_snapshot(metadata):
                return
        except (OSError, ValueError, KeyError):
            pass
        raise LauncherError(tr("Bitte eine Vollversion ab 1.0 oder einen Snapshot aus dem offiziellen Katalog auswählen. Aktualisiere gegebenenfalls die Versionsliste."))

    def prepare_local_version(self, version: str, cancel: threading.Event, notify: Callable[[str], None],
                              progress: Callable[[int, int], None]) -> str:
        """Explicit network-enabled file installation, independent of accounts."""
        check_runtime_platform(self.settings.java_path)
        version = safe_version_id(version)
        self.check_supported_version(version)
        maximum = 1
        def check():
            if cancel.is_set():
                raise Cancelled(tr("Download abgebrochen."))
        def status(text):
            check()
            notify(str(text))
        def set_max(value):
            nonlocal maximum
            check()
            maximum = max(1, int(value))
        def advanced(value):
            check()
            progress(int(value), maximum)
        callbacks = {"setStatus": status, "setMax": set_max, "setProgress": advanced}
        notify(tr("Spieldateien werden ohne Konto-Anmeldung heruntergeladen. Internet wird benötigt …"))
        self.game_root.mkdir(parents=True, exist_ok=True)
        install.install_minecraft_version(version, self.game_root, callback=callbacks)
        check()
        metadata = self.version_metadata(version)
        jar_id = safe_version_id(metadata.get("jar", version))
        jar = self.game_root / "versions" / jar_id / (jar_id + ".jar")
        with jar.open("rb") as stream:
            expected = metadata.get("downloads", {}).get("client", {}).get("sha1")
            if expected and hashlib.file_digest(stream, "sha1").hexdigest() != expected:
                raise LauncherError(tr("Der Client-Download ist beschädigt. Bitte erneut herunterladen."))
        if self.settings.java_path:
            executable = validate_java(self.settings.java_path)
        else:
            component = metadata.get("javaVersion", {}).get("component", "jre-legacy")
            executable = runtime.get_executable_path(component, self.game_root)
            if not executable:
                runtime.install_jvm_runtime(component, self.game_root, callback=callbacks)
                executable = runtime.get_executable_path(component, self.game_root)
            if not executable or not Path(executable).is_file():
                raise LauncherError(tr("Kein passendes Java verfügbar. Bitte unter Einstellungen auswählen."))
        self.prepare_offline(version, metadata, executable, "", cancel, progress)
        return version

    def list_versions(self, offline: bool = False) -> tuple[list[dict], bool]:
        cache = self.root / "versions-cache.json"
        if offline:
            try:
                versions = json.loads(cache.read_text(encoding="utf-8"))
                return filter_versions(versions, "Alle"), True
            except (OSError, ValueError, TypeError, KeyError):
                raise LauncherError(tr("Kein lokaler Versionskatalog. Bitte einmal im Online-Modus aktualisieren.")) from None
        try:
            response = requests.get(MANIFEST_URL)
            response.raise_for_status()
            versions = filter_versions(response.json()["versions"], "Alle")
            if not versions:
                raise LauncherError(tr("Der Versionskatalog enthält keine gültigen Releases."))
            for item in versions:
                safe_version_id(item["id"])
            atomic_json(cache, versions)
            return versions, False
        except (requests.RequestException, ValueError, KeyError, LauncherError):
            if cache.exists():
                try:
                    versions = json.loads(cache.read_text(encoding="utf-8"))
                    for item in versions:
                        safe_version_id(item["id"])
                    return filter_versions(versions, "Alle"), True
                except (ValueError, KeyError, TypeError, LauncherError):
                    pass
            raise LauncherError(tr("Versionsliste konnte nicht geladen werden. Prüfe die Internetverbindung und klicke auf Aktualisieren.")) from None

    def login(self, cancel: threading.Event, notify: Callable[[str], None],
              link_ready: Callable[[str], None] | None = None) -> str:
        client_id = valid_client_id(self.settings.client_id)
        profile = browser_login(client_id, cancel, notify, link_ready)
        if cancel.is_set():
            raise Cancelled(tr("Anmeldung abgebrochen."))
        notify(tr("Deine Minecraft-Java-Lizenz wird geprüft …"))
        validate_profile(profile)
        if cancel.is_set():
            raise Cancelled(tr("Anmeldung abgebrochen."))
        self.accounts.write(profile, client_id)
        return profile["name"]

    def launch(self, version: str, cancel: threading.Event, notify: Callable[[str], None],
               progress: Callable[[int, int], None], started: Callable[[], None], offline: bool = False,
               community_servers: list[dict] | None = None, world_folder: str | None = None) -> int:
        check_runtime_platform(self.settings.java_path)
        version = safe_version_id(version)
        self.check_supported_version(version)
        if offline:
            return self.launch_offline(version, cancel, notify, progress, started, community_servers, world_folder)
        client_id = valid_client_id(self.settings.client_id)
        saved = self.accounts.read()
        if not saved or saved["client_id"] != client_id:
            raise LauncherError(tr("Bitte zuerst mit dem Microsoft-Konto anmelden, das Minecraft Java besitzt."))

        def check():
            if cancel.is_set():
                raise Cancelled(tr("Vorgang abgebrochen. Bereits geprüfte Downloads bleiben erhalten."))

        notify(tr("Anmeldung und Minecraft-Lizenz werden geprüft …"))
        profile = microsoft_account.complete_refresh(client_id, None, None, saved["refresh_token"])
        validate_profile(profile)
        self.accounts.write(profile, client_id)
        check()
        maximum = 1

        def status(text):
            check()
            # Only installation status, never auth payloads or command arguments.
            notify(str(text))

        def maximum_changed(value):
            nonlocal maximum
            check()
            maximum = max(1, int(value))
            progress(0, maximum)

        def progressed(value):
            check()
            progress(int(value), maximum)

        callback = {"setStatus": status, "setMax": maximum_changed, "setProgress": progressed}
        notify("Minecraft " + version + tr(" wird geprüft und bei Bedarf heruntergeladen …"))
        self.game_root.mkdir(parents=True, exist_ok=True)
        install.install_minecraft_version(version, self.game_root, callback=callback)
        check()
        metadata = self.version_metadata(version)
        jar_id = safe_version_id(metadata.get("jar", version))
        client_file = self.game_root / "versions" / jar_id / (jar_id + ".jar")
        if not client_file.is_file():
            raise LauncherError(tr("Der Minecraft-Client wurde nicht vollständig heruntergeladen. Bitte erneut versuchen."))
        expected = metadata.get("downloads", {}).get("client", {}).get("sha1")
        if expected:
            with client_file.open("rb") as stream:
                actual = hashlib.file_digest(stream, "sha1").hexdigest()
            if actual != expected:
                raise LauncherError(tr("Die Prüfsumme des Minecraft-Clients stimmt nicht. Bitte erneut starten, um den Download zu reparieren."))
        options = {"username": profile["name"], "uuid": profile["id"], "token": profile["access_token"],
                   "launcherName": "Blockwerk", "launcherVersion": VERSION,
                   "jvmArguments": ["-Xms512M", "-Xmx" + str(self.settings.memory_mb) + "M"],
                   "gameDirectory": str(self.game_directory(version)), "enableLoggingConfig": True}
        if self.settings.java_path:
            options["executablePath"] = validate_java(self.settings.java_path)
        else:
            # Modern manifests install their designated runtime via the library.
            # Very old manifests omit javaVersion, so supply Mojang's Java 8 runtime.
            component = metadata.get("javaVersion", {}).get("component", "jre-legacy")
            executable = runtime.get_executable_path(component, self.game_root)
            if not executable:
                notify(tr("Passendes Java wird installiert: ") + component)
                runtime.install_jvm_runtime(component, self.game_root, callback=callback)
                executable = runtime.get_executable_path(component, self.game_root)
            if not executable or not Path(executable).is_file():
                raise LauncherError(tr("Mojang stellt für dieses System keine passende Java-Laufzeit bereit. Wähle Java unter Einstellungen manuell aus."))
            options["executablePath"] = executable
        check()
        # Refresh again after a lengthy first installation rather than launch with
        # an access token that could have expired during the downloads.
        notify(tr("Anmeldung für den Spielstart wird erneuert …"))
        profile = microsoft_account.complete_refresh(client_id, None, None, profile["refresh_token"])
        validate_profile(profile)
        self.accounts.write(profile, client_id)
        options.update(username=profile["name"], uuid=profile["id"], token=profile["access_token"])
        check()
        directory = self.game_directory(version)
        directory.mkdir(parents=True, exist_ok=True)
        notify(tr("Lokale Dateien werden für den Offline-Modus geprüft …"))
        self.prepare_offline(version, metadata, options["executablePath"], profile["id"], cancel, progress)
        check()
        quick_play = add_world_launch(options, metadata, directory, world_folder)
        if world_folder and not quick_play:
            notify(tr("Diese Version unterstützt keinen direkten Weltstart. Öffne Einzelspieler und wähle die Welt im Spiel aus."))
        arguments = minecraft_command(version, self.game_root, options)
        # Do not print arguments: they include the Minecraft access token.
        process = subprocess.Popen(arguments, cwd=directory, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        started()
        notify("Minecraft " + version + tr(" läuft. Viel Spaß!"))
        return process.wait()

    def receipt_path(self, version: str) -> Path:
        return self.root / "prepared" / (safe_version_id(version) + ".json")

    def offline_available(self, version: str) -> bool:
        return bool(version) and self.receipt_path(version).is_file()

    def _inside(self, base: Path, relative: str) -> Path:
        path = (base / relative).resolve()
        if not path.is_relative_to(base.resolve()):
            raise LauncherError(tr("Ungültiger lokaler Dateipfad."))
        return path

    def prepare_offline(self, version: str, metadata: dict, executable: str, account_id: str,
                        cancel: threading.Event, progress: Callable[[int, int], None]) -> None:
        files = set((self.game_root / "versions" / version).rglob("*"))
        if metadata.get("inheritsFrom"):
            parent_id = safe_version_id(metadata["inheritsFrom"])
            files.add(self.game_root / "versions" / parent_id / (parent_id + ".json"))
        logging = metadata.get("logging", {}).get("client", {}).get("file")
        if logging:
            files.add(self._inside(self.game_root / "assets" / "log_configs", logging["id"]))
        # Use the same platform/rule evaluation as the real command generator.
        native_only = {Path(command.get_library_path(lib["name"], str(self.game_root)))
                       for lib in metadata.get("libraries", [])
                       if "downloads" in lib and "artifact" not in lib["downloads"]
                       and "classifiers" in lib["downloads"]}
        for entry in command.get_libraries(metadata, str(self.game_root)).split(os.pathsep):
            # Legacy native-only Maven entries have no ordinary JAR. Library 8
            # still includes that nonexistent, harmless classpath element.
            if entry and Path(entry) not in native_only:
                files.add(Path(entry))
        component = metadata.get("javaVersion", {}).get("component", "jre-legacy")
        java_root = self.game_root / "runtime" / component
        if java_root.exists():
            files.update(java_root.rglob("*"))
        if metadata.get("assetIndex"):
            index_id = metadata.get("assets", metadata["assetIndex"]["id"])
            index_path = self._inside(self.game_root / "assets" / "indexes", index_id + ".json")
            files.add(index_path)
            assets = json.loads(index_path.read_text(encoding="utf-8"))
            for name, entry in assets.get("objects", {}).items():
                digest = entry["hash"]
                if not re.fullmatch(r"[a-f0-9]{40}", digest):
                    raise LauncherError(tr("Ungültiger Asset-Index."))
                source = self.game_root / "assets" / "objects" / digest[:2] / digest
                files.add(source)
                destinations = []
                if assets.get("virtual"):
                    destinations.append(self.game_root / "assets" / "virtual" / "legacy")
                if assets.get("map_to_resources") or index_id == "pre-1.6":
                    destinations.append(self.game_directory(version) / "resources")
                for destination in destinations:
                    target = self._inside(destination, name)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if not target.exists() or target.stat().st_size != source.stat().st_size:
                        shutil.copyfile(source, target)
                    files.add(target)
        # A missing required file must fail before Popen. Directories are not
        # inventory entries, but missing dependency paths are never skipped.
        # Runtime installer bookkeeping is rewritten on every repair and is not
        # read by the JVM. Only immutable launch dependencies belong in a receipt.
        selected = sorted((p for p in files if not p.is_dir() and not p.name.endswith(".sha1") and p.name != ".version"), key=str)
        inventory = []
        for index, file in enumerate(selected):
            if cancel.is_set():
                raise Cancelled(tr("Vorbereitung abgebrochen."))
            if not file.is_file():
                raise LauncherError(tr("Installation unvollständig. Bitte im Online-Modus erneut starten: ") + file.name)
            relative = str(file.resolve().relative_to(self.root.resolve()))
            with file.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            inventory.append({"path": relative, "sha256": digest})
            progress(index + 1, len(selected))
        with Path(executable).open("rb") as stream:
            java_hash = hashlib.file_digest(stream, "sha256").hexdigest()
        atomic_json(self.receipt_path(version), {"schema": 1, "version": version,
                    "platform": sys.platform, "machine": platform.machine(), "account_id": account_id,
                    "java": str(Path(executable).resolve()), "java_hash": java_hash, "files": inventory})

    def launch_offline(self, version: str, cancel: threading.Event, notify: Callable[[str], None],
                       progress: Callable[[int, int], None], started: Callable[[], None],
                       community_servers: list[dict] | None = None, world_folder: str | None = None) -> int:
        saved = local_profile(self.settings.offline_name)
        try:
            receipt = json.loads(self.receipt_path(version).read_text(encoding="utf-8"))
            if (receipt["schema"] != 1 or receipt["version"] != version or receipt["platform"] != sys.platform
                    or receipt["machine"] != platform.machine()):
                raise ValueError
            entries = receipt["files"]
            if not isinstance(entries, list) or not entries:
                raise ValueError
            notify(tr("Offline-Modus: lokale Spieldateien werden geprüft …"))
            for index, entry in enumerate(entries):
                if cancel.is_set():
                    raise Cancelled(tr("Offline-Start abgebrochen."))
                file = self._inside(self.root, entry["path"])
                with file.open("rb") as stream:
                    actual = hashlib.file_digest(stream, "sha256").hexdigest()
                if actual != entry["sha256"]:
                    raise ValueError
                progress(index + 1, len(entries))
            executable = validate_java(self.settings.java_path or receipt["java"])
            if str(Path(executable).resolve()) != receipt["java"]:
                raise ValueError
            with Path(executable).open("rb") as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != receipt["java_hash"]:
                    raise ValueError
        except (OSError, ValueError, KeyError, TypeError):
            raise LauncherError(tr("Die Spieldateien fehlen oder wurden verändert. Bitte mit Internet auf ‚Spieldateien herunterladen‘ klicken. Eine Microsoft-Anmeldung ist dafür nicht nötig.")) from None
        if cancel.is_set():
            raise Cancelled(tr("Offline-Start abgebrochen."))
        directory = self.game_directory(version, saved["name"])
        directory.mkdir(parents=True, exist_ok=True)
        from .servers import ServerStore, prepare_server_file
        legacy = self.root / "instances" / "community" / saved["name"] / version / "servers.dat"
        rows = community_servers if community_servers is not None else ServerStore(self.root).list()
        prepare_server_file(directory / "servers.dat", rows, legacy)
        resources = self.game_directory(version) / "resources"
        if resources.is_dir():
            shutil.copytree(resources, directory / "resources", dirs_exist_ok=True)
        options = {"username": saved["name"], "uuid": saved["id"], "token": "0",
                   "executablePath": executable, "launcherName": "Blockwerk", "launcherVersion": VERSION,
                   "jvmArguments": ["-Xms512M", "-Xmx" + str(self.settings.memory_mb) + "M"],
                   "gameDirectory": str(directory), "enableLoggingConfig": True}
        metadata = self.version_metadata(version)
        quick_play = add_world_launch(options, metadata, directory, world_folder)
        if world_folder and not quick_play:
            notify(tr("Diese Version unterstützt keinen direkten Weltstart. Öffne Einzelspieler und wähle die Welt im Spiel aus."))
        arguments = minecraft_command(version, self.game_root, options)
        process = subprocess.Popen(arguments, cwd=directory, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        started()
        notify("Minecraft " + version + tr(" läuft mit lokalem Profil. Mehrspieler ist für Server verfügbar, die lokale Profile zulassen."))
        return process.wait()
