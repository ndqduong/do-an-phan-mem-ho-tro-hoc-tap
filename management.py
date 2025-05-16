import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CourseManagementWidget(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db = db_path
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        # Trang quản lý môn học
        self.setStyleSheet("background-color: #f0f2f5;")
        root = QVBoxLayout(self)

        # Header breadcrumb
        hdr = QFrame()
        hdr.setStyleSheet("background-color: #0d3a66; border-radius:4px;")
        hdr_layout = QHBoxLayout(hdr)
        back = QLabel("◀")
        back.setFont(QFont("Arial", 14))
        back.setStyleSheet("color:white;")
        hdr_layout.addWidget(back)
        hdr_layout.addSpacing(8)
        bc = QLabel("Trang chủ / Quản lý môn học")
        bc.setFont(QFont("Arial", 10))
        bc.setStyleSheet("color:white;")
        hdr_layout.addWidget(bc)
        hdr_layout.addStretch()
        root.addWidget(hdr)
        root.addSpacing(12)

        # Form nhập
        form_frame = QFrame()
        form_frame.setStyleSheet("background:white; border-radius:8px;")
        form = QGridLayout(form_frame)
        form.setContentsMargins(16, 16, 16, 16)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(10)

        # Mã môn
        form.addWidget(QLabel("Mã môn"), 0, 0)
        self.edit_code = QLineEdit()
        self.edit_code.setPlaceholderText("Nhập mã môn")
        form.addWidget(self.edit_code, 1, 0)

        # Tên môn
        form.addWidget(QLabel("Tên môn"), 0, 1)
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("Nhập tên môn")
        form.addWidget(self.edit_name, 1, 1)

        # Số tín chỉ
        form.addWidget(QLabel("Số tín chỉ"), 2, 0)
        self.cb_credit = QComboBox()
        self.cb_credit.addItems([str(i) for i in range(1, 6)])
        form.addWidget(self.cb_credit, 3, 0)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.setSpacing(10)
        for text, handler, style in (
            ("Thêm", self.add_course, "background:#007bff;color:#fff;"),
            ("Cập nhật", self.update_course, "background:#007bff;color:#fff;"),
            ("Xóa", self.delete_course, "background:#ccc;color:#333;")
        ):
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            btn.setFixedHeight(32)
            btn.setStyleSheet(f"{style}border:none;padding:0 16px;border-radius:4px;")
            btn_layout.addWidget(btn)
        form.addLayout(btn_layout, 4, 0, 1, 2)

        root.addWidget(form_frame)
        root.addSpacing(12)

        # Bảng dữ liệu
        table_frame = QFrame()
        table_frame.setStyleSheet("background:white; border-radius:8px;")
        table_layout = QVBoxLayout(table_frame)
        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["Mã môn", "Tên môn", "Số tín chỉ"])  
        self.tbl.setColumnWidth(0, 150)
        self.tbl.setColumnWidth(1, 300)
        self.tbl.setColumnWidth(2, 100)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.itemClicked.connect(self._on_row)
        table_layout.addWidget(self.tbl)
        root.addWidget(table_frame)

    def _run(self, sql, args=(), commit=False):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(sql, args)
        if commit:
            conn.commit()
        rows = cur.fetchall()
        conn.close()
        return rows

    def _load_data(self):
        self.tbl.setRowCount(0)
        for ma, ten, tc in self._run("SELECT ma_mon, ten_mon, so_tin_chi FROM mon_hoc"):
            row = self.tbl.rowCount()
            self.tbl.insertRow(row)
            self.tbl.setItem(row, 0, QTableWidgetItem(str(ma)))
            self.tbl.setItem(row, 1, QTableWidgetItem(str(ten)))
            self.tbl.setItem(row, 2, QTableWidgetItem(str(tc)))

    def _on_row(self, item):
        r = item.row()
        self.edit_code.setText(self.tbl.item(r, 0).text())
        self.edit_name.setText(self.tbl.item(r, 1).text())
        self.cb_credit.setCurrentText(self.tbl.item(r, 2).text())

    def add_course(self):
        ma = self.edit_code.text().strip()
        ten = self.edit_name.text().strip()
        tc = int(self.cb_credit.currentText())
        if not ma or not ten:
            QMessageBox.warning(self, "Lỗi", "Nhập đủ thông tin.")
            return
        try:
            self._run(
                "INSERT INTO mon_hoc(ma_mon, ten_mon, so_tin_chi) VALUES(?, ?, ?)",
                (ma, ten, tc),
                commit=True
            )
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Lỗi", "Mã môn đã tồn tại.")
        self._load_data()

    def update_course(self):
        ma = self.edit_code.text().strip()
        ten = self.edit_name.text().strip()
        if not ma:
            QMessageBox.warning(self, "Lỗi", "Chọn môn để sửa.")
            return
        tc = int(self.cb_credit.currentText())
        self._run(
            "UPDATE mon_hoc SET ten_mon = ?, so_tin_chi = ? WHERE ma_mon = ?",
            (ten, tc, ma),
            commit=True
        )
        self._load_data()

    def delete_course(self):
        ma = self.edit_code.text().strip()
        if not ma:
            QMessageBox.warning(self, "Lỗi", "Chọn môn để xóa.")
            return
        self._run("DELETE FROM mon_hoc WHERE ma_mon = ?", (ma,), commit=True)
        self._load_data()
        self.edit_code.clear()
        self.edit_name.clear()

class ClassManagementWidget(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db = db_path
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        self.setStyleSheet("background-color: #f0f2f5;")
        root = QVBoxLayout(self)

        # Header breadcrumb
        hdr = QFrame()
        hdr.setStyleSheet("background-color: #0d3a66; border-radius:4px;")
        hdr_layout = QHBoxLayout(hdr)
        back = QLabel("◀")
        back.setFont(QFont("Arial", 14))
        back.setStyleSheet("color:white;")
        hdr_layout.addWidget(back)
        hdr_layout.addSpacing(8)
        bc = QLabel("Trang chủ / Quản lý lớp học")
        bc.setFont(QFont("Arial", 10))
        bc.setStyleSheet("color:white;")
        hdr_layout.addWidget(bc)
        hdr_layout.addStretch()
        root.addWidget(hdr)
        root.addSpacing(12)

        # Form nhập: Mã lớp, Mã môn, Thời gian - Phòng
        form_frame = QFrame()
        form_frame.setStyleSheet("background:white; border-radius:8px;")
        form = QGridLayout(form_frame)
        form.setContentsMargins(16, 16, 16, 16)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(10)

        form.addWidget(QLabel("Mã lớp"), 0, 0)
        self.edit_class = QLineEdit()
        self.edit_class.setPlaceholderText("Nhập mã lớp")
        form.addWidget(self.edit_class, 1, 0)

        form.addWidget(QLabel("Mã môn"), 0, 1)
        self.edit_course = QLineEdit()
        self.edit_course.setPlaceholderText("Nhập mã môn")
        form.addWidget(self.edit_course, 1, 1)

        form.addWidget(QLabel("Thời gian - Phòng"), 2, 0)
        self.edit_room = QLineEdit()
        self.edit_room.setPlaceholderText("VD: Thứ Hai 08:00 - A101")
        form.addWidget(self.edit_room, 3, 0)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.setSpacing(10)
        for text, handler, style in (
            ("Thêm", self.add_class, "background:#007bff;color:#fff;"),
            ("Cập nhật", self.update_class, "background:#007bff;color:#fff;"),
            ("Xóa", self.delete_class, "background:#ccc;color:#333;")
        ):
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            btn.setFixedHeight(32)
            btn.setStyleSheet(f"{style}border:none;padding:0 16px;border-radius:4px;")
            btn_layout.addWidget(btn)
        form.addLayout(btn_layout, 4, 0, 1, 2)

        root.addWidget(form_frame)
        root.addSpacing(12)

        # Bảng dữ liệu: Mã lớp, Mã môn, Thời gian - Phòng
        table_frame = QFrame()
        table_frame.setStyleSheet("background:white; border-radius:8px;")
        table_layout = QVBoxLayout(table_frame)
        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["Mã lớp", "Mã môn", "Thời gian - Phòng"])  
        self.tbl.setColumnWidth(0, 150)
        self.tbl.setColumnWidth(1, 150)
        self.tbl.setColumnWidth(2, 300)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.itemClicked.connect(self._on_row)
        table_layout.addWidget(self.tbl)
        root.addWidget(table_frame)

    def _run(self, sql, args=(), commit=False):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(sql, args)
        if commit:
            conn.commit()
        rows = cur.fetchall()
        conn.close()
        return rows

    def _load_data(self):
        self.tbl.setRowCount(0)
        for lop, ma, tg in self._run("SELECT ma_lop, ma_mon, thoi_gian FROM lop_hoc"):
            row = self.tbl.rowCount()
            self.tbl.insertRow(row)
            self.tbl.setItem(row, 0, QTableWidgetItem(str(lop)))
            self.tbl.setItem(row, 1, QTableWidgetItem(str(ma)))
            self.tbl.setItem(row, 2, QTableWidgetItem(str(tg)))

    def _on_row(self, item):
        r = item.row()
        self.edit_class.setText(self.tbl.item(r, 0).text())
        self.edit_course.setText(self.tbl.item(r, 1).text())
        self.edit_room.setText(self.tbl.item(r, 2).text())

    def add_class(self):
        lop = self.edit_class.text().strip()
        ma = self.edit_course.text().strip()
        tg = self.edit_room.text().strip()
        if not lop or not ma or not tg:
            QMessageBox.warning(self, "Lỗi", "Nhập đủ thông tin.")
            return
        self._run(
            "INSERT INTO lop_hoc(ma_lop, ma_mon, thoi_gian) VALUES(?, ?, ?)",
            (lop, ma, tg),
            commit=True
        )
        self._load_data()

    def update_class(self):
        current_row = self.tbl.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Lỗi", "Chọn lớp để sửa.")
            return
        lop = self.edit_class.text().strip()
        ma = self.edit_course.text().strip()
        tg = self.edit_room.text().strip()
        self._run(
            "UPDATE lop_hoc SET ma_lop = ?, ma_mon = ?, thoi_gian = ? WHERE ma_lop = ?",
            (lop, ma, tg, lop),
            commit=True
        )
        self._load_data()

    def delete_class(self):
        current_row = self.tbl.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Lỗi", "Chọn lớp để xóa.")
            return
        lop = self.tbl.item(current_row, 0).text()
        self._run("DELETE FROM lop_hoc WHERE ma_lop = ?", (lop,), commit=True)
        self._load_data()
        self.edit_class.clear()
        self.edit_course.clear()
        self.edit_room.clear()
