"""Main application window."""
import random
from functools import cmp_to_key

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QComboBox,
    QPushButton, QLabel, QFileDialog, QMessageBox, QSplitter,
    QMenuBar, QMenu, QStatusBar, QDialog, QInputDialog, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QKeySequence

from ..database import DictionaryDB
from ..tts import TTSManager
from ..models import DictionaryEntry, Translation
from ..utils import (
    SettingsManager, compare_entries, STATUS_LABELS, LANGUAGE_NAMES,
    ImportExport,
)
from ..themes import ThemeManager
from .widgets import DetailPanel

from .dialogs import SettingsDialog, QuizDialog, AddEntryDialog, MoveEntryDialog, ContactDialog
from PyQt6.QtGui import QAction, QFont, QKeySequence, QIcon  # ← QIcon ekle
# Diğer dialog importlarının yanına ekleyin

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("logo.ico"))  # ← BUNU EKLE
        self.settings = SettingsManager()
        # ... devamı
        self.db = DictionaryDB()
        self.tts = TTSManager()
        self.theme_manager = ThemeManager()

        self.current_entries = []
        self.all_entries = self.db.get_all_entries()
        self.all_entries.sort(key=cmp_to_key(compare_entries))
        self.current_entries = self.all_entries[:]
        self.current_entry = None

        self.init_ui()
        self.apply_theme()
        self.populate_list()
        self.populate_filter_tags()
        self.update_statistics()
        self.restore_geometry()
        self.search_input.setFocus()

    def init_ui(self):
        self.setWindowTitle("Sözlük — Offline Desktop Dictionary")
        self.setGeometry(100, 100, 1500, 900)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(14)
        left_layout.setContentsMargins(18, 18, 18, 18)

        self._build_menu()
        self._build_toolbar(left_layout)
        self._build_search(left_layout)
        self._build_main_content(left_layout)

        # Right sidebar
        right_widget = QWidget()
        right_widget.setFixedWidth(300)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(14)
        right_layout.setContentsMargins(18, 18, 18, 18)
        self._build_sidebar(right_layout)

        main_layout.addWidget(left_widget, 4)
        main_layout.addWidget(right_widget, 1)

        self.statusBar().showMessage("Hazır")

    def _build_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Dosya")
        import_menu = QMenu("İçe Aktar", self)
        file_menu.addMenu(import_menu)
        for fmt in ["JSON", "Excel", "TXT"]:
            action = QAction(f"{fmt} İçe Aktar...", self)
            action.triggered.connect(lambda checked, f=fmt: self.import_data(f))
            import_menu.addAction(action)

        export_menu = QMenu("Dışa Aktar", self)
        file_menu.addMenu(export_menu)
        for fmt in ["JSON", "Excel", "TXT"]:
            action = QAction(f"{fmt} Dışa Aktar...", self)
            action.triggered.connect(lambda checked, f=fmt: self.export_data(f))
            export_menu.addAction(action)

        file_menu.addSeparator()

        quiz_action = QAction("🎯 Kelime Quiz", self)
        quiz_action.setShortcut(QKeySequence("Ctrl+Q"))
        quiz_action.triggered.connect(self.start_quiz)
        file_menu.addAction(quiz_action)

        word_of_day_action = QAction("📖 Günün Kelimesi", self)
        word_of_day_action.triggered.connect(self.show_word_of_day)
        file_menu.addAction(word_of_day_action)

        file_menu.addSeparator()

        settings_action = QAction("⚙ Ayarlar", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        clear_action = QAction("🗑 Tüm Verileri Temizle", self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

        exit_action = QAction("Çıkış", self)
        exit_action.setShortcut(QKeySequence("Ctrl+W"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("Görünüm")
        theme_menu = QMenu("Tema", self)
        view_menu.addMenu(theme_menu)

        self.light_theme_action = QAction("☀ Açık Tema", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(self.light_theme_action)

        self.dark_theme_action = QAction("🌙 Koyu Tema", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(self.dark_theme_action)

        help_menu = menubar.addMenu("Yardım")
        shortcuts_action = QAction("⌨ Klavye Kısayolları", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
# --- EKLENEN KISIM ---
        contact_action = QAction("📬 İletişim & Geri Bildirim", self)
        contact_action.triggered.connect(self.open_contact_dialog)
        help_menu.addAction(contact_action)
        # ---------------------        
        about_action = QAction("ℹ Hakkında", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _build_toolbar(self, layout):
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.add_btn = QPushButton("+ Yeni Kelime")
        self.add_btn.setShortcut(QKeySequence("Ctrl+N"))
        self.add_btn.setProperty("variant", "success")
        self.add_btn.clicked.connect(self.add_entry)
        toolbar.addWidget(self.add_btn)

        toolbar.addSpacing(16)

        for label, fmt in [("JSON", "JSON"), ("Excel", "Excel"), ("TXT", "TXT")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, f=fmt: self.export_data(f))
            toolbar.addWidget(btn)

        toolbar.addStretch()

        # Tema butonu — daha görünür
        self.theme_btn = QPushButton("🌙  Koyu Tema")
        self.theme_btn.setProperty("variant", "theme")
        self.theme_btn.setMinimumWidth(140)
        self.theme_btn.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_btn)

        toolbar.addSpacing(10)

        self.fav_filter_btn = QPushButton("⭐ Favoriler")
        self.fav_filter_btn.setCheckable(True)
        self.fav_filter_btn.clicked.connect(self.apply_filters)
        toolbar.addWidget(self.fav_filter_btn)

        layout.addLayout(toolbar)

    def _build_search(self, layout):
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setSpacing(10)
        search_layout.setContentsMargins(14, 10, 14, 10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Kelime, anlam veya örnek cümle ara...")
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(self.search_input, 2)

        search_layout.addWidget(QLabel("Dil:"))
        self.pair_filter_combo = QComboBox()
        self.pair_filter_combo.addItem("Tümü")
        self.pair_filter_combo.addItems(["ru-tr", "tr-ru", "en-tr", "tr-en"])
        self.pair_filter_combo.currentTextChanged.connect(self.apply_filters)
        search_layout.addWidget(self.pair_filter_combo)

        search_layout.addWidget(QLabel("Tür:"))
        self.pos_filter_combo = QComboBox()
        self.pos_filter_combo.addItem("Tümü")
        self.pos_filter_combo.currentTextChanged.connect(self.apply_filters)
        search_layout.addWidget(self.pos_filter_combo)

        search_layout.addWidget(QLabel("Durum:"))
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["Tümü", "Öğrenilmedi", "Öğreniliyor", "Öğrenildi"])
        self.status_filter_combo.currentTextChanged.connect(self.apply_filters)
        search_layout.addWidget(self.status_filter_combo)

        layout.addWidget(search_frame)

    def _build_main_content(self, layout):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Word list
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.list_widget.itemSelectionChanged.connect(self.on_select)
        list_layout.addWidget(self.list_widget)

        splitter.addWidget(list_container)

        # Detail panel
        self.detail_panel = DetailPanel(self.tts)
        self.detail_panel.speak_requested.connect(self.on_speak_requested)
        self.detail_panel.copy_requested.connect(self.on_copy_requested)
        self.detail_panel.status_changed.connect(self.on_detail_status_changed)
        self.detail_panel.favorite_toggled.connect(self.on_detail_favorite_toggled)
        self.detail_panel.edit_requested.connect(self.edit_current_entry)
        self.detail_panel.delete_requested.connect(self.delete_current_entry)

        splitter.addWidget(self.detail_panel)
        splitter.setSizes([400, 700])
        layout.addWidget(splitter)

    def _build_sidebar(self, layout):
        # Stats
        stats_label = QLabel("📊  İstatistikler")
        stats_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(stats_label)

        self.total_label = QLabel("Toplam: 0")
        self.learned_label = QLabel("Öğrenilen: 0")
        self.learning_label = QLabel("Öğreniliyor: 0")
        self.not_started_label = QLabel("Başlanmamış: 0")
        self.favorites_label = QLabel("Favori: 0")

        for lbl in [self.total_label, self.learned_label, self.learning_label,
                    self.not_started_label, self.favorites_label]:
            layout.addWidget(lbl)

        # Progress bar for learned words
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)

        layout.addSpacing(20)

        # Status list
        status_label = QLabel("📋  Tüm Kelimeler")
        status_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(status_label)

        self.status_list_widget = QListWidget()
        self.status_list_widget.itemClicked.connect(self.on_status_list_click)
        layout.addWidget(self.status_list_widget)

        layout.addStretch()

    def apply_theme(self):
        theme = self.settings.get("theme", "light")
        self.theme_manager.set_theme(theme)
        self.light_theme_action.setChecked(theme == "light")
        self.dark_theme_action.setChecked(theme == "dark")

        # Tema butonu metnini güncelle
        if self.theme_manager.is_dark():
            self.theme_btn.setText("☀️  Açık Tema")
        else:
            self.theme_btn.setText("🌙  Koyu Tema")

        app = QApplication.instance()
        if app:
            app.setStyleSheet(self.theme_manager.get_stylesheet())

    def set_theme(self, theme):
        self.settings.set("theme", theme)
        self.apply_theme()

    def toggle_theme(self):
        new_theme = self.theme_manager.toggle_theme()
        self.settings.set("theme", new_theme)
        self.apply_theme()

    def restore_geometry(self):
        geo = self.settings.get("window_geometry")
        if geo:
            try:
                self.restoreGeometry(bytes.fromhex(geo))
            except Exception:
                pass

    def save_geometry(self):
        try:
            self.settings.set("window_geometry", self.saveGeometry().toHex().data().decode())
        except Exception:
            pass

    def on_speak_requested(self, text, lang):
        if not self.settings.get("tts_enabled", True):
            QMessageBox.information(self, "Seslendirme", "Seslendirme kapalı. Ayarlardan açabilirsiniz.")
            return

        def on_start():
            self.statusBar().showMessage(f"🔊 Ses hazırlanıyor: {text}")

        def on_finish():
            self.statusBar().showMessage("✓ Seslendirme tamamlandı", 3000)

        def on_error(msg):
            self.statusBar().showMessage(f"✗ Seslendirme hatası: {msg}", 5000)
            QMessageBox.warning(self, "Seslendirme Hatası", msg)

        rate = self.settings.get("tts_rate", 0)
        self.tts.speak(text, lang, rate=rate, on_start=on_start, on_finish=on_finish, on_error=on_error)

    def on_copy_requested(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.statusBar().showMessage(f"📋 Panoya kopyalandı: {text}", 2000)

    def on_detail_status_changed(self, status):
        if self.current_entry:
            self.current_entry.status = status
            self.db.update_entry(self.current_entry)
            self.refresh_view()

    def on_detail_favorite_toggled(self, is_favorite):
        if self.current_entry:
            self.current_entry.is_favorite = is_favorite
            self.db.update_entry(self.current_entry)
            self.refresh_view()

    def edit_current_entry(self):
        if not self.current_entry:
            return
        dialog = AddEntryDialog(self, self.current_entry.word, self.current_entry.language_pair)
        for i, trans in enumerate(self.current_entry.translations):
            if i == 0:
                dialog.translation_widgets[0][0].setText(trans.part_of_speech)
                dialog.translation_widgets[0][1].setText(trans.definition)
                dialog.translation_widgets[0][2].setText(trans.example)
            else:
                dialog.add_translation_row(trans.part_of_speech, trans.definition, trans.example)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            entry = dialog.get_updated_entry(
                self.current_entry.status,
                self.current_entry.is_favorite
            )
            if entry:
                self.db.update_entry(entry)
                self.refresh_view()
                self.on_select()
                QMessageBox.information(self, "Başarılı", f"'{entry.word}' güncellendi.")

    def delete_current_entry(self):
        if not self.current_entry:
            return
        reply = QMessageBox.question(
            self, "Silme Onayı",
            f"'{self.current_entry.word}' silinecek. Emin misiniz?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_entry(self.current_entry.word, self.current_entry.language_pair)
            self.current_entry = None
            self.refresh_view()
            self.detail_panel.set_entry(None)
            QMessageBox.information(self, "Silindi", "Kelime silindi.")

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        menu = QMenu()
        move_action = QAction("Başka Sözlüğe Taşı...", self)
        move_action.triggered.connect(lambda: self.move_entry(entry))
        menu.addAction(move_action)

        fav_action = QAction(
            "Favorilerden Çıkar" if entry.is_favorite else "Favorilere Ekle",
            self
        )
        fav_action.triggered.connect(lambda: self.toggle_favorite_from_menu(entry))
        menu.addAction(fav_action)
        menu.exec(self.list_widget.mapToGlobal(pos))

    def toggle_favorite_from_menu(self, entry):
        entry.is_favorite = not entry.is_favorite
        self.db.update_entry(entry)
        self.refresh_view()
        if (self.current_entry and
                self.current_entry.word == entry.word and
                self.current_entry.language_pair == entry.language_pair):
            self.detail_panel.set_entry(entry)

    def move_entry(self, entry):
        dialog = MoveEntryDialog(self, entry.language_pair)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            target_pair = dialog.get_target_pair()
            new_entry = DictionaryEntry(
                entry.word, target_pair, entry.translations, entry.status, entry.is_favorite
            )
            self.db.delete_entry(entry.word, entry.language_pair)
            success, msg = self.db.add_entry(new_entry)
            if success:
                self.refresh_view()
                QMessageBox.information(self, "Başarılı", "Kelime başarıyla taşındı.")
            else:
                self.db.add_entry(entry)
                QMessageBox.warning(self, "Hata", f"Taşıma başarısız: {msg}")

    def apply_filters(self):
        search_text = self.search_input.text().strip()
        pair_filter = self.pair_filter_combo.currentText()
        pos_filter = self.pos_filter_combo.currentText()
        status_filter = self.status_filter_combo.currentText()
        show_favorites_only = self.fav_filter_btn.isChecked()

        if search_text:
            results = self.db.search_entries(search_text)
        else:
            results = self.db.get_all_entries()

        results.sort(key=cmp_to_key(compare_entries))

        if pair_filter != "Tümü":
            results = [e for e in results if e.language_pair == pair_filter]
        if pos_filter != "Tümü":
            results = [e for e in results if any(t.part_of_speech == pos_filter for t in e.translations)]
        if status_filter != "Tümü":
            reverse_map = {v: k for k, v in STATUS_LABELS.items()}
            status_key = reverse_map.get(status_filter, "")
            results = [e for e in results if e.status == status_key]
        if show_favorites_only:
            results = [e for e in results if e.is_favorite]

        self.current_entries = results
        self.populate_list()

    def on_select(self):
        selected = self.list_widget.currentItem()
        if not selected:
            return
        entry = selected.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        self.current_entry = entry
        self.detail_panel.set_entry(entry)

        if self.settings.get("auto_tts", False) and self.settings.get("tts_enabled", True):
            lang = self.tts.get_source_lang(entry.language_pair)
            rate = self.settings.get("tts_rate", 0)
            self.tts.speak(entry.word, lang, rate=rate)

    def populate_list(self):
        self.list_widget.clear()
        for entry in self.current_entries:
            item = QListWidgetItem()
            if entry.is_favorite:
                item.setText(f"★ {entry.word}")
                item.setToolTip(f"{entry.word} (Favori)")
            else:
                item.setText(entry.word)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.list_widget.addItem(item)
        self.statusBar().showMessage(f"{len(self.current_entries)} kayıt")

    def populate_filter_tags(self):
        tags = self.db.get_all_tags()
        self.pos_filter_combo.clear()
        self.pos_filter_combo.addItem("Tümü")
        self.pos_filter_combo.addItems(sorted(tags))

    def add_entry(self):
        dialog = AddEntryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entry = dialog.get_entry()
            if entry:
                success, msg = self.db.add_entry(entry)
                if success:
                    self.refresh_view()
                    QMessageBox.information(self, "Başarılı", f"'{entry.word}' eklendi.")
                else:
                    QMessageBox.warning(self, "Uyarı", msg)

    def import_data(self, fmt=None):
        if fmt is None:
            formats = ["JSON", "Excel", "TXT"]
            item, ok = QInputDialog.getItem(self, "İçe Aktar", "Format seçin:", formats, 0, False)
            if not ok or not item:
                return
            fmt = item
        ext = fmt.lower()
        file_filter = f"{fmt} Files (*.{ext})"
        if fmt == "TXT":
            file_filter = "Text Files (*.txt)"
        filepath, _ = QFileDialog.getOpenFileName(self, f"İçe Aktar {fmt}", "", file_filter)
        if not filepath:
            return
        try:
            if fmt == "JSON":
                entries = ImportExport.import_json(filepath)
            elif fmt == "Excel":
                entries = ImportExport.import_excel(filepath)
            elif fmt == "TXT":
                entries = ImportExport.import_txt(filepath)
            else:
                return
            added, skipped = self.db.import_entries(entries)
            self.refresh_view()
            QMessageBox.information(self, "Tamamlandı", f"Eklenen: {added}, Atlanan: {skipped}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İçe aktarma başarısız: {str(e)}")

    def export_data(self, fmt):
        ext = fmt.lower()
        file_filter = f"{fmt} Files (*.{ext})"
        if fmt == "TXT":
            file_filter = "Text Files (*.txt)"
        filepath, _ = QFileDialog.getSaveFileName(self, f"Dışa Aktar {fmt}", "", file_filter)
        if not filepath:
            return
        try:
            entries = self.db.get_all_entries()
            if fmt == "JSON":
                ImportExport.export_json(entries, filepath)
            elif fmt == "Excel":
                ImportExport.export_excel(entries, filepath)
            elif fmt == "TXT":
                ImportExport.export_txt(entries, filepath)
            QMessageBox.information(self, "Başarılı", f"Veriler kaydedildi: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız: {str(e)}")

    def clear_all(self):
        reply = QMessageBox.question(
            self, "Tümünü Temizle",
            "Tüm veriler silinecek. Devam etmek istiyor musunuz?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_all()
            self.refresh_view()
            self.statusBar().showMessage("Veritabanı temizlendi.")

    def refresh_view(self):
        self.all_entries = self.db.get_all_entries()
        self.all_entries.sort(key=cmp_to_key(compare_entries))
        self.apply_filters()
        self.populate_filter_tags()
        self.update_statistics()

    def update_statistics(self):
        stats = self.db.get_stats()
        self.total_label.setText(f"Toplam: {stats['total']}")
        self.learned_label.setText(f"✅ Öğrenilen: {stats['learned']}")
        self.learning_label.setText(f"📖 Öğreniliyor: {stats['learning']}")
        self.not_started_label.setText(f"⏳ Başlanmamış: {stats['not_started']}")
        self.favorites_label.setText(f"⭐ Favori: {stats['favorites']}")

        # Update progress bar color based on learned percentage
        total = stats['total']
        if total > 0:
            pct = stats['learned'] / total * 100
            self.progress_bar.setStyleSheet(f"""
                QFrame {{
                    background-color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1f883d,
                        stop:{pct/100:.2f} #1f883d,
                        stop:{pct/100:.2f} #d0d7de,
                        stop:1 #d0d7de
                    );
                    border-radius: 4px;
                }}
            """)

        self.update_status_list()

    def update_status_list(self):
        entries = self.db.get_all_entries()
        entries.sort(key=cmp_to_key(compare_entries))
        self.status_list_widget.clear()
        for e in entries:
            item = QListWidgetItem(f"{e.word} ({e.language_pair})")
            item.setData(Qt.ItemDataRole.UserRole, e)
            self.status_list_widget.addItem(item)

    def on_status_list_click(self, item):
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        for i in range(self.list_widget.count()):
            it = self.list_widget.item(i)
            data = it.data(Qt.ItemDataRole.UserRole)
            if data and data.word == entry.word and data.language_pair == entry.language_pair:
                self.list_widget.setCurrentItem(it)
                break

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_theme()

    def start_quiz(self):
        dialog = QuizDialog(self.db, self)
        dialog.exec()

    def show_word_of_day(self):
        entries = self.db.get_all_entries()
        if not entries:
            QMessageBox.information(self, "Günün Kelimesi", "Sözlükte kelime yok.")
            return
        entry = random.choice(entries)
        translations_text = "\n".join([f"• {t.definition}" for t in entry.translations])
        QMessageBox.information(
            self, "Günün Kelimesi",
            f"<b style='font-size:18px;'>{entry.word}</b> "
            f"<span style='color:#656d76;'>({entry.language_pair})</span>"
            f"<br><br>{translations_text}"
        )

    def show_shortcuts(self):
        msg = (
            "<b>Klavye Kısayolları</b><br><br>"
            "<table>"
            "<tr><td><b>Ctrl+N</b></td><td>Yeni kelime ekle</td></tr>"
            "<tr><td><b>Ctrl+F</b></td><td>Arama kutusuna odaklan</td></tr>"
            "<tr><td><b>Ctrl+Q</b></td><td>Kelime quiz</td></tr>"
            "<tr><td><b>Ctrl+,</b></td><td>Ayarlar</td></tr>"
            "<tr><td><b>Ctrl+W</b></td><td>Uygulamayı kapat</td></tr>"
            "<tr><td><b>Delete</b></td><td>Seçili kelimeyi sil</td></tr>"
            "<tr><td><b>F5</b></td><td>Listeyi yenile</td></tr>"
            "</table>"
        )
        QMessageBox.information(self, "Klavye Kısayolları", msg)

    def show_about(self):
        QMessageBox.about(
            self, "Hakkında",
            "<b>Sözlük v2.0</b><br><br>"
            "Offline Desktop Dictionary<br><br>"
            "<b>Özellikler:</b><br>"
            "• Rusça-Türkçe / İngilizce-Türkçe<br>"
            "• Sesli telaffuz (TTS)<br>"
            "• Kelime quiz<br>"
            "• Favoriler<br>"
            "• Koyu/Açık tema<br>"
            "• JSON/Excel/TXT içe/dışa aktarma"
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            if self.list_widget.hasFocus():
                self.delete_current_entry()
        elif event.key() == Qt.Key.Key_F5:
            self.refresh_view()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_F:
            self.search_input.setFocus()
        super().keyPressEvent(event)

    def closeEvent(self, event):
        self.save_geometry()
        self.tts.stop()
        self.db.close()
        event.accept()
