"""Custom UI widgets for the dictionary application."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..models import DictionaryEntry, Translation
from ..tts import TTSManager
from ..utils import STATUS_LABELS, LANGUAGE_NAMES


class TranslationCard(QWidget):
    """A card widget displaying a single translation."""

    speak_requested = pyqtSignal(str, str)
    copy_requested = pyqtSignal(str)

    def __init__(self, trans: Translation, target_lang: str, tts_manager: TTSManager, parent=None):
        super().__init__(parent)
        self.trans = trans
        self.target_lang = target_lang
        self.tts_manager = tts_manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(14, 12, 14, 12)

        # Top row: POS + Definition + Actions
        top = QHBoxLayout()
        top.setSpacing(10)

        pos_label = QLabel(f"[{self.trans.part_of_speech}]")
        pos_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        top.addWidget(pos_label)

        def_label = QLabel(self.trans.definition)
        def_label.setWordWrap(True)
        def_label.setStyleSheet("font-size: 15px;")
        top.addWidget(def_label, 1)

        # Speak button
        speak_btn = QPushButton("▶")
        speak_btn.setFixedSize(32, 32)
        speak_btn.setToolTip("Çeviriyi dinle")
        speak_btn.setProperty("variant", "primary")
        speak_btn.clicked.connect(
            lambda: self.speak_requested.emit(self.trans.definition, self.target_lang)
        )
        top.addWidget(speak_btn)

        # Copy button
        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(32, 32)
        copy_btn.setToolTip("Kopyala")
        copy_btn.clicked.connect(lambda: self.copy_requested.emit(self.trans.definition))
        top.addWidget(copy_btn)

        layout.addLayout(top)

        # Example sentence
        if self.trans.example:
            ex_label = QLabel(f"Örnek: {self.trans.example}")
            ex_label.setWordWrap(True)
            ex_label.setStyleSheet("font-style: italic; font-size: 14px; padding-left: 4px;")
            layout.addWidget(ex_label)


class DetailPanel(QWidget):
    """Modern detail panel for selected dictionary entry."""

    speak_requested = pyqtSignal(str, str)
    copy_requested = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    favorite_toggled = pyqtSignal(bool)
    edit_requested = pyqtSignal()
    delete_requested = pyqtSignal()

    def __init__(self, tts_manager: TTSManager, parent=None):
        super().__init__(parent)
        self.tts_manager = tts_manager
        self.current_entry = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(18, 18, 18, 18)

        # Word header
        header = QHBoxLayout()
        header.setSpacing(12)

        self.word_label = QLabel("Kelime")
        self.word_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.addWidget(self.word_label)

        self.fav_btn = QPushButton("☆")
        self.fav_btn.setFixedSize(40, 40)
        self.fav_btn.setToolTip("Favorilere ekle/çıkar")
        self.fav_btn.setStyleSheet("font-size: 22px; border: none; background: transparent;")
        self.fav_btn.clicked.connect(self._toggle_favorite)
        header.addWidget(self.fav_btn)

        self.speak_word_btn = QPushButton("▶  Dinle")
        self.speak_word_btn.setFixedSize(100, 36)
        self.speak_word_btn.setToolTip("Kelimeyi dinle")
        self.speak_word_btn.setProperty("variant", "primary")
        self.speak_word_btn.clicked.connect(self._speak_word)
        header.addWidget(self.speak_word_btn)

        self.copy_word_btn = QPushButton("📋")
        self.copy_word_btn.setFixedSize(40, 36)
        self.copy_word_btn.setToolTip("Panoya kopyala")
        self.copy_word_btn.clicked.connect(self._copy_word)
        header.addWidget(self.copy_word_btn)

        header.addStretch()
        layout.addLayout(header)

        # Language pair
        self.pair_label = QLabel("Dil Çifti")
        self.pair_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.pair_label)

        # Status
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        status_label = QLabel("Öğrenme Durumu:")
        status_label.setStyleSheet("font-size: 14px;")
        status_layout.addWidget(status_label)

        self.status_combo = QComboBox()
        self.status_combo.addItems([
            STATUS_LABELS["not_started"],
            STATUS_LABELS["learning"],
            STATUS_LABELS["learned"],
        ])
        self.status_combo.setFixedWidth(160)
        self.status_combo.currentTextChanged.connect(self._on_status_changed)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        # Translations scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        self.translations_container = QWidget()
        self.translations_layout = QVBoxLayout(self.translations_container)
        self.translations_layout.setSpacing(12)
        self.translations_layout.setContentsMargins(0, 0, 0, 0)
        self.translations_layout.addStretch()
        scroll.setWidget(self.translations_container)
        layout.addWidget(scroll)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.edit_btn = QPushButton("✏  Düzenle")
        self.edit_btn.clicked.connect(self.edit_requested.emit)
        actions.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑  Sil")
        self.delete_btn.setProperty("variant", "danger")
        self.delete_btn.clicked.connect(self.delete_requested.emit)
        actions.addWidget(self.delete_btn)

        actions.addStretch()
        layout.addLayout(actions)

    def set_entry(self, entry: DictionaryEntry):
        self.current_entry = entry
        if not entry:
            self.word_label.setText("Kelime")
            self.pair_label.setText("Dil Çifti")
            self._clear_translations()
            return

        self.word_label.setText(entry.word)
        source_lang = self.tts_manager.get_source_lang(entry.language_pair)
        target_lang = self.tts_manager.get_target_lang(entry.language_pair)
        self.pair_label.setText(
            f"{LANGUAGE_NAMES.get(source_lang, source_lang)} → "
            f"{LANGUAGE_NAMES.get(target_lang, target_lang)} ({entry.language_pair})"
        )

        self.status_combo.blockSignals(True)
        idx = list(STATUS_LABELS.values()).index(STATUS_LABELS.get(entry.status, "not_started"))
        self.status_combo.setCurrentIndex(idx)
        self.status_combo.blockSignals(False)

        self.fav_btn.setText("★" if entry.is_favorite else "☆")

        self._clear_translations()
        for trans in entry.translations:
            card = TranslationCard(trans, target_lang, self.tts_manager)
            card.speak_requested.connect(self.speak_requested.emit)
            card.copy_requested.connect(self.copy_requested.emit)
            self.translations_layout.insertWidget(self.translations_layout.count() - 1, card)

    def _clear_translations(self):
        while self.translations_layout.count() > 1:  # Keep the stretch
            item = self.translations_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _speak_word(self):
        if self.current_entry:
            lang = self.tts_manager.get_source_lang(self.current_entry.language_pair)
            self.speak_requested.emit(self.current_entry.word, lang)

    def _copy_word(self):
        if self.current_entry:
            self.copy_requested.emit(self.current_entry.word)

    def _toggle_favorite(self):
        if self.current_entry:
            new_val = not self.current_entry.is_favorite
            self.current_entry.is_favorite = new_val
            self.fav_btn.setText("★" if new_val else "☆")
            self.favorite_toggled.emit(new_val)

    def _on_status_changed(self, text):
        reverse_map = {v: k for k, v in STATUS_LABELS.items()}
        status = reverse_map.get(text, "not_started")
        self.status_changed.emit(status)