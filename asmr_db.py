import re
import urllib
from lxml import etree
from colorama import Fore, Style
from peewee import SqliteDatabase, Model, CharField

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

def simple_spider(rjcode):
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
        return {
            "album": rjcode,
            "simple_id": "",
            "classic_id": ""
        }
    japanese_link = tree.xpath("//a[contains(text(),'日文')]/@href")
    simple_link = tree.xpath(f"//a[contains(text(),'简体中文')]/@href")
    classic_link = tree.xpath(f"//a[contains(text(),'繁体中文')]/@href")
    return {
        "album" : re.search(r'RJ[^.]*', japanese_link[0]).group() if japanese_link else rjcode,
        "simple_id": re.search(r'RJ[^.]*', simple_link[0]).group() if simple_link else "",
        "classic_id": re.search(r'RJ[^.]*', classic_link[0]).group() if classic_link else "",
    }

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

