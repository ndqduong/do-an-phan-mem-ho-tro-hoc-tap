import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QTextEdit, QCalendarWidget, QListWidget, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CourseManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Quản lý môn học")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        # Table
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["Mã môn", "Tên môn", "Số tín chỉ"])
        layout.addWidget(table)
        # Controls
        btn_add = QPushButton("Thêm môn mới")
        layout.addWidget(btn_add)
        layout.addStretch()

class ClassManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Quản lý lớp học")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Mã lớp", "Môn", "Giáo viên", "Thời gian"])
        layout.addWidget(table)
        btn_add = QPushButton("Thêm lớp mới")
        layout.addWidget(btn_add)
        layout.addStretch()

class TimetableSuggestionPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Gợi ý Thời khóa biểu")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        cal = QCalendarWidget()
        layout.addWidget(cal)
        btn_gen = QPushButton("Tạo gợi ý mới")
        layout.addWidget(btn_gen)
        layout.addStretch()

class StudyPlanPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Lập kế hoạch ôn tập")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        text = QTextEdit()
        text.setPlaceholderText("Nhập nội dung kế hoạch ôn tập...")
        layout.addWidget(text)
        btn_save = QPushButton("Lưu kế hoạch")
        layout.addWidget(btn_save)
        layout.addStretch()

class GamePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Trò chơi học tập")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        # Placeholder for game
        placeholder = QLabel("[Giao diện trò chơi sẽ hiển thị ở đây]")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        layout.addStretch()

class ReminderPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Nhắc nhở")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        list_widget = QListWidget()
        layout.addWidget(list_widget)
        btn_add = QPushButton("Thêm nhắc nhở")
        layout.addWidget(btn_add)
        layout.addStretch()

class ChatPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Chat nhóm")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        chat_history = QTextEdit()
        chat_history.setReadOnly(True)
        layout.addWidget(chat_history)
        input_line = QLineEdit()
        input_line.setPlaceholderText("Nhập tin nhắn...")
        layout.addWidget(input_line)
        btn_send = QPushButton("Gửi")
        layout.addWidget(btn_send)
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng dụng Lịch Học Thông Minh")
        self.resize(1200, 700)

        # Sidebar buttons
        sidebar = QWidget()
        side_layout = QVBoxLayout(sidebar)
        buttons = [
            ("Quản lý môn học", CourseManagementPage),
            ("Quản lý lớp học", ClassManagementPage),
            ("Gợi ý TKB", TimetableSuggestionPage),
            ("Lập kế hoạch ôn tập", StudyPlanPage),
            ("Trò chơi học tập", GamePage),
            ("Nhắc nhở", ReminderPage),
            ("Chat nhóm", ChatPage)
        ]
        self.stack = QStackedWidget()
        for idx, (name, page_cls) in enumerate(buttons):
            btn = QPushButton(name)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, i=idx: self.stack.setCurrentIndex(i))
            side_layout.addWidget(btn)
            # Add page
            self.stack.addWidget(page_cls())
        side_layout.addStretch()
        sidebar.setFixedWidth(200)

        # Main layout
        main = QWidget()
        main_layout = QHBoxLayout(main)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        self.setCentralWidget(main)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
