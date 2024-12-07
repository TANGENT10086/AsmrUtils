import os
import re
from shutil import copyfile

dir_path = r"D:\ASMR\处理\生肉"
mp3_path = r"D:\ASMR\翻译\音频"

row = r"D:\ASMR\处理\生肉"
cooked = r"D:\ASMR\处理\熟肉"

def rename_directory():
    for folder in os.listdir(dir_path):
        os.renames(os.path.join(dir_path, folder), os.path.join(dir_path, re.search(r"RJ\d{6}(\d{2})?", folder).group()))

def move() :
    for folder in os.listdir(dir_path):
        if not folder.startswith("RJ"):
            continue
        folder_path = os.path.join(dir_path, folder)
        for file in os.listdir(folder_path):
            if not file.endswith(".mp3"):
                continue
            filename = os.path.splitext(file)[0]
            filename = filename.replace('&', '~').replace('#', ' ').replace('[', '「').replace(']', '」').replace("\"", "").replace("'", "")
            filename = filename.strip()
            legalFilename = filename + ".mp3"
            if legalFilename != file:
                print(f"{file} 重命名为 {legalFilename}")
                os.renames(os.path.join(folder_path, file), os.path.join(folder_path, legalFilename))
            copyfile(os.path.join(folder_path, legalFilename), os.path.join(mp3_path, folder + "_" + legalFilename))

def check_cover(full_path):
    images = [file for file in os.listdir(full_path) if file.lower().endswith(('.jpg', '.png', '.jpeg'))]
    if not any(file.startswith("cover") for file in images) and len(images) > 1:
        print(f"{full_path} 未确定封面")

def check():
    not_row_list = []
    not_cooked_list = []
    for folder in [f for f in os.listdir(row) if f.startswith("RJ")]:
        folder_path = os.path.join(row, folder)
        check_cover(folder_path)
        if any(file.endswith(".lrc") or file.endswith(".vtt") or file.endswith(".srt") or file.endswith(".ass") for file in os.listdir(folder_path)):
            not_row_list.append(folder)

    for folder in [f for f in os.listdir(cooked) if f.startswith("RJ")]:
        folder_path = os.path.join(cooked, folder)
        check_cover(folder_path)
        if not any(file.endswith(".lrc") or file.endswith(".vtt") or file.endswith(".srt") or file.endswith(".ass") for file in os.listdir(folder_path)):
            not_cooked_list.append(folder)
    
    print(not_row_list)
    print(not_cooked_list)

if __name__ == '__main__':
    # rename_directory()
    check()
    move()