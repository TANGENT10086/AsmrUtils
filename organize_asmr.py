import os
import re
import subprocess
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
    main()
