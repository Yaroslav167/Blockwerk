# Microsoft-Anmeldung · Blockwerk 0.9.1

Stand: 14. November 2026.

## Registriert und vorkonfiguriert

Die eigene Microsoft-App **Blockwerk** ist registriert:

- Öffentliche Application (client) ID: `e3162f09-b543-4833-82fb-9c25008e3ceb`
- Kontotyp: persönliche Microsoft-Konten.
- Plattform: Mobile/Desktop, öffentlicher Client.
- Registrierte Rückleitung: `http://localhost:29147/callback`
- Anmeldung: Authorization Code mit PKCE; kein Client-Secret.

Die öffentliche ID liegt in `launcher-auth.json` und wird in Windows-, Linux-
und macOS-Pakete übernommen. Ein explizit gespeicherter eigener Client-ID-Wert
hat weiterhin Vorrang. Die Registrierung wurde in Microsoft Azure sichtbar
bestätigt. Eine Registrierung allein ist kein Nachweis eines erfolgreichen
Minecraft-Logins oder einer Minecraft-API-Freigabe.

## Minecraft-API-Freigabe bleibt offen

Der Projektbetreiber hat ausdrücklich entschieden, den bisherigen lokalen Modus
ohne Konto beizubehalten und die Freigabe offenzulassen. Es wurde kein Antrag
abgeschickt und keine Zustimmung zu EULA-/Nutzungsbedingungen im Antrag erklärt.

Das am 14.11.2026 geprüfte offizielle Formular verlangt Authentifizierung und
Spielbesitzprüfung vor Gameplay bzw. Serverzugang, unabhängig von der
Serverkonfiguration. Der gegenwärtige lokale Start ohne Konto entspricht diesem
Zulassungskriterium nicht. Ein Antrag darf ihn nicht als stets lizenzgeprüft
darstellen. Der lokale Modus wurde in dieser Ausgabe nicht geändert.

Die Microsoft-Seite kann mit der App-ID geöffnet werden. Der spätere
Minecraft-Schritt kann ohne API-Freigabe abgelehnt werden. Ein vollständiger
realer Konto-Login, Konto-Skin-Upload, Realms und authentifizierter Serverbeitritt
sind weiterhin nicht bestätigt. App-ID-Konfigurationsprüfungen testen dies nicht.

Offizielles Formular: [Minecraft AppID Review](https://aka.ms/mce-reviewappid).

## Selbst prüfen

```sh
python main.py --check-auth auth-status.json
```

Im Windows-Paket kann `Blockwerk.exe --check-auth auth-status.json` verwendet
werden. Erwartet: `client_id_configured: true`, die obige öffentliche ID und
`minecraft_app_permission: not_verified`. Der Test führt keine Anmeldung aus
und liest keine gespeicherten Kontotokens.

Beim Quellupdate werden unveränderte Publisher-Standarddateien aktualisiert,
damit auch eine bisher leere mitgelieferte App-ID übernommen wird. Eigene
Änderungen an `launcher-auth.json` und `update-source.json` bleiben erhalten.
