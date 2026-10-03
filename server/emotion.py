# -*- coding: utf-8 -*-
"""情绪检测：先判断明确语义，再处理哭腔/表情，避免亲密语境被误判为悲伤。"""

T1 = {
    "😤": "scolded", "😠": "scolded", "😡": "scolded",
    "😭": "sad", "😢": "sad", "🥺": "sad",
    "😍": "intimate", "😘": "intimate", "❤": "intimate", "🥰": "intimate",
    "😱": "startled", "😨": "startled",
    "🤩": "excited", "🎉": "excited",
}

# 明确语义优先级：痛苦/悲伤只有在真正的负面语境中成立。
SAD_WORDS = ["难过", "伤心", "失落", "痛苦", "绝望", "崩溃", "心碎", "委屈死了"]
AROUSED_WORDS = ["想要", "好想", "欲望", "湿", "硬", "顶", "进来", "操", "干我", "要了", "发情", "做", "性爱", "亲密"]
INTIMATE_WORDS = ["抱", "亲", "爱你", "想你", "要你", "老公", "daddy", "Daddy", "亲亲", "抱抱", "宝贝", "亲爱的", "吻", "摸", "碰", "舔", "咬"]
CRY_WORDS = ["呜呜", "呜呜呜", "哭哭", "哭了", "哭着", "哭腔", "求饶", "抽泣", "啜泣"]

T2 = [
    (["开心", "高兴", "好耶"], "happy"),
    (["生气", "讨厌", "烦"], "scolded"),
    (["紧张", "害怕", "怕"], "nervous"),
    (["专注", "认真", "干活"], "focused"),
]


def detect_emotion(text):
    text = text or ""
    # 明确悲伤语义优先于单纯哭腔。
    if any(w in text for w in SAD_WORDS):
        return "sad"

    # 哭声/哭腔不是情绪本身：在亲密或性语境中，保留愉悦、兴奋的状态。
    has_cry = any(w in text for w in CRY_WORDS)
    has_aroused = any(w in text for w in AROUSED_WORDS)
    has_intimate = any(w in text for w in INTIMATE_WORDS)
    if has_cry and (has_aroused or has_intimate):
        return "aroused" if has_aroused else "intimate"

    # 明确欲望/性爱语义压过哭脸表情。
    if has_aroused:
        return "aroused"
    if has_intimate:
        return "intimate"

    for sym, emo in T1.items():
        if sym in text:
            return emo
    for kws, emo in T2:
        for kw in kws:
            idx = text.find(kw)
            if idx >= 0:
                window = text[max(0, idx - 4):idx]
                if "不" in window or "没" in window:
                    continue
                return emo
    return None
