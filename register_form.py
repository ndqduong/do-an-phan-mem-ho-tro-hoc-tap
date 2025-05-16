# register_form.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class RegisterForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng ký")
        self.setFixedSize(1000, 600)  # Kích thước form
        # Ảnh nền tự co giãn
        self.setStyleSheet(
            "QDialog { border-image: url('background.png') 0 0 0 0 stretch stretch; }"
        )
        self._init_ui()

    def _init_ui(self):
        # Layout chính ngang: logo | form
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(40)

        # --- Logo bên trái ---
        logo_label = QLabel()
        logo_pix = QPixmap('logo.png').scaled(
            350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )  # Logo lớn hơn
        logo_label.setPixmap(logo_pix)
        logo_label.setAlignment(Qt.AlignCenter)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addStretch()
        main_layout.addWidget(left_container, 1)

        # --- Form đăng ký bên phải ---
        form_container = QWidget()
        form_container.setStyleSheet(
            "background-color: rgba(255,255,255,120); border-radius: 20px;"
        )  # Nền trắng mờ hơn
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 50, 40, 40)  # Tăng margin trên để không che title
        form_layout.setSpacing(8)

        # Tiêu đề
        title = QLabel("Đăng ký")
        title.setFont(QFont('Arial', 20, QFont.Bold))  # Giảm size để không bị cắt chân
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background: transparent; color: #333;")
        form_layout.addWidget(title)

        # Các trường: label trên input, sát nhau
        fields = [
            ('Họ và tên', False),
            ('Email', False),
            ('Mật khẩu', True),
            ('Xác nhận mật khẩu', True),
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
            )  # Nền input mờ hơn
            if is_pwd:
                inp.setEchoMode(QLineEdit.Password)
            form_layout.addWidget(lbl)
            form_layout.addWidget(inp)

        # Nút Đăng ký
        btn = QPushButton('Đăng ký')
        btn.setFont(QFont('Arial', 16, QFont.Bold))
        btn.setFixedHeight(48)
        btn.setStyleSheet(
            "background-color: #28a745; color: white; border-radius: 10px;"
        )
        form_layout.addWidget(btn)

        # Link quay lại đăng nhập
        back = QLabel('<a href="#">Quay lại đăng nhập</a>')
        back.setFont(QFont('Arial', 13))
        back.setAlignment(Qt.AlignCenter)
        back.setStyleSheet("background: transparent; color: #0645AD;")
        back.setTextInteractionFlags(Qt.TextBrowserInteraction)
        back.setOpenExternalLinks(False)
        form_layout.addWidget(back)

        form_layout.addStretch()
        main_layout.addWidget(form_container, 2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = RegisterForm()
    dlg.show()
    sys.exit(app.exec_())
