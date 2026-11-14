# Aktueller Stand 0.9.1

Die eigene Blockwerk-App ist registriert; ihre öffentliche Client-ID wird
mitgeliefert. Minecraft-API-Freigabe und echter Login bleiben offen.
Details und bewusste Entscheidung zum lokalen Modus: AUTH-STATUS.md.
Die folgenden Registrierungsschritte sind eine allgemeine Anleitung.

# Online-Anmeldung einrichten (optional für lokalen Offline-Modus)

## Was für den Online-Modus benötigt wird

1. Ein unterstütztes System mit Internetzugang; Details in PLATTFORMEN.md.
2. Ein persönliches Microsoft-Konto mit gültiger Minecraft-Java-Berechtigung.
3. Eine eigene Microsoft-App-Registrierung, deren Client-ID für die Minecraft-API
   freigegeben ist. Diese Freigabe gehört zum Launcher-Projekt, nicht zum Kauf
   des Spiels. **Die App-ID ist registriert, ihre Minecraft-Freigabe ist nicht bestätigt.**

Das Projekt implementiert den echten Anmelde- und Startablauf. Ohne Punkt 3 kann
der Microsoft-/Minecraft-Login nicht vollständig abgeschlossen werden.

## Microsoft-Konto erstellen

Im Launcher auf „Microsoft-Konto erstellen“ klicken oder
[Microsofts Registrierung](https://signup.live.com/) öffnen. Microsoft legt
fest, welche Angaben, Bestätigungen und Sicherheitsprüfungen erforderlich sind.
Ein neu erstelltes Konto enthält nicht automatisch eine Minecraft-Lizenz.
Passwörter und Bestätigungscodes ausschließlich auf Microsofts Website eingeben.

Für Minecraft zuerst dasselbe Konto im
[offiziellen Launcher](https://www.minecraft.net/download) verwenden und prüfen,
ob Minecraft Java spielbar ist. Falls nötig dort ein Java-/Xbox-Profil einrichten.

## Einmalige Einrichtung für den Projektbetreiber

### 1. Eine Desktop-App registrieren

Im [Microsoft-Entra-Portal](https://entra.microsoft.com/) die App-Registrierungen
öffnen und eine neue Registrierung erstellen. Dafür wird ein Konto mit den
entsprechenden Registrierungsrechten benötigt.

- Name: zum Beispiel „Blockwerk“.
- Unterstützte Kontotypen: persönliche Microsoft-Konten. Falls diese Auswahl
  in deiner Organisation eingeschränkt ist, müssen die Registrierungsrechte
  zunächst durch den zuständigen Administrator geklärt werden.
- Plattform: **Mobile und Desktopanwendungen / Public client (native)**.
- Benutzerdefinierte Redirect-URI exakt eintragen:

```text
http://localhost:29147/callback
```

Die Desktop-Rückleitung muss korrekt registriert sein. Zusätzliche Gerätecode-
oder Passwort-Flows sind für den verwendeten Authorization-Code-Ablauf mit PKCE
nicht erforderlich und wurden hier nicht zusätzlich aktiviert.
Die **Application (client) ID** von der Übersichtsseite kopieren.
Kein Client-Secret erstellen oder im Launcher hinterlegen. Die Desktop-App
verwendet Authorization Code mit PKCE und `XboxLive.signin offline_access`.
Die App-ID ist öffentlich; sie ist kein Passwort und keine E-Mail-Adresse.

Microsoft beschreibt die
[Desktop-Konfiguration](https://learn.microsoft.com/en-us/entra/identity-platform/scenario-desktop-app-registration)
und die [Regeln für lokale Redirect-URIs](https://learn.microsoft.com/en-us/entra/identity-platform/reply-url).
Der Port 29147 wird nur während der Anmeldung auf 127.0.0.1 geöffnet; kein
Zugriff aus dem Netzwerk ist dafür nötig. Ist der Port belegt, die andere
Anmeldung schließen und erneut versuchen.

### 2. Minecraft-API-Freigabe beantragen

Die [Dokumentation der verwendeten Launcher-Bibliothek](https://minecraft-launcher-lib.readthedocs.io/en/stable/tutorial/microsoft_login.html)
verweist auf die zusätzliche Freigabe für neue App-IDs. Über den dort verlinkten
offiziellen Antragsweg beziehungsweise
[Minecraft App-ID Review](https://aka.ms/mce-reviewappid) die eigene Client-ID
zur Prüfung einreichen. Voraussetzungen und Verfügbarkeit legt Microsoft/Mojang
fest; eine Registrierung allein garantiert keine Genehmigung. Falls der
Antragsweg geändert wurde, den aktuellen Verweisen in der Bibliotheksdokumentation
oder dem Minecraft-Support folgen.

Ohne Freigabe können Microsoft- und Xbox-Schritte funktionieren und der letzte
Minecraft-Schritt trotzdem mit HTTP 403 bzw. „Invalid app registration“ scheitern.
Eine andere Redirect-URI oder ein anderer Minecraft-Account behebt eine fehlende
App-Freigabe nicht. Es wird keine fremde Launcher-App-ID als Ersatz verwendet.

### 3. App-ID in Blockwerk eintragen

1. `Blockwerk.exe` öffnen.
2. Einstellungen → Einrichtung für Projektbetreiber aufklappen.
3. Die freigegebene App-ID einfügen und Einstellungen speichern.
4. „Microsoft-Konto“ öffnen und „Mit Microsoft anmelden“ anklicken.
5. Im Browser bei Microsoft anmelden und die Berechtigungen für deine App prüfen.
6. Nach der Rückkehr werden Xbox, Minecraft-Profil und Lizenz geprüft. Erst
   danach erscheint der Profilname. „Weiter zum Online-Spielen“ anklicken.

Eine erfolgreiche Anmeldung zeigt den echten Minecraft-Profilnamen.
Nach Ablauf von fünf Minuten lässt sich die Browseranmeldung erneut starten.

### 4. Für Spieler vorkonfigurierte Pakete bauen

Die öffentliche eigene Client-ID kann vor dem Bauen in der Projektdatei
`launcher-auth.json` gesetzt werden:

```json
{"schema": 1, "client_id": "HIER-DIE-EIGENE-FREIGEGEBENE-CLIENT-ID"}
```

Der Beispieltext ist kein gültiger Wert. Tatsächlich muss dort die eigene
UUID stehen. In 0.9.1 ist die eigene registrierte App-ID hinterlegt; ihre Freigabe bleibt offen. Das Build-Skript
nimmt die Datei in Windows-/Linux-/macOS-Pakete auf. Bei neuen Benutzerprofilen
wird die Kennung automatisch übernommen. Eine ausdrücklich gespeicherte lokale
Kennung hat Vorrang. Die Datei enthält niemals Client-Secrets oder Kontotokens.

Eine syntaktisch richtige ID belegt keine Minecraft-Freigabe. Diese muss der
Projektbetreiber über den oben verlinkten Antragsweg beantragen und erhalten.
Der lokale Befehl `python main.py --check-auth auth-status.json` meldet lediglich
die vorhandene Konfiguration, ausdrücklich keine bestätigte Freigabe.

## Versionen und Welten

Unter „Versionen“ zwischen Vollversionen ab 1.0 und Snapshots umschalten.
Die Snapshot-Liste umfasst auch offiziell dort geführte Pre-Releases/Release Candidates.
Eine Zeile auswählen und „Diese Version auswählen“ klicken. Danach
auf der Spielen-Seite „Minecraft starten“ verwenden. Downloads und das passende
Java erfolgen bei Bedarf automatisch. „Vorhanden“ bedeutet, dass die Client-JAR
existiert; die vollständige Installationsprüfung erfolgt beim Start.

Jede Version verwendet ihren eigenen Ordner unter
`instances` im jeweiligen Blockwerk-Datenordner (siehe README.md). Bestehende Welten können nach einer
Sicherung bei geschlossenem Spiel in den jeweiligen `saves`-Unterordner kopiert
werden. Neuere Welten nicht mit einer älteren Minecraft-Version öffnen.

## Häufige Probleme

| Anzeige / Problem | Nächster Schritt |
| --- | --- |
| Einrichtung ausstehend | Der Projektbetreiber muss Blockwerk registrieren und die Minecraft-Freigabe erhalten. |
| Minecraft-API-Freigabe fehlt / 403 | Freigabestatus der App-ID bei Minecraft prüfen. |
| Konto hat kein Java-Profil | Im offiziellen Launcher Konto, Lizenz und Profil prüfen. |
| Xbox-Anmeldung abgelehnt | Xbox-Profil, Region und Microsoft-Familieneinstellungen prüfen. |
| Anmeldung abgelaufen | In Blockwerk abmelden und erneut bei Microsoft anmelden. |
| Nur für diese Sitzung | Windows DPAPI ist in diesem Profil nicht verfügbar; beim nächsten Appstart erneut anmelden. |
| Versionsliste leer | Internet prüfen, unter Versionen auf Aktualisieren klicken. |
| Alte Version startet nicht | Grafiktreiber und kompatibles Java prüfen; ggf. Java-Datei unter Einstellungen wählen. |
| Download abgebrochen | Erneut starten; vorhandene Downloads werden geprüft und fehlende Teile nachgeladen. |
| Minecraft endet mit Fehlercode | Spielordner öffnen und `logs/latest.log` bzw. `crash-reports` ansehen, sofern die Version sie erzeugt hat. |

Ein eigener Java-Pfad gilt für alle Versionen. Das Feld leeren, um wieder die
automatische Auswahl zu nutzen. RAM an den vorhandenen Arbeitsspeicher anpassen.

## Frühere Prüfungen der Ausgabe 0.1

Am 25. Oktober 2026 wurden die Kernlogik, der lokale OAuth-Callback mit PKCE,
Lizenzsperren, die sichere Sitzung ohne Klartextdatei, echte Mojang-Metadaten
und ein historischer Originaldownload geprüft. Eine vollwertige Microsoft-
Anmeldung und eine spielbare Minecraft-Sitzung wurden mangels freigegebener
App-ID und angemeldetem berechtigtem Konto nicht durchgeführt.

Die native DPAPI-Rundreise kann in der eingeschränkten Build-Umgebung nicht
ausgeführt werden. Der getestete Ersatz hält die Anmeldung ausschließlich im
Arbeitsspeicher. Der Windows-Build und die Qt-Oberfläche werden separat geprüft.




## Aktuell in 0.5: Kontoseite und lokale Profile

Für ein lokales Offline-Profil ist keine dieser Microsoft-Einrichtungen nötig.
Im Launcher Offline · Einzelspieler wählen, Namen eingeben, die gewünschte Version
auswählen und bei Bedarf mit Internet „Spieldateien herunterladen“ anklicken.
Danach offline starten. Lokale Profile haben eigene Welten und können sich nicht
auf kontogeprüften Online-Servern oder Realms anmelden.

Ohne App-Kennung zeigt die Kontoseite „Einrichtung ausstehend“. Mit eingerichteter
Kennung beginnt der Browserlogin. „Browser erneut öffnen“ und „Anmeldelink kopieren“
stehen nur während der Browserphase zur Verfügung. Abbrechen verwirft die laufende
Anmeldung; danach lässt sich ein neuer Versuch starten. Der Browser-Callback allein
ist noch kein erfolgreicher Minecraft-Login: Profil und Lizenz werden danach geprüft.
