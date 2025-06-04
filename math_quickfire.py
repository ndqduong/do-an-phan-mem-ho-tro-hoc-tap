# math_quickfire.py

import sys
import random
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog, QFrame
)

class MathQuickfireWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.time_left = 60
        self.score = 0
        self.current_answer = None
        self.difficulty_tier = 1  # 1=easy, 2=medium, 3=hard
        self._init_ui()
        self._start_round()

    def _init_ui(self):
        # Set overall background to a soft color
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#f3f4f6"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title Frame
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #1E3A8A; border-radius: 8px;")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(12, 12, 12, 12)

        lbl_title = QLabel("TÍNH NHANH")
        lbl_title.setFont(QFont("Arial", 28, QFont.Bold))
        lbl_title.setStyleSheet("color: white;")
        lbl_title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(lbl_title)

        main_layout.addWidget(title_frame)

        # Timer and Score Frame
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: white; border-radius: 8px;")
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(12, 12, 12, 12)
        info_layout.setSpacing(20)

        self.lbl_timer = QLabel("Thời gian: 60")
        self.lbl_timer.setFont(QFont("Arial", 18, QFont.Bold))
        self.lbl_timer.setStyleSheet("color: #D14343;")  # red
        self.lbl_timer.setAlignment(Qt.AlignCenter)

        self.lbl_score = QLabel("Điểm: 0")
        self.lbl_score.setFont(QFont("Arial", 18, QFont.Bold))
        self.lbl_score.setStyleSheet("color: #157F27;")  # green
        self.lbl_score.setAlignment(Qt.AlignCenter)

        info_layout.addWidget(self.lbl_timer)
        info_layout.addStretch()
        info_layout.addWidget(self.lbl_score)
        main_layout.addWidget(info_frame)

        # Question Frame
        question_frame = QFrame()
        question_frame.setStyleSheet("background-color: white; border-radius: 8px;")
        question_layout = QVBoxLayout(question_frame)
        question_layout.setContentsMargins(12, 12, 12, 12)

        self.lbl_question = QLabel("")
        self.lbl_question.setFont(QFont("Consolas", 24, QFont.Bold))
        self.lbl_question.setStyleSheet("color: #1E3A8A;")
        self.lbl_question.setAlignment(Qt.AlignCenter)
        question_layout.addWidget(self.lbl_question)

        main_layout.addWidget(question_frame)

        # Answer Input
        h_ans = QHBoxLayout()
        h_ans.setSpacing(10)
        self.input_answer = QLineEdit()
        self.input_answer.setFont(QFont("Arial", 18))
        self.input_answer.setFixedWidth(160)
        self.input_answer.setAlignment(Qt.AlignCenter)
        self.input_answer.setPlaceholderText("Nhập kết quả")
        self.input_answer.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #3B82F6;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
            }
            """
        )
        self.input_answer.returnPressed.connect(self._check_answer)
        h_ans.addStretch()
        h_ans.addWidget(self.input_answer)
        h_ans.addStretch()
        main_layout.addLayout(h_ans)

        # Exit Button
        self.btn_exit = QPushButton("Thoát")
        self.btn_exit.setFont(QFont("Arial", 16, QFont.Bold))
        self.btn_exit.setCursor(Qt.PointingHandCursor)
        self.btn_exit.setStyleSheet(
            """
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
            """
        )
        self.btn_exit.clicked.connect(self.close)
        main_layout.addWidget(self.btn_exit, alignment=Qt.AlignCenter)

        # Set fixed window size for a cleaner look
        self.setFixedSize(500, 550)

        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def _start_round(self):
        self.time_left = 60
        self.score = 0
        self.difficulty_tier = 1
        self.lbl_score.setText("Điểm: 0")
        self.input_answer.setEnabled(True)
        self.input_answer.clear()
        self.input_answer.setFocus()
        self._new_question()
        self.timer.start(1000)
        self._update_timer_label()

    def _tick(self):
        self.time_left -= 1
        self._update_timer_label()
        if self.time_left <= 0:
            self.timer.stop()
            self._show_end_dialog()

    def _update_timer_label(self):
        self.lbl_timer.setText(f"Thời gian: {self.time_left}")

    def _new_question(self):
        # Xác định difficulty_tier dựa vào điểm
        if self.score < 10:
            self.difficulty_tier = 1
        elif self.score < 20:
            self.difficulty_tier = 2
        else:
            self.difficulty_tier = 3

        # Sinh biểu thức theo tier
        if self.difficulty_tier == 1:
            # Tier 1: 1 phép tính giữa a∈[1..11], b∈[1..20], op ∈ {+, −, ×}
            a = random.randint(1, 11)
            b = random.randint(1, 20)
            op = random.choice(['+', '−', '×'])
            if op == '+':
                self.current_answer = a + b
            elif op == '−':
                self.current_answer = a - b
            else:  # '×'
                self.current_answer = a * b
            expr = f"{a} {op} {b}"

        elif self.difficulty_tier == 2:
            # Tier 2: Nhân 2 số [1..50]
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            op = '×'
            self.current_answer = a * b
            expr = f"{a} {op} {b}"

        else:
            # Tier 3: Nhân 3 số [1..11]
            a = random.randint(1, 11)
            b = random.randint(1, 11)
            c = random.randint(1, 11)
            op = '×'
            self.current_answer = a * b * c
            expr = f"{a} {op} {b} {op} {c}"

        self.lbl_question.setText(f"{expr} = ?")
        self.input_answer.clear()

    def _check_answer(self):
        text = self.input_answer.text().strip()
        if not text:
            return
        try:
            val = int(text)
        except ValueError:
            self.input_answer.clear()
            return

        if val == self.current_answer:
            # Đúng: +1 điểm, cộng thời gian theo tier
            self.score += 1
            self.lbl_score.setText(f"Điểm: {self.score}")
            if self.difficulty_tier == 1:
                self.time_left += 2   # easy: +2s
            elif self.difficulty_tier == 2:
                self.time_left += 5   # medium: +5s
            else:
                self.time_left += 8   # hard: +8s
        else:
            # Sai: trừ thời gian theo tier
            if self.difficulty_tier == 1:
                self.time_left = max(0, self.time_left - 5)   # easy: -5s
            elif self.difficulty_tier == 2:
                self.time_left = max(0, self.time_left - 3)   # medium: -3s
            else:
                self.time_left = max(0, self.time_left - 1)   # hard: -1s

        self._update_timer_label()
        if self.time_left <= 0:
            self.timer.stop()
            self._show_end_dialog()
        else:
            self._new_question()

    def _show_end_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Kết quả Tính Nhanh")
        dialog.setModal(True)
        dialog.setFixedSize(380, 220)

        # Dialog background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        dialog.setAutoFillBackground(True)
        dialog.setPalette(palette)

        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(20, 20, 20, 20)
        dlg_layout.setSpacing(15)

        title_lbl = QLabel("⏰ Hết giờ!")
        title_lbl.setFont(QFont("Arial", 22, QFont.Bold))
        title_lbl.setStyleSheet("color: #1E3A8A;")
        title_lbl.setAlignment(Qt.AlignCenter)
        dlg_layout.addWidget(title_lbl)

        score_lbl = QLabel(f"Điểm của bạn: {self.score}")
        score_lbl.setFont(QFont("Arial", 18))
        score_lbl.setStyleSheet("color: #157F27;")
        score_lbl.setAlignment(Qt.AlignCenter)
        dlg_layout.addWidget(score_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_retry = QPushButton("Chơi lại")
        btn_retry.setFont(QFont("Arial", 14, QFont.Bold))
        btn_retry.setCursor(Qt.PointingHandCursor)
        btn_retry.setStyleSheet(
            """
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            """
        )
        btn_retry.clicked.connect(lambda: (dialog.accept(), self._start_round()))
        btn_layout.addWidget(btn_retry)

        dlg_layout.addLayout(btn_layout)
        dialog.exec_()

    def _on_restart(self):
        self._start_round()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MathQuickfireWidget()
    w.show()
    sys.exit(app.exec_())
