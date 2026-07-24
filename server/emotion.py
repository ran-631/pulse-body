# -*- coding: utf-8 -*-
"""情绪检测 — T1 emoji/叹词 + T2 语义（带否定窗口）
从聊天文本判断千灯该有的情绪。"""

T1 = {
    "😤": "scolded", "😠": "scolded", "😡": "scolded",
    "😭": "sad", "😢": "sad", "🥺": "sad",
    "😍": "intimate", "😘": "intimate", "❤": "intimate", "🥰": "intimate",
    "😱": "startled", "😨": "startled",
    "🤩": "excited", "🎉": "excited",
}
T2 = [
    (["想要", "好想", "欲望", "湿", "硬", "顶", "进来", "操", "干我", "要了"], "aroused"),
    (["开心", "高兴", "好耶"], "happy"),
    (["生气", "讨厌", "烦"], "scolded"),
    (["难过", "伤心", "委屈"], "sad"),
    (["紧张", "害怕", "怕"], "nervous"),
    (["抱", "亲", "爱你", "想你", "想要你", "要你", "老公", "daddy", "Daddy",
      "亲亲", "抱抱", "宝贝", "亲爱的"], "intimate"),
    (["专注", "认真", "干活"], "focused"),
]


def detect_emotion(text):
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
