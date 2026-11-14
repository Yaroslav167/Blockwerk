# Blockwerk · Downloads

[Windows, Linux und macOS: Version 0.9.1 herunterladen](https://github.com/Yaroslav167/Blockwerk/releases/tag/v0.9.1)

Die verteilten Pakete verwenden den öffentlichen GitHub-Release-Feed für Launcher-Updates.
Ältere Hinweise auf den lokalen Ausgabeordner als einzigen Updatekanal sind überholt.
Linux/macOS sind in dieser Veröffentlichung Quellpakete; native Build-Ergebnisse
werden erst nach bestandenen Zielsystem-Prüfungen als solche bezeichnet.

Microsoft-Status 0.9.1: Eigene App-ID registriert und hinterlegt.
Minecraft-API-Freigabe bleibt ausdrücklich offen; der lokale Modus bleibt erhalten.
Eine vollständige echte Minecraft-Anmeldung ist weiterhin nicht bestätigt.
Details: AUTH-STATUS.md. Ältere Hinweise zur fehlenden Registrierung sind überholt.

# Blockwerk 0.9.1 · Minecraft Java Launcher

## macOS und Linux auf Stand 0.9.0

Überarbeitete Startskripte, externe Python-Umgebung je Architektur, Startprotokolle,
Plattformdiagnose und Update-Installation für verwaltete Quellpakete. Native Builds
sind auf dem Zielsystem mit --build-native vorbereitet.
Details und offene native Tests: [PLATTFORMEN.md](PLATTFORMEN.md).


## Deutsch / English

Oben rechts **Deutsch** oder **English** auswählen. Die Oberfläche wechselt direkt;
die Sprache bleibt nach Neustarts gespeichert. Während eines Downloads oder Spiels
ist die Auswahl gesperrt. Eigene Profil-, Welt- und Servernamen werden nicht übersetzt.
Die Sprache von Minecraft selbst wird weiterhin in dessen Einstellungen gewählt.

Choose **Deutsch** or **English** in the top-right corner. The interface switches
immediately and remembers your choice after restart. Language selection is disabled
while a task or game is running. Your own profile, world and server names stay unchanged.
Minecraft's own language is selected in the game's settings.


## Offline-Mehrspieler ohne Serverlimit

Ab 0.8 gibt es zwei Spielmodi. Offline unterstützt Einzelspieler und die normale
Minecraft-Serverliste ohne Fünferlimit. Unter Mehrspieler Server hinzufügen; die
Liste bleibt nach Neustarts erhalten. Details: MODS-UND-SERVER.md.

## Skins und wöchentliche Launcher-Updates

Unter **Skins** drei originale Blockwerk-Skins auswählen, eigene PNGs importieren,
Classic/Slim einstellen und die Figur mit der Maus drehen. Ein lokales
Ressourcenpaket zeigt den Skin auf diesem Computer auf den Standardfiguren der
gewählten Spielinstanz. Es ändert keinen Konto-Skin und ist für andere Spieler
nicht sichtbar. Der echte Konto-Upload benötigt weiterhin eine funktionierende
Microsoft-Anmeldung; die freigegebene App-ID fehlt in dieser Ausgabe.
PNG-Export und die offizielle Minecraft-Profilseite sind als Alternative vorhanden.

Unter **Updates** prüft der Launcher alle sieben Tage während der Nutzung seinen
Kanal auf veröffentlichte neue Launcher-Ausgaben. Nach geprüftem Download wird
Windows über **Installieren & Launcher neu starten** aktualisiert; der alte
App-Ordner bleibt als Sicherung erhalten. Minecraft, Mods und Welten werden dabei
nicht automatisch aktualisiert. Der Windows-Build verwendet den lokalen
Ausgabeordner als Kanal; eine öffentliche Update-Webseite ist nicht eingerichtet.
Andere Computer können ihren Kanal auswählen. Die überarbeiteten Linux-/macOS-
Quellpakete unterstützen die Installation über ihren Python-Helfer.
Details und Veröffentlichungsablauf: [SKINS-UND-UPDATES.md](SKINS-UND-UPDATES.md).

## Neu: Welten und Snapshots

Unter **Welten** findest du lokale Java-Spielstände aus Blockwerk, dem offiziellen
Minecraft-Ordner und zusätzlich gewählten Ordnern. Bestehende Welten lassen sich
öffnen, mit unterstützten Versionen direkt per Quick Play. Andere Quellen und
Versionswechsel verwenden Spielkopien. **Neue Welt in Minecraft** startet das
echte Spiel, in dem du die neue Welt mit Seed und Einstellungen erzeugst.

Über dem Versionswähler und auf der Versionen-Seite zwischen **Vollversionen**
und **Snapshots** umschalten. Der öffentliche Katalog enthielt am 26.10.2026 103 Releases
und 756 Snapshots, einschließlich dort geführter Pre-Releases/Release Candidates.
Details: [WELTEN-UND-SNAPSHOTS.md](WELTEN-UND-SNAPSHOTS.md).

## Neu: Eigene Microsoft-Kontoseite

Über **Microsoft-Konto** öffnet sich eine eigene Seite für Anmeldestatus,
Browser-Anmeldung, Fortschritt, Abbrechen, Kontowechsel und Abmelden. Passwörter
und Bestätigungscodes werden ausschließlich auf Microsofts Website eingegeben.
Die technische App-Registrierung steht getrennt unter **Einstellungen → Einrichtung
für Projektbetreiber**. Die Seite unterscheidet fehlende Registrierung, vorhandene
App-Kennung, laufende Anmeldung und tatsächlich geprüfte Minecraft-Berechtigung.

**Diese Ausgabe enthält weiterhin keine freigegebene App-Kennung.** Ihr fehlt
damit die externe Voraussetzung für einen vollständigen echten Microsoft-Login.
Eine schöner gestaltete Seite ersetzt die Registrierung und Minecraft-Freigabe
nicht. Der Projektbetreiber kann seine eigene freigegebene öffentliche Client-ID
vor dem Paketbau in `launcher-auth.json` eintragen, damit Spieler sie später
nicht selbst einrichten müssen. Keine Client-Secrets oder Tokens in diese Datei.

## Neu: Animation auf dem Hauptbildschirm

Die Blocklandschaft auf der Spielen-Seite ist animiert: schwebende Grasblöcke,
sanft bewegte Insel, ziehende Pixelwolken und funkelnde Partikel. Die Grafik wird
lokal mit Qt gezeichnet und benötigt keine Downloads oder Videodateien.
Mit „Animation pausieren“ lässt sich die Bewegung anhalten und fortsetzen.
Auf anderen Seiten sowie bei minimiertem oder geschlossenem Fenster hält der
Animationstimer an. Die detaillierte Landschaft wird zwischengespeichert.

## Mods und Server

Fabric, Forge, Quilt und NeoForge haben unter **Mods & Loader** eigene
installierbare Profile. Alle vier haben den echten Installationstest bestanden.
Lokale Mod-JARs können hinzugefügt, geprüft und aktiviert
oder deaktiviert werden. Andere Installer können manuell in den jeweiligen
Profilordner installieren; das erzeugte Minecraft-Profil wird danach übernommen.

**Offline · Einzelspieler & Server** verwendet ein lokales Profil. Der getrennte
Community-Modus und das Fünferlimit wurden entfernt. Im Minecraft-Menü
**Mehrspieler → Server hinzufügen** werden beliebig viele Server dauerhaft in
`servers.dat` gespeichert. Server müssen lokale Profile zulassen. Launcher-Favoriten
unter **Server** werden einmalig zur Liste des jeweiligen Spielprofils hinzugefügt;
Einträge, Reihenfolge, Bilder und Änderungen aus Minecraft bleiben erhalten.
Details: [MODS-UND-SERVER.md](MODS-UND-SERVER.md).

## Ohne Microsoft-Konto lokal spielen

1. Spielmodus **Offline · Einzelspieler & Server** auswählen.
2. Einen lokalen Spielernamen mit 3–16 Buchstaben, Ziffern oder Unterstrichen eingeben.
3. Gewünschtes offizielles Release ab 1.0 auswählen.
4. Falls noch nicht vorbereitet: **Spieldateien herunterladen** klicken. Dieser
   einzelne Schritt benötigt Internet und lädt Originaldateien und Java ohne
   Microsoft-Anmeldung herunter.
5. Danach **Offline starten** klicken. Der Launcher prüft die lokalen Dateien
   und startet ohne Microsoft-Anmeldung oder Netzaufruf des Launchers.

Lokale Profile haben eine feste lokale UUID und eigene Welten unter
`instances/local/<Spielername>/<Version>/`. Gleicher Name bedeutet gleiche lokale
Identität; eine Namensänderung öffnet einen anderen Spielordner. Das lokale Profil
ist kein Microsoft-Konto und keine gültige Anmeldung für kontogeprüfte Server
oder Realms. Auch Abmelden vom Microsoft-Konto entfernt das lokale Profil nicht.

Die Minecraft-Anwendung selbst kann eigene Netzwerkversuche unternehmen; alte
Versionen kontaktieren beispielsweise historische Ressourcenserver. Der Offline-
Schalter steuert die Netzaufrufe des Launchers.

## Microsoft-Anmeldung und der Browserknopf

Der Online-Modus erfordert weiterhin ein echtes Microsoft-Konto mit Java-
Berechtigung und eine eigene für die Minecraft-API freigegebene Microsoft-App-ID.
Diese App-ID ist nicht enthalten. **Ohne App-ID kann kein gültiger OAuth-Login
für diesen Launcher gestartet werden.** Die Kontoseite erklärt den fehlenden
Einrichtungsschritt und bietet den lokalen Spielmodus an.

Mit gültiger hinterlegter App-ID startet „Mit Microsoft anmelden“ den Browserlogin. Ein noch
nicht gespeicherter gültiger Wert in den Einstellungen wird vorher übernommen.
Ein Klick im Offline-Modus schaltet zur Online-Anmeldung um. Scheitert Pythons
Browseröffnung, versucht Blockwerk zusätzlich den Browserhandler des Systems.
Während der Anmeldung lässt sich der Browser erneut öffnen oder der kurzlebige
Anmeldelink kopieren. Die Kontowahl wird bei Microsoft angezeigt. Die Anmeldung
kann während des Wartens und zwischen den Microsoft-/Xbox-Schritten abgebrochen
werden. Fehlermeldungen werden ohne rohe Token-/Serverantworten angezeigt.
Es werden keine Konten oder erfolgreiche Anmeldungen vorgetäuscht.

Die externe App-Freigabe wird nicht durch die Browserkorrektur ersetzt.
Einrichtung und Voraussetzungen: [EINRICHTUNG.md](EINRICHTUNG.md).

## Downloads und Plattformen

- Windows: portable App, gesamtes ZIP entpacken und `Blockwerk.exe` starten.
- Linux: Quellpaket, Python 3.12 installieren, `sh start-linux.sh` ausführen.
- macOS: Quellpaket, Python 3.12 installieren, `sh start-macos.command` ausführen.

Linux/macOS sind hier nicht nativ gebaut oder ausgeführt worden. Details zu
Systembibliotheken, nativen Builds und der vorbereiteten CI-Matrix stehen in
[PLATTFORMEN.md](PLATTFORMEN.md). Beim ersten Skriptstart wird `.venv` eingerichtet;
spätere Starts benötigen keinen pip-Aufruf.

Die Versionsliste enthält offizielle Releases ab 1.0 und eine getrennte Snapshot-
Auswahl. Alpha/Beta bleiben ausgeblendet. Die Auswahl garantiert keine Lauffähigkeit
jeder Version auf jeder Hardware. Bedrock ist nicht enthalten. Mod-Profile werden
separat verwaltet.

## Entwicklung und Tests

```sh
python -m pip install -r requirements-build.txt
python -m unittest discover -s tests -v
python tests/integration_releases.py
python tests/integration_snapshots.py
python tests/integration_install.py
# Optional: große Downloads und echte Installation von vier Loadern:
python tests/integration_loaders.py
python tools/build.py
```

Das Build-Skript läuft auf dem jeweiligen Zielsystem und erstellt ein natives
Paket unter `dist/`. Die vorbereitete GitHub-Actions-Datei wurde nicht extern
ausgeführt. Die Integrationsprüfung lädt echte Spieldateien, fängt den Spielstart
jedoch ab. Die separat lokal durchgeführte Prozessprüfung und ihre Grenzen stehen
in [PRUEFBERICHT.md](PRUEFBERICHT.md).

## Dateien

Windows: `%LOCALAPPDATA%/Blockwerk`; macOS: `~/Library/Application Support/Blockwerk`;
Linux: `$XDG_DATA_HOME/blockwerk` bzw. `~/.local/share/blockwerk`.
`BLOCKWERK_DATA_DIR` überschreibt den Datenordner. Unter `minecraft/` liegen die
gemeinsamen Spieldateien, unter `prepared/` lokale Prüfsummen. Online-Spielordner
liegen unter `instances/<Version>/`, lokale Profile unter `instances/local/`.

Online-Refresh-Tokens verwenden Windows DPAPI, macOS Keychain bzw. Linux Secret
Service. Wenn sicherer Speicher nicht verfügbar ist, bleibt die Microsoft-Sitzung
nur im Arbeitsspeicher. Das lokale Offline-Profil braucht keinen Token.
Vor Änderungen oder Versionswechseln vorhandene Welten sichern.

Unabhängiges Projekt, nicht von Mojang/Microsoft entwickelt oder unterstützt.
Minecraft wird nicht mitgeliefert. Eigener Code: MIT; Fremdlizenzen: THIRD_PARTY.md.
