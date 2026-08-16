from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class ContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("İletişim ve Hakkında")
        self.setFixedSize(380, 240)

        layout = QVBoxLayout()

        # Başlık
        title_label = QLabel("<h2>Sözlük v2.0</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # İletişim ve Geliştirici Bilgileri (HTML formatında tıklanabilir bağlantılar)
        info_html = """
        <p style='text-align: center;'>Geliştirici: <b>Arda Talha Tekinel</b></p>
        <hr>
        <p>Uygulamayla ilgili bir hata bildirimi veya öneride bulunmak için:</p>
        <ul>
            <li><b>GitHub:</b> <a href='https://github.com/arda803/final-dictionary/issues'>Hata / Öneri Bildir</a></li>
            <li><b>LinkedIn:</b> <a href='https://www.linkedin.com/in/kullanici-adiniz'>LinkedIn Profilim</a></li>
            <li><b>E-posta:</b> <a href='mailto:epostaniz@example.com'>epostaniz@example.com</a></li>
        </ul>
        """
        info_label = QLabel(info_html)
        # Linklerin bilgisayarın varsayılan tarayıcısında açılmasını sağlar
        info_label.setOpenExternalLinks(True) 
        layout.addWidget(info_label)

        # Kapat Butonu
        btn_close = QPushButton("Kapat")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.setLayout(layout)
