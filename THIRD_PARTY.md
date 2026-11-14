# Third-party components

Blockwerk's own source code uses the MIT license. Minecraft is not included;
the user downloads it from Mojang's servers under the applicable Minecraft terms.
No Microsoft/Mojang affiliation or endorsement is implied.

The Windows distribution uses dynamically linked Qt libraries. The `_internal`
directory is part of the distribution. You may replace compatible Qt/PySide
libraries and debug modifications in accordance with their licenses. Blockwerk
does not impose restrictions on reverse engineering for that purpose.

| Component | License / source |
| --- | --- |
| Python 3.12 | PSF; https://www.python.org/downloads/source/ |
| minecraft-launcher-lib 8.0 | BSD-2-Clause; https://codeberg.org/JakobDev/minecraft-launcher-lib |
| Qt 6 / PySide6 Essentials / Shiboken6 6.12.0 | LGPL-3.0 option; https://code.qt.io/cgit/qt/qtbase.git/ and https://code.qt.io/cgit/pyside/pyside-setup.git/ (v6.12.0) |
| requests | Apache-2.0; https://github.com/psf/requests |
| urllib3 | MIT; https://github.com/urllib3/urllib3 |
| certifi | MPL-2.0; https://github.com/certifi/python-certifi |
| charset-normalizer | MIT; https://github.com/jawah/charset_normalizer |
| idna | BSD-3-Clause; https://github.com/kjd/idna |
| PyInstaller bootloader | GPL-2.0-or-later with distribution exception; https://github.com/pyinstaller/pyinstaller |

The Windows build includes `licenses/` with package notices, the Python license,
and the GNU LGPLv3/GPLv3 texts. `BUILD-DEPENDENCIES.txt` records exact versions.
Source for unmodified Qt/PySide is available through the upstream repositories
and the Qt source download service at https://download.qt.io/official_releases/.
When distributing modified libraries, provide their corresponding source and
comply with their respective license requirements.

The block landscape and application icon are drawn by this project's code.
Windows system fonts are used through the operating system and are not bundled.

Keyring 25.7.0 (MIT) and platform dependencies: https://github.com/jaraco/keyring . Package license notices are included in native builds.
