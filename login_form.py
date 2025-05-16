# login_form.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class LoginForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập")
        self.setFixedSize(1000, 600)
        # Ảnh nền co giãn
        self.setStyleSheet(
            "QDialog { border-image: url('background.png') 0 0 0 0 stretch stretch; }"
        )
        self._init_ui()

    def _init_ui(self):
        # Layout ngang: logo | form
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(40)

        # --- Logo bên trái ---
        logo_label = QLabel()
        logo_pix = QPixmap('logo.png').scaled(
            350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )  # logo to vừa phải
        logo_label.setPixmap(logo_pix)
        logo_label.setAlignment(Qt.AlignCenter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addStretch()
        main_layout.addWidget(left, 1)

        # --- Form đăng nhập bên phải ---
        form = QWidget()
        form.setStyleSheet(
            "background-color: rgba(255,255,255,120); border-radius: 20px;"
        )
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(40, 50, 40, 40)
        form_layout.setSpacing(12)

        # Tiêu đề
        title = QLabel("Đăng nhập")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background: transparent; color: #333;")
        form_layout.addWidget(title)

        # Các trường: label trên input
        fields = [
            ('Email', False),
            ('Mật khẩu', True),
        ]
        for text, is_pwd in fields:
            lbl = QLabel(text)
            lbl.setFont(QFont('Arial', 14))
            lbl.setStyleSheet("background: transparent; color: #222;")
            inp = QLineEdit()
            inp.setPlaceholderText(text)
            inp.setFixedHeight(38)
            inp.setFont(QFont('Arial', 12))
            inp.setStyleSheet(
                "background-color: rgba(255,255,255,150);"
                " border: 1px solid #bbb; border-radius: 8px; padding-left: 10px;"
            )
            if is_pwd:
                inp.setEchoMode(QLineEdit.Password)
            form_layout.addWidget(lbl)
            form_layout.addWidget(inp)

        # Nút Đăng nhập
        btn = QPushButton('Đăng nhập')
        btn.setFont(QFont('Arial', 16, QFont.Bold))
        btn.setFixedHeight(48)
        btn.setStyleSheet(
            "background-color: #007bff; color: white; border-radius: 10px;"
        )
        form_layout.addWidget(btn)

        # Link sang Đăng ký
        link = QLabel('<a href="#">Chưa có tài khoản? Đăng ký</a>')
        link.setFont(QFont('Arial', 13))
        link.setAlignment(Qt.AlignCenter)
        link.setStyleSheet("background: transparent; color: #0645AD;")
        link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link.setOpenExternalLinks(False)
        form_layout.addWidget(link)

        form_layout.addStretch()
        main_layout.addWidget(form, 2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = LoginForm()
    dlg.show()
    sys.exit(app.exec_())
