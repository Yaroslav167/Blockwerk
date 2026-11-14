Aktueller Microsoft-Status ab 0.9.1: Eigene Client-ID registriert und
vorkonfiguriert, Minecraft-API-Freigabe weiterhin offen. Siehe AUTH-STATUS.md.
Ältere Hinweise auf eine noch fehlende Registrierung sind überholt.

# Skins und Launcher-Updates · Blockwerk 0.7.0

## Skins auswählen und hinzufügen

Unter **Skins** einen der drei eigens für Blockwerk gezeichneten Skins auswählen
oder **Skin-PNGs hinzufügen** verwenden. Java-PNGs mit 64 × 64 oder 64 × 32 Pixeln
und bis zu 1 MB werden unterstützt. Die importierte PNG bleibt unverändert.
Die Vorschau lässt sich mit der Maus drehen; bei modernen Skins zwischen
Classic und Slim wählen. **PNG exportieren** speichert den ausgewählten Skin.

### Lokal spielen

Zuerst das gewünschte Spielprofil und die Minecraft-Version wählen und deren
Spieldateien installieren. Dann **Lokales Skinpaket anwenden** verwenden und das
Spiel starten. Das Ressourcenpaket ersetzt die Standardfiguren dieser Instanz.
Es ist nur auf diesem Computer sichtbar und kann auch andere Figuren ohne
eigenen Konto-Skin verändern. Die Armform folgt dem Standardmodell des Spiels.
Das ist kein echter, für andere Spieler sichtbarer Konto-Skin.

Das Paket benötigt eine installierte Version mit interner `version.json`,
gewöhnlich 1.14 oder neuer. Die Ressourcenpaket-Version und vorhandenen
Standardtexturen werden aus dem tatsächlichen Client-JAR gelesen. Andere
Ressourcenpakete bleiben ausgewählt. Die bisherige `options.txt` wird einmal
als `options.txt.blockwerk-before-skin` gesichert. Ein laufendes Spiel neu starten;
im Minecraft-Menü **Optionen → Ressourcenpakete** lässt sich das Paket deaktivieren.
Eine darüber liegende Skin-Mod oder ein anderes Ressourcenpaket kann es überlagern.

### Echter Konto-Skin

**Im Microsoft-Konto anwenden** lädt die PNG erst nach diesem ausdrücklichen
Klick ins angemeldete Minecraft-Java-Konto hoch. Auswählen oder Importieren allein
ändert kein Online-Konto. Dazu ist eine funktionierende Microsoft-Anmeldung mit
Java-Berechtigung nötig. Diese Ausgabe enthält weiterhin keine freigegebene
Microsoft-App-ID; der echte Konto-Upload konnte daher nicht mit einem realen
Konto getestet werden. Siehe `EINRICHTUNG.md`.

Als bereits nutzbare Alternative PNG exportieren und über **Offizielle
Skin-Profilseite öffnen** auf minecraft.net selbst hochladen.

## Wöchentliche Updates nur für den Launcher

Unter **Updates** ist die Prüfung alle sieben Tage voreingestellt. Sie läuft
beim Start oder während der Nutzung, sobald der Launcher frei ist. Ist die App
geschlossen, wird beim nächsten Öffnen geprüft. Eine fehlgeschlagene Prüfung
wird frühestens nach einer Stunde erneut versucht. **Jetzt prüfen** funktioniert
auch manuell. Die Wochenprüfung kann abgeschaltet werden.

Der Updater verändert weder Minecraft-Versionen noch Mods oder Welten und lädt
keinen Minecraft-Katalog automatisch neu. Ein neuer Launcher muss zunächst vom
Projektbetreiber veröffentlicht werden. Es entsteht nicht automatisch jede Woche
eine neue Softwareversion.

Das hier gebaute Windows-Paket verwendet den lokalen Ausgabeordner mit
`Blockwerk-Updates.json` als Kanal. Dieser Ordner muss erreichbar bleiben.
Auf einem anderen Computer unter **Lokalen Updateordner wählen** den Ordner mit
Feed und Paketen angeben. Optional ist eine eigene HTTPS-Feedadresse möglich.
Es wurde keine öffentliche Update-Webseite eingerichtet.

**Updatepaket herunterladen** prüft Dateigröße und SHA256. Danach installiert
**Installieren & Launcher neu starten** das Windows-Paket. Der getrennte Helfer
wartet auf das Beenden des Launchers, tauscht dessen Ordner aus und startet die
neue App. Der vorherige App-Ordner bleibt als `.Blockwerk-backup-…` daneben
erhalten. Bei einem fehlgeschlagenen Ordnerwechsel wird zurückgerollt.
Während des Spielens wird keine Installation ausgelöst.

Die App muss in ihrem eigenen vollständig entpackten Ordner liegen. Fremde
Dateien im App-Ordner oder darin liegende Spieldaten verhindern den automatischen
Austausch; in diesem Fall manuell in einen neuen Ordner entpacken. Standardmäßig
liegen persönliche Daten außerhalb der App im Benutzer-Datenordner.
Die überarbeiteten Linux-/macOS-Quellpakete unterstützen jetzt einen eigenen
Python-Helfer zur Installation mit Inventar und Dateisicherung. Selbst gebaute
native Linux-/macOS-Apps bleiben manuelle Installationen. Siehe PLATTFORMEN.md.

## Neue Ausgabe veröffentlichen

1. Versionsnummer in `blockwerk/core.py` und `blockwerk/__init__.py` erhöhen,
   Änderungen prüfen und Tests ausführen.
2. In einen sauberen Ausgabeordner bauen:
   `python tools/build.py`. Optional bestimmt `BLOCKWERK_LOCAL_UPDATE_FEED`
   den beim Bau eingebetteten absoluten Pfad der lokalen Feeddatei.
3. `python tools/package_release.py --output-dir PFAD` erzeugt Archive,
   Feed und Prüfsummen. `PFAD` enthält `Blockwerk-Windows` und den Quellordner
   `Blockwerk-Projekt`. Während des Paketbaus den Feed nicht prüfen lassen.
4. Den fertigen Feed zusammen mit den fertigen Archiven in den gewählten
   Kanalordner übernehmen. Für einen eigenen Webkanal kann anschließend
   `python tools/create_update_feed.py --output-dir PFAD --base-url https://…`
   einen HTTPS-Feed erzeugen. Diese Werkzeuge laden nichts ins Internet hoch.

Nur einen selbst kontrollierten Updatekanal verwenden. Die Prüfsumme erkennt
beschädigte oder gegenüber dem Feed veränderte Pakete; diese Ausgabe ist nicht
codesigniert und verwendet keine zusätzliche Herausgeber-Signatur des Feeds.
