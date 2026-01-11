#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建完整的教师数据库
按照原文顺序：管理部 → 理论组 → 声乐组 → 器乐组 → 舞蹈部
"""

import json

teachers = []

# ============ 管理部 (6人) ============
teachers.extend([
    {
        "id": "001_chen_tao",
        "name": "陈涛",
        "department": "管理部",
        "position": "创始人",
        "shortSummary": "青年男中音，中国传统文化促进会青年歌唱家学术委员会委员",
        "photo": "photos/chen_tao.jpg",
        "bio": "陈涛，创始人。青年男中音，曾就职兰州大剧院并长期从事声乐演出与教学。中国传统文化促进会青年歌唱家学术委员会委员，甘肃省音乐家协会会员；曾担任中Sin国际音乐比赛（新加坡）总决赛评委。毕业于兰州大学艺术学院音乐表演专业，师从四川音乐学院男中音歌唱家郭江滨副教授；此前先后师从兰州大学石大勇副教授和天津音乐学院青年教师、男高音歌唱家杨博老师。\n\n陈涛先生参与并主演过多部歌剧与大型交响合唱作品，包括《茶花女》（饰演男爵 Barone）、《波西米亚人》（饰军官）、《乡村骑士》、《图兰朵》（传令官）、《卡门》，以及中央音乐学院原创联套歌剧《山海经·奔月》、兰州大剧院原创民族歌剧《西风烈》（饰蒋英超）等。此外参与贝多芬《第九交响曲》终章《欢乐颂》、马勒《第二》《第八交响曲》、福雷《安魂曲》等重要作品的演出。曾受邀参加国家大剧院与国内外多个重要音乐节及纪念活动演出，并多次在《黄河大合唱》中担任领唱。",
        "achievements": [
            "2025年获"青歌新人"称号",
            "甘肃省第三届与第四届声乐大赛（美声唱法）青年组三等奖",
            "第十届、第十一届、第十五届金钟奖甘肃赛区（美声唱法）三等奖",
            "甘肃省首届"思路之星·我的舞台梦"美声唱法大学组第一名"
        ]
    },
    {
        "id": "002_su_haipeng",
        "name": "苏海鹏",
        "department": "管理部",
        "position": "创始人",
        "shortSummary": "润德艺术学校创办者，12年以上艺考教学与管理经验",
        "photo": "photos/su_haipeng.jpg",
        "bio": "苏海鹏，创始人。兰州市润德艺术学校创办者之一，长期从事音乐艺考教学与学校管理工作。担任兰州市安宁区民办教育协会理事，并为甘肃地区打击乐协会成员。拥有12年以上艺考教学与管理经验，培养学员近三千人，积累了丰富的教学与组织管理经验。\n\n教学理念上，苏老师坚持"严格管理、科学教学"的原则，重视视唱练耳等基础课程的系统教学。为提升教学与管理水平，多次前往西安、北京、上海等地学习先进的教育理念与教学方法。",
        "achievements": []
    },
    {
        "id": "003_wang_yu",
        "name": "王玉",
        "department": "管理部",
        "position": "校长",
        "shortSummary": "校长，视唱练耳教师，原兰州城市学院Fusion合唱团负责人",
        "photo": "photos/wang_yu.jpg",
        "bio": "王玉，校长。毕业于兰州城市学院，师从萧昱副教授并一直跟随学习。自2017年起从事视唱练耳教学，深受学生欢迎，工作态度认真负责。在校期间曾担任兰州城市学院Fusion合唱团负责人。\n\n演出经历：2018年随甘肃省歌剧院交响乐团参与大型交响乐《梦回敦煌》的排练并赴银川演出；2018年12月毕业实习汇报表演中于《歌剧魅影》中饰演魅影一角。",
        "achievements": []
    },
    {
        "id": "004_qi_junxia",
        "name": "祁军霞",
        "department": "管理部",
        "position": "财务总监",
        "shortSummary": "财务总监，中共党员，8年以上艺考培训与教学经验",
        "photo": "photos/qi_junxia.jpg",
        "bio": "祁军霞，财务总监，中共党员，音乐学学士。具有8年以上艺考培训与教学经验，参与过教材编写工作（如《高考基本乐理冲刺试卷》）。所带学生成绩优异，教学与管理受到同行与学生好评。",
        "achievements": []
    },
    {
        "id": "005_jing_xiangdong",
        "name": "景想东",
        "department": "管理部",
        "position": "财务主管",
        "shortSummary": "财务主管",
        "photo": "photos/jing_xiangdong.jpg",
        "bio": "景想东，财务主管。",
        "achievements": []
    },
    {
        "id": "006_su_haizhen",
        "name": "苏海震",
        "department": "管理部",
        "position": "后勤主管",
        "shortSummary": "后勤主管，为人耿直热情，关爱学生",
        "photo": "photos/su_haizhen.jpg",
        "bio": "苏海震，后勤主管。长期负责学校后勤保障工作，为人耿直、热情，关爱学生，工作踏实肯干，致力于提升后勤服务质量与效率。",
        "achievements": []
    }
])

# ============ 理论组 (3人 - 包含跨部门的苏海鹏、王玉) ============
teachers.extend([
    {
        "id": "007_su_haipeng_theory",
        "name": "苏海鹏",
        "department": "理论组",
        "position": "视唱练耳教师",
        "shortSummary": "视唱练耳教师，多次赴外学习先进教学方法",
        "photo": "photos/su_haipeng_theory.jpg",
        "bio": "苏海鹏，润德艺术学校创始人，兰州市安宁区民办教育协会理事，长期从事艺考教学与管理，视唱练耳教学能力突出并多次赴外学习先进教学方法。",
        "achievements": []
    },
    {
        "id": "008_wang_yu_theory",
        "name": "王玉",
        "department": "理论组",
        "position": "视唱练耳教师",
        "shortSummary": "视唱练耳教师，曾任合唱团负责人并有丰富舞台与教学经验",
        "photo": "photos/wang_yu_theory.jpg",
        "bio": "王玉，视唱练耳教师。毕业于兰州城市学院，师从萧昱副教授。自2017年起从事视唱练耳教学，曾任兰州城市学院Fusion合唱团负责人，参与大型交响乐《梦回敦煌》演出及《歌剧魅影》表演，具备丰富的舞台与教学经验。",
        "achievements": []
    },
    {
        "id": "009_qi_junxia_theory",
        "name": "祁军霞",
        "department": "理论组",
        "position": "乐理教师",
        "shortSummary": "乐理教师，参与教材编写，所带学生成绩优异",
        "photo": "photos/qi_junxia_theory.jpg",
        "bio": "祁军霞，乐理教师，中共党员，音乐学学士。具有8年以上艺考培训与教学经验，参与过教材编写工作（如《高考基本乐理冲刺试卷》）。所带学生成绩优异，教学与管理受到同行与学生好评。",
        "achievements": []
    }
])

# ============ 声乐组 (16人) ============
teachers.extend([
    {
        "id": "010_du_jigang",
        "name": "杜吉刚",
        "department": "声乐组",
        "position": "顾问",
        "shortSummary": "著名华裔男高音歌唱家，原中央歌剧院主要演员",
        "photo": "photos/du_jigang.jpg",
        "bio": "杜吉刚，著名华裔男高音歌唱家，曾为中央歌剧院主要演员并受聘为多项国家级与国际性声乐赛事的评委与专家。早年就读于中国人民解放军艺术学院音乐系，后在中央音乐学院及海外培训班深造；其艺术生涯横跨歌剧、音乐会与独唱会，曾代表国家赴海外参赛与交流，受国内外评论界高度评价。其演唱以技巧与舞台表现力著称。",
        "achievements": []
    },
    {
        "id": "011_guo_jiangbin",
        "name": "郭江滨",
        "department": "声乐组",
        "position": "顾问",
        "shortSummary": "男中音歌唱家，四川音乐学院声乐副教授",
        "photo": "photos/guo_jiangbin.jpg",
        "bio": "郭江滨，男中音歌唱家、四川音乐学院声乐副教授，担任多项国内外赛事评审并受聘为多所高校与机构的特聘教授与顾问。其教学成果显著，学生多次在国际赛事中获奖，个人亦获多项国际赛事奖励并多次担任重要评审职务。",
        "achievements": []
    },
    {
        "id": "012_shi_dayong",
        "name": "石大勇",
        "department": "声乐组",
        "position": "特聘教师",
        "shortSummary": "兰州大学艺术学院副教授",
        "photo": "photos/shi_dayong.jpg",
        "bio": "石大勇，兰州大学艺术学院副教授，长期从事声乐教学与演出工作。",
        "achievements": []
    },
    {
        "id": "013_yin_shenglin",
        "name": "尹胜麟",
        "department": "声乐组",
        "position": "特聘教师",
        "shortSummary": "博士、男高音，西北民族大学音乐学院副教授、硕士生导师",
        "photo": "photos/yin_shenglin.jpg",
        "bio": "尹胜麟，博士、男高音，西北民族大学音乐学院副教授、硕士生导师，具有国际化学习与教学背景，曾在意大利与波兰等地深造并获多项赛事奖励。",
        "achievements": []
    },
    {
        "id": "014_wang_juquan",
        "name": "王举全",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "从事声乐艺考教学逾20年，培养出多名获奖学生",
        "photo": "photos/wang_juquan.jpg",
        "bio": "王举全，从事声乐艺考教学逾20年，在教学过程中培养出多名在省级与国家级赛事中获奖的学生，教学经验丰富且注重基础训练。",
        "achievements": []
    },
    {
        "id": "015_sun_miao",
        "name": "孙淼",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "女高音，硕士研究生，甘肃省歌剧院青年演员",
        "photo": "photos/sun_miao.jpg",
        "bio": "孙淼，女高音，硕士研究生学历，甘肃省歌剧院青年演员，师从多位声乐与舞台表演教授，具备良好的舞台表演与声乐基础，曾在多项赛事中获奖。",
        "achievements": []
    },
    {
        "id": "016_chen_pudong",
        "name": "陈璞东",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "男高音，声乐博士，兼具学术与艺术实践经验",
        "photo": "photos/chen_pudong.jpg",
        "bio": "陈璞东，男高音，声乐博士，曾在多项国内外赛事中获奖并参与舞台创作与教学工作，兼具学术与艺术实践经验。",
        "achievements": []
    },
    {
        "id": "017_ma_xiyuan",
        "name": "马熙媛",
        "department": "声乐组",
        "position": "流行与音乐剧教师",
        "shortSummary": "音乐剧演员与流行歌手，参与多部音乐剧演出",
        "photo": "photos/ma_xiyuan.jpg",
        "bio": "马熙媛，音乐剧演员与流行歌手，参与多部音乐剧演出并发表原创作品，亦担任比赛评审与艺术指导工作。",
        "achievements": []
    },
    {
        "id": "018_zhao_xingcai",
        "name": "赵兴财",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "男高音，甘肃省音乐家协会会员，丰富的歌剧与合唱演出经验",
        "photo": "photos/zhao_xingcai.jpg",
        "bio": "赵兴财，男高音，甘肃省音乐家协会会员，长期参与歌剧与交响合唱演出，具备丰富的舞台与合唱演出经验。",
        "achievements": []
    },
    {
        "id": "019_wu_bin",
        "name": "吴彬",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "兰州音乐厅合唱团男高音，中国金融音乐家协会会员",
        "photo": "photos/wu_bin.jpg",
        "bio": "吴彬，兰州音乐厅合唱团男高音，中国金融音乐家协会会员。曾获第四届中国民族声乐敦煌奖西南赛区三等奖，参与四川电视台多项纪念与庆典演出，并参加环青海湖国际公路自行车赛闭幕式等大型活动演出。",
        "achievements": ["第四届中国民族声乐敦煌奖西南赛区三等奖"]
    },
    {
        "id": "020_yu_wei",
        "name": "于伟",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "硕士研究生，2017年加入兰州音乐厅合唱团",
        "photo": "photos/yu_wei.jpg",
        "bio": "于伟，硕士研究生学历，2017年加入兰州音乐厅合唱团，参与多部歌剧与大型晚会的排练与演出，曾参与2019年在北京人民大会堂举行的中华人民共和国成立70周年庆典演出排演，并在金钟奖甘肃赛区等赛事中获奖。",
        "achievements": []
    },
    {
        "id": "021_liu_peng",
        "name": "刘鹏",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "中共党员，参与多部歌剧与交响合唱作品演出",
        "photo": "photos/liu_peng.jpg",
        "bio": "刘鹏，中共党员，自加入合唱团以来参与多台歌剧与交响合唱作品演出，包括《波西米亚人》《图兰朵》《茶花女》《卡门》《乡村骑士》《奔月》以及大型音乐舞蹈史诗《奋斗吧·中华儿女》和《敦煌·慈悲颂》等巡演。",
        "achievements": []
    },
    {
        "id": "022_zhang_bo",
        "name": "张铂",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "兰州大剧院男中音，甘肃省音乐家协会会员",
        "photo": "photos/zhang_bo.jpg",
        "bio": "张铂，兰州大剧院男中音，甘肃省音乐家协会会员，兼任高校合唱团声乐指导。曾参与多部歌剧与交响合唱演出，并在教学方面取得多项学生升学与比赛成果。",
        "achievements": []
    },
    {
        "id": "023_tong_qianying",
        "name": "童倩影",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "抒情女高音，四川音乐学院歌剧系毕业，现于俄罗斯国立师范大学攻读硕士",
        "photo": "photos/tong_qianying.jpg",
        "bio": "童倩影，抒情女高音，毕业于四川音乐学院歌剧系，现于俄罗斯国立师范大学攻读硕士学位。多次在国内外竞赛与展演中获奖，获得包括新加坡中Sin国际比赛在内的多个荣誉称号。",
        "achievements": []
    },
    {
        "id": "024_huang_zijun",
        "name": "黄子俊",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "青年抒情男中音，四川音乐学院歌剧系本科，俄罗斯国立师范大学硕士",
        "photo": "photos/huang_zijun.jpg",
        "bio": "黄子俊，青年抒情男中音，本科毕业于四川音乐学院歌剧系，硕士就读于俄罗斯国立师范大学。参与国际音乐节与比赛并获多项荣誉，活跃于演出与教学两端。",
        "achievements": []
    },
    {
        "id": "025_ke_xia",
        "name": "柯夏",
        "department": "声乐组",
        "position": "声乐教师",
        "shortSummary": "青年抒情女高音，四川音乐学院歌剧系毕业并在俄罗斯深造",
        "photo": "photos/ke_xia.jpg",
        "bio": "柯夏，青年抒情女高音，毕业于四川音乐学院歌剧系并在俄罗斯深造。曾获新加坡中Sin国际音乐比赛歌剧组第一名及俄罗斯留声机国际比赛评审团特别奖等多项奖项，并多次参加全国性展演活动。",
        "achievements": [
            "新加坡中Sin国际音乐比赛歌剧组第一名",
            "俄罗斯留声机国际比赛评审团特别奖"
        ]
    }
])

print(f"✅ 当前进度：{len(teachers)} 人")
print("继续处理器乐组和舞蹈部...")

# 保存到文件
with open('data/teachers.json', 'w', encoding='utf-8') as f:
    json.dump(teachers, f, ensure_ascii=False, indent=2)

print(f"\n✅ 已保存 {len(teachers)} 位教师的信息")
