import sys, time
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QTabWidget, QTabBar, QGridLayout
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QFont, QIntValidator

THEMES = {
    "Catppuccin Mocha": """
        QWidget { background:#1e1e2e; color:#cdd6f4; }
        QTabBar::tab { background:#313244; }
        QTabBar::tab:selected { background:#89b4fa; color:#1e1e2e; }
        QPushButton, QLineEdit { background:#313244; }
    """,
    "Catppuccin Latte": """
        QWidget { background:#eff1f5; color:#4c4f69; }
        QTabBar::tab { background:#ccd0da; }
        QTabBar::tab:selected { background:#7287fd; color:white; }
        QPushButton, QLineEdit { background:#ccd0da; }
    """,
    "Dracula": """
        QWidget { background:#282a36; color:#f8f8f2; }
        QTabBar::tab { background:#44475a; }
        QTabBar::tab:selected { background:#bd93f9; color:black; }
        QPushButton, QLineEdit { background:#44475a; }
    """,
    "Nord": """
        QWidget { background:#2e3440; color:#eceff4; }
        QTabBar::tab { background:#3b4252; }
        QTabBar::tab:selected { background:#88c0d0; color:black; }
        QPushButton, QLineEdit { background:#3b4252; }
    """,
    "Gruvbox Dark": """
        QWidget { background:#282828; color:#ebdbb2; }
        QTabBar::tab { background:#3c3836; }
        QTabBar::tab:selected { background:#fabd2f; color:black; }
        QPushButton, QLineEdit { background:#3c3836; }
    """,
    "Solarized Dark": """
        QWidget { background:#002b36; color:#eee8d5; }
        QTabBar::tab { background:#073642; }
        QTabBar::tab:selected { background:#268bd2; color:black; }
        QPushButton, QLineEdit { background:#073642; }
    """,
    "Midnight": """
        QWidget { background:#0d1117; color:#c9d1d9; }
        QTabBar::tab { background:#161b22; }
        QTabBar::tab:selected { background:#58a6ff; color:black; }
        QPushButton, QLineEdit { background:#161b22; }
    """,
    "Tokyo Night": """
        QWidget { background:#1a1b26; color:#c0caf5; }
        QTabBar::tab { background:#24283b; }
        QTabBar::tab:selected { background:#7aa2f7; color:black; }
        QPushButton, QLineEdit { background:#24283b; }
    """,
    "Rose Pine": """
        QWidget { background:#191724; color:#e0def4; }
        QTabBar::tab { background:#26233a; }
        QTabBar::tab:selected { background:#eb6f92; color:black; }
        QPushButton, QLineEdit { background:#26233a; }
    """,
    "One Dark": """
        QWidget { background:#282c34; color:#abb2bf; }
        QTabBar::tab { background:#353b45; }
        QTabBar::tab:selected { background:#61afef; color:black; }
        QPushButton, QLineEdit { background:#353b45; }
    """,
    "Cyber Neon": """
        QWidget { background:#0f0f17; color:#e6e6ff; }
        QTabBar::tab { background:#1b1b2b; }
        QTabBar::tab:selected { background:#ff4fd8; color:black; }
        QPushButton, QLineEdit { background:#1b1b2b; }
    """,
}

BASE_STYLE = """
QTabWidget::pane { border:none; }
QTabBar { qproperty-expanding:false; }
QTabBar::tab { padding:6px 18px; margin:6px; border-radius:8px; font-size:11pt; }
QPushButton { padding:6px 14px; border-radius:6px; font-size:10pt; }
QLineEdit { padding:6px; border-radius:6px; text-align:center; font-size:12pt; }
"""

class CenteredTabBar(QTabBar):
    def tabSizeHint(self, index):
        s = super().tabSizeHint(index)
        s.setWidth(s.width() + 10)
        return s

class TimeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClockPy")
        self.setFixedSize(520, 480)
        self.settings = QSettings("ClockApp", "Preferences")
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        bar_wrap = QWidget()
        bar = QHBoxLayout(bar_wrap)
        bar.addStretch()
        self.tabs = QTabWidget()
        self.tabs.setTabBar(CenteredTabBar())
        self.tabs.setDocumentMode(True)
        self.tabs.setUsesScrollButtons(False)
        bar.addWidget(self.tabs)
        bar.addStretch()
        root.addWidget(bar_wrap)
        self.init_clock()
        self.init_stopwatch()
        self.init_timer()
        self.init_themes()
        self.apply_saved_theme()

    def extract_color(self, css, key):
        for line in css.splitlines():
            if key in line and "#" in line:
                return "#" + line.split("#")[1][:6]
        return "#444444"

    def init_clock(self):
        tab = QWidget()
        l = QVBoxLayout(tab)
        l.addStretch()
        self.clock = QLabel()
        self.clock.setFont(QFont("Consolas", 34))
        self.clock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.clock)
        l.addStretch()
        t = QTimer(self)
        t.timeout.connect(lambda: self.clock.setText(datetime.now().strftime("%H:%M:%S")))
        t.start(1000)
        self.tabs.addTab(tab, "Clock")

    def init_stopwatch(self):
        tab = QWidget()
        l = QVBoxLayout(tab)
        l.addStretch()
        self.sw = QLabel("00:00:00.000")
        self.sw.setFont(QFont("Consolas", 26))
        self.sw.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.sw)
        r = QHBoxLayout()
        r.addStretch()
        for t, f in [("Start", self.sw_start), ("Stop", self.sw_stop), ("Reset", self.sw_reset)]:
            r.addWidget(QPushButton(t, clicked=f))
        r.addStretch()
        l.addLayout(r)
        l.addStretch()
        self.swt = QTimer(self)
        self.swt.timeout.connect(self.sw_update)
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.tabs.addTab(tab, "Stopwatch")

    def sw_start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.swt.start(10)

    def sw_stop(self):
        if self.running:
            self.running = False
            self.elapsed += time.time() - self.start_time
            self.swt.stop()

    def sw_reset(self):
        self.swt.stop()
        self.running = False
        self.elapsed = 0
        self.sw.setText("00:00:00.000")

    def sw_update(self):
        e = time.time() - self.start_time + self.elapsed
        self.sw.setText(f"{int(e//3600):02}:{int(e//60)%60:02}:{int(e)%60:02}.{int((e%1)*1000):03}")

    def init_timer(self):
        tab = QWidget()
        l = QVBoxLayout(tab)
        l.addStretch()
        self.tl = QLabel("00:00:00.000")
        self.tl.setFont(QFont("Consolas", 32))
        self.tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.tl)
        labels = QHBoxLayout()
        labels.addStretch()
        for t in ["Hours", "Minutes", "Seconds", "MS"]:
            lb = QLabel(t)
            lb.setFixedWidth(90)
            lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            labels.addWidget(lb)
        labels.addStretch()
        l.addLayout(labels)
        inputs = QHBoxLayout()
        inputs.addStretch()
        self.boxes = []
        for _ in range(4):
            b = QLineEdit("0")
            b.setValidator(QIntValidator(0, 999))
            b.setFixedWidth(90)
            self.boxes.append(b)
            inputs.addWidget(b)
        inputs.addStretch()
        l.addLayout(inputs)
        r = QHBoxLayout()
        r.addStretch()
        for t, f in [("Start", self.t_start), ("Stop", self.t_stop), ("Reset", self.t_reset)]:
            r.addWidget(QPushButton(t, clicked=f))
        r.addStretch()
        l.addLayout(r)
        l.addStretch()
        self.tt = QTimer(self)
        self.tt.timeout.connect(self.t_update)
        self.remaining = 0
        self.tabs.addTab(tab, "Timer")

    def t_start(self):
        h, m, s, ms = [int(b.text() or 0) for b in self.boxes]
        self.remaining = h*3600000 + m*60000 + s*1000 + ms
        if self.remaining > 0:
            self.tt.start(10)

    def t_stop(self):
        self.tt.stop()

    def t_reset(self):
        self.tt.stop()
        self.tl.setText("00:00:00.000")

    def t_update(self):
        self.remaining -= 10
        if self.remaining <= 0:
            self.tt.stop()
            QApplication.beep()
            self.tl.setText("00:00:00.000")
            return
        self.tl.setText(f"{self.remaining//3600000:02}:{self.remaining//60000%60:02}:{self.remaining//1000%60:02}.{self.remaining%1000:03}")

    def init_themes(self):
        tab = QWidget()
        v = QVBoxLayout(tab)
        v.addStretch()
        grid_wrap = QHBoxLayout()
        grid_wrap.addStretch()
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        cols = 6
        for i, (name, css) in enumerate(THEMES.items()):
            bg = self.extract_color(css, "QWidget")
            accent = self.extract_color(css, "QTabBar::tab:selected")
            btn = QPushButton()
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{bg};
                    border-radius:6px;
                    border:3px solid {accent};
                }}
                QPushButton:hover {{ border:2px solid white; }}
            """)
            btn.clicked.connect(lambda _, c=css, n=name: self.apply_theme(c, n))
            grid.addWidget(btn, i // cols, i % cols)
        grid_wrap.addLayout(grid)
        grid_wrap.addStretch()
        v.addLayout(grid_wrap)
        v.addStretch()
        self.tabs.addTab(tab, "Themes")

    def apply_theme(self, css, name):
        QApplication.instance().setStyleSheet(BASE_STYLE + css)
        self.settings.setValue("theme", name)

    def apply_saved_theme(self):
        name = self.settings.value("theme", "Catppuccin Mocha")
        self.apply_theme(THEMES.get(name, THEMES["Catppuccin Mocha"]), name)

app = QApplication(sys.argv)
w = TimeApp()
w.show()
sys.exit(app.exec())
