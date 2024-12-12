import os
import re
import sys
from shutil import copyfile
from functools import partial
from PyQt6.QtWidgets import QHBoxLayout, QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QFrame, QTextEdit
from PyQt6.QtCore import Qt

def format_to_rjcode(source_path):
    for folder in os.listdir(source_path):
        os.renames(os.path.join(source_path, folder),
                   os.path.join(source_path, re.search(r"RJ\d{6}(\d{2})?", folder).group()))

def copy_and_prefix(source_path, target_path):
    for folder in os.listdir(source_path):
        if not folder.startswith("RJ"):
            continue
        folder_path = os.path.join(source_path, folder)
        for file in os.listdir(folder_path):
            if not file.endswith(".mp3"):
                continue
            filename = os.path.splitext(file)[0]
            filename = (filename
                        .replace('&', '~')
                        .replace('#', ' ')
                        .replace('[', '「')
                        .replace(']', '」')
                        .replace("\"", "")
                        .replace("'", ""))
            filename = filename.strip()
            legalFilename = filename + ".mp3"
            if legalFilename != file:
                os.renames(os.path.join(folder_path, file), os.path.join(folder_path, legalFilename))
            copyfile(os.path.join(folder_path, legalFilename), os.path.join(target_path, folder + "_" + legalFilename))

def check_cover(folder_path):
    images = [file for file in os.listdir(folder_path) if file.lower().endswith(('.jpg', '.png', '.jpeg'))]
    if not any(file.startswith("cover") for file in images) and len(images) > 1:
        ex.print_log(f"{os.path.basename(folder_path)} 未确定封面")
    if not images:
        ex.print_log(f"{os.path.basename(folder_path)} 无封面")

def check_subtitles(folder_path, is_cooked):
    subtitle_extensions = (".lrc", ".vtt", ".srt", ".ass")
    has_subtitles = any(file.lower().endswith(subtitle_extensions) for file in os.listdir(folder_path))
    if is_cooked and not has_subtitles:
        ex.print_log(f"{os.path.basename(folder_path)} 应是生肉")
    if not is_cooked and has_subtitles:
        ex.print_log(f"{os.path.basename(folder_path)} 应是熟肉")

def check_folders(base_path, is_cooked):
    for folder in [f for f in os.listdir(base_path) if f.startswith("RJ")]:
        folder_path = os.path.join(base_path, folder)
        check_cover(folder_path)
        check_subtitles(folder_path, is_cooked)

def check(row, cooked):
    check_folders(row, is_cooked=False)
    check_folders(cooked, is_cooked=True)

class MultiFolderSelectorApp(QWidget):
    row_label = "生肉"
    cooked_label = "熟肉"
    audio_label = "已处理音频"

    row = "D:\ASMR\处理\生肉"
    cooked = "D:\ASMR\处理\熟肉"
    target_path = "D:\ASMR\翻译\音频"

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("翻译之前")
        self.resize(400, 480)
        self.center()

        main_layout = QVBoxLayout()

        self.default_paths = {
            self.row_label: self.row,
            self.cooked_label: self.cooked,
            self.audio_label: self.target_path
        }

        self.labels = {}

        for label_name, default_path in self.default_paths.items():

            v_layout = QVBoxLayout()

            label = QLabel(f"<span style='color:black; font-family: SimHei; font-size: 14px;'>{label_name}: {default_path}</span>", self)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.labels[label_name] = label
            v_layout.addWidget(label)

            h_layout = QHBoxLayout()

            select_button = QPushButton("选择", self)
            select_button.setFixedSize(80, 40)
            select_button.setStyleSheet("""
                QPushButton {
                    background-color: #f5f8fe;   /* 背景色 */
                    font-size: 16px;             /* 字体大小 */
                    border-radius: 10px;         /* 边框圆角 */
                    padding: 10px 5px;           /* 缩小左右内边距为5px */
                }
                QPushButton:hover {
                    background-color: #e2edfa;   /* 悬停时的背景色 */
                }
                QPushButton:pressed {
                    background-color: #a5cbf1;   /* 按钮按下时的背景色 */
                }
            """)
            select_button.clicked.connect(lambda checked, ln=label_name, dp=default_path: self.open_folder(ln, dp))
            h_layout.addWidget(select_button)

            check_button = QPushButton("检查", self)
            check_button.setFixedSize(80, 40)
            check_button.setStyleSheet("""
                 QPushButton {
                     background-color: #ffcccb;   /* 背景色 */
                     font-size: 16px;             /* 字体大小 */
                     border-radius: 10px;         /* 边框圆角 */
                     padding: 10px 5px;           /* 缩小左右内边距为5px */
                 }
                 QPushButton:hover {
                     background-color: #ffa07a;   /* 悬停时的背景色 */
                 }
                 QPushButton:pressed {
                     background-color: #ff4500;   /* 按钮按下时的背景色 */
                 }
             """)
            check_button.clicked.connect(partial(self.dispatch_check, label_name))
            h_layout.addWidget(check_button)

            v_layout.addLayout(h_layout)

            main_layout.addLayout(v_layout)

            separator = QFrame(self)
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            main_layout.addWidget(separator)

        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.output_text)

        start_layout = QHBoxLayout()
        start_layout.addStretch(1)
        start_button = QPushButton("开始", self)
        start_button.setFixedSize(80, 40)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;   /* 背景色 */
                color: white;                /* 文字颜色 */
                font-size: 16px;             /* 字体大小 */
                border-radius: 10px;         /* 边框圆角 */
                padding: 10px 5px;           /* 缩小左右内边距为5px */
            }
            QPushButton:hover {
                background-color: #45a049;   /* 悬停时的背景色 */
            }
            QPushButton:pressed {
                background-color: #3e8e41;   /* 按钮按下时的背景色 */
            }
        """)
        start_button.clicked.connect(lambda: self.start_process())
        start_layout.addWidget(start_button)
        start_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(start_layout)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def dispatch_check(self, label_name):
        folder_path = re.sub(r'^[^:]+: ', '', re.search(r'>(.*?)<', self.labels[label_name].text()).group(1)).strip()
        if label_name == self.row_label:
            check_folders(folder_path, is_cooked=False)
        elif label_name == self.cooked_label:
            check_folders(folder_path, is_cooked=True)
        elif label_name == self.audio_label:
            if len(os.listdir(self.target_path)) != 0:
                self.print_log(f"{folder_path} 未清空")
        self.print_log(f"{label_name} (路径: {folder_path}) 检查完毕")

    def open_folder(self, label_name, default_path):
        folder_path = QFileDialog.getExistingDirectory(self, f"Select {label_name}", default_path)
        if folder_path:
            self.labels[label_name].setText(
                f"<span style='color:black; font-family: SimHei; font-size: 14px;'>{label_name}: {folder_path}</span>")
            if label_name == self.row_label:
                self.row = folder_path
            elif label_name == self.cooked_label:
                self.cooked = folder_path
            elif label_name == self.audio_label:
                self.target_path = folder_path

    def center(self):
        screen = self.screen().availableGeometry()
        center_point = screen.center()
        window_geo = self.frameGeometry()
        window_geo.moveCenter(center_point)
        self.move(window_geo.topLeft())

    def start_process(self):
        format_to_rjcode(self.row)
        check(self.row, self.cooked)
        copy_and_prefix(self.row, self.target_path)
        self.print_log("运行完毕")

    def print_log(self, text):
        self.output_text.append(text)

# pyinstaller --onefile --windowed --clean --icon=../before.ico before_trans.py

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MultiFolderSelectorApp()
    ex.show()
    sys.exit(app.exec())
