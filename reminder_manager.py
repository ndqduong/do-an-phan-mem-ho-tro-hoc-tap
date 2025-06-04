import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDateEdit, QTimeEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QSizePolicy, QComboBox, QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer

DB_PATH = 'reminders.db'
# DB chứa thời khoá biểu đã lưu
SCHEDULE_DB = 'lichhoc.db'

# Thời gian bắt đầu tương ứng của từng tiết (ước lượng)
SLOT_START_TIMES = {
    1: '07:00',
    2: '07:50',
    3: '08:40',
    4: '09:30',
    5: '10:20',
    6: '11:10',
    7: '13:00',
    8: '13:50',
    9: '14:40',
    10: '15:30',
    11: '16:20',
    12: '17:10',
    13: '18:00',
    14: '18:50',
    15: '19:40',
    16: '20:30'
}

# Số phút nhắc trước tiết đầu tiên mỗi ngày
FIRST_CLASS_ADVANCE = 15

class ReminderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nhắc Nhở Học Tập")
        self.resize(600, 400)
        self._init_db()
        self._init_ui()
        self._load_reminders()
        self._load_tt_alerts()
        self.last_first_date = ""
        # Timer kiểm tra nhắc mỗi phút
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer)
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
        c.execute('''
            CREATE TABLE IF NOT EXISTS timetable_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thu INTEGER NOT NULL,
                slot INTEGER NOT NULL,
                advance INTEGER NOT NULL DEFAULT 15,
                last_date TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _init_ui(self):
        self.setStyleSheet(
            """
            QWidget { background-color:#001f3f; color:white; }
            QLineEdit, QDateEdit, QTimeEdit, QComboBox, QSpinBox {
                background-color:#224870; color:white;
                border:1px solid #335; border-radius:4px; padding:2px 4px;
            }
            QPushButton { background-color:#3B82F6; color:white; border:none; padding:4px 12px; border-radius:6px; }
            QPushButton:hover { background-color:#1E40AF; }
            QTableWidget { background-color:#0d3a66; }
            QHeaderView::section { background-color:#224870; color:white; border:none; padding:4px; }
            QGroupBox { border:1px solid #335; border-radius:6px; margin-top:8px; }
            QGroupBox::title { subcontrol-origin: margin; left:10px; top:-7px; font-weight:bold; }
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        # --- Panel nhập liệu ---␊
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

        group_rem = QGroupBox("Nhắc nhở cá nhân")
        rem_layout = QVBoxLayout(group_rem)
        rem_layout.addLayout(form_layout)

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
        self.table.setColumnHidden(0, True)

        rem_layout.addWidget(self.table)

        # --- Nút Xóa ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_delete = QPushButton("Xóa nhắc")
        btn_delete.clicked.connect(self._delete_selected)
        btn_layout.addWidget(btn_delete)
        rem_layout.addLayout(btn_layout)

        main_layout.addWidget(group_rem)

        # --- Thiết lập thông báo thời khoá biểu ---
        tt_form = QHBoxLayout()
        tt_form.setSpacing(8)

        lbl_day = QLabel("Thứ:")
        self.combo_day = QComboBox()
        self.combo_day.addItems(["2", "3", "4", "5", "6", "7", "CN"])

        lbl_slot = QLabel("Tiết:")
        self.spin_slot = QSpinBox()
        self.spin_slot.setRange(1, 16)

        lbl_adv = QLabel("Báo trước:")
        self.spin_adv = QSpinBox()
        self.spin_adv.setRange(1, 120)
        self.spin_adv.setValue(15)

        btn_add_tt = QPushButton("Thêm TKB")
        btn_add_tt.clicked.connect(self._add_tt_alert)

        tt_form.addWidget(lbl_day)
        tt_form.addWidget(self.combo_day)
        tt_form.addWidget(lbl_slot)
        tt_form.addWidget(self.spin_slot)
        tt_form.addWidget(lbl_adv)
        tt_form.addWidget(self.spin_adv)
        tt_form.addWidget(QLabel("phút"))
        tt_form.addWidget(btn_add_tt)
        tt_form.addStretch()

        group_tt = QGroupBox("Thông báo TKB")
        tt_layout = QVBoxLayout(group_tt)
        tt_layout.addLayout(tt_form)

        self.table_tt = QTableWidget(0, 4)
        self.table_tt.setHorizontalHeaderLabels(["ID", "Thứ", "Tiết", "Báo trước"])
        for i in range(4):
            self.table_tt.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents if i != 0 else QHeaderView.ResizeToContents)
        self.table_tt.setSelectionBehavior(self.table_tt.SelectRows)
        self.table_tt.setEditTriggers(self.table_tt.NoEditTriggers)
        self.table_tt.setColumnHidden(0, True)
        tt_layout.addWidget(self.table_tt)

        btn_tt_layout = QHBoxLayout()
        btn_tt_layout.addStretch()
        btn_del_tt = QPushButton("Xóa TKB")
        btn_del_tt.clicked.connect(self._delete_tt_selected)
        btn_tt_layout.addWidget(btn_del_tt)
        tt_layout.addLayout(btn_tt_layout)

        main_layout.addWidget(group_tt)
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

    # ----- Các hàm quản lý thông báo TKB -----

    def _load_tt_alerts(self):
        self.table_tt.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, thu, slot, advance FROM timetable_alerts ORDER BY thu, slot")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            self._append_tt_row(row)

    def _append_tt_row(self, row):
        row_idx = self.table_tt.rowCount()
        self.table_tt.insertRow(row_idx)
        for col, val in enumerate(row):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignCenter)
            self.table_tt.setItem(row_idx, col, item)

    def _add_tt_alert(self):
        thu = self.combo_day.currentIndex() + 2
        slot = self.spin_slot.value()
        adv = self.spin_adv.value()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO timetable_alerts(thu, slot, advance) VALUES (?,?,?)", (thu, slot, adv))
        conn.commit()
        new_id = c.lastrowid
        conn.close()
        self._append_tt_row((new_id, thu, slot, adv))

    def _delete_tt_selected(self):
        selected = self.table_tt.selectionModel().selectedRows()
        if not selected:
            return
        reply = QMessageBox.question(
            self, "Xác nhận", "Xóa thông báo TKB đã chọn?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for idx in sorted(selected, key=lambda x: x.row(), reverse=True):
            rid = int(self.table_tt.item(idx.row(), 0).text())
            c.execute("DELETE FROM timetable_alerts WHERE id=?", (rid,))
            self.table_tt.removeRow(idx.row())
        conn.commit()
        conn.close()

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

    def _on_timer(self):
        """Hàm timer gọi mỗi phút."""
        self._check_first_class()
        self._check_reminders()
        self._check_tt_alerts()

    def _check_first_class(self):
        """Nhắc nhở 15 phút trước tiết đầu của ngày."""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        if self.last_first_date == today:
            return

        day_num = now.isoweekday() + 1
        conn = sqlite3.connect(SCHEDULE_DB)
        cur = conn.cursor()
        cur.execute("SELECT batch_name FROM saved_tkb ORDER BY saved_at DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            conn.close()
            return
        batch = row[0]
        cur.execute(
            "SELECT tiet_bat_dau, ma_mon, ma_lop, phong FROM saved_tkb "
            "WHERE batch_name=? AND thu=? ORDER BY tiet_bat_dau LIMIT 1",
            (batch, day_num),
        )
        info = cur.fetchone()
        conn.close()
        if not info:
            return
        slot, mon, lop, room = info
        start_str = SLOT_START_TIMES.get(slot)
        if not start_str:
            return
        start_dt = datetime.combine(now.date(), datetime.strptime(start_str, "%H:%M").time())
        remind_dt = start_dt - timedelta(minutes=FIRST_CLASS_ADVANCE)
        if now.strftime("%Y-%m-%d %H:%M") == remind_dt.strftime("%Y-%m-%d %H:%M"):
            msg = f"Sắp đến tiết {slot}: {mon} ({lop}) phòng {room} lúc {start_str}"
            QMessageBox.information(self, "Nhắc TKB", msg)
            self.last_first_date = today

    def _check_tt_alerts(self):
        """Kiểm tra các thông báo TKB do người dùng thiết lập."""
        now = datetime.now()
        day_num = now.isoweekday() + 1

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, slot, advance, last_date FROM timetable_alerts WHERE thu=?", (day_num,))
        alerts = c.fetchall()
        conn.close()
        if not alerts:
            return

        sconn = sqlite3.connect(SCHEDULE_DB)
        cur = sconn.cursor()
        cur.execute("SELECT batch_name FROM saved_tkb ORDER BY saved_at DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            sconn.close()
            return
        batch = row[0]

        for rid, slot, adv, last_date in alerts:
            cur.execute(
                "SELECT ma_mon, ma_lop, phong FROM saved_tkb WHERE batch_name=? AND thu=? AND tiet_bat_dau=? LIMIT 1",
                (batch, day_num, slot),
            )
            info = cur.fetchone()
            if not info:
                continue
            mon, lop, room = info
            start_str = SLOT_START_TIMES.get(slot)
            if not start_str:
                continue
            start_dt = datetime.combine(now.date(), datetime.strptime(start_str, "%H:%M").time())
            remind_dt = start_dt - timedelta(minutes=adv)
            if now.strftime("%Y-%m-%d %H:%M") == remind_dt.strftime("%Y-%m-%d %H:%M") and last_date != now.strftime("%Y-%m-%d"):
                msg = f"Sắp đến tiết {slot}: {mon} ({lop}) phòng {room} lúc {start_str}"
                QMessageBox.information(self, "Nhắc TKB", msg)
                uconn = sqlite3.connect(DB_PATH)
                uc = uconn.cursor()
                uc.execute("UPDATE timetable_alerts SET last_date=? WHERE id=?", (now.strftime("%Y-%m-%d"), rid))
                uconn.commit()
                uconn.close()

        sconn.close()

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
