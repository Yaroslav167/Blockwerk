# Microsoft-Konfiguration · Blockwerk 0.9.1

14. November 2026: Registrierung und Desktop-Redirect im Azure-Portal
sichtbar bestätigt. Öffentliche eigene Client-ID eingebunden. 124 Tests
ausgeführt: 123 bestanden, ein POSIX-Test übersprungen. Der Kontomodus ohne
Anmeldung bleibt unverändert. Kein Minecraft-Freigabeantrag abgeschickt;
keine echte Minecraft-Anmeldung nachgewiesen. Details: AUTH-STATUS.md.

Historischer Prüfstand:

# Plattform-Überarbeitung 0.9.0 · 14. November 2026

122 Tests auf Windows: 121 bestanden, ein POSIX-Test übersprungen.
Geprüft: Quellupdates aus ZIP/Tar, Inventar und Prüfsummen, Erhalt persönlicher
Daten und Konfiguration, Sicherung, Rücksetzen bei Neustartfehler, Abbruch,
Archiv-Traversal und Links, Ablehnung veränderter Quellen, Architektur-Fingerprints
und simulierte Bootstrap-Starts ohne erneutes pip. Kein natives Linux/macOS
verfügbar; WSL ist nicht installiert. CI ist vorbereitet, nicht extern ausgeführt.
Details und verbleibende Spieltests: PLATTFORMEN.md.

Frühere Prüfungen:

# Prüfbericht · Blockwerk 0.9.0

Stand: 14. November 2026. Windows x64.

**112 Tests bestanden.** Neue Sprachtests prüfen Englisch auf allen zehn Seiten
bei Mindestfenstergröße, Deutsch/Englisch-Umschalten mit gespeicherter Auswahl,
Erhalt eigener Spieler- und Servernamen, Seitenwechsel, stabile interne
Versionskategorien für Releases/Snapshots, Sprachsperre bei laufenden Aufgaben
und Rückfall auf Deutsch bei ungültiger gespeicherter Sprache. Die übrigen
Server-, Skin-, Update-, Welt-, Mod- und Anmeldetests bleiben enthalten.

Die Übersetzungen werden lokal mitgeliefert. Für den Sprachwechsel ist weder
ein Internetdienst noch eine neue Anmeldung nötig. Die Oberfläche wird neu
aufgebaut; laufende Downloads/Spiele verhindern den Wechsel. Die Sprache von
Minecraft selbst und von fremden Installern wird nicht umgestellt.

Die native Windows-EXE 0.9.0 wurde mit getrennten Testdatenordnern jeweils auf
Deutsch und Englisch gestartet. Beide Aufnahmen wurden mit dem nativen
Windows-Qt-Plugin erstellt, visuell geprüft und mit Exitcode 0 beendet. Die
Sprachauswahl ist oben rechts sichtbar. Keine echten Konten oder Welten wurden
für diese Prüfung geöffnet. Linux/macOS wurden weiterhin nicht nativ getestet.

Die folgenden Abschnitte dokumentieren frühere Versionen.

# Prüfbericht · Blockwerk 0.8.0

Stand: 14. November 2026, Windows x64.

**107 Tests bestanden.** Der Offline-Start erlaubt Mehrspieler und Chat ohne
Microsoft-Kontoabfrage. Zwei statt drei Spielmodi, unbegrenzte Favoriten (30 im
Persistenztest), Speicherung nach Neustart, Einträge aus Minecraft mit Emoji und
Serverbild, Erhalt unbekannter Tags und der Reihenfolge, Ingame-Löschungen,
Sicherung und Übernahme alter Serverlisten sind geprüft. Mod-Profile verwenden
jetzt ebenfalls den normalen lokalen Spielordner. Alte Community-Einstellungen
werden auf Offline migriert. Kein öffentlicher Serverbeitritt wurde getestet;
Serverregeln und Versions-/Mod-Kompatibilität gelten weiterhin.

Die native Windows-EXE 0.8.0 startete auf Spielen- und Server-Seite jeweils mit
Exitcode 0. Eine isolierte Testliste mit zwölf Favoriten wurde dargestellt;
Hinzufügen blieb verfügbar. Die Aufnahmen wurden visuell geprüft. Diese
Testadressen wurden nicht kontaktiert. Das neue Paket liegt neben den früheren
Ausgaben in `Blockwerk-Windows-0.8.0`; bestehende geöffnete Apps bleiben erhalten.

Die folgenden Abschnitte dokumentieren frühere Versionen und deren damalige
Prüfungen. Das dort beschriebene Fünferlimit gilt ab 0.8 nicht mehr.

# Prüfbericht · Blockwerk 0.7.0

Stand: 29. Oktober 2026. Windows x64, Python 3.12.14, Qt/PySide 6.12.0,
minecraft-launcher-lib 8.0, Keyring 25.7.0, PyInstaller 6.22.3.

## Automatische Prüfungen

**101 Tests ausgeführt: alle bestanden.** Isolierte Testdaten, simulierte
Online-Konten und ein nativer Windows-DPAPI-Rundreisetest. Die bisherigen 83
Tests aus 0.6 sind enthalten. Zehn UI-Seiten wurden bei der Mindestgröße
1040 × 780 gerendert.

## Skins und Updates in 0.7

- Drei originale Starter-Skins, persistente Auswahl und Classic/Slim, PNG-Import
  ohne Veränderung, Duplikaterkennung und alte 64 × 32-Skins geprüft.
  Ungültige Dateitypen und übergroße Bilddimensionen werden vor dem Dekodieren
  abgelehnt. Auswählen und Importieren lösen keinen Konto-Upload aus.
- Der ausdrückliche Konto-Upload ist mit simulierter Token-Erneuerung,
  Java-Berechtigung und Multipart-Anfrage geprüft. **Kein echter Online-Upload:**
  eine freigegebene Microsoft-App-ID und ein berechtigtes Testkonto fehlen.
- Lokales Skinpaket liest tatsächliche Client-Metadaten, erhält andere
  Ressourcenpakete und sichert eine vorhandene `options.txt`. Beschädigte
  Ressourcenpaket-Einstellungen werden vor dem Überschreiben abgelehnt.
- Echte Minecraft-1.20.1-Dateien: Ressourcenformat 15, 18 Standardtexturen.
  Mit aktiviertem Skinpaket wurde ein ausschließlich für Tests vorhandener
  Welt-Spielstand gestartet. Das echte Spielprotokoll bestätigte das Laden von
  `file/blockwerk-local-skin.zip` und den Weltbeitritt; der Prozess lief bis zum
  gezielten Testende. Keine Pack-/Textur-Ladefehler in diesem Test. Die konkrete
  Spielerfigur wurde nicht per Bildschirmaufnahme verifiziert.
- Zusätzlich wurde aus dem echten installierten 26.3-JAR das Ressourcenformat
  97.1 gelesen und ein entsprechendes Paket ausschließlich im Testordner erzeugt.
  Das ist eine Metadatenprüfung, kein Spieltest von 26.3.
- Wochenintervall, gespeicherter Ausschalter, einstündiger Fehler-Retry,
  kein Downgrade, HTTPS-Anforderungen, Dateigröße, SHA256 und Abbruchbereinigung
  geprüft. Manipulierte Pakete ersetzen keinen vorhandenen geprüften Download.
- Windows-Staging und Ordnerwechsel mit isolierten Testpaketen geprüft:
  altes Paket bleibt erhalten, simulierte Fehler rollen zurück, externe
  Spielstände bleiben unverändert. Unsichere Archivpfade und gemischte
  App-Ordner werden abgelehnt. Die UI blockiert Installation während einer
  laufenden Aufgabe; die Wochenprüfung lädt keinen Minecraft-Katalog neu.
- Updatepakete werden erst nach ausdrücklichem Klick installiert. Geprüft wird
  nur während der Nutzung bzw. beim nächsten Öffnen nach sieben Tagen. Der
  lokale Kanal benötigt eine neu veröffentlichte Launcher-Ausgabe; es wurde
  kein öffentlicher Updatehost eingerichtet. Quellpakete bleiben manuell.
- Die gebaute Windows-EXE 0.7.0 startete auf Skins- und Updates-Seite mit dem
  nativen Windows-Qt-Plugin, erzeugte beide Prüfscreenshots und beendete sich
  jeweils mit Exitcode 0. Eigene frische Test-Datenordner wurden verwendet.
- Der gebaute eigenständige `BlockwerkUpdater.exe` bestand seinen nativen
  Selbsttest mit Exitcode 0: isolierter Ordnerwechsel, neue Dateiinhalte und
  Erhalt der vorherigen App verifiziert. Beim Selbsttest wurde keine echte
  Benutzer-App ersetzt oder neu gestartet. Das ist kein Ende-zu-Ende-Test
  eines zukünftigen veröffentlichten Releasewechsels mit laufendem Spiel.

Die fertige portable Ausgabe liegt diesmal in `Blockwerk-Windows-0.7.0`, weil
die vorherige Ausgabe im Ordner `Blockwerk-Windows` während des Baus geöffnet
war. Das neue Windows-ZIP enthält wie üblich den Paketordner `Blockwerk-Windows`.

Die folgenden Abschnitte dokumentieren frühere Prüfungen mit ihrem damaligen
Versionsstand; umfassende Mod-, Plattform- oder Online-Kompatibilität folgt daraus
nicht.

## Welten und Snapshots in 0.6

- Welt-Erkennung in normalen Minecraft-Spielständen und allen Blockwerk-
  Instanzen: Online, lokale Spieler, Community, Mod-Profile und zusätzliche
  Quellen. Doppelte Suchquellen werden anhand des tatsächlichen Pfads dedupliziert.
- Begrenztes Lesen gzip-komprimierter NBT-Metadaten mit Weltname, Version,
  Snapshot-Kennung, Spielmodus und Spielzeit. Beschädigte und übergroße Daten
  werden als unlesbar markiert, ohne andere Welten auszublenden.
- Spielkopien mit Erhalt des Originals, Wiederverwendung vorhandener Kopien,
  Versionskopie innerhalb derselben Instanz, Abbruchbereinigung, Sitzungssperren
  und Verbot eines rekursiven Zielordners geprüft.
- Welt-Schaltfläche ordnet ursprünglichen lokalen Spieler und Version zu.
  Neue Welt verwendet das ausgewählte Spielprofil und erzeugt keine fingierte
  `level.dat`; die vollständige Erstellung erfolgt im echten Minecraft-Dialog.
- Kategorie Vollversionen/Snapshots auf Spielen- und Versionen-Seite synchron,
  gespeicherte Auswahl, Offline-Katalog mit Snapshots und Prüfung zulässiger
  Snapshot-IDs. Alpha/Beta bleiben ausgeschlossen.
- Vorhandene reale Daten schreibgeschützt geprüft: **9 Java-Welten gefunden,
  alle 9 Metadaten lesbar**. Native Übersicht mit diesen echten Einträgen und
  die minimale Fenstergröße wurden aufgenommen und visuell geprüft.
- Alle aktuell angebotenen **103 Vollversions- und 756 Snapshot-Manifeste**
  über Mojangs öffentliche Server geladen, Prüfsummen und echte Startargumente
  geprüft. Keine ungelösten Argument-Platzhalter. Das ersetzt keinen Spieltest
  aller 859 Versionen auf jeder Hardware.

### Echter Weltbeitritt in Vollversion und Snapshot

Eine geschlossene vorhandene 1.20.1-Welt mit 23 Dateien / 18.692.028 Bytes wurde
ausschließlich gelesen und zweimal in separate Test-Spielordner kopiert.
Minecraft 1.20.1 und Snapshot 23w31a wurden mit Originaldateien und Mojang-Java
installiert/vorbereitet. Beide wirklichen Spielprozesse erhielten native
`--quickPlaySingleplayer`-Argumente. Die jeweiligen Spielprotokolle bestätigten
den Beitritt zur Welt (`joined the game` / Anmeldung mit Entity-ID).

Beide Prozesse liefen bis zum gezielten Testende. Die SHA256-Prüfsummen aller
23 Originaldateien wurden vorher und nach jedem Test verglichen: **unverändert**.
Kein Original-Spielstand wurde gestartet. Nur die eigenen Testkopien wurden
durch Minecraft geladen und konvertiert. Während der Offline-Startbefehlsprüfung
waren Launcher-Netzaufrufe ausdrücklich gesperrt.

Ältere Versionen ohne Quick Play erhalten keine unbekannten Weltstart-Argumente;
der Zugriff erfolgt über das echte Einzelspielermenü im richtigen Spielordner.
Eine vollständige interaktive Neuerstellung mit allen Welt-Einstellungen wurde
nicht automatisiert durchgeklickt. Langzeittests jeder Welt, aller Mods und
Versionswechselkombinationen sowie Multiplayer-Verbindungen sind nicht bestätigt.

## Neue Microsoft-Kontoseite und Anmeldeprüfung in 0.5

- Ohne App-Kennung öffnet sich die Kontoseite mit „Einrichtung ausstehend“.
  Es wird kein Browserlogin vorgetäuscht; die technische Betreiber-Einrichtung
  ist in den Einstellungen zunächst eingeklappt.
- Eine gültige eigene öffentliche Kennung kann über `launcher-auth.json`
  vorkonfiguriert werden. Ungültige Konfiguration wird zurückgewiesen.
  Eine vorhandene Kennung wird niemals als nachgewiesene Minecraft-Freigabe
  dargestellt. Der echte Freigabestatus bleibt ohne Login unbekannt.
- Tatsächlicher lokaler HTTP-Rückkanal mit Microsoft-Endpunkten als Test-Mocks:
  PKCE, zufälliger State, persönliche Microsoft-Konten, explizite Kontowahl,
  keine Client-Secrets und Weitergabe des PKCE-Verifiers geprüft.
- Getrennte Microsoft-/Xbox-/Minecraft-Austauschschritte mit simulierten
  Antworten geprüft. Abbruch nach einer Netzantwort verhindert den nächsten
  Schritt und die Kontospeicherung. Abgelaufene Codes werden verständlich
  erklärt; rohe OAuth-Antworten und Tokens erscheinen nicht im Fehlertext.
- Der Callback meldet nur den Empfang der Microsoft-Antwort. Der echte
  Minecraft-Profilname wird erst nach Profil-/Lizenzprüfung und Speicherung
  an die Oberfläche übergeben. Die Rückleitungsseite hat `no-store` und
  `no-referrer`; Auth-Codes werden dort nicht ausgegeben.
- Browser erneut öffnen, Anmeldelink kopieren, Abbrechen, Fehleranzeige mit
  erneutem Versuch, Kontowechsel, Abmelden und Rückkehr zum Online-Spielen
  in der Qt-Oberfläche geprüft. Fehlgeschlagene Logins bleiben als Hinweis
  auf der Kontoseite, ohne irreführende Erfolgsanzeige.
- Alle acht Seiten werden gerendert. Native Windows-Aufnahmen der echten
  leeren Konfiguration und der minimalen Fenstergröße visuell geprüft.
  Weitere Warte-/Fehler-/Erfolgszustände verwendeten ausdrücklich Testdaten;
  daraus folgt kein erfolgreicher externer Microsoft-Login.

**Externe Voraussetzung fehlt weiterhin:** Der Benutzer hat bestätigt, dass
keine eigene App-ID vorliegt. Diese Ausgabe enthält deshalb eine leere
`launcher-auth.json`. Es wurde keine Microsoft-App registriert und kein
Freigabeantrag im Namen des Benutzers eingereicht. Ohne Registrierung und
Minecraft-Freigabe ist die echte Online-Anmeldung noch nicht betriebsbereit.

## Neue Animation in 0.4.1

- Native Windows-Qt-Oberfläche mit der echten Startseite aufgenommen, auch bei
  der minimalen Fenstergröße. Texte und Pause-Schaltfläche bleiben bedienbar.
- 60 aufeinanderfolgende Frames aufgenommen: die Animationszeit entwickelte
  sich um 6,2 Sekunden weiter; erster und letzter Frame unterscheiden sich.
- Die detaillierte Landschaft wurde während dieser Frames aus demselben Cache
  wiederverwendet. Die reguläre Timer-Vorgabe ist 33 ms (etwa 30 Bilder/s).
- Pausieren friert die Animationszeit ein; Fortsetzen startet den Timer wieder.
- Verlassen der Spielen-Seite und Minimieren stoppen den Timer; Rückkehr und
  Wiederherstellen setzen ihn fort. Schließen stoppt den Timer ebenfalls.
- Alle Elemente entstehen lokal durch Qt-Zeichenbefehle. Keine Video-, Textur-
  oder Netzwerkabhängigkeit wurde für die Animation hinzugefügt.

## Bestehende Funktionsprüfungen

- Vier Mod-Metadatenformate, Versionsregeln, Zurückweisen bekannter falscher
  Loader-/Minecraft-Kombinationen, unbekannte Regeln als manuell zu prüfen.
- Getrennte Mod-Profile, geerbte Minecraft-Startprofile, ausgewählte Loader-
  Version und Java, echtes Fabric-Profil-API ohne Java-Installer.
- Mod-Import, Aktivieren/Deaktivieren, Großschreibung der JAR-Endung und
  Übernahme aktiver Dateien in den richtigen Spielordner.
- Maximal fünf gespeicherte Server, Zurückweisen des sechsten, Duplikate,
  Entfernen, Ersetzen, erneutes Laden, IPv6 und Adressvalidierung.
- Native NBT-Serverliste unabhängig eingelesen; Java-UTF-Kodierung für Emoji.
- Dritter Modus ohne Microsoft-Konto und ohne Launcher-Netzaufrufe beim Start,
  eigene Community-Instanz und aktiviertes Mehrspielermenü.
- Offline-Dateiprüfung einschließlich geerbter Basisprofile. Veränderliche
  Java-Installer-Marker machen vorbereitete Profile nicht mehr ungültig.
- Bisherige Prüfungen für Kontospeicherung, PKCE/State, Browser-Fallback,
  Versionsfilter, sichere Pfade, Offline-Profil und Plattformverzeichnisse.
- Alle acht Launcher-Seiten mit Qt gerendert; native Windows-Vorschauen für
  Mods und Server visuell geprüft. Kleine Fenster verwenden Scrollbereiche.

## Echte Loader-Installationen und Java-Spielprozesse aus 0.4 vom 25. Oktober

| Loader | Minecraft | Loader-Version | Installation / Offline-Startargumente | Echter Prozess |
|---|---|---|---|---|
| Fabric | 1.20.1 | 0.20.1 | bestanden | 45 Sekunden, Grafik/Audio initialisiert |
| Forge | 1.20.1 | 47.4.28 | bestanden | 45 Sekunden, Grafik/Audio initialisiert |
| Quilt | 1.20.1 | 0.30.1 | bestanden | 45 Sekunden, Grafik/Audio initialisiert |
| NeoForge | 1.20.4 | 20.4.253 | bestanden | 45 Sekunden, Grafik/Audio initialisiert |

Installationen mit Originaldateien und Mojang-Java 17 in eigenen Testordnern.
Eine echte Fabric API 0.92.2+1.20.1 wurde vom offiziellen Fabric-Maven importiert,
in den Mod-Ordner kopiert und vom echten Fabric-Spielprozess geladen. Sein
Protokoll meldete 57 Mods einschließlich der API-Module.

Zusätzliche Prüfung der vorbereiteten Befehle mit abgefangenem Spielprozess:
keine offenen Argumentplatzhalter, vorhandene Mod-Datei und native Serverliste,
keine Netzaufrufe des Launchers oder Microsoft-Kontoabfrage beim lokalen Start.

Anschließend alle vier Java-Spielprozesse tatsächlich gestartet. Die Logs
bestätigten Loader, Render-Initialisierung, OpenAL und Texturatlanten. Die eigenen
Testprozesse liefen bis zum Ende der jeweils 45 Sekunden und wurden gezielt
beendet. Keine Benutzerwelten wurden geöffnet oder verändert.

Die Windows-Sandbox blockierte zunächst Java `toRealPath` bei Fabric/Quilt und
NeoForges Installer. Die gleichen Profile bestanden außerhalb der Sandbox;
Dateirechte und Java-Sicherheitsprüfungen wurden nicht abgeschwächt.

Lokale Spielidentitäten besitzen keinen gültigen Online-Token. Die echten Clients
meldeten deshalb unter anderem HTTP 401 für Konto-/Attributabfragen. Minecraft
selbst kann Netzwerkversuche unternehmen. Diese Meldungen belegen keinen Online-
Login. Der Launcher führt beim lokalen Start keine Kontoprüfung durch.

Bei diesen Loader-Prüfungen wurden eine spielbare Welt, ein visuell bestätigtes
Hauptmenü, ein konkreter Multiplayer-Server und beliebige weitere Modkombinationen
nicht geprüft. Die späteren echten Weltbeitritte in 0.6 sind oben getrennt beschrieben. Diese
Prozessprüfungen garantieren nicht, dass alle Mods zusammen funktionieren.
Andere JAR-/EXE-Installer haben einen manuellen Importweg; kein beliebiger
Fremdinstaller wurde als universell kompatibel getestet.

## Weiter geltende Prüfungen aus 0.2 und 0.3

Alle 103 damals angebotenen offiziellen Releases ab 1.0 anhand echter Metadaten
und Startargumente geprüft. Echte Minecraft-1.0-Installation mit Mojang-Java und
1.432 lokalen Dateien vorbereitet und ohne Launcher-Netz geprüft. Ein echter
1.0-Prozess initialisierte Audio; visuelles Gameplay wurde nicht bestätigt.
Das ist kein Spieltest aller Versionen auf jeder Hardware.

## Windows-Paket und andere Plattformen

Die gebaute Windows-EXE 0.6.0 startete mit dem nativen Windows-Qt-Plugin auf
Spielen- und Welten-Seite jeweils mit Exitcode 0. Die Weltübersicht des Pakets
las echte Spielstände aus dem normalen Minecraft-Ordner und erzeugte den
Prüfscreenshot. Alle Paketprüfungen nutzten neue eigene Konfigurationsordner.
Der echte HTTPS-Abruf durch die EXE bestand mit Exitcode 0 und ohne Cache-Fallback:
859 Katalogeinträge, davon 103 Vollversionen und 756 Snapshots.

Die neue Windows-EXE 0.5.0 startete mit Exitcode 0 sowohl auf der Spielen- als
auch auf der Microsoft-Kontoseite. Beide nativen Windows-Qt-Aufnahmen wurden
erzeugt. Die eingepackte `launcher-auth.json` wurde durch die EXE gelesen:
`--check-auth` meldete Version 0.5.0, `client_id_configured: false`,
`minecraft_app_permission: not_verified`, keinen Client-Secret-Bedarf und
keine Passwortabfrage durch den Launcher. Das ist eine Konfigurationsprüfung,
kein externer Login-Test. Alle Aufrufe verwendeten eigene neue Testordner.

Die neu gebaute Windows-EXE 0.4.1 startete mit dem nativen Windows-Qt-Plugin,
zeichnete die neue Blockszene samt Pause-Knopf und erstellte den Prüfscreenshot
mit Exitcode 0. Der Datenordner war ausschließlich ein neuer Testordner.
Die Animation wurde zusätzlich vor dem Paketbau über echte zeitlich versetzte
Qt-Frames und ihre Pause-/Fensterzustände geprüft, wie oben beschrieben.

Die Windows-EXE 0.4.0 hatte beide Paketprüfungen mit Exitcode 0 bestanden:
nativer Start mit dem Windows-Qt-Plugin und erzeugtem Screenshot sowie echter
HTTPS-Abruf des offiziellen Mojang-Katalogs (103 Releases, kein Cache-Fallback).
Die Tests verwendeten neue Datenordner; private Benutzereinstellungen wurden
nicht geladen. ZIP-Dateien werden vor Freigabe vollständig auf CRC-Integrität
geprüft, Unix-Startskripte in den Quellarchiven auf Ausführungsrechte. SHA256-
Prüfsummen liegen neben den Download-Dateien.

Linux/macOS-Code, Startskripte und native Build-Konfigurationen sind vorhanden,
aber hier nicht auf diesen Systemen ausgeführt. Die Pakete für Linux/macOS
enthalten Quellcode. Die vorbereitete CI wurde nicht extern gestartet.

Eine echte Microsoft-Anmeldung ist hier weiterhin nicht abschließend geprüft:
Es fehlt eine eigene freigegebene App-ID und ein angemeldetes berechtigtes
Testkonto. Die bestehende Benutzeranmeldung wurde nicht gelesen oder verändert.
Die ausgelieferte App enthält keine App-ID. Ihre Kontoseite erklärt die
ausstehende Betreiber-Einrichtung. Die lokalen Modi brauchen keine Microsoft-Anmeldung.

Der Kontospeicher unter Linux/macOS ist mit Mocks geprüft; der native Windows-
DPAPI-Test bestand für 0.4.1 außerhalb der Sandbox. Paket und EXE sind unsigniert.
Das Fünferlimit gilt für gespeicherte Launcher-Favoriten; weitere Ingame-Einträge
oder Direktverbindungen bestimmt der unveränderte Minecraft-Client.
