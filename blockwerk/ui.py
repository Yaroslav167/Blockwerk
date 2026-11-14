"""Qt desktop UI. Network and installation work run outside the UI thread."""
from __future__ import annotations
from .i18n import tr
from .i18n import set_language, source_text

from dataclasses import replace
from datetime import datetime
import os
from pathlib import Path
import sys
import threading
import time

from PySide6.QtCore import Qt, QObject, Signal, QTimer, QUrl, QSize
from PySide6.QtGui import QColor, QDesktopServices, QFont, QFontDatabase, QIcon, QPainter, QPen, QPixmap, QPolygonF
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import (QApplication, QAbstractItemView, QComboBox, QFileDialog,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPlainTextEdit, QProgressBar, QPushButton, QScrollArea, QSpinBox,
    QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QCheckBox, QListWidget, QListWidgetItem)

from .core import (Cancelled, LauncherError, LauncherService, REDIRECT_URI,
                   VERSION, filter_versions, human_error, valid_client_id, validate_java, local_profile, is_release, is_snapshot)
from .profiles import ProfileManager, LOADERS
from .servers import ServerStore
from .landscape import Landscape
from .worlds import WorldManager, normalized_version
from .skins import SkinStore, load_skin
from .skin_view import SkinPreview
from .updates import UpdateManager


STYLE = """
QWidget { background: #121914; color: #e9f0e5; font-family: 'Segoe UI'; font-size: 14px; }
QMainWindow { background: #121914; }
QWidget#sidebar { background: #0c120e; border-right: 1px solid #253027; }
QLabel { background: transparent; }
QLabel#muted { color: #9eaea0; }
QLabel#eyebrow { color: #afd68c; font-size: 11px; font-weight: 700; letter-spacing: 2px; }
QLabel#heading { font-size: 27px; font-weight: 700; }
QLabel#heroTitle { font-size: 36px; font-weight: 700; color: #f3f7e9; }
QLabel#section { font-size: 17px; font-weight: 600; }
QLabel#brand { font-size: 23px; font-weight: 800; letter-spacing: 1px; }
QLabel#badge { color: #c4e7a4; background: #273c26; border: 1px solid #3a5633;
 border-radius: 12px; padding: 5px 11px; font-size: 11px; font-weight: 600; }
QFrame#card { background: #1a241c; border: 1px solid #2d3b2f; border-radius: 12px; }
QFrame#notice { background: #252b1d; border: 1px solid #454e2a; border-radius: 9px; }
QPushButton { background: #26362a; border: 1px solid #3a4b3b; border-radius: 7px;
 padding: 10px 15px; font-weight: 600; }
QPushButton:hover { background: #334836; border-color: #637a55; }
QPushButton:pressed { background: #1c2b20; }
QPushButton:disabled { color: #738171; background: #202a21; border-color: #2c392d; }
QPushButton#primary { background: #b8e285; color: #15220e; border: 1px solid #b8e285;
 font-size: 16px; font-weight: 700; padding: 14px 24px; }
QPushButton#primary:hover { background: #c9ef99; }
QPushButton#primary:disabled { background: #33472b; color: #829374; border-color: #405237; }
QPushButton#nav { text-align: left; background: transparent; border: none; padding: 9px 16px; color: #9eaea0; }
QPushButton#nav:checked { background: #233321; color: #cfedac; border-left: 3px solid #b8e285; border-radius: 5px; }
QPushButton#nav:hover { background: #1b281d; color: #e9f0e5; }
QPushButton#link { background: transparent; border: none; color: #b8d998; padding: 6px 2px; text-align: left; }
QLineEdit, QComboBox, QSpinBox { background: #101a13; border: 1px solid #415040;
 border-radius: 6px; padding: 9px 11px; min-height: 21px; selection-background-color: #496136; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: #b8e285; }
QComboBox QAbstractItemView { background: #1d2a20; selection-background-color: #3b5130; padding: 4px; }
QComboBox::drop-down { border: none; width: 26px; }
QPlainTextEdit { background: #101811; border: 1px solid #29372b; border-radius: 6px;
 color: #a4b3a1; padding: 8px; font: 12px 'Consolas'; }
QProgressBar { background: #0f1811; border: none; border-radius: 3px; max-height: 6px; }
QProgressBar::chunk { background: #b8e285; border-radius: 3px; }
QTableWidget { background: #172019; alternate-background-color: #1b271d; border: 1px solid #2d3b2f;
 border-radius: 8px; gridline-color: #29362b; selection-background-color: #344e2c; }
QTableWidget::item { padding-left: 12px; border-bottom: 1px solid #263329; }
QListWidget { background: #172019; border: 1px solid #2d3b2f; border-radius: 8px; }
QListWidget::item { padding: 10px; border-bottom: 1px solid #263329; }
QListWidget::item:selected { background: #344e2c; color: #e9f0e5; }
QHeaderView::section { background: #223025; color: #aebfa7; padding: 12px; border: none;
 font-size: 12px; font-weight: 600; text-align: left; }
QScrollBar:vertical { background: #121914; width: 10px; }
QScrollBar::handle:vertical { background: #3d513d; min-height: 25px; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollArea { border: none; background: transparent; }
QMessageBox { background: #1a241c; }
QToolTip { background: #27382a; color: #ecf4e6; border: 1px solid #5c7054; padding: 6px; }
"""


def label(text: str, name: str = "", wrap: bool = False) -> QLabel:
    widget = QLabel(text)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setObjectName(name)
    widget.setWordWrap(wrap)
    return widget


def button(text, callback, name="") -> QPushButton:
    widget = QPushButton(text.replace("&", "&&"))
    widget.setObjectName(name)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    widget.clicked.connect(callback)
    return widget


def card() -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(22, 20, 22, 20)
    layout.setSpacing(12)
    return frame, layout


def app_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor("#152019"))
    painter = QPainter(pixmap)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#b8e285"))
    painter.drawPolygon(QPolygonF([QPointF(32, 9), QPointF(55, 21), QPointF(32, 34), QPointF(9, 21)]))
    painter.setBrush(QColor("#678e48"))
    painter.drawPolygon(QPolygonF([QPointF(9, 24), QPointF(30, 36), QPointF(30, 57), QPointF(9, 45)]))
    painter.setBrush(QColor("#3e6034"))
    painter.drawPolygon(QPolygonF([QPointF(34, 36), QPointF(55, 24), QPointF(55, 45), QPointF(34, 57)]))
    painter.end()
    return QIcon(pixmap)


class Events(QObject):
    status = Signal(str)
    progress = Signal(int, int)
    started = Signal()
    finished = Signal(str, object)
    failed = Signal(str, str)
    auth_link = Signal(str)
    update_checked = Signal(object)
    update_failed = Signal(str)


class LauncherWindow(QMainWindow):
    def __init__(self, service: LauncherService, offline_preview=False):
        super().__init__()
        self.service = service
        set_language(service.settings.language)
        self.offline_preview = offline_preview
        self.profiles = ProfileManager(service)
        self.servers = ServerStore(service.root)
        self.worlds = WorldManager(service, self.profiles)
        self.skins = SkinStore(service.root)
        self.skins.ensure_starters()
        self.updates = UpdateManager(service.root)
        self.update_info = None
        self.update_package = None
        self.update_check_running = False
        self.closing = False
        self.world_rows = []
        self.worlds_loaded = False
        self.versions: list[dict] = []
        self.username = ""
        self.auth_phase = 0
        self.auth_error = ""
        self.auth_url = ""
        self.active_task = ""
        self.busy = False
        self.playing = False
        self.cancel_event = threading.Event()
        self.events = Events(self)
        self.events.status.connect(self.show_status)
        self.events.progress.connect(self.show_progress)
        self.events.started.connect(self.game_started)
        self.events.finished.connect(self.finished)
        self.events.failed.connect(self.failed)
        self.events.auth_link.connect(self.receive_auth_link)
        self.events.update_checked.connect(self.update_checked)
        self.events.update_failed.connect(self.update_failed)
        self.setWindowTitle("Blockwerk · Minecraft Java Launcher")
        self.setWindowIcon(app_icon())
        self.resize(1160, 830)
        self.setMinimumSize(1040, 780)
        container = QWidget()
        root = QHBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setCentralWidget(container)
        self.make_sidebar(root)
        main = QWidget()
        layout = QVBoxLayout(main)
        layout.setContentsMargins(30, 24, 30, 22)
        layout.setSpacing(18)
        root.addWidget(main, 1)
        top = QHBoxLayout()
        self.title_label = label(tr("Spielen"), "heading")
        top.addWidget(self.title_label)
        top.addStretch()
        self.language_combo = QComboBox()
        self.language_combo.setAccessibleName(tr('Sprache'))
        self.language_combo.addItem('Deutsch', 'de')
        self.language_combo.addItem('English', 'en')
        self.language_combo.setCurrentIndex(self.language_combo.findData(service.settings.language))
        self.language_combo.currentIndexChanged.connect(self.change_language)
        top.addWidget(self.language_combo)
        top.addWidget(label("JAVA EDITION", "badge"))
        layout.addLayout(top)
        self.notice = QFrame()
        self.notice.setObjectName("notice")
        notice_layout = QHBoxLayout(self.notice)
        notice_layout.setContentsMargins(14, 9, 10, 9)
        notice_layout.addWidget(label(tr("Microsoft-Anmeldung: Die Einrichtung von Blockwerk ist noch nicht abgeschlossen."), wrap=True), 1)
        notice_layout.addWidget(button("Details →", self.open_account, "link"))
        layout.addWidget(self.notice)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        self.make_play_page()
        self.make_versions_page()
        self.make_settings_page()
        self.make_about_page()
        self.make_mods_page()
        self.make_servers_page()
        self.make_account_page()
        self.make_worlds_page()
        self.make_skins_page()
        self.make_updates_page()
        self.status = label(tr("Bereit. Spielprofil und Spielmodus auswählen."), "muted", True)
        layout.addWidget(self.status)
        self.refresh_profiles(self.service.settings.selected_profile)
        self.refresh_servers()
        self.read_account()
        self.update_account()
        self.refresh_skins()
        self.refresh_update_status()
        self.navigate(0)
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(60000)
        self.update_timer.timeout.connect(self.scheduled_update_check)
        if not offline_preview:
            QTimer.singleShot(150, self.reload_versions)
            QTimer.singleShot(1800, self.scheduled_update_check)
            self.update_timer.start()

    def change_language(self, *_):
        language = self.language_combo.currentData()
        if language == self.service.settings.language:
            return self
        if self.busy or self.update_check_running:
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(self.language_combo.findData(self.service.settings.language))
            self.language_combo.blockSignals(False)
            return self
        previous = self.service.settings.language
        self.service.settings.language = language
        try:
            self.service.settings.save(self.service.root)
        except OSError:
            self.service.settings.language = previous
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(self.language_combo.findData(previous))
            self.language_combo.blockSignals(False)
            QMessageBox.warning(self, tr('Sprache wechseln'), tr('Sprache konnte nicht gespeichert werden.'))
            return self
        page = self.stack.currentIndex()
        replacement = LauncherWindow(self.service, offline_preview=True)
        replacement.offline_preview = self.offline_preview
        replacement.versions = list(self.versions)
        replacement.world_rows = list(self.world_rows)
        replacement.worlds_loaded = self.worlds_loaded
        replacement.username = self.username
        replacement.update_info = self.update_info
        replacement.update_package = self.update_package
        replacement.populate_combo()
        replacement.render_versions()
        replacement.render_worlds()
        replacement.update_account()
        replacement.refresh_update_status()
        replacement.navigate(page)
        replacement.restoreGeometry(self.saveGeometry())
        QApplication.instance().blockwerk_window = replacement
        replacement.show()
        if not self.offline_preview:
            replacement.update_timer.start()
            if not replacement.versions:
                QTimer.singleShot(150, replacement.reload_versions)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.close()
        return replacement

    def make_sidebar(self, root):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 26, 18, 20)
        layout.setSpacing(8)
        icon = QLabel()
        icon.setPixmap(app_icon().pixmap(44, 44))
        layout.addWidget(icon)
        layout.addWidget(label("BLOCKWERK", "brand"))
        layout.addWidget(label(tr("Dein Weg in die Welt."), "muted"))
        layout.addSpacing(20)
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav_inner = QWidget()
        nav_inner.setObjectName('navContent')
        nav_inner.setStyleSheet("QWidget#navContent { background: #0c120e; }")
        nav_layout = QVBoxLayout(nav_inner)
        nav_layout.setContentsMargins(0,0,0,0)
        nav_layout.setSpacing(3)
        self.nav_buttons = []
        for index, text in enumerate([tr("▦   Spielen"), tr("≡   Versionen"), tr("⚙   Einstellungen"), tr("ⓘ   Über Blockwerk"), tr("◇   Mods & Loader"), "⇄   Server"]):
            nav = button(text, lambda checked=False, i=index: self.navigate(i), "nav")
            nav.setCheckable(True)
            nav.setProperty("pageIndex", index)
            nav_layout.addWidget(nav)
            self.nav_buttons.append(nav)
        nav = button(tr("▧   Welten"), lambda: self.navigate(7), "nav")
        nav.setProperty("pageIndex", 7)
        nav.setCheckable(True)
        nav_layout.addWidget(nav)
        self.nav_buttons.append(nav)
        for index,text in ((8,"◇   Skins"),(9,"↑   Updates")):
            nav=button(text,lambda checked=False,i=index:self.navigate(i),"nav")
            nav.setProperty("pageIndex",index)
            nav.setCheckable(True)
            nav_layout.addWidget(nav)
            self.nav_buttons.append(nav)
            if index==9:self.updates_nav=nav
        nav_layout.addStretch()
        nav_scroll.setWidget(nav_inner)
        layout.addWidget(nav_scroll,1)
        layout.addWidget(label(tr("DEIN KONTO"), "eyebrow"))
        self.account_name = label(tr("Nicht angemeldet"), wrap=True)
        self.account_note = label(tr("Microsoft-Konto benötigt"), "muted", True)
        layout.addWidget(self.account_name)
        layout.addWidget(self.account_note)
        self.login_button = button(tr("Microsoft-Konto"), self.open_account)
        self.login_button.setStyleSheet("font-size:12px; padding:10px 7px;")
        self.logout_button = button(tr("Abmelden"), self.logout, "link")
        layout.addWidget(self.login_button)
        layout.addWidget(self.logout_button)
        self.signup_button = button(tr("Microsoft-Konto erstellen ↗"), lambda: self.open_url("https://signup.live.com/"), "link")
        self.signup_button.setStyleSheet("font-size:11px;")
        layout.addWidget(self.signup_button)
        layout.addSpacing(18)
        platform_label = {"win32": "Windows", "darwin": "macOS"}.get(sys.platform, "Linux")
        layout.addWidget(label(tr("UNABHÄNGIGER LAUNCHER\n") + platform_label + " · v" + VERSION, "muted"))
        root.addWidget(sidebar)

    def make_play_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        modes = QHBoxLayout()
        modes.addWidget(label(tr("SPIELMODUS"), "eyebrow"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Online · Microsoft", tr("Offline · Einzelspieler & Server")])
        self.mode_combo.setCurrentIndex(1 if self.service.settings.offline_mode else 0)
        self.mode_combo.currentIndexChanged.connect(self.mode_changed)
        modes.addWidget(self.mode_combo)
        modes.addStretch()
        modes.addWidget(label("Java Edition", "muted"))
        layout.addLayout(modes)
        profile_choice = QHBoxLayout()
        profile_choice.addWidget(label(tr("Spielprofil")))
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumContentsLength(20)
        self.profile_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.profile_combo.addItem("Vanilla", "")
        self.profile_combo.currentIndexChanged.connect(self.profile_changed)
        profile_choice.addWidget(self.profile_combo, 1)
        profile_choice.addWidget(button(tr("Mods & Loader →"), lambda: self.navigate(4), "link"))
        profile_choice.addWidget(button(tr("Welten →"), lambda: self.navigate(7), "link"))
        layout.addLayout(profile_choice)
        self.local_profile_row = QWidget()
        profile_layout = QHBoxLayout(self.local_profile_row)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        profile_layout.addWidget(label(tr("Lokaler Spielername")))
        self.local_name_input = QLineEdit(self.service.settings.offline_name)
        self.local_name_input.setPlaceholderText(tr("3–16 Zeichen, z. B. Spieler"))
        self.local_name_input.setMaxLength(16)
        self.local_name_input.editingFinished.connect(self.save_local_name)
        profile_layout.addWidget(self.local_name_input, 1)
        profile_layout.addWidget(label(tr("Ohne Microsoft-Konto"), "muted"))
        layout.addWidget(self.local_profile_row)
        hero = self.landscape = Landscape()
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(28, 22, 28, 22)
        hero_layout.setSpacing(9)
        hero_layout.addWidget(label(tr("BAU. ENTDECKE. BLEIB NEUGIERIG."), "eyebrow"))
        hero_layout.addWidget(label(tr("Deine nächste\nWelt wartet."), "heroTitle"))
        hero_layout.addWidget(label(tr("Original Minecraft Java.\nDeine Version. Dein Abenteuer."), "muted"))
        hero_layout.addStretch()
        layout.addWidget(hero)
        launch_card, launch_layout = card()
        row = QHBoxLayout()
        choice = QVBoxLayout()
        choice.setSpacing(7)
        kind_row = QHBoxLayout()
        kind_row.addWidget(label(tr("VERSION AUSWÄHLEN"), "eyebrow"), 1)
        self.version_kind_combo = QComboBox()
        self.version_kind_combo.addItems([tr("Vollversionen"), "Snapshots"])
        self.version_kind_combo.setCurrentText(tr(self.service.settings.version_filter))
        self.version_kind_combo.currentTextChanged.connect(self.version_kind_changed)
        kind_row.addWidget(self.version_kind_combo)
        choice.addLayout(kind_row)
        self.version_combo = QComboBox()
        self.version_combo.setMinimumWidth(220)
        self.version_combo.addItem(tr("Versionsliste wird geladen …"), "")
        self.version_combo.currentIndexChanged.connect(self.version_changed)
        choice.addWidget(self.version_combo)
        self.version_note = label(tr("Alle Releases findest du unter Versionen."), "muted")
        self.version_note.setStyleSheet("font-size:12px;")
        choice.addWidget(self.version_note)
        row.addLayout(choice, 1)
        row.addSpacing(18)
        self.play_button = button(tr("Microsoft-Login einrichten →"), self.play, "primary")
        row.addWidget(self.play_button)
        launch_layout.addLayout(row)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        launch_layout.addWidget(self.progress_bar)
        footer = QHBoxLayout()
        self.install_note = label(tr("Originale Downloads · Passendes Java automatisch"), "muted")
        self.install_note.setStyleSheet("font-size:12px;")
        footer.addWidget(self.install_note, 1)
        self.prepare_button = button(tr("Spieldateien herunterladen"), self.prepare_local, "link")
        self.prepare_button.setToolTip(tr("Lädt Minecraft und Java mit Internet herunter. Keine Konto-Anmeldung nötig."))
        footer.addWidget(self.prepare_button)
        self.cancel_button = button(tr("Abbrechen"), self.cancel, "link")
        self.cancel_button.hide()
        footer.addWidget(self.cancel_button)
        launch_layout.addLayout(footer)
        layout.addWidget(launch_card)
        extras = QHBoxLayout()
        for title, detail in [(tr("Vanilla, wie du es kennst"), tr("Spieldateien direkt von Mojang.")),
                              (tr("Ein Zuhause je Version"), tr("Welten und Einstellungen getrennt."))]:
            frame, sub = card()
            sub.setContentsMargins(17, 13, 17, 13)
            sub.setSpacing(4)
            sub.addWidget(label(title))
            small = label(detail, "muted", True)
            small.setStyleSheet("font-size:12px;")
            sub.addWidget(small)
            extras.addWidget(frame)
        layout.addLayout(extras)
        log_header = QHBoxLayout()
        log_header.addWidget(label(tr("Aktivität"), "section"))
        log_header.addStretch()
        log_header.addWidget(button(tr("Spielordner öffnen ↗"), self.open_instance, "link"))
        layout.addLayout(log_header)
        self.activity = QPlainTextEdit()
        self.activity.setReadOnly(True)
        self.activity.setMaximumBlockCount(100)
        self.activity.setMinimumHeight(65)
        self.activity.setMaximumHeight(100)
        self.activity.setPlaceholderText(tr("Hier erscheinen Anmeldung, Downloads und Spielstatus."))
        layout.addWidget(self.activity, 1)
        page.setWidget(inner)
        self.stack.addWidget(page)

    def make_versions_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(label(tr("Vollversionen und Snapshots"), "section"))
        layout.addWidget(label(tr("Oben zwischen Vollversionen ab 1.0 und Snapshots wechseln. Die Snapshot-Liste enthält auch offizielle Pre-Releases und Release Candidates. Für Versionswechsel werden Welten als Spielkopie geöffnet."), "muted", True))
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("Version suchen …"))
        self.search.textChanged.connect(self.render_versions)
        filters.addWidget(self.search, 1)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([tr("Vollversionen"), "Snapshots"])
        self.filter_combo.setCurrentText(tr(self.service.settings.version_filter))
        self.filter_combo.currentTextChanged.connect(self.version_kind_changed)
        filters.addWidget(self.filter_combo)
        self.refresh_button = button(tr("Aktualisieren"), lambda: self.reload_versions(online=True))
        filters.addWidget(self.refresh_button)
        layout.addLayout(filters)
        self.version_count = label(tr("Versionsliste wird geladen …"), "muted")
        layout.addWidget(self.version_count)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([tr("Version"), tr("Typ"), tr("Veröffentlicht"), tr("Dateien")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.cellDoubleClicked.connect(lambda *_: self.choose_table_version())
        layout.addWidget(self.table, 1)
        bottom = QHBoxLayout()
        bottom.addWidget(label(tr("Jede Version hat ihren eigenen Spielordner."), "muted", True), 1)
        self.choose_button = button(tr("Diese Version auswählen →"), self.choose_table_version, "primary")
        bottom.addWidget(self.choose_button)
        layout.addLayout(bottom)
        self.stack.addWidget(page)

    def make_settings_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(16)
        auth_frame, auth_layout = card()
        auth_layout.addWidget(label(tr("Microsoft-Konto"), "section"))
        auth_layout.addWidget(label(tr("Anmeldung, Kontostatus und Hilfe findest du auf der Kontoseite. Die technische Registrierung wird einmalig vom Projektbetreiber eingerichtet."), "muted", True))
        auth_layout.addWidget(button(tr("Kontoseite öffnen →"), self.open_account))
        auth_layout.addWidget(button(tr("Einrichtung für Projektbetreiber ▾"), self.toggle_publisher_setup, "link"))
        self.publisher_setup = QWidget()
        setup = QVBoxLayout(self.publisher_setup)
        setup.setContentsMargins(0, 8, 0, 0)
        setup.setSpacing(10)
        setup.addWidget(label(tr("1 · Eigene Microsoft-App registrieren\nPersönliche Microsoft-Konten · Mobile/Desktop · Public Client"), "muted", True))
        setup.addWidget(button(tr("Microsoft-App registrieren ↗"), lambda: self.open_url("https://entra.microsoft.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"), "link"))
        setup.addWidget(label(tr("2 · Diese Redirect-URI in der App hinterlegen"), "muted"))
        redirect = QLineEdit(REDIRECT_URI)
        redirect.setReadOnly(True)
        setup.addWidget(redirect)
        setup.addWidget(label(tr("3 · Eigene öffentliche Application (client) ID eintragen"), "muted", True))
        self.client_input = QLineEdit(self.service.settings.client_id)
        self.client_input.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        self.client_input.setMaxLength(80)
        setup.addWidget(self.client_input)
        setup.addWidget(label(tr("4 · Einstellungen speichern und Minecraft-API-Freigabe beantragen\nEine eingetragene ID bestätigt noch keine Freigabe. Kein Client-Secret eintragen."), "muted", True))
        setup.addWidget(button(tr("Minecraft-Freigabe beantragen ↗"), lambda: self.open_url("https://aka.ms/mce-reviewappid"), "link"))
        setup.addWidget(button(tr("Vollständige Einrichtungsanleitung ↗"), self.open_guide, "link"))
        self.publisher_setup.hide()
        auth_layout.addWidget(self.publisher_setup)
        layout.addWidget(auth_frame)
        game_frame, game_layout = card()
        game_layout.addWidget(label(tr("Spiel & Java"), "section"))
        row = QHBoxLayout()
        row.addWidget(label(tr("Arbeitsspeicher für Minecraft")), 1)
        self.memory_input = QSpinBox()
        self.memory_input.setRange(1024, 32768)
        self.memory_input.setSingleStep(512)
        self.memory_input.setSuffix(" MB")
        self.memory_input.setValue(self.service.settings.memory_mb)
        row.addWidget(self.memory_input)
        game_layout.addLayout(row)
        game_layout.addWidget(label(tr("4096 MB sind ein guter Start. Lass genug RAM für dein Betriebssystem frei."), "muted", True))
        game_layout.addWidget(label(tr("Eigene Java-Datei (optional)")))
        java_row = QHBoxLayout()
        self.java_input = QLineEdit(self.service.settings.java_path)
        self.java_input.setPlaceholderText(tr("Automatisch die zur Minecraft-Version passende Laufzeit"))
        java_row.addWidget(self.java_input, 1)
        self.java_browse = button(tr("Auswählen …"), self.choose_java)
        java_row.addWidget(self.java_browse)
        game_layout.addLayout(java_row)
        game_layout.addWidget(label(tr("Leer lassen für automatische Installation. Ein eigener Pfad gilt für alle Versionen und muss zur gewählten Version passen."), "muted", True))
        layout.addWidget(game_frame)
        storage, storage_layout = card()
        storage_layout.addWidget(label(tr("Deine Dateien"), "section"))
        path_label = label(str(self.service.root), "muted", True)
        path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        storage_layout.addWidget(path_label)
        storage_layout.addWidget(button(tr("Datenordner öffnen ↗"), lambda: self.open_folder(self.service.root), "link"))
        layout.addWidget(storage)
        self.save_button = button(tr("Einstellungen speichern"), self.save_settings, "primary")
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        page.setWidget(inner)
        self.settings_content = inner
        self.stack.addWidget(page)

    def make_account_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(16)
        layout.addWidget(label("MICROSOFT · MINECRAFT JAVA", "eyebrow"))
        layout.addWidget(label(tr("Dein Konto. Deine Welten."), "heroTitle", True))
        layout.addWidget(label(tr("Verbinde dein Microsoft-Konto mit Minecraft-Java-Berechtigung. Die Anmeldung öffnet die offizielle Microsoft-Seite in deinem Browser."), "muted", True))
        self.auth_status_card, content = card()
        self.auth_badge = label(tr("EINRICHTUNG AUSSTEHEND"), "eyebrow")
        self.auth_heading = label(tr("Microsoft-Anmeldung noch nicht verfügbar"), "section", True)
        self.auth_details = label("", "muted", True)
        self.auth_details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content.addWidget(self.auth_badge)
        content.addWidget(self.auth_heading)
        content.addWidget(self.auth_details)
        self.auth_progress = QProgressBar()
        self.auth_progress.setRange(0, 4)
        self.auth_progress.setTextVisible(False)
        content.addWidget(self.auth_progress)
        self.auth_steps = []
        for text in (tr("Microsoft im Browser öffnen"), tr("Microsoft- und Xbox-Konto verbinden"), tr("Minecraft-Java-Profil und Lizenz prüfen"), tr("Anmeldung sicher speichern")):
            step = label("○  " + text, "muted", True)
            self.auth_steps.append(step)
            content.addWidget(step)
        self.auth_start_button = button(tr("Mit Microsoft anmelden ↗"), self.login, "primary")
        content.addWidget(self.auth_start_button)
        self.auth_play_button = button(tr("Weiter zum Online-Spielen →"), self.choose_online_mode, "primary")
        content.addWidget(self.auth_play_button)
        self.auth_cancel_button = button(tr("Anmeldung abbrechen"), self.cancel, "link")
        content.addWidget(self.auth_cancel_button)
        fallback = QHBoxLayout()
        self.auth_reopen_button = button(tr("Browser erneut öffnen ↗"), self.reopen_auth_browser, "link")
        self.auth_copy_button = button(tr("Anmeldelink kopieren"), self.copy_auth_link, "link")
        fallback.addWidget(self.auth_reopen_button)
        fallback.addWidget(self.auth_copy_button)
        fallback.addStretch()
        content.addLayout(fallback)
        self.auth_manage_logout = button(tr("Von Blockwerk abmelden"), self.logout, "link")
        content.addWidget(self.auth_manage_logout)
        self.auth_switch_button = button(tr("Anderes Microsoft-Konto verwenden ↗"), self.login, "link")
        content.addWidget(self.auth_switch_button)
        layout.addWidget(self.auth_status_card)
        safety, safe = card()
        safe.addWidget(label(tr("Deine Anmeldung bleibt bei Microsoft"), "section"))
        safe.addWidget(label(tr("E-Mail, Passwort und Bestätigungscodes gibst du ausschließlich auf Microsofts Website ein. Blockwerk erhält danach die Anmeldeberechtigung und prüft dein Minecraft-Java-Profil. Ein neues Microsoft-Konto enthält nicht automatisch Minecraft Java."), "muted", True))
        actions = QHBoxLayout()
        actions.addWidget(button(tr("Microsoft-Konto erstellen ↗"), lambda: self.open_url("https://signup.live.com/"), "link"))
        actions.addWidget(button(tr("Offiziellen Launcher öffnen ↗"), lambda: self.open_url("https://www.minecraft.net/download"), "link"))
        actions.addStretch()
        safe.addLayout(actions)
        layout.addWidget(safety)
        bottom = QHBoxLayout()
        self.auth_setup_button = button(tr("Einrichtung für Projektbetreiber →"), self.show_publisher_setup, "link")
        bottom.addWidget(self.auth_setup_button)
        bottom.addStretch()
        self.auth_local_button = button(tr("Lokal spielen →"), self.choose_local_mode)
        bottom.addWidget(self.auth_local_button)
        layout.addLayout(bottom)
        layout.addStretch()
        page.setWidget(inner)
        self.stack.addWidget(page)

    def open_account(self):
        self.navigate(6)
        self.refresh_auth_page()

    def toggle_publisher_setup(self):
        self.publisher_setup.setVisible(not self.publisher_setup.isVisible())

    def show_publisher_setup(self):
        if self.busy:
            return
        self.navigate(2)
        self.publisher_setup.show()
        self.client_input.setFocus()

    def choose_local_mode(self):
        if not self.busy:
            self.mode_combo.setCurrentIndex(1)
            self.navigate(0)

    def choose_online_mode(self):
        if not self.busy:
            self.mode_combo.setCurrentIndex(0)
            self.navigate(0)

    def receive_auth_link(self, url):
        self.auth_url = url if self.busy and self.active_task == "login" else ""
        self.refresh_auth_page()

    def reopen_auth_browser(self):
        if self.auth_url and self.busy and self.active_task == "login":
            self.open_url(self.auth_url)

    def copy_auth_link(self):
        if self.auth_url and self.busy and self.active_task == "login":
            QApplication.clipboard().setText(self.auth_url)
            self.show_status(tr("Anmeldelink kopiert. Öffne ihn in deinem Browser und kehre anschließend zu Blockwerk zurück."))

    def refresh_auth_page(self):
        if not hasattr(self, "auth_heading"):
            return
        configured = bool(self.service.settings.client_id)
        logging_in = self.busy and self.active_task == "login"
        connected = bool(self.username)
        if logging_in:
            badge, heading = tr("ANMELDUNG LÄUFT"), tr("Im Browser fortfahren") if self.auth_phase <= 1 else tr("Dein Konto wird geprüft")
            detail = tr("Wähle dein Microsoft-Konto im Browser aus. Wenn kein Fenster erscheint, öffne den Browser unten erneut oder kopiere den Anmeldelink. Die Anmeldung wartet höchstens fünf Minuten.") if self.auth_phase <= 1 else tr("Blockwerk verbindet dein Xbox-Profil und prüft, ob Minecraft Java für dein Konto verfügbar ist.")
        elif self.auth_error:
            badge, heading, detail = tr("ANMELDUNG NICHT ABGESCHLOSSEN"), tr("Bitte prüfe diesen Hinweis"), self.auth_error
        elif connected:
            badge, heading = tr("KONTO VERBUNDEN"), tr("Angemeldet als ") + self.username
            detail = tr("Minecraft Java wurde bei der Anmeldung geprüft. Die Berechtigung wird vor jedem Online-Spielstart erneut geprüft. ") + (tr("Die Anmeldung gilt nur für diese Sitzung, weil kein sicherer Kontospeicher verfügbar ist.") if self.service.accounts.session_only else tr("Deine Anmeldung wird im geschützten Kontospeicher des Betriebssystems verwahrt."))
        elif configured:
            badge, heading = tr("BEREIT ZUR ANMELDUNG"), tr("Mit deinem Microsoft-Konto fortfahren")
            detail = tr('Die Microsoft-App ist registriert. Die Minecraft-API-Freigabe bleibt offen. Eine vollständige Minecraft-Anmeldung ist deshalb nicht zugesichert. Der lokale Modus ohne Konto bleibt verfügbar.')
        else:
            badge, heading = tr("EINRICHTUNG AUSSTEHEND"), tr("Microsoft-Anmeldung noch nicht verfügbar")
            detail = tr("Blockwerk besitzt noch keine eigene freigegebene Microsoft-App-Kennung. Der Projektbetreiber muss den Launcher registrieren und für die Minecraft-API freigeben lassen. Du brauchst hier keine E-Mail-Adresse oder ein Passwort einzutragen. Lokale Profile bleiben verfügbar.")
        if logging_in and self.cancel_event.is_set():
            badge, heading, detail = tr("ABBRUCH LÄUFT"), tr("Anmeldung wird beendet"), tr("Eine laufende Anfrage wird noch abgeschlossen. Ihre Antwort wird danach verworfen; es wird keine neue Anmeldung gespeichert.")
        self.auth_badge.setText(badge)
        self.auth_heading.setText(heading)
        self.auth_details.setText(detail)
        phase = self.auth_phase if logging_in else 4 if connected and not self.auth_error else 0
        self.auth_progress.setValue(phase)
        steps = (tr("Microsoft im Browser öffnen"), tr("Microsoft- und Xbox-Konto verbinden"), tr("Minecraft-Java-Profil und Lizenz prüfen"), tr("Anmeldung sicher speichern"))
        for index, (step, text) in enumerate(zip(self.auth_steps, steps), 1):
            step.setText(("✓  " if index < phase or phase == 4 else "→  " if index == phase else "○  ") + text)
            step.setStyleSheet("color: #b8e285;" if phase and index <= phase else "color: #9eaea0;")
        self.auth_start_button.setText(tr("Erneut mit Microsoft anmelden ↗") if self.auth_error else tr("Mit Microsoft anmelden ↗"))
        self.auth_start_button.setVisible(not connected or bool(self.auth_error))
        self.auth_start_button.setEnabled(configured and not self.busy)
        self.auth_play_button.setVisible(connected and not self.auth_error and not logging_in)
        self.auth_play_button.setEnabled(not self.busy)
        self.auth_cancel_button.setVisible(logging_in)
        self.auth_cancel_button.setEnabled(not self.cancel_event.is_set())
        self.auth_reopen_button.setVisible(logging_in and bool(self.auth_url))
        self.auth_copy_button.setVisible(logging_in and bool(self.auth_url))
        self.auth_manage_logout.setVisible(connected)
        self.auth_manage_logout.setEnabled(not self.busy)
        self.auth_switch_button.setVisible(connected and not logging_in)
        self.auth_switch_button.setEnabled(not self.busy)
        self.auth_setup_button.setEnabled(not self.busy)
        self.auth_local_button.setEnabled(not self.busy)

    def make_about_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 0, 0)
        frame, content = card()
        content.addWidget(label(tr("Ein eigener Weg zu Minecraft Java."), "section"))
        content.addWidget(label("Blockwerk " + VERSION + tr(" ist ein unabhängiger Launcher für Windows, Linux und macOS. Er lädt originale Minecraft-Java-Dateien und verwendet den Microsoft-Login im Browser."), "muted", True))
        content.addWidget(label(tr("Für den Online-Modus brauchst du ein Microsoft-Konto mit Minecraft-Java-Berechtigung und eine freigegebene App-ID. Offline kannst du ein lokales Profil ohne Microsoft-Konto verwenden. Das ist keine Online-Identität und funktioniert nicht als Anmeldung für kontogeprüfte Server oder Realms."), "muted", True))
        content.addWidget(label(tr("Verfügbar sind Vollversionen ab 1.0 und Snapshots. Unter Welten stehen lokale Java-Spielstände aus Blockwerk, Minecraft und gewählten Ordnern. Vorbereitete Versionen lassen sich offline starten. Über ‚Spieldateien herunterladen‘ werden sie mit Internet eingerichtet, auch ohne Konto."), "muted", True))
        content.addWidget(label(tr("Deine Anmeldung"), "section"))
        content.addWidget(label(tr("Blockwerk fragt kein Passwort ab. Windows verwendet DPAPI, macOS den Schlüsselbund und Linux Secret Service. Fehlt der sichere Speicher, gilt die Anmeldung nur für die aktuelle Sitzung. Offline werden keine Tokens erneuert oder Dateien heruntergeladen. Abmelden entfernt die Microsoft-Sitzung; lokale Profile und Welten bleiben erhalten."), "muted", True))
        content.addWidget(button(tr("Minecraft herunterladen ↗"), lambda: self.open_url("https://www.minecraft.net/download"), "link"))
        content.addWidget(button(tr("Microsoft-Konto erstellen ↗"), lambda: self.open_url("https://signup.live.com/"), "link"))
        content.addWidget(button(tr("Anleitung & technische Hinweise ↗"), self.open_guide, "link"))
        content.addWidget(label(tr("Nicht von Mojang oder Microsoft entwickelt oder unterstützt. Minecraft ist eine Marke von Mojang/Microsoft. Es werden keine Spieldateien mitgeliefert."), "muted", True))
        layout.addWidget(frame)
        layout.addStretch()
        page.setWidget(inner)
        self.stack.addWidget(page)

    def make_mods_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        self.mods_content = QWidget()
        layout = QVBoxLayout(self.mods_content)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(14)
        layout.addWidget(label(tr("Eigene Mod-Profile mit getrennten Welten."), "section"))
        layout.addWidget(label(tr("Mods müssen zu Minecraft, Loader und Abhängigkeiten passen. Fabric API, Bibliotheken und andere benötigte Mods zusätzlich importieren. Unbekannte Metadaten werden nicht als Kompatibilitätsgarantie behandelt."), "muted", True))
        frame, form = card()
        self.mod_name_input = QLineEdit()
        self.mod_name_input.setPlaceholderText(tr("Neues Profil, z. B. Mein Fabric"))
        self.mod_name_input.setMaxLength(60)
        form.addWidget(self.mod_name_input)
        row = QHBoxLayout()
        self.mods_base_combo = QComboBox()
        self.mods_base_combo.setMinimumWidth(115)
        row.addWidget(self.mods_base_combo)
        self.mod_loader_combo = QComboBox()
        for identifier, name in LOADERS.items():
            self.mod_loader_combo.addItem(name, identifier)
        row.addWidget(self.mod_loader_combo)
        self.loader_version_combo = QComboBox()
        self.loader_version_combo.setMinimumWidth(130)
        row.addWidget(self.loader_version_combo, 1)
        row.addWidget(button(tr("Versionen laden"), self.load_loader_versions))
        self.mods_base_combo.currentTextChanged.connect(lambda *_: self.loader_version_combo.clear())
        self.mod_loader_combo.currentIndexChanged.connect(lambda *_: self.loader_version_combo.clear())
        form.addLayout(row)
        form.addWidget(button(tr("Profil erstellen & installieren"), self.create_mod_profile, "primary"))
        form.addWidget(label(tr("Fabric, Forge, Quilt und NeoForge: Installation mit passenden Versionen geprüft. Für andere Installer ‚Eigener Installer‘ wählen. Die Installation benötigt Internet; bestehende Profile lassen sich lokal starten."), "muted", True))
        layout.addWidget(frame)
        selected = QHBoxLayout()
        selected.addWidget(label(tr("MOD-PROFIL"), "eyebrow"))
        self.mods_profile_combo = QComboBox()
        self.mods_profile_combo.setMinimumContentsLength(20)
        self.mods_profile_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.mods_profile_combo.currentIndexChanged.connect(self.refresh_mods)
        selected.addWidget(self.mods_profile_combo, 1)
        selected.addWidget(button(tr("Zum Spielen auswählen →"), self.select_mod_profile))
        layout.addLayout(selected)
        self.mod_path_label = label(tr("Noch kein Mod-Profil vorhanden."), "muted", True)
        self.mod_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.mod_path_label)
        self.mods_table = QTableWidget(0, 4)
        self.mods_table.setHorizontalHeaderLabels([tr("Mod-Datei"), tr("Status"), tr("Loader"), tr("Hinweis")])
        self.mods_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.mods_table.verticalHeader().hide()
        self.mods_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.mods_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.mods_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.mods_table.setMinimumHeight(180)
        layout.addWidget(self.mods_table)
        actions = QHBoxLayout()
        actions.addWidget(button(tr("Mod-JARs hinzufügen …"), self.add_mod_files))
        actions.addWidget(button(tr("Aktiv / deaktiviert"), self.toggle_selected_mod))
        actions.addWidget(button(tr("Mod-Ordner öffnen ↗"), self.open_mod_folder, "link"))
        actions.addWidget(button(tr("Aktualisieren"), self.refresh_mods, "link"))
        layout.addLayout(actions)
        manual, manual_layout = card()
        manual_layout.addWidget(label(tr("Weitere Installer & vorhandene Profile"), "section"))
        manual_layout.addWidget(label(tr("Eigenen JAR-/EXE-Installer manuell ausführen. Im Installer den unten gezeigten Minecraft-Zielordner wählen. Danach die installierte Version suchen und übernehmen. Die Unterstützung hängt vom Dateiformat und Installer ab."), "muted", True))
        manual_layout.addWidget(button(tr("Minecraft-Zielordner öffnen ↗"), self.open_mod_game_root, "link"))
        manual_layout.addWidget(button(tr("Eigenen Installer öffnen …"), self.open_custom_installer))
        installed = QHBoxLayout()
        self.custom_version_combo = QComboBox()
        installed.addWidget(self.custom_version_combo, 1)
        installed.addWidget(button(tr("Suchen"), self.scan_custom_versions))
        installed.addWidget(button(tr("Installierte Version übernehmen"), self.adopt_custom_version))
        manual_layout.addLayout(installed)
        layout.addWidget(manual)
        page.setWidget(self.mods_content)
        self.stack.addWidget(page)

    def make_skins_page(self):
        page=QScrollArea()
        page.setWidgetResizable(True)
        self.skins_content=QWidget()
        layout=QVBoxLayout(self.skins_content)
        layout.setContentsMargins(0,0,12,0)
        layout.setSpacing(14)
        layout.addWidget(label(tr("Dein Look für Minecraft Java"), "section"))
        layout.addWidget(label(tr("Eigene Skin-PNGs hinzufügen oder einen der originalen Blockwerk-Skins auswählen. Die Vorschau lässt sich mit der Maus drehen."), "muted", True))
        row=QHBoxLayout()
        self.skin_list=QListWidget()
        self.skin_list.setMinimumWidth(190)
        self.skin_list.setMinimumHeight(270)
        self.skin_list.setMaximumHeight(360)
        self.skin_list.currentItemChanged.connect(self.skin_selected)
        row.addWidget(self.skin_list,1)
        self.skin_preview=SkinPreview()
        row.addWidget(self.skin_preview,1)
        layout.addLayout(row)
        actions=QHBoxLayout()
        actions.addWidget(button(tr("Skin-PNGs hinzufügen …"),self.add_skin_files))
        actions.addWidget(button(tr("PNG exportieren …"),self.export_skin))
        self.skin_variant=QComboBox()
        self.skin_variant.addItem(tr("Classic · breite Arme"),"classic")
        self.skin_variant.addItem(tr("Slim · schmale Arme"),"slim")
        self.skin_variant.currentIndexChanged.connect(self.skin_variant_changed)
        actions.addWidget(self.skin_variant)
        layout.addLayout(actions)
        self.skin_status=label(tr("Wähle einen Skin aus."),"muted",True)
        layout.addWidget(self.skin_status)
        local,content=card()
        content.addWidget(label(tr("Im lokalen Spiel anzeigen"), "section"))
        content.addWidget(label(tr("Das lokale Skinpaket ersetzt die Standardfiguren in der gewählten Spielinstanz. Es ist kein Konto-Skin: Andere Spieler sehen die Änderung nicht, und auch andere Standardfiguren können so aussehen. Die Armform richtet sich dabei nach dem Standardmodell des Spiels."),"muted",True))
        self.skin_target=label("", "muted", True)
        content.addWidget(self.skin_target)
        content.addWidget(button(tr("Lokales Skinpaket anwenden"),self.apply_local_skin,"primary"))
        content.addWidget(label(tr("Benötigt installierte Spieldateien mit version.json, gewöhnlich Minecraft 1.14 oder neuer. Eigene Ressourcenpakete bleiben ausgewählt; ein laufendes Spiel danach neu starten."),"muted",True))
        layout.addWidget(local)
        online,content=card()
        content.addWidget(label(tr("Als echten Minecraft-Konto-Skin verwenden"), "section"))
        content.addWidget(label(tr("Mit einer funktionierenden Microsoft-/Minecraft-Anmeldung kann der Skin im eigenen Konto geändert werden. Alternativ die PNG exportieren und auf der offiziellen Minecraft-Profilseite hochladen."),"muted",True))
        self.skin_online_button=button(tr("Im Microsoft-Konto anwenden"),self.apply_account_skin)
        content.addWidget(self.skin_online_button)
        content.addWidget(button(tr("Offizielle Skin-Profilseite öffnen ↗"),lambda:self.open_url("https://www.minecraft.net/msaprofile/mygames/editskin"),"link"))
        layout.addWidget(online)
        page.setWidget(self.skins_content)
        self.stack.addWidget(page)

    def refresh_skins(self):
        selected=self.skins.selected()
        self.skin_list.blockSignals(True)
        self.skin_list.clear()
        chosen=0
        for index,row in enumerate(self.skins.data()['items']):
            item=QListWidgetItem(row['name'])
            item.setData(Qt.ItemDataRole.UserRole,row['id'])
            item.setSizeHint(QSize(180,52))
            self.skin_list.addItem(item)
            if selected and row['id']==selected['id']:chosen=index
        self.skin_list.setCurrentRow(chosen)
        self.skin_list.blockSignals(False)
        self.skin_selected()

    def skin_selected(self,*_):
        item=self.skin_list.currentItem()
        if item is None:return
        try:
            identifier=item.data(Qt.ItemDataRole.UserRole)
            self.skins.select(identifier)
            row=self.skins.selected()
            image=load_skin(self.skins.path(identifier))
            self.skin_variant.blockSignals(True)
            self.skin_variant.setCurrentIndex(self.skin_variant.findData(row['variant']))
            self.skin_variant.setEnabled(image.height()==64)
            self.skin_variant.blockSignals(False)
            self.skin_preview.set_skin(image,row['variant'])
            self.skin_status.setText(tr("Ausgewählt: ")+row['name']+" · "+str(image.width())+" × "+str(image.height())+tr(" Pixel. Noch keine Kontoänderung durchgeführt."))
        except Exception as error:
            self.skin_status.setText(human_error(error))

    def skin_variant_changed(self,*_):
        row=self.skins.selected()
        if row:
            try:
                self.skins.select(row['id'],self.skin_variant.currentData())
                self.skin_preview.set_skin(load_skin(self.skins.path(row['id'])),self.skin_variant.currentData())
            except Exception as error:self.skin_status.setText(human_error(error))

    def add_skin_files(self):
        paths,_=QFileDialog.getOpenFileNames(self,tr("Java-Skin-PNGs auswählen"),"","Skin-PNG (*.png)")
        if not paths:return
        try:
            for path in paths:self.skins.add(Path(path),self.skin_variant.currentData())
            self.refresh_skins()
        except Exception as error:QMessageBox.warning(self,tr("Skin hinzufügen"),human_error(error))

    def export_skin(self):
        row=self.skins.selected()
        if not row:return
        target,_=QFileDialog.getSaveFileName(self,tr("Skin-PNG exportieren"),row['name']+'.png',"PNG (*.png)")
        if target:
            try:
                import shutil
                shutil.copy2(self.skins.path(row['id']),target)
                self.skin_status.setText(tr("Skin-PNG exportiert. Die Originaldatei bleibt unverändert."))
            except OSError as error:self.skin_status.setText(human_error(error))

    def apply_local_skin(self):
        if self.busy:return
        if not self.service.settings.offline_mode:self.mode_combo.setCurrentIndex(1)
        if not self.save_local_name():return
        version=self.launch_version()
        if not version:
            self.skin_status.setText(tr("Bitte unter Spielen zuerst eine Version auswählen und ihre Spieldateien herunterladen."))
            return
        service=self.active_service()
        directory=self.world_game_directory(service,version)
        self.run_task("skin_local",lambda:self.skins.local_pack(service,version,directory))

    def apply_account_skin(self):
        if not self.busy and self.username:
            self.run_task("skin_online",lambda:self.skins.apply_account(self.service,self.cancel_event))
            self.cancel_button.hide()  # An already submitted account change cannot be undone by cancel.

    def make_updates_page(self):
        page=QScrollArea()
        page.setWidgetResizable(True)
        self.updates_content=QWidget()
        layout=QVBoxLayout(self.updates_content)
        layout.setContentsMargins(0,0,12,0)
        layout.setSpacing(14)
        layout.addWidget(label(tr("Blockwerk aktuell halten"), "section"))
        layout.addWidget(label(tr("Nur der Launcher wird auf Updates geprüft. Minecraft-Versionen, Mods, Welten und die Minecraft-Versionsliste werden dabei nicht automatisch aktualisiert."),"muted",True))
        frame,content=card()
        content.addWidget(label(tr("INSTALLIERT · ")+VERSION,"eyebrow"))
        self.update_heading=label(tr("Noch keine Updateprüfung"), "section", True)
        self.update_status=label("", "muted", True)
        self.update_notes=label("", "muted", True)
        content.addWidget(self.update_heading)
        content.addWidget(self.update_status)
        content.addWidget(self.update_notes)
        self.update_automatic=QCheckBox(tr("Launcher jede Woche auf neue Versionen prüfen"))
        self.update_automatic.setChecked(bool(self.updates.state.get('automatic',True)))
        self.update_automatic.toggled.connect(self.set_weekly_updates)
        content.addWidget(self.update_automatic)
        content.addWidget(label(tr("Die Prüfung läuft beim Start oder während der Nutzung, sobald sieben Tage vergangen sind und der Launcher frei ist. Eine geschlossene App wird nicht aufgeweckt. Ein Neustart zur Installation erfolgt erst über den Knopf unten."),"muted",True))
        actions=QHBoxLayout()
        self.update_check_button=button(tr("Jetzt prüfen"),self.check_updates)
        self.update_download_button=button(tr("Updatepaket herunterladen"),self.download_update)
        actions.addWidget(self.update_check_button)
        actions.addWidget(self.update_download_button)
        content.addLayout(actions)
        self.update_install_button=button(tr("Installieren & Launcher neu starten"),self.install_update,"primary")
        content.addWidget(self.update_install_button)
        self.update_open_button=button(tr("Downloadordner öffnen ↗"),self.open_update_folder,"link")
        content.addWidget(self.update_open_button)
        content.addWidget(label(tr('Automatische Installation: portables Windows-Paket sowie Linux/macOS-Quellpakete. Native Linux/macOS-Builds werden manuell installiert. Eine Sicherung bleibt erhalten.'),"muted",True))
        layout.addWidget(frame)
        source,content=card()
        self.update_source_card=source
        content.addWidget(label(tr("Dein Updatekanal"), "section"))
        self.update_source_label=label("", "muted", True)
        self.update_source_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content.addWidget(self.update_source_label)
        content.addWidget(button(tr("Lokalen Updateordner wählen …"),self.choose_update_folder))
        content.addWidget(label(tr("Der lokale Kanal liest Blockwerk-Updates.json und das passende Paket aus dem Ausgabeordner. Ein Update ist erst verfügbar, wenn dort eine neue Launcher-Ausgabe veröffentlicht wurde."),"muted",True))
        self.update_url_input=QLineEdit()
        self.update_url_input.setPlaceholderText(tr("Optional: https://deine-webseite/Blockwerk-Updates.json"))
        content.addWidget(self.update_url_input)
        content.addWidget(button(tr("HTTPS-Updatequelle speichern"),self.set_update_url,"link"))
        layout.addWidget(source)
        page.setWidget(self.updates_content)
        self.stack.addWidget(page)

    def refresh_update_status(self):
        if not hasattr(self,'update_heading'):return
        info=self.update_info
        configured=bool(self.updates.source.get('location'))
        kind=tr("Lokaler Updatekanal") if self.updates.source['kind']=='local' else tr("HTTPS-Updatekanal")
        self.update_source_label.setText(kind+"\n"+(self.updates.source.get('location') or tr("Noch keine Quelle eingerichtet.")))
        if self.update_check_running:
            self.update_heading.setText(tr("Updatequelle wird geprüft …"))
        elif info and info['newer']:
            self.update_heading.setText(tr("Neue Launcher-Version: ")+info['version'])
        elif info:
            self.update_heading.setText(tr("Du verwendest die aktuelle Launcher-Version"))
        else:self.update_heading.setText(tr("Updatequelle bereit") if configured else tr("Updatequelle auswählen"))
        try:
            last=float(self.updates.state.get('last_check',0))
            text=tr("Zuletzt geprüft: ")+datetime.fromtimestamp(last).strftime('%d.%m.%Y %H:%M') if last else tr("Noch nicht geprüft.")
        except (TypeError,ValueError,OverflowError,OSError):text=tr("Noch nicht geprüft.")
        if info and info['newer'] and not info['available']:
            text+=tr(" Für dieses System liegt im Kanal noch kein Paket vor.")
        if self.update_package:text+=tr(" Geprüftes Paket heruntergeladen.")
        self.update_status.setText(text)
        self.update_notes.setText(info['notes'] if info else '')
        self.update_check_button.setEnabled(configured and not self.update_check_running and not self.busy)
        self.update_download_button.setEnabled(bool(info and info['available']) and not self.busy and not self.update_check_running)
        self.update_install_button.setEnabled(bool(self.update_package) and self.updates.can_install() and not self.busy and not self.update_check_running)
        self.language_combo.setEnabled(not self.busy and not self.update_check_running)
        self.update_source_card.setEnabled(not self.busy and not self.update_check_running)
        self.update_automatic.setEnabled(not self.busy and not self.update_check_running)
        self.update_open_button.setVisible(bool(self.update_package))
        self.updates_nav.setText("↑   Updates •" if info and info['newer'] else "↑   Updates")

    def set_weekly_updates(self,enabled):
        try:self.updates.set_automatic(enabled)
        except Exception as error:self.update_status.setText(human_error(error))

    def choose_update_folder(self):
        folder=QFileDialog.getExistingDirectory(self,tr("Ordner mit Blockwerk-Updates.json auswählen"))
        if folder:
            try:
                self.updates.set_source('local',str(Path(folder)/'Blockwerk-Updates.json'))
                self.update_info=None;self.update_package=None
                self.refresh_update_status()
                self.check_updates()
            except Exception as error:QMessageBox.warning(self,tr("Updatequelle"),human_error(error))

    def set_update_url(self):
        try:
            self.updates.set_source('https',self.update_url_input.text())
            self.update_info=None;self.update_package=None
            self.refresh_update_status()
            self.check_updates()
        except Exception as error:QMessageBox.warning(self,tr("Updatequelle"),human_error(error))

    def scheduled_update_check(self):
        if not self.closing and not self.busy and self.updates.due():self.check_updates()

    def check_updates(self):
        if self.busy or self.update_check_running or self.closing:return
        self.update_check_running=True
        self.refresh_update_status()
        def check():
            try:
                result=self.updates.check()
                if not self.closing:self.events.update_checked.emit(result)
            except Exception as error:
                if not self.closing:self.events.update_failed.emit(human_error(error))
        threading.Thread(target=check,daemon=True,name='Blockwerk-UpdateCheck').start()

    def update_checked(self,result):
        self.update_check_running=False
        if result.get('source')!=self.updates.source:
            self.refresh_update_status()
            return
        if not self.update_info or self.update_info['version']!=result['version']:self.update_package=None
        self.update_info=result
        self.refresh_update_status()

    def update_failed(self,message):
        self.update_check_running=False
        self.refresh_update_status()
        self.update_status.setText(message+tr(" Die vorhandene App bleibt verwendbar."))

    def download_update(self):
        if not self.busy and self.update_info and self.update_info['available']:
            self.run_task('update_download',lambda:self.updates.download(self.update_info,self.cancel_event,
                self.events.status.emit,self.events.progress.emit))

    def install_update(self):
        if self.busy or not self.update_package or not self.update_info:return
        self.run_task('update_prepare',lambda:self.updates.stage_update(self.update_info,self.update_package,
            self.cancel_event,self.events.status.emit))

    def open_update_folder(self):
        if self.update_package:self.open_folder(Path(self.update_package).parent)

    def make_worlds_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        self.worlds_content = QWidget()
        layout = QVBoxLayout(self.worlds_content)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(14)
        layout.addWidget(label(tr("Deine lokalen Minecraft-Java-Welten"), "section"))
        layout.addWidget(label(tr("Blockwerk-Profile, der normale Minecraft-Ordner und zusätzlich gewählte Ordner. Andere Quellen werden beim ersten Öffnen als Spielkopie übernommen. Neue Welten werden von Minecraft selbst erzeugt."), "muted", True))
        filters = QHBoxLayout()
        self.world_search = QLineEdit()
        self.world_search.setPlaceholderText(tr("Welt, Version oder Profil suchen …"))
        self.world_search.textChanged.connect(self.render_worlds)
        filters.addWidget(self.world_search, 1)
        filters.addWidget(button(tr("Ordner hinzufügen …"), self.add_world_root))
        filters.addWidget(button(tr("Aktualisieren"), self.refresh_worlds))
        layout.addLayout(filters)
        self.world_count = label(tr("Noch keine Welten geladen."), "eyebrow")
        layout.addWidget(self.world_count)
        self.world_table = QTableWidget(0, 5)
        self.world_table.setHorizontalHeaderLabels([tr("Welt"), "Minecraft", tr("Spielmodus"), tr("Zuletzt gespielt"), tr("Herkunft")])
        self.world_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.world_table.verticalHeader().hide()
        self.world_table.verticalHeader().setDefaultSectionSize(50)
        self.world_table.setMinimumHeight(210)
        self.world_table.setMaximumHeight(390)
        self.world_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.world_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.world_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.world_table.itemSelectionChanged.connect(self.world_selection_changed)
        self.world_table.cellDoubleClicked.connect(lambda *_: self.open_world())
        layout.addWidget(self.world_table, 1)
        self.world_detail = label(tr("Eine Welt auswählen oder ‚Neue Welt in Minecraft‘ verwenden."), "muted", True)
        self.world_detail.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.world_detail)
        actions = QHBoxLayout()
        self.world_open_button = button(tr("Welt spielen ▶"), self.open_world, "primary")
        self.world_copy_button = button(tr("In gewählter Version spielen …"), lambda: self.open_world(use_selection=True))
        actions.addWidget(self.world_open_button)
        actions.addWidget(self.world_copy_button)
        actions.addWidget(button(tr("Weltordner öffnen ↗"), self.open_world_folder, "link"))
        layout.addLayout(actions)
        target, content = card()
        self.world_target = label("", "section", True)
        content.addWidget(self.world_target)
        content.addWidget(label(tr("Bei älteren Versionen im Spiel ‚Einzelspieler‘ wählen. Für neue Welten dort ‚Neue Welt erstellen‘ anklicken und die gewünschten Einstellungen wählen. Fehlende Spieldateien benötigen einen Internet-Download."), "muted", True))
        bottom = QHBoxLayout()
        bottom.addWidget(button(tr("Neue Welt in Minecraft …"), self.new_world, "primary"))
        bottom.addWidget(button(tr("Spielprofil / Version wählen →"), lambda: self.navigate(0), "link"))
        content.addLayout(bottom)
        layout.addWidget(target)
        page.setWidget(self.worlds_content)
        self.stack.addWidget(page)
        self.world_selection_changed()

    def update_world_target(self):
        if hasattr(self, "world_target"):
            version = self.launch_version() or tr("Version auswählen")
            self.world_target.setText(tr("Gewählte Spielversion: ") + version + " · " + self.profile_combo.currentText())

    def refresh_worlds(self):
        if not self.busy:
            self.show_status(tr("Lokale Minecraft-Java-Welten werden gesucht …"))
            self.run_task("worlds", lambda: self.worlds.scan(self.cancel_event))

    def render_worlds(self, *_):
        if not hasattr(self, "world_table"):
            return
        query = self.world_search.text().casefold().strip()
        rows = [row for row in self.world_rows if query in (row["name"] + " " + row["minecraft_version"] + " " + row["source"]).casefold()]
        self.world_table.setRowCount(len(rows))
        self.world_count.setText(str(len(rows)) + " / " + str(len(self.world_rows)) + tr(" WELTEN"))
        for index, row in enumerate(rows):
            try:
                played = datetime.fromtimestamp(row["last_played"] / 1000).strftime("%d.%m.%Y %H:%M") if row["last_played"] else tr("Unbekannt")
            except (OSError, ValueError, OverflowError):
                played = tr("Unbekannt")
            values = (row["name"], row["minecraft_version"] or row["launch_version"] or tr("Unbekannt"), row["game_mode"], played, row["source"])
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row["id"])
                item.setToolTip(value + ("\n" + row["error"] if row["error"] else ""))
                if col == 0:
                    item.setIcon(app_icon())
                self.world_table.setItem(index, col, item)
        if rows:
            self.world_table.selectRow(0)
        self.world_selection_changed()

    def selected_world(self):
        index = self.world_table.currentRow()
        if index < 0 or self.world_table.item(index, 0) is None:
            raise LauncherError(tr("Bitte zuerst eine Welt auswählen."))
        identifier = self.world_table.item(index, 0).data(Qt.ItemDataRole.UserRole)
        return next(row for row in self.world_rows if row["id"] == identifier)

    def world_selection_changed(self):
        try:
            row = self.selected_world()
            self.world_detail.setText(row["name"] + "\n" + row["path"] + ("\n" + row["error"] if row["error"] else ""))
            selected = True
        except (LauncherError, StopIteration, AttributeError):
            selected = False
        self.world_open_button.setEnabled(selected)
        self.world_copy_button.setEnabled(selected)

    def add_world_root(self):
        path = QFileDialog.getExistingDirectory(self, tr("Minecraft-, saves- oder Weltordner auswählen"))
        if path:
            try:
                self.worlds.add_root(Path(path))
                self.refresh_worlds()
            except Exception as error:
                QMessageBox.warning(self, "Weltordner", human_error(error))

    def open_world_folder(self):
        try:
            path = Path(self.selected_world()["path"])
            if not path.is_dir():
                raise LauncherError(tr("Der Weltordner ist nicht mehr vorhanden."))
            self.open_folder(path)
        except Exception as error:
            self.show_status(human_error(error))

    def select_world_version(self, row):
        profile = row["profile_id"]
        if row["launch_version"]:
            index = self.profile_combo.findData(profile)
            if index < 0:
                raise LauncherError(tr("Das zugehörige Mod-Profil ist nicht mehr vorhanden."))
            self.profile_combo.setCurrentIndex(index)
        if row["mode"] in ("local", "community"):
            self.local_name_input.setText(row["player"])
            if not self.save_local_name():
                raise LauncherError(tr("Der lokale Spielername dieses Spielordners ist ungültig."))
            self.mode_combo.setCurrentIndex(1)
        if self.profile_combo.currentData():
            return
        version = row["launch_version"] or row["minecraft_version"]
        match = next((v for v in self.versions if normalized_version(v["id"]) == normalized_version(version)), None)
        if match is None and row["launch_version"]:
            try:
                metadata = self.service.version_metadata(version)
                if is_release(metadata) or is_snapshot(metadata):
                    match = {"id": version, "type": metadata["type"]}
                    self.versions.append(match)
            except (OSError, ValueError):
                pass
        if match:
            self.service.settings.selected_version = match["id"]
            self.version_kind_changed("Snapshots" if is_snapshot(match) else "Vollversionen")
            self.version_combo.setCurrentIndex(self.version_combo.findData(match["id"]))
        elif not self.launch_version():
            raise LauncherError(tr("Bitte zuerst einen Versionskatalog laden und die passende Spielversion auswählen."))

    def world_game_directory(self, service, version):
        return service.game_directory(version, self.service.settings.offline_name if self.service.settings.offline_mode else None)

    def open_world(self, checked=False, *, use_selection=False):
        if self.busy:
            return
        try:
            row = self.selected_world()
            if not use_selection:
                self.select_world_version(row)
            self.start_world_task(row)
        except Exception as error:
            QMessageBox.warning(self, tr("Welt öffnen"), human_error(error))

    def new_world(self):
        if not self.busy:
            try:
                self.start_world_task(None)
            except Exception as error:
                QMessageBox.warning(self, tr("Neue Welt"), human_error(error))

    def start_world_task(self, row):
        if not self.service.settings.offline_mode and not self.username:
            self.mode_combo.setCurrentIndex(1)
        if self.service.settings.offline_mode and not self.save_local_name():
            return
        version = self.launch_version()
        if not version:
            raise LauncherError(tr("Bitte zuerst eine Vollversion oder einen Snapshot auswählen."))
        identifier = self.profile_combo.currentData()
        if identifier and not self.profiles.read(identifier).get("installed"):
            raise LauncherError(tr("Bitte zuerst das gewählte Mod-Profil unter Mods & Loader installieren."))
        service = self.active_service()
        directory = self.world_game_directory(service, version)
        offline = self.service.settings.offline_mode
        community = self.servers.list() if offline else None
        base = self.profiles.read(identifier)["base"] if identifier else version
        force_copy = bool(row and row["minecraft_version"] and normalized_version(row["minecraft_version"]) != normalized_version(base))
        self.navigate(0)
        def work():
            if offline and not service.offline_available(version):
                service.prepare_local_version(version, self.cancel_event, self.events.status.emit, self.events.progress.emit)
            world = self.worlds.play_copy(row, directory, self.cancel_event, self.events.status.emit, force_copy=force_copy) if row else None
            if row is None:
                self.events.status.emit(tr("In Minecraft ‚Einzelspieler‘ → ‚Neue Welt erstellen‘ wählen. Minecraft erzeugt die neue Welt mit deinen Einstellungen."))
            if identifier:
                return self.profiles.launch(identifier, self.cancel_event, self.events.status.emit,
                    self.events.progress.emit, self.events.started.emit, offline=offline, community_servers=community, world_folder=world)
            return service.launch(version, self.cancel_event, self.events.status.emit,
                self.events.progress.emit, self.events.started.emit, offline=offline, community_servers=community, world_folder=world)
        self.run_task("world_launch", work)

    def make_servers_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        self.servers_content = QWidget()
        layout = QVBoxLayout(self.servers_content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(label(tr("Gespeicherte Server · ohne Launcher-Limit"), "section", True))
        layout.addWidget(label(tr("Lokales Profil ohne Microsoft-Anmeldung. Nur für Server, deren Betreiber lokale Profile zulässt. Keine Anmeldung für kontogeprüfte Server oder Realms. Füge beliebig viele Favoriten hinzu oder speichere Server direkt im Minecraft-Menü Mehrspieler."), "muted", True))
        self.server_count = label("0 Server", "eyebrow")
        layout.addWidget(self.server_count)
        self.server_table = QTableWidget(0, 2)
        self.server_table.setHorizontalHeaderLabels([tr("Name"), tr("Serveradresse")])
        self.server_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.server_table.verticalHeader().hide()
        self.server_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.server_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.server_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.server_table.setMinimumHeight(200)
        self.server_table.setMaximumHeight(320)
        layout.addWidget(self.server_table, 1)
        row = QHBoxLayout()
        self.server_name_input = QLineEdit()
        self.server_name_input.setPlaceholderText(tr("Servername"))
        self.server_name_input.setMaxLength(80)
        self.server_address_input = QLineEdit()
        self.server_address_input.setPlaceholderText(tr("spiel.example.org:25565"))
        self.server_address_input.setMaxLength(255)
        row.addWidget(self.server_name_input)
        row.addWidget(self.server_address_input, 1)
        self.server_add_button = button(tr("Hinzufügen"), self.add_server)
        row.addWidget(self.server_add_button)
        layout.addLayout(row)
        bottom = QHBoxLayout()
        bottom.addWidget(button(tr("Aus Liste entfernen"), self.remove_server))
        bottom.addStretch()
        bottom.addWidget(button(tr("Offline-Modus auswählen →"), self.select_offline_mode, "primary"))
        layout.addLayout(bottom)
        layout.addWidget(label(tr("Neue Favoriten werden beim Offline-Start einmalig zur Serverliste des gewählten Spielprofils hinzugefügt. Im Spiel unter Mehrspieler kannst du Server hinzufügen, bearbeiten und entfernen. Diese Änderungen bleiben erhalten. Die Serverliste gehört zum jeweiligen Spielprofil und zur Version."), "muted", True))
        page.setWidget(self.servers_content)
        self.stack.addWidget(page)

    def active_service(self):
        identifier = self.profile_combo.currentData()
        return self.profiles.service(identifier) if identifier else self.service

    def launch_version(self):
        identifier = self.profile_combo.currentData()
        if identifier:
            data = self.profiles.read(identifier)
            return data.get("installed") or data["base"]
        return self.version_combo.currentData()

    def profile_changed(self, *_):
        if not hasattr(self, "status"):
            return
        identifier = self.profile_combo.currentData() or ""
        self.service.settings.selected_profile = identifier
        try:
            self.service.settings.save(self.service.root)
            if identifier:
                data = self.profiles.read(identifier)
                if self.service.settings.version_filter != "Vollversionen":
                    self.version_kind_changed("Vollversionen")
                index = self.version_combo.findData(data["base"])
                if index >= 0:
                    self.version_combo.setCurrentIndex(index)
            self.version_combo.setEnabled(not self.busy and not identifier)
            self.version_kind_combo.setEnabled(not self.busy and not identifier)
            self.version_changed()
        except Exception as error:
            self.show_status(human_error(error))

    def refresh_profiles(self, selected=None):
        selected = selected if isinstance(selected, str) else self.profile_combo.currentData() or ""
        managed = self.mods_profile_combo.currentData()
        rows = self.profiles.list()
        self.profile_combo.blockSignals(True)
        self.mods_profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItem("Vanilla", "")
        self.mods_profile_combo.clear()
        for data in rows:
            name = data["name"] + " · " + LOADERS[data["loader"]] + " · " + data["base"]
            if not data.get("installed"):
                name += tr(" (noch installieren)")
            self.profile_combo.addItem(name, data["id"])
            self.mods_profile_combo.addItem(name, data["id"])
        self.profile_combo.setCurrentIndex(max(0, self.profile_combo.findData(selected)))
        self.mods_profile_combo.setCurrentIndex(max(0, self.mods_profile_combo.findData(selected or managed)))
        self.profile_combo.blockSignals(False)
        self.mods_profile_combo.blockSignals(False)
        self.profile_changed()
        self.refresh_mods()

    def load_loader_versions(self):
        loader = self.mod_loader_combo.currentData()
        if loader == "custom":
            self.show_status(tr("Für eigene Installer erst ein Profil erstellen, dann die lokale Installer-Datei öffnen."))
            return
        base = self.mods_base_combo.currentText()
        if not base:
            self.show_status(tr("Bitte zuerst den Minecraft-Versionskatalog laden."))
            return
        self.run_task("loader_versions", lambda: self.profiles.loader_versions(loader, base))

    def create_mod_profile(self):
        if self.busy:
            return
        try:
            data = self.profiles.create(self.mod_name_input.text(), self.mods_base_combo.currentText(),
                                        self.mod_loader_combo.currentData(), self.loader_version_combo.currentText())
            self.refresh_profiles(data["id"])
            self.run_task("mod_install", lambda: self.profiles.install(data["id"], self.cancel_event,
                          self.events.status.emit, self.events.progress.emit))
        except Exception as error:
            QMessageBox.warning(self, tr("Mod-Profil"), human_error(error))

    def selected_mod_id(self):
        identifier = self.mods_profile_combo.currentData()
        if not identifier:
            raise LauncherError(tr("Bitte zuerst ein Mod-Profil erstellen oder auswählen."))
        return identifier

    def refresh_mods(self, *_):
        if not hasattr(self, "mods_table"):
            return
        self.mods_table.setRowCount(0)
        identifier = self.mods_profile_combo.currentData()
        if not identifier:
            self.mod_path_label.setText(tr("Noch kein Mod-Profil vorhanden."))
            return
        try:
            service = self.profiles.service(identifier)
            self.mod_path_label.setText("Minecraft-Zielordner: " + str(service.game_root) + "\nMod-Ablage: " + str(self.profiles.mod_folder(identifier)))
            rows = self.profiles.mods(identifier)
            self.mods_table.setRowCount(len(rows))
            for index, row in enumerate(rows):
                values = [row["file"], tr("Aktiv") if row["enabled"] else tr("Deaktiviert"), ", ".join(row["loaders"]) or tr("Unbekannt"), row["hint"]]
                for col, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setToolTip(value)
                    item.setData(Qt.ItemDataRole.UserRole, row["file"])
                    self.mods_table.setItem(index, col, item)
        except Exception as error:
            self.show_status(human_error(error))

    def select_mod_profile(self):
        try:
            index = self.profile_combo.findData(self.selected_mod_id())
            self.profile_combo.setCurrentIndex(index)
            self.navigate(0)
        except LauncherError as error:
            self.show_status(str(error))

    def add_mod_files(self):
        try:
            identifier = self.selected_mod_id()
            files, _ = QFileDialog.getOpenFileNames(self, tr("Mod-JARs auswählen"), "", "Minecraft-Mods (*.jar)")
            if files:
                count = self.profiles.add_mods(identifier, [Path(file) for file in files])
                self.refresh_mods()
                self.show_status(str(count) + tr(" Mod-Dateien importiert. Abhängigkeiten und Hinweise prüfen."))
        except Exception as error:
            QMessageBox.warning(self, tr("Mods importieren"), human_error(error))

    def toggle_selected_mod(self):
        row = self.mods_table.currentRow()
        if row < 0:
            self.show_status(tr("Bitte eine Mod-Datei auswählen."))
            return
        try:
            self.profiles.toggle_mod(self.selected_mod_id(), self.mods_table.item(row, 0).data(Qt.ItemDataRole.UserRole))
            self.refresh_mods()
        except Exception as error:
            self.show_status(human_error(error))

    def open_mod_folder(self):
        try:
            self.open_folder(self.profiles.mod_folder(self.selected_mod_id()))
        except LauncherError as error:
            self.show_status(str(error))

    def open_mod_game_root(self):
        try:
            self.open_folder(self.profiles.service(self.selected_mod_id()).game_root)
        except LauncherError as error:
            self.show_status(str(error))

    def open_custom_installer(self):
        try:
            identifier = self.selected_mod_id()
            service = self.profiles.service(identifier)
            data = self.profiles.read(identifier)
            if not (service.game_root / "versions" / data["base"]).exists():
                raise LauncherError(tr("Bitte zuerst das Profil erstellen und die Basisdateien installieren."))
            file, _ = QFileDialog.getOpenFileName(self, tr("Lokalen Installer auswählen"), "", "Installer (*.jar *.exe)")
            if not file:
                return
            QMessageBox.information(self, tr("Installer-Zielordner"), tr("Im Installer diesen Minecraft-Ordner auswählen:\n\n") + str(service.game_root) + tr("\n\nDanach ‚Suchen‘ und ‚Installierte Version übernehmen‘ verwenden."))
            self.run_task("custom_installer", lambda: self.profiles.run_installer(identifier, Path(file)))
        except Exception as error:
            QMessageBox.warning(self, "Installer", human_error(error))

    def scan_custom_versions(self):
        self.custom_version_combo.clear()
        try:
            self.custom_version_combo.addItems(self.profiles.installed_versions(self.selected_mod_id()))
        except LauncherError as error:
            self.show_status(str(error))

    def adopt_custom_version(self):
        try:
            identifier = self.selected_mod_id()
            version = self.custom_version_combo.currentText()
            if not version:
                raise LauncherError(tr("Bitte erst installierte Versionen suchen und auswählen."))
            self.run_task("mod_adopt", lambda: self.profiles.adopt(identifier, version, self.cancel_event,
                          self.events.status.emit, self.events.progress.emit))
        except LauncherError as error:
            self.show_status(str(error))

    def refresh_servers(self):
        try:
            rows = self.servers.list()
            self.server_table.setRowCount(len(rows))
            self.server_count.setText(str(len(rows)) + " Server")
            self.server_add_button.setEnabled(not self.busy)
            for index, row in enumerate(rows):
                for col, value in enumerate((row["name"], row["address"])):
                    item = QTableWidgetItem(value)
                    item.setData(Qt.ItemDataRole.UserRole, row["id"])
                    self.server_table.setItem(index, col, item)
        except Exception as error:
            self.show_status(human_error(error))

    def add_server(self):
        try:
            self.servers.add(self.server_name_input.text(), self.server_address_input.text())
            self.server_name_input.clear()
            self.server_address_input.clear()
            self.refresh_servers()
        except Exception as error:
            QMessageBox.warning(self, tr("Server speichern"), human_error(error))

    def remove_server(self):
        row = self.server_table.currentRow()
        if row < 0:
            return
        try:
            self.servers.remove(self.server_table.item(row, 0).data(Qt.ItemDataRole.UserRole))
            self.refresh_servers()
        except Exception as error:
            self.show_status(human_error(error))

    def select_offline_mode(self):
        self.mode_combo.setCurrentIndex(1)
        self.navigate(0)

    def navigate(self, index):
        if not hasattr(self, "stack"):
            return
        self.stack.setCurrentIndex(index)
        self.title_label.setText([tr("Spielen"), tr("Versionen"), tr("Einstellungen"), tr("Über Blockwerk"), tr("Mods & Loader"), "Server", tr("Microsoft-Konto"), tr("Welten"), "Skins", tr("Launcher-Updates")][index])
        for i, nav in enumerate(self.nav_buttons):
            nav.setChecked(nav.property("pageIndex") == index)
        if index == 7 and hasattr(self, "world_table"):
            self.update_world_target()
            if not self.worlds_loaded and not self.busy:
                self.refresh_worlds()
        elif index==8:
            self.skin_target.setText(tr("Gewähltes Spielprofil: ")+self.profile_combo.currentText()+" · "+(self.launch_version() or tr("Version unter Spielen auswählen")))
            self.skin_online_button.setEnabled(bool(self.username) and not self.busy)
        elif index==9:self.refresh_update_status()

    def read_account(self):
        try:
            account = self.service.accounts.read()
            self.username = account["name"] if account and account["client_id"] == self.service.settings.client_id else ""
        except LauncherError as error:
            self.show_status(str(error))

    def update_account(self):
        configured = bool(self.service.settings.client_id)
        offline = self.service.settings.offline_mode
        self.notice.setVisible(not configured and not offline)
        self.local_profile_row.setVisible(offline)
        self.prepare_button.setVisible(offline)
        self.account_name.setText(self.service.settings.offline_name if offline else self.username or tr("Nicht angemeldet"))
        self.account_note.setText(tr("Lokales Profil · ohne Konto") if offline else (tr("Anmeldung gespeichert") if self.service.accounts.persistent else tr("Nur für diese Sitzung")) if self.username else tr("Launcher-Einrichtung fehlt") if not configured else tr("Microsoft-Konto benötigt"))
        self.login_button.setVisible(True)
        self.login_button.setText(tr("Konto verwalten") if self.username else tr("Microsoft-Konto"))
        self.logout_button.setVisible(bool(self.username) or self.service.accounts.persistent or self.service.accounts.path.exists())
        self.signup_button.setVisible(not self.username and not offline)
        if self.playing:
            self.play_button.setText(tr("Minecraft läuft …"))
        elif offline:
            self.play_button.setText(tr("Offline starten  ▶"))
        elif not configured:
            self.play_button.setText(tr("Microsoft-Konto öffnen →"))
        elif not self.username:
            self.play_button.setText(tr("Mit Microsoft anmelden →"))
        else:
            self.play_button.setText(tr("Minecraft starten  ▶"))
        self.play_button.setEnabled(not self.busy and (not self.username or bool(self.version_combo.currentData())))
        self.install_note.setText(tr("Ohne Konto · Einzelspieler und Server mit lokalen Profilen") if offline else tr("Originale Downloads · Passendes Java automatisch"))
        self.refresh_auth_page()
        if hasattr(self,'skin_online_button'):self.skin_online_button.setEnabled(bool(self.username) and not self.busy)

    def set_busy(self, busy):
        self.busy = busy
        self.language_combo.setEnabled(not busy and not self.update_check_running)
        self.login_button.setEnabled(not busy)
        self.logout_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        self.choose_button.setEnabled(not busy)
        self.version_combo.setEnabled(not busy and not bool(self.profile_combo.currentData()))
        self.mode_combo.setEnabled(not busy)
        self.profile_combo.setEnabled(not busy)
        self.version_kind_combo.setEnabled(not busy and not bool(self.profile_combo.currentData()))
        self.mods_content.setEnabled(not busy)
        self.servers_content.setEnabled(not busy)
        self.worlds_content.setEnabled(not busy)
        self.skins_content.setEnabled(not busy)
        self.updates_content.setEnabled(not busy)
        self.local_name_input.setEnabled(not busy)
        self.prepare_button.setEnabled(not busy)
        self.settings_content.setEnabled(not busy)
        self.cancel_button.setVisible(busy and not self.playing)
        if not busy:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
        self.update_account()
        self.refresh_update_status()

    def run_task(self, kind, function):
        if self.busy:
            return
        self.cancel_event = threading.Event()
        self.active_task = kind
        self.set_busy(True)
        self.progress_bar.setRange(0, 0)

        def work():
            try:
                result = function()
                self.events.finished.emit(kind, result)
            except Exception as error:
                self.events.failed.emit(kind, human_error(error))

        threading.Thread(target=work, daemon=True, name="Blockwerk-" + kind).start()

    def show_status(self, text):
        text = tr(text)
        self.status.setText(text)
        if self.active_task == "login":
            if text.startswith((tr("Bitte im Microsoft-Browser"), tr("Bitte im Microsoft-Browserfenster anmelden …"))):
                self.auth_phase = 1
            elif text.startswith((tr("Microsoft und Xbox"), tr("Microsoft und Xbox werden verbunden …"))):
                self.auth_phase = 2
            elif text.startswith((tr("Deine Minecraft-Java-Lizenz"), tr("Deine Minecraft-Java-Lizenz wird geprüft …"))):
                self.auth_phase = 3
            self.refresh_auth_page()
        if hasattr(self, "activity"):
            previous = getattr(self, "_last_status", "")
            if previous != text:
                self.activity.appendPlainText(datetime.now().strftime("%H:%M") + "  " + text)
                self._last_status = text

    def show_progress(self, value, maximum):
        self.progress_bar.setRange(0, max(1, maximum))
        self.progress_bar.setValue(min(maximum, max(0, value)))

    def game_started(self):
        self.playing = True
        self.cancel_button.hide()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.update_account()

    def finished(self, kind, result):
        self.playing = False
        self.active_task = ""
        if kind == "login":
            self.auth_url = ""
            self.auth_error = ""
            self.auth_phase = 4
        self.set_busy(False)
        if kind == "versions":
            self.versions, cached = result
            self.populate_combo()
            self.render_versions()
            self.show_status((tr("Lokaler Release-Katalog geladen. Vorbereitete Versionen sind offline startbar.") if cached else
                              str(len(self.versions)) + tr(" Vollversionen und Snapshots aus dem Mojang-Katalog geladen.")))
        elif kind == "worlds":
            self.world_rows = result
            self.worlds_loaded = True
            self.render_worlds()
            self.show_status(str(len(result)) + tr(" lokale Java-Welten gefunden."))
        elif kind=='skin_local':
            self.skin_status.setText(tr("Lokales Skinpaket aktiviert. Starte das gewählte Spielprofil neu. Das Paket ändert Standardfiguren nur auf diesem Gerät."))
            self.show_status(tr("Lokales Skinpaket im gewählten Spielordner aktiviert."))
        elif kind=='skin_online':
            self.skin_status.setText(tr("Minecraft hat den Konto-Skin ‚")+str(result)+tr("‘ übernommen. Ein laufendes Spiel danach neu starten."))
            self.show_status(tr("Minecraft-Konto-Skin erfolgreich geändert."))
        elif kind=='update_download':
            self.update_package=Path(result)
            self.refresh_update_status()
            self.show_status(tr("Launcher-Update heruntergeladen; Größe und SHA256 sind geprüft."))
        elif kind=='update_prepare':
            try:
                self.updates.start_helper(result)
                self.close()
            except Exception as error:
                self.update_status.setText(human_error(error))
            return
        elif kind == "login":
            self.username = result
            self.update_account()
            self.navigate(6)
            self.show_status(tr("Angemeldet als ") + result + tr(". Minecraft Java ist verfügbar.") +
                             (tr(" Anmeldung gilt nur für diese Sitzung; sicherer Kontospeicher ist nicht verfügbar.") if self.service.accounts.session_only else ""))
        elif kind in ("launch", "world_launch"):
            self.worlds_loaded = False
            self.render_versions()
            self.version_changed()
            if result == 0:
                self.show_status(tr("Minecraft wurde beendet. Bereit für dein nächstes Abenteuer."))
            else:
                self.show_status(tr("Minecraft wurde mit Fehlercode ") + str(result) + tr(" beendet. Prüfe logs und crash-reports im Spielordner."))
                QMessageBox.warning(self, tr("Minecraft wurde beendet"), self.status.text())
        elif kind == "prepare":
            self.version_changed()
            self.render_versions()
            self.show_status("Minecraft " + str(result) + tr(" ist vorbereitet. Du kannst jetzt offline ohne Microsoft-Konto starten."))
        elif kind == "loader_versions":
            self.loader_version_combo.clear()
            self.loader_version_combo.addItems(result)
            self.show_status(str(len(result)) + tr(" passende Loader-Versionen geladen."))
        elif kind in ("mod_install", "mod_adopt"):
            self.refresh_profiles(result["id"])
            self.show_status(tr("Mod-Profil ‚") + result["name"] + tr("‘ ist vorbereitet. Mods als passende JAR-Dateien hinzufügen."))
        elif kind == "custom_installer":
            self.scan_custom_versions()
            self.show_status(tr("Installer beendet (Code ") + str(result) + tr("). Installiertes Profil auswählen und übernehmen."))

    def failed(self, kind, message):
        self.playing = False
        self.active_task = ""
        if kind == "login":
            self.auth_url = ""
            self.auth_phase = 0
            self.auth_error = tr("Anmeldung abgebrochen. Du kannst es erneut versuchen.") if self.cancel_event.is_set() else message
        self.set_busy(False)
        if kind == "versions" and not self.versions:
            self.version_combo.clear()
            self.version_combo.addItem(tr("Keine Versionen geladen"), "")
            self.version_count.setText(tr("Keine Versionen. Nutze Aktualisieren, sobald du online bist."))
            self.update_account()
        self.show_status(message)
        if kind == "login":
            self.navigate(6)
            self.refresh_auth_page()
            return
        if kind.startswith('skin_'):
            self.skin_status.setText(message)
        if kind.startswith('update_'):
            self.refresh_update_status()
            self.update_status.setText(message)
        if not self.cancel_event.is_set():
            QMessageBox.warning(self, tr("Vorgang nicht abgeschlossen"), message)

    def reload_versions(self, *, online=False):
        if self.busy or self.closing:
            return
        offline = self.service.settings.offline_mode and not online
        self.show_status(tr("Lokaler Versionskatalog wird geladen …") if offline else tr("Versionskatalog wird von Mojang geladen …"))
        self.run_task("versions", lambda: self.service.list_versions(offline=offline))

    def version_kind_changed(self, kind):
        kind = source_text(kind)
        if not hasattr(self, "filter_combo"):
            return
        for combo in (self.version_kind_combo, self.filter_combo):
            combo.blockSignals(True)
            combo.setCurrentText(tr(kind))
            combo.blockSignals(False)
        self.service.settings.version_filter = kind
        if kind == "Snapshots" and self.profile_combo.currentData():
            self.profile_combo.setCurrentIndex(0)
        self.populate_combo()
        self.render_versions()

    def mode_changed(self, *_):
        if not hasattr(self, "stack") or not hasattr(self, "status"):
            return
        self.service.settings.offline_mode = self.mode_combo.currentIndex() != 0
        self.service.settings.community_mode = False
        try:
            self.service.settings.save(self.service.root)
        except OSError as error:
            self.show_status(human_error(error))
        self.update_account()
        self.show_status(tr("Offline: Einzelspieler oder Mehrspieler öffnen. Server müssen lokale Profile zulassen. Serverlisten werden im Spiel gespeichert.") if self.service.settings.offline_mode else tr("Online: Anmeldung, Lizenzprüfung und Downloads sind aktiv."))

    def populate_combo(self):
        selected = self.service.settings.selected_version
        releases = filter_versions(self.versions, "Releases")
        choices = filter_versions(self.versions, self.service.settings.version_filter)
        self.version_combo.blockSignals(True)
        self.version_combo.clear()
        for version in choices:
            self.version_combo.addItem(version["id"], version["id"])
        if not choices:
            self.version_combo.addItem(tr("Keine Einträge – Versionsliste aktualisieren"), "")
        index = self.version_combo.findData(selected)
        if index >= 0:
            self.version_combo.setCurrentIndex(index)
        self.version_combo.blockSignals(False)
        selected = self.mods_base_combo.currentText()
        self.mods_base_combo.clear()
        self.mods_base_combo.addItems([v["id"] for v in releases])
        if selected:
            self.mods_base_combo.setCurrentText(selected)
        if self.profile_combo.currentData():
            self.profile_changed()
        else:
            self.version_changed()

    def version_changed(self, *_):
        version = self.launch_version()
        if version:
            if not self.profile_combo.currentData():
                self.service.settings.selected_version = version
            try:
                self.service.settings.save(self.service.root)
            except OSError as error:
                self.show_status(human_error(error))
            active = self.active_service()
            installed = (active.game_root / "versions" / version / (version + ".jar")).exists()
            self.version_note.setText(tr("Offline vorbereitet · Prüfung beim Start") if active.offline_available(version) else tr("Über ‚Spieldateien herunterladen‘ vorbereiten") if self.service.settings.offline_mode else tr("Dateien vorhanden · Prüfung beim Start") if installed else tr("Wird beim ersten Start heruntergeladen"))
        self.update_account()
        if hasattr(self, "world_target"):
            self.update_world_target()

    def render_versions(self, *_):
        if not hasattr(self, "table"):
            return
        versions = filter_versions(self.versions, self.filter_combo.currentText(), self.search.text().strip())
        self.version_count.setText(str(len(versions)) + tr(" von ") + str(len(self.versions)) + tr(" Versionen"))
        self.table.setRowCount(len(versions))
        names = {"release": "Release", "snapshot": "Snapshot", "old_alpha": "Alpha / Classic", "old_beta": "Beta"}
        for row, version in enumerate(versions):
            installed = (self.service.game_root / "versions" / version["id"] / (version["id"] + ".jar")).exists()
            date = version.get("releaseTime", "")[:10]
            cells = [version["id"], names.get(version.get("type"), version.get("type", "")), date, tr("Offline vorbereitet") if self.service.offline_available(version["id"]) else tr("Vorhanden") if installed else tr("Download verfügbar")]
            for column, value in enumerate(cells):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, version["id"])
                self.table.setItem(row, column, item)
        if versions:
            self.table.selectRow(0)

    def choose_table_version(self):
        if self.busy:
            return
        row = self.table.currentRow()
        if row < 0:
            self.show_status(tr("Bitte zuerst eine Version in der Liste auswählen."))
            return
        version = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.profile_combo.setCurrentIndex(0)
        self.service.settings.selected_version = version
        self.populate_combo()
        self.navigate(0)
        self.show_status("Minecraft " + version + tr(" ausgewählt."))

    def login(self):
        if self.busy:
            return
        if self.service.settings.offline_mode:
            self.mode_combo.setCurrentIndex(0)
        entered = self.client_input.text().strip()
        if entered and entered != self.service.settings.client_id:
            try:
                expected_id = valid_client_id(entered)
            except LauncherError as error:
                QMessageBox.warning(self, tr("App-ID prüfen"), str(error))
                return
            self.save_settings()
            if self.service.settings.client_id != expected_id:
                return
        if not self.service.settings.client_id:
            self.auth_error = ""
            self.open_account()
            self.show_status(tr("Die Microsoft-Anmeldung wartet auf die Registrierung und Freigabe des Launchers durch den Projektbetreiber."))
            return
        self.auth_error = ""
        self.auth_phase = 0
        self.auth_url = ""
        self.navigate(6)
        self.run_task("login", lambda: self.service.login(self.cancel_event, self.events.status.emit, self.events.auth_link.emit))

    def logout(self):
        if self.busy:
            return
        try:
            self.service.accounts.delete()
            self.username = ""
            self.auth_error = ""
            self.auth_phase = 0
            self.auth_url = ""
            self.update_account()
            self.show_status(tr("Lokal abgemeldet. Deine Minecraft-Dateien und Welten bleiben erhalten."))
        except OSError as error:
            self.show_status(human_error(error))

    def play(self):
        if self.busy:
            return
        offline = self.service.settings.offline_mode
        if offline and not self.save_local_name():
            return
        if not offline and (not self.service.settings.client_id or not self.username):
            self.login()
            return
        version = self.launch_version()
        if not version:
            self.navigate(1)
            return
        self._last_progress_time = 0.0

        def progress(value, maximum):
            now = time.monotonic()
            if now - self._last_progress_time > .08 or value >= maximum or value == 0:
                self.events.progress.emit(value, maximum)
                self._last_progress_time = now

        try:
            community = self.servers.list() if offline else None
        except LauncherError as error:
            self.show_status(str(error))
            return
        identifier = self.profile_combo.currentData()
        if identifier:
            self.run_task("launch", lambda: self.profiles.launch(identifier, self.cancel_event,
                          self.events.status.emit, progress, self.events.started.emit, offline=offline, community_servers=community))
        else:
            self.run_task("launch", lambda: self.service.launch(version, self.cancel_event,
                          self.events.status.emit, progress, self.events.started.emit, offline=offline, community_servers=community))

    def save_local_name(self):
        try:
            self.service.settings.offline_name = local_profile(self.local_name_input.text())["name"]
            self.service.settings.save(self.service.root)
            self.update_account()
            return True
        except Exception as error:
            self.show_status(human_error(error))
            return False

    def prepare_local(self):
        if self.busy or not self.save_local_name():
            return
        identifier = self.profile_combo.currentData()
        if identifier:
            self.run_task("mod_install", lambda: self.profiles.install(identifier, self.cancel_event,
                          self.events.status.emit, self.events.progress.emit))
            return
        version = self.version_combo.currentData()
        if not version:
            self.show_status(tr("Bitte zuerst eine Version laden und auswählen. Für den Katalog einmal auf Online stellen und Aktualisieren klicken."))
            return
        self.run_task("prepare", lambda: self.service.prepare_local_version(version, self.cancel_event,
                      self.events.status.emit, self.events.progress.emit))

    def cancel(self):
        if self.playing:
            return
        self.cancel_event.set()
        self.auth_url = ""
        self.show_status(tr("Anmeldung wird abgebrochen. Eine laufende Anfrage wird noch abgeschlossen …") if self.active_task == "login" else tr("Abbruch angefordert. Ein laufender Download wird noch abgeschlossen …"))
        self.cancel_button.setEnabled(False)
        QTimer.singleShot(500, lambda: self.cancel_button.setEnabled(True))

    def save_settings(self):
        if self.busy:
            return
        try:
            client_id = valid_client_id(self.client_input.text()) if self.client_input.text().strip() else ""
            java_path = self.java_input.text().strip().strip('"')
            if java_path:
                java_path = validate_java(java_path)
            updated = replace(self.service.settings, client_id=client_id, memory_mb=self.memory_input.value(),
                              java_path=java_path, version_filter=source_text(self.filter_combo.currentText()))
            updated.save(self.service.root)
            if client_id != self.service.settings.client_id:
                self.service.accounts.delete()
                self.username = ""
            self.service.settings = updated
            self.client_input.setText(client_id)
            self.update_account()
            self.auth_error = ""
            self.refresh_auth_page()
            self.show_status(tr("Einstellungen gespeichert.") + (tr(" Die App-Kennung ist hinterlegt; die Minecraft-Freigabe wird erst beim echten Login geprüft.") if client_id else tr(" Die Launcher-Registrierung für Microsoft fehlt noch.")))
        except Exception as error:
            QMessageBox.warning(self, tr("Einstellungen prüfen"), human_error(error))

    def choose_java(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("Java auswählen"), "", "Java (java.exe javaw.exe)" if sys.platform == "win32" else tr("Java (java);;Alle Dateien (*)"))
        if path:
            self.java_input.setText(path)

    def open_instance(self):
        version = self.launch_version()
        service = self.active_service()
        directory = service.game_directory(version, self.service.settings.offline_name if self.service.settings.offline_mode else None) if version else service.root / "instances"
        self.open_folder(directory)

    def open_folder(self, path):
        try:
            path.mkdir(parents=True, exist_ok=True)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
                self.show_status(tr("Ordner konnte nicht geöffnet werden: ") + str(path))
        except OSError as error:
            self.show_status(human_error(error))

    def open_url(self, url):
        if not QDesktopServices.openUrl(QUrl(url)):
            self.show_status(tr("Der Standardbrowser konnte nicht geöffnet werden."))

    def open_guide(self):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
        guide = base / "EINRICHTUNG.md"
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(guide))):
            QMessageBox.information(self, tr("Microsoft-App einrichten"), tr("Die Anleitung liegt neben dem Projekt: EINRICHTUNG.md\n\nRegistriere eine Public-Client-App für persönliche Microsoft-Konten. Redirect-URI: ") + REDIRECT_URI + tr("\nBeantrage anschließend die Minecraft-API-Freigabe."))

    def closeEvent(self, event):
        if self.busy and not self.playing:
            answer = QMessageBox.question(self, tr("Vorgang läuft"), tr("Launcher schließen und den aktuellen Vorgang abbrechen? Fehlende Downloads werden beim nächsten Start repariert."))
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.cancel_event.set()
        self.closing=True
        self.update_timer.stop()
        event.accept()


def run(screenshot: str | None = None, preview_page: int = 0) -> int:
    app = QApplication.instance() or QApplication(sys.argv[:1])
    if screenshot and os.name == "nt":
        # The offscreen Qt plugin has no Windows font database. Use fonts already
        # installed on this PC for QA; do not redistribute system font files.
        fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        for filename in ("segoeui.ttf", "segoeuib.ttf", "consola.ttf", "seguisym.ttf"):
            QFontDatabase.addApplicationFont(str(fonts / filename))
    app.setApplicationName("Blockwerk")
    app.setOrganizationName("Blockwerk")
    font = "Segoe UI" if sys.platform == "win32" else "Helvetica Neue" if sys.platform == "darwin" else "DejaVu Sans"
    app.setFont(QFont(font, 10))
    app.setStyleSheet(STYLE.replace("'Segoe UI'", "'" + font + "'"))
    try:
        service = LauncherService()
        window = LauncherWindow(service, offline_preview=bool(screenshot))
    except Exception as error:
        QMessageBox.critical(None, tr("Blockwerk konnte nicht starten"), human_error(error))
        return 1
    window.show()
    if screenshot:
        window.navigate(preview_page)
        def capture():
            # Capture the actual first-run UI, without a fake account or version list.
            window.version_combo.setItemText(0, tr("Nach Online-Abruf verfügbar"))
            window.grab().save(screenshot)
            app.quit()
        QTimer.singleShot(300, capture)
    return app.exec()
