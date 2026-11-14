# Mods, Installer und Offline-Server · Blockwerk 0.8

## Forge, Fabric, Quilt und NeoForge

1. „Mods & Loader“ öffnen. Einen Profilnamen eingeben.
2. Die Minecraft-Version und den passenden Loader auswählen.
3. „Versionen laden“ anklicken und eine Loader-Version wählen.
4. „Profil erstellen & installieren“ anklicken. Dieser Schritt braucht Internet
   und kann mehrere hundert MB herunterladen und Installer-Prozesse ausführen.
5. Das Profil auswählen und über „Mod-JARs hinzufügen“ lokale Mod-Dateien importieren.
6. „Zum Spielen auswählen“ klicken. Auf der Spielen-Seite steht das Profil im
   Dropdown „Spielprofil“. Der Versionswähler ist für ein Mod-Profil festgelegt.

Jedes Profil besitzt eigene Minecraft-Dateien, Mods, Konfigurationen und Welten.
Mods sind standardmäßig für alle drei Spielmodi dieses Profils vorgesehen. Vor
jedem Start werden die aktiven JAR-Dateien aus der Mod-Ablage in den gewählten
Spielordner kopiert. Deaktivierte Mods bleiben als `.jar.disabled` erhalten.

Forge, Quilt und NeoForge werden über die
[Modloader-Schnittstelle der Bibliothek](https://minecraft-launcher-lib.readthedocs.io/en/stable/modules/mod_loader.html)
installiert. Fabric verwendet das offizielle
[Fabric-Profil-API](https://meta.fabricmc.net/) für das Launcher-JSON.
Die Versionsauswahl zeigt nur Loader-Versionen, die der Adapter für
die gewählte Minecraft-Version anbietet. Sehr alte oder neue Kombinationen können
vom jeweiligen Installer oder der Bibliothek noch nicht unterstützt werden.

Echte Installation und Offline-Startargumente wurden für Fabric 0.20.1, Forge
47.4.28 und Quilt 0.30.1 auf Minecraft 1.20.1 sowie NeoForge 20.4.253 auf
Minecraft 1.20.4 geprüft. Ein anfänglicher Windows-Dateizugriffsfehler trat
innerhalb der eingeschränkten Test-Sandbox auf; außerhalb dieser Sandbox
bestand auch NeoForge den Installationstest. Ergebnisse und Grenzen stehen
im Prüfbericht.

## Welche Mods funktionieren?

Kompatible Minecraft-Java-Mods im JAR-Format können importiert werden. Eine
Garantie für „alle Mods“ gibt es nicht: Minecraft-Version, Loader, Java und die
anderen installierten Mods müssen zusammenpassen. Forge- und Fabric-Mods sind
grundsätzlich verschiedene Formate. Quilt kann manche Fabric-Mods laden, aber
auch hier besteht keine allgemeine Garantie.

Blockwerk liest `fabric.mod.json`, `quilt.mod.json`, `META-INF/mods.toml`,
`META-INF/neoforge.mods.toml` und ältere Forge-Kennungen. Erkannte eindeutige
Loader- oder Minecraft-Versionskonflikte werden beim Import abgelehnt. Ein Teil
üblicher Versionsregeln wird geprüft; unbekannte Regeln bleiben „manuell prüfen“.
Die Prüfung ersetzt keinen tatsächlichen Spielstart mit dem gesamten Mod-Set.

Fabric API und andere Mod-Abhängigkeiten müssen zusätzlich importiert werden.
Fehlende erkannte Abhängigkeiten werden in der Tabelle als Hinweis angezeigt.
Es gibt keinen automatischen Mod-Shop, keine automatische Auflösung aller
Abhängigkeiten und keine Garantie gegen Mod-Konflikte oder beschädigte Welten.
Die [Fabric-Anleitung](https://docs.fabricmc.net/players/installing-mods) beschreibt
die Anforderungen an passende Version, Loader und Mod-Abhängigkeiten.

Server-Plugins, Bedrock-Add-ons und Resourcepacks sind keine universellen
Forge-/Fabric-Mods. Der JAR-Import wandelt solche Formate nicht ineinander um.

## Andere Installer und installierte Profile

Für einen anderen Installer „Eigener Installer“ wählen und ein Profil mit der
gewünschten Minecraft-Basis erstellen. Nach der Installation der Basisdateien:

1. „Minecraft-Zielordner öffnen“ verwenden und den Pfad merken.
2. „Eigenen Installer öffnen“ anklicken und die eigene JAR- oder Windows-EXE-Datei
   wählen. Der Installer läuft als normales Programm.
3. Im Installer ausdrücklich den angezeigten Minecraft-Zielordner auswählen.
4. Nach Ende des Installers „Suchen“ klicken, die erzeugte Version wählen und
   „Installierte Version übernehmen“ anklicken.

Dieser Weg unterstützt Installer, die ein kompatibles Minecraft-Versionsprofil
und Bibliotheken erzeugen. EXE-Dateien laufen nur unter Windows. Ein Profil mit
`inheritsFrom` muss direkt zur gewählten Basis gehören. Beliebige Installer,
mehrstufige Vererbungen oder abweichende proprietäre Formate sind nicht generell
unterstützt. Es wird keine Kompatibilität nur anhand der Dateiendung versprochen.

## Offline-Server ohne Launcher-Limit

Es gibt nur noch **Online · Microsoft** und **Offline · Einzelspieler & Server**.
Der getrennte Community-Modus und das Fünferlimit sind entfernt.

1. Offline-Modus, lokalen Namen und passendes Vanilla-/Mod-Profil wählen.
2. Minecraft starten und **Mehrspieler → Server hinzufügen** öffnen.
3. Name und Adresse speichern und dem Server beitreten.

Minecraft speichert die Liste dauerhaft in der `servers.dat` des gewählten
Spielprofils und der Version. Derselbe Name und dasselbe Profil öffnen wieder
seine Liste. Verschiedene Spielinstanzen haben eigene Listen wie zuvor.

Unter **Server** lassen sich außerdem beliebig viele Launcher-Favoriten speichern.
Neue Adressen werden beim Offline-Start einmalig ergänzt. Vorhandene Einträge,
Reihenfolge, Serverbilder und unbekannte Mod-Tags bleiben bytegetreu erhalten.
Änderungen und Löschungen im Spiel werden beim nächsten Start nicht rückgängig
gemacht. Das Entfernen eines Launcher-Favoriten löscht keinen Ingame-Eintrag;
diesen in Minecraft entfernen. Vor einer Ergänzung entsteht eine Sicherung
`servers.dat.blockwerk-backup`; `blockwerk-server-imports.json` merkt sich bereits
übernommene Adressen. Eine beschädigte Serverliste wird nicht überschrieben.

Alte Community-Einstellungen werden in Offline umgestellt. Wenn noch keine lokale
Serverliste existiert, wird die frühere Community-Serverliste kopiert; ihr Original
bleibt erhalten. Alte Community-Welten bleiben über Welten auffindbar.

Der Server muss lokale Profile zulassen (häufig „Cracked“ oder Offline-Mode genannt).
Verfügbarkeit, Whitelist, eigene Serveranmeldung, Minecraft-Version und nötige Mods
bestimmt der jeweilige Server. Deshalb ist kein Beitritt zu jedem Server garantiert.
Kontogeprüfte Server und Realms benötigen eine gültige Microsoft-Anmeldung.
Es wurde kein öffentlicher fremder Server für diese Änderung betreten.

## Daten und verbleibende Tests

Unter `profiles/<Profil-ID>/` liegen `profile.json`, die zentrale Mod-Ablage
`mods/`, das jeweilige `minecraft/` und die Spielordner unter `instances/`.
Die globalen Favoriten liegen in `community-servers.json`.

Tests und konkrete Ergebnisse stehen in PRUEFBERICHT.md. Linux/macOS sind weiterhin
Quellpakete mit Start-/Build-Skripten; die nativen Programme für diese Systeme
wurden auf diesem Windows-Rechner nicht erzeugt oder ausgeführt.
