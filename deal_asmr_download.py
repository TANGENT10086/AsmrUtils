import os
import re
import time
import subprocess
from shutil import copyfile
from colorama import Fore, Style
from mutagen.mp3 import MP3
from after_trans import spider


AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac'}
SUBTITLE_EXTENSIONS = {'.lrc', '.srt', '.ass', '.vtt'}
ZIP_EXTENSIONS = {'.zip'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


base_path = "D:\\ASMR\\处理"


def organize_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            if file_ext in AUDIO_EXTENSIONS or file_ext in SUBTITLE_EXTENSIONS or file_ext in ZIP_EXTENSIONS:
                target_path = os.path.join(folder_path, file)
            elif file_ext in IMAGE_EXTENSIONS:
                target_path = os.path.join(folder_path, '图片', file)
            else:
                target_path = os.path.join(folder_path, '其他', file)
            rename_with_auto_increment(file_path, target_path)


def rename_with_auto_increment(src, dest):
    src_name = os.path.splitext(src)[0]
    dest_name = os.path.splitext(dest)[0]
    extension = os.path.splitext(src)[1].lower()
    new_dest = dest
    counter = 1
    # 目标文件已存在，且和源文件路径不同文件名相同
    while os.path.exists(new_dest):
        # 源文件目标文件相同，就不移动
        if src == dest:
            return
        new_dest = f"{dest_name}_{counter}{extension}"
        counter += 1

    os.renames(src, new_dest)


def batch_convert_and_check(directory):
    wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')]

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
            print(f"删除 {wav_file}")
        else:
            print(Fore.YELLOW + f"警告: {mp3_file} 未达到 320 kbps 的比特率，未删除 {wav_file}。" + Style.RESET_ALL)


def unzip_with_7zip(zip_path, output_dir):
    if zip_path != "" and not zip_path.startswith("3500"):
        command = [
            "D:\\Tool\\7Zip\\7-Zip\\7z.exe",
            "x",
            zip_path,
            f"-o{output_dir}",
            "-aoa"
        ]
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL)
            print(f"成功解压 {zip_path} 到 {output_dir}")
        except subprocess.CalledProcessError as e:
            print(f"解压失败: {e}")
        os.remove(zip_path)


def main():
    artificial_path = "D:\ASMR\字幕\正常导入"
    mechanical_path = "D:\ASMR\字幕\whisper large-v3 3500"
    zip_map = {path: {os.path.splitext(zip_file)[0] for zip_file in os.listdir(path)} for path in [artificial_path, mechanical_path]}

    for folder in filter(lambda f: f.startswith("RJ"), os.listdir(base_path)):
        start_time = time.time()
        folder_path = os.path.join(base_path, folder)
        rjcode = re.search(r"RJ\d{6}(\d{2})?", folder).group()
        print(rjcode)
        info = spider(rjcode)
        spider_time = time.time()
        print(f"爬取网页耗时 {1000 * (spider_time - start_time):.2f} 毫秒")


        zip_path = ""
        outer_break = False
        if any(file.endswith(".lrc") or file.endswith(".vtt") or file.endswith(".srt") or file.endswith(".ass") for file in os.listdir(folder_path)):
            outer_break = True
        for key in [artificial_path, mechanical_path]:
            if outer_break:
                break
            for code in [info["album"], info["simple_id"], info["classic_id"]]:
                if code in zip_map[key]:
                    if key == artificial_path:
                        zip_path = os.path.join(folder_path, code + ".zip")
                        copyfile(os.path.join(artificial_path, code + ".zip"), zip_path)
                    else:
                        copyfile(os.path.join(mechanical_path, code + ".zip"), os.path.join(folder_path, "3500" + code + ".zip"))
                    outer_break = True
                    break
        unzip_with_7zip(zip_path, folder_path)

        organize_files(folder_path)

        move_time = time.time()
        print(f"整理文件耗时 {1000 * (move_time - spider_time):.2f} 毫秒")


        batch_convert_and_check(folder_path)
        convert_time = time.time()
        print(f"转换类型耗时 {1000 * (convert_time - move_time):.2f} 毫秒")


        if any(file.endswith(".lrc") or file.endswith(".vtt") or file.endswith(".srt") or file.endswith(".ass") for file in os.listdir(folder_path)):
            os.renames(folder_path, os.path.join(base_path, "熟肉", folder))
        else:
            os.renames(folder_path, os.path.join(base_path, "生肉", folder))


if __name__ == '__main__':
    # base_path = "D:\ASMR\特殊处理\闯关式"
    main()