import os
import json


def rename_to_numbers(directory):
    backup_file = os.path.join(directory, "filenames.json")
    files = [f for f in os.listdir(directory) if f.endswith(".mp3")]

    original_names = {str(i): files[i] for i in range(len(files))}
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(original_names, f, ensure_ascii=False, indent=4)

    for i, filename in enumerate(files):
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, f"{i}{os.path.splitext(filename)[1]}")
        os.rename(old_path, new_path)
    print("文件已重命名为数字，原始文件名已备份。")


def restore_filenames(directory):
    backup_file = os.path.join(directory, "filenames.json")
    if not os.path.exists(backup_file):
        print("备份文件不存在，无法恢复文件名。")
        return

    with open(backup_file, 'r', encoding='utf-8') as f:
        original_names = json.load(f)

    for num, original_name in original_names.items():
        original_name = original_name.replace(".mp3", ".lrc")
        temp_name = os.path.join(directory, f"{num}{os.path.splitext(original_name)[1]}")
        original_path = os.path.join(directory, original_name)
        os.rename(temp_name, original_path)

    os.remove(backup_file)
    print("文件名已恢复。")

# 不要把备份文件打进压缩包
if __name__ == '__main__':
    directory = "D:\ASMR\翻译\音频"

    # rename_to_numbers(directory)
    restore_filenames(directory)
