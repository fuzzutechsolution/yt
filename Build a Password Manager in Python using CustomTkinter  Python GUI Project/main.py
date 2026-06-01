import sys
import json
import os
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, QRect
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QLinearGradient,
    QBrush, QPen, QCursor, QPalette, QRadialGradient
)

# ──────────────────────────────────────────────
#  FILE
# ──────────────────────────────────────────────
FILE_NAME = "passwords.json"


# ══════════════════════════════════════════════
#  GLOBAL STYLESHEET
# ══════════════════════════════════════════════
GLOBAL_QSS = """
* {
    font-family: "Segoe UI", "Arial", sans-serif;
}

QMainWindow {
    background: #0B0F1E;
}

/* ── Scroll Area ── */
QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 4px 2px;
}
QScrollBar::handle:vertical {
    background: rgba(100, 120, 255, 0.4);
    min-height: 30px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(100, 120, 255, 0.7);
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0px;
}

/* ── Input Fields ── */
QLineEdit {
    background: rgba(18, 22, 42, 0.95);
    border: 1px solid rgba(100, 120, 255, 0.2);
    border-radius: 10px;
    padding: 12px 16px;
    color: #E2E8F0;
    font-size: 13px;
    selection-background-color: rgba(100, 120, 255, 0.4);
}
QLineEdit:focus {
    border: 1px solid rgba(100, 120, 255, 0.6);
    background: rgba(20, 25, 48, 0.98);
}
QLineEdit:hover {
    border: 1px solid rgba(100, 120, 255, 0.35);
}

/* ── Primary Button ── */
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:1 #8B5CF6);
    border: none;
    border-radius: 12px;
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 14px 20px;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7C7FF7, stop:1 #A78BFA);
}
QPushButton#primaryBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5558E8, stop:1 #7C3AED);
}

/* ── Small Action Buttons (on cards) ── */
QPushButton#actionBtn {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #8892A4;
    font-size: 13px;
    padding: 4px;
}
QPushButton#actionBtn:hover {
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.4);
    color: #A5B4FC;
}

/* ── Delete Button ── */
QPushButton#deleteBtn {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #8892A4;
    font-size: 13px;
    padding: 4px;
}
QPushButton#deleteBtn:hover {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #FCA5A5;
}

/* ── Badge ── */
QLabel#badge {
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 8px;
    color: #A5B4FC;
    font-size: 11px;
    font-weight: bold;
    padding: 4px 12px;
}
"""


# ══════════════════════════════════════════════
#  Glass Card — base for frosted card panels
# ══════════════════════════════════════════════
class GlassCard(QFrame):
    """A card with rounded corners, subtle gradient bg, and a faint border."""

    def __init__(self, radius=16, parent=None):
        super().__init__(parent)
        self._radius = radius
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)

        # Card fill — dark glass
        grad = QLinearGradient(0, 0, 0, rect.height())
        grad.setColorAt(0.0, QColor(20, 24, 50, 210))
        grad.setColorAt(1.0, QColor(14, 18, 38, 230))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        p.drawRoundedRect(rect, self._radius, self._radius)

        p.end()


# ══════════════════════════════════════════════
#  Password Card — one per saved entry
# ══════════════════════════════════════════════
class PasswordCard(GlassCard):
    """Displays one saved password with view/copy/delete actions."""

    def __init__(self, index, website, username, password, on_delete, on_copy, parent=None):
        super().__init__(radius=14, parent=parent)
        self.index = index
        self._password = password
        self._visible = False
        self.setFixedHeight(100)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 14, 12)
        layout.setSpacing(12)

        # ── Left: Info ──
        info = QVBoxLayout()
        info.setSpacing(3)

        lbl_web = QLabel(website)
        lbl_web.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_web.setStyleSheet("color: #C4B5FD;")  # soft purple

        lbl_user = QLabel(f"  {username}")
        lbl_user.setFont(QFont("Segoe UI", 10))
        lbl_user.setStyleSheet("color: #64748B;")

        self.lbl_pass = QLabel(f"  {'●' * min(len(password), 12)}")
        self.lbl_pass.setFont(QFont("Segoe UI", 10))
        self.lbl_pass.setStyleSheet("color: #64748B;")

        info.addWidget(lbl_web)
        info.addWidget(lbl_user)
        info.addWidget(self.lbl_pass)

        layout.addLayout(info, stretch=1)

        # ── Right: Action buttons ──
        btns = QVBoxLayout()
        btns.setSpacing(4)
        btns.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.eye_btn = self._make_btn("👁", "actionBtn")
        self.eye_btn.clicked.connect(self._toggle_pass)
        btns.addWidget(self.eye_btn)

        copy_btn = self._make_btn("📋", "actionBtn")
        copy_btn.setToolTip("Copy password")
        copy_btn.clicked.connect(lambda: on_copy(password))
        btns.addWidget(copy_btn)

        del_btn = self._make_btn("✕", "deleteBtn")
        del_btn.setToolTip("Delete")
        del_btn.clicked.connect(lambda: on_delete(index))
        btns.addWidget(del_btn)

        layout.addLayout(btns)

    @staticmethod
    def _make_btn(text, obj_name):
        b = QPushButton(text)
        b.setObjectName(obj_name)
        b.setFixedSize(32, 32)
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return b

    def _toggle_pass(self):
        self._visible = not self._visible
        if self._visible:
            self.lbl_pass.setText(f"  {self._password}")
            self.eye_btn.setText("🔒")
        else:
            self.lbl_pass.setText(f"  {'●' * min(len(self._password), 12)}")
            self.eye_btn.setText("👁")


# ══════════════════════════════════════════════
#  Main Window
# ══════════════════════════════════════════════
class PasswordManager(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fuzzu Password Manager")
        self.setMinimumSize(560, 680)
        self.resize(600, 780)
        self._bg_phase = 0.0

        # Background animation timer
        self._bg_timer = QTimer(self)
        self._bg_timer.timeout.connect(self._tick_bg)
        self._bg_timer.start(40)

        # ── Central widget ──
        central = QWidget()
        self.setCentralWidget(central)

        # Full-window scroll
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root_layout.addWidget(scroll)

        container = QWidget()
        container.setObjectName("container")
        scroll.setWidget(container)

        main = QVBoxLayout(container)
        main.setContentsMargins(36, 28, 36, 20)
        main.setSpacing(20)

        # ═══ Header ═══
        hdr = QVBoxLayout()
        hdr.setSpacing(2)

        title = QLabel("🔐  Password Manager")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #E2E8F0;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        subtitle = QLabel("Securely store & manage your credentials")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #64748B;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)

        hdr.addWidget(title)
        hdr.addWidget(subtitle)
        main.addLayout(hdr)

        # ═══ Add Password Card ═══
        add_card = GlassCard(radius=18)
        card_lay = QVBoxLayout(add_card)
        card_lay.setContentsMargins(24, 20, 24, 20)
        card_lay.setSpacing(12)

        card_title = QLabel("✦  Add New Password")
        card_title.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        card_title.setStyleSheet("color: #CBD5E1;")
        card_lay.addWidget(card_title)

        # Website
        self.inp_web = QLineEdit()
        self.inp_web.setPlaceholderText("🌐  Website name")
        self.inp_web.setFixedHeight(46)
        card_lay.addWidget(self.inp_web)

        # Username
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("👤  Username or email")
        self.inp_user.setFixedHeight(46)
        card_lay.addWidget(self.inp_user)

        # Password row (input + toggle)
        pass_row = QHBoxLayout()
        pass_row.setSpacing(8)

        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("🔑  Password")
        self.inp_pass.setFixedHeight(46)
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        pass_row.addWidget(self.inp_pass, stretch=1)

        self.eye_btn = QPushButton("👁")
        self.eye_btn.setObjectName("actionBtn")
        self.eye_btn.setFixedSize(46, 46)
        self.eye_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.eye_btn.setStyleSheet("""
            QPushButton {
                background: rgba(18, 22, 42, 0.95);
                border: 1px solid rgba(100, 120, 255, 0.2);
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                border: 1px solid rgba(100, 120, 255, 0.5);
                background: rgba(25, 30, 55, 1);
            }
        """)
        self.eye_btn.clicked.connect(self._toggle_input_pass)
        pass_row.addWidget(self.eye_btn)

        card_lay.addLayout(pass_row)

        # Save button
        self.save_btn = QPushButton("💾   Save Password")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.setFixedHeight(50)
        self.save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_btn.clicked.connect(self._save_password)
        card_lay.addWidget(self.save_btn)

        # Status message
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: transparent;")
        self.status_label.setFixedHeight(20)
        card_lay.addWidget(self.status_label)

        main.addWidget(add_card)

        # ═══ Search Row ═══
        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("🔍  Search passwords...")
        self.inp_search.setFixedHeight(42)
        self.inp_search.textChanged.connect(self._filter)
        search_row.addWidget(self.inp_search, stretch=1)

        self.badge = QLabel("0 saved")
        self.badge.setObjectName("badge")
        self.badge.setFixedHeight(34)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_row.addWidget(self.badge)

        main.addLayout(search_row)

        # ═══ Password List ═══
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(8)
        main.addLayout(self.list_layout)

        # Empty state
        self.empty_label = QLabel("🔒  No passwords saved yet\nAdd your first password above!")
        self.empty_label.setFont(QFont("Segoe UI", 11))
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #475569;
            background: rgba(15, 19, 35, 0.6);
            border: 1px dashed rgba(100, 120, 255, 0.15);
            border-radius: 14px;
            padding: 36px;
        """)
        main.addWidget(self.empty_label)

        # Stretch
        main.addStretch()

        # Footer
        footer = QLabel("✦ Developed by FuzzuTech")
        footer.setFont(QFont("Segoe UI", 9))
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #334155; padding: 12px 0;")
        main.addWidget(footer)

        # ── Load data ──
        self._pass_visible = False
        self._refresh()

    # ── Background painting ──

    def _tick_bg(self):
        self._bg_phase += 0.012
        if self._bg_phase > 6.283:
            self._bg_phase -= 6.283
        self.centralWidget().update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Base dark gradient
        base = QLinearGradient(0, 0, w * 0.3, h)
        base.setColorAt(0.0, QColor(11, 15, 30))
        base.setColorAt(0.5, QColor(13, 17, 35))
        base.setColorAt(1.0, QColor(9, 12, 26))
        p.fillRect(self.rect(), QBrush(base))

        # Orb 1 — indigo (top right)
        ox1 = w * 0.75 + 40 * math.sin(self._bg_phase * 0.7)
        oy1 = h * 0.18 + 25 * math.cos(self._bg_phase * 0.9)
        r1 = QRadialGradient(ox1, oy1, 260)
        r1.setColorAt(0.0, QColor(99, 102, 241, 22))
        r1.setColorAt(0.6, QColor(99, 102, 241, 6))
        r1.setColorAt(1.0, QColor(99, 102, 241, 0))
        p.setBrush(QBrush(r1))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(ox1) - 260, int(oy1) - 260, 520, 520)

        # Orb 2 — purple (bottom left)
        ox2 = w * 0.2 + 35 * math.cos(self._bg_phase * 0.5)
        oy2 = h * 0.72 + 30 * math.sin(self._bg_phase * 0.8)
        r2 = QRadialGradient(ox2, oy2, 220)
        r2.setColorAt(0.0, QColor(139, 92, 246, 18))
        r2.setColorAt(0.6, QColor(139, 92, 246, 5))
        r2.setColorAt(1.0, QColor(139, 92, 246, 0))
        p.setBrush(QBrush(r2))
        p.drawEllipse(int(ox2) - 220, int(oy2) - 220, 440, 440)

        # Orb 3 — blue-cyan (center)
        ox3 = w * 0.5 + 50 * math.sin(self._bg_phase * 0.6)
        oy3 = h * 0.45 + 35 * math.cos(self._bg_phase * 1.1)
        r3 = QRadialGradient(ox3, oy3, 200)
        r3.setColorAt(0.0, QColor(56, 189, 248, 10))
        r3.setColorAt(0.6, QColor(56, 189, 248, 3))
        r3.setColorAt(1.0, QColor(56, 189, 248, 0))
        p.setBrush(QBrush(r3))
        p.drawEllipse(int(ox3) - 200, int(oy3) - 200, 400, 400)

        p.end()

    # ── Password visibility toggle (input) ──

    def _toggle_input_pass(self):
        self._pass_visible = not self._pass_visible
        if self._pass_visible:
            self.inp_pass.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_btn.setText("🔒")
        else:
            self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_btn.setText("👁")

    # ── Data helpers ──

    def _load(self):
        if not os.path.exists(FILE_NAME):
            return []
        try:
            with open(FILE_NAME, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_all(self, data):
        with open(FILE_NAME, "w") as f:
            json.dump(data, f, indent=4)

    # ── Save new password ──

    def _save_password(self):
        web = self.inp_web.text().strip()
        usr = self.inp_user.text().strip()
        pwd = self.inp_pass.text().strip()

        if not web or not usr or not pwd:
            self._show_status("⚠  Please fill in all fields", "#F59E0B")
            # Highlight empty fields
            for inp, val in [(self.inp_web, web), (self.inp_user, usr), (self.inp_pass, pwd)]:
                if not val:
                    inp.setStyleSheet("""
                        QLineEdit {
                            background: rgba(18, 22, 42, 0.95);
                            border: 1px solid rgba(239, 68, 68, 0.6);
                            border-radius: 10px; padding: 12px 16px;
                            color: #E2E8F0; font-size: 13px;
                        }
                    """)
                    QTimer.singleShot(1500, lambda i=inp: i.setStyleSheet(""))
            return

        data = self._load()
        data.append({"website": web, "username": usr, "password": pwd})
        self._save_all(data)

        self.inp_web.clear()
        self.inp_user.clear()
        self.inp_pass.clear()

        self._show_status("✓  Password saved successfully!", "#22C55E")
        self._refresh()

    def _show_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        QTimer.singleShot(2500, lambda: self.status_label.setStyleSheet("color: transparent;"))

    # ── Delete ──

    def _delete(self, index):
        data = self._load()
        if 0 <= index < len(data):
            data.pop(index)
            self._save_all(data)
            self._refresh()

    # ── Copy ──

    def _copy(self, text):
        QApplication.clipboard().setText(text)
        self._show_status("✓  Password copied to clipboard!", "#6366F1")

    # ── Refresh list ──

    def _refresh(self, filter_text=""):
        # Clear list
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        data = self._load()

        if filter_text:
            filtered = [
                (i, d) for i, d in enumerate(data)
                if filter_text.lower() in d["website"].lower()
                or filter_text.lower() in d["username"].lower()
            ]
        else:
            filtered = list(enumerate(data))

        self.badge.setText(f"{len(data)} saved")
        self.empty_label.setVisible(len(filtered) == 0)

        for idx, entry in filtered:
            card = PasswordCard(
                index=idx,
                website=entry["website"],
                username=entry["username"],
                password=entry["password"],
                on_delete=self._delete,
                on_copy=self._copy
            )
            self.list_layout.addWidget(card)

    def _filter(self, text):
        self._refresh(filter_text=text)


# ══════════════════════════════════════════════
#  Entry Point
# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(11, 15, 30))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(226, 232, 240))
    pal.setColor(QPalette.ColorRole.Base, QColor(14, 18, 38))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(18, 22, 42))
    pal.setColor(QPalette.ColorRole.Text, QColor(226, 232, 240))
    pal.setColor(QPalette.ColorRole.Button, QColor(20, 25, 48))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(226, 232, 240))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(99, 102, 241))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(71, 85, 105))
    app.setPalette(pal)

    app.setStyleSheet(GLOBAL_QSS)

    window = PasswordManager()
    window.show()
    sys.exit(app.exec())