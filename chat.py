import sys
import sqlite3
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QFileDialog, QMenu, QAction,
    QInputDialog, QSizePolicy
)
from PyQt5.QtGui import QClipboard, QFont
from PyQt5.QtCore import Qt, QPoint

# --- Database setup: đảm bảo bảng messages có đủ cột ---
DB_PATH = 'chat.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT,
    sender TEXT,
    content TEXT,
    timestamp TEXT,
    file_path TEXT DEFAULT ''
)
''')
conn.commit()
conn.close()


class ChatWidget(QWidget):
    """
    ChatWidget có thể nhúng vào bất kỳ QWidget nào khác,
    nhưng chạy riêng ở đây nên nó được đặt làm chính.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []          # list of (id, sender, content, full_ts, file_path)
        self.current_class = None   # Lớp học đang hiển thị (ví dụ 'CT101', 'CT102', ...)
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Chat Lớp Học")
        self.resize(1200, 800)

        main_v = QVBoxLayout(self)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(0)

        # ==== 1. ComboBox chọn lớp học ====
        top_h = QHBoxLayout()
        lbl = QLabel("Chọn lớp:")
        lbl.setFont(QFont("Arial", 10, QFont.Bold))
        lbl.setFixedHeight(28)

        self.class_combo = QComboBox()
        self.class_combo.addItems(["CT101", "CT102", "CT103", "CT104"])
        self.class_combo.setFixedHeight(28)
        self.class_combo.setStyleSheet("""
            background-color: white;
            color: black;
            padding: 4px;
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
        self.class_combo.currentTextChanged.connect(self.on_class_changed)

        top_h.addWidget(lbl)
        top_h.addWidget(self.class_combo)
        top_h.addStretch()
        main_v.addLayout(top_h)

        # ==== 2. Thanh tìm kiếm tin nhắn ====
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Tìm kiếm tin nhắn...')
        self.search_edit.setFixedHeight(28)
        self.search_edit.setStyleSheet("""
            background-color: white;
            color: black;
            padding: 4px;
            border: 1px solid #ccc;
            border-radius: 4px;
        """)

        btn_search = QPushButton('Tìm')
        btn_search.setFixedSize(50, 28)
        btn_search.setStyleSheet("""
            background-color: #f0f0f0;
            color: black;
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
        btn_search.clicked.connect(self._search_messages)

        btn_clear = QPushButton('Xóa')
        btn_clear.setFixedSize(50, 28)
        btn_clear.setStyleSheet("""
            background-color: #f0f0f0;
            color: black;
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
        btn_clear.clicked.connect(self._refresh_messages)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_clear)
        search_layout.addStretch()
        main_v.addLayout(search_layout)

        # ==== 3. Danh sách chat (QListWidget) ====
        self.chat_list_widget = QListWidget()
        self.chat_list_widget.setStyleSheet('border:none; background:#f0f2f5;')
        self.chat_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_list_widget.customContextMenuRequested.connect(self._on_message_context)
        self.chat_list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_v.addWidget(self.chat_list_widget, stretch=1)

        # ==== 4. Ô nhập tin nhắn, nút đính kèm, nút gửi ====
        input_layout = QHBoxLayout()

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText('Nhập tin nhắn...')
        self.input_edit.setFixedHeight(30)
        self.input_edit.setStyleSheet("""
            background-color: white;
            color: black;
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
        """)

        btn_attach = QPushButton('📎')
        btn_attach.setFixedSize(30, 30)
        btn_attach.setStyleSheet("""
            background-color: #f0f0f0;
            color: black;
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
        btn_attach.clicked.connect(self._attach_file)

        btn_send = QPushButton('Gửi')
        btn_send.setStyleSheet("""
            background-color: #1f3b72;
            color: white;
            border: none;
            border-radius: 4px;
        """)
        btn_send.setFixedSize(70, 30)
        btn_send.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(btn_attach)
        input_layout.addWidget(btn_send)
        main_v.addLayout(input_layout)

        # Khi khởi động, pick lớp đầu tiên nếu có:
        if self.class_combo.count():
            self.class_combo.setCurrentIndex(0)

    def on_class_changed(self, class_name: str):
        """
        Khi người dùng chọn 1 lớp khác, load lại tin nhắn của lớp đó.
        """
        self.set_current_class(class_name)

    def set_current_class(self, class_name: str):
        """
        Gán current_class và tải lại toàn bộ tin nhắn từ DB.
        """
        self.current_class = class_name
        self._refresh_messages()

    def _refresh_messages(self):
        """
        Clear QListWidget, nạp lại tin nhắn từ DB theo class_name.
        """
        self.chat_list_widget.clear()
        self.messages.clear()

        if not self.current_class:
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'SELECT id, sender, content, timestamp, file_path '
            'FROM messages WHERE class_name=? ORDER BY id',
            (self.current_class,)
        )
        rows = c.fetchall()
        conn.close()

        self.messages = rows
        last_date = None

        for msg in rows:
            msg_id, sender, content, full_ts, path = msg

            # Parse ngày từ full_ts = 'YYYY-MM-DD HH:MM'
            try:
                dt = datetime.strptime(full_ts, '%Y-%m-%d %H:%M')
            except:
                dt = datetime.now()
            date_str = dt.strftime('%Y-%m-%d')

            # Nếu khác ngày trước, chèn separator ngày
            if date_str != last_date:
                sep_item = QListWidgetItem()
                sep_item.setFlags(Qt.ItemIsEnabled)
                sep_label = QLabel(f"–––– {date_str} ––––")
                sep_label.setFont(QFont('Arial', 9, QFont.Bold))
                sep_label.setStyleSheet('color:#555555; margin:8px 0px;')
                sep_label.setAlignment(Qt.AlignCenter)
                sep_item.setSizeHint(sep_label.sizeHint())
                self.chat_list_widget.addItem(sep_item)
                self.chat_list_widget.setItemWidget(sep_item, sep_label)
                last_date = date_str

            # Thêm bubble tin nhắn (có header + nội dung)
            self._append_message_item(msg_id, sender, content, full_ts, path)

        self.chat_list_widget.scrollToBottom()

    def _append_message_item(self, msg_id, sender, content, full_ts, path):
        """
        Hiển thị 1 tin nhắn (có header, content, timestamp nội bộ).
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Nếu sender là “Bạn”, bubble bên phải, nền xanh mint nhạt
        if sender == 'Bạn':
            bubble_bg = '#C6FCD6'
            text_color = 'black'
            align = Qt.AlignRight
            header_html = ''  # Không hiện “Bạn”
            border_style = 'none'
        else:
            bubble_bg = '#FFFFFF'
            text_color = 'black'
            align = Qt.AlignLeft
            header_html = (
                f"<div style='font-weight:bold; font-size:10pt; margin-bottom:4px; "
                f"color:#333333;'>{sender}</div>"
            )
            border_style = '1px solid #E0E0E0'

        # Xây dựng HTML cho bubble
        html = (
            f"<div style='background:{bubble_bg}; color:{text_color}; padding:8px;"
            f" border-radius:16px; border:{border_style}; max-width:65%; "
            f"margin-top:8px; margin-bottom:8px; box-shadow:0px 1px 3px rgba(0,0,0,0.1);'>"
            f"{header_html}"
            f"<div style='font-size:10pt; line-height:1.4;'>{content}</div>"
        )
        if path:
            name = path.split('/')[-1]
            html += (
                f"<div style='margin-top:4px; font-size:9pt; color:#1e90ff;'>"
                f"<a href=\"file:///{path}\" style='text-decoration:none; color:#1e90ff;'>{name}</a></div>"
            )
        # Thêm timestamp ở cuối: font 8pt, màu xám, margin-top nhỏ để liền sát
        html += (
            f"<div style='font-size:8pt; color:#757575; text-align:right; margin-top:4px;'>"
            f"{full_ts.split(' ')[1]}</div>"
            f"</div>"
        )

        bubble = QLabel()
        bubble.setTextFormat(Qt.RichText)
        bubble.setText(html)
        bubble.setWordWrap(True)
        # Cho phép mở link bên ngoài (file:///) khi bấm vào
        bubble.setOpenExternalLinks(True)

        layout.addWidget(bubble, alignment=align)

        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        # Gán đầy đủ data (kể cả file_path) để Thu hồi & chỉnh sửa chính xác
        item.setData(Qt.UserRole, (msg_id, sender, content, full_ts, path))
        self.chat_list_widget.addItem(item)
        self.chat_list_widget.setItemWidget(item, widget)
        self.chat_list_widget.scrollToBottom()

    def _send_message(self):
        """
        Lấy text từ input_edit, lưu vào DB với timestamp “YYYY-MM-DD HH:MM”,
        rồi thêm vào QListWidget.
        """
        text = self.input_edit.text().strip()
        if not text or not self.current_class:
            return

        full_ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO messages(class_name, sender, content, timestamp, file_path) '
            'VALUES (?,?,?,?,?)',
            (self.current_class, 'Bạn', text, full_ts, '')
        )
        conn.commit()
        msg_id = c.lastrowid
        conn.close()

        # Kiểm tra cần chèn separator ngày hay không
        if self.messages:
            last_full_ts = self.messages[-1][3]
            last_date = datetime.strptime(last_full_ts, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d')
        else:
            last_date = None
        new_date = full_ts.split(' ')[0]
        if new_date != last_date:
            sep_item = QListWidgetItem()
            sep_item.setFlags(Qt.ItemIsEnabled)
            sep_label = QLabel(f"–––– {new_date} ––––")
            sep_label.setFont(QFont('Arial', 9, QFont.Bold))
            sep_label.setStyleSheet('color:#555555; margin:8px 0px;')
            sep_label.setAlignment(Qt.AlignCenter)
            sep_item.setSizeHint(sep_label.sizeHint())
            self.chat_list_widget.addItem(sep_item)
            self.chat_list_widget.setItemWidget(sep_item, sep_label)

        self.messages.append((msg_id, 'Bạn', text, full_ts, ''))
        self._append_message_item(msg_id, 'Bạn', text, full_ts, '')
        self.input_edit.clear()

    def _attach_file(self):
        """
        Cho phép chọn file, lưu path vào DB, hiển thị trong chat.
        """
        if not self.current_class:
            return

        path, _ = QFileDialog.getOpenFileName(self, 'Chọn tập tin')
        if not path:
            return

        full_ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO messages(class_name, sender, content, timestamp, file_path) '
            'VALUES (?,?,?,?,?)',
            (self.current_class, 'Bạn', '', full_ts, path)
        )
        conn.commit()
        msg_id = c.lastrowid
        conn.close()

        # Kiểm tra separator ngày
        if self.messages:
            last_full_ts = self.messages[-1][3]
            last_date = datetime.strptime(last_full_ts, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d')
        else:
            last_date = None
        new_date = full_ts.split(' ')[0]
        if new_date != last_date:
            sep_item = QListWidgetItem()
            sep_item.setFlags(Qt.ItemIsEnabled)
            sep_label = QLabel(f"–––– {new_date} ––––")
            sep_label.setFont(QFont('Arial', 9, QFont.Bold))
            sep_label.setStyleSheet('color:#555555; margin:8px 0px;')
            sep_label.setAlignment(Qt.AlignCenter)
            sep_item.setSizeHint(sep_label.sizeHint())
            self.chat_list_widget.addItem(sep_item)
            self.chat_list_widget.setItemWidget(sep_item, sep_label)

        self.messages.append((msg_id, 'Bạn', '', full_ts, path))
        self._append_message_item(msg_id, 'Bạn', '', full_ts, path)

    def _search_messages(self):
        """
        Tìm kiếm tin nhắn theo nội dung. Nếu match, hiển thị lại.
        """
        term = self.search_edit.text().strip().lower()
        self.chat_list_widget.clear()
        last_date = None

        for msg in self.messages:
            msg_id, sender, content, full_ts, path = msg
            if term in content.lower():
                dt = datetime.strptime(full_ts, '%Y-%m-%d %H:%M')
                date_str = dt.strftime('%Y-%m-%d')
                if date_str != last_date:
                    sep_item = QListWidgetItem()
                    sep_item.setFlags(Qt.ItemIsEnabled)
                    sep_label = QLabel(f"–––– {date_str} ––––")
                    sep_label.setFont(QFont('Arial', 9, QFont.Bold))
                    sep_label.setStyleSheet('color:#555555; margin:8px 0px;')
                    sep_label.setAlignment(Qt.AlignCenter)
                    sep_item.setSizeHint(sep_label.sizeHint())
                    self.chat_list_widget.addItem(sep_item)
                    self.chat_list_widget.setItemWidget(sep_item, sep_label)
                    last_date = date_str

                self._append_message_item(msg_id, sender, content, full_ts, path)

        self.chat_list_widget.scrollToBottom()

    def _on_message_context(self, pos: QPoint):
        """
        Chuột phải lên tin nhắn sẽ bật menu:
        + Nếu là tin của “Bạn”: Thu hồi, Chỉnh sửa, Sao chép
        + Nếu là tin của người khác: Ẩn, Trả lời
        """
        item = self.chat_list_widget.itemAt(pos)
        if not item:
            return
        msg_id, sender, content, full_ts, path = item.data(Qt.UserRole)
        menu = QMenu()

        if sender == 'Bạn':
            act_recall = QAction('Thu hồi tin nhắn', self)
            act_recall.triggered.connect(lambda: self._recall_message(item))
            act_edit = QAction('Chỉnh sửa tin nhắn', self)
            act_edit.triggered.connect(lambda: self._edit_message(item))
            act_copy = QAction('Sao chép', self)
            act_copy.triggered.connect(lambda: self._copy_message(content))
            menu.addAction(act_recall)
            menu.addAction(act_edit)
            menu.addAction(act_copy)
        else:
            act_hide = QAction('Ẩn tin nhắn', self)
            act_hide.triggered.connect(lambda: self._hide_message(item))
            act_reply = QAction('Trả lời', self)
            act_reply.triggered.connect(lambda: self._reply_message(item))
            menu.addAction(act_hide)
            menu.addAction(act_reply)

        menu.exec_(self.chat_list_widget.viewport().mapToGlobal(pos))

    def _recall_message(self, item: QListWidgetItem):
        """
        Xóa tin khỏi CSDL và refresh lại giao diện. Tin sẽ biến mất.
        """
        msg_id, sender, content, full_ts, path = item.data(Qt.UserRole)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM messages WHERE id=?', (msg_id,))
        conn.commit()
        conn.close()
        # Sau khi xóa DB, hãy refresh toàn bộ để đảm bảo thứ tự separator ngày đúng
        self._refresh_messages()

    def _edit_message(self, item: QListWidgetItem):
        """
        Cho phép chỉnh sửa nội dung message. Sau đó update DB.
        """
        msg_id, sender, content, full_ts, path = item.data(Qt.UserRole)
        new_text, ok = QInputDialog.getText(
            self, 'Chỉnh sửa tin nhắn', 'Nội dung mới:', text=content
        )
        if ok:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('UPDATE messages SET content=? WHERE id=?', (new_text, msg_id))
            conn.commit()
            conn.close()
            self._refresh_messages()

    def _copy_message(self, content: str):
        """
        Copy content vào Clipboard.
        """
        cb: QClipboard = QApplication.clipboard()
        cb.setText(content)

    def _hide_message(self, item: QListWidgetItem):
        """
        Chỉ ẩn item đó (vẫn giữ trong DB).
        """
        item.setHidden(True)

    def _reply_message(self, item: QListWidgetItem):
        """
        Đặt @TênSender: NộiDung vào ô input để trả lời.
        """
        msg_id, sender, content, full_ts, path = item.data(Qt.UserRole)
        self.input_edit.setText(f"@{sender}: {content}")
        self.input_edit.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ChatWidget()
    win.show()
    sys.exit(app.exec_())
