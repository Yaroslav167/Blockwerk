Aktueller Microsoft-Status ab 0.9.1: Eigene Client-ID registriert und
vorkonfiguriert, Minecraft-API-Freigabe weiterhin offen. Siehe AUTH-STATUS.md.
Ältere Hinweise auf eine noch fehlende Registrierung sind überholt.

# Blockwerk 0.9.0 · überarbeitete Linux-/macOS-Quellpakete

## Funktionsstand

Dieselbe Python-/Qt-Anwendung wie Windows 0.9.0: Deutsch/English, Animation,
Release-/Snapshot-Auswahl, lokale Profile, Mehrspieler ohne Fünferlimit,
gespeicherte Minecraft-Serverlisten, Welten/Spielkopien, neue Welten über
Minecraft, Skin-Auswahl/-Import, lokale Skinpakete und getrennte
Fabric-/Forge-/Quilt-/NeoForge-Profile.

| Funktion | Linux-/macOS-Quellpaket |
| --- | --- |
| Oberfläche und Sprache | Gemeinsamer Code mit Windows |
| Minecraft, Welten, Skins, Server, Mods | Enthalten; native Spielsitzungen hier nicht geprüft |
| Microsoft-Anmeldung/Konto-Skins | Weiterhin keine freigegebene App-ID mitgeliefert |
| Sicherer Kontospeicher | macOS Keychain / Linux Secret Service; sonst Sitzungsspeicher |
| Wöchentliche Updateprüfung | Eigener lokaler Kanal oder HTTPS erforderlich |
| Update installieren und neu starten | Für diese verwalteten Quellpakete eingebaut |
| Selbst gebaute native App aktualisieren | Paket herunterladen und manuell ersetzen |
| Fremdinstaller | JAR; Windows-EXE-Installer laufen nur unter Windows |
| Native Binärpakete / Signierung | Hier nicht auf Linux/macOS gebaut oder signiert |

## Linux starten

64-Bit-Linux mit glibc 2.34+ auf x64 bzw. glibc 2.39+ auf ARM64,
Python 3.12 und eine Desktop-Sitzung mit X11/Wayland verwenden. Die Startlogik
akzeptiert auch Python 3.13/3.14 mit passenden Bibliotheks-Wheels; 3.12 ist die
hier verwendete Basis. Für Debian/Ubuntu werden u.a. diese Pakete benötigt:

```sh
sudo apt install python3-venv libegl1 libopengl0 libxcb-cursor0 libdbus-1-3 fonts-dejavu-core
sh start-linux.sh
```

Ist python3 älter als 3.12, Python 3.12 separat installieren und auswählen:

```sh
BLOCKWERK_PYTHON=/pfad/zu/python3.12 sh start-linux.sh
```

Für dauerhafte Kontospeicherung muss ein Secret-Service-Schlüsselbund in der
D-Bus-Sitzung verfügbar und entsperrt sein. Sonst bleibt eine Anmeldung nur für
diese Sitzung erhalten. Ein headless Server ist kein Minecraft-Desktop.

**Linux ARM64:** Die verwendete Launcher-Bibliothek 8.0 wählt beim automatischen
Java-Download den x86-Linux-Kanal. Blockwerk fordert deshalb vor Installation
oder Spielstart ein eigenes ARM-Java unter Einstellungen an. Minecraft und Mods
müssen ebenfalls ARM unterstützen. Insbesondere alte native Bibliotheken können
ARM ausschließen; eine universelle Spielekompatibilität ist nicht bestätigt.

## macOS starten

macOS 14 oder neuer verwenden. Python 3.12 für die eigene Architektur installieren, ZIP entpacken und
start-macos.command öffnen oder im Terminal ausführen:

```sh
sh start-macos.command
```

Das Skript ist im Archiv ausführbar markiert. Falls ein Entpacker dies verliert:
chmod +x start-macos.command. macOS-Sicherheitsentscheidungen und ggf. die
Python-Zertifikatseinrichtung erfolgen mit den normalen Systemwerkzeugen.

Apple Silicon und Intel verwenden getrennte Python-Umgebungen. Alte
Minecraft-Versionen mit ausschließlich Intel-Natives benötigen gegebenenfalls
eine konsistente Intel-Umgebung unter Rosetta: Intel-Python, Intel-Java und
passende Spiel-/Mod-Natives. Nur Java zu wechseln garantiert diese Konsistenz
nicht. Diese Umgebung wurde hier nicht nativ getestet. Mit BLOCKWERK_PYTHON
kann der gewünschte Python-Interpreter ausgewählt werden.

## Neue Startlogik

Der erste Start benötigt Internet für Python-Bibliotheken. Die Umgebung liegt
außerhalb des entpackten Programms im Benutzerdatenordner unter
launcher-runtime/Python-ABI-System-Architektur-Abhängigkeitenhash. Sie bleibt
bei Updates am gleichen Ort. Andere Architekturen oder geänderte Abhängigkeiten
bekommen getrennte Umgebungen. Eine POSIX-Dateisperre serialisiert Erststarts.

Erst nach Installation und Importprüfung entsteht die Bereit-Markierung.
Danach erfolgt bei unveränderten Abhängigkeiten kein pip-Aufruf. Die frühere
.venv/.blockwerk-0.4.0-ready wird nicht mehr verwendet; alte Umgebungen werden
nicht gelöscht. Start- und Installationsfehler stehen unter logs/launcher-start.log:

- macOS: ~/Library/Application Support/Blockwerk
- Linux: $XDG_DATA_HOME/blockwerk bzw. ~/.local/share/blockwerk
- BLOCKWERK_DATA_DIR überschreibt den Datenordner.

Diagnose ohne Kontozugriff oder Spielstart:

```sh
sh start-linux.sh --check-platform platform-check.json
# macOS:
sh start-macos.command --check-platform platform-check.json
```

## Launcher-Updates

release-source.json enthält Version und Prüfsummen der verwalteten Programmdateien.
Unter Updates den Ordner mit Blockwerk-Updates.json oder eine HTTPS-Quelle wählen.
Ein Feed direkt neben dem entpackten Blockwerk-Ordner wird automatisch gefunden.
Feed und darin genanntes Archiv müssen erreichbar sein. Es gibt hier keinen
öffentlichen Updatehost; neue Software muss zunächst veröffentlicht werden.

Nach sieben Tagen wird beim nächsten Start bzw. während der Nutzung geprüft.
Minecraft, Mods und Welten werden dabei nicht aktualisiert. Nach geprüftem
Download mit Installieren & Launcher neu starten fortfahren. Der separate
Python-Helfer wartet auf das Beenden der App und ersetzt verwaltete Programmdateien.
Er sichert frühere Dateien im Ordner .Blockwerk-source-backup-… daneben.

Spieldaten, unbekannte lokale Dateien, Python-Umgebungen sowie launcher-auth.json
und update-source.json bleiben erhalten. Eigene Änderungen an Programmdateien
führen zum Abbruch und erfordern manuelle Installation. Erkannte Kopier- oder
Neustartfehler rollen die ersetzten Dateien zurück. Das ist keine Garantie gegen
Stromausfall oder defekte Datenträger.

Ältere Quellpakete ohne Inventar einmal manuell durch dieses Paket ersetzen.
Spieldaten im Benutzerdatenordner werden weiterverwendet. Selbst gebaute native
Linux-/macOS-Apps bleiben manuelle Installationen; die Windows-Update-EXE wird
auf POSIX nicht verwendet.

## Native App auf dem Zielsystem bauen

```sh
sh start-linux.sh --build-native
# oder auf einem Mac:
sh start-macos.command --build-native
```

Die Build-Umgebung wird eingerichtet. Ergebnisse: dist/Blockwerk-Linux-Architektur
bzw. dist/Blockwerk-macOS-Architektur. Auf macOS enthält der Paketordner Blockwerk.app.
Der gesamte Ordner gehört zur Ausgabe. PyInstaller benötigt zum Bauen jeweils
das Zielbetriebssystem; eine auf Windows umbenannte Datei ist keine Mac-App.

Die vorbereitete GitHub-Actions-Matrix umfasst Windows, Linux x64/ARM64 und
macOS Apple Silicon/Intel. Sie prüft Shell-Syntax, Unit-Tests und native Appstarts
mit Screenshots in beiden Sprachen. Der Workflow wurde hier nicht extern
ausgeführt; es wurde kein öffentliches Repository angelegt.

## Prüfstand

122 Tests auf Windows: 121 bestanden, ein POSIX-Test für Ausführungsbits übersprungen.
Die POSIX-Update-Dateioperationen liefen mit isolierten Paketen auf Windows.
Bootstrap-Tests simulieren Unix-Prozesse, Paketinstallation und POSIX-Sperre.
Ausführungsrechte werden zusätzlich an den erzeugten Archiven geprüft.

Hier ist Windows verfügbar; WSL/Linux und macOS sind nicht installiert.
Native Appstarts, Finder/Wayland/X11, Keychain/Secret Service, Grafik, Audio,
Eingabe, Serverbeitritte und vollständige Java-/Mod-Spielsitzungen müssen auf den
Zielsystemen noch getestet werden. Ohne freigegebenen Microsoft-Client ist auch
hier keine vollständige echte Microsoft-Anmeldung nachgewiesen. Eine Garantie
für alle Mods oder Versionen wird nicht gegeben.

Systemanforderungen der tatsächlich verwendeten Qt-Wheels:
[PySide6-Essentials 6.12.0](https://pypi.org/project/PySide6-Essentials/6.12.0/).

Quellen: [PyInstaller](https://pyinstaller.org/en/stable/usage.html#supporting-multiple-operating-systems),
[Python venv](https://docs.python.org/3/library/venv.html),
[GitHub-Runner](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
