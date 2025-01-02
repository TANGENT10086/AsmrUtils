import re
import io
import os
import time
import ctypes
from PIL import Image
from zipfile import ZipFile
from mutagen.mp3 import MP3
from os.path import basename
from mutagen.id3 import ID3, APIC, TPE1, TALB

from asmr_db import spider

dir_path = r"D:\ASMR\处理\生肉"
lrc_path = r"D:\ASMR\翻译\字幕"
zip_path = r"D:\ASMR\字幕\whisper 3500"

def move_lrc():
    if os.path.exists(lrc_path):
        for file in os.listdir(lrc_path):
            index = file.find("_")
            rjcode = file[:index]
            filename = file[index+1:]
            os.renames(os.path.join(lrc_path, file), os.path.join(dir_path, rjcode, filename))

    os.makedirs(lrc_path, exist_ok=True)

def process_audio():
    for folder in [f for f in os.listdir(dir_path) if f.startswith("RJ")]:
        suffix = get_suffix(folder)
        rjcode = folder.split(" ")[0]
        start_time = time.time()
        folder_path = os.path.join(dir_path, folder)
        print(rjcode)
        info = select_cover(folder, spider(rjcode))
        print("%s %s" % (info['album'], info['title']))
        spider_time = time.time()
        print("爬取网页耗时%d毫秒" % (1000*(spider_time-start_time)))

        for file in [f for f in os.listdir(folder_path) if f.endswith(".mp3")]:
            set_mp3_info(os.path.join(folder_path, file), info)
        target_path = os.path.join(dir_path, info["album"] + suffix + info["title"])
        os.rename(folder_path, target_path)
        set_folder_icon(target_path)
        set_time = time.time()
        print("修改信息耗时%d毫秒\n" % (1000*(set_time-spider_time)))

def get_suffix(folder):
    if len(folder.split(" ")) == 1:
        if dir_path == r"D:\ASMR\处理\生肉":
            suffix = " N "
        elif dir_path == r"D:\ASMR\处理\熟肉":
            suffix = " "
        else:
            suffix = " unknown "
    else:
            if folder.split(" ")[1] == "N":
                suffix = " N "
            else:
                suffix = " "
    return suffix

def select_cover(folder, info):
    folder_path = os.path.join(dir_path, folder)
    images = [file for file in os.listdir(folder_path) if file.lower().endswith(('.jpg', '.png', '.jpeg'))]
    if images:
        cover_file = next((f for f in images if f.startswith("cover")), images[0])
        cover_path = os.path.join(folder_path, cover_file)
        with Image.open(cover_path) as image:
            info["type"] = image.format
            byte_io = io.BytesIO()
            image.save(byte_io, format=info["type"])
            info["cover"] = byte_io.getvalue()
            image = image.crop(get_coordinate(image.size))
            image = image.resize((256, 256), Image.Resampling.LANCZOS)
            image.save(os.path.join(folder_path, "cover.ico"), format='ICO')
    else:
        print("没有图片")
    return info

def set_mp3_info(file, info):
    del_cover(file)
    audio = MP3(file)
    if audio.tags is None:
        audio.add_tags()

    audio.tags['APIC'] = APIC(encoding=3, mime=f'image/{info["type"]}', type=3, desc='Cover', data=info["cover"])
    audio.tags['TPE1'] = TPE1(encoding=3, text=info["artist"])
    audio.tags['TALB'] = TALB(encoding=3, text=info["album"])

    audio.save()

def del_cover(mp3_dir):
    audio = MP3(mp3_dir)

    if audio.tags is None:
        audio.add_tags()

    if isinstance(audio.tags, ID3):
        for tag in list(audio.tags.keys()):
            if tag.startswith('APIC'):
                del audio.tags[tag]

    audio.save()

def set_folder_icon(folder_path, icon_name="cover.ico"):

    if not os.path.exists(folder_path):
        raise Exception("Folder not found")

    ini_file_path = os.path.join(folder_path, "desktop.ini")

    if os.path.exists(ini_file_path):
        os.remove(ini_file_path)
        SHChangeNotify = ctypes.windll.shell32.SHChangeNotify
        SHChangeNotify(0x08000000, 0x0000, None, None)


    if not os.access(folder_path, os.W_OK):
        raise PermissionError(f"No write permission for folder: {folder_path}")

    with open(ini_file_path, 'w', encoding='utf-8') as ini_file:
        ini_file.write("[.ShellClassInfo]\n")
        ini_file.write(f"IconResource={icon_name},0\n")  # 设置图标路径
        ini_file.write(f"IconFile={icon_name}\n")  # 备用图标路径
        ini_file.write("IconIndex=0\n")
        ini_file.write("InfoTip=This folder has a custom icon.\n")

    ctypes.windll.kernel32.SetFileAttributesW(ctypes.c_wchar_p(folder_path), 0x04)

    SHChangeNotify = ctypes.windll.shell32.SHChangeNotify
    SHChangeNotify(0x08000000, 0x0000, None, None)

def get_coordinate(size):
    diff = size[0] - size[1]
    if diff > 0:
        a = diff // 2
        return (a, 0, size[0] - a, size[1])
    elif diff < 0:
        a = -diff // 2
        return (0, a, size[0], size[1] - a)
    else:
        return (0, 0, size[0], size[1])

def zip_lrc():
    for folder in os.listdir(dir_path):
        if folder.startswith("RJ"):
            zip_list = [os.path.join(dir_path, folder, file) for file in os.listdir(os.path.join(dir_path, folder)) if file.endswith(".lrc")]
            rjcode = folder.split(" ")[0]
            zip_filename = os.path.join(zip_path, f"{rjcode}.zip")
            with ZipFile(zip_filename, "w") as z:
                for f in zip_list:
                    z.write(f, arcname=basename(f))

if __name__ == '__main__':

    # 生肉
    move_lrc()
    zip_lrc()
    process_audio()

    # # 熟肉
    # dir_path = "D:\ASMR\处理\熟肉"
    # process_audio()
