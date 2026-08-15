#!/usr/bin/env python3
import sys
import os

# Windows görev çubuğu ikonu için AppUserModelID - BUNU EN BAŞTA YAP
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("arda.sozluk.app.v2")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow


def get_icon_path():
    """PyInstaller ile çalışırken doğru yolu bul"""
    if getattr(sys, 'frozen', False):
        # PyInstaller ile çalışıyoruz
        base_path = sys._MEIPASS
    else:
        # Normal Python çalıştırması
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(base_path, "logo.ico")
    
    # Eğer bulunamazsa, exe'nin yanına da bak
    if not os.path.exists(icon_path) and getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        alt_path = os.path.join(exe_dir, "logo.ico")
        if os.path.exists(alt_path):
            return alt_path
    
    return icon_path


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sözlük")
    app.setApplicationVersion("2.0")
    
    # İkonu yükle
    icon_path = get_icon_path()
    print(f"Ikon yolu: {icon_path}")  # Debug için
    
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        print("Ikon yüklendi")
    else:
        print(f"UYARI: Ikon bulunamadı: {icon_path}")
    
    window = MainWindow()
    
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    
    window.setWindowTitle("Sözlük")
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()