import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

DB_PATH = r"C:\study plan\lichhoc.db"


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

        form_frame = QFrame()
        form_frame.setStyleSheet("background:white; border-radius:8px;")
        form = QGridLayout(form_frame)
        form.setContentsMargins(16, 16, 16, 16)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(10)

        form.addWidget(QLabel("Mã môn"), 0, 0)
        self.edit_course_code = QLineEdit()
        self.edit_course_code.setPlaceholderText("Nhập mã môn")
        form.addWidget(self.edit_course_code, 1, 0)

        form.addWidget(QLabel("Tên môn"), 0, 1)
        self.edit_course_name = QLineEdit()
        self.edit_course_name.setPlaceholderText("Nhập tên môn")
        form.addWidget(self.edit_course_name, 1, 1)

        form.addWidget(QLabel("Số tín chỉ"), 2, 0)
        self.cb_credit = QComboBox()
        self.cb_credit.addItems([str(i) for i in range(1, 6)])
        form.addWidget(self.cb_credit, 3, 0)

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

        table_frame = QFrame()
        table_frame.setStyleSheet("background:white; border-radius:8px;")
        table_layout = QVBoxLayout(table_frame)
        self.tbl_course = QTableWidget(0, 3)
        self.tbl_course.setHorizontalHeaderLabels(["Mã môn", "Tên môn", "Số tín chỉ"])
        self.tbl_course.setColumnWidth(0, 150)
        self.tbl_course.setColumnWidth(1, 300)
        self.tbl_course.setColumnWidth(2, 100)
        self.tbl_course.horizontalHeader().setStretchLastSection(True)
        self.tbl_course.itemClicked.connect(self._on_row_course)
        table_layout.addWidget(self.tbl_course)
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
        self.tbl_course.setRowCount(0)
        for code, name, credit in self._run("SELECT ma_mon, ten_mon, so_tin_chi FROM mon_hoc ORDER BY ma_mon"):
            row = self.tbl_course.rowCount()
            self.tbl_course.insertRow(row)
            self.tbl_course.setItem(row, 0, QTableWidgetItem(code))
            self.tbl_course.setItem(row, 1, QTableWidgetItem(name))
            self.tbl_course.setItem(row, 2, QTableWidgetItem(str(credit)))

    def _on_row_course(self, item):
        r = item.row()
        self.edit_course_code.setText(self.tbl_course.item(r, 0).text())
        self.edit_course_name.setText(self.tbl_course.item(r, 1).text())
        self.cb_credit.setCurrentText(self.tbl_course.item(r, 2).text())

    def add_course(self):
        code = self.edit_course_code.text().strip()
        name = self.edit_course_name.text().strip()
        credit = self.cb_credit.currentText()
        if not code or not name:
            QMessageBox.warning(self, "Lỗi", "Nhập đủ thông tin.")
            return

        # Kiểm tra xem mã môn đã tồn tại chưa
        exists = self._run("SELECT COUNT(*) FROM mon_hoc WHERE ma_mon = ?", (code,))[0][0]
        if exists:
            QMessageBox.warning(self, "Lỗi", f"Mã môn '{code}' đã tồn tại.")
            return

        self._run(
            "INSERT INTO mon_hoc(ma_mon, ten_mon, so_tin_chi) VALUES(?, ?, ?)",
            (code, name, credit),
            commit=True
        )
        self._load_data()
        self.edit_course_code.clear()
        self.edit_course_name.clear()
        self.cb_credit.setCurrentIndex(0)

    def update_course(self):
        current_row = self.tbl_course.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Lỗi", "Chọn môn để sửa.")
            return

        code = self.edit_course_code.text().strip()
        name = self.edit_course_name.text().strip()
        credit = self.cb_credit.currentText()
        if not code or not name:
            QMessageBox.warning(self, "Lỗi", "Nhập đủ thông tin.")
            return

        # Cập nhật theo mã môn
        self._run(
            "UPDATE mon_hoc SET ten_mon = ?, so_tin_chi = ? WHERE ma_mon = ?",
            (name, credit, code),
            commit=True
        )
        self._load_data()

    def delete_course(self):
        current_row = self.tbl_course.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Lỗi", "Chọn môn để xóa.")
            return

        code = self.tbl_course.item(current_row, 0).text()
        # Xóa các lớp, lịch học liên quan đến môn này (nếu có)
        self._run("DELETE FROM lich_hoc WHERE ma_lop IN (SELECT ma_lop FROM lop_hoc WHERE ma_mon = ?)", (code,), commit=True)
        self._run("DELETE FROM lop_hoc WHERE ma_mon = ?", (code,), commit=True)
        self._run("DELETE FROM mon_hoc WHERE ma_mon = ?", (code,), commit=True)

        self._load_data()
        self.edit_course_code.clear()
        self.edit_course_name.clear()
        self.cb_credit.setCurrentIndex(0)



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

        # Form nhập: Mã lớp, Mã môn, Thứ, Tiết bắt đầu, Số tiết, Phòng
        form_frame = QFrame()
        form_frame.setStyleSheet("background:white; border-radius:8px;")
        form = QGridLayout(form_frame)
        form.setContentsMargins(16, 16, 16, 16)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(10)

        # Mã lớp
        form.addWidget(QLabel("Mã lớp"), 0, 0)
        self.edit_class = QLineEdit()
        self.edit_class.setPlaceholderText("Nhập mã lớp")
        form.addWidget(self.edit_class, 1, 0)

        # Mã môn (dùng ComboBox để chọn từ các môn có sẵn)
        form.addWidget(QLabel("Mã môn"), 0, 1)
        self.combo_course = QComboBox()
        form.addWidget(self.combo_course, 1, 1)

        # Thứ (2=Thứ Hai ... 8=Chủ Nhật)
        form.addWidget(QLabel("Thứ"), 2, 0)
        self.spin_day = QSpinBox()
        self.spin_day.setRange(2, 8)
        self.spin_day.setSuffix(" (2=Thứ 2 ... 8=Chủ Nhật)")
        form.addWidget(self.spin_day, 3, 0)

        # Tiết bắt đầu
        form.addWidget(QLabel("Tiết bắt đầu"), 2, 1)
        self.spin_start = QSpinBox()
        self.spin_start.setRange(1, 10)
        form.addWidget(self.spin_start, 3, 1)

        # Số tiết
        form.addWidget(QLabel("Số tiết"), 4, 0)
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 10)
        form.addWidget(self.spin_count, 5, 0)

        # Phòng
        form.addWidget(QLabel("Phòng"), 4, 1)
        self.edit_room = QLineEdit()
        self.edit_room.setPlaceholderText("VD: A8-601")
        form.addWidget(self.edit_room, 5, 1)

        # Nút hành động
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
        form.addLayout(btn_layout, 6, 0, 1, 2)

        root.addWidget(form_frame)
        root.addSpacing(12)

        # Bảng dữ liệu: id, Mã lớp, Mã môn, Thứ, Tiết bắt đầu, Số tiết, Phòng
        table_frame = QFrame()
        table_frame.setStyleSheet("background:white; border-radius:8px;")
        table_layout = QVBoxLayout(table_frame)
        self.tbl = QTableWidget(0, 7)
        self.tbl.setHorizontalHeaderLabels([
            "ID", "Mã lớp", "Mã môn", "Thứ", "Tiết bắt đầu", "Số tiết", "Phòng"
        ])
        # Ẩn cột ID (dùng nội bộ để chọn update/delete)
        self.tbl.setColumnHidden(0, True)
        self.tbl.setColumnWidth(1, 100)
        self.tbl.setColumnWidth(2, 100)
        self.tbl.setColumnWidth(3, 50)
        self.tbl.setColumnWidth(4, 80)
        self.tbl.setColumnWidth(5, 60)
        self.tbl.setColumnWidth(6, 120)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.itemClicked.connect(self._on_row)
        table_layout.addWidget(self.tbl)
        root.addWidget(table_frame)

        # Nạp danh sách mã môn vào combo
        self._load_course_list()

    def _run(self, sql, args=(), commit=False):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(sql, args)
        if commit:
            conn.commit()
        rows = cur.fetchall()
        conn.close()
        return rows

    def _load_course_list(self):
        """Đổ tất cả mã môn lên ComboBox"""
        self.combo_course.clear()
        courses = self._run("SELECT ma_mon FROM mon_hoc ORDER BY ma_mon")
        for (ma,) in courses:
            self.combo_course.addItem(ma)

    def _load_data(self):
        """
        Hiển thị từng bản ghi từ lich_hoc.
        Mỗi hàng là một schedule riêng biệt, có ID để thao tác update/delete.
        """
        self.tbl.setRowCount(0)
        query = """
            SELECT lh.id, l.ma_lop, l.ma_mon, lh.thu, lh.tiet_bat_dau, lh.so_tiet, lh.phong
            FROM lich_hoc AS lh
            JOIN lop_hoc AS l ON lh.ma_lop = l.ma_lop
            ORDER BY l.ma_lop, lh.thu, lh.tiet_bat_dau
        """
        for row in self._run(query):
            # row = (id, ma_lop, ma_mon, thu, tiet_bat_dau, so_tiet, phong)
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            for col, val in enumerate(row):
                item = QTableWidgetItem("" if val is None else str(val))
                # Canh giữa cho các cột số
                if col in (3, 4, 5):
                    item.setTextAlignment(Qt.AlignCenter)
                self.tbl.setItem(r, col, item)

    def _on_row(self, item):
        """
        Khi click vào một hàng, lấy ID lịch, hiển thị lên form để sửa/xóa.
        """
        r = item.row()
        # Cột 0 là ID (ẩn), cột 1=Mã lớp, cột 2=Mã môn, cột 3=Thứ, 4=Tiết bắt đầu, 5=Số tiết, 6=Phòng
        self.current_id = int(self.tbl.item(r, 0).text())
        self.edit_class.setText(self.tbl.item(r, 1).text())
        ma_mon = self.tbl.item(r, 2).text()
        # Bật đúng mã môn trong combo
        idx = self.combo_course.findText(ma_mon)
        if idx >= 0:
            self.combo_course.setCurrentIndex(idx)
        self.spin_day.setValue(int(self.tbl.item(r, 3).text()))
        self.spin_start.setValue(int(self.tbl.item(r, 4).text()))
        self.spin_count.setValue(int(self.tbl.item(r, 5).text()))
        self.edit_room.setText(self.tbl.item(r, 6).text())

    def add_class(self):
        """
        Thêm 1 bản ghi vào lop_hoc (nếu chưa có) và lich_hoc.
        Nếu mã lớp đã tồn tại trong lop_hoc, chỉ thêm lich_hoc mới.
        """
        lop = self.edit_class.text().strip()
        ma = self.combo_course.currentText()
        thu = self.spin_day.value()
        tiet_bd = self.spin_start.value()
        so_tiet = self.spin_count.value()
        phong = self.edit_room.text().strip()

        if not lop or not ma or not phong:
            QMessageBox.warning(self, "Lỗi", "Nhập đủ thông tin (mã lớp, mã môn, phòng).")
            return

        # 1) Thêm vào lop_hoc nếu chưa tồn tại mã lớp
        exists_lop = self._run("SELECT COUNT(*) FROM lop_hoc WHERE ma_lop = ?", (lop,))[0][0]
        if not exists_lop:
            self._run(
                "INSERT INTO lop_hoc(ma_lop, ma_mon) VALUES(?, ?)",
                (lop, ma),
                commit=True
            )
        else:
            # Nếu lớp đã tồn tại nhưng mã môn khác, cập nhật mã môn
            current_mon = self._run("SELECT ma_mon FROM lop_hoc WHERE ma_lop = ?", (lop,))[0][0]
            if current_mon != ma:
                self._run(
                    "UPDATE lop_hoc SET ma_mon = ? WHERE ma_lop = ?",
                    (ma, lop),
                    commit=True
                )

        # 2) Thêm bản ghi lịch vào lich_hoc
        #    Trước khi thêm, kiểm tra xem có chính xác cùng ngày/tiết/phòng không?
        duplicate = self._run(
            "SELECT COUNT(*) FROM lich_hoc WHERE ma_lop = ? AND thu = ? AND tiet_bat_dau = ? AND so_tiet = ? AND phong = ?",
            (lop, thu, tiet_bd, so_tiet, phong)
        )[0][0]
        if duplicate:
            QMessageBox.information(self, "Thông báo", "Bản ghi lịch này đã tồn tại, không thêm lại.")
            return

        self._run(
            "INSERT INTO lich_hoc(ma_lop, thu, tiet_bat_dau, so_tiet, phong) VALUES(?, ?, ?, ?, ?)",
            (lop, thu, tiet_bd, so_tiet, phong),
            commit=True
        )

        self._load_data()
        self._clear_form()

    def update_class(self):
        """
        Cập nhật bản ghi lịch có ID = self.current_id
        """
        if not hasattr(self, 'current_id'):
            QMessageBox.warning(self, "Lỗi", "Chọn một dòng lịch để sửa.")
            return

        thu = self.spin_day.value()
        tiet_bd = self.spin_start.value()
        so_tiet = self.spin_count.value()
        phong = self.edit_room.text().strip()

        if not phong:
            QMessageBox.warning(self, "Lỗi", "Phòng không được để trống.")
            return

        # Cập nhật lich_hoc theo ID
        self._run(
            "UPDATE lich_hoc SET thu = ?, tiet_bat_dau = ?, so_tiet = ?, phong = ? WHERE id = ?",
            (thu, tiet_bd, so_tiet, phong, self.current_id),
            commit=True
        )

        # Nếu mã lớp hoặc mã môn cũng bị thay đổi (nếu người dùng sửa form)
        lop = self.edit_class.text().strip()
        ma = self.combo_course.currentText()
        # Cập nhật mã lớp / mã môn trong lop_hoc nếu có
        #  - tìm ma_lop gốc qua lich_hoc.id, rồi so sánh
        old_lop = self._run("SELECT ma_lop FROM lich_hoc WHERE id = ?", (self.current_id,))[0][0]
        if lop and lop != old_lop:
            # Thay đổi ma_lop cho bảng lich_hoc và lop_hoc
            self._run("UPDATE lich_hoc SET ma_lop = ? WHERE id = ?", (lop, self.current_id), commit=True)
            # Nếu lop mới chưa có trong lop_hoc → thêm
            exists_newlop = self._run("SELECT COUNT(*) FROM lop_hoc WHERE ma_lop = ?", (lop,))[0][0]
            if not exists_newlop:
                self._run("INSERT INTO lop_hoc(ma_lop, ma_mon) VALUES(?, ?)", (lop, ma), commit=True)
            else:
                # cập nhật lại mã môn nếu cần
                self._run("UPDATE lop_hoc SET ma_mon = ? WHERE ma_lop = ?", (ma, lop), commit=True)

        # Cập nhật mã môn trong lop_hoc nếu người dùng đổi
        if ma:
            self._run("UPDATE lop_hoc SET ma_mon = ? WHERE ma_lop = ?", (ma, lop), commit=True)

        self._load_data()
        self._clear_form()

    def delete_class(self):
        """
        Xóa chính xác bản ghi lịch có ID = self.current_id
        Nếu muốn xóa cả lớp, phải xóa tất cả lịch của lớp đó rồi mới xóa lop_hoc.
        """
        if not hasattr(self, 'current_id'):
            QMessageBox.warning(self, "Lỗi", "Chọn một dòng lịch để xóa.")
            return

        # Xác nhận xóa
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa bản ghi lịch này?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # Trước hết, lưu lại mã lớp để kiểm tra sau
        lop = self._run("SELECT ma_lop FROM lich_hoc WHERE id = ?", (self.current_id,))[0][0]

        # Xóa bản ghi lịch
        self._run("DELETE FROM lich_hoc WHERE id = ?", (self.current_id,), commit=True)

        # Nếu một lớp không còn bản ghi lịch nào → có thể xóa cả lop_hoc
        remaining = self._run("SELECT COUNT(*) FROM lich_hoc WHERE ma_lop = ?", (lop,))[0][0]
        if remaining == 0:
            # xóa lop_hoc
            self._run("DELETE FROM lop_hoc WHERE ma_lop = ?", (lop,), commit=True)

        self._load_data()
        self._clear_form()

    def _clear_form(self):
        """Xóa trắng form sau khi Thêm / Cập nhật / Xóa."""
        self.edit_class.clear()
        if self.combo_course.count() > 0:
            self.combo_course.setCurrentIndex(0)
        self.spin_day.setValue(2)
        self.spin_start.setValue(1)
        self.spin_count.setValue(1)
        self.edit_room.clear()
        if hasattr(self, 'current_id'):
            delattr(self, 'current_id')
