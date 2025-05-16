import qtawesome as qta
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy

class SidebarMenu(QWidget):
    """
    Thanh điều hướng bên trái, chỉ chứa các nút menu.
    """
    menuClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("background-color: #0d3a66;")  # nền xanh đậm
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Các mục menu: (key, qtawesome icon, label)
        menu_items = [
            ('overview', 'fa.home', 'Trang chủ'),
            ('courses',  'fa.book', 'Quản lý môn học'),
            ('classes',  'fa.users', 'Quản lý lớp học'),
            ('suggest',  'fa.calendar-check-o', 'Gợi ý thời khóa biểu'),
            ('plan',     'fa.clipboard', 'Lập kế hoạch ôn tập'),
            ('games',    'fa.gamepad', 'Trò chơi học tập'),
            ('reminder', 'fa.bell', 'Nhắc nhở'),
            ('chat',     'fa.envelope', 'Chat nhóm'),
        ]

        for key, icon_name, text in menu_items:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setIcon(qta.icon(icon_name, color='white'))
            btn.setIconSize(QSize(20, 20))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setStyleSheet(
                """
                QPushButton {
                    color: white;
                    background: none;
                    border: none;
                    text-align: left;
                    padding: 8px 0;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #145a96;
                }
                QPushButton:pressed {
                    background-color: #0a2c4f;
                }
                """
            )
            btn.clicked.connect(lambda _, k=key: self.menuClicked.emit(k))
            layout.addWidget(btn)

        layout.addStretch()
