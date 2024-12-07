import re
import io
import os
import time
import ctypes
import urllib
from PIL import Image
from lxml import etree
from urllib import request
from zipfile import ZipFile
from mutagen.mp3 import MP3
from os.path import basename
from colorama import Fore, Style
from mutagen.id3 import ID3, APIC, TPE1, TALB
from peewee import SqliteDatabase, Model, CharField

dir_path = r"D:\ASMR\处理\生肉"
lrc_path = r"D:\ASMR\翻译\字幕"
zip_path = r"D:\ASMR\字幕\whisper large-v3 3500"

db = SqliteDatabase('dlsite.db')


class Product(Model):
    id = CharField(max_length=10, unique=True)  # 日文RJ号
    simple_id = CharField(max_length=10)  # 简体RJ号
    classic_id = CharField(max_length=10)  # 繁体RJ号
    title = CharField()  # 标题
    character_voice = CharField()  # 声优
    maker_name = CharField()  # 社团名
    tag = CharField()  # 标签
    sell_date = CharField()  # 发售日期
    author = CharField()  # 作者
    illustration = CharField()  # 插画

    class Meta:
        database = db  # 指定数据库


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

def spider(rjcode):
    product = Product.get_or_none(Product.id == rjcode)
    if product:
        print(Fore.YELLOW + f"{rjcode} 已存在" + Style.RESET_ALL)
        return {
            "album": product.id,
            "simple_id": product.simple_id,
            "classic_id": product.classic_id,
            "title": product.title,
            "artist": product.character_voice
        }
    url = f"https://www.dlsite.com/maniax/work/=/product_id/{rjcode}.html"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "cookie": "localesuggested=true; locale=zh-cn; uniqid=0.68km8tf14h; _inflow_params=%7B%22referrer_uri%22%3A%22%22%7D; _inflow_ad_params=%7B%22ad_name%22%3A%22referral%22%7D; __lt__cid=77e5edb6-3b3f-4680-9e92-9568260f984d; _gaid=2019146159.1700016022; _tt_enable_cookie=1; _ttp=9WUw92AYXZI40PWxZ4LrZ8t59np; adr_id=symBOqdnts9BSWaFoCGdMuK0DiKMlZ05IFaO2cqa8NLm6I7g; _yjsu_yjad=1700016023.5e4493ac-1a47-4c69-8050-3778fb8cd65d; adultchecked=1; dlloginjp=1; DL_STAR_ID=8; cptl1=1; OptanonAlertBoxClosed=2024-02-06T07:18:09.330Z; _ga_sid=1707996694; _inflow_dlsite_params=%7B%22dlsite_referrer_url%22%3A%22https%3A%2F%2Fwww.dlsite.com%2Fmaniax%2Fcircle%2Fprofile%2F%3D%2Fmaker_id%2FRG69847.html%22%7D; _ga=GA1.1.2019146159.1700016022; _ga_YG879NVEC7=GS1.1.1707997183.1.1.1707997193.0.0.0; _ga_8CE5GPSG57=GS1.1.1707997184.1.1.1707997193.0.0.0; _ga_7SZK58MGBY=GS1.1.1707997184.1.1.1707997193.0.0.0; _ga_ZW5GTXK6EV=GS1.1.1707996694.5.1.1707997835.0.0.0; cptl3=1; cptl2=1; utm_c=work_link; session_state=cf30a107dd9b2750c66bb6cf7c713595c9ec0b5012a99c27d5c030b75e32ac87.4tced31jpiiok884cgoskkc8c; vendor_design=normal; __DLsite_SID=3rv9k5m4thpvk5tfqhgadeqbqq; loginchecked=1; uhashjp=9b27e974abc1a4048636f9370ec786717ca5ceb6; iom_jp=SFT000005448281; uid_jp=SFT000005448281; DL_PRODUCT_LOG=%2CRJ01219422%2CRJ357069%2CVJ01002159%2CRJ01258864%2CRJ01255152%2CRJ01241065%2CRJ01263771%2CRJ01228291%2CRJ01223120%2CRJ01238637%2CRJ01112305%2CRJ01083454%2CRJ01064664%2CRJ01217348%2CRJ01260482%2CRJ01121785%2CRJ01261790%2CRJ01188411%2CRJ01203763%2CRJ01265139%2CRJ01066842%2CRJ01127775%2CRJ01240271%2CRJ01215410%2CRJ01242069%2CRJ01064682%2CRJ01150190%2CRJ01237209%2CRJ01226682%2CRJ01245701%2CRJ01258637%2CRJ405653%2CRJ01178455%2CRJ01186078%2CRJ01246585%2CRJ01253951%2CRJ01255670%2CRJ01234618%2CRJ01258651%2CRJ01255005%2CRJ01260562%2CRJ01247565%2CRJ01256295%2CRJ01246984%2CRJ01258910%2CRJ01251834%2CRJ01260060%2CRJ01019849%2CRJ01228193%2CRJ01248548; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Oct+04+2024+11%3A13%3A43+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.23.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&AwaitingReconsent=false&groups=C0003%3A1%2CC0001%3A1%2CC0002%3A1%2CC0004%3A1%2CBG5%3A1&geolocation=US%3BCA"
    }
    tree = fetch_page(url, headers)
    if tree is None:
        return {"album": rjcode,
                "simple_id": "",
                "classic_id": "",
                "title": "default",
                "artist": "default",
                "maker_name": "default",
                "tag": "default",
                "sell_date": "default",
                "author": "default",
                "illustration": "default"
                }
    info = {
        "album" : re.search(r'RJ[^.]*', tree.xpath("//a[contains(text(),'日文')]/@href")[0]).group() if tree.xpath("//a[contains(text(),'日文')]/@href") else rjcode,
        "simple_id": "",
        "classic_id": "",
        "title": deal_title(tree.xpath("//*[@id='work_name']/text()")[0]),
        "artist" : " / ".join(tree.xpath("//th[contains(text(),'声优')]/../td/a/text()")) or "未知艺术家",
        "maker_name": tree.xpath('//*[@class="maker_name"]/a/text()')[0],
        "tag": deal_tag(tree),
        "sell_date": tree.xpath("//th[contains(text(),'贩卖日')]/../td/a/text()")[0],
        "author": deal_author(tree),
        "illustration": tree.xpath("//th[contains(text(),'插画')]/../td/a/text()")[0] if tree.xpath("//th[contains(text(),'插画')]/../td/a/text()") else "无"
    }
    for lang in ["繁体中文", "简体中文"]:
        chinese_link = tree.xpath(f"//a[contains(text(),'{lang}')]/@href")
        if chinese_link:
            if lang == "简体中文":
                info["simple_id"] = re.search(r'RJ[^.]*', chinese_link[0]).group()
            else:
                info["classic_id"] = re.search(r'RJ[^.]*', chinese_link[0]).group()
            chinese_tree = fetch_page(chinese_link[0], headers)
            if chinese_tree is not None:
                info["title"] = deal_title(chinese_tree.xpath("//*[@id='work_name']/text()")[0])

    if Product.get_or_none(Product.id == info["album"]):
        print(Fore.YELLOW + f"{rjcode} 日文RJ号已存在" + Style.RESET_ALL)
        return info

    Product.create(id=info["album"], simple_id=info["simple_id"], classic_id=info["classic_id"], title=info["title"], character_voice=info["artist"],
                   maker_name=info["maker_name"], tag=info["tag"], sell_date=info["sell_date"], author=info["author"], illustration=info["illustration"])

    return info
def fetch_page(url, headers, retries=3, timeout=10):
    while retries >= 0:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as response:
                return etree.HTML(response.read().decode("utf-8"))
        except Exception:
            print(Fore.YELLOW + f"{re.search(r'RJ[^.]*', url).group()} 请求失败，重试中... ({retries}次剩余)" + Style.RESET_ALL)
            retries -= 1
    print(Fore.RED + f"{url} 请求失败，已达到最大重试次数 {re.search(r'RJ[^.]*', url).group()} " + Style.RESET_ALL)
    return None
def deal_title(title):
    placeholder = ['〇', '○', '◯', '●','■']
    map = {
        '监x': '监禁',
        '監x': '监禁',
        '陵x': '凌辱',
        '凌x': '凌辱',
        '强x': '强制',
        '強x': '强制',
        '輪x': '轮奸',
        '轮x': '轮奸',

        '痴x': '痴汉',
        'レxプ': 'レイプ',
        'メxガ': 'メスガ',
        'せxリ': 'せなリ',
        '近親相x': '近亲相奸',
        '強x発情': '强制发情',
        'ちxぽ': 'ちんぽ',
        'まxこ': 'まんこ',
        '睡x': '睡奸',
        'x女': '少女',
        '金x': '金玉',
        '孤x院': '孤儿院',
        'xサクヤ': '反サクヤ',
        'x学生': '小学生',
        '年x': '年若',
        '犯xれ': '犯され',
        'モブxなどなど': 'モブ姦などなど',
        'おxん': 'おまん',

        'xリ': 'ロリ',
        'ロx': 'ロリ',
        'Jx': 'JK',
        'xK': 'JK',
        '催x': '催眠',
        'x眠': '催眠',
        'x小鬼': '雌小鬼',
        '雌x鬼': '雌小鬼',
        '雌小x': '雌小鬼',
        '小x': '小穴',
        'x穴': '小穴',
        '萝x': '萝莉',
        'x莉': '萝莉',
        '肉x': '肉棒',
        'x棒': '肉棒',
        '侵x': '侵犯',
        'x犯': '侵犯',
        '奴x': '奴隶',
        'x隶': '奴隶',
    }
    for key in map.keys():
        for char in placeholder:
            title = title.replace(key.replace('x', char), map[key])
    while title.endswith('.'):
        title = title[:-1]
    return re.sub(r'[\\/:*?"<>|]', '', re.sub(r'【.*?】|（.*?）|\(.*?\)|《.*?》|≪.*?≫', '', title)).strip()
def deal_tag(tree):
    map = {
        '秘密さわさわ': '痴汉',
        '强行': '强制',
        '兽X': '兽奸',
        '暗示': '催眠',
        '机械X': '机械奸',
        '异种X': '异种奸',
        '精神支配': '洗脑',
        '强X': '强奸',
        '超ひどい': '鬼畜',
        '造孽': '鬼畜',
        '萝': '萝莉',
        '教育': '调教',
        '奴仆': '奴隶',
        '近親もの': '近亲相奸',
        '骨科': '近亲相奸',
        '下僕': '奴隶',
        '强制/無理矢理': '命令/无理矢理',
        '偷偷摸摸': '痴汉',
        'しつけ': '调教',
    }
    tag_list = []
    i = 1
    while True:
        a = tree.xpath(f"//th[contains(text(),'分类')]/../td/div/a[{i}]/text()")
        if a:
            tag = a[0]
            for key in map.keys():
                tag = tag.replace(key, map[key])
            tag_list.append(tag)
            i += 1
        else:
            break

    return " ".join(tag_list)
def deal_author(tree):
    story = tree.xpath("//th[contains(text(),'剧情')]/../td/a/text()")
    if story:
        return " ".join(story)
    author = tree.xpath("//th[contains(text(),'作者')]/../td/a/text()")
    if author:
        return " ".join(author)
    return "无"

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
