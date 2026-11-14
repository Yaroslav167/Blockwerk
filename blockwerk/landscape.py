"""Animated, original voxel artwork, rendered locally with Qt."""
from __future__ import annotations
from .i18n import tr

import math
import random

from PySide6.QtCore import QElapsedTimer, QEvent, QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPixmap, QPolygonF
from PySide6.QtWidgets import QFrame, QToolButton


class Landscape(QFrame):
    """Cached block island, drifting clouds and fireflies at about 30 FPS."""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(220)
        self.setObjectName("hero")
        self.setAccessibleName(tr("Animierte Blocklandschaft"))
        self.phase = 0.0
        self._terrain = None
        self._terrain_key = None
        self._observed_window = None
        self._clock = QElapsedTimer()
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(33)
        self.animation_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.animation_timer.timeout.connect(self._advance)
        self.pause_button = QToolButton(self)
        self.pause_button.setCheckable(True)
        self.pause_button.setText(tr("Animation pausieren"))
        self.pause_button.setAccessibleName(tr("Animation pausieren"))
        self.pause_button.setToolTip(tr("Bewegung auf der Startseite anhalten oder fortsetzen"))
        self.pause_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pause_button.setStyleSheet("""
            QToolButton { background: #1c3024; color: #d8e9c6;
                border: 1px solid #58714a; border-radius: 5px;
                font-size: 11px; padding: 5px 9px; }
            QToolButton:hover, QToolButton:focus { background: #344e30;
                border-color: #b8e285; }
        """)
        self.pause_button.toggled.connect(self._pause_changed)

    def _pause_changed(self, paused):
        text = tr("Animation fortsetzen") if paused else tr("Animation pausieren")
        self.pause_button.setText(text)
        self.pause_button.setAccessibleName(text)
        self._position_control()
        self._sync_timer()

    def _position_control(self):
        self.pause_button.adjustSize()
        self.pause_button.move(max(8, self.width() - self.pause_button.width() - 14),
                               max(8, self.height() - self.pause_button.height() - 12))
        self.pause_button.raise_()

    def _sync_timer(self):
        animate = self.isVisible() and not self.window().isMinimized() and not self.pause_button.isChecked()
        if animate and not self.animation_timer.isActive():
            self._clock.start()
            self.animation_timer.start()
        elif not animate:
            self.animation_timer.stop()

    def _advance(self):
        if not self.isVisible() or self.window().isMinimized():
            self._sync_timer()
            return
        self.phase += min(self._clock.restart() / 1000.0, 0.15)
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        window = self.window()
        if window is not self._observed_window:
            if self._observed_window is not None:
                self._observed_window.removeEventFilter(self)
            self._observed_window = window
            window.installEventFilter(self)
        self._position_control()
        self._sync_timer()

    def hideEvent(self, event):
        self.animation_timer.stop()
        super().hideEvent(event)

    def eventFilter(self, watched, event):
        if watched is self._observed_window and event.type() in (
                QEvent.Type.WindowStateChange, QEvent.Type.Show, QEvent.Type.Hide):
            self._sync_timer()
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_control()

    @staticmethod
    def _polygon(painter, points, color):
        painter.setBrush(QColor(color))
        painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))

    def _cube(self, painter, px, py, size, depth, top, left, right):
        self._polygon(painter, [(px, py), (px + size, py + size * .48),
                               (px, py + size * .96), (px - size, py + size * .48)], top)
        self._polygon(painter, [(px - size, py + size * .48), (px, py + size * .96),
                               (px, py + size * .96 + depth), (px - size, py + size * .48 + depth)], left)
        self._polygon(painter, [(px, py + size * .96), (px + size, py + size * .48),
                               (px + size, py + size * .48 + depth), (px, py + size * .96 + depth)], right)

    def _cached_terrain(self):
        w, h, ratio = self.width(), self.height(), self.devicePixelRatioF()
        key = (w, h, ratio)
        if self._terrain_key == key:
            return self._terrain
        # Only resize/DPI changes redraw the detailed terrain; animation reuses it.
        image = QPixmap(max(1, round(w * ratio)), max(1, round(h * ratio)))
        image.setDevicePixelRatio(ratio)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        rng = random.Random(18)
        size, ox, oy = 28, w - 210, h - 131
        for diagonal in range(-4, 11):
            for x in range(-2, 7):
                y = diagonal - x
                if -2 <= y <= 5:
                    elevation = 9 + max(0, 3 - abs(x + 1)) * 9 + rng.choice([0, 0, 9])
                    water = x > 3 and y > 0
                    px = ox + (x - y) * size
                    py = oy + (x + y) * size * .48 - (3 if water else elevation)
                    self._cube(painter, px, py, size, 33 + elevation * .27,
                               rng.choice(["#759d51", "#84aa5b", "#91b963"]) if not water else "#648e80",
                               "#56633d" if not water else "#3a685e", "#3d5232" if not water else "#32594f")
        for tx, ty in [(w - 270, h - 140), (w - 116, h - 112), (w - 344, h - 86)]:
            painter.setBrush(QColor("#5e5940"))
            painter.drawRect(tx - 6, ty, 12, 55)
            painter.setBrush(QColor("#385e32"))
            painter.drawRect(tx - 29, ty - 31, 58, 44)
            painter.setBrush(QColor("#4e793d"))
            painter.drawRect(tx - 20, ty - 49, 46, 34)
            painter.setBrush(QColor("#699347"))
            painter.drawRect(tx - 20, ty - 49, 46, 9)
        painter.end()
        self._terrain_key, self._terrain = key, image
        return image

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        w, h, t = self.width(), self.height(), self.phase
        shape = QPainterPath()
        shape.addRoundedRect(0, 0, w, h, 14, 14)
        painter.setClipPath(shape)
        sky = QLinearGradient(0, 0, 0, h)
        sky.setColorAt(0, QColor("#203b35"))
        sky.setColorAt(1, QColor("#354d32"))
        painter.fillRect(self.rect(), sky)
        # Square sun and voxel clouds drift independently of the islands.
        painter.setBrush(QColor("#d4e89d"))
        painter.drawRect(w - 107, 26 + round(2 * math.sin(t * .22)), 34, 34)
        span = max(1, w * .6)
        for start, y, speed, opacity in ((80, 28, 8, 55), (300, 62, 12, 75), (470, 15, 6, 35)):
            cx = round(w * .43 + ((start + t * speed) % span) - 60)
            painter.setBrush(QColor(211, 230, 195, opacity))
            painter.drawRect(cx, y + 10, 92, 13)
            painter.drawRect(cx + 18, y, 34, 12)
            painter.drawRect(cx + 53, y + 4, 23, 10)
        # Small floating grass blocks make the slow vertical movement visible.
        for x, y, offset in ((w - 365, 37, 0), (w - 63, 100, 2.5)):
            self._cube(painter, x, y + math.sin(t * .85 + offset) * 6,
                       17, 19, "#a4cc73", "#6d7549", "#485d37")
        painter.drawPixmap(QPointF(0, math.sin(t * .7) * 4), self._cached_terrain())
        # Reproducible fireflies: no random allocation or external assets per frame.
        for i in range(20):
            x = w * .56 + ((i * 59) % max(1, int(w * .42))) + math.sin(t * .6 + i) * 9
            y = h - ((i * 43 + t * (6 + i % 4)) % max(1, h - 14))
            glow = int(45 + 100 * (.5 + .5 * math.sin(t * 1.6 + i * 2)))
            painter.setBrush(QColor(210, 241, 145, glow))
            painter.drawRect(round(x), round(y), 3 if i % 3 else 4, 3 if i % 3 else 4)
        # Preserve a calm, high-contrast surface underneath the live heading.
        fade = QLinearGradient(0, 0, w * .76, 0)
        fade.setColorAt(0, QColor("#243d2b"))
        fade.setColorAt(.60, QColor("#243d2b"))
        fade.setColorAt(1, QColor(36, 61, 43, 0))
        painter.fillRect(self.rect(), fade)
        painter.end()
