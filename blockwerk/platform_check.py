"""Read-only platform report. Never opens the account store or starts a game."""
from importlib import metadata
import os
from pathlib import Path
import platform
import struct
import sys
from .core import VERSION, data_directory


def report():
    packages = {}
    for name in ('PySide6-Essentials', 'minecraft-launcher-lib', 'keyring', 'SecretStorage'):
        try:packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:packages[name] = None
    machine = platform.machine().lower()
    return {'version': VERSION, 'system': platform.system(), 'machine': machine,
        'python': platform.python_version(), 'pointer_bits': struct.calcsize('P') * 8,
        'data_directory': str(data_directory()), 'packages': packages,
        'package_kind': 'native' if getattr(sys, 'frozen', False) else 'source',
        'desktop_session': any(os.environ.get(k) for k in ('DISPLAY', 'WAYLAND_DISPLAY')) if sys.platform == 'linux' else None,
        'java_selection': 'manual_required' if sys.platform == 'linux' and machine in ('aarch64', 'arm64') else 'automatic_or_manual',
        'account_accessed': False, 'game_started': False}
