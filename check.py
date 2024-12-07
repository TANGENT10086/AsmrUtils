import os
from mutagen.mp3 import MP3

asmr_path = r"E:\ASMR"
trans_path = r"D:\ASMR\字幕\正常导入"


def check_bitrate():
    low128, low320 = [], []

    asmr = [folder for folder in os.listdir(asmr_path) if folder.startswith("RJ")]
    total_count = len(asmr)

    for index, folder in enumerate(asmr, 1):
        folder_path = os.path.join(asmr_path, folder)
        folder_code = folder.split(' ')[0]

        audio_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]
        for file in audio_files:
            mp3_path = os.path.join(folder_path, file)
            mp3 = MP3(mp3_path)
            bitrate = mp3.info.bitrate / 1000

            if 128 < bitrate < 320 and folder_code not in low320:
                low320.append(folder_code)
            elif bitrate <= 128:
                low128.append(f"{folder_code}_{file}")

        print(f"{index}/{total_count}")

    print("low128:")
    print("\n".join(low128))
    print("low320:")
    print("\n".join(low320))


def check_duplication():
    last_rjcode = None
    asmr = [folder for folder in os.listdir(asmr_path) if folder.startswith("RJ")]
    for folder in asmr:
        rjcode = folder.split(" ")[0]
        if rjcode == last_rjcode:
            print(last_rjcode)
        last_rjcode = rjcode


def search_new_trans():
    rjcode = [folder.split(" ")[0] for folder in os.listdir(asmr_path) if folder.startswith("RJ") and folder.split(" ")[1] == "N"]

    for z in os.listdir(trans_path):
        zcode = os.path.splitext(z)[0]
        if zcode in rjcode:
            print(zcode)


def check_cover():
    for folder in [f for f in os.listdir(asmr_path) if f.startswith("RJ")]:
        folder_path = os.path.join(asmr_path, folder)
        images = [file for file in os.listdir(folder_path) if file.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if not any(file.startswith("cover") for file in images) and len(images) > 1:
            print(f"{folder} 未确定封面")
        if not images:
            print(f"{folder} 无图片")


def check_duration():
    for folder in [f for f in os.listdir(asmr_path) if f.startswith("RJ")]:
        folder_path = os.path.join(asmr_path, folder)
        for file in [f for f in os.listdir(folder_path) if f.endswith(".mp3")]:
            audio = MP3(os.path.join(folder_path, file))
            duration = audio.info.length
            if duration > 3600:
                print(f"{os.path.join(folder_path, file)} - 时长: {duration / 60:.2f} 分钟")


if __name__ == '__main__':
    asmr_path = "D:\ASMR\处理\生肉"
    # check_duration()
    check_cover()
    # check_duplication()
    # search_new_trans()
    # check_bitrate()