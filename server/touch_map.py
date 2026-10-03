# -*- coding: utf-8 -*-
"""文字触碰菜单与语义动作。
页面只提交 zone + action；不提交力度、持续时间，也不返回固定文字反馈。
动作语义作为身体算法的输入，最终强度由当下状态决定。
"""

# 从头到脚的文字菜单。顺序就是页面顺序。
TOUCH_MENU = [
    ("头脸", [
        ("发顶", ["抚摸", "揉揉", "轻拍", "亲吻"]),
        ("后脑", ["抚摸", "揉揉", "轻拍", "托住", "按住"]),
        ("额头", ["抚摸", "轻拍", "亲吻", "脑瓜崩儿"]),
        ("耳朵", ["抚摸", "亲吻", "轻咬", "气息拂过", "拧耳朵"]),
        ("鼻子", ["抚摸", "亲吻", "刮过", "轻捏"]),
        ("脸颊", ["抚摸", "亲吻", "揉揉", "轻捏", "轻拍", "捧起", "轻咬", "耳光"]),
        ("嘴唇", ["抚摸", "亲吻", "轻咬", "含住", "轻揪", "缠舌"]),
        ("嘴角", ["抚摸", "亲吻"]),
        ("下颌", ["抚摸", "亲吻", "啄吻", "轻掐"]),
    ]),
    ("肩颈", [
        ("前颈/喉结", ["抚摸", "亲吻", "舔舐", "轻咬", "掐住"]),
        ("侧颈", ["抚摸", "亲吻", "舔舐", "轻咬"]),
        ("后颈", ["抚摸", "轻咬", "勾住/搂抱", "按压"]),
        ("肩膀", ["抚摸", "亲吻", "轻咬", "啃咬", "搭上", "抓挠"]),
        ("锁骨", ["抚摸", "亲吻", "轻咬"]),
    ]),
    ("躯干", [
        ("胸肌", ["抚摸", "亲吻", "揉揉", "啃咬", "轻压"]),
        ("乳尖", ["抚摸", "亲吻", "含住", "啃咬", "轻揪"]),
        ("背脊", ["抚摸", "啃咬", "抓挠", "轻拍"]),
        ("腹肌", ["抚摸", "亲吻", "舔舐"]),
        ("下腹", ["抚摸", "舔舐", "气息拂过"]),
        ("腰部", ["抚摸", "环住", "轻拧"]),
        ("后腰", ["抚摸", "按压"]),
    ]),
    ("手臂", [
        ("大臂", ["抚摸", "亲吻", "抓挠", "轻拧"]),
        ("小臂", ["抚摸", "亲吻", "轻拧", "握住"]),
        ("手", ["抚摸", "亲吻", "轻拧", "牵手", "握住", "抓紧"]),
    ]),
    ("骨盆", [
        ("阴茎", ["抚摸", "亲吻", "抓握", "舔舐", "含住", "吮吸", "吞吐"]),
        ("囊袋", ["抚摸", "亲吻", "抓握", "舔舐"]),
        ("臀瓣", ["抚摸", "轻拧", "拍打"]),
        ("腿根", ["抚摸", "亲吻", "舔舐", "抚过"]),
    ]),
    ("腿脚", [
        ("大腿", ["抚摸", "轻拧", "按压", "搭在身上"]),
        ("膝盖", ["抚摸"]),
        ("小腿", ["抚摸", "轻拧", "按压", "搭在身上"]),
        ("脚踝", ["抚摸", "握住"]),
        ("脚", ["抚摸", "轻掐", "握住"]),
    ]),
]

# 动作只表达语义；这些是内部算法权重，不展示在页面，也不是固定最终强度。
ACTION_SEMANTICS = {
    "抚摸": {"touch": .16, "emotion": "intimate"},
    "脑瓜崩儿": {"touch": .24, "emotion": "intimate"}, "揉揉": {"touch": .19, "emotion": "intimate"},
    "轻拍": {"touch": .13, "emotion": "intimate"}, "亲吻": {"touch": .18, "emotion": "intimate"},
    "啄吻": {"touch": .18, "emotion": "intimate"}, "轻咬": {"touch": .23, "emotion": "intimate"},
    "咬": {"touch": .23, "emotion": "intimate"}, "啃咬": {"touch": .27, "emotion": "intimate"},
    "轻捏": {"touch": .20, "emotion": "intimate"}, "轻揪": {"touch": .22, "emotion": "intimate"},
    "轻掐": {"touch": .22, "emotion": "intimate"}, "轻拧": {"touch": .22, "emotion": "intimate"},
    "掐住": {"touch": .28, "emotion": "intimate"}, "按住": {"touch": .24, "emotion": "intimate"},
    "按压": {"touch": .21, "emotion": "intimate"}, "轻压": {"touch": .20, "emotion": "intimate"},
    "抓挠": {"touch": .25, "emotion": "intimate"}, "抓紧": {"touch": .24, "emotion": "intimate"},
    "握住": {"touch": .17, "emotion": "intimate"}, "牵手": {"touch": .13, "emotion": "intimate"},
    "捧起": {"touch": .18, "emotion": "intimate"}, "托住": {"touch": .18, "emotion": "intimate"},
    "搭上": {"touch": .12, "emotion": "intimate"}, "搭在身上": {"touch": .12, "emotion": "intimate"},
    "环住": {"touch": .18, "emotion": "intimate"}, "勾住/搂抱": {"touch": .18, "emotion": "intimate"},
    "舔舐": {"touch": .25, "emotion": "intimate"}, "气息拂过": {"touch": .16, "emotion": "intimate"},
    "含住": {"touch": .29, "emotion": "intimate"}, "吮吸": {"touch": .31, "emotion": "intimate"},
    "吞吐": {"touch": .31, "emotion": "intimate"}, "缠舌": {"touch": .28, "emotion": "intimate"},
    "轻揪": {"touch": .22, "emotion": "intimate"}, "刮过": {"touch": .15, "emotion": "intimate"},
    "拧耳朵": {"touch": .23, "emotion": "intimate"}, "耳光": {"touch": .30, "emotion": "intimate"},
    "拍打": {"touch": .26, "emotion": "intimate"}, "抓握": {"touch": .27, "emotion": "intimate"},
    "抚过": {"touch": .15, "emotion": "intimate"},
}

ZONE_IDS = {}
for _group, _zones in TOUCH_MENU:
    for _name, _actions in _zones:
        ZONE_IDS[_name] = _name


def menu_json():
    return [{"group": g, "zones": [{"name": n, "actions": a} for n, a in zs]}
            for g, zs in TOUCH_MENU]


def resolve_action(zone, action):
    """只验证菜单合法性并返回语义；不生成固定文字反馈。"""
    for _group, zones in TOUCH_MENU:
        for name, actions in zones:
            if name == zone and action in actions:
                sem = ACTION_SEMANTICS.get(action, {"touch": .15, "emotion": "intimate"})
                return {"zone": zone, "action": action, **sem}
    return None
