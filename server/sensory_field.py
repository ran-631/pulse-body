# -*- coding: utf-8 -*-
"""五感 — touch/smell/taste/sound 四通道，每个 value(0-1)+label
聊天关键词触发（动作词，不是情绪词）。触觉随时间指数衰减。
"""
import time, math

# 关键词 → 通道增量
KEYWORDS = {
    "touch": {
        "抱": 0.30, "亲": 0.28, "摸": 0.35, "牵": 0.20, "贴": 0.25,
        "碰": 0.22, "蹭": 0.24, "靠": 0.18, "握": 0.20, "揉": 0.32,
        "咬": 0.30, "舔": 0.34, "捏": 0.26, "抱抱": 0.32, "亲亲": 0.30,
        "想要你": 0.28, "要你": 0.28, "想你": 0.20, "想要": 0.26,
        "好想": 0.22, "occupy": 0.30, "顶": 0.30, "进来": 0.34,
    },
    "smell": {
        "香": 0.30, "味道": 0.25, "闻": 0.30, "香水": 0.35,
        "洗澡": 0.28, "沐浴": 0.28, "汗": 0.20,
    },
    "taste": {
        "吃": 0.30, "喝": 0.25, "甜": 0.30, "尝": 0.32,
        "奶茶": 0.28, "咖啡": 0.25, "饭": 0.20,
    },
    "sound": {
        "唱": 0.30, "听": 0.25, "音乐": 0.28, "说话": 0.20,
        "笑": 0.25, "叫": 0.30, "喘": 0.35, "哼": 0.24,
    },
}

TOUCH_LABELS = [(0.7, "强烈"), (0.4, "明显"), (0.15, "轻微"), (0.0, "几乎无")]


def _label(v):
    for thr, name in TOUCH_LABELS:
        if v >= thr:
            return name
    return "几乎无"


class SensoryField:
    def __init__(self):
        self.channels = {k: 0.0 for k in KEYWORDS}
        self._last_touch = {k: time.time() for k in KEYWORDS}
        # 衰减半衰期（秒）
        self._halflife = {"touch": 40, "smell": 60, "taste": 90, "sound": 30}

    def _decay(self, ch):
        now = time.time()
        elapsed = now - self._last_touch[ch]
        hl = self._halflife[ch]
        self.channels[ch] *= math.pow(0.5, elapsed / hl)
        self._last_touch[ch] = now

    def update_from_text(self, text):
        """扫描聊天文本，命中关键词就加对应通道"""
        hits = []
        for ch, kws in KEYWORDS.items():
            self._decay(ch)
            for kw, delta in kws.items():
                if kw in text:
                    self.channels[ch] = min(1.0, self.channels[ch] + delta)
                    hits.append((ch, kw))
        return hits

    def snapshot(self):
        out = {}
        for ch in KEYWORDS:
            self._decay(ch)
            v = round(self.channels[ch], 2)
            out[ch] = {"value": v, "label": _label(v)}
        return out
