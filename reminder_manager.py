import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDateEdit, QTimeEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer

DB_PATH = 'reminders.db'

class ReminderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nhắc Nhở Học Tập")
        self.resize(600, 400)
        self._init_db()
        self._init_ui()
        self._load_reminders()
        # Timer kiểm tra nhắc mỗi phút
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_reminders)
        self.timer.start(60 * 1000)  # 60 giây

    def _init_db(self):
        # Tạo table nếu chưa có
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Panel nhập liệu ---
        form_layout = QHBoxLayout()
        form_layout.setSpacing(8)

        # Nhập nội dung nhắc nhở
        lbl_msg = QLabel("Nội dung:")
        lbl_msg.setFixedWidth(60)
        self.edit_msg = QLineEdit()
        self.edit_msg.setPlaceholderText("Nhập nội dung cần nhắc...")
        self.edit_msg.setMinimumWidth(200)

        # Chọn ngày, giờ
        lbl_date = QLabel("Ngày:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        lbl_time = QLabel("Giờ:")
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")

        # Nút Thêm
        btn_add = QPushButton("Thêm")
        btn_add.clicked.connect(self._add_reminder)

        form_layout.addWidget(lbl_msg)
        form_layout.addWidget(self.edit_msg)
        form_layout.addWidget(lbl_date)
        form_layout.addWidget(self.date_edit)
        form_layout.addWidget(lbl_time)
        form_layout.addWidget(self.time_edit)
        form_layout.addWidget(btn_add)

        main_layout.addLayout(form_layout)

        # --- Bảng hiển thị nhắc nhở ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nội dung", "Ngày", "Giờ"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(self.table)

        # --- Nút Xóa ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_delete = QPushButton("Xóa nhắc")
        btn_delete.clicked.connect(self._delete_selected)
        btn_layout.addWidget(btn_delete)
        main_layout.addLayout(btn_layout)

    def _load_reminders(self):
        """Tải toàn bộ reminder từ DB và hiển thị vào table."""
        self.table.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, message, date, time FROM reminders ORDER BY date, time")
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self._append_row_to_table(row)

    def _append_row_to_table(self, row):
        """Thêm 1 hàng row = (id, message, date, time) vào QTableWidget."""
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        for col, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            if col == 0:
                # Ẩn cột ID sau khi load
                item.setTextAlignment(Qt.AlignCenter)
            elif col in (2, 3):
                item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, col, item)

    def _add_reminder(self):
        """Thêm reminder mới vào DB và table."""
        msg = self.edit_msg.text().strip()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        time = self.time_edit.time().toString("HH:mm")

        if not msg:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập nội dung nhắc nhở.")
            return

        # Lưu vào DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO reminders(message,date,time) VALUES (?,?,?)", (msg, date, time))
        conn.commit()
        new_id = c.lastrowid
        conn.close()

        # Thêm vào table ngay lập tức
        self._append_row_to_table((new_id, msg, date, time))

        # Clear ô nhập
        self.edit_msg.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())

    def _delete_selected(self):
        """Xóa các dòng đang được chọn trong table và DB."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        # Xác nhận xóa
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa nhắc nhở đã chọn?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Xóa mỗi hàng
        for idx in sorted(selected, key=lambda x: x.row(), reverse=True):
            row = idx.row()
            id_item = self.table.item(row, 0)
            if id_item:
                rid = int(id_item.text())
                c.execute("DELETE FROM reminders WHERE id=?", (rid,))
            self.table.removeRow(row)
        conn.commit()
        conn.close()

    def _check_reminders(self):
        """Hàm được gọi mỗi phút để kiểm tra nhắc nhở đến giờ."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, message FROM reminders WHERE date || ' ' || time = ?", (now,))
        matches = c.fetchall()
        conn.close()

        for rid, msg in matches:
            # Hiện thông báo nhắc
            QMessageBox.information(self, "Nhắc nhở", f"🔔 {msg}")
            # Sau khi đã nhắc, xóa khỏi DB và table
            self._remove_reminder(rid)

    def _remove_reminder(self, rid):
        """Xóa reminder có id=rid khỏi DB và table, dùng khi đã nhắc."""
        # Xóa khỏi DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM reminders WHERE id=?", (rid,))
        conn.commit()
        conn.close()
        # Xóa khỏi table
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            if id_item and int(id_item.text()) == rid:
                self.table.removeRow(row)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ReminderWindow()
    win.show()
    sys.exit(app.exec_())
