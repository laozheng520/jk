import os
import sys
import json
import re
import time
import subprocess
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
for _cand in ("enc", "py", "pyy"):
    _p = os.path.join(ROOT, _cand)
    if os.path.isdir(_p):
        PYY_DIR = _p
        break
else:
    PYY_DIR = os.path.join(ROOT, "PY")
API_JSON = os.path.join(ROOT, "公众号宜优精选.json")
SCAN_EXCLUDE = {"__init__", "base", "spider", "main", "config"}
DEEP_WORKERS = 10
URL_TIMEOUT = 10
MAX_URLS_PER_FILE = 5

PY_KEY_HEX = os.environ.get("PY_KEY_HEX", "").strip()
PY_KEY = bytes.fromhex(PY_KEY_HEX) if len(PY_KEY_HEX) == 64 else None

_PINYIN_WORD_MAP = {
    "aikan": "爱看",
    "aiqing": "爱情",
    "ba": "八",
    "baba": "爸爸",
    "bai": "百",
    "bailing": "白领",
    "bang": "帮",
    "baokuan": "爆款",
    "bofang": "播放",
    "bofangqi": "播放器",
    "bofangye": "播放页",
    "chang": "场",
    "chaoqing": "超清",
    "cheng": "城",
    "chengshi": "城市",
    "chuanshuo": "传说",
    "chuanyue": "穿越",
    "cunzhuang": "村庄",
    "dajuyuan": "大剧院",
    "dapian": "大片",
    "di": "第",
    "dianbo": "点播",
    "diannao": "电脑",
    "dianshi": "电视",
    "dianshiju": "电视剧",
    "dianying": "电影",
    "dianyingyuan": "电影院",
    "difang": "地方",
    "diguo": "帝国",
    "donghua": "动画",
    "dongman": "动漫",
    "dongxi": "东西",
    "dongzuo": "动作",
    "duanju": "短剧",
    "dubo": "独播",
    "dujia": "独家",
    "duoduo": "多多",
    "duoduoyingshi": "多多影视",
    "duoduoyingyuan": "多多影院",
    "dushi": "都市",
    "er": "二",
    "ertong": "儿童",
    "erzi": "儿子",
    "fanda": "饭搭",
    "fandazi": "饭搭子",
    "fanzui": "犯罪",
    "feikuai": "飞快",
    "feikuaiyingshi": "飞快影视",
    "fenlei": "分类",
    "gangju": "港剧",
    "gaofen": "高分",
    "gaoqing": "高清",
    "ge": "阁",
    "gengxin": "更新",
    "gewu": "歌舞",
    "gewupian": "歌舞片",
    "gongchang": "工厂",
    "gongting": "宫廷",
    "guankan": "观看",
    "guochan": "国产",
    "guonei": "国内",
    "guowai": "国外",
    "guoyuan": "果园",
    "haiwai": "海外",
    "hanju": "韩剧",
    "hanyu": "韩语",
    "hao": "号",
    "haokan": "好看",
    "haopian": "好片",
    "hongguo": "红果",
    "hongguohuangju": "红果黄剧",
    "huaijiu": "怀旧",
    "huangju": "黄剧",
    "huaren": "华人",
    "huayu": "华语",
    "huayuan": "花园",
    "huifang": "回放",
    "jiakong": "架空",
    "jianpian": "荐片",
    "jianpianyingshi": "荐片影视",
    "jiating": "家庭",
    "jiemei": "姐妹",
    "jilupian": "纪录片",
    "jingcai": "精彩",
    "jingdian": "经典",
    "jingfei": "警匪",
    "jingsong": "惊悚",
    "jingxuan": "精选",
    "jinpai": "金牌",
    "jinpaiyingyuan": "金牌影院",
    "jiu": "九",
    "ju": "剧",
    "juchang": "剧场",
    "julebu": "俱乐部",
    "jumi": "剧迷",
    "juqing": "剧情",
    "juyuan": "剧院",
    "kehuan": "科幻",
    "kongbu": "恐怖",
    "koubei": "口碑",
    "languang": "蓝光",
    "laopian": "老片",
    "laoshi": "老师",
    "le": "乐",
    "leyuan": "乐园",
    "lianzai": "连载",
    "liebiaoye": "列表页",
    "lishi": "历史",
    "liu": "六",
    "lou": "楼",
    "lunli": "伦理",
    "luntan": "论坛",
    "maitian": "麦田",
    "maitianyingyuan": "麦田影院",
    "mama": "妈妈",
    "maoxian": "冒险",
    "meiju": "美剧",
    "men": "门",
    "mianfei": "免费",
    "mogu": "蘑菇",
    "moguyingshi": "蘑菇影视",
    "muchang": "牧场",
    "naifei": "奈飞",
    "naifeigongchang": "奈飞工厂",
    "nian": "年",
    "nongchang": "农场",
    "nongcun": "农村",
    "nongcunmama": "农村妈妈",
    "nunu": "努努",
    "nunuyingyuan": "努努影院",
    "nver": "女儿",
    "oumei": "欧美",
    "pai": "派",
    "paopao": "泡泡",
    "paopaowu": "泡泡屋",
    "pian": "片",
    "pianku": "片库",
    "pianyuan": "片源",
    "piaofang": "票房",
    "qi": "七",
    "qian": "千",
    "qianqian": "千千",
    "qianqianyingshi": "千千影视",
    "qihuan": "奇幻",
    "qingchun": "青春",
    "quanji": "全集",
    "quanwang": "全网",
    "rebo": "热播",
    "rexue": "热血",
    "rebozhijia": "热播之家",
    "remen": "热门",
    "renmen": "人们",
    "ri": "日",
    "rihan": "日韩",
    "riju": "日剧",
    "riyu": "日语",
    "san": "三",
    "shenghuo": "生活",
    "shenhua": "神话",
    "shenju": "神剧",
    "shequ": "社区",
    "shi": "十",
    "shijian": "时间",
    "shijie": "世界",
    "shipin": "视频",
    "shoubo": "首播",
    "shoufa": "首发",
    "shouji": "手机",
    "shouye": "首页",
    "si": "四",
    "sousuo": "搜索",
    "taiju": "泰剧",
    "tang": "堂",
    "tiantang": "天堂",
    "tiyu": "体育",
    "tongxue": "同学",
    "tuijian": "推荐",
    "wan": "万",
    "wang": "网",
    "wangguo": "王国",
    "wangju": "网剧",
    "wangluo": "网络",
    "wanjie": "完结",
    "wenyi": "文艺",
    "wu": "五",
    "wuxia": "武侠",
    "xiangcun": "乡村",
    "xiangqingye": "详情页",
    "xianxia": "仙侠",
    "xiaoyuan": "校园",
    "xiaozhen": "小镇",
    "xihuan": "喜欢",
    "xiju": "喜剧",
    "xingqiu": "星球",
    "xinpian": "新片",
    "xiongdi": "兄弟",
    "xuanhuan": "玄幻",
    "xuanyi": "悬疑",
    "xuesheng": "学生",
    "yi": "一",
    "ying": "影",
    "yingcheng": "影城",
    "yingmi": "影迷",
    "yingshi": "影视",
    "yingwen": "英文",
    "yingxiang": "映像",
    "yingxiangxingqiu": "映像星球",
    "yingyin": "影音",
    "yingyuan": "影院",
    "yinyue": "音乐",
    "youqing": "友情",
    "yuan": "院",
    "yuanchuang": "原创",
    "yuanxian": "院线",
    "yue": "月",
    "zainan": "灾难",
    "zaixian": "在线",
    "zaixianzhijia": "在线之家",
    "zhan": "站",
    "zhanzheng": "战争",
    "zhencang": "珍藏",
    "zhibo": "直播",
    "zhichang": "职场",
    "zhongguo": "中国",
    "zhongwen": "中文",
    "zhuanji": "传记",
    "zhuiju": "追剧",
    "ziyuan": "资源",
    "zizhi": "自制",
    "zongyi": "综艺",
    "zu": "族",
    "zuire": "最热",
    "zuixin": "最新",
}


_PINYIN_SYLLABLES = frozenset([
    "a", "ai", "an", "ang", "ao", "ba", "bai", "ban", "bang", "bao", "bei", "ben",
    "beng", "bi", "bian", "biao", "bie", "bin", "bing", "bo", "bu", "ca", "cai", "can",
    "cang", "cao", "ce", "cen", "ceng", "cha", "chai", "chan", "chang", "chao", "che", "chen",
    "cheng", "chi", "chong", "chou", "chu", "chuai", "chuan", "chuang", "chui", "chun", "chuo", "ci",
    "cong", "cou", "cu", "cuan", "cui", "cun", "cuo", "da", "dai", "dan", "dang", "dao",
    "de", "dei", "den", "deng", "di", "dian", "diao", "die", "ding", "diu", "dong", "dou",
    "du", "duan", "dui", "dun", "duo", "e", "ei", "en", "eng", "er", "fa", "fan",
    "fang", "fei", "fen", "feng", "fo", "fou", "fu", "ga", "gai", "gan", "gang", "gao",
    "ge", "gei", "gen", "geng", "gong", "gou", "gu", "gua", "guai", "guan", "guang", "gui",
    "gun", "guo", "ha", "hai", "han", "hang", "hao", "he", "hei", "hen", "heng", "hong",
    "hou", "hu", "hua", "huai", "huan", "huang", "hui", "hun", "huo", "ji", "jia", "jian",
    "jiang", "jiao", "jie", "jin", "jing", "jiong", "jiu", "ju", "juan", "jue", "jun", "ka",
    "kai", "kan", "kang", "kao", "ke", "kei", "ken", "keng", "kong", "kou", "ku", "kua",
    "kuai", "kuan", "kuang", "kui", "kun", "kuo", "la", "lai", "lan", "lang", "lao", "le",
    "lei", "leng", "li", "lia", "lian", "liang", "liao", "lie", "lin", "ling", "liu", "long",
    "lou", "lu", "luan", "lue", "lun", "luo", "lv", "ma", "mai", "man", "mang", "mao",
    "me", "mei", "men", "meng", "mi", "mian", "miao", "mie", "min", "ming", "miu", "mo",
    "mou", "mu", "na", "nai", "nan", "nang", "nao", "ne", "nei", "nen", "neng", "ni",
    "nian", "niang", "niao", "nie", "nin", "ning", "niu", "nong", "nou", "nu", "nuan", "nue",
    "nuo", "nv", "o", "ou", "pa", "pai", "pan", "pang", "pao", "pei", "pen", "peng",
    "pi", "pian", "piao", "pie", "pin", "ping", "po", "pou", "pu", "qi", "qia", "qian",
    "qiang", "qiao", "qie", "qin", "qing", "qiong", "qiu", "qu", "quan", "que", "qun", "ran",
    "rang", "rao", "re", "ren", "reng", "ri", "rong", "rou", "ru", "ruan", "rui", "run",
    "ruo", "sa", "sai", "san", "sang", "sao", "se", "sen", "seng", "sha", "shai", "shan",
    "shang", "shao", "she", "shei", "shen", "sheng", "shi", "shou", "shu", "shua", "shuai", "shuan",
    "shuang", "shui", "shun", "shuo", "si", "song", "sou", "su", "suan", "sui", "sun", "suo",
    "ta", "tai", "tan", "tang", "tao", "te", "teng", "ti", "tian", "tiao", "tie", "ting",
    "tong", "tou", "tu", "tuan", "tui", "tun", "tuo", "wa", "wai", "wan", "wang", "wei",
    "wen", "weng", "wo", "wu", "xi", "xia", "xian", "xiang", "xiao", "xie", "xin", "xing",
    "xiong", "xiu", "xu", "xuan", "xue", "xun", "ya", "yan", "yang", "yao", "ye", "yi",
    "yin", "ying", "yo", "yong", "you", "yu", "yuan", "yue", "yun", "za", "zai", "zan",
    "zang", "zao", "ze", "zei", "zen", "zeng", "zha", "zhai", "zhan", "zhang", "zhao", "zhe",
    "zhei", "zhen", "zheng", "zhi", "zhong", "zhou", "zhu", "zhua", "zhuai", "zhuan", "zhuang", "zhui",
    "zhun", "zhuo", "zi", "zong", "zou", "zu", "zuan", "zui", "zun", "zuo",
])

def _split_pinyin_syllables(text):
    """拼音串切成音节（长度优先+回溯）；切不动返回 None"""
    n = len(text)
    if n == 0 or n > 60:
        return None
    dp = [None] * (n + 1)
    dp[n] = []
    for i in range(n - 1, -1, -1):
        for l in range(min(6, n - i), 0, -1):
            if text[i:i + l] in _PINYIN_SYLLABLES and dp[i + l] is not None:
                dp[i] = [text[i:i + l]] + dp[i + l]
                break
    return dp[0]

def _pinyin_to_cn_strict(chunk):
    """严格拼音转中文：只能用词库整词转出，任何单字兜底/切分失败返回 None"""
    syls = _split_pinyin_syllables(chunk)
    if not syls:
        return None
    out, i, n = [], 0, len(syls)
    while i < n:
        hit = None
        for l in range(min(4, n - i), 0, -1):
            key = "".join(syls[i:i + l])
            if key in _PINYIN_WORD_MAP:
                hit = _PINYIN_WORD_MAP[key]
                i += l
                break
        if not hit:
            return None
        out.append(hit)
    return "".join(out)

def _strict_pinyin_name(low):
    """文件名严格转中文：所有字母块都必须整词转出，否则返回 None（数字保留）"""
    parts = re.findall(r"[a-z]+|\d+", low)
    if not parts:
        return None
    out, has_alpha = [], False
    for p in parts:
        if p.isalpha():
            has_alpha = True
            c = _pinyin_to_cn_strict(p)
            if c is None:
                return None
            out.append(c)
        else:
            out.append(p)
    return "".join(out) if has_alpha else None

def _format_name_2p2(cn_chars, en_chars, dg_chars):
    """2+2 格式化：英文优先，其次数字，最后纯中文截4个"""
    if en_chars:
        return en_chars[:2] + cn_chars[:2]
    elif dg_chars:
        return dg_chars[:2] + cn_chars[:2]
    else:
        return cn_chars[:4]
def _num_to_cn(n):
    d = "零一二三四五六七八九"
    if n < 10:
        return d[n]
    if n < 100:
        t, o = divmod(n, 10)
        s = "十" if t == 1 else d[t] + "十"
        return s + (d[o] if o else "")
    return str(n)

def _random_unique_cn(base, taken):
    import random
    if base not in taken:
        return base
    pool = "23456789新老大小前后甲乙丙丁天地东西南北"
    stem = base[:3]
    for _ in range(200):
        cand = (stem + random.choice(pool))[:4]
        if cand not in taken:
            return cand
    for _ in range(500):
        cand = "".join(random.choice(pool) for _ in range(4))
        if cand not in taken:
            return cand
    return base

def make_cn_name(filename, taken, fengdou_counter):
    name = filename[:-3] if filename.endswith(".py") else filename
    cn_chars = "".join(c for c in name if "\u4e00" <= c <= "\u9fff")
    en_chars = "".join(c for c in name if "a" <= c.lower() <= "z")
    dg_chars = "".join(c for c in name if "0" <= c <= "9")
    if cn_chars:
        cn_base = _format_name_2p2(cn_chars, en_chars, dg_chars)
        if not cn_base:
            return None, fengdou_counter
        return _random_unique_cn(cn_base, taken), fengdou_counter
    strict = _strict_pinyin_name(name.lower())
    if strict is None:
        while True:
            cn_name = "枫斗" + _num_to_cn(fengdou_counter[0]) + "线"
            fengdou_counter[0] += 1
            if cn_name not in taken:
                return cn_name, fengdou_counter
    cn2 = "".join(c for c in strict if "\u4e00" <= c <= "\u9fff")
    dg2 = "".join(c for c in strict if "0" <= c <= "9")
    cn_base = _format_name_2p2(cn2, "", dg2)
    if not cn_base:
        return None, fengdou_counter
    return _random_unique_cn(cn_base, taken), fengdou_counter

# 拼音音节 -> 常用单字
_PINYIN_CHAR_MAP = {
    "a": "啊",
    "ai": "爱",
    "an": "安",
    "ang": "昂",
    "ao": "奥",
    "ba": "爸",
    "bai": "白",
    "ban": "办",
    "bang": "帮",
    "bao": "爆",
    "bei": "碑",
    "ben": "本",
    "beng": "崩",
    "bi": "比",
    "bian": "变",
    "biao": "表",
    "bie": "别",
    "bin": "宾",
    "bing": "并",
    "bo": "播",
    "bu": "部",
    "ca": "擦",
    "cai": "彩",
    "can": "参",
    "cang": "藏",
    "cao": "草",
    "ce": "测",
    "cen": "岑",
    "ceng": "层",
    "cha": "查",
    "chai": "拆",
    "chan": "产",
    "chang": "场",
    "chao": "超",
    "che": "车",
    "chen": "陈",
    "cheng": "城",
    "chi": "吃",
    "chong": "充",
    "chou": "抽",
    "chu": "出",
    "chuai": "揣",
    "chuan": "穿",
    "chuang": "创",
    "chui": "吹",
    "chun": "春",
    "chuo": "戳",
    "ci": "此",
    "cong": "从",
    "cou": "凑",
    "cu": "促",
    "cuan": "窜",
    "cui": "催",
    "cun": "村",
    "cuo": "错",
    "da": "大",
    "dai": "带",
    "dan": "单",
    "dang": "当",
    "dao": "到",
    "de": "的",
    "dei": "得",
    "den": "扽",
    "deng": "等",
    "di": "帝",
    "dian": "电",
    "diao": "掉",
    "die": "跌",
    "ding": "定",
    "diu": "丢",
    "dong": "动",
    "dou": "都",
    "du": "独",
    "duan": "短",
    "dui": "对",
    "dun": "顿",
    "duo": "多",
    "e": "额",
    "ei": "诶",
    "en": "恩",
    "eng": "嗯",
    "er": "儿",
    "fa": "发",
    "fan": "饭",
    "fang": "放",
    "fei": "飞",
    "fen": "分",
    "feng": "风",
    "fo": "佛",
    "fou": "否",
    "fu": "富",
    "ga": "嘎",
    "gai": "该",
    "gan": "干",
    "gang": "港",
    "gao": "高",
    "ge": "歌",
    "gei": "给",
    "gen": "根",
    "geng": "更",
    "gong": "工",
    "gou": "狗",
    "gu": "菇",
    "gua": "瓜",
    "guai": "怪",
    "guan": "观",
    "guang": "光",
    "gui": "贵",
    "gun": "滚",
    "guo": "国",
    "ha": "哈",
    "hai": "海",
    "han": "韩",
    "hang": "行",
    "hao": "好",
    "he": "和",
    "hei": "黑",
    "hen": "很",
    "heng": "横",
    "hong": "红",
    "hou": "后",
    "hu": "虎",
    "hua": "华",
    "huai": "怀",
    "huan": "幻",
    "huang": "黄",
    "hui": "回",
    "hun": "混",
    "huo": "活",
    "ji": "集",
    "jia": "家",
    "jian": "荐",
    "jiang": "将",
    "jiao": "叫",
    "jie": "结",
    "jin": "金",
    "jing": "精",
    "jiong": "窘",
    "jiu": "旧",
    "ju": "剧",
    "juan": "卷",
    "jue": "决",
    "jun": "军",
    "ka": "卡",
    "kai": "开",
    "kan": "看",
    "kang": "抗",
    "kao": "靠",
    "ke": "科",
    "kei": "尅",
    "ken": "肯",
    "keng": "坑",
    "kong": "恐",
    "kou": "口",
    "ku": "库",
    "kua": "夸",
    "kuai": "快",
    "kuan": "款",
    "kuang": "框",
    "kui": "亏",
    "kun": "困",
    "kuo": "扩",
    "la": "拉",
    "lai": "来",
    "lan": "蓝",
    "lang": "狼",
    "lao": "老",
    "le": "乐",
    "lei": "类",
    "leng": "冷",
    "li": "历",
    "lia": "俩",
    "lian": "连",
    "liang": "两",
    "liao": "料",
    "lie": "列",
    "lin": "林",
    "ling": "领",
    "liu": "六",
    "long": "龙",
    "lou": "楼",
    "lu": "录",
    "luan": "乱",
    "lue": "略",
    "lun": "论",
    "luo": "络",
    "lv": "绿",
    "ma": "妈",
    "mai": "麦",
    "man": "漫",
    "mang": "忙",
    "mao": "冒",
    "me": "么",
    "mei": "美",
    "men": "门",
    "meng": "梦",
    "mi": "迷",
    "mian": "免",
    "miao": "妙",
    "mie": "灭",
    "min": "民",
    "ming": "名",
    "miu": "谬",
    "mo": "蘑",
    "mou": "某",
    "mu": "牧",
    "na": "那",
    "nai": "奈",
    "nan": "难",
    "nang": "囊",
    "nao": "脑",
    "ne": "呢",
    "nei": "内",
    "nen": "嫩",
    "neng": "能",
    "ni": "你",
    "nian": "年",
    "niang": "娘",
    "niao": "鸟",
    "nie": "捏",
    "nin": "您",
    "ning": "宁",
    "niu": "牛",
    "nong": "农",
    "nou": "耨",
    "nu": "努",
    "nuan": "暖",
    "nue": "虐",
    "nuo": "诺",
    "nv": "女",
    "o": "哦",
    "ou": "欧",
    "pa": "怕",
    "pai": "牌",
    "pan": "盘",
    "pang": "旁",
    "pao": "泡",
    "pei": "配",
    "pen": "盆",
    "peng": "朋",
    "pi": "批",
    "pian": "片",
    "piao": "票",
    "pie": "撇",
    "pin": "频",
    "ping": "平",
    "po": "破",
    "pou": "剖",
    "pu": "普",
    "qi": "奇",
    "qia": "恰",
    "qian": "千",
    "qiang": "强",
    "qiao": "桥",
    "qie": "切",
    "qin": "亲",
    "qing": "情",
    "qiong": "穷",
    "qiu": "球",
    "qu": "区",
    "quan": "全",
    "que": "确",
    "qun": "群",
    "ran": "然",
    "rang": "让",
    "rao": "绕",
    "re": "热",
    "ren": "人",
    "reng": "扔",
    "ri": "日",
    "rong": "荣",
    "rou": "肉",
    "ru": "如",
    "ruan": "软",
    "rui": "瑞",
    "run": "润",
    "ruo": "若",
    "sa": "撒",
    "sai": "赛",
    "san": "三",
    "sang": "桑",
    "sao": "扫",
    "se": "色",
    "sen": "森",
    "seng": "僧",
    "sha": "沙",
    "shai": "晒",
    "shan": "山",
    "shang": "上",
    "shao": "少",
    "she": "社",
    "shei": "谁",
    "shen": "神",
    "sheng": "生",
    "shi": "视",
    "shou": "首",
    "shu": "书",
    "shua": "刷",
    "shuai": "帅",
    "shuan": "栓",
    "shuang": "双",
    "shui": "水",
    "shun": "顺",
    "shuo": "说",
    "si": "四",
    "song": "悚",
    "sou": "搜",
    "su": "苏",
    "suan": "算",
    "sui": "随",
    "sun": "孙",
    "suo": "索",
    "ta": "他",
    "tai": "泰",
    "tan": "坛",
    "tang": "堂",
    "tao": "桃",
    "te": "特",
    "teng": "腾",
    "ti": "体",
    "tian": "田",
    "tiao": "条",
    "tie": "铁",
    "ting": "庭",
    "tong": "童",
    "tou": "头",
    "tu": "图",
    "tuan": "团",
    "tui": "推",
    "tun": "吞",
    "tuo": "托",
    "wa": "瓦",
    "wai": "外",
    "wan": "完",
    "wang": "网",
    "wei": "为",
    "wen": "文",
    "weng": "翁",
    "wo": "我",
    "wu": "屋",
    "xi": "喜",
    "xia": "侠",
    "xian": "线",
    "xiang": "像",
    "xiao": "小",
    "xie": "谢",
    "xin": "新",
    "xing": "星",
    "xiong": "兄",
    "xiu": "秀",
    "xu": "许",
    "xuan": "选",
    "xue": "学",
    "xun": "寻",
    "ya": "呀",
    "yan": "言",
    "yang": "阳",
    "yao": "要",
    "ye": "页",
    "yi": "艺",
    "yin": "音",
    "ying": "影",
    "yo": "哟",
    "yong": "用",
    "you": "友",
    "yu": "语",
    "yuan": "院",
    "yue": "乐",
    "yun": "云",
    "za": "杂",
    "zai": "在",
    "zan": "赞",
    "zang": "脏",
    "zao": "造",
    "ze": "则",
    "zei": "贼",
    "zen": "怎",
    "zeng": "增",
    "zha": "扎",
    "zhai": "摘",
    "zhan": "战",
    "zhang": "张",
    "zhao": "找",
    "zhe": "这",
    "zhei": "这",
    "zhen": "珍",
    "zheng": "争",
    "zhi": "之",
    "zhong": "中",
    "zhou": "周",
    "zhu": "主",
    "zhua": "抓",
    "zhuai": "拽",
    "zhuan": "传",
    "zhuang": "庄",
    "zhui": "追",
    "zhun": "准",
    "zhuo": "桌",
    "zi": "子",
    "zong": "综",
    "zou": "走",
    "zu": "族",
    "zuan": "钻",
    "zui": "最",
    "zun": "尊",
    "zuo": "作",
}

# 有效拼音音节表（用于切分）
_PINYIN_SYLLABLES = frozenset([
    "a", "ai", "an", "ang", "ao", "ba", "bai", "ban", "bang", "bao", "bei", "ben",
    "beng", "bi", "bian", "biao", "bie", "bin", "bing", "bo", "bu", "ca", "cai", "can",
    "cang", "cao", "ce", "cen", "ceng", "cha", "chai", "chan", "chang", "chao", "che", "chen",
    "cheng", "chi", "chong", "chou", "chu", "chuai", "chuan", "chuang", "chui", "chun", "chuo", "ci",
    "cong", "cou", "cu", "cuan", "cui", "cun", "cuo", "da", "dai", "dan", "dang", "dao",
    "de", "dei", "den", "deng", "di", "dian", "diao", "die", "ding", "diu", "dong", "dou",
    "du", "duan", "dui", "dun", "duo", "e", "ei", "en", "eng", "er", "fa", "fan",
    "fang", "fei", "fen", "feng", "fo", "fou", "fu", "ga", "gai", "gan", "gang", "gao",
    "ge", "gei", "gen", "geng", "gong", "gou", "gu", "gua", "guai", "guan", "guang", "gui",
    "gun", "guo", "ha", "hai", "han", "hang", "hao", "he", "hei", "hen", "heng", "hong",
    "hou", "hu", "hua", "huai", "huan", "huang", "hui", "hun", "huo", "ji", "jia", "jian",
    "jiang", "jiao", "jie", "jin", "jing", "jiong", "jiu", "ju", "juan", "jue", "jun", "ka",
    "kai", "kan", "kang", "kao", "ke", "kei", "ken", "keng", "kong", "kou", "ku", "kua",
    "kuai", "kuan", "kuang", "kui", "kun", "kuo", "la", "lai", "lan", "lang", "lao", "le",
    "lei", "leng", "li", "lia", "lian", "liang", "liao", "lie", "lin", "ling", "liu", "long",
    "lou", "lu", "luan", "lue", "lun", "luo", "lv", "ma", "mai", "man", "mang", "mao",
    "me", "mei", "men", "meng", "mi", "mian", "miao", "mie", "min", "ming", "miu", "mo",
    "mou", "mu", "na", "nai", "nan", "nang", "nao", "ne", "nei", "nen", "neng", "ni",
    "nian", "niang", "niao", "nie", "nin", "ning", "niu", "nong", "nou", "nu", "nuan", "nue",
    "nuo", "nv", "o", "ou", "pa", "pai", "pan", "pang", "pao", "pei", "pen", "peng",
    "pi", "pian", "piao", "pie", "pin", "ping", "po", "pou", "pu", "qi", "qia", "qian",
    "qiang", "qiao", "qie", "qin", "qing", "qiong", "qiu", "qu", "quan", "que", "qun", "ran",
    "rang", "rao", "re", "ren", "reng", "ri", "rong", "rou", "ru", "ruan", "rui", "run",
    "ruo", "sa", "sai", "san", "sang", "sao", "se", "sen", "seng", "sha", "shai", "shan",
    "shang", "shao", "she", "shei", "shen", "sheng", "shi", "shou", "shu", "shua", "shuai", "shuan",
    "shuang", "shui", "shun", "shuo", "si", "song", "sou", "su", "suan", "sui", "sun", "suo",
    "ta", "tai", "tan", "tang", "tao", "te", "teng", "ti", "tian", "tiao", "tie", "ting",
    "tong", "tou", "tu", "tuan", "tui", "tun", "tuo", "wa", "wai", "wan", "wang", "wei",
    "wen", "weng", "wo", "wu", "xi", "xia", "xian", "xiang", "xiao", "xie", "xin", "xing",
    "xiong", "xiu", "xu", "xuan", "xue", "xun", "ya", "yan", "yang", "yao", "ye", "yi",
    "yin", "ying", "yo", "yong", "you", "yu", "yuan", "yue", "yun", "za", "zai", "zan",
    "zang", "zao", "ze", "zei", "zen", "zeng", "zha", "zhai", "zhan", "zhang", "zhao", "zhe",
    "zhei", "zhen", "zheng", "zhi", "zhong", "zhou", "zhu", "zhua", "zhuai", "zhuan", "zhuang", "zhui",
    "zhun", "zhuo", "zi", "zong", "zou", "zu", "zuan", "zui", "zun", "zuo",
])

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def log(msg):
    print("[check] {}".format(msg), flush=True)


def scan_py():
    files = []
    if not os.path.isdir(PYY_DIR):
        return files
    for dirpath, _dirs, names in os.walk(PYY_DIR):
        for n in names:
            if not n.lower().endswith(".py"):
                continue
            base = os.path.splitext(n)[0]
            if base.strip().lower() in SCAN_EXCLUDE:
                continue
            files.append(os.path.join(dirpath, n))
    return sorted(files)


def read_text(path):
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def get_code_text(path):
    text = read_text(path)
    if text is None:
        return None
    t = text.strip()
    if "\n" not in t and len(t) > 100:
        if "class " not in t and "def " not in t and "import " not in t:
            if PY_KEY is not None:
                try:
                    import base64
                    base64.b64decode(t)
                    try:
                        from Crypto.Cipher import AES
                        raw = base64.b64decode(t)
                        iv, ct = raw[:16], raw[16:]
                        p = AES.new(PY_KEY, AES.MODE_CBC, iv).decrypt(ct)
                        return p[:-p[-1]].decode("utf-8")
                    except Exception:
                        pass
                except Exception:
                    pass
    return text


def is_encrypted_file(path):
    text = read_text(path)
    if not text:
        return False
    t = text.strip()
    if "\n" in t or len(t) < 100:
        return False
    if "class " in t or "def " in t or "import " in t:
        return False
    return True


def extract_urls(path):
    text = get_code_text(path)
    if not text:
        return []
    raw = re.findall(r'https?://[^\s\'"<>\\]+', text)
    urls = []
    for u in raw:
        u = u.rstrip('.,;!?)\'"')
        if len(u) > 10:
            urls.append(u)
    seen = set()
    uniq = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def date_variants(url):
    variants = [url]
    if re.search(r"\d{8}", url):
        for d in (datetime.date.today(),
                  datetime.date.today() - datetime.timedelta(days=1)):
            nd = re.sub(r"\d{8}", d.strftime("%Y%m%d"), url)
            if nd != url and nd not in variants:
                variants.append(nd)
    return variants


def curl_check(url):
    try:
        out = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w",
             "%{http_code} %{num_redirects} %{url_effective}",
             "--max-time", str(URL_TIMEOUT), "-L",
             "-A", UA["User-Agent"], url],
            capture_output=True, text=True, timeout=URL_TIMEOUT + 5)
        parts = out.stdout.strip().split(" ", 2)
        code = int(parts[0]) if parts and parts[0].isdigit() else 0
        n_red = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        final = parts[2] if len(parts) > 2 else url
        return code, n_red, final
    except Exception:
        return 0, 0, url


def check_one_url(url):
    import requests
    tried = []
    try:
        r = requests.head(url, timeout=URL_TIMEOUT, allow_redirects=True, headers=UA)
        if r.status_code < 400:
            return "alive", r.status_code, len(r.history), str(r.url)
        tried.append((r.status_code, len(r.history), str(r.url)))
    except Exception:
        pass
    try:
        r = requests.get(url, timeout=URL_TIMEOUT, allow_redirects=True, headers=UA)
        if r.status_code < 400:
            return "alive", r.status_code, len(r.history), str(r.url)
        tried.append((r.status_code, len(r.history), str(r.url)))
    except Exception:
        pass
    code, n_red, final = curl_check(url)
    if code < 400 and code >= 200:
        return "alive", code, n_red, final
    tried.append((code, n_red, final))
    for c, nr, f in tried:
        if c in (403, 429):
            return "uncertain", c, nr, f
    c, nr, f = tried[-1] if tried else (0, 0, url)
    return "dead", c, nr, f


def url_check(path):
    urls = extract_urls(path)
    if not urls:
        return False, "未找到网址"
    seen_domains = set()
    checked = 0
    uncertain = []
    last_err = ""
    for url in urls:
        try:
            domain = urlparse(url).netloc.lower()
        except Exception:
            continue
        if not domain or domain in seen_domains:
            continue
        seen_domains.add(domain)
        checked += 1
        if checked > MAX_URLS_PER_FILE:
            break
        for variant in date_variants(url):
            st, code, n_red, final = check_one_url(variant)
            if st == "alive":
                info = "有效({}".format(code)
                if n_red > 0:
                    info += ",跳转{}次".format(n_red)
                if variant != url:
                    info += ",日期轮换域名命中"
                info += ")"
                return True, info
            if st == "uncertain":
                uncertain.append("HTTP {}".format(code))
            else:
                last_err = "HTTP {}".format(code) if code else "连接失败"
    if uncertain:
        note = "疑似被拦截({})，已保留".format(",".join(sorted(set(uncertain))))
        log("  保留: {} ({})".format(os.path.basename(path), note))
        return True, note
    return False, "网址均失效({})".format(last_err)


def norm_api(a):
    a = (a or "").strip()
    while a.startswith("./"):
        a = a[2:]
    return a


ENC_LOADER = "http://xn--oev29b.top/files/py/loader.py"
ENC_BASE = "http://xn--oev29b.top/files/enc"


def enc_site_of(entry):
    try:
        ext = json.loads(entry.get("ext") or "{}")
        return ext.get("site") or ""
    except Exception:
        return ""


def main():
    t0 = time.time()
    files = scan_py()
    log("扫描到 {} 个 py 文件".format(len(files)))

    enc_files = [fp for fp in files if is_encrypted_file(fp)]
    normal_files = [fp for fp in files if fp not in enc_files]

    checkable_enc = []
    uncheckable_enc = []
    for fp in enc_files:
        dec = get_code_text(fp)
        t = (read_text(fp) or "").strip()
        if dec is not None and dec.strip() != t:
            checkable_enc.append(fp)
        else:
            uncheckable_enc.append(fp)
    if enc_files:
        log("加密文件 {} 个（可解密检测 {}，直接添加 {}）".format(len(enc_files), len(checkable_enc), len(uncheckable_enc)))

    to_check = normal_files + checkable_enc
    ok_files = []
    dead = []
    with ThreadPoolExecutor(max_workers=DEEP_WORKERS) as ex:
        fut_map = {ex.submit(url_check, fp): fp for fp in to_check}
        for fut in as_completed(fut_map):
            fp = fut_map[fut]
            try:
                ok, reason = fut.result(timeout=URL_TIMEOUT * MAX_URLS_PER_FILE * 3 + 30)
            except Exception:
                ok, reason = False, "检测超时"
            name = os.path.basename(fp)
            if ok:
                ok_files.append(fp)
            else:
                dead.append((name, reason))
                log("  死源: {} ({})".format(name, reason))
    deleted = 0
    for name, reason in dead:
        fp = os.path.join(PYY_DIR, name)
        for cand in to_check:
            if os.path.basename(cand) == name:
                fp = cand
                break
        try:
            os.remove(fp)
            deleted += 1
            log("  已删除: {}".format(name))
        except Exception as e:
            log("  删除失败: {} ({})".format(name, e))
    log("存活 {} 个，死源 {} 个（已删 {}），加密直接添加 {} 个".format(len(ok_files), len(dead), deleted, len(uncheckable_enc)))

    cfg = None
    if os.path.isfile(API_JSON):
        try:
            with open(API_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = None
    if not isinstance(cfg, dict):
        cfg = {}
    sites = cfg.get("sites")
    if not isinstance(sites, list):
        sites = []

    file_apis = {}
    for fp in ok_files:
        if fp not in normal_files:
            continue
        rel = os.path.relpath(fp, ROOT).replace(os.sep, "/")
        api = "./" + rel
        file_apis[norm_api(api)] = api

    kept = []
    kept_enc = []
    others = []
    dropped = 0
    ok_normal_set = set(os.path.normpath(p) for p in ok_files if p in normal_files)
    ok_enc_set = set(os.path.normpath(p) for p in ok_files if p in checkable_enc)
    enc_alive = set(os.path.basename(fp)[:-3] if os.path.basename(fp).endswith(".py") else os.path.basename(fp) for fp in checkable_enc if os.path.normpath(fp) in ok_enc_set)
    enc_alive |= set(os.path.basename(fp)[:-3] if os.path.basename(fp).endswith(".py") else os.path.basename(fp) for fp in uncheckable_enc)
    for s in sites:
        if not isinstance(s, dict):
            others.append(s)
            continue
        api = (s.get("api") or "").strip()
        if api == ENC_LOADER:
            site = enc_site_of(s)
            if site in enc_alive:
                kept_enc.append(s)
            else:
                dropped += 1
            continue
        na = norm_api(api)
        if na.endswith(".py") and na:
            fp = os.path.normpath(os.path.join(ROOT, na))
            if fp in ok_normal_set:
                kept.append(s)
            else:
                dropped += 1
        else:
            others.append(s)

    taken = set()
    for s in kept + kept_enc + others:
        if isinstance(s, dict):
            if s.get("name"):
                taken.add(s["name"])
            if s.get("key"):
                taken.add(s["key"])
    fengdou_counter = [1]

    used = set(norm_api(s.get("api")) for s in kept)
    added = []
    for na in sorted(file_apis):
        if na in used:
            continue
        fn = os.path.basename(na)
        name = fn[:-3] if fn.endswith(".py") else fn
        added.append({
            "key": name,
            "name": name,
            "type": 3,
            "searchable": 1,
            "quickSearch": 1,
            "api": file_apis[na],
        })

    used_enc = set(enc_site_of(s) for s in kept_enc)
    added_enc = []
    enc_to_add = [fp for fp in checkable_enc if os.path.normpath(fp) in ok_enc_set] + uncheckable_enc
    for fp in sorted(enc_to_add):
        fn = os.path.basename(fp)
        site = fn[:-3] if fn.endswith(".py") else fn
        if site in used_enc:
            continue
        cn_name, fengdou_counter = make_cn_name(fn, taken, fengdou_counter)
        if not cn_name:
            continue
        taken.add(cn_name)
        taken.add("💕 {} 💕 ".format(cn_name))
        added_enc.append({
            "key": site,
            "name": "💕 {} 💕 ".format(cn_name),
            "type": 3,
            "api": ENC_LOADER,
            "ext": json.dumps({"site": site, "base": ENC_BASE, "name": cn_name}, ensure_ascii=False),
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1,
        })

    cfg["sites"] = kept + added + kept_enc + added_enc + others

    with open(API_JSON, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

    log("生成完成: 共 {} 条 (新增 {}, 保留 {}, 加密新增 {}, 加密保留 {}, 清理 {}, 删除文件 {}), 耗时 {:.1f}s".format(
        len(cfg["sites"]), len(added), len(kept), len(added_enc), len(kept_enc), dropped, deleted, time.time() - t0))

    with open(os.path.join(ROOT, "check_report.txt"), "w", encoding="utf-8") as f:
        f.write("检测时间: {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        f.write("共 {} 条 (新增 {}, 保留 {}, 加密新增 {}, 加密保留 {}, 清理 {}, 删除文件 {})\n".format(
            len(cfg["sites"]), len(added), len(kept), len(added_enc), len(kept_enc), dropped, deleted))
        f.write("死源 {} 个:\n".format(len(dead)))
        for n, r in sorted(dead):
            f.write("  - {} ({})\n".format(n, r))


if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    main()
