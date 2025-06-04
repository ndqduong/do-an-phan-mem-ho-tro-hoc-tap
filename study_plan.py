import sys
import sqlite3
from datetime import timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QScrollArea, QListWidget, QListWidgetItem, QCheckBox,
    QComboBox, QMessageBox, QFrame,
    QVBoxLayout, QHBoxLayout, QDateEdit, QSpinBox, QHeaderView
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QDate

DB_PATH = 'lichhoc.db'


class StudyPlanWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.available_courses = []
        self.selected_courses = []
        self.available_batches = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Title bar
        title_bar = QFrame()
        title_bar.setStyleSheet("background-color: #0d3a66; padding: 16px;")
        tb = QHBoxLayout(title_bar)
        lbl = QLabel("Lập Kế Hoạch Ôn Tập")
        lbl.setFont(QFont('Segoe UI', 20, QFont.Bold))
        lbl.setStyleSheet("color: white;")
        tb.addWidget(lbl)
        root.addWidget(title_bar)

        # Content area
        content = QFrame()
        content.setStyleSheet(
            "background-color: #f3f4f6; border-bottom-left-radius:10px; border-bottom-right-radius:10px;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(20)

        # Panel Batch: chọn lịch đã lưu
        p0 = QFrame()
        p0.setStyleSheet("background:white; border-radius:5px;")
        l0 = QHBoxLayout(p0)
        l0.setContentsMargins(16, 16, 16, 16)
        lbl0 = QLabel("Chọn lịch đã lưu:")
        lbl0.setFont(QFont('Segoe UI', 12, QFont.Bold))
        l0.addWidget(lbl0)
        self.combo_batch = QComboBox()
        l0.addWidget(self.combo_batch)
        btn_refresh = QPushButton("Tải lại")
        btn_refresh.clicked.connect(self._load_batches)
        l0.addWidget(btn_refresh)
        cl.addWidget(p0)

        # Panel 1: choose courses to study
        p1 = QFrame()
        p1.setStyleSheet("background:white; border-radius:5px;")
        l1 = QVBoxLayout(p1)
        l1.setContentsMargins(16, 16, 16, 16)
        lbl1 = QLabel("Chọn môn ôn tập:")
        lbl1.setFont(QFont('Segoe UI', 12, QFont.Bold))
        l1.addWidget(lbl1)
        self.lst_courses = QListWidget()
        self.lst_courses.setFixedHeight(200)
        self._load_courses()
        l1.addWidget(self.lst_courses)
        cl.addWidget(p1)

        # Panel 2: date range and hours per day
        p2 = QFrame()
        p2.setStyleSheet("background:white; border-radius:8px;")
        h2 = QHBoxLayout(p2)
        h2.setContentsMargins(16, 16, 16, 16)
        h2.setSpacing(20)
        # Start date
        h2.addWidget(QLabel("Từ ngày:"))
        self.dt_start = QDateEdit(QDate.currentDate())
        self.dt_start.setCalendarPopup(True)
        h2.addWidget(self.dt_start)
        # End date
        h2.addWidget(QLabel("Đến ngày:"))
        self.dt_end = QDateEdit(QDate.currentDate().addDays(30))
        self.dt_end.setCalendarPopup(True)
        h2.addWidget(self.dt_end)
        # Hours per day
        h2.addWidget(QLabel("Tiết ôn/ngày:"))
        self.spin = QSpinBox()
        self.spin.setRange(1, 16)
        self.spin.setValue(2)
        h2.addWidget(self.spin)
        # Spacer + button
        h2.addStretch()
        btn = QPushButton("Tạo kế hoạch")
        btn.setStyleSheet(
            "background:#3B82F6; color:white; padding:8px 24px; border:none; border-radius:5px;")
        btn.clicked.connect(self._generate_plan)
        h2.addWidget(btn)
        cl.addWidget(p2)

        # Panel 3: result table
        p3 = QFrame()
        p3.setStyleSheet("background:white; border-radius:8px;")
        v3 = QVBoxLayout(p3)
        v3.setContentsMargins(16, 16, 16, 16)
        v3.setSpacing(8)
        lbl3 = QLabel("Kế hoạch ôn tập:")
        lbl3.setFont(QFont('Segoe UI', 12, QFont.Bold))
        v3.addWidget(lbl3)
        self.tbl = QTableWidget()
        self.tbl.setColumnCount(3)
        self.tbl.setHorizontalHeaderLabels(['Ngày', 'Tiết', 'Môn ôn'])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        v3.addWidget(self.tbl)
        cl.addWidget(p3)

        root.addWidget(content)

        # Loại cải tiến bổ sung: gợi ý môn ưu tiên
        # Panel 4: chọn mức độ ưu tiên cho từng môn
        p4 = QFrame()
        p4.setStyleSheet("background:white; border-radius:5px;")
        l4 = QHBoxLayout(p4)
        l4.setContentsMargins(16, 16, 16, 16)
        lbl4 = QLabel("Ưu tiên ôn trước:")
        lbl4.setFont(QFont('Segoe UI', 12))
        l4.addWidget(lbl4)
        self.cb_priority = QComboBox()
        self.cb_priority.addItems(["Không", "Tăng cường môn cũ", "Tập trung môn bài mới"])
        l4.addWidget(self.cb_priority)
        cl.addWidget(p4)

    def _run(self, sql, args=()):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql, args)
        rows = cur.fetchall()
        conn.close()
        return rows

    def _exec(self, sql, args=()):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql, args)
        conn.commit()
        conn.close()

    def _load_batches(self):
        """
        Tải tên các batch_name từ saved_tkb lên combo_batch.
        """
        self.combo_batch.clear()
        rows = self._run("SELECT DISTINCT batch_name, saved_at FROM saved_tkb ORDER BY saved_at DESC")
        for batch, saved_at in rows:
            self.combo_batch.addItem(f"{batch} (lưu: {saved_at})", batch)
        # Nếu có batch, chọn batch đầu tiên
        if self.combo_batch.count() > 0:
            self.combo_batch.setCurrentIndex(0)

    def _load_courses(self):
        """
        Lấy danh sách môn từ mon_hoc, hiển thị trong lst_courses.
        """
        self.lst_courses.clear()
        rows = self._run('SELECT ma_mon, ten_mon FROM mon_hoc ORDER BY ma_mon')
        for ma, ten in rows:
            item = QListWidgetItem(f"{ma} - {ten}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lst_courses.addItem(item)

    def _generate_plan(self):
        """
        Xây dựng kế hoạch ôn tập dựa vào:
          - Môn đã chọn
          - Khoảng ngày
          - Tiết/ngày
          - Buổi trống trong lịch đã lưu
          - Mức độ ưu tiên (tùy chọn)
        """
        # 1. Lấy batch đã chọn
        idx_batch = self.combo_batch.currentIndex()
        if idx_batch < 0:
            QMessageBox.warning(self, 'Thiếu lịch', 'Vui lòng chọn một lịch đã lưu!')
            return
        batch = self.combo_batch.itemData(idx_batch)

        # 2. Lấy danh sách môn user chọn
        courses = []
        for i in range(self.lst_courses.count()):
            item = self.lst_courses.item(i)
            if item.checkState() == Qt.Checked:
                courses.append(item.text().split(' - ')[0])  # lưu ma_mon
        if not courses:
            QMessageBox.warning(self, 'Thiếu môn', 'Chọn ít nhất 1 môn để ôn tập!')
            return

        # 3. Lấy ngày bắt đầu và kết thúc, kiểm tra hợp lệ
        start = self.dt_start.date().toPyDate()
        end = self.dt_end.date().toPyDate()
        if end < start:
            QMessageBox.warning(self, 'Sai ngày', 'Ngày kết thúc phải sau ngày bắt đầu!')
            return

        # 4. Số tiết/ngày
        daily = self.spin.value()

        # 5. Lấy dữ liệu lịch đã lưu của batch: chỉ cần thu, tiet_bat_dau, so_tiet
        all_sched = self._run("""
            SELECT ma_lop, ma_mon, thu, tiet_bat_dau, so_tiet
            FROM saved_tkb
            WHERE batch_name = ?
        """, (batch,))
        # Chuyển thành dict: key = (thu), value = list of occupied slots
        occupied = {d: set() for d in range(2, 9)}
        for ma_lop, ma_mon, thu, tiet_bd, so_tiet in all_sched:
            for sl in range(tiet_bd, tiet_bd + so_tiet):
                occupied[thu].add(sl)

        # 6. Phân loại môn theo ưu tiên (nếu cần)
        priority_mode = self.cb_priority.currentIndex()
        # priority_mode: 0=Không, 1=Tăng cường môn cũ (ồn lại môn đã có trong lịch),
        # 2=Tập trung môn bài mới (ồn môn chưa học)
        # Lấy môn đã xuất hiện trong all_sched
        studied_mons = set([ma_mon for _, ma_mon, _, _, _ in all_sched])
        prioritized = []
        non_prioritized = []
        if priority_mode == 1:
            # Đưa các môn đã học (studied_mons) lên trước
            for mon in courses:
                if mon in studied_mons:
                    prioritized.append(mon)
                else:
                    non_prioritized.append(mon)
        elif priority_mode == 2:
            # Đưa các môn chưa học lên trước
            for mon in courses:
                if mon not in studied_mons:
                    prioritized.append(mon)
                else:
                    non_prioritized.append(mon)
        else:
            prioritized = courses[:]
        course_order = prioritized + non_prioritized

        # 7. Tạo kế hoạch ôn tập: vòng qua từng ngày, từng tiết nhưng chỉ ôn ở những slot chưa có lớp
        self.tbl.setRowCount(0)
        row = 0
        date = start
        course_index = 0
        while date <= end:
            # Xác định thu của ngày: isoweekday() returns 1=Mon..7=Sun, 
            # nhưng trong DB dùng 2=Mon..8=Sun => thu = isoweekday()+1
            thu = date.isoweekday() + 1

            # Xác định các slot trống trong ngày: slot từ 1..k thỏa tiêu chí daily, nhưng chỉ nếu slot not in occupied[thu]
            free_slots = []
            for sl in range(1, 17):  # giả sử max 16 tiết
                if sl not in occupied.get(thu, set()):
                    free_slots.append(sl)
            # Lấy tối đa 'daily' slot đầu tiên từ free_slots
            available_slots = free_slots[:daily]

            # Nếu không có đủ free slot, bỏ qua ngày đó
            for sl in available_slots:
                self.tbl.insertRow(row)
                self.tbl.setItem(row, 0, QTableWidgetItem(date.strftime('%Y-%m-%d')))
                self.tbl.setItem(row, 1, QTableWidgetItem(f"Tiết {sl}"))
                # Gán môn theo Round-robin trên course_order
                mon = course_order[course_index % len(course_order)]
                self.tbl.setItem(row, 2, QTableWidgetItem(mon))
                row += 1
                course_index += 1

            date += timedelta(days=1)

        # Nếu bảng vẫn trống, báo không tìm được slot
        if self.tbl.rowCount() == 0:
            QMessageBox.information(self, "Không có buổi trống", "Không tìm thấy buổi trống nào trong khoảng ngày đã chọn.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Lập Kế Hoạch Ôn Tập')
        self.resize(800, 600)
        self.setCentralWidget(StudyPlanWidget())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
