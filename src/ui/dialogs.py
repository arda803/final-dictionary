"""Dialog windows for the dictionary application."""
import random
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QDialogButtonBox, QGroupBox, QSpinBox,
    QCheckBox, QMessageBox, QWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ..models import DictionaryEntry, Translation
from ..database import DictionaryDB
from ..tts import TTSCache
from ..utils import AutoTagger, SettingsManager, STATUS_LABELS


class SettingsDialog(QDialog):
    def __init__(self, settings: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Ayarlar")
        self.setModal(True)
        self.setMinimumWidth(500)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        # TTS Group
        tts_group = QGroupBox("🔊  Seslendirme Ayarları")
        tts_layout = QFormLayout(tts_group)
        tts_layout.setSpacing(12)

        self.tts_enabled_check = QCheckBox("Seslendirmeyi etkinleştir")
        self.tts_enabled_check.setChecked(self.settings.get("tts_enabled", True))
        tts_layout.addRow(self.tts_enabled_check)

        self.auto_tts_check = QCheckBox("Kelime seçildiğinde otomatik seslendir")
        self.auto_tts_check.setChecked(self.settings.get("auto_tts", False))
        tts_layout.addRow(self.auto_tts_check)

        self.tts_rate_spin = QSpinBox()
        self.tts_rate_spin.setRange(-50, 50)
        self.tts_rate_spin.setValue(self.settings.get("tts_rate", 0))
        self.tts_rate_spin.setSuffix("%")
        tts_layout.addRow("Ses hızı:", self.tts_rate_spin)

        self.cache_label = QLabel()
        self._update_cache_label()
        tts_layout.addRow(self.cache_label)

        clear_cache_btn = QPushButton("🗑  Önbelleği Temizle")
        clear_cache_btn.clicked.connect(self.clear_cache)
        tts_layout.addRow(clear_cache_btn)

        layout.addWidget(tts_group)

        # Theme Group
        theme_group = QGroupBox("🎨  Tema Ayarları")
        theme_layout = QFormLayout(theme_group)
        theme_layout.setSpacing(12)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Açık", "Koyu"])
        current_theme = self.settings.get("theme", "light")
        self.theme_combo.setCurrentIndex(0 if current_theme == "light" else 1)
        theme_layout.addRow("Tema:", self.theme_combo)

        layout.addWidget(theme_group)
        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _update_cache_label(self):
        cache = TTSCache()
        cache_size = cache.get_cache_size()
        cache_mb = cache_size / (1024 * 1024)
        self.cache_label.setText(f"Önbellek boyutu: {cache_mb:.2f} MB")

    def clear_cache(self):
        cache = TTSCache()
        cache.clear_cache()
        self._update_cache_label()
        QMessageBox.information(self, "Tamamlandı", "Ses önbelleği temizlendi.")

    def save_settings(self):
        self.settings.set("tts_enabled", self.tts_enabled_check.isChecked())
        self.settings.set("auto_tts", self.auto_tts_check.isChecked())
        self.settings.set("tts_rate", self.tts_rate_spin.value())
        theme = "light" if self.theme_combo.currentIndex() == 0 else "dark"
        self.settings.set("theme", theme)
        self.accept()


class QuizDialog(QDialog):
    def __init__(self, db: DictionaryDB, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("🎯  Kelime Quiz")
        self.setModal(True)
        self.setMinimumWidth(580)
        self.setMinimumHeight(450)

        self.entries = [e for e in db.get_all_entries() if e.translations]
        random.shuffle(self.entries)
        self.current_index = 0
        self.score = 0
        self.total = min(10, len(self.entries))
        self._answered = False

        if self.total == 0:
            QMessageBox.warning(self, "Uyarı", "Quiz için yeterli kelime yok.")
            self.reject()
            return

        self._setup_ui()
        self._show_question()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(28, 28, 28, 28)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Question
        self.question_label = QLabel()
        self.question_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.question_label)

        # Hint
        self.hint_label = QLabel()
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.hint_label)

        # Answer input
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Çeviriyi yazın ve Enter'a basın...")
        self.answer_input.returnPressed.connect(self.check_answer)
        layout.addWidget(self.answer_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.check_btn = QPushButton("✓  Kontrol Et")
        self.check_btn.setProperty("variant", "success")
        self.check_btn.clicked.connect(self.check_answer)
        btn_layout.addWidget(self.check_btn)

        self.skip_btn = QPushButton("→  Atla")
        self.skip_btn.clicked.connect(self.next_question)
        btn_layout.addWidget(self.skip_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Result
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px; padding: 12px;")
        layout.addWidget(self.result_label)

        layout.addStretch()

    def _show_question(self):
        if self.current_index >= self.total:
            self._show_results()
            return

        self._answered = False
        entry = self.entries[self.current_index]
        self.progress_bar.setValue(self.current_index)
        self.progress_bar.setFormat(f"Soru {self.current_index + 1} / {self.total}")
        self.question_label.setText(entry.word)

        poses = [t.part_of_speech for t in entry.translations if t.part_of_speech]
        if poses:
            self.hint_label.setText(f"İpucu: {', '.join(sorted(set(poses)))}")
        else:
            self.hint_label.setText("")

        self.answer_input.clear()
        self.result_label.clear()
        self.check_btn.setEnabled(True)
        self.answer_input.setEnabled(True)
        self.answer_input.setFocus()

    def check_answer(self):
        if self._answered:
            return
        self._answered = True
        self.check_btn.setEnabled(False)
        self.answer_input.setEnabled(False)

        entry = self.entries[self.current_index]
        user_answer = self.answer_input.text().strip().lower()
        correct_answers = [t.definition.strip().lower() for t in entry.translations]

        if user_answer in correct_answers:
            self.score += 1
            self.result_label.setText(
                f"✅ Doğru!  →  {', '.join(t.definition for t in entry.translations)}"
            )
        else:
            self.result_label.setText(
                f"❌ Yanlış!  →  Doğru cevap: {', '.join(t.definition for t in entry.translations)}"
            )

        QTimer.singleShot(1800, self.next_question)

    def next_question(self):
        self.current_index += 1
        self._show_question()

    def _show_results(self):
        self.progress_bar.setValue(self.total)
        self.progress_bar.setFormat("Tamamlandı")
        self.question_label.setText("🎉  Quiz Tamamlandı!")
        self.hint_label.setText(f"Skor: {self.score} / {self.total}")
        self.hint_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        percentage = (self.score / self.total * 100) if self.total > 0 else 0
        if percentage >= 80:
            self.result_label.setText("Mükemmel! 🌟")
        elif percentage >= 50:
            self.result_label.setText("İyi gidiyorsun! 👍")
        else:
            self.result_label.setText("Tekrar dene! 💪")

        self.answer_input.hide()
        self.check_btn.hide()

        try:
            self.skip_btn.clicked.disconnect()
        except Exception:
            pass
        self.skip_btn.setText("↺  Tekrar Oyna")
        self.skip_btn.clicked.connect(self._restart)

    def _restart(self):
        random.shuffle(self.entries)
        self.current_index = 0
        self.score = 0
        self._answered = False
        self.answer_input.show()
        self.check_btn.show()
        self.skip_btn.setText("→  Atla")
        try:
            self.skip_btn.clicked.disconnect()
        except Exception:
            pass
        self.skip_btn.clicked.connect(self.next_question)
        self._show_question()


class AddEntryDialog(QDialog):
    def __init__(self, parent=None, existing_word=None, existing_pair=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Kelime Ekle" if not existing_word else "Kelimeyi Düzenle")
        self.setModal(True)
        self.setMinimumWidth(680)
        self.existing_word = existing_word
        self.existing_pair = existing_pair
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(12)

        self.word_edit = QLineEdit()
        self.word_edit.setPlaceholderText("Kelimeyi girin")
        if self.existing_word:
            self.word_edit.setText(self.existing_word)
            self.word_edit.setReadOnly(True)
        form.addRow("Kelime:", self.word_edit)

        self.pair_combo = QComboBox()
        self.pair_combo.addItems(["ru-tr", "tr-ru", "en-tr", "tr-en"])
        if self.existing_pair:
            idx = self.pair_combo.findText(self.existing_pair)
            if idx >= 0:
                self.pair_combo.setCurrentIndex(idx)
                self.pair_combo.setEnabled(False)
        form.addRow("Dil Çifti:", self.pair_combo)

        layout.addLayout(form)

        # Translations
        trans_header = QLabel("Çeviriler:")
        trans_header.setStyleSheet("font-weight: bold; font-size: 15px; margin-top: 10px;")
        layout.addWidget(trans_header)

        self.translations_layout = QVBoxLayout()
        self.translation_widgets = []
        self.add_translation_row()
        layout.addLayout(self.translations_layout)

        add_trans_btn = QPushButton("+  Yeni Çeviri Ekle")
        add_trans_btn.setProperty("variant", "primary")
        add_trans_btn.clicked.connect(self.add_translation_row)
        layout.addWidget(add_trans_btn)

        layout.addStretch()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.word_edit.textChanged.connect(self.auto_tag)

    def add_translation_row(self, pos_text="", def_text="", ex_text=""):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setSpacing(10)
        row_layout.setContentsMargins(0, 0, 0, 0)

        pos_edit = QLineEdit()
        pos_edit.setPlaceholderText("Tür")
        pos_edit.setFixedWidth(110)
        if pos_text:
            pos_edit.setText(pos_text)

        def_edit = QLineEdit()
        def_edit.setPlaceholderText("Anlam / Çeviri")
        if def_text:
            def_edit.setText(def_text)

        ex_edit = QLineEdit()
        ex_edit.setPlaceholderText("Örnek cümle")
        if ex_text:
            ex_edit.setText(ex_text)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(32, 32)
        remove_btn.setToolTip("Kaldır")
        remove_btn.setProperty("variant", "danger")
        remove_btn.clicked.connect(lambda: self.remove_translation_row(row_widget))

        row_layout.addWidget(pos_edit)
        row_layout.addWidget(def_edit, 1)
        row_layout.addWidget(ex_edit, 1)
        row_layout.addWidget(remove_btn)

        self.translation_widgets.append((pos_edit, def_edit, ex_edit, row_widget))
        self.translations_layout.addWidget(row_widget)

    def remove_translation_row(self, widget):
        if len(self.translation_widgets) <= 1:
            QMessageBox.warning(self, "Uyarı", "En az bir çeviri tanımı olmalı.")
            return
        for i, (_, _, _, w) in enumerate(self.translation_widgets):
            if w is widget:
                w.deleteLater()
                del self.translation_widgets[i]
                break

    def auto_tag(self):
        word = self.word_edit.text().strip()
        if not word:
            return
        pair = self.pair_combo.currentText()
        source = pair.split("-")[0]
        tag = AutoTagger.tag(word, source)
        if self.translation_widgets:
            pos_edit, _, _, _ = self.translation_widgets[0]
            if not pos_edit.text():
                pos_edit.setText(tag)

    def get_entry(self) -> Optional[DictionaryEntry]:
        word = self.word_edit.text().strip()
        if not word:
            QMessageBox.warning(self, "Hata", "Kelime alanı boş olamaz.")
            return None
        pair = self.pair_combo.currentText()
        translations = []
        for pos_edit, def_edit, ex_edit, _ in self.translation_widgets:
            definition = def_edit.text().strip()
            if not definition:
                continue
            pos = pos_edit.text().strip() or "Noun"
            example = ex_edit.text().strip()
            translations.append(Translation(pos, definition, example))
        if not translations:
            QMessageBox.warning(self, "Hata", "En az bir anlam/çeviri gereklidir.")
            return None
        return DictionaryEntry(word, pair, translations, "not_started")

    def get_updated_entry(self, current_status: str, current_favorite: bool = False) -> Optional[DictionaryEntry]:
        entry = self.get_entry()
        if entry:
            entry.status = current_status
            entry.is_favorite = current_favorite
        return entry


class MoveEntryDialog(QDialog):
    def __init__(self, parent=None, current_pair=None):
        super().__init__(parent)
        self.setWindowTitle("Kelimeyi Taşı")
        self.setModal(True)
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        self.pair_combo = QComboBox()
        pairs = ["ru-tr", "tr-ru", "en-tr", "tr-en"]
        for p in pairs:
            if p != current_pair:
                self.pair_combo.addItem(p)
        form.addRow("Hedef Sözlük:", self.pair_combo)
        layout.addLayout(form)
        layout.addStretch()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_target_pair(self) -> str:
        return self.pair_combo.curren
        tText()

class ContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("İletişim ve Hakkında")
        self.setMinimumSize(460, 350)  # Pencere boyutu rahatlatıldı

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)  # İç boşluklar artırıldı
        layout.setSpacing(12)

        # Başlık
        title_label = QLabel("<h2 style='margin:0;'>Sözlük v2.0</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Geliştirici
        dev_label = QLabel("<p style='margin:0; font-size: 13px;'>Geliştirici: <b>Arda Talha Tekinel</b></p>")
        dev_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(dev_label)

        # İletişim İçeriği
        info_html = """
        <div style='line-height: 1.6; font-size: 13px;'>
            <p style='margin-bottom: 8px;'>Uygulamayla ilgili bir hata bildirimi veya öneride bulunmak için kanallar:</p>
            <ul style='margin-top: 0; padding-left: 18px;'>
                <li style='margin-bottom: 6px;'><b>GitHub:</b> <a style='color: #58a6ff;' href='https://github.com/arda803/final-dictionary/issues'>Hata / Öneri Bildir</a></li>
                <li style='margin-bottom: 6px;'><b>LinkedIn:</b> <a style='color: #58a6ff;' href='https://www.linkedin.com/in/arda-talha-tekinel-882176351/'>LinkedIn Profilim</a></li>
                <li><b>E-posta:</b> <a style='color: #58a6ff;' href='ardatalhatekinel@gmail.com'>ardatalhatekinel@gmail.com</a></li>
                <li style='margin-bottom: 6px;'><b>Youtube:</b> <a style='color: #58a6ff;' href='https://www.youtube.com/@Kedilercoksel314'>Youtube Kanalım</a></li>
            </ul>
        </div>
        """
        info_label = QLabel(info_html)
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)

        layout.addStretch()

        # Kapat Butonu
        btn_close = QPushButton("Kapat")
        btn_close.setMinimumHeight(36)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.setLayout(layout)
