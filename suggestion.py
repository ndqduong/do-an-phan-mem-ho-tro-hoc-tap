import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QScrollArea, QListWidget, QListWidgetItem, QCheckBox,
    QFrame, QComboBox, QMessageBox, QDialog, QHeaderView
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

DB_PATH = 'lichhoc.db'

# Các ca học: Sáng, Chiều, Tối
SESSIONS = ['Sáng', 'Chiều', 'Tối']
# Thứ tự ưu tiên ca học
SESSION_ORDER = {'Sáng': 0, 'Chiều': 1, 'Tối': 2}


def slot_to_session(slot):
    """
    Chuyển một số tiết (tiet_bat_dau) thành ca:
      - 1..6  → Sáng
      - 7..12 → Chiều
      - >12   → Tối
    """
    if 1 <= slot <= 6:
        return 'Sáng'
    if 7 <= slot <= 12:
        return 'Chiều'
    return 'Tối'


class SuggestionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.free_slots = set()         # set của các ô trống đã chọn (row, col)
        self.available_courses = []     # list các (ma_mon, ten_mon, QCheckBox)
        self.selected_courses = []      # danh sách các chuỗi "ma_mon - ten_mon" đã chọn
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Gợi ý Thời khóa biểu")
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        content = QFrame()
        content.setStyleSheet("background-color: white; border-radius: 10px;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # ===== Panel chọn môn =====
        course_panel = QFrame()
        course_panel.setStyleSheet("background-color: #f9fafb; border-radius: 8px;")
        cp_layout = QHBoxLayout(course_panel)
        cp_layout.setContentsMargins(16, 16, 16, 16)
        cp_layout.setSpacing(20)

        cp_layout.addWidget(QLabel('Chọn môn:'))
        self.course_table = QTableWidget(0, 2)
        self.course_table.setHorizontalHeaderLabels(['Chọn', 'Môn'])
        self.course_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.course_table.setColumnWidth(0, 50)
        self.course_table.verticalHeader().hide()
        self._load_courses()
        scroll_courses = QScrollArea()
        scroll_courses.setFixedSize(500, 150)
        scroll_courses.setWidgetResizable(True)
        scroll_courses.setWidget(self.course_table)
        cp_layout.addWidget(scroll_courses)

        cp_layout.addWidget(QLabel('Môn đã chọn (Check để ưu tiên):'))
        self.selected_list = QListWidget()
        self.selected_list.setFixedSize(750, 150)
        cp_layout.addWidget(self.selected_list)

        content_layout.addWidget(course_panel)

        # ===== Panel chọn buổi trống =====
        free_panel = QFrame()
        free_panel.setStyleSheet("background-color: #f9fafb; border-radius: 8px;")
        fp_layout = QVBoxLayout(free_panel)
        fp_layout.setContentsMargins(16, 16, 16, 16)
        fp_layout.addWidget(QLabel('Chọn buổi trống:'))

        self.free_table = QTableWidget(16, 6)
        self.free_table.setHorizontalHeaderLabels(['T2', 'T3', 'T4', 'T5', 'T6', 'T7'])
        self.free_table.setVerticalHeaderLabels([f'Tiết {i}' for i in range(1, 17)])
        self.free_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.free_table.verticalHeader().setDefaultSectionSize(24)

        # Khóa các ô Tiết 6 (index=5) và 12 (index=11)
        for r in (5, 11):
            for c in range(6):
                it = QTableWidgetItem("")
                it.setFlags(Qt.NoItemFlags)
                it.setBackground(QColor('#cccccc'))
                self.free_table.setItem(r, c, it)

        self.free_table.cellClicked.connect(self._toggle_free_slot)
        self.free_table.horizontalHeader().sectionClicked.connect(self._toggle_free_column)
        fp_layout.addWidget(self.free_table)
        content_layout.addWidget(free_panel)

        # ===== Panel cấu hình và nút Gợi ý =====
        config_panel = QFrame()
        config_panel.setStyleSheet("background-color: #f9fafb; border-radius: 8px;")
        cfg_layout = QHBoxLayout(config_panel)
        cfg_layout.setContentsMargins(16, 16, 16, 16)
        cfg_layout.addWidget(QLabel('Số tiết tối đa/ngày:'))
        self.max_combo = QComboBox()
        self.max_combo.addItems([str(i) for i in range(1, 17)])
        self.max_combo.setCurrentText('6')
        cfg_layout.addWidget(self.max_combo)

        btn_suggest = QPushButton('Gợi ý TKB')
        btn_suggest.setMinimumSize(200, 50)
        btn_suggest.setStyleSheet('background-color: #3B82F6; color: white;')
        btn_suggest.clicked.connect(self._on_suggest)
        cfg_layout.addStretch()
        cfg_layout.addWidget(btn_suggest)
        content_layout.addWidget(config_panel)

        main_layout.addWidget(content, 1)

    def _load_courses(self):
        """
        Lấy danh sách môn từ mon_hoc, đổ lên course_table cùng checkbox.
        """
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT ma_mon, ten_mon FROM mon_hoc ORDER BY ma_mon')
        for ma, ten in cur.fetchall():
            row = self.course_table.rowCount()
            self.course_table.insertRow(row)
            chk = QCheckBox()
            chk.stateChanged.connect(lambda st, m=ma, t=ten: self._on_course_toggle(m, t, st))
            self.course_table.setCellWidget(row, 0, chk)
            self.course_table.setItem(row, 1, QTableWidgetItem(f"{ma} - {ten}"))
            self.available_courses.append((ma, ten, chk))
        conn.close()

    def _on_course_toggle(self, ma, ten, state):
        """
        Khi user chọn/bo chọn một môn, cập nhật self.selected_courses và QListWidget.
        """
        txt = f"{ma} - {ten}"
        if state == Qt.Checked and txt not in self.selected_courses:
            self.selected_courses.append(txt)
        elif state == Qt.Unchecked and txt in self.selected_courses:
            self.selected_courses.remove(txt)

        # Cập nhật QListWidget bên phải
        self.selected_list.clear()
        for c in self.selected_courses:
            item = QListWidgetItem(c)
            # Mỗi item có thể được check thêm để ưu tiên
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.selected_list.addItem(item)

    def _toggle_free_slot(self, r, c):
        """
        Đánh dấu / Bỏ đánh dấu 1 ô (r,c) trong free_table.
        """
        if r in (5, 11):
            return
        key = (r, c)
        it = self.free_table.item(r, c) or QTableWidgetItem("")
        self.free_table.setItem(r, c, it)
        if key in self.free_slots:
            it.setBackground(QColor('white'))
            self.free_slots.remove(key)
        else:
            it.setBackground(QColor('#FFDC00'))
            self.free_slots.add(key)

    def _toggle_free_column(self, c):
        """
        Khi click header cột, chọn/bỏ toàn bộ cột đó (ngoại trừ r=5 và r=11).
        """
        for r in range(16):
            if r in (5, 11):
                continue
            self._toggle_free_slot(r, c)

    def _run(self, sql, args=()):
        """
        Thực thi SELECT/INSERT/UPDATE/DELETE và trả về rows (nếu có).
        """
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql, args)
        rows = cur.fetchall()
        conn.close()
        return rows

    def _on_suggest(self):
        """
        Xây thuật toán gợi ý TKB và hiển thị dialog cho phép Lưu lịch.
        """
        if not self.selected_courses or not self.free_slots:
            QMessageBox.warning(self, 'Thiếu thông tin', 'Vui lòng chọn môn và buổi trống!')
            return

        # 1. Xác định course_order (ưu tiên đã check trước, còn lại sau)
        prio, others = [], []
        for i in range(self.selected_list.count()):
            txt = self.selected_list.item(i).text()
            if self.selected_list.item(i).checkState() == Qt.Checked:
                prio.append(txt)
            else:
                others.append(txt)
        course_order = prio + others
        maxd = int(self.max_combo.currentText())

        # 2. Lấy tất cả bản ghi lich_hoc (mỗi entry là một buổi của một lớp)
        rows = self._run("""
            SELECT l.ma_lop, l.ma_mon, lh.thu, lh.tiet_bat_dau, lh.so_tiet, lh.phong
            FROM lop_hoc AS l
            JOIN lich_hoc AS lh ON l.ma_lop = lh.ma_lop
        """)
        entries = []
        seen_keys = set()
        for ml, mm, thu, tiet_bd, so_tiet, phong in rows:
            # Bỏ môn user không chọn
            chosen_mons = [txt.split(' - ')[0] for txt in course_order]
            if mm not in chosen_mons:
                continue

            # Tạo list các tiết từ tiet_bd đến tiet_bd+so_tiet-1
            slots = list(range(tiet_bd, tiet_bd + so_tiet))
            if not slots:
                continue

            # Loại bỏ duplicate hoàn toàn (nếu DB có entry giống hệt)
            key = (ml, mm, thu, tiet_bd, so_tiet, phong)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            sess = slot_to_session(slots[0])
            entries.append({
                'lop': ml,
                'mon': mm,
                'day': thu,
                'slots': slots,
                'sess': sess,
                'phong': phong
            })

        # 3. Sắp xếp entries theo ưu tiên: (index môn trong course_order, ca, ngày, tiết bắt đầu)
        def entry_priority(e):
            mon_str = e['mon']
            idx = next((i for i, txt in enumerate(course_order) if txt.startswith(f"{mon_str} ")), len(course_order))
            return (idx, SESSION_ORDER[e['sess']], e['day'], e['slots'][0])

        entries.sort(key=entry_priority)

        # 4. Greedy allocate + thu thập result_entries để lưu vào DB
        frees = set(self.free_slots)
        result = {d: {s: [] for s in SESSIONS} for d in range(2, 9)}
        conflicts = []
        count_per_day = {d: 0 for d in range(2, 9)}
        result_entries = []  # list các dict để insert vào saved_tkb

        # Pass1: tuân maxd
        for e in entries:
            placed = False
            d = e['day']
            sess = e['sess']
            meets_maxd = (count_per_day[d] < maxd)
            any_free = all(((sl - 1, d - 2) in frees) for sl in e['slots'])

            if meets_maxd and any_free:
                tiet_str = ",".join(map(str, e['slots']))
                info = f"{e['lop']}: {e['mon']}\nTiết {tiet_str}\nPhòng {e['phong']}"
                result[d][sess].append(info)
                # Lưu entry chuẩn để chèn DB
                result_entries.append({
                    'ma_lop': e['lop'],
                    'ma_mon': e['mon'],
                    'thu': d,
                    'tiet_bat_dau': e['slots'][0],
                    'so_tiet': len(e['slots']),
                    'phong': e['phong']
                })
                for sl in e['slots']:
                    frees.discard((sl - 1, d - 2))
                count_per_day[d] += len(e['slots'])
                placed = True

            if not placed:
                conflicts.append(e)

        # Pass2: bỏ qua maxd, chỉ quan tâm buổi trống
        unplaced = []
        for e in conflicts:
            d = e['day']
            sess = e['sess']
            any_free = all(((sl - 1, d - 2) in frees) for sl in e['slots'])
            if any_free:
                tiet_str = ",".join(map(str, e['slots']))
                info = f"{e['lop']}: {e['mon']}\nTiết {tiet_str}\nPhòng {e['phong']}"
                result[d][sess].append(info)
                # Lưu thêm vào result_entries
                result_entries.append({
                    'ma_lop': e['lop'],
                    'ma_mon': e['mon'],
                    'thu': d,
                    'tiet_bat_dau': e['slots'][0],
                    'so_tiet': len(e['slots']),
                    'phong': e['phong']
                })
                for sl in e['slots']:
                    frees.discard((sl - 1, d - 2))
            else:
                unplaced.append(f"{e['lop']}: {e['mon']}")

        # 5. Hiển thị dialog gợi ý, thêm nút "Lưu lịch" và "Đóng"
        dlg = QDialog(self)
        dlg.setWindowTitle('Lịch gợi ý')
        dlg.resize(960, 700)
        dlg.setStyleSheet("background-color: white;")

        tbl = QTableWidget(len(SESSIONS), 7, dlg)
        tbl.setHorizontalHeaderLabels(['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'])
        tbl.setVerticalHeaderLabels(SESSIONS)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setDefaultSectionSize(100)
        tbl.setWordWrap(True)
        tbl.setStyleSheet("background-color: white;")
        for d in range(2, 9):
            c = d - 2
            for r, s in enumerate(SESSIONS):
                content = '\n---\n'.join(result[d][s])
                tbl.setItem(r, c, QTableWidgetItem(content))

        lbl_unplaced = None
        if unplaced:
            lbl_unplaced = QLabel('Không xếp được: ' + '; '.join(unplaced))
            lbl_unplaced.setWordWrap(True)

        # Nút Lưu và Đóng
        btn_save = QPushButton("Lưu lịch")
        btn_close = QPushButton("Đóng")
        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        btn_hbox.addWidget(btn_save)
        btn_hbox.addSpacing(16)
        btn_hbox.addWidget(btn_close)

        btn_close.clicked.connect(dlg.close)

        def on_save():
            # Tạo batch_name và saved_at
            batch_name = "TKB-" + datetime.now().strftime("%Y%m%d-%H%M%S")
            saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            for rec in result_entries:
                cur.execute("""
                    INSERT INTO saved_tkb 
                    (batch_name, ma_lop, ma_mon, thu, tiet_bat_dau, so_tiet, phong, saved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    batch_name,
                    rec['ma_lop'],
                    rec['ma_mon'],
                    rec['thu'],
                    rec['tiet_bat_dau'],
                    rec['so_tiet'],
                    rec['phong'],
                    saved_at
                ))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Lưu thành công", f"Đã lưu lịch vào batch: {batch_name}")
            dlg.close()

        btn_save.clicked.connect(on_save)

        main_v = QVBoxLayout(dlg)
        main_v.addWidget(tbl)
        if lbl_unplaced:
            main_v.addWidget(lbl_unplaced)
        main_v.addLayout(btn_hbox)

        dlg.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Lịch Học Thông Minh')
        self.resize(1200, 800)
        self.setCentralWidget(SuggestionPage())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
