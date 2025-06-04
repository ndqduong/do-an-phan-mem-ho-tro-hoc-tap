# home.py
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QStackedWidget, QFrame, QSizePolicy,
    QGridLayout, QCalendarWidget, QListWidget
)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt

from chat import ChatWidget
from menu import SidebarMenu
from management import CourseManagementWidget, ClassManagementWidget
from suggestion import SuggestionPage
from study_plan import StudyPlanWidget

DB_PATH = 'lichhoc.db'


class OverviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("background-color: #001f3f;")
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(20)

        # Calendar card
        cal_card = QFrame()
        cal_card.setStyleSheet("background-color:#224870; border-radius:10px;")
        cal_layout = QVBoxLayout(cal_card)
        cal_layout.setContentsMargins(16, 16, 16, 16)
        lbl_month = QLabel("THÁNG 4, 2024")
        lbl_month.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_month.setStyleSheet("color:white;")
        cal_layout.addWidget(lbl_month)
        cal = QCalendarWidget()
        cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        cal.setStyleSheet("QCalendarWidget { background-color:#224870; color:white; }")
        cal_layout.addWidget(cal)
        grid.addWidget(cal_card, 0, 0)

        # Số môn học card
        card1 = QFrame()
        card1.setStyleSheet("background-color:#3B82F6; border-radius:10px;")
        c1 = QVBoxLayout(card1)
        c1.setContentsMargins(16, 16, 16, 16)
        icon1 = QLabel()
        icon1.setPixmap(QIcon("icons/book-open.svg").pixmap(32, 32))
        c1.addWidget(icon1)
        c1.addStretch()
        lbl1 = QLabel("Số môn học")
        lbl1.setFont(QFont("Arial", 10))
        lbl1.setStyleSheet("color:white;")
        num1 = QLabel("5")
        num1.setFont(QFont("Arial", 24, QFont.Bold))
        num1.setStyleSheet("color:white;")
        c1.addWidget(lbl1)
        c1.addWidget(num1, alignment=Qt.AlignRight)
        grid.addWidget(card1, 0, 1)

        # Lớp học tuần này card
        card2 = QFrame()
        card2.setStyleSheet("background-color:#10B981; border-radius:10px;")
        c2 = QVBoxLayout(card2)
        c2.setContentsMargins(16, 16, 16, 16)
        icon2 = QLabel()
        icon2.setPixmap(QIcon("icons/calendar.svg").pixmap(32, 32))
        c2.addWidget(icon2)
        c2.addStretch()
        lbl2 = QLabel("Lớp học tuần này")
        lbl2.setFont(QFont("Arial", 10))
        lbl2.setStyleSheet("color:white;")
        num2 = QLabel("10")
        num2.setFont(QFont("Arial", 24, QFont.Bold))
        num2.setStyleSheet("color:white;")
        c2.addWidget(lbl2)
        c2.addWidget(num2, alignment=Qt.AlignRight)
        grid.addWidget(card2, 0, 2)

        # Thời khóa biểu card
        table_card = QFrame()
        table_card.setStyleSheet("background-color:white; border-radius:10px;")
        tbl_layout = QVBoxLayout(table_card)
        tbl_layout.setContentsMargins(16, 16, 16, 16)
        lbl_tbl = QLabel("Thời khóa biểu")
        lbl_tbl.setFont(QFont("Arial", 12, QFont.Bold))
        tbl_layout.addWidget(lbl_tbl)
        lst = QListWidget()
        for itm in ["CS101—Thứ Hai 08:00", "ENG202—Thứ Ba 10:30", "HIS305—Thứ Tư 13:00", "MATH210—Thứ Năm 15:00"]:
            lst.addItem(itm)
        tbl_layout.addWidget(lst)
        grid.addWidget(table_card, 1, 0, 1, 2)

        # Thống kê học tập card
        chart_card = QFrame()
        chart_card.setStyleSheet("background-color:white; border-radius:10px;")
        ch_layout = QVBoxLayout(chart_card)
        ch_layout.setContentsMargins(16, 16, 16, 16)
        lbl_ch = QLabel("Thống kê học tập")
        lbl_ch.setFont(QFont("Arial", 12, QFont.Bold))
        ch_layout.addWidget(lbl_ch)
        chart_lbl = QLabel("[Biểu đồ]")
        chart_lbl.setAlignment(Qt.AlignCenter)
        ch_layout.addWidget(chart_lbl)
        grid.addWidget(chart_card, 1, 2)

        root.addLayout(grid)
        root.addStretch()


class GameWidget(QWidget):
    """
    Trang placeholder cho Trò chơi học tập.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Chức năng Trò chơi học tập sẽ được phát triển.")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lịch Học Thông Minh")
        self.resize(1200, 700)

        central = QWidget()
        central.setStyleSheet("background-color: #001f3f;")
        self.setCentralWidget(central)

        h = QHBoxLayout(central)

        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo = QLabel()
        logo.setPixmap(QPixmap("icons/logo1.svg").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo)

        self.sidebar = SidebarMenu(self)
        logo_layout.addWidget(self.sidebar)
        logo_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        h.addWidget(logo_container)

        self.stack = QStackedWidget()

        self.page_overview = OverviewWidget()
        self.page_courses  = CourseManagementWidget(DB_PATH)
        self.page_classes  = ClassManagementWidget(DB_PATH)
        self.page_suggest  = SuggestionPage()
        self.page_game     = GameWidget()
        self.page_study    = StudyPlanWidget()
        self.page_chat     = ChatWidget()
        self.page_chat.set_current_class('CT101')

        self.stack.addWidget(self.page_overview)  # index 0
        self.stack.addWidget(self.page_courses)   # index 1
        self.stack.addWidget(self.page_classes)   # index 2
        self.stack.addWidget(self.page_suggest)   # index 3
        self.stack.addWidget(self.page_game)      # index 4
        self.stack.addWidget(self.page_study)     # index 5
        self.stack.addWidget(self.page_chat)      # index 6

        h.addWidget(self.stack)

        self.sidebar.menuClicked.connect(self.switch_page)
        self.stack.setCurrentWidget(self.page_overview)

    def switch_page(self, key):
        if key == 'overview':
            self.stack.setCurrentWidget(self.page_overview)
        elif key == 'courses':
            self.stack.setCurrentWidget(self.page_courses)
        elif key == 'classes':
            self.stack.setCurrentWidget(self.page_classes)
        elif key == 'suggest':
            self.stack.setCurrentWidget(self.page_suggest)
        elif key == 'games':
            self.stack.setCurrentWidget(self.page_game)
        elif key == 'study':
            self.stack.setCurrentWidget(self.page_study)
        elif key == 'chat':
            self.stack.setCurrentWidget(self.page_chat)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
