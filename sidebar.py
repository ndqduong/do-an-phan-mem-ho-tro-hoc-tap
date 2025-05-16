# sidebar.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt5.QtGui     import QIcon, QPixmap, QFont
from PyQt5.QtCore    import Qt, pyqtSignal, QSize

class SidebarMenu(QWidget):
    menuClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # chiều rộng cố định
        self.setFixedWidth(260)
        # nền xanh đậm
        self.setStyleSheet("background-color: #0d3a66;")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20,20,20,20)
        lay.setSpacing(15)

        # --- Logo ---
        logo = QLabel()
        pix = QPixmap("icons/logo.png")   # đường dẫn tới logo của bạn
        pix = pix.scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pix)
        lay.addWidget(logo, alignment=Qt.AlignCenter)

        # --- Title ---
        title = QLabel("LỊCH HỌC THÔNG MINH")
        title.setFont(QFont("Arial",14,QFont.Bold))
        title.setStyleSheet("color:white; margin-top:8px;")
        lay.addWidget(title, alignment=Qt.AlignCenter)
        lay.addSpacing(20)

        # --- Menu items ---
        items = [
            ("Trang chủ",           "icons/home.svg"),
            ("Quản lý môn học",     "icons/book-open.svg"),
            ("Quản lý lớp học",     "icons/users.svg"),
            ("Gợi ý thời khóa biểu","icons/calendar-check.svg"),
            ("Lập kế hoạch ôn tập",  "icons/clipboard.svg"),
            ("Nhắc nhở",            "icons/bell.svg"),
            ("Chat nhóm",           "icons/message-circle.svg"),
        ]
        for text, icon_path in items:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(20,20))
            btn.setStyleSheet(
                "color:white;"
                "background:none;"
                "border:none;"
                "text-align:left;"
                "padding:8px 0;"
                "font-size:13px;"
            )
            btn.clicked.connect(lambda _, t=text: self.menuClicked.emit(t))
            lay.addWidget(btn)

        lay.addStretch()
