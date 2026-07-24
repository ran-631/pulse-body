# -*- coding: utf-8 -*-
"""呼吸引擎 — 心率是主驱动
RATE = clamp(base + hr_sync + Δemo + Δposition + noise, 8, 35)
DEPTH = 1.0 - (rate-8)/27  越快越浅
"""
import time, math, random

EMOTION_BR = {
    "neutral": 0, "focused": -1, "happy": 1, "excited": 5,
    "nervous": 4, "scolded": 2, "sad": 0, "startled": 6,
    "intimate": 4, "aroused": 8,
}
POSITION_BR = {
    "sitting": 0, "lying_back": -1, "lying_side": -1,
    "prone": 3, "kneeling": 2, "standing": 0,
}

DEPTH_LABEL = [
    (0.85, "很深很长"), (0.65, "深长"), (0.45, "平稳"),
    (0.25, "偏浅"), (0.0, "急促"),
]


def _label(rate):
    for txt in ["急促", "偏浅", "平稳", "深长", "很深很长"]:
        pass
    depth = 1.0 - (rate - 8) / 27.0
    for thr, name in DEPTH_LABEL:
        if depth >= thr:
            return name, round(depth, 2)
    return "急促", round(depth, 2)


class Breathing:
    def __init__(self, hr_ref):
        self.hr = hr_ref
        self._seed = random.random() * 1000

    def _noise(self):
        t = time.time() * 0.08 + self._seed
        return math.sin(t) * 0.8

    def compute(self):
        cur_hr = self.hr.compute()
        base = 14
        hr_sync = (cur_hr - 70) * 0.15
        d_emo = EMOTION_BR.get(self.hr.emotion, 0)
        d_pos = POSITION_BR.get(self.hr.position, 0)
        rate = base + hr_sync + d_emo + d_pos + self._noise()
        rate = max(8, min(35, rate))
        label, depth = _label(rate)
        return {"rate": round(rate), "depth": depth, "label": label}
