import shutil
import subprocess
import os
from os.path import basename
from zipfile import ZipFile

upload_path = "D:\ASMR\上传"

def remove_mp3():
    for folder in [f for f in os.listdir(upload_path) if f.startswith("RJ")]:
        for file in os.listdir(os.path.join(upload_path, folder)):
            if file.endswith(('.mp3','.jpg', '.png', 'jpeg')):
                os.remove(os.path.join(upload_path, folder, file))
            if os.path.isdir(os.path.join(upload_path, folder, file)):
                shutil.rmtree(os.path.join(upload_path, folder, file))

def batch_zip():
    zip_path = os.path.join(upload_path, "压缩包")
    os.makedirs(zip_path, exist_ok=True)

    for folder in [f for f in os.listdir(upload_path) if f.startswith("RJ")]:
        folder_path = os.path.join(upload_path, folder)
        # 需要压缩的文件
        zip_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]
        # 压缩文件名和压缩文件路径
        zip_name = os.path.join(zip_path, folder + ".zip")

        with ZipFile(zip_name, "w") as zip_ref:
            for file in zip_list:
                zip_ref.write(file, arcname=basename(file))

        print(folder)
if __name__ == '__main__':
    # remove_mp3()
    batch_zip()