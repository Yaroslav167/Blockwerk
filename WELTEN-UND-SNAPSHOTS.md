# Welten und Snapshots · Blockwerk 0.6

## Vorhandene Welten sehen

**Welten** zeigt lokale Minecraft-Java-Spielstände aus allen Blockwerk-Instanzen
(auch andere lokale Spielernamen, Community und Mod-Profile), dem normalen
Minecraft-Java-Ordner und zusätzlich gewählten Ordnern. Über **Ordner hinzufügen**
kannst du einen Minecraft-, `saves`- oder einzelnen Weltordner auswählen.
Andere Launcher verwenden oft eigene Ordner. Ganze Festplatten werden nicht
durchsucht. Verknüpfte Weltordner bei Bedarf über ihren tatsächlichen Pfad hinzufügen.

Die Tabelle zeigt Name, Minecraft-Version, Spielmodus, letzten Spielzeitpunkt
und Herkunft. Nach Name, Version und Profil lässt sich suchen. **Aktualisieren**
sucht erneut. Bedrock-Welten, fremde Server und Realms werden nicht heruntergeladen.

## Eine bestehende Welt spielen

**Welt spielen** oder ein Doppelklick verwendet bei einer bekannten Blockwerk-Welt
das zugehörige Spielprofil, die Version und den lokalen Spielernamen. Bei einer
externen Welt wird die gespeicherte Minecraft-Version gesucht. Fehlende Spieldateien
werden mit Internet geladen. Lokaler Einzelspieler benötigt keine Microsoft-Anmeldung.

Neuere Versionen mit Quick Play öffnen die ausgewählte Welt direkt. Ältere
Versionen starten Minecraft mit dem richtigen Spielordner: dort **Einzelspieler**
anklicken und die Welt wählen. Die Direktstart-Argumente wurden mit
[Snapshot 23w14a](https://feedback.minecraft.net/hc/en-us/articles/14594878948237-Minecraft-Java-Edition-Snapshot-23w14a)
eingeführt; der Launcher prüft das tatsächliche Versionsmanifest.

Mod-Welten brauchen passende Mods und Loader. Bekannte Blockwerk-Mod-Profile
werden zugeordnet. Bei anderen Quellen gegebenenfalls zuerst das richtige
Mod-Profil unter Spielen wählen. Nicht alle Abhängigkeiten stehen in `level.dat`.

## Andere Versionen und Spielkopien

Eine Welt aus einem anderen Spielordner wird zuerst vollständig als **Spielkopie**
in das gewählte Profil übernommen. Das Original wird nicht verschoben oder
überschrieben. Eine vorhandene Spielkopie für dieses Ziel wird später weiterbenutzt;
Änderungen am Original werden nicht automatisch synchronisiert. Beide können in
der Übersicht stehen.

Für einen bewussten Versionswechsel zuerst unter **Spielen** die Zielversion wählen,
dann die Welt markieren und **In gewählter Version spielen** anklicken. Auch im
gleichen Spielordner entsteht bei abweichender gespeicherter Version eine Kopie.
Neuere Weltformate sind dadurch nicht automatisch mit älteren Versionen kompatibel.
Minecraft kann Konvertierungs- oder Experiment-Hinweise anzeigen.

Die Quellwelt muss geschlossen sein; ihre Sitzungssperre wird vor einem Import
geprüft. Interne symbolische Verknüpfungen werden beim Kopieren abgelehnt. Ein
abgebrochener Import entfernt ausschließlich seine eigene unvollständige Kopie.

## Eine neue Welt erstellen

1. Unter **Spielen** Profil, Version und Spielmodus wählen.
2. **Welten → Neue Welt in Minecraft** anklicken.
3. Im echten Spiel **Einzelspieler → Neue Welt erstellen** wählen.
4. Name, Seed, Schwierigkeit und weitere Einstellungen im Spiel festlegen.

Minecraft selbst erzeugt Terrain und Metadaten. Blockwerk legt keine leere
Ersatzwelt an. Nach normalem Beenden und erneutem Öffnen der Weltübersicht oder
**Aktualisieren** erscheint die neue Welt.

## Vollversionen und Snapshots

Über dem Versionswähler auf **Spielen** und auf der Versionen-Seite zwischen
**Vollversionen** und **Snapshots** umschalten. Beide Filter werden synchronisiert.
Die Vollversionen beginnen bei 1.0. Snapshots umfassen die von Mojang so
klassifizierten Versionen einschließlich dort geführter Pre-Releases/Release
Candidates. Alpha/Beta bleiben ausgeblendet. Am 26. Oktober 2026 wurden 103
Vollversionen und 756 Snapshots im offiziellen Katalog angeboten.

Ein alter Offline-Katalog enthält eventuell noch keine Snapshots. **Versionen →
Aktualisieren** lädt den öffentlichen Katalog mit Internet und ohne Microsoft-Konto.
Bereits vorbereitete Snapshots starten anschließend lokal ohne Launcher-Netzaufrufe.
Mod-Profile haben weiterhin eine feste unterstützte Vollversion; die Auswahl eines
Snapshots auf der Versionen-Seite wechselt deshalb zu Vanilla.

## Daten und Teststand

Zusätzliche Quellen stehen in `world-roots.json`, Spielkopie-Zuordnungen in
`world-imports.json` im Blockwerk-Datenordner. Welten bleiben normale Java-
Spielstände unter `instances/.../saves/`.

Neun echte vorhandene Welten wurden lesend erkannt. Eine separate Kopie einer
1.20.1-Welt wurde mit echtem Direktstart in Minecraft 1.20.1 und Snapshot 23w31a
geladen. Die Prüfsummen des Originals blieben unverändert. Alle angebotenen
Vollversions-/Snapshot-Metadaten und Startargumente wurden geprüft. Das ist kein
Spieltest jeder Welt in jeder Version. Details: PRUEFBERICHT.md.
