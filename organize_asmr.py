import os
import re
import subprocess
import zipfile
from pathlib import Path

from colorama import Fore, Style
from shutil import copyfile
from mutagen.mp3 import MP3

from asmr_db import simple_spider

BASE_EXTENSIONS = ('.mp3', '.wav', '.flac', '.lrc', '.srt', '.ass', '.vtt', '.zip')
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')

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
    # 支持的文件扩展名
    supported_formats = ('.wav', '.flac')

    # 查找支持的音频文件
    audio_files = [
        os.path.join(root, f)
        for root, dirs, files in os.walk(directory)
        for f in files if f.endswith(supported_formats)
    ]

    for audio_file in audio_files:
        output_file = os.path.splitext(audio_file)[0] + '.mp3'

        # 如果目标 MP3 文件已存在，先删除
        if os.path.exists(output_file):
            os.remove(output_file)

        # 使用 ffmpeg 转换音频文件为 MP3
        command = f'ffmpeg -loglevel error -i "{audio_file}" -b:a 320k "{output_file}" -y'
        subprocess.run(command, shell=True)

        # 检查生成的 MP3 文件的比特率
        if os.path.exists(output_file):
            mp3_file = MP3(output_file)
            if mp3_file.info.bitrate / 1000 == 320:
                os.remove(audio_file)  # 删除原始文件
            else:
                print(
                    Fore.YELLOW + f"警告: {output_file} 未达到 320 kbps 的比特率，未删除 {audio_file}。" + Style.RESET_ALL)

def unzip(zip_path, output_dir):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                decoded_name = file.encode('cp437').decode('gbk')
                zip_ref.extract(file, output_dir)
                (Path(output_dir) / file).rename(Path(output_dir) / decoded_name)
    except FileNotFoundError:
        print(Fore.RED + f"{zip_path} ZIP文件不存在" + Style.RESET_ALL)
    except PermissionError:
        print(Fore.RED + f"{zip_path} 无法写入目标目录，请检查权限" + Style.RESET_ALL)

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
                    unzip(os.path.join(subtitles_path, code + ".zip"), folder_path)
                else:
                    copyfile(os.path.join(subtitles_path, code + ".zip"), os.path.join(folder_path, code + ".zip"))
                break

def has_subtitles(folder_path):
    for root, dirs, files in os.walk(folder_path):
        if any(file.endswith(('.lrc', '.srt', '.ass', '.vtt', ".zip")) for file in files):
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
    main()
