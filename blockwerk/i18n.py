"""Bundled UI translations; stable identifiers and user content stay unchanged."""
LANGUAGE = 'de'


def set_language(value):
    global LANGUAGE
    LANGUAGE = value if value in ('de', 'en') else 'de'


def tr(text):
    return EN.get(text, text) if LANGUAGE == 'en' else text


def source_text(text):
    return REVERSE.get(text, text)


EN = {'\n\nDanach ‚Suchen‘ und ‚Installierte Version übernehmen‘ verwenden.': '\n'
                                                                         '\n'
                                                                         "Then use 'Search' and 'Use installed "
                                                                         "version'.",
 '\nBeantrage anschließend die Minecraft-API-Freigabe.': '\nThen request Minecraft API access.',
 ' (noch installieren)': ' (install first)',
 ' Anmeldung gilt nur für diese Sitzung; sicherer Kontospeicher ist nicht verfügbar.': ' Sign-in is valid for '
                                                                                       'this session only; secure '
                                                                                       'account storage is '
                                                                                       'unavailable.',
 ' Dateien übertragen …': ' files copied …',
 ' Die App-Kennung ist hinterlegt; die Minecraft-Freigabe wird erst beim echten Login geprüft.': ' The app ID is '
                                                                                                 'configured; '
                                                                                                 'Minecraft '
                                                                                                 'approval is '
                                                                                                 'checked during '
                                                                                                 'actual sign-in.',
 ' Die Launcher-Registrierung für Microsoft fehlt noch.': ' Microsoft registration for this launcher is still '
                                                          'missing.',
 ' Die vorhandene App bleibt verwendbar.': ' The existing app remains usable.',
 ' Für dieses System liegt im Kanal noch kein Paket vor.': ' No package for this system has been published to '
                                                           'this channel yet.',
 ' Geprüftes Paket heruntergeladen.': ' Verified package downloaded.',
 ' Mod-Dateien importiert. Abhängigkeiten und Hinweise prüfen.': ' mod files imported. Check dependencies and '
                                                                 'compatibility notes.',
 ' Pixel. Noch keine Kontoänderung durchgeführt.': ' pixels. No account changes have been made.',
 ' Versionen': ' versions',
 ' Vollversionen und Snapshots aus dem Mojang-Katalog geladen.': ' releases and snapshots loaded from the Mojang '
                                                                 'catalog.',
 ' WELTEN': ' WORLDS',
 ' ausgewählt.': ' selected.',
 ' beendet. Prüfe logs und crash-reports im Spielordner.': '. Check logs and crash-reports in the game folder.',
 ' ist ein unabhängiger Launcher für Windows, Linux und macOS. Er lädt originale Minecraft-Java-Dateien und verwendet den Microsoft-Login im Browser.': ' '
                                                                                                                                                        'is '
                                                                                                                                                        'an '
                                                                                                                                                        'independent '
                                                                                                                                                        'launcher '
                                                                                                                                                        'for '
                                                                                                                                                        'Windows, '
                                                                                                                                                        'Linux '
                                                                                                                                                        'and '
                                                                                                                                                        'macOS. '
                                                                                                                                                        'It '
                                                                                                                                                        'downloads '
                                                                                                                                                        'original '
                                                                                                                                                        'Minecraft '
                                                                                                                                                        'Java '
                                                                                                                                                        'files '
                                                                                                                                                        'and '
                                                                                                                                                        'uses '
                                                                                                                                                        'Microsoft '
                                                                                                                                                        'sign-in '
                                                                                                                                                        'in '
                                                                                                                                                        'your '
                                                                                                                                                        'browser.',
 ' ist laut Metadaten nicht für Minecraft ': ' is not intended for Minecraft ',
 ' ist vorbereitet. Du kannst jetzt offline ohne Microsoft-Konto starten.': ' is ready. You can now launch '
                                                                            'offline without a Microsoft account.',
 ' lokale Java-Welten gefunden.': ' local Java worlds found.',
 ' läuft mit lokalem Profil. Mehrspieler ist für Server verfügbar, die lokale Profile zulassen.': ' is running '
                                                                                                  'with a local '
                                                                                                  'profile. '
                                                                                                  'Multiplayer is '
                                                                                                  'available for '
                                                                                                  'servers that '
                                                                                                  'allow local '
                                                                                                  'profiles.',
 ' läuft. Viel Spaß!': ' is running. Have fun!',
 ' nicht. Bitte eine passende Version wählen.': '. Select a compatible version.',
 ' passende Loader-Versionen geladen.': ' compatible loader versions loaded.',
 ' unterstützt Minecraft ': ' supports Minecraft ',
 ' von ': ' of ',
 ' wird geprüft und bei Bedarf heruntergeladen …': ' is being checked and downloaded if needed …',
 ' wird installiert …': ' is being installed …',
 '). Bitte erneut versuchen.': '). Try again.',
 '). Installiertes Profil auswählen und übernehmen.': '). Select and use the installed profile.',
 ', nicht zu ': ', not ',
 '-Installer ist fehlgeschlagen. Java und installer-error.log im Profilordner prüfen.': ' installer failed. Check '
                                                                                        'Java and '
                                                                                        'installer-error.log in '
                                                                                        'the profile folder.',
 '. Minecraft Java ist verfügbar.': '. Minecraft Java is available.',
 '1 · Eigene Microsoft-App registrieren\nPersönliche Microsoft-Konten · Mobile/Desktop · Public Client': '1 · '
                                                                                                         'Register '
                                                                                                         'your '
                                                                                                         'own '
                                                                                                         'Microsoft '
                                                                                                         'app\n'
                                                                                                         'Personal '
                                                                                                         'Microsoft '
                                                                                                         'accounts '
                                                                                                         '· '
                                                                                                         'Mobile/Desktop '
                                                                                                         '· '
                                                                                                         'Public '
                                                                                                         'client',
 '2 · Diese Redirect-URI in der App hinterlegen': '2 · Configure this redirect URI in the app',
 '3 · Eigene öffentliche Application (client) ID eintragen': '3 · Enter your own public Application (client) ID',
 '3–16 Zeichen, z. B. Spieler': '3–16 characters, e.g. Player',
 '4 · Einstellungen speichern und Minecraft-API-Freigabe beantragen\nEine eingetragene ID bestätigt noch keine Freigabe. Kein Client-Secret eintragen.': '4 '
                                                                                                                                                         '· '
                                                                                                                                                         'Save '
                                                                                                                                                         'settings '
                                                                                                                                                         'and '
                                                                                                                                                         'request '
                                                                                                                                                         'Minecraft '
                                                                                                                                                         'API '
                                                                                                                                                         'access\n'
                                                                                                                                                         'An '
                                                                                                                                                         'entered '
                                                                                                                                                         'ID '
                                                                                                                                                         'does '
                                                                                                                                                         'not '
                                                                                                                                                         'confirm '
                                                                                                                                                         'approval. '
                                                                                                                                                         'Do '
                                                                                                                                                         'not '
                                                                                                                                                         'enter '
                                                                                                                                                         'a '
                                                                                                                                                         'client '
                                                                                                                                                         'secret.',
 '4096 MB sind ein guter Start. Lass genug RAM für dein Betriebssystem frei.': '4096 MB is a good starting point. '
                                                                               'Leave enough RAM for your '
                                                                               'operating system.',
 'ABBRUCH LÄUFT': 'CANCELING',
 'ANMELDUNG LÄUFT': 'SIGNING IN',
 'ANMELDUNG NICHT ABGESCHLOSSEN': 'SIGN-IN NOT COMPLETED',
 'Abbrechen': 'Cancel',
 'Abbruch angefordert. Ein laufender Download wird noch abgeschlossen …': 'Cancellation requested. The current '
                                                                          'download is finishing …',
 'Abenteuer': 'Adventure',
 'Abmelden': 'Sign out',
 'Absoluter Pfad im Updatearchiv.': 'Absolute path in update archive.',
 'Aktiv': 'Enabled',
 'Aktiv / deaktiviert': 'Enable / disable',
 'Aktivität': 'Activity',
 'Aktualisieren': 'Refresh',
 'Alle Releases findest du unter Versionen.': 'All releases are listed under Versions.',
 'Als echten Minecraft-Konto-Skin verwenden': 'Use as your Minecraft account skin',
 'Anderes Microsoft-Konto verwenden ↗': 'Use another Microsoft account ↗',
 'Angemeldet als ': 'Signed in as ',
 'Animation fortsetzen': 'Resume animation',
 'Animation pausieren': 'Pause animation',
 'Animierte Blocklandschaft': 'Animated block landscape',
 'Anleitung & technische Hinweise ↗': 'Guide & technical notes ↗',
 'Anmeldelink kopieren': 'Copy sign-in link',
 'Anmeldelink kopiert. Öffne ihn in deinem Browser und kehre anschließend zu Blockwerk zurück.': 'Sign-in link '
                                                                                                 'copied. Open it '
                                                                                                 'in your '
                                                                                                 'browser, then '
                                                                                                 'return to '
                                                                                                 'Blockwerk.',
 'Anmelden': 'Sign in',
 'Anmeldung abbrechen': 'Cancel sign-in',
 'Anmeldung abgebrochen.': 'Sign-in canceled.',
 'Anmeldung abgebrochen. Du kannst es erneut versuchen.': 'Sign-in canceled. You can try again.',
 'Anmeldung für den Spielstart wird erneuert …': 'Refreshing sign-in for game launch …',
 'Anmeldung gespeichert': 'Sign-in saved',
 'Anmeldung nach 5 Minuten abgelaufen. Bitte erneut versuchen.': 'Sign-in timed out after 5 minutes. Try again.',
 'Anmeldung sicher speichern': 'Store sign-in securely',
 'Anmeldung und Minecraft-Lizenz werden geprüft …': 'Checking sign-in and Minecraft license …',
 'Anmeldung wird abgebrochen. Eine laufende Anfrage wird noch abgeschlossen …': 'Canceling sign-in. The current '
                                                                                'request is finishing …',
 'Anmeldung wird beendet': 'Finishing sign-in',
 'Anmeldung, Kontostatus und Hilfe findest du auf der Kontoseite. Die technische Registrierung wird einmalig vom Projektbetreiber eingerichtet.': 'Sign-in, '
                                                                                                                                                  'account '
                                                                                                                                                  'status '
                                                                                                                                                  'and '
                                                                                                                                                  'help '
                                                                                                                                                  'are '
                                                                                                                                                  'available '
                                                                                                                                                  'on '
                                                                                                                                                  'the '
                                                                                                                                                  'account '
                                                                                                                                                  'page. '
                                                                                                                                                  'The '
                                                                                                                                                  'project '
                                                                                                                                                  'operator '
                                                                                                                                                  'configures '
                                                                                                                                                  'the '
                                                                                                                                                  'app '
                                                                                                                                                  'registration '
                                                                                                                                                  'once.',
 'App-ID prüfen': 'Check app ID',
 'Arbeitsspeicher für Minecraft': 'Memory for Minecraft',
 'Aus Liste entfernen': 'Remove from list',
 'Ausgewählt: ': 'Selected: ',
 'Auswählen …': 'Browse …',
 'Automatisch die zur Minecraft-Version passende Laufzeit': 'Automatically use the runtime required by this '
                                                            'Minecraft version',
 'Automatische Installation gibt es für das portable Windows-Paket. Dieses Paket bitte manuell entpacken.': 'Automatic '
                                                                                                            'installation '
                                                                                                            'is '
                                                                                                            'available '
                                                                                                            'for '
                                                                                                            'the '
                                                                                                            'portable '
                                                                                                            'Windows '
                                                                                                            'package. '
                                                                                                            'Extract '
                                                                                                            'this '
                                                                                                            'package '
                                                                                                            'manually.',
 'Automatische Installation unterstützt das portable Windows-Paket in einem eigenen App-Ordner. Quellpakete und andere Systeme können das geprüfte Paket manuell installieren. Die vorherige App bleibt als Sicherung erhalten.': 'Automatic '
                                                                                                                                                                                                                                  'installation '
                                                                                                                                                                                                                                  'supports '
                                                                                                                                                                                                                                  'the '
                                                                                                                                                                                                                                  'portable '
                                                                                                                                                                                                                                  'Windows '
                                                                                                                                                                                                                                  'package '
                                                                                                                                                                                                                                  'in '
                                                                                                                                                                                                                                  'its '
                                                                                                                                                                                                                                  'own '
                                                                                                                                                                                                                                  'app '
                                                                                                                                                                                                                                  'folder. '
                                                                                                                                                                                                                                  'Source '
                                                                                                                                                                                                                                  'packages '
                                                                                                                                                                                                                                  'and '
                                                                                                                                                                                                                                  'other '
                                                                                                                                                                                                                                  'systems '
                                                                                                                                                                                                                                  'can '
                                                                                                                                                                                                                                  'install '
                                                                                                                                                                                                                                  'the '
                                                                                                                                                                                                                                  'verified '
                                                                                                                                                                                                                                  'package '
                                                                                                                                                                                                                                  'manually. '
                                                                                                                                                                                                                                  'The '
                                                                                                                                                                                                                                  'previous '
                                                                                                                                                                                                                                  'app '
                                                                                                                                                                                                                                  'is '
                                                                                                                                                                                                                                  'kept '
                                                                                                                                                                                                                                  'as '
                                                                                                                                                                                                                                  'a '
                                                                                                                                                                                                                                  'backup.',
 'BAU. ENTDECKE. BLEIB NEUGIERIG.': 'BUILD. EXPLORE. STAY CURIOUS.',
 'BEREIT ZUR ANMELDUNG': 'READY TO SIGN IN',
 'Bei älteren Versionen im Spiel ‚Einzelspieler‘ wählen. Für neue Welten dort ‚Neue Welt erstellen‘ anklicken und die gewünschten Einstellungen wählen. Fehlende Spieldateien benötigen einen Internet-Download.': 'For '
                                                                                                                                                                                                                   'older '
                                                                                                                                                                                                                   'versions, '
                                                                                                                                                                                                                   'select '
                                                                                                                                                                                                                   "'Singleplayer' "
                                                                                                                                                                                                                   'in '
                                                                                                                                                                                                                   'the '
                                                                                                                                                                                                                   'game. '
                                                                                                                                                                                                                   'To '
                                                                                                                                                                                                                   'create '
                                                                                                                                                                                                                   'a '
                                                                                                                                                                                                                   'world, '
                                                                                                                                                                                                                   'choose '
                                                                                                                                                                                                                   "'Create "
                                                                                                                                                                                                                   'New '
                                                                                                                                                                                                                   "World' "
                                                                                                                                                                                                                   'and '
                                                                                                                                                                                                                   'your '
                                                                                                                                                                                                                   'settings '
                                                                                                                                                                                                                   'there. '
                                                                                                                                                                                                                   'Missing '
                                                                                                                                                                                                                   'game '
                                                                                                                                                                                                                   'files '
                                                                                                                                                                                                                   'require '
                                                                                                                                                                                                                   'an '
                                                                                                                                                                                                                   'internet '
                                                                                                                                                                                                                   'download.',
 'Benötigt installierte Spieldateien mit version.json, gewöhnlich Minecraft 1.14 oder neuer. Eigene Ressourcenpakete bleiben ausgewählt; ein laufendes Spiel danach neu starten.': 'Requires '
                                                                                                                                                                                   'installed '
                                                                                                                                                                                   'game '
                                                                                                                                                                                   'files '
                                                                                                                                                                                   'with '
                                                                                                                                                                                   'version.json, '
                                                                                                                                                                                   'usually '
                                                                                                                                                                                   'Minecraft '
                                                                                                                                                                                   '1.14 '
                                                                                                                                                                                   'or '
                                                                                                                                                                                   'newer. '
                                                                                                                                                                                   'Your '
                                                                                                                                                                                   'other '
                                                                                                                                                                                   'resource '
                                                                                                                                                                                   'packs '
                                                                                                                                                                                   'stay '
                                                                                                                                                                                   'selected; '
                                                                                                                                                                                   'restart '
                                                                                                                                                                                   'a '
                                                                                                                                                                                   'running '
                                                                                                                                                                                   'game '
                                                                                                                                                                                   'afterwards.',
 'Bereit. Spielprofil und Spielmodus auswählen.': 'Ready. Select a game profile and mode.',
 'Bewegung auf der Startseite anhalten oder fortsetzen': 'Pause or resume animation on the home page',
 'Bitte Classic oder Slim wählen.': 'Select Classic or Slim.',
 'Bitte Mod-Dateien im JAR-Format auswählen.': 'Select mod files in JAR format.',
 'Bitte eine Mod-Datei auswählen.': 'Please select a mod file.',
 'Bitte eine Serveradresse wie spiel.example.org:25565 eingeben, ohne https://.': 'Enter a server address such as '
                                                                                  'play.example.org:25565 without '
                                                                                  'https://.',
 'Bitte eine Skin-PNG mit höchstens 1 MB auswählen.': 'Select a skin PNG no larger than 1 MB.',
 'Bitte eine Vollversion ab 1.0 oder einen Snapshot aus dem offiziellen Katalog auswählen. Aktualisiere gegebenenfalls die Versionsliste.': 'Select '
                                                                                                                                            'a '
                                                                                                                                            'release '
                                                                                                                                            'from '
                                                                                                                                            '1.0 '
                                                                                                                                            'onwards '
                                                                                                                                            'or '
                                                                                                                                            'a '
                                                                                                                                            'snapshot '
                                                                                                                                            'from '
                                                                                                                                            'the '
                                                                                                                                            'official '
                                                                                                                                            'catalog. '
                                                                                                                                            'Refresh '
                                                                                                                                            'the '
                                                                                                                                            'version '
                                                                                                                                            'list '
                                                                                                                                            'if '
                                                                                                                                            'needed.',
 'Bitte eine vorhandene Blockwerk-Update-JSON auswählen.': 'Select an existing Blockwerk update JSON file.',
 'Bitte eine vorhandene Java-Programmdatei auswählen (Windows: java.exe/javaw.exe; Linux/macOS: bin/java).': 'Select '
                                                                                                             'an '
                                                                                                             'existing '
                                                                                                             'Java '
                                                                                                             'executable '
                                                                                                             '(Windows: '
                                                                                                             'java.exe/javaw.exe; '
                                                                                                             'Linux/macOS: '
                                                                                                             'bin/java).',
 'Bitte einen Loader und ein Minecraft-Release ab 1.0 auswählen.': 'Select a loader and a Minecraft release from '
                                                                   '1.0 onwards.',
 'Bitte einen Profilnamen mit 1–60 sichtbaren Zeichen wählen.': 'Choose a profile name with 1–60 visible '
                                                                'characters.',
 'Bitte einen Updateordner oder eine HTTPS-Updatequelle hinterlegen.': 'Configure an update folder or HTTPS '
                                                                       'update source.',
 'Bitte einen vorhandenen Minecraft-, saves- oder Weltordner wählen.': 'Select an existing Minecraft, saves or '
                                                                       'world folder.',
 'Bitte erst installierte Versionen suchen und auswählen.': 'Search for installed versions and select one first.',
 'Bitte im Microsoft-Browser': 'Please continue in your\nMicrosoft browser window',
 'Bitte im Microsoft-Browserfenster anmelden …': 'Sign in in the Microsoft browser window …',
 'Bitte prüfe diesen Hinweis': 'Please check this message',
 'Bitte trage unter Einstellungen eine gültige Microsoft-App-ID (Client-ID) ein.': 'Enter a valid Microsoft app '
                                                                                   'ID (client ID) under '
                                                                                   'Settings.',
 'Bitte unter Spielen zuerst eine Version auswählen und ihre Spieldateien herunterladen.': 'Select a version '
                                                                                           'under Play and '
                                                                                           'download its game '
                                                                                           'files first.',
 'Bitte zuerst das Profil erstellen und die Basisdateien installieren.': 'Create the profile and install its base '
                                                                         'files first.',
 'Bitte zuerst das gewählte Mod-Profil unter Mods & Loader installieren.': 'Install the selected mod profile '
                                                                           'under Mods & Loaders first.',
 'Bitte zuerst dein Microsoft-Konto mit Minecraft Java verbinden.': 'Connect your Microsoft account with '
                                                                    'Minecraft Java first.',
 'Bitte zuerst den Minecraft-Versionskatalog laden.': 'Load the Minecraft version catalog first.',
 'Bitte zuerst die Basisdateien des Profils installieren.': "Install the profile's base files first.",
 'Bitte zuerst ein Mod-Profil erstellen oder auswählen.': 'Create or select a mod profile first.',
 'Bitte zuerst eine Version in der Liste auswählen.': 'Select a version in the list first.',
 'Bitte zuerst eine Version laden und auswählen. Für den Katalog einmal auf Online stellen und Aktualisieren klicken.': 'Load '
                                                                                                                        'and '
                                                                                                                        'select '
                                                                                                                        'a '
                                                                                                                        'version '
                                                                                                                        'first. '
                                                                                                                        'Switch '
                                                                                                                        'to '
                                                                                                                        'Online '
                                                                                                                        'and '
                                                                                                                        'click '
                                                                                                                        'Refresh '
                                                                                                                        'once '
                                                                                                                        'to '
                                                                                                                        'load '
                                                                                                                        'the '
                                                                                                                        'catalog.',
 'Bitte zuerst eine Vollversion oder einen Snapshot auswählen.': 'Select a release or snapshot first.',
 'Bitte zuerst eine Welt auswählen.': 'Select a world first.',
 'Bitte zuerst einen Skin auswählen.': 'Select a skin first.',
 'Bitte zuerst einen Versionskatalog laden und die passende Spielversion auswählen.': 'Load a version catalog and '
                                                                                      'select the appropriate '
                                                                                      'game version first.',
 'Bitte zuerst mit dem Microsoft-Konto anmelden, das Minecraft Java besitzt.': 'Sign in with the Microsoft '
                                                                               'account that owns Minecraft Java '
                                                                               'first.',
 'Blockwerk aktuell halten': 'Keep Blockwerk up to date',
 'Blockwerk besitzt noch keine eigene freigegebene Microsoft-App-Kennung. Der Projektbetreiber muss den Launcher registrieren und für die Minecraft-API freigeben lassen. Du brauchst hier keine E-Mail-Adresse oder ein Passwort einzutragen. Lokale Profile bleiben verfügbar.': 'Blockwerk '
                                                                                                                                                                                                                                                                                   'does '
                                                                                                                                                                                                                                                                                   'not '
                                                                                                                                                                                                                                                                                   'yet '
                                                                                                                                                                                                                                                                                   'have '
                                                                                                                                                                                                                                                                                   'its '
                                                                                                                                                                                                                                                                                   'own '
                                                                                                                                                                                                                                                                                   'approved '
                                                                                                                                                                                                                                                                                   'Microsoft '
                                                                                                                                                                                                                                                                                   'app '
                                                                                                                                                                                                                                                                                   'ID. '
                                                                                                                                                                                                                                                                                   'The '
                                                                                                                                                                                                                                                                                   'project '
                                                                                                                                                                                                                                                                                   'operator '
                                                                                                                                                                                                                                                                                   'must '
                                                                                                                                                                                                                                                                                   'register '
                                                                                                                                                                                                                                                                                   'the '
                                                                                                                                                                                                                                                                                   'launcher '
                                                                                                                                                                                                                                                                                   'and '
                                                                                                                                                                                                                                                                                   'obtain '
                                                                                                                                                                                                                                                                                   'Minecraft '
                                                                                                                                                                                                                                                                                   'API '
                                                                                                                                                                                                                                                                                   'approval. '
                                                                                                                                                                                                                                                                                   'You '
                                                                                                                                                                                                                                                                                   'do '
                                                                                                                                                                                                                                                                                   'not '
                                                                                                                                                                                                                                                                                   'need '
                                                                                                                                                                                                                                                                                   'to '
                                                                                                                                                                                                                                                                                   'enter '
                                                                                                                                                                                                                                                                                   'an '
                                                                                                                                                                                                                                                                                   'email '
                                                                                                                                                                                                                                                                                   'address '
                                                                                                                                                                                                                                                                                   'or '
                                                                                                                                                                                                                                                                                   'password '
                                                                                                                                                                                                                                                                                   'here. '
                                                                                                                                                                                                                                                                                   'Local '
                                                                                                                                                                                                                                                                                   'profiles '
                                                                                                                                                                                                                                                                                   'remain '
                                                                                                                                                                                                                                                                                   'available.',
 'Blockwerk fragt kein Passwort ab. Windows verwendet DPAPI, macOS den Schlüsselbund und Linux Secret Service. Fehlt der sichere Speicher, gilt die Anmeldung nur für die aktuelle Sitzung. Offline werden keine Tokens erneuert oder Dateien heruntergeladen. Abmelden entfernt die Microsoft-Sitzung; lokale Profile und Welten bleiben erhalten.': 'Blockwerk '
                                                                                                                                                                                                                                                                                                                                                      'never '
                                                                                                                                                                                                                                                                                                                                                      'asks '
                                                                                                                                                                                                                                                                                                                                                      'for '
                                                                                                                                                                                                                                                                                                                                                      'your '
                                                                                                                                                                                                                                                                                                                                                      'password. '
                                                                                                                                                                                                                                                                                                                                                      'Windows '
                                                                                                                                                                                                                                                                                                                                                      'uses '
                                                                                                                                                                                                                                                                                                                                                      'DPAPI, '
                                                                                                                                                                                                                                                                                                                                                      'macOS '
                                                                                                                                                                                                                                                                                                                                                      'uses '
                                                                                                                                                                                                                                                                                                                                                      'Keychain '
                                                                                                                                                                                                                                                                                                                                                      'and '
                                                                                                                                                                                                                                                                                                                                                      'Linux '
                                                                                                                                                                                                                                                                                                                                                      'uses '
                                                                                                                                                                                                                                                                                                                                                      'Secret '
                                                                                                                                                                                                                                                                                                                                                      'Service. '
                                                                                                                                                                                                                                                                                                                                                      'Without '
                                                                                                                                                                                                                                                                                                                                                      'secure '
                                                                                                                                                                                                                                                                                                                                                      'storage, '
                                                                                                                                                                                                                                                                                                                                                      'sign-in '
                                                                                                                                                                                                                                                                                                                                                      'lasts '
                                                                                                                                                                                                                                                                                                                                                      'for '
                                                                                                                                                                                                                                                                                                                                                      'this '
                                                                                                                                                                                                                                                                                                                                                      'session '
                                                                                                                                                                                                                                                                                                                                                      'only. '
                                                                                                                                                                                                                                                                                                                                                      'Offline '
                                                                                                                                                                                                                                                                                                                                                      'mode '
                                                                                                                                                                                                                                                                                                                                                      'does '
                                                                                                                                                                                                                                                                                                                                                      'not '
                                                                                                                                                                                                                                                                                                                                                      'refresh '
                                                                                                                                                                                                                                                                                                                                                      'tokens '
                                                                                                                                                                                                                                                                                                                                                      'or '
                                                                                                                                                                                                                                                                                                                                                      'download '
                                                                                                                                                                                                                                                                                                                                                      'files. '
                                                                                                                                                                                                                                                                                                                                                      'Signing '
                                                                                                                                                                                                                                                                                                                                                      'out '
                                                                                                                                                                                                                                                                                                                                                      'removes '
                                                                                                                                                                                                                                                                                                                                                      'the '
                                                                                                                                                                                                                                                                                                                                                      'Microsoft '
                                                                                                                                                                                                                                                                                                                                                      'session; '
                                                                                                                                                                                                                                                                                                                                                      'local '
                                                                                                                                                                                                                                                                                                                                                      'profiles '
                                                                                                                                                                                                                                                                                                                                                      'and '
                                                                                                                                                                                                                                                                                                                                                      'worlds '
                                                                                                                                                                                                                                                                                                                                                      'remain.',
 'Blockwerk konnte nicht starten': 'Blockwerk could not start',
 'Blockwerk verbindet dein Xbox-Profil und prüft, ob Minecraft Java für dein Konto verfügbar ist.': 'Blockwerk is '
                                                                                                    'connecting '
                                                                                                    'your Xbox '
                                                                                                    'profile and '
                                                                                                    'checking '
                                                                                                    'whether '
                                                                                                    'Minecraft '
                                                                                                    'Java is '
                                                                                                    'available '
                                                                                                    'for your '
                                                                                                    'account.',
 'Blockwerk-Profile, der normale Minecraft-Ordner und zusätzlich gewählte Ordner. Andere Quellen werden beim ersten Öffnen als Spielkopie übernommen. Neue Welten werden von Minecraft selbst erzeugt.': 'Blockwerk '
                                                                                                                                                                                                         'profiles, '
                                                                                                                                                                                                         'the '
                                                                                                                                                                                                         'regular '
                                                                                                                                                                                                         'Minecraft '
                                                                                                                                                                                                         'folder '
                                                                                                                                                                                                         'and '
                                                                                                                                                                                                         'additional '
                                                                                                                                                                                                         'folders '
                                                                                                                                                                                                         'you '
                                                                                                                                                                                                         'select. '
                                                                                                                                                                                                         'Worlds '
                                                                                                                                                                                                         'from '
                                                                                                                                                                                                         'other '
                                                                                                                                                                                                         'locations '
                                                                                                                                                                                                         'are '
                                                                                                                                                                                                         'copied '
                                                                                                                                                                                                         'when '
                                                                                                                                                                                                         'first '
                                                                                                                                                                                                         'opened. '
                                                                                                                                                                                                         'Minecraft '
                                                                                                                                                                                                         'itself '
                                                                                                                                                                                                         'creates '
                                                                                                                                                                                                         'new '
                                                                                                                                                                                                         'worlds.',
 'Browser erneut öffnen ↗': 'Open browser again ↗',
 'Classic · breite Arme': 'Classic · wide arms',
 'DEIN KONTO': 'YOUR ACCOUNT',
 'Das Updatearchiv enthält doppelte Dateinamen.': 'The update archive contains duplicate filenames.',
 'Das Updatearchiv enthält einen unzulässigen Dateipfad.': 'The update archive contains an unsafe file path.',
 'Das Updatepaket ist größer als angekündigt.': 'The update package is larger than declared.',
 'Das Updatepaket muss direkt im gewählten Updateordner liegen.': 'The update package must be directly inside the '
                                                                  'selected update folder.',
 'Das Updatepaket wurde nach dem Download verändert.': 'The update package changed after download.',
 'Das Versionsmanifest enthält einen unbekannten Startparameter. Bitte den Launcher aktualisieren.': 'The version '
                                                                                                     'manifest '
                                                                                                     'contains an '
                                                                                                     'unknown '
                                                                                                     'launch '
                                                                                                     'argument. '
                                                                                                     'Update the '
                                                                                                     'launcher.',
 'Das entpackte Update ist zu groß.': 'The extracted update is too large.',
 'Das geprüfte Update wird neben dem App-Ordner vorbereitet …': 'Preparing the verified update beside the app '
                                                                'folder …',
 'Das installierte Profil muss direkt zur gewählten Minecraft-Basis passen.': 'The installed profile must '
                                                                              'directly match the selected base '
                                                                              'Minecraft version.',
 'Das lokale Skinpaket benötigt eine vollständig installierte Minecraft-Version mit version.json (gewöhnlich 1.14 oder neuer). Bitte zuerst Spieldateien herunterladen.': 'The '
                                                                                                                                                                          'local '
                                                                                                                                                                          'skin '
                                                                                                                                                                          'pack '
                                                                                                                                                                          'requires '
                                                                                                                                                                          'a '
                                                                                                                                                                          'fully '
                                                                                                                                                                          'installed '
                                                                                                                                                                          'Minecraft '
                                                                                                                                                                          'version '
                                                                                                                                                                          'with '
                                                                                                                                                                          'version.json '
                                                                                                                                                                          '(usually '
                                                                                                                                                                          '1.14 '
                                                                                                                                                                          'or '
                                                                                                                                                                          'newer). '
                                                                                                                                                                          'Download '
                                                                                                                                                                          'game '
                                                                                                                                                                          'files '
                                                                                                                                                                          'first.',
 'Das lokale Skinpaket ersetzt die Standardfiguren in der gewählten Spielinstanz. Es ist kein Konto-Skin: Andere Spieler sehen die Änderung nicht, und auch andere Standardfiguren können so aussehen. Die Armform richtet sich dabei nach dem Standardmodell des Spiels.': 'The '
                                                                                                                                                                                                                                                                            'local '
                                                                                                                                                                                                                                                                            'skin '
                                                                                                                                                                                                                                                                            'pack '
                                                                                                                                                                                                                                                                            'replaces '
                                                                                                                                                                                                                                                                            'default '
                                                                                                                                                                                                                                                                            'characters '
                                                                                                                                                                                                                                                                            'in '
                                                                                                                                                                                                                                                                            'the '
                                                                                                                                                                                                                                                                            'selected '
                                                                                                                                                                                                                                                                            'game '
                                                                                                                                                                                                                                                                            'instance. '
                                                                                                                                                                                                                                                                            'It '
                                                                                                                                                                                                                                                                            'is '
                                                                                                                                                                                                                                                                            'not '
                                                                                                                                                                                                                                                                            'an '
                                                                                                                                                                                                                                                                            'account '
                                                                                                                                                                                                                                                                            'skin: '
                                                                                                                                                                                                                                                                            'other '
                                                                                                                                                                                                                                                                            'players '
                                                                                                                                                                                                                                                                            'cannot '
                                                                                                                                                                                                                                                                            'see '
                                                                                                                                                                                                                                                                            'the '
                                                                                                                                                                                                                                                                            'change, '
                                                                                                                                                                                                                                                                            'and '
                                                                                                                                                                                                                                                                            'other '
                                                                                                                                                                                                                                                                            'default '
                                                                                                                                                                                                                                                                            'characters '
                                                                                                                                                                                                                                                                            'may '
                                                                                                                                                                                                                                                                            'also '
                                                                                                                                                                                                                                                                            'use '
                                                                                                                                                                                                                                                                            'it. '
                                                                                                                                                                                                                                                                            'Arm '
                                                                                                                                                                                                                                                                            'shape '
                                                                                                                                                                                                                                                                            'follows '
                                                                                                                                                                                                                                                                            'the '
                                                                                                                                                                                                                                                                            "game's "
                                                                                                                                                                                                                                                                            'default '
                                                                                                                                                                                                                                                                            'model.',
 'Das zugehörige Mod-Profil ist nicht mehr vorhanden.': 'The associated mod profile no longer exists.',
 'Datei': 'File',
 'Datei oder Programm nicht verfügbar. Prüfe Speicherplatz und den eingestellten Java-Pfad.': 'File or program '
                                                                                              'unavailable. Check '
                                                                                              'disk space and the '
                                                                                              'configured Java '
                                                                                              'path.',
 'Dateien': 'Files',
 'Dateien vorhanden · Prüfung beim Start': 'Files installed · Checked on launch',
 'Datenordner öffnen ↗': 'Open data folder ↗',
 'Deaktiviert': 'Disabled',
 'Dein Konto wird geprüft': 'Checking your account',
 'Dein Konto. Deine Welten.': 'Your account. Your worlds.',
 'Dein Look für Minecraft Java': 'Your look for Minecraft Java',
 'Dein Updatekanal': 'Your update channel',
 'Dein Weg in die Welt.': 'Your way into the world.',
 'Deine Anmeldung': 'Your sign-in',
 'Deine Anmeldung bleibt bei Microsoft': 'Your sign-in stays with Microsoft',
 'Deine Anmeldung wird im geschützten Kontospeicher des Betriebssystems verwahrt.': 'Your sign-in is stored in '
                                                                                    "your operating system's "
                                                                                    'protected account storage.',
 'Deine Dateien': 'Your files',
 'Deine Minecraft-Java-Lizenz': 'Your Minecraft Java license',
 'Deine Minecraft-Java-Lizenz wird geprüft …': 'Checking your Minecraft Java license …',
 'Deine lokalen Minecraft-Java-Welten': 'Your local Minecraft Java worlds',
 'Deine nächste\nWelt wartet.': 'Your next\nworld awaits.',
 'Dem Update fehlt eine gültige SHA256-Prüfsumme.': 'The update has no valid SHA256 checksum.',
 'Der App-Ordner enthält weitere Dateien. Bitte das Paket manuell in einen eigenen App-Ordner entpacken.': 'The '
                                                                                                           'app '
                                                                                                           'folder '
                                                                                                           'contains '
                                                                                                           'additional '
                                                                                                           'files. '
                                                                                                           'Extract '
                                                                                                           'the '
                                                                                                           'package '
                                                                                                           'manually '
                                                                                                           'into '
                                                                                                           'its '
                                                                                                           'own '
                                                                                                           'app '
                                                                                                           'folder.',
 'Der Browser konnte nicht geöffnet werden. Bitte einen Standardbrowser einrichten.': 'Could not open the '
                                                                                      'browser. Configure a '
                                                                                      'default browser.',
 'Der Client-Download ist beschädigt. Bitte erneut herunterladen.': 'The client download is corrupted. Download '
                                                                    'it again.',
 'Der Datenordner liegt im App-Ordner. Bitte das Update manuell installieren, damit deine Spieldaten erhalten bleiben.': 'The '
                                                                                                                         'data '
                                                                                                                         'folder '
                                                                                                                         'is '
                                                                                                                         'inside '
                                                                                                                         'the '
                                                                                                                         'app '
                                                                                                                         'folder. '
                                                                                                                         'Install '
                                                                                                                         'the '
                                                                                                                         'update '
                                                                                                                         'manually '
                                                                                                                         'to '
                                                                                                                         'preserve '
                                                                                                                         'your '
                                                                                                                         'game '
                                                                                                                         'data.',
 'Der Minecraft-Client wurde nicht vollständig heruntergeladen. Bitte erneut versuchen.': 'The Minecraft client '
                                                                                          'download is '
                                                                                          'incomplete. Try again.',
 'Der Online-Dienst ist nicht erreichbar oder hat die Anfrage abgelehnt. Prüfe deine Internetverbindung und versuche es erneut.': 'The '
                                                                                                                                  'online '
                                                                                                                                  'service '
                                                                                                                                  'is '
                                                                                                                                  'unavailable '
                                                                                                                                  'or '
                                                                                                                                  'rejected '
                                                                                                                                  'the '
                                                                                                                                  'request. '
                                                                                                                                  'Check '
                                                                                                                                  'your '
                                                                                                                                  'internet '
                                                                                                                                  'connection '
                                                                                                                                  'and '
                                                                                                                                  'try '
                                                                                                                                  'again.',
 'Der Port muss eine Zahl sein.': 'The port must be a number.',
 'Der Port muss zwischen 1 und 65535 liegen.': 'The port must be between 1 and 65535.',
 'Der Schlüsselbund konnte die Anmeldung nicht entfernen. Bitte entsperren und erneut abmelden.': 'The keychain '
                                                                                                  'could not '
                                                                                                  'remove the '
                                                                                                  'sign-in. '
                                                                                                  'Unlock it and '
                                                                                                  'sign out '
                                                                                                  'again.',
 'Der Standardbrowser konnte nicht geöffnet werden.': 'The default browser could not be opened.',
 'Der Versionskatalog enthält keine gültigen Releases.': 'The version catalog contains no valid releases.',
 'Der Vorgang konnte nicht abgeschlossen werden (': 'The task could not be completed (',
 'Der Weltordner ist nicht mehr vorhanden.': 'The world folder no longer exists.',
 'Der Zielordner darf nicht innerhalb der Quellwelt liegen.': 'The destination folder must not be inside the '
                                                              'source world.',
 'Der alte 64 × 32-Skin unterstützt nur breite Arme.': 'The legacy 64 × 32 skin only supports wide arms.',
 'Der lokale Kanal liest Blockwerk-Updates.json und das passende Paket aus dem Ausgabeordner. Ein Update ist erst verfügbar, wenn dort eine neue Launcher-Ausgabe veröffentlicht wurde.': 'The '
                                                                                                                                                                                          'local '
                                                                                                                                                                                          'channel '
                                                                                                                                                                                          'reads '
                                                                                                                                                                                          'Blockwerk-Updates.json '
                                                                                                                                                                                          'and '
                                                                                                                                                                                          'the '
                                                                                                                                                                                          'matching '
                                                                                                                                                                                          'package '
                                                                                                                                                                                          'from '
                                                                                                                                                                                          'the '
                                                                                                                                                                                          'output '
                                                                                                                                                                                          'folder. '
                                                                                                                                                                                          'An '
                                                                                                                                                                                          'update '
                                                                                                                                                                                          'is '
                                                                                                                                                                                          'available '
                                                                                                                                                                                          'only '
                                                                                                                                                                                          'after '
                                                                                                                                                                                          'a '
                                                                                                                                                                                          'new '
                                                                                                                                                                                          'launcher '
                                                                                                                                                                                          'release '
                                                                                                                                                                                          'has '
                                                                                                                                                                                          'been '
                                                                                                                                                                                          'published '
                                                                                                                                                                                          'there.',
 'Der lokale Spielername braucht 3–16 Zeichen: Buchstaben, Ziffern oder Unterstriche.': 'The local player name '
                                                                                        'must contain 3–16 '
                                                                                        'letters, numbers or '
                                                                                        'underscores.',
 'Der lokale Spielername dieses Spielordners ist ungültig.': 'The local player name for this game folder is '
                                                             'invalid.',
 'Die Anleitung liegt neben dem Projekt: EINRICHTUNG.md\n\nRegistriere eine Public-Client-App für persönliche Microsoft-Konten. Redirect-URI: ': 'The '
                                                                                                                                                 'guide '
                                                                                                                                                 'is '
                                                                                                                                                 'next '
                                                                                                                                                 'to '
                                                                                                                                                 'the '
                                                                                                                                                 'project: '
                                                                                                                                                 'EINRICHTUNG.md\n'
                                                                                                                                                 '\n'
                                                                                                                                                 'Register '
                                                                                                                                                 'a '
                                                                                                                                                 'public-client '
                                                                                                                                                 'app '
                                                                                                                                                 'for '
                                                                                                                                                 'personal '
                                                                                                                                                 'Microsoft '
                                                                                                                                                 'accounts. '
                                                                                                                                                 'Redirect '
                                                                                                                                                 'URI: ',
 'Die Anmeldung gilt nur für diese Sitzung, weil kein sicherer Kontospeicher verfügbar ist.': 'Sign-in lasts for '
                                                                                              'this session only '
                                                                                              'because secure '
                                                                                              'account storage is '
                                                                                              'unavailable.',
 'Die App-Kennung ist hinterlegt. Ob Microsoft/Minecraft diese Registrierung freigegeben hat, zeigt sich erst beim echten Login. Klicke unten, um die Anmeldung im Browser zu starten.': 'The '
                                                                                                                                                                                         'app '
                                                                                                                                                                                         'ID '
                                                                                                                                                                                         'is '
                                                                                                                                                                                         'configured. '
                                                                                                                                                                                         'Actual '
                                                                                                                                                                                         'sign-in '
                                                                                                                                                                                         'will '
                                                                                                                                                                                         'determine '
                                                                                                                                                                                         'whether '
                                                                                                                                                                                         'Microsoft/Minecraft '
                                                                                                                                                                                         'has '
                                                                                                                                                                                         'approved '
                                                                                                                                                                                         'this '
                                                                                                                                                                                         'registration. '
                                                                                                                                                                                         'Click '
                                                                                                                                                                                         'below '
                                                                                                                                                                                         'to '
                                                                                                                                                                                         'sign '
                                                                                                                                                                                         'in '
                                                                                                                                                                                         'through '
                                                                                                                                                                                         'your '
                                                                                                                                                                                         'browser.',
 'Die Launcher-Konfiguration launcher-auth.json ist ungültig. Bitte eine korrigierte Ausgabe von Blockwerk verwenden.': 'The '
                                                                                                                        'launcher-auth.json '
                                                                                                                        'configuration '
                                                                                                                        'is '
                                                                                                                        'invalid. '
                                                                                                                        'Use '
                                                                                                                        'a '
                                                                                                                        'corrected '
                                                                                                                        'Blockwerk '
                                                                                                                        'release.',
 'Die Liste zusätzlicher Weltordner ist beschädigt.': 'The list of additional world folders is corrupted.',
 'Die Microsoft-Anmeldung wartet auf die Registrierung und Freigabe des Launchers durch den Projektbetreiber.': 'Microsoft '
                                                                                                                'sign-in '
                                                                                                                'is '
                                                                                                                'waiting '
                                                                                                                'for '
                                                                                                                'the '
                                                                                                                'project '
                                                                                                                'operator '
                                                                                                                'to '
                                                                                                                'register '
                                                                                                                'and '
                                                                                                                'obtain '
                                                                                                                'approval '
                                                                                                                'for '
                                                                                                                'this '
                                                                                                                'launcher.',
 'Die Microsoft-Anmeldung wurde abgelehnt oder abgebrochen.': 'Microsoft sign-in was denied or canceled.',
 'Die Minecraft-Anmeldung ist abgelaufen. Bitte erneut anmelden.': 'Minecraft sign-in expired. Sign in again.',
 'Die Paketbeschreibung ist zu groß.': 'The package manifest is too large.',
 'Die Prüfsumme des Minecraft-Clients stimmt nicht. Bitte erneut starten, um den Download zu reparieren.': 'The '
                                                                                                           'Minecraft '
                                                                                                           'client '
                                                                                                           'checksum '
                                                                                                           'does '
                                                                                                           'not '
                                                                                                           'match. '
                                                                                                           'Launch '
                                                                                                           'again '
                                                                                                           'to '
                                                                                                           'repair '
                                                                                                           'the '
                                                                                                           'download.',
 'Die Prüfung läuft beim Start oder während der Nutzung, sobald sieben Tage vergangen sind und der Launcher frei ist. Eine geschlossene App wird nicht aufgeweckt. Ein Neustart zur Installation erfolgt erst über den Knopf unten.': 'Checks '
                                                                                                                                                                                                                                      'run '
                                                                                                                                                                                                                                      'at '
                                                                                                                                                                                                                                      'startup '
                                                                                                                                                                                                                                      'or '
                                                                                                                                                                                                                                      'during '
                                                                                                                                                                                                                                      'use '
                                                                                                                                                                                                                                      'when '
                                                                                                                                                                                                                                      'seven '
                                                                                                                                                                                                                                      'days '
                                                                                                                                                                                                                                      'have '
                                                                                                                                                                                                                                      'passed '
                                                                                                                                                                                                                                      'and '
                                                                                                                                                                                                                                      'the '
                                                                                                                                                                                                                                      'launcher '
                                                                                                                                                                                                                                      'is '
                                                                                                                                                                                                                                      'idle. '
                                                                                                                                                                                                                                      'A '
                                                                                                                                                                                                                                      'closed '
                                                                                                                                                                                                                                      'app '
                                                                                                                                                                                                                                      'is '
                                                                                                                                                                                                                                      'not '
                                                                                                                                                                                                                                      'awakened. '
                                                                                                                                                                                                                                      'Installation '
                                                                                                                                                                                                                                      'restarts '
                                                                                                                                                                                                                                      'the '
                                                                                                                                                                                                                                      'launcher '
                                                                                                                                                                                                                                      'only '
                                                                                                                                                                                                                                      'after '
                                                                                                                                                                                                                                      'you '
                                                                                                                                                                                                                                      'click '
                                                                                                                                                                                                                                      'the '
                                                                                                                                                                                                                                      'button '
                                                                                                                                                                                                                                      'below.',
 'Die Ressourcenpaket-Auswahl in options.txt ist nicht lesbar. Bitte zuerst im Spiel prüfen.': 'The resource pack '
                                                                                               'selection in '
                                                                                               'options.txt '
                                                                                               'cannot be read. '
                                                                                               'Check it in the '
                                                                                               'game first.',
 'Die Server-Importhistorie ist beschädigt. Die Minecraft-Serverliste bleibt erhalten.': 'The server import '
                                                                                         'history is corrupted. '
                                                                                         'The Minecraft server '
                                                                                         'list is kept.',
 'Die Serverliste muss eine Liste sein.': 'Server data must be a list.',
 'Die Skin-PNG konnte nicht gelesen werden.': 'Could not read the skin PNG.',
 'Die Skin-PNG konnte nicht gespeichert werden.': 'Could not save the skin PNG.',
 'Die Spieldateien fehlen oder wurden verändert. Bitte mit Internet auf ‚Spieldateien herunterladen‘ klicken. Eine Microsoft-Anmeldung ist dafür nicht nötig.': 'Game '
                                                                                                                                                                'files '
                                                                                                                                                                'are '
                                                                                                                                                                'missing '
                                                                                                                                                                'or '
                                                                                                                                                                'have '
                                                                                                                                                                'changed. '
                                                                                                                                                                'Connect '
                                                                                                                                                                'to '
                                                                                                                                                                'the '
                                                                                                                                                                'internet '
                                                                                                                                                                'and '
                                                                                                                                                                'click '
                                                                                                                                                                "'Download "
                                                                                                                                                                'game '
                                                                                                                                                                "files'. "
                                                                                                                                                                'No '
                                                                                                                                                                'Microsoft '
                                                                                                                                                                'sign-in '
                                                                                                                                                                'is '
                                                                                                                                                                'required.',
 'Die Update-Paketliste ist ungültig.': 'The update package list is invalid.',
 'Die Update-Prüfsumme stimmt nicht. Das Paket wird nicht installiert.': 'The update checksum does not match. The '
                                                                         'package will not be installed.',
 'Die Update-Version ist ungültig.': 'Invalid update version.',
 'Die Updateadresse ist ungültig.': 'Invalid update address.',
 'Die Updatebeschreibung ist keine gültige JSON-Datei.': 'The update manifest is not valid JSON.',
 'Die Updatebeschreibung ist zu groß.': 'The update manifest is too large.',
 'Die Updategröße ist ungültig oder zu groß.': 'The update size is invalid or too large.',
 'Die Zieldatei existiert bereits.': 'The destination file already exists.',
 'Die ausgewählte Welt liegt nicht im Spielordner.': 'The selected world is not in the game folder.',
 'Die gespeicherte Anmeldung ist abgelaufen. Bitte abmelden und erneut bei Microsoft anmelden.': 'The saved '
                                                                                                 'sign-in has '
                                                                                                 'expired. Sign '
                                                                                                 'out and sign in '
                                                                                                 'with Microsoft '
                                                                                                 'again.',
 'Die gespeicherte Anmeldung ist nicht verfügbar. Bitte abmelden und erneut anmelden.': 'Saved sign-in is '
                                                                                        'unavailable. Sign out '
                                                                                        'and sign in again.',
 'Die gespeicherte Serverliste ist beschädigt.': 'The saved server list is corrupted.',
 'Die gespeicherte Skin-Auswahl ist beschädigt.': 'The saved skin selection is corrupted.',
 'Die gewählte Java-Datei ist nicht ausführbar.': 'The selected Java file is not executable.',
 'Die lokale Updatequelle ist nicht erreichbar. Bitte den Updateordner prüfen oder neu auswählen.': 'The local '
                                                                                                    'update '
                                                                                                    'source is '
                                                                                                    'unavailable. '
                                                                                                    'Check or '
                                                                                                    'reselect the '
                                                                                                    'update '
                                                                                                    'folder.',
 'Die mitgelieferte Updatequelle ist ungültig.': 'The bundled update source is invalid.',
 'Die sichere Kontospeicherung benötigt Windows.': 'Secure account storage requires Windows.',
 'Die vorhandene servers.dat ist nicht lesbar. Sie wird nicht überschrieben; bitte im Spiel prüfen.': 'The '
                                                                                                      'existing '
                                                                                                      'servers.dat '
                                                                                                      'cannot be '
                                                                                                      'read. It '
                                                                                                      'will not '
                                                                                                      'be '
                                                                                                      'overwritten; '
                                                                                                      'check it '
                                                                                                      'in the '
                                                                                                      'game.',
 'Diese Anmeldung ist abgelaufen oder wurde bereits verwendet. Bitte starte die Microsoft-Anmeldung erneut.': 'This '
                                                                                                              'sign-in '
                                                                                                              'has '
                                                                                                              'expired '
                                                                                                              'or '
                                                                                                              'was '
                                                                                                              'already '
                                                                                                              'used. '
                                                                                                              'Start '
                                                                                                              'Microsoft '
                                                                                                              'sign-in '
                                                                                                              'again.',
 'Diese Datei ist keine gültige PNG-Skin-Datei.': 'This file is not a valid skin PNG.',
 'Diese Loader-Version ist nicht verfügbar. Bitte Versionen neu laden.': 'This loader version is unavailable. '
                                                                         'Reload the versions.',
 'Diese Mod-Datei existiert bereits: ': 'This mod file already exists: ',
 'Diese Serveradresse ist bereits gespeichert.': 'This server address is already saved.',
 'Diese Version auswählen →': 'Select this version →',
 'Diese Version oder Java-Laufzeit ist auf den Downloadservern nicht verfügbar.': 'This version or Java runtime '
                                                                                  'is unavailable on the download '
                                                                                  'servers.',
 'Diese Version unterstützt keinen direkten Weltstart. Öffne Einzelspieler und wähle die Welt im Spiel aus.': 'This '
                                                                                                              'version '
                                                                                                              'does '
                                                                                                              'not '
                                                                                                              'support '
                                                                                                              'launching '
                                                                                                              'a '
                                                                                                              'world '
                                                                                                              'directly. '
                                                                                                              'Open '
                                                                                                              'Singleplayer '
                                                                                                              'and '
                                                                                                              'select '
                                                                                                              'the '
                                                                                                              'world '
                                                                                                              'in '
                                                                                                              'the '
                                                                                                              'game.',
 'Diese Welt enthält eine Verknüpfung. Bitte eine vollständige Weltkopie ohne Verknüpfungen auswählen.': 'This '
                                                                                                         'world '
                                                                                                         'contains '
                                                                                                         'a link. '
                                                                                                         'Select '
                                                                                                         'a '
                                                                                                         'complete '
                                                                                                         'world '
                                                                                                         'copy '
                                                                                                         'without '
                                                                                                         'links.',
 'Diese Welt ist nicht mehr verfügbar oder muss in Minecraft wiederhergestellt werden.': 'This world is '
                                                                                         'unavailable or must be '
                                                                                         'restored in Minecraft.',
 'Diese Welt ist noch geöffnet oder gesperrt. Schließe Minecraft, bevor du eine Spielkopie erstellst.': 'This '
                                                                                                        'world is '
                                                                                                        'open or '
                                                                                                        'locked. '
                                                                                                        'Close '
                                                                                                        'Minecraft '
                                                                                                        'before '
                                                                                                        'creating '
                                                                                                        'a play '
                                                                                                        'copy.',
 'Diese installierte Version wurde nicht gefunden.': 'This installed version was not found.',
 'Dieser App-Ordner ist kein unterstütztes Blockwerk-Paket.': 'This app folder is not a supported Blockwerk '
                                                              'package.',
 'Dieser Server ist nicht mehr vorhanden.': 'This server no longer exists.',
 'Dieser Skin ist nicht mehr vorhanden.': 'This skin no longer exists.',
 'Dieser Spielername ist als Ordnername reserviert. Bitte einen anderen wählen.': 'This player name is reserved '
                                                                                  'as a folder name. Choose '
                                                                                  'another name.',
 'Dieses Konto besitzt keine nutzbare Minecraft-Java-Lizenz. Prüfe Kauf oder Game Pass im offiziellen Launcher.': 'This '
                                                                                                                  'account '
                                                                                                                  'has '
                                                                                                                  'no '
                                                                                                                  'usable '
                                                                                                                  'Minecraft '
                                                                                                                  'Java '
                                                                                                                  'license. '
                                                                                                                  'Check '
                                                                                                                  'your '
                                                                                                                  'purchase '
                                                                                                                  'or '
                                                                                                                  'Game '
                                                                                                                  'Pass '
                                                                                                                  'in '
                                                                                                                  'the '
                                                                                                                  'official '
                                                                                                                  'launcher.',
 'Dieses Microsoft-Konto hat kein Minecraft-Java-Profil. Prüfe Lizenz und Konto im offiziellen Launcher.': 'This '
                                                                                                           'Microsoft '
                                                                                                           'account '
                                                                                                           'has '
                                                                                                           'no '
                                                                                                           'Minecraft '
                                                                                                           'Java '
                                                                                                           'profile. '
                                                                                                           'Check '
                                                                                                           'your '
                                                                                                           'license '
                                                                                                           'and '
                                                                                                           'account '
                                                                                                           'in '
                                                                                                           'the '
                                                                                                           'official '
                                                                                                           'launcher.',
 'Dieses Mod-Profil ist beschädigt.': 'This mod profile is corrupted.',
 'Dieses Mod-Profil ist noch nicht installiert. Bitte unter Mods installieren.': 'This mod profile is not '
                                                                                 'installed yet. Install it under '
                                                                                 'Mods.',
 'Dieses Updateformat wird nicht unterstützt.': 'This update format is not supported.',
 'Download abgebrochen.': 'Download canceled.',
 'Download verfügbar': 'Download available',
 'Downloadordner öffnen ↗': 'Open download folder ↗',
 'Du verwendest die aktuelle Launcher-Version': 'You are using the latest launcher version',
 'E-Mail, Passwort und Bestätigungscodes gibst du ausschließlich auf Microsofts Website ein. Blockwerk erhält danach die Anmeldeberechtigung und prüft dein Minecraft-Java-Profil. Ein neues Microsoft-Konto enthält nicht automatisch Minecraft Java.': 'Enter '
                                                                                                                                                                                                                                                         'your '
                                                                                                                                                                                                                                                         'email, '
                                                                                                                                                                                                                                                         'password '
                                                                                                                                                                                                                                                         'and '
                                                                                                                                                                                                                                                         'verification '
                                                                                                                                                                                                                                                         'codes '
                                                                                                                                                                                                                                                         'only '
                                                                                                                                                                                                                                                         'on '
                                                                                                                                                                                                                                                         "Microsoft's "
                                                                                                                                                                                                                                                         'website. '
                                                                                                                                                                                                                                                         'Blockwerk '
                                                                                                                                                                                                                                                         'then '
                                                                                                                                                                                                                                                         'receives '
                                                                                                                                                                                                                                                         'authorization '
                                                                                                                                                                                                                                                         'and '
                                                                                                                                                                                                                                                         'checks '
                                                                                                                                                                                                                                                         'your '
                                                                                                                                                                                                                                                         'Minecraft '
                                                                                                                                                                                                                                                         'Java '
                                                                                                                                                                                                                                                         'profile. '
                                                                                                                                                                                                                                                         'A '
                                                                                                                                                                                                                                                         'new '
                                                                                                                                                                                                                                                         'Microsoft '
                                                                                                                                                                                                                                                         'account '
                                                                                                                                                                                                                                                         'does '
                                                                                                                                                                                                                                                         'not '
                                                                                                                                                                                                                                                         'automatically '
                                                                                                                                                                                                                                                         'include '
                                                                                                                                                                                                                                                         'Minecraft '
                                                                                                                                                                                                                                                         'Java.',
 'EINRICHTUNG AUSSTEHEND': 'SETUP PENDING',
 'EXE-Installer laufen nur unter Windows.': 'EXE installers only run on Windows.',
 'Eigene Java-Datei (optional)': 'Custom Java executable (optional)',
 'Eigene Mod-Profile mit getrennten Welten.': 'Your own mod profiles with separate worlds.',
 'Eigene Skin-PNGs hinzufügen oder einen der originalen Blockwerk-Skins auswählen. Die Vorschau lässt sich mit der Maus drehen.': 'Add '
                                                                                                                                  'your '
                                                                                                                                  'own '
                                                                                                                                  'skin '
                                                                                                                                  'PNGs '
                                                                                                                                  'or '
                                                                                                                                  'choose '
                                                                                                                                  'an '
                                                                                                                                  'original '
                                                                                                                                  'Blockwerk '
                                                                                                                                  'skin. '
                                                                                                                                  'Drag '
                                                                                                                                  'the '
                                                                                                                                  'preview '
                                                                                                                                  'to '
                                                                                                                                  'rotate '
                                                                                                                                  'it.',
 'Eigenen Installer öffnen …': 'Open custom installer …',
 'Eigenen JAR-/EXE-Installer manuell ausführen. Im Installer den unten gezeigten Minecraft-Zielordner wählen. Danach die installierte Version suchen und übernehmen. Die Unterstützung hängt vom Dateiformat und Installer ab.': 'Run '
                                                                                                                                                                                                                                 'your '
                                                                                                                                                                                                                                 'own '
                                                                                                                                                                                                                                 'JAR/EXE '
                                                                                                                                                                                                                                 'installer '
                                                                                                                                                                                                                                 'manually. '
                                                                                                                                                                                                                                 'In '
                                                                                                                                                                                                                                 'the '
                                                                                                                                                                                                                                 'installer, '
                                                                                                                                                                                                                                 'select '
                                                                                                                                                                                                                                 'the '
                                                                                                                                                                                                                                 'Minecraft '
                                                                                                                                                                                                                                 'destination '
                                                                                                                                                                                                                                 'folder '
                                                                                                                                                                                                                                 'shown '
                                                                                                                                                                                                                                 'below. '
                                                                                                                                                                                                                                 'Then '
                                                                                                                                                                                                                                 'search '
                                                                                                                                                                                                                                 'for '
                                                                                                                                                                                                                                 'and '
                                                                                                                                                                                                                                 'use '
                                                                                                                                                                                                                                 'the '
                                                                                                                                                                                                                                 'installed '
                                                                                                                                                                                                                                 'version. '
                                                                                                                                                                                                                                 'Support '
                                                                                                                                                                                                                                 'depends '
                                                                                                                                                                                                                                 'on '
                                                                                                                                                                                                                                 'the '
                                                                                                                                                                                                                                 'file '
                                                                                                                                                                                                                                 'format '
                                                                                                                                                                                                                                 'and '
                                                                                                                                                                                                                                 'installer.',
 'Ein Download war unvollständig. Bitte erneut starten; die Installation wird geprüft.': 'A download was '
                                                                                         'incomplete. Launch '
                                                                                         'again to verify the '
                                                                                         'installation.',
 'Ein Downloadpfad wurde aus Sicherheitsgründen abgelehnt.': 'A download path was rejected for security reasons.',
 'Ein Servername muss 1–80 sichtbare Zeichen haben.': 'A server name must contain 1–80 visible characters.',
 'Ein Zuhause je Version': 'A home for every version',
 'Ein eigener Weg zu Minecraft Java.': 'Your own way to Minecraft Java.',
 'Eine Spielkopie der Welt wird erstellt. Das Original bleibt erhalten …': 'Creating a play copy of the world. '
                                                                           'The original is kept …',
 'Eine Welt auswählen oder ‚Neue Welt in Minecraft‘ verwenden.': "Select a world or use 'New world in Minecraft'.",
 'Eine laufende Anfrage wird noch abgeschlossen. Ihre Antwort wird danach verworfen; es wird keine neue Anmeldung gespeichert.': 'The '
                                                                                                                                 'current '
                                                                                                                                 'request '
                                                                                                                                 'is '
                                                                                                                                 'finishing. '
                                                                                                                                 'Its '
                                                                                                                                 'response '
                                                                                                                                 'will '
                                                                                                                                 'be '
                                                                                                                                 'discarded; '
                                                                                                                                 'no '
                                                                                                                                 'new '
                                                                                                                                 'sign-in '
                                                                                                                                 'will '
                                                                                                                                 'be '
                                                                                                                                 'saved.',
 'Einrichtung für Projektbetreiber →': 'Setup for project operators →',
 'Einrichtung für Projektbetreiber ▾': 'Setup for project operators ▾',
 'Einstellungen': 'Settings',
 'Einstellungen gespeichert.': 'Settings saved.',
 'Einstellungen prüfen': 'Check settings',
 'Einstellungen speichern': 'Save settings',
 'Einzelspieler': 'Singleplayer',
 'Entfernen': 'Remove',
 'Erneut mit Microsoft anmelden ↗': 'Sign in with Microsoft again ↗',
 'Es steht kein passendes neues Update bereit.': 'No matching new update is available.',
 'Fabric hat kein passendes Launcher-Profil geliefert.': 'Fabric did not return a matching launcher profile.',
 'Fabric, Forge, Quilt und NeoForge: Installation mit passenden Versionen geprüft. Für andere Installer ‚Eigener Installer‘ wählen. Die Installation benötigt Internet; bestehende Profile lassen sich lokal starten.': 'Fabric, '
                                                                                                                                                                                                                        'Forge, '
                                                                                                                                                                                                                        'Quilt '
                                                                                                                                                                                                                        'and '
                                                                                                                                                                                                                        'NeoForge: '
                                                                                                                                                                                                                        'installation '
                                                                                                                                                                                                                        'tested '
                                                                                                                                                                                                                        'with '
                                                                                                                                                                                                                        'compatible '
                                                                                                                                                                                                                        'versions. '
                                                                                                                                                                                                                        'For '
                                                                                                                                                                                                                        'other '
                                                                                                                                                                                                                        'installers, '
                                                                                                                                                                                                                        'choose '
                                                                                                                                                                                                                        "'Custom "
                                                                                                                                                                                                                        "installer'. "
                                                                                                                                                                                                                        'Installation '
                                                                                                                                                                                                                        'requires '
                                                                                                                                                                                                                        'internet; '
                                                                                                                                                                                                                        'existing '
                                                                                                                                                                                                                        'profiles '
                                                                                                                                                                                                                        'can '
                                                                                                                                                                                                                        'launch '
                                                                                                                                                                                                                        'locally.',
 'Für den Online-Modus brauchst du ein Microsoft-Konto mit Minecraft-Java-Berechtigung und eine freigegebene App-ID. Offline kannst du ein lokales Profil ohne Microsoft-Konto verwenden. Das ist keine Online-Identität und funktioniert nicht als Anmeldung für kontogeprüfte Server oder Realms.': 'Online '
                                                                                                                                                                                                                                                                                                      'mode '
                                                                                                                                                                                                                                                                                                      'requires '
                                                                                                                                                                                                                                                                                                      'a '
                                                                                                                                                                                                                                                                                                      'Microsoft '
                                                                                                                                                                                                                                                                                                      'account '
                                                                                                                                                                                                                                                                                                      'with '
                                                                                                                                                                                                                                                                                                      'Minecraft '
                                                                                                                                                                                                                                                                                                      'Java '
                                                                                                                                                                                                                                                                                                      'access '
                                                                                                                                                                                                                                                                                                      'and '
                                                                                                                                                                                                                                                                                                      'an '
                                                                                                                                                                                                                                                                                                      'approved '
                                                                                                                                                                                                                                                                                                      'app '
                                                                                                                                                                                                                                                                                                      'ID. '
                                                                                                                                                                                                                                                                                                      'Offline '
                                                                                                                                                                                                                                                                                                      'mode '
                                                                                                                                                                                                                                                                                                      'uses '
                                                                                                                                                                                                                                                                                                      'a '
                                                                                                                                                                                                                                                                                                      'local '
                                                                                                                                                                                                                                                                                                      'profile '
                                                                                                                                                                                                                                                                                                      'without '
                                                                                                                                                                                                                                                                                                      'a '
                                                                                                                                                                                                                                                                                                      'Microsoft '
                                                                                                                                                                                                                                                                                                      'account. '
                                                                                                                                                                                                                                                                                                      'It '
                                                                                                                                                                                                                                                                                                      'cannot '
                                                                                                                                                                                                                                                                                                      'authenticate '
                                                                                                                                                                                                                                                                                                      'with '
                                                                                                                                                                                                                                                                                                      'account-verified '
                                                                                                                                                                                                                                                                                                      'servers '
                                                                                                                                                                                                                                                                                                      'or '
                                                                                                                                                                                                                                                                                                      'Realms.',
 'Für diese Minecraft-Version wurden keine unterstützten Standard-Skin-Texturen gefunden.': 'No supported default '
                                                                                            'skin textures were '
                                                                                            'found for this '
                                                                                            'Minecraft version.',
 'Für eigene Installer erst ein Profil erstellen, dann die lokale Installer-Datei öffnen.': 'For custom '
                                                                                            'installers, create a '
                                                                                            'profile first, then '
                                                                                            'open the local '
                                                                                            'installer file.',
 'Gespeicherte Server · ohne Launcher-Limit': 'Saved servers · no launcher limit',
 'Gewählte Spielversion: ': 'Selected game version: ',
 'Gewähltes Spielprofil: ': 'Selected game profile: ',
 'HTTPS-Updatekanal': 'HTTPS update channel',
 'HTTPS-Updatequelle speichern': 'Save HTTPS update source',
 'Herkunft': 'Source',
 'Hier erscheinen Anmeldung, Downloads und Spielstatus.': 'Sign-in, downloads and game status appear here.',
 'Hinweis': 'Note',
 'Hinzufügen': 'Add',
 'INSTALLIERT · ': 'INSTALLED · ',
 'IPv6-Adressen bitte in eckige Klammern setzen.': 'Put IPv6 addresses in square brackets.',
 'Im Browser fortfahren': 'Continue in browser',
 'Im Installer diesen Minecraft-Ordner auswählen:\n\n': 'Select this Minecraft folder in the installer:\n\n',
 'Im Microsoft-Konto anwenden': 'Apply to Microsoft account',
 'Im Updatepaket fehlen App-Dateien.': 'The update package is missing app files.',
 'Im lokalen Spiel anzeigen': 'Show in local game',
 'In Minecraft ‚Einzelspieler‘ → ‚Neue Welt erstellen‘ wählen. Minecraft erzeugt die neue Welt mit deinen Einstellungen.': 'In '
                                                                                                                           'Minecraft, '
                                                                                                                           'choose '
                                                                                                                           "'Singleplayer' "
                                                                                                                           '→ '
                                                                                                                           "'Create "
                                                                                                                           'New '
                                                                                                                           "World'. "
                                                                                                                           'Minecraft '
                                                                                                                           'creates '
                                                                                                                           'the '
                                                                                                                           'world '
                                                                                                                           'using '
                                                                                                                           'your '
                                                                                                                           'settings.',
 'In gewählter Version spielen …': 'Play in selected version …',
 'Installation unvollständig. Bitte im Online-Modus erneut starten: ': 'Installation incomplete. Launch again in '
                                                                       'online mode: ',
 'Installer beendet (Code ': 'Installer finished (code ',
 'Installer-Zielordner': 'Installer destination folder',
 'Installieren & Launcher neu starten': 'Install & restart launcher',
 'Installiert': 'Installed',
 'Installierte Version übernehmen': 'Use installed version',
 'Java (java);;Alle Dateien (*)': 'Java (java);;All files (*)',
 'Java auswählen': 'Select Java',
 'Java-Skin-PNGs auswählen': 'Select Java skin PNGs',
 'Java-Skins müssen 64 × 64 oder 64 × 32 Pixel groß sein.': 'Java skins must be 64 × 64 or 64 × 32 pixels.',
 'Jede Version hat ihren eigenen Spielordner.': 'Each version has its own game folder.',
 'Jetzt prüfen': 'Check now',
 'KONTO VERBUNDEN': 'ACCOUNT CONNECTED',
 'Kein Java für den Installer verfügbar.': 'No Java runtime available for the installer.',
 'Kein Schreibzugriff. Prüfe den Blockwerk-Datenordner und freien Speicherplatz.': 'Write access denied. Check '
                                                                                   'the Blockwerk data folder and '
                                                                                   'available disk space.',
 'Kein lokaler Versionskatalog. Bitte einmal im Online-Modus aktualisieren.': 'No local version catalog. Refresh '
                                                                              'once in online mode.',
 'Kein nativer Schlüsselbund verfügbar.': 'No native keychain available.',
 'Kein passendes Java verfügbar. Bitte unter Einstellungen auswählen.': 'No matching Java runtime available. '
                                                                        'Select one under Settings.',
 'Keine Einträge – Versionsliste aktualisieren': 'No entries – refresh the version list',
 'Keine Versionen geladen': 'No versions loaded',
 'Keine Versionen. Nutze Aktualisieren, sobald du online bist.': 'No versions. Use Refresh when you are online.',
 'Keine lesbare Mod-JAR oder ungültige Metadaten: ': 'Unreadable mod JAR or invalid metadata: ',
 'Kompatibilität': 'Compatibility',
 'Konto verwalten': 'Manage account',
 'Kontoseite öffnen →': 'Open account page →',
 'Kreativ': 'Creative',
 'Launcher jede Woche auf neue Versionen prüfen': 'Check for launcher updates every week',
 'Launcher schließen und den aktuellen Vorgang abbrechen? Fehlende Downloads werden beim nächsten Start repariert.': 'Close '
                                                                                                                     'the '
                                                                                                                     'launcher '
                                                                                                                     'and '
                                                                                                                     'cancel '
                                                                                                                     'the '
                                                                                                                     'current '
                                                                                                                     'task? '
                                                                                                                     'Missing '
                                                                                                                     'downloads '
                                                                                                                     'will '
                                                                                                                     'be '
                                                                                                                     'repaired '
                                                                                                                     'on '
                                                                                                                     'the '
                                                                                                                     'next '
                                                                                                                     'launch.',
 'Launcher-Einrichtung fehlt': 'Launcher setup missing',
 'Launcher-Update heruntergeladen; Größe und SHA256 sind geprüft.': 'Launcher update downloaded; size and SHA256 '
                                                                    'verified.',
 'Launcher-Update wird heruntergeladen und geprüft …': 'Downloading and verifying launcher update …',
 'Launcher-Updates': 'Launcher updates',
 'Leer lassen für automatische Installation. Ein eigener Pfad gilt für alle Versionen und muss zur gewählten Version passen.': 'Leave '
                                                                                                                               'empty '
                                                                                                                               'for '
                                                                                                                               'automatic '
                                                                                                                               'installation. '
                                                                                                                               'A '
                                                                                                                               'custom '
                                                                                                                               'path '
                                                                                                                               'applies '
                                                                                                                               'to '
                                                                                                                               'all '
                                                                                                                               'versions '
                                                                                                                               'and '
                                                                                                                               'must '
                                                                                                                               'match '
                                                                                                                               'the '
                                                                                                                               'selected '
                                                                                                                               'version.',
 'Loader': 'Loader',
 'Loader-Installation abgebrochen.': 'Loader installation canceled.',
 'Lokal abgemeldet. Deine Minecraft-Dateien und Welten bleiben erhalten.': 'Signed out locally. Your Minecraft '
                                                                           'files and worlds are kept.',
 'Lokal spielen →': 'Play locally →',
 'Lokale Dateien werden für den Offline-Modus geprüft …': 'Checking local files for offline mode …',
 'Lokale Minecraft-Java-Welten werden gesucht …': 'Searching for local Minecraft Java worlds …',
 'Lokalen Installer auswählen': 'Select local installer',
 'Lokalen Updateordner wählen …': 'Choose local update folder …',
 'Lokaler Release-Katalog geladen. Vorbereitete Versionen sind offline startbar.': 'Local release catalog loaded. '
                                                                                   'Prepared versions can launch '
                                                                                   'offline.',
 'Lokaler Spielername': 'Local player name',
 'Lokaler Updatekanal': 'Local update channel',
 'Lokaler Versionskatalog wird geladen …': 'Loading local version catalog …',
 'Lokales Profil ohne Microsoft-Anmeldung. Nur für Server, deren Betreiber lokale Profile zulässt. Keine Anmeldung für kontogeprüfte Server oder Realms. Füge beliebig viele Favoriten hinzu oder speichere Server direkt im Minecraft-Menü Mehrspieler.': 'Local '
                                                                                                                                                                                                                                                           'profile '
                                                                                                                                                                                                                                                           'without '
                                                                                                                                                                                                                                                           'Microsoft '
                                                                                                                                                                                                                                                           'sign-in. '
                                                                                                                                                                                                                                                           'Only '
                                                                                                                                                                                                                                                           'for '
                                                                                                                                                                                                                                                           'servers '
                                                                                                                                                                                                                                                           'that '
                                                                                                                                                                                                                                                           'allow '
                                                                                                                                                                                                                                                           'local '
                                                                                                                                                                                                                                                           'profiles. '
                                                                                                                                                                                                                                                           'Does '
                                                                                                                                                                                                                                                           'not '
                                                                                                                                                                                                                                                           'authenticate '
                                                                                                                                                                                                                                                           'with '
                                                                                                                                                                                                                                                           'account-verified '
                                                                                                                                                                                                                                                           'servers '
                                                                                                                                                                                                                                                           'or '
                                                                                                                                                                                                                                                           'Realms. '
                                                                                                                                                                                                                                                           'Add '
                                                                                                                                                                                                                                                           'as '
                                                                                                                                                                                                                                                           'many '
                                                                                                                                                                                                                                                           'favorites '
                                                                                                                                                                                                                                                           'as '
                                                                                                                                                                                                                                                           'you '
                                                                                                                                                                                                                                                           'like, '
                                                                                                                                                                                                                                                           'or '
                                                                                                                                                                                                                                                           'save '
                                                                                                                                                                                                                                                           'servers '
                                                                                                                                                                                                                                                           'directly '
                                                                                                                                                                                                                                                           'in '
                                                                                                                                                                                                                                                           "Minecraft's "
                                                                                                                                                                                                                                                           'Multiplayer '
                                                                                                                                                                                                                                                           'menu.',
 'Lokales Profil · ohne Konto': 'Local profile · no account',
 'Lokales Skinpaket aktiviert. Starte das gewählte Spielprofil neu. Das Paket ändert Standardfiguren nur auf diesem Gerät.': 'Local '
                                                                                                                             'skin '
                                                                                                                             'pack '
                                                                                                                             'enabled. '
                                                                                                                             'Restart '
                                                                                                                             'the '
                                                                                                                             'selected '
                                                                                                                             'game '
                                                                                                                             'profile. '
                                                                                                                             'This '
                                                                                                                             'pack '
                                                                                                                             'changes '
                                                                                                                             'default '
                                                                                                                             'characters '
                                                                                                                             'only '
                                                                                                                             'on '
                                                                                                                             'this '
                                                                                                                             'device.',
 'Lokales Skinpaket anwenden': 'Apply local skin pack',
 'Lokales Skinpaket im gewählten Spielordner aktiviert.': 'Local skin pack enabled in the selected game folder.',
 'Lädt Minecraft und Java mit Internet herunter. Keine Konto-Anmeldung nötig.': 'Downloads Minecraft and Java '
                                                                                'over the internet. No account '
                                                                                'sign-in required.',
 'MOD-PROFIL': 'MOD PROFILE',
 'Microsoft hat geantwortet, aber Blockwerk hat für diese App-Kennung keine Minecraft-API-Freigabe. Der Projektbetreiber muss die Freigabe abschließen. Dein Passwort behebt das nicht.': 'Microsoft '
                                                                                                                                                                                          'responded, '
                                                                                                                                                                                          'but '
                                                                                                                                                                                          'Blockwerk '
                                                                                                                                                                                          'has '
                                                                                                                                                                                          'no '
                                                                                                                                                                                          'Minecraft '
                                                                                                                                                                                          'API '
                                                                                                                                                                                          'approval '
                                                                                                                                                                                          'for '
                                                                                                                                                                                          'this '
                                                                                                                                                                                          'app '
                                                                                                                                                                                          'ID. '
                                                                                                                                                                                          'The '
                                                                                                                                                                                          'project '
                                                                                                                                                                                          'operator '
                                                                                                                                                                                          'must '
                                                                                                                                                                                          'complete '
                                                                                                                                                                                          'approval. '
                                                                                                                                                                                          'Your '
                                                                                                                                                                                          'password '
                                                                                                                                                                                          'cannot '
                                                                                                                                                                                          'resolve '
                                                                                                                                                                                          'this.',
 'Microsoft hat kein vollständiges Minecraft-Java-Profil geliefert. Öffne Minecraft zuerst im offiziellen Launcher.': 'Microsoft '
                                                                                                                      'did '
                                                                                                                      'not '
                                                                                                                      'return '
                                                                                                                      'a '
                                                                                                                      'complete '
                                                                                                                      'Minecraft '
                                                                                                                      'Java '
                                                                                                                      'profile. '
                                                                                                                      'Open '
                                                                                                                      'Minecraft '
                                                                                                                      'in '
                                                                                                                      'the '
                                                                                                                      'official '
                                                                                                                      'launcher '
                                                                                                                      'first.',
 'Microsoft im Browser öffnen': 'Open Microsoft in browser',
 'Microsoft und Xbox': 'Microsoft and Xbox',
 'Microsoft und Xbox werden verbunden …': 'Connecting Microsoft and Xbox …',
 'Microsoft- und Xbox-Konto verbinden': 'Connect Microsoft and Xbox accounts',
 'Microsoft-Anmeldung noch nicht verfügbar': 'Microsoft sign-in not available yet',
 'Microsoft-Anmeldung: Die Einrichtung von Blockwerk ist noch nicht abgeschlossen.': 'Microsoft sign-in: '
                                                                                     'Blockwerk setup is not '
                                                                                     'finished yet.',
 'Microsoft-App einrichten': 'Set up Microsoft app',
 'Microsoft-App registrieren ↗': 'Register Microsoft app ↗',
 'Microsoft-Konto': 'Microsoft account',
 'Microsoft-Konto benötigt': 'Microsoft account required',
 'Microsoft-Konto erstellen ↗': 'Create Microsoft account ↗',
 'Microsoft-Konto öffnen →': 'Open Microsoft account →',
 'Microsoft-Login einrichten →': 'Set up Microsoft sign-in →',
 'Minecraft Java wurde bei der Anmeldung geprüft. Die Berechtigung wird vor jedem Online-Spielstart erneut geprüft. ': 'Minecraft '
                                                                                                                       'Java '
                                                                                                                       'was '
                                                                                                                       'verified '
                                                                                                                       'during '
                                                                                                                       'sign-in. '
                                                                                                                       'Access '
                                                                                                                       'is '
                                                                                                                       'checked '
                                                                                                                       'again '
                                                                                                                       'before '
                                                                                                                       'each '
                                                                                                                       'online '
                                                                                                                       'launch. ',
 'Minecraft hat den Konto-Skin ‚': "Minecraft accepted the account skin '",
 'Minecraft hat den Zugriff abgelehnt. Der Projektbetreiber muss die Minecraft-API-Freigabe der App prüfen; auch eine Dienststörung ist möglich. Bitte später erneut versuchen.': 'Minecraft '
                                                                                                                                                                                  'denied '
                                                                                                                                                                                  'access. '
                                                                                                                                                                                  'The '
                                                                                                                                                                                  'project '
                                                                                                                                                                                  'operator '
                                                                                                                                                                                  'must '
                                                                                                                                                                                  'check '
                                                                                                                                                                                  'the '
                                                                                                                                                                                  "app's "
                                                                                                                                                                                  'Minecraft '
                                                                                                                                                                                  'API '
                                                                                                                                                                                  'approval; '
                                                                                                                                                                                  'a '
                                                                                                                                                                                  'service '
                                                                                                                                                                                  'outage '
                                                                                                                                                                                  'is '
                                                                                                                                                                                  'also '
                                                                                                                                                                                  'possible. '
                                                                                                                                                                                  'Try '
                                                                                                                                                                                  'again '
                                                                                                                                                                                  'later.',
 'Minecraft hat die Skin-Änderung abgelehnt. Prüfe Konto, Minecraft-Berechtigung und Skin-Datei.': 'Minecraft '
                                                                                                   'rejected the '
                                                                                                   'skin change. '
                                                                                                   'Check your '
                                                                                                   'account, '
                                                                                                   'Minecraft '
                                                                                                   'access and '
                                                                                                   'skin file.',
 'Minecraft herunterladen ↗': 'Download Minecraft ↗',
 'Minecraft läuft …': 'Minecraft is running …',
 'Minecraft starten  ▶': 'Launch Minecraft  ▶',
 'Minecraft wurde beendet': 'Minecraft has closed',
 'Minecraft wurde beendet. Bereit für dein nächstes Abenteuer.': 'Minecraft has closed. Ready for your next '
                                                                 'adventure.',
 'Minecraft wurde mit Fehlercode ': 'Minecraft exited with error code ',
 'Minecraft-, saves- oder Weltordner auswählen': 'Select a Minecraft, saves or world folder',
 'Minecraft-Freigabe beantragen ↗': 'Request Minecraft approval ↗',
 'Minecraft-Java-Profil und Lizenz prüfen': 'Verify Minecraft Java profile and license',
 'Minecraft-Konto-Skin erfolgreich geändert.': 'Minecraft account skin changed successfully.',
 'Minecraft-Zielordner öffnen ↗': 'Open Minecraft destination folder ↗',
 'Mit Microsoft anmelden →': 'Sign in with Microsoft →',
 'Mit Microsoft anmelden ↗': 'Sign in with Microsoft ↗',
 'Mit deinem Microsoft-Konto fortfahren': 'Continue with your Microsoft account',
 'Mit einer funktionierenden Microsoft-/Minecraft-Anmeldung kann der Skin im eigenen Konto geändert werden. Alternativ die PNG exportieren und auf der offiziellen Minecraft-Profilseite hochladen.': 'With '
                                                                                                                                                                                                      'working '
                                                                                                                                                                                                      'Microsoft/Minecraft '
                                                                                                                                                                                                      'sign-in, '
                                                                                                                                                                                                      'you '
                                                                                                                                                                                                      'can '
                                                                                                                                                                                                      'change '
                                                                                                                                                                                                      'the '
                                                                                                                                                                                                      'skin '
                                                                                                                                                                                                      'in '
                                                                                                                                                                                                      'your '
                                                                                                                                                                                                      'account. '
                                                                                                                                                                                                      'Alternatively, '
                                                                                                                                                                                                      'export '
                                                                                                                                                                                                      'the '
                                                                                                                                                                                                      'PNG '
                                                                                                                                                                                                      'and '
                                                                                                                                                                                                      'upload '
                                                                                                                                                                                                      'it '
                                                                                                                                                                                                      'on '
                                                                                                                                                                                                      'the '
                                                                                                                                                                                                      'official '
                                                                                                                                                                                                      'Minecraft '
                                                                                                                                                                                                      'profile '
                                                                                                                                                                                                      'page.',
 'Mod-Datei': 'Mod file',
 'Mod-JARs': 'Mod JARs',
 'Mod-JARs auswählen': 'Select mod JARs',
 'Mod-JARs hinzufügen …': 'Add mod JARs …',
 'Mod-Metadaten sind ungewöhnlich groß: ': 'Mod metadata is unusually large: ',
 'Mod-Ordner öffnen ↗': 'Open mods folder ↗',
 'Mod-Profil': 'Mod profile',
 'Mod-Profil ‚': "Mod profile '",
 'Mods & Loader': 'Mods & Loaders',
 'Mods & Loader →': 'Mods & Loaders →',
 'Mods importieren': 'Import mods',
 'Mods müssen zu Minecraft, Loader und Abhängigkeiten passen. Fabric API, Bibliotheken und andere benötigte Mods zusätzlich importieren. Unbekannte Metadaten werden nicht als Kompatibilitätsgarantie behandelt.': 'Mods '
                                                                                                                                                                                                                    'must '
                                                                                                                                                                                                                    'match '
                                                                                                                                                                                                                    'Minecraft, '
                                                                                                                                                                                                                    'the '
                                                                                                                                                                                                                    'loader '
                                                                                                                                                                                                                    'and '
                                                                                                                                                                                                                    'their '
                                                                                                                                                                                                                    'dependencies. '
                                                                                                                                                                                                                    'Also '
                                                                                                                                                                                                                    'import '
                                                                                                                                                                                                                    'Fabric '
                                                                                                                                                                                                                    'API, '
                                                                                                                                                                                                                    'libraries '
                                                                                                                                                                                                                    'and '
                                                                                                                                                                                                                    'any '
                                                                                                                                                                                                                    'other '
                                                                                                                                                                                                                    'required '
                                                                                                                                                                                                                    'mods. '
                                                                                                                                                                                                                    'Unknown '
                                                                                                                                                                                                                    'metadata '
                                                                                                                                                                                                                    'is '
                                                                                                                                                                                                                    'not '
                                                                                                                                                                                                                    'a '
                                                                                                                                                                                                                    'compatibility '
                                                                                                                                                                                                                    'guarantee.',
 'Mojang stellt für dieses System keine passende Java-Laufzeit bereit. Wähle Java unter Einstellungen manuell aus.': 'Mojang '
                                                                                                                     'provides '
                                                                                                                     'no '
                                                                                                                     'matching '
                                                                                                                     'Java '
                                                                                                                     'runtime '
                                                                                                                     'for '
                                                                                                                     'this '
                                                                                                                     'system. '
                                                                                                                     'Select '
                                                                                                                     'Java '
                                                                                                                     'manually '
                                                                                                                     'under '
                                                                                                                     'Settings.',
 'Nach Online-Abruf verfügbar': 'Available after loading the online catalog',
 'Name': 'Name',
 'Neue Favoriten werden beim Offline-Start einmalig zur Serverliste des gewählten Spielprofils hinzugefügt. Im Spiel unter Mehrspieler kannst du Server hinzufügen, bearbeiten und entfernen. Diese Änderungen bleiben erhalten. Die Serverliste gehört zum jeweiligen Spielprofil und zur Version.': 'New '
                                                                                                                                                                                                                                                                                                      'favorites '
                                                                                                                                                                                                                                                                                                      'are '
                                                                                                                                                                                                                                                                                                      'added '
                                                                                                                                                                                                                                                                                                      'once '
                                                                                                                                                                                                                                                                                                      'to '
                                                                                                                                                                                                                                                                                                      'the '
                                                                                                                                                                                                                                                                                                      'selected '
                                                                                                                                                                                                                                                                                                      'game '
                                                                                                                                                                                                                                                                                                      "profile's "
                                                                                                                                                                                                                                                                                                      'server '
                                                                                                                                                                                                                                                                                                      'list '
                                                                                                                                                                                                                                                                                                      'at '
                                                                                                                                                                                                                                                                                                      'offline '
                                                                                                                                                                                                                                                                                                      'launch. '
                                                                                                                                                                                                                                                                                                      'In '
                                                                                                                                                                                                                                                                                                      "Minecraft's "
                                                                                                                                                                                                                                                                                                      'Multiplayer '
                                                                                                                                                                                                                                                                                                      'menu, '
                                                                                                                                                                                                                                                                                                      'you '
                                                                                                                                                                                                                                                                                                      'can '
                                                                                                                                                                                                                                                                                                      'add, '
                                                                                                                                                                                                                                                                                                      'edit '
                                                                                                                                                                                                                                                                                                      'and '
                                                                                                                                                                                                                                                                                                      'remove '
                                                                                                                                                                                                                                                                                                      'servers. '
                                                                                                                                                                                                                                                                                                      'Your '
                                                                                                                                                                                                                                                                                                      'changes '
                                                                                                                                                                                                                                                                                                      'are '
                                                                                                                                                                                                                                                                                                      'kept. '
                                                                                                                                                                                                                                                                                                      'Server '
                                                                                                                                                                                                                                                                                                      'lists '
                                                                                                                                                                                                                                                                                                      'belong '
                                                                                                                                                                                                                                                                                                      'to '
                                                                                                                                                                                                                                                                                                      'the '
                                                                                                                                                                                                                                                                                                      'selected '
                                                                                                                                                                                                                                                                                                      'profile '
                                                                                                                                                                                                                                                                                                      'and '
                                                                                                                                                                                                                                                                                                      'version.',
 'Neue Launcher-Version: ': 'New launcher version: ',
 'Neue Welt': 'New world',
 'Neue Welt in Minecraft …': 'New world in Minecraft …',
 'Neues Profil, z. B. Mein Fabric': 'New profile, e.g. My Fabric',
 'Nicht angemeldet': 'Not signed in',
 'Nicht von Mojang oder Microsoft entwickelt oder unterstützt. Minecraft ist eine Marke von Mojang/Microsoft. Es werden keine Spieldateien mitgeliefert.': 'Not '
                                                                                                                                                           'developed '
                                                                                                                                                           'or '
                                                                                                                                                           'supported '
                                                                                                                                                           'by '
                                                                                                                                                           'Mojang '
                                                                                                                                                           'or '
                                                                                                                                                           'Microsoft. '
                                                                                                                                                           'Minecraft '
                                                                                                                                                           'is '
                                                                                                                                                           'a '
                                                                                                                                                           'trademark '
                                                                                                                                                           'of '
                                                                                                                                                           'Mojang/Microsoft. '
                                                                                                                                                           'No '
                                                                                                                                                           'game '
                                                                                                                                                           'files '
                                                                                                                                                           'are '
                                                                                                                                                           'included.',
 'Noch kein Mod-Profil vorhanden.': 'No mod profile yet.',
 'Noch keine Quelle eingerichtet.': 'No source configured yet.',
 'Noch keine Updateprüfung': 'No update check yet',
 'Noch keine Welten geladen.': 'No worlds loaded yet.',
 'Noch nicht geprüft.': 'Not checked yet.',
 'Nur der Launcher wird auf Updates geprüft. Minecraft-Versionen, Mods, Welten und die Minecraft-Versionsliste werden dabei nicht automatisch aktualisiert.': 'Only '
                                                                                                                                                              'the '
                                                                                                                                                              'launcher '
                                                                                                                                                              'is '
                                                                                                                                                              'checked '
                                                                                                                                                              'for '
                                                                                                                                                              'updates. '
                                                                                                                                                              'Minecraft '
                                                                                                                                                              'versions, '
                                                                                                                                                              'mods, '
                                                                                                                                                              'worlds '
                                                                                                                                                              'and '
                                                                                                                                                              'the '
                                                                                                                                                              'Minecraft '
                                                                                                                                                              'version '
                                                                                                                                                              'list '
                                                                                                                                                              'are '
                                                                                                                                                              'not '
                                                                                                                                                              'updated '
                                                                                                                                                              'automatically.',
 'Nur für diese Sitzung': 'This session only',
 'Oben zwischen Vollversionen ab 1.0 und Snapshots wechseln. Die Snapshot-Liste enthält auch offizielle Pre-Releases und Release Candidates. Für Versionswechsel werden Welten als Spielkopie geöffnet.': 'Switch '
                                                                                                                                                                                                          'between '
                                                                                                                                                                                                          'releases '
                                                                                                                                                                                                          'from '
                                                                                                                                                                                                          '1.0 '
                                                                                                                                                                                                          'onwards '
                                                                                                                                                                                                          'and '
                                                                                                                                                                                                          'snapshots '
                                                                                                                                                                                                          'above. '
                                                                                                                                                                                                          'Snapshots '
                                                                                                                                                                                                          'also '
                                                                                                                                                                                                          'include '
                                                                                                                                                                                                          'official '
                                                                                                                                                                                                          'pre-releases '
                                                                                                                                                                                                          'and '
                                                                                                                                                                                                          'release '
                                                                                                                                                                                                          'candidates. '
                                                                                                                                                                                                          'Version '
                                                                                                                                                                                                          'changes '
                                                                                                                                                                                                          'open '
                                                                                                                                                                                                          'worlds '
                                                                                                                                                                                                          'as '
                                                                                                                                                                                                          'play '
                                                                                                                                                                                                          'copies.',
 'Offizielle Skin-Profilseite öffnen ↗': 'Open official skin profile page ↗',
 'Offiziellen Launcher öffnen ↗': 'Open official launcher ↗',
 'Offline starten  ▶': 'Launch offline  ▶',
 'Offline vorbereitet': 'Ready for offline play',
 'Offline vorbereitet · Prüfung beim Start': 'Ready for offline play · Checked on launch',
 'Offline · Einzelspieler & Server': 'Offline · Singleplayer & servers',
 'Offline-Modus auswählen →': 'Select offline mode →',
 'Offline-Modus: lokale Spieldateien werden geprüft …': 'Offline mode: checking local game files …',
 'Offline-Start abgebrochen.': 'Offline launch canceled.',
 'Offline: Einzelspieler oder Mehrspieler öffnen. Server müssen lokale Profile zulassen. Serverlisten werden im Spiel gespeichert.': 'Offline: '
                                                                                                                                     'open '
                                                                                                                                     'Singleplayer '
                                                                                                                                     'or '
                                                                                                                                     'Multiplayer. '
                                                                                                                                     'Servers '
                                                                                                                                     'must '
                                                                                                                                     'allow '
                                                                                                                                     'local '
                                                                                                                                     'profiles. '
                                                                                                                                     'Minecraft '
                                                                                                                                     'saves '
                                                                                                                                     'your '
                                                                                                                                     'server '
                                                                                                                                     'lists.',
 'Ohne Konto · Einzelspieler und Server mit lokalen Profilen': 'No account · Singleplayer and servers allowing '
                                                               'local profiles',
 'Ohne Microsoft-Konto': 'Without Microsoft account',
 'Online: Anmeldung, Lizenzprüfung und Downloads sind aktiv.': 'Online: sign-in, license checks and downloads are '
                                                               'enabled.',
 'Optional: https://deine-webseite/Blockwerk-Updates.json': 'Optional: '
                                                            'https://your-website/Blockwerk-Updates.json',
 'Ordner': 'Folder',
 'Ordner hinzufügen …': 'Add folder …',
 'Ordner konnte nicht geöffnet werden: ': 'Could not open folder: ',
 'Ordner mit Blockwerk-Updates.json auswählen': 'Choose the folder containing Blockwerk-Updates.json',
 'Original Minecraft Java.\nDeine Version. Dein Abenteuer.': 'Original Minecraft Java.\n'
                                                             'Your version. Your adventure.',
 'Originale Downloads · Passendes Java automatisch': 'Original downloads · Matching Java installed automatically',
 'PNG exportieren …': 'Export PNG …',
 'Passendes Java wird installiert: ': 'Installing matching Java: ',
 'Port 29147 ist belegt. Schließe andere Launcher-Anmeldungen und versuche es erneut.': 'Port 29147 is in use. '
                                                                                        'Close other launcher '
                                                                                        'sign-ins and try again.',
 'Profil': 'Profile',
 'Profil erstellen & installieren': 'Create & install profile',
 'SPIELMODUS': 'GAME MODE',
 'Schließen': 'Close',
 'Server speichern': 'Save server',
 'Serveradresse': 'Server address',
 'Servername': 'Server name',
 'Skin hinzufügen': 'Add skin',
 'Skin-PNG exportieren': 'Export skin PNG',
 'Skin-PNG exportiert. Die Originaldatei bleibt unverändert.': 'Skin PNG exported. The original file is '
                                                               'unchanged.',
 'Skin-PNGs hinzufügen …': 'Add skin PNGs …',
 'Skin-Änderung abgebrochen.': 'Skin change canceled.',
 'Slim · schmale Arme': 'Slim · narrow arms',
 'Spiel & Java': 'Game & Java',
 'Spieldateien direkt von Mojang.': 'Game files directly from Mojang.',
 'Spieldateien herunterladen': 'Download game files',
 'Spieldateien werden ohne Konto-Anmeldung heruntergeladen. Internet wird benötigt …': 'Downloading game files '
                                                                                       'without account sign-in. '
                                                                                       'Internet is required …',
 'Spielen': 'Play',
 'Spielkopie: ': 'Play copy: ',
 'Spielmodus': 'Game mode',
 'Spielordner öffnen ↗': 'Open game folder ↗',
 'Spielprofil': 'Game profile',
 'Spielprofil / Version wählen →': 'Select game profile / version →',
 'Sprache': 'Language',
 'Sprache konnte nicht gespeichert werden.': 'Could not save the language setting.',
 'Sprache wechseln': 'Change language',
 'Status': 'Status',
 'Suchen': 'Search',
 'Typ': 'Type',
 'UNABHÄNGIGER LAUNCHER\n': 'INDEPENDENT LAUNCHER\n',
 'Unbekannt': 'Unknown',
 'Unbekannte Updatequelle.': 'Unknown update source.',
 'Unbekannter Loader.': 'Unknown loader.',
 'Ungültige IPv6-Adresse.': 'Invalid IPv6 address.',
 'Ungültige Mod-Datei.': 'Invalid mod file.',
 'Ungültige Versionskennung.': 'Invalid version ID.',
 'Ungültiger Asset-Index.': 'Invalid asset index.',
 'Ungültiger Servername.': 'Invalid server name.',
 'Ungültiger Skin.': 'Invalid skin.',
 'Ungültiger Updatepaket-Pfad.': 'Invalid update package path.',
 'Ungültiger Weltordner.': 'Invalid world folder.',
 'Ungültiger Windows-Pfad im Update.': 'Invalid Windows path in update.',
 'Ungültiger lokaler Dateipfad.': 'Invalid local file path.',
 'Ungültiges Mod-Profil.': 'Invalid mod profile.',
 'Unterstützt werden lokale JAR- und Windows-EXE-Installer.': 'Local JAR and Windows EXE installers are '
                                                              'supported.',
 'Update-Download abgebrochen.': 'Update download canceled.',
 'Update-Vorbereitung abgebrochen.': 'Update preparation canceled.',
 'Updatebeschreibung und App-Paket passen nicht zusammen.': 'The update manifest and app package do not match.',
 'Updatepaket herunterladen': 'Download update package',
 'Updatequelle': 'Update source',
 'Updatequelle auswählen': 'Select update source',
 'Updatequelle bereit': 'Update source ready',
 'Updatequelle wird geprüft …': 'Checking update source …',
 'VERSION AUSWÄHLEN': 'SELECT VERSION',
 'Vanilla, wie du es kennst': 'Vanilla, just as you know it',
 'Verbinde dein Microsoft-Konto mit Minecraft-Java-Berechtigung. Die Anmeldung öffnet die offizielle Microsoft-Seite in deinem Browser.': 'Connect '
                                                                                                                                          'your '
                                                                                                                                          'Microsoft '
                                                                                                                                          'account '
                                                                                                                                          'with '
                                                                                                                                          'Minecraft '
                                                                                                                                          'Java '
                                                                                                                                          'access. '
                                                                                                                                          'Sign-in '
                                                                                                                                          'opens '
                                                                                                                                          'the '
                                                                                                                                          'official '
                                                                                                                                          'Microsoft '
                                                                                                                                          'page '
                                                                                                                                          'in '
                                                                                                                                          'your '
                                                                                                                                          'browser.',
 'Verfügbar sind Vollversionen ab 1.0 und Snapshots. Unter Welten stehen lokale Java-Spielstände aus Blockwerk, Minecraft und gewählten Ordnern. Vorbereitete Versionen lassen sich offline starten. Über ‚Spieldateien herunterladen‘ werden sie mit Internet eingerichtet, auch ohne Konto.': 'Releases '
                                                                                                                                                                                                                                                                                                'from '
                                                                                                                                                                                                                                                                                                '1.0 '
                                                                                                                                                                                                                                                                                                'onwards '
                                                                                                                                                                                                                                                                                                'and '
                                                                                                                                                                                                                                                                                                'snapshots '
                                                                                                                                                                                                                                                                                                'are '
                                                                                                                                                                                                                                                                                                'available. '
                                                                                                                                                                                                                                                                                                'Worlds '
                                                                                                                                                                                                                                                                                                'lists '
                                                                                                                                                                                                                                                                                                'local '
                                                                                                                                                                                                                                                                                                'Java '
                                                                                                                                                                                                                                                                                                'saves '
                                                                                                                                                                                                                                                                                                'from '
                                                                                                                                                                                                                                                                                                'Blockwerk, '
                                                                                                                                                                                                                                                                                                'Minecraft '
                                                                                                                                                                                                                                                                                                'and '
                                                                                                                                                                                                                                                                                                'selected '
                                                                                                                                                                                                                                                                                                'folders. '
                                                                                                                                                                                                                                                                                                'Prepared '
                                                                                                                                                                                                                                                                                                'versions '
                                                                                                                                                                                                                                                                                                'can '
                                                                                                                                                                                                                                                                                                'launch '
                                                                                                                                                                                                                                                                                                'offline. '
                                                                                                                                                                                                                                                                                                'Use '
                                                                                                                                                                                                                                                                                                "'Download "
                                                                                                                                                                                                                                                                                                'game '
                                                                                                                                                                                                                                                                                                "files' "
                                                                                                                                                                                                                                                                                                'to '
                                                                                                                                                                                                                                                                                                'set '
                                                                                                                                                                                                                                                                                                'them '
                                                                                                                                                                                                                                                                                                'up '
                                                                                                                                                                                                                                                                                                'over '
                                                                                                                                                                                                                                                                                                'the '
                                                                                                                                                                                                                                                                                                'internet, '
                                                                                                                                                                                                                                                                                                'even '
                                                                                                                                                                                                                                                                                                'without '
                                                                                                                                                                                                                                                                                                'an '
                                                                                                                                                                                                                                                                                                'account.',
 'Version': 'Version',
 'Version auswählen': 'Select version',
 'Version suchen …': 'Search versions …',
 'Version unter Spielen auswählen': 'Select a version under Play',
 'Versionen': 'Versions',
 'Versionen laden': 'Load versions',
 'Versionskatalog wird von Mojang geladen …': 'Loading version catalog from Mojang …',
 'Versionsliste konnte nicht geladen werden. Prüfe die Internetverbindung und klicke auf Aktualisieren.': 'Could '
                                                                                                          'not '
                                                                                                          'load '
                                                                                                          'the '
                                                                                                          'version '
                                                                                                          'list. '
                                                                                                          'Check '
                                                                                                          'your '
                                                                                                          'internet '
                                                                                                          'connection '
                                                                                                          'and '
                                                                                                          'click '
                                                                                                          'Refresh.',
 'Versionsliste wird geladen …': 'Loading version list …',
 'Veröffentlicht': 'Released',
 'Vollständige Einrichtungsanleitung ↗': 'Full setup guide ↗',
 'Vollversion': 'Release',
 'Vollversionen': 'Releases',
 'Vollversionen und Snapshots': 'Releases and snapshots',
 'Von Blockwerk abmelden': 'Sign out of Blockwerk',
 'Vorbereitung abgebrochen.': 'Preparation canceled.',
 'Vorgang abgebrochen. Bereits geprüfte Downloads bleiben erhalten.': 'Task canceled. Already verified downloads '
                                                                      'are kept.',
 'Vorgang läuft': 'Task in progress',
 'Vorgang nicht abgeschlossen': 'Task not completed',
 'Vorhanden': 'Installed',
 'Vorhandene Spielkopie wird geöffnet. Das Original bleibt erhalten.': 'Opening an existing play copy. The '
                                                                       'original is kept.',
 'Web-Updates benötigen eine HTTPS-Adresse ohne Anmeldedaten.': 'Web updates require an HTTPS address without '
                                                                'credentials.',
 'Weiter zum Online-Spielen →': 'Continue to online play →',
 'Weitere Installer & vorhandene Profile': 'Other installers & existing profiles',
 'Welt': 'World',
 'Welt spielen ▶': 'Play world ▶',
 'Welt öffnen': 'Open world',
 'Welt, Version oder Profil suchen …': 'Search world, version or profile …',
 'Welten': 'Worlds',
 'Welten und Einstellungen getrennt.': 'Separate worlds and settings.',
 'Welten →': 'Worlds →',
 'Weltimport abgebrochen.': 'World import canceled.',
 'Weltordner öffnen ↗': 'Open world folder ↗',
 'Weltsuche abgebrochen.': 'World search canceled.',
 'Windows konnte die gespeicherte Anmeldung nicht öffnen. Bitte erneut anmelden.': 'Windows could not open the '
                                                                                   'saved sign-in. Sign in again.',
 'Wird beim ersten Start heruntergeladen': 'Downloaded on first launch',
 'Wähle dein Microsoft-Konto im Browser aus. Wenn kein Fenster erscheint, öffne den Browser unten erneut oder kopiere den Anmeldelink. Die Anmeldung wartet höchstens fünf Minuten.': 'Select '
                                                                                                                                                                                      'your '
                                                                                                                                                                                      'Microsoft '
                                                                                                                                                                                      'account '
                                                                                                                                                                                      'in '
                                                                                                                                                                                      'the '
                                                                                                                                                                                      'browser. '
                                                                                                                                                                                      'If '
                                                                                                                                                                                      'no '
                                                                                                                                                                                      'window '
                                                                                                                                                                                      'appears, '
                                                                                                                                                                                      'reopen '
                                                                                                                                                                                      'the '
                                                                                                                                                                                      'browser '
                                                                                                                                                                                      'below '
                                                                                                                                                                                      'or '
                                                                                                                                                                                      'copy '
                                                                                                                                                                                      'the '
                                                                                                                                                                                      'sign-in '
                                                                                                                                                                                      'link. '
                                                                                                                                                                                      'Sign-in '
                                                                                                                                                                                      'waits '
                                                                                                                                                                                      'up '
                                                                                                                                                                                      'to '
                                                                                                                                                                                      'five '
                                                                                                                                                                                      'minutes.',
 'Wähle einen Skin aus.': 'Select a skin.',
 'Xbox Live hat die Anmeldung abgelehnt. Prüfe Xbox-Profil und bei Kinderkonten die Microsoft-Familieneinstellungen.': 'Xbox '
                                                                                                                       'Live '
                                                                                                                       'denied '
                                                                                                                       'sign-in. '
                                                                                                                       'Check '
                                                                                                                       'your '
                                                                                                                       'Xbox '
                                                                                                                       'profile '
                                                                                                                       'and, '
                                                                                                                       'for '
                                                                                                                       'child '
                                                                                                                       'accounts, '
                                                                                                                       'Microsoft '
                                                                                                                       'family '
                                                                                                                       'settings.',
 'Ziehen zum Drehen': 'Drag to rotate',
 'Zuletzt geprüft: ': 'Last checked: ',
 'Zuletzt gespielt': 'Last played',
 'Zum Spielen auswählen →': 'Select for playing →',
 'Zuschauer': 'Spectator',
 'Zwei ausgewählte Dateien haben denselben Namen.': 'Two selected files have the same name.',
 'spiel.example.org:25565': 'play.example.org:25565',
 'Über Blockwerk': 'About Blockwerk',
 'Über ‚Spieldateien herunterladen‘ vorbereiten': "Prepare using 'Download game files'",
 'Überleben': 'Survival',
 '‘ ist vorbereitet. Mods als passende JAR-Dateien hinzufügen.': "' is ready. Add matching mod JAR files.",
 '‘ übernommen. Ein laufendes Spiel danach neu starten.': "'. Restart a running game afterwards.",
 '≡   Versionen': '≡   Versions',
 'ⓘ   Über Blockwerk': 'ⓘ   About Blockwerk',
 '▦   Spielen': '▦   Play',
 '▧   Welten': '▧   Worlds',
 '◇   Mods & Loader': '◇   Mods & Loaders',
 '⚙   Einstellungen': '⚙   Settings'}

EN.update({'Dieses Paket bitte manuell installieren.': 'Please install this package manually.', 'Launcher-Update wird vorbereitet. Persönliche Daten bleiben erhalten …': 'Preparing launcher update. Personal data is kept …', 'Das Quellpaket konnte nicht geprüft werden. Bitte manuell installieren.': 'Could not verify the source package. Install it manually.', 'Automatische Installation: portables Windows-Paket sowie Linux/macOS-Quellpakete. Native Linux/macOS-Builds werden manuell installiert. Eine Sicherung bleibt erhalten.': 'Automatic installation: portable Windows package and Linux/macOS source packages. Native Linux/macOS builds require manual installation. A backup is kept.', 'Linux ARM benötigt ein passendes ARM-Java. Bitte unter Einstellungen die Java-Datei auswählen. Minecraft und Mods müssen ARM unterstützen.': 'Linux ARM requires matching ARM Java. Select its Java executable under Settings. Minecraft and mods must support ARM.'})

EN.update({'Die Microsoft-App ist registriert. Die Minecraft-API-Freigabe bleibt offen. Eine vollständige Minecraft-Anmeldung ist deshalb nicht zugesichert. Der lokale Modus ohne Konto bleibt verfügbar.': 'The Microsoft app is registered. Minecraft API approval remains pending. Full Minecraft sign-in is therefore not guaranteed. Local mode without an account remains available.'})

REVERSE = {value: key for key, value in EN.items()}
