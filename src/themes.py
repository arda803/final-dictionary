from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    stylesheet: str


LIGHT_THEME = Theme(
    name="light",
    stylesheet="""
    /* ---------- Global ---------- */
    QWidget {
        background: #f4f7fb;
        color: #1f2937;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 15px;
    }
    QMainWindow::separator { background: transparent; width: 8px; height: 8px; }

    /* ---------- Menu ---------- */
    QMenuBar, QStatusBar {
        background: #eef3fb;
        border: none;
        font-size: 14px;
    }
    QMenuBar::item {
        padding: 8px 14px;
        border-radius: 6px;
    }
    QMenuBar::item:selected { background: #dbe7fb; }
    QMenu {
        background: #ffffff;
        border: 1px solid #d4deec;
        padding: 8px;
        font-size: 15px;
    }
    QMenu::item {
        padding: 10px 16px;
        border-radius: 6px;
    }
    QMenu::item:selected { background: #dbeafe; color: #0f172a; }

    /* ---------- Dialog / MessageBox / InputDialog ---------- */
    QDialog, QMessageBox, QInputDialog {
        background: #f4f7fb;
        color: #1f2937;
    }

    /* ---------- Card / GroupBox ---------- */
    QFrame#Card, QGroupBox {
        background: #ffffff;
        border: 1px solid #d8e1ee;
        border-radius: 14px;
    }
    QGroupBox {
        margin-top: 12px;
        padding-top: 14px;
        font-weight: 600;
        font-size: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 6px;
        color: #0f172a;
    }

    /* ---------- Inputs ---------- */
    QLineEdit, QTextEdit, QListWidget, QComboBox {
        background: #ffffff;
        border: 1px solid #cfd9e8;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 15px;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }
    QLineEdit:focus, QTextEdit:focus, QListWidget:focus, QComboBox:focus {
        border: 1px solid #2563eb;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 32px;
        border-left: 1px solid #cfd9e8;
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #6b7280;
        width: 0px;
        height: 0px;
    }
    QComboBox QAbstractItemView {
        background: #ffffff;
        border: 1px solid #cfd9e8;
        border-radius: 10px;
        padding: 8px;
        outline: 0px;
        font-size: 15px;
        selection-background-color: #dbeafe;
        selection-color: #1e3a8a;
    }
    QComboBox::item:selected {
        background: #dbeafe;
        color: #1e3a8a;
        border-radius: 6px;
    }

    /* ---------- List Widget ---------- */
    QListWidget::item {
        border-radius: 8px;
        padding: 9px 12px;
        margin: 3px 5px;
        font-size: 15px;
    }
    QListWidget::item:selected { background: #dbeafe; color: #1e3a8a; }
    QListWidget::item:selected:!active { background: #dbeafe; color: #1e3a8a; }
    QListWidget::item:hover { background: #eaf2ff; }

    /* ---------- Buttons ---------- */
    QPushButton {
        background: #e7eef9;
        color: #1e293b;
        border: 1px solid #d0dbed;
        border-radius: 10px;
        padding: 10px 16px;
        font-size: 15px;
        font-weight: 600;
    }
    QPushButton:hover { background: #dbe7fb; }
    QPushButton:pressed { background: #c9daf8; }

    QPushButton[variant="primary"] {
        background: #2563eb;
        color: white;
        border: 1px solid #1d4ed8;
    }
    QPushButton[variant="primary"]:hover { background: #1d4ed8; }

    QPushButton[variant="success"] {
        background: #16a34a;
        color: white;
        border: 1px solid #15803d;
    }
    QPushButton[variant="success"]:hover { background: #15803d; }

    QPushButton[variant="warning"] {
        background: #f59e0b;
        color: #1f2937;
        border: 1px solid #d97706;
    }
    QPushButton[variant="warning"]:hover { background: #d97706; color: white; }

    QPushButton[variant="danger"] {
        background: #dc2626;
        color: white;
        border: 1px solid #b91c1c;
    }
    QPushButton[variant="danger"]:hover { background: #b91c1c; }

    QPushButton[variant="theme"] {
        background: #1e293b;
        color: #fbbf24;
        border: 2px solid #334155;
        font-size: 15px;
        font-weight: 700;
        padding: 10px 18px;
    }
    QPushButton[variant="theme"]:hover { background: #334155; }

    /* ---------- Radio ---------- */
    QRadioButton {
        spacing: 10px;
        font-weight: 500;
        font-size: 15px;
    }
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 2px solid #9ca3af;
        background: #ffffff;
    }
    QRadioButton::indicator:checked {
        background: #2563eb;
        border: 2px solid #2563eb;
    }

    /* ---------- Splitter ---------- */
    QSplitter::handle { background: #d8e1ee; }
    QSplitter::handle:horizontal {
        width: 6px;
        margin: 2px 0;
        border-radius: 3px;
    }
    QSplitter::handle:vertical {
        height: 6px;
        margin: 0 2px;
        border-radius: 3px;
    }

    /* ---------- ScrollBar ---------- */
    QScrollBar:vertical {
        background: transparent;
        width: 12px;
        margin: 2px;
    }
    QScrollBar::handle:vertical {
        background: #b6c7e4;
        border-radius: 6px;
        min-height: 28px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

    QScrollBar:horizontal {
        background: transparent;
        height: 12px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal {
        background: #b6c7e4;
        border-radius: 6px;
        min-width: 28px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; height: 0; }

    /* ---------- ProgressBar ---------- */
    QProgressBar {
        border: 1px solid #d0d7de;
        border-radius: 8px;
        text-align: center;
        height: 24px;
        font-size: 13px;
        background: #e7eef9;
        color: #1f2937;
    }
    QProgressBar::chunk {
        background-color: #2563eb;
        border-radius: 8px;
    }

    /* ---------- Labels ---------- */
    QLabel { color: #1f2937; font-size: 15px; }

    /* ---------- StatusBar ---------- */
    QStatusBar::item { border: none; }
    QStatusBar { font-size: 14px; }
    """,
)


DARK_THEME = Theme(
    name="dark",
    stylesheet="""
    /* ---------- Global ---------- */
    QWidget {
        background: #121926;
        color: #e5e7eb;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 15px;
    }
    QMainWindow::separator { background: transparent; width: 8px; height: 8px; }

    /* ---------- Menu ---------- */
    QMenuBar, QStatusBar {
        background: #172133;
        border: none;
        font-size: 14px;
    }
    QMenuBar::item {
        padding: 8px 14px;
        border-radius: 6px;
    }
    QMenuBar::item:selected { background: #25324a; }
    QMenu {
        background: #1a2438;
        border: 1px solid #334155;
        padding: 8px;
        font-size: 15px;
    }
    QMenu::item {
        padding: 10px 16px;
        border-radius: 6px;
    }
    QMenu::item:selected { background: #2d3e5f; color: #f8fafc; }

    /* ---------- Dialog / MessageBox / InputDialog ---------- */
    QDialog, QMessageBox, QInputDialog {
        background: #121926;
        color: #e5e7eb;
    }

    /* ---------- Card / GroupBox ---------- */
    QFrame#Card, QGroupBox {
        background: #1a2438;
        border: 1px solid #2f3b53;
        border-radius: 14px;
    }
    QGroupBox {
        margin-top: 12px;
        padding-top: 14px;
        font-weight: 600;
        font-size: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 6px;
        color: #cbd5e1;
    }

    /* ---------- Inputs ---------- */
    QLineEdit, QTextEdit, QListWidget, QComboBox {
        background: #111a2b;
        border: 1px solid #31415f;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 15px;
        color: #f3f4f6;
        selection-background-color: #3b82f6;
        selection-color: #f8fafc;
    }
    QLineEdit:focus, QTextEdit:focus, QListWidget:focus, QComboBox:focus {
        border: 1px solid #60a5fa;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 32px;
        border-left: 1px solid #31415f;
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #94a3b8;
        width: 0px;
        height: 0px;
    }
    QComboBox QAbstractItemView {
        background: #1a2438;
        border: 1px solid #31415f;
        border-radius: 10px;
        padding: 8px;
        outline: 0px;
        font-size: 15px;
        selection-background-color: #2f4670;
        selection-color: #dbeafe;
    }
    QComboBox::item:selected {
        background: #2f4670;
        color: #dbeafe;
        border-radius: 6px;
    }

    /* ---------- List Widget ---------- */
    QListWidget::item {
        border-radius: 8px;
        padding: 9px 12px;
        margin: 3px 5px;
        font-size: 15px;
    }
    QListWidget::item:selected { background: #2f4670; color: #dbeafe; }
    QListWidget::item:selected:!active { background: #2f4670; color: #dbeafe; }
    QListWidget::item:hover { background: #24324b; }

    /* ---------- Buttons ---------- */
    QPushButton {
        background: #25324a;
        color: #e2e8f0;
        border: 1px solid #33445f;
        border-radius: 10px;
        padding: 10px 16px;
        font-size: 15px;
        font-weight: 600;
    }
    QPushButton:hover { background: #314364; }
    QPushButton:pressed { background: #1f2e47; }

    QPushButton[variant="primary"] {
        background: #3b82f6;
        color: #eff6ff;
        border: 1px solid #2563eb;
    }
    QPushButton[variant="primary"]:hover { background: #2563eb; }

    QPushButton[variant="success"] {
        background: #22c55e;
        color: #052e16;
        border: 1px solid #16a34a;
    }
    QPushButton[variant="success"]:hover { background: #16a34a; color: #ecfdf5; }

    QPushButton[variant="warning"] {
        background: #fbbf24;
        color: #422006;
        border: 1px solid #f59e0b;
    }
    QPushButton[variant="warning"]:hover { background: #f59e0b; color: #fff7ed; }

    QPushButton[variant="danger"] {
        background: #ef4444;
        color: #fef2f2;
        border: 1px solid #dc2626;
    }
    QPushButton[variant="danger"]:hover { background: #dc2626; }

    QPushButton[variant="theme"] {
        background: #fbbf24;
        color: #1f2937;
        border: 2px solid #f59e0b;
        font-size: 15px;
        font-weight: 700;
        padding: 10px 18px;
    }
    QPushButton[variant="theme"]:hover { background: #f59e0b; }

    /* ---------- Radio ---------- */
    QRadioButton {
        spacing: 10px;
        font-weight: 500;
        font-size: 15px;
    }
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 2px solid #64748b;
        background: transparent;
    }
    QRadioButton::indicator:checked {
        background: #3b82f6;
        border: 2px solid #3b82f6;
    }

    /* ---------- Splitter ---------- */
    QSplitter::handle { background: #2f3b53; }
    QSplitter::handle:horizontal {
        width: 6px;
        margin: 2px 0;
        border-radius: 3px;
    }
    QSplitter::handle:vertical {
        height: 6px;
        margin: 0 2px;
        border-radius: 3px;
    }

    /* ---------- ScrollBar ---------- */
    QScrollBar:vertical {
        background: transparent;
        width: 12px;
        margin: 2px;
    }
    QScrollBar::handle:vertical {
        background: #445676;
        border-radius: 6px;
        min-height: 28px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

    QScrollBar:horizontal {
        background: transparent;
        height: 12px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal {
        background: #445676;
        border-radius: 6px;
        min-width: 28px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; height: 0; }

    /* ---------- ProgressBar ---------- */
    QProgressBar {
        border: 1px solid #334155;
        border-radius: 8px;
        text-align: center;
        height: 24px;
        font-size: 13px;
        background: #172133;
        color: #e5e7eb;
    }
    QProgressBar::chunk {
        background-color: #3b82f6;
        border-radius: 8px;
    }

    /* ---------- Labels ---------- */
    QLabel { color: #e5e7eb; font-size: 15px; }

    /* ---------- StatusBar ---------- */
    QStatusBar::item { border: none; }
    QStatusBar { font-size: 14px; }
    """,
)


class ThemeManager:
    def __init__(self):
        self._themes = {
            "light": LIGHT_THEME,
            "dark": DARK_THEME,
        }
        self._current = "light"

    @property
    def current_theme(self) -> str:
        return self._current

    def set_theme(self, name: str):
        if name in self._themes:
            self._current = name

    def toggle_theme(self) -> str:
        self._current = "dark" if self._current == "light" else "light"
        return self._current

    def get_stylesheet(self) -> str:
        return self._themes[self._current].stylesheet

    def is_dark(self) -> bool:
        return self._current == "dark"