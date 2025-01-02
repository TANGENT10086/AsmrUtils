import os
import re
import time
import subprocess
from colorama import Fore, Style
from shutil import copyfile
from mutagen.mp3 import MP3
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QFrame, QTextEdit
from PyQt6.QtCore import Qt

from asmr_db import simple_spider

BASE_EXTENSIONS = ('.mp3', '.wav', '.flac', '.lrc', '.srt', '.ass', '.vtt', '.zip')
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')

class MyWindow(QWidget):
    base = "根路径"
    artificial = "非机翻文件路径"
    mechanical = "机翻文件路径"

    default_path = {
        base : "D:\ASMR\处理",
        artificial : "D:\ASMR\字幕\正常导入",
        mechanical : "D:\ASMR\字幕\whisper 3500"
    }

    def __init__(self):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle("翻译之前")
        self.resize(400, 400)
        self.center()

        self.labels = {}
        # 创建一个垂直布局
        main_layout = QVBoxLayout()

        # 根路径
        main_layout.addLayout(self.get_layout(self.base))
        main_layout.addWidget(self.separator())

        # 非机翻路径
        self.checkbox1 = QCheckBox("该路径下存放非机翻压缩包\n格式为zip，仅搜索与解压\n音频名和字幕名不一致需手动调整")
        self.checkbox1.setChecked(True)
        main_layout.addLayout(self.get_layout(self.artificial))
        main_layout.addWidget(self.checkbox1)
        main_layout.addWidget(self.separator())

        # 机翻路径
        self.checkbox2 = QCheckBox("该路径下存放机翻压缩包\n为了区别机翻生肉与熟肉，仅搜索，不解压\n其余同上")
        self.checkbox2.setChecked(True)
        main_layout.addLayout(self.get_layout(self.mechanical))
        main_layout.addWidget(self.checkbox2)
        main_layout.addWidget(self.separator())

        # 是否转mp3
        self.checkbox3 = QCheckBox("是否将所有wav转为mp3\n需安装ffmpeg并设置环境变量")
        self.checkbox3.setChecked(True)
        main_layout.addWidget(self.checkbox3)
        main_layout.addWidget(self.separator())

        # 是否重新组织文件
        self.checkbox4 = QCheckBox("是否启用文件整理\n将音频和压缩包移动至根路径\n将图片移动至图片文件夹\n将其他文件移动到其他文件夹")
        self.checkbox4.setChecked(True)
        main_layout.addWidget(self.checkbox4)
        main_layout.addWidget(self.separator())

        # 开始按钮
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
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
        h_layout.addWidget(start_button)
        h_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(h_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def center(self):
        screen = self.screen().availableGeometry()
        center_point = screen.center()
        window_geo = self.frameGeometry()
        window_geo.moveCenter(center_point)
        self.move(window_geo.topLeft())

    def open_folder(self, label_name, default_path):
        # 选择路径
        folder_path = QFileDialog.getExistingDirectory(self, f"Select {label_name}", default_path)
        if folder_path:
            self.labels[label_name].setText(f"{label_name}: {folder_path}")

    def separator(self):
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def get_layout(self, label_name):
        h_layout = QHBoxLayout()
        label = QLabel(f"{label_name}: {self.default_path[label_name]}", self)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.labels[label_name] = label
        h_layout.addWidget(label)
        h_layout.addStretch(1)
        button = QPushButton("选择", self)
        button.clicked.connect(lambda checked, ln=label_name, dp="": self.open_folder(ln, dp))
        h_layout.addWidget(button)
        return h_layout

    def start_process(self):
        base_path = extract_path(self.labels[self.base].text())
        artificial_path = extract_path(self.labels[self.artificial].text()) if self.checkbox1.isChecked() else ""
        machine_path = extract_path(self.labels[self.mechanical].text()) if self.checkbox2.isChecked() else ""
        is_convert = self.checkbox3.isChecked()
        is_organize = self.checkbox4.isChecked()
        time.sleep(1)
        deal_subtitles(base_path, artificial_path, True)
        deal_subtitles(base_path, machine_path, False)

        for folder in [f for f in os.listdir(base_path) if f.startswith("RJ")]:
            folder_path = os.path.join(base_path, folder)
            if is_organize:
                organize_files(folder_path)

            if is_convert:
                batch_convert(folder_path)

            if has_subtitles(folder_path):
                os.renames(folder_path, os.path.join(base_path, "熟肉", folder))
            else:
                os.renames(folder_path, os.path.join(base_path, "生肉", folder))

        print("执行完毕")

    default_path = {
        base : "D:\ASMR\处理",
        artificial : "D:\ASMR\字幕\正常导入",
        mechanical : "D:\ASMR\字幕\whisper 3500"
    }

def organize_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            if file_ext in BASE_EXTENSIONS:
                target_path = os.path.join(folder_path, file)
            elif file_ext in IMAGE_EXTENSIONS:
                target_path = os.path.join(folder_path, '图片', file)
            else:
                target_path = os.path.join(folder_path, '其他', file)

            rename_with_auto_increment(file_path, target_path)

def rename_with_auto_increment(src, dest):
    name = os.path.splitext(dest)[0]
    extension = os.path.splitext(dest)[1].lower()
    new_dest = dest
    counter = 1
    # 目标文件已存在且和源文件不同
    while os.path.exists(new_dest):
        # 源文件位置正确，直接返回
        if src == dest:
            return
        new_dest = f"{name}_{counter}{extension}"
        counter += 1

    os.renames(src, new_dest)

def batch_convert(directory):
    wav_files = [f for root, dirs, files in os.walk(directory) for f in files if f.endswith('.wav')]
    for wav_file in wav_files:
        wav_path = os.path.join(directory, wav_file)
        output_file = os.path.splitext(wav_path)[0] + '.mp3'
        if os.path.exists(output_file):
            os.remove(output_file)
        command = f'ffmpeg -loglevel error -i "{wav_path}" -b:a 320k "{output_file}" -y'
        subprocess.run(command, shell=True)
        mp3_file = os.path.splitext(wav_path)[0] + '.mp3'
        if MP3(mp3_file).info.bitrate / 1000 == 320:
            os.remove(wav_path)
        else:
            print(Fore.YELLOW + f"警告: {mp3_file} 未达到 320 kbps 的比特率，未删除 {wav_file}。" + Style.RESET_ALL)

def unzip_with_7zip(zip_path, output_dir):
    if zip_path:
        command = [
            "D:\\Tool\\7Zip\\7-Zip\\7z.exe",
            "x",
            zip_path,
            f"-o{output_dir}",
            "-aoa"
        ]
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"{zip_path} 解压失败: {e}" + Style.RESET_ALL)

def extract_path(text):
    match = re.search(r"([A-Za-z]:[\\/][^ ](?:[^\n]*)*)", text)
    return match.group(1) if match else ""

def deal_subtitles(base_path, subtitles_path, is_artificial):
    if subtitles_path == "":
        return

    zip_map = set(os.path.splitext(zip_file)[0] for zip_file in os.listdir(subtitles_path))

    for folder in [f for f in os.listdir(base_path) if f.startswith("RJ")]:
        folder_path = os.path.join(base_path, folder)
        if has_subtitles(folder_path):
            break
        info = simple_spider(folder)
        print(info)
        for code in [info["album"], info["simple_id"], info["classic_id"]]:
            if code in zip_map:
                print(code)
                if is_artificial:
                    unzip_with_7zip(os.path.join(subtitles_path, code + ".zip"), folder_path)
                else:
                    copyfile(os.path.join(subtitles_path, code + ".zip"), os.path.join(folder_path, code + ".zip"))
                break

def has_subtitles(folder_path):
    for root, dirs, files in os.walk(folder_path):
        if any(file.endswith(('.lrc', '.srt', '.ass', '.vtt')) for file in files):
            return True
    return False

def main():
    base_path = "D:\ASMR\处理"
    artificial_path = "D:\ASMR\字幕\正常导入"
    machine_path = "D:\ASMR\字幕\whisper 3500"
    is_convert = True
    is_organize = False

    deal_subtitles(base_path, artificial_path, True)
    deal_subtitles(base_path, machine_path, False)

    for folder in [f for f in os.listdir(base_path) if f.startswith("RJ")]:
        print(folder)
        folder_path = os.path.join(base_path, folder)
        if is_organize:
            organize_files(folder_path)

        if is_convert:
            batch_convert(folder_path)

        if has_subtitles(folder_path):
            os.renames(folder_path, os.path.join(base_path, "熟肉", folder))
        else:
            os.renames(folder_path, os.path.join(base_path, "生肉", folder))

if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # window = MyWindow()
    # window.show()
    # sys.exit(app.exec())
    main()
