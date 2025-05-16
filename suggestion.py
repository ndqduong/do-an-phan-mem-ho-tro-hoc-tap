import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QComboBox, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from menu import SidebarMenu

class SuggestionPage(QWidget):
    """
    Trang Gợi ý thời khóa biểu, giống giao diện Home/Management.
    """
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        # Content nền trắng bo góc
        self.setStyleSheet("background-color: #f0f2f5;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Panel config
        panel = QFrame()
        panel.setStyleSheet(
            "background-color: white; border-radius: 10px;"
        )
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(40)

        # Tiết trống
        lbl_slot = QLabel("Tiết trống:")
        cb_slot = QComboBox()
        cb_slot.addItem("-- Chọn tiết trống --")
        for i in range(1, 9): cb_slot.addItem(f"Tiết {i}")
        cb_slot.setFixedWidth(150)

        # Số tiết tối đa
        lbl_max = QLabel("Số tiết tối đa:")
        self.spin_max = QSpinBox()
        self.spin_max.setRange(1, 8)
        self.spin_max.setValue(6)
        self.spin_max.setFixedWidth(80)

        # Môn ưu tiên
        lbl_prior = QLabel("Môn ưu tiên:")
        cb_prior = QComboBox()
        cb_prior.addItem("-- Chọn môn học --")
        cb_prior.setFixedWidth(150)

        # Môn loại trừ
        lbl_ex = QLabel("Môn loại trừ:")
        cb_ex = QComboBox()
        cb_ex.addItem("-- Chọn môn học --")
        cb_ex.setFixedWidth(150)

        # Nút tạo gợi ý
        btn = QPushButton("Tạo gợi ý")
        btn.setStyleSheet(
            "background-color: #007bff; color: white; border: none; border-radius: 5px; padding: 8px 24px;"
        )
        btn.setFixedHeight(36)
        btn.clicked.connect(self._on_suggest)

        panel_layout.addWidget(lbl_slot)
        panel_layout.addWidget(cb_slot)
        panel_layout.addWidget(lbl_max)
        panel_layout.addWidget(self.spin_max)
        panel_layout.addWidget(lbl_prior)
        panel_layout.addWidget(cb_prior)
        panel_layout.addWidget(lbl_ex)
        panel_layout.addWidget(cb_ex)
        panel_layout.addStretch()
        panel_layout.addWidget(btn)

        layout.addWidget(panel)

        # Label tháng
        lbl_month = QLabel("THÁNG 4, 2024")
        lbl_month.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl_month)

        # Bảng gợi ý
        self.table = QTableWidget(6, 6)
        days = ['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7']
        self.table.setHorizontalHeaderLabels(days)
        self.table.setVerticalHeaderLabels([f"Tiết {i}" for i in range(1,7)])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setStyleSheet(
            "QTableWidget { background: white; gridline-color: #ddd; }"
        )
        layout.addWidget(self.table)

    def _on_suggest(self):
        max_slots = self.spin_max.value()
        # Clear bảng
        for r in range(6):
            for c in range(6):
                self.table.setItem(r, c, QTableWidgetItem(""))
        # Đánh dấu màu xanh giống Home/Management button
        for c in range(6):
            for r in range(max_slots):
                item = QTableWidgetItem("")
                item.setBackground(Qt.darkBlue if c % 2 else Qt.darkCyan)
                self.table.setItem(r, c, item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lịch Học Thông Minh")
        self.resize(1200, 700)

        # Central widget và layout
        central = QWidget()
        central.setStyleSheet("background-color: #001f3f;")
        self.setCentralWidget(central)
        h = QHBoxLayout(central)

        # Sidebar cùng màu và menu giống home.py
        self.sidebar = SidebarMenu(self)
        h.addWidget(self.sidebar)

        # Suggestion page
        self.suggest_page = SuggestionPage()
        h.addWidget(self.suggest_page)

        # Kết nối menu nếu cần
        self.sidebar.menuClicked.connect(lambda key: None)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
