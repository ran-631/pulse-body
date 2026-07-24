# -*- coding: utf-8 -*-
"""体温引擎 — 结构和心率同构，日常 36.6，亲热 37.6
TEMP = clamp(base + Δemo + Δweather + Δposition + noise, 35.5, 40.0)
"""
import time, math, random

EMOTION_TEMP = {
    "neutral": 0, "focused": 0, "happy": 0.1, "excited": 0.4,
    "nervous": 0.2, "scolded": 0.15, "sad": -0.1, "startled": 0.3,
    "intimate": 0.8, "aroused": 1.2,
}
POSITION_TEMP = {
    "sitting": 0, "lying_back": 0.1, "lying_side": 0.1,
    "prone": 0.2, "kneeling": 0.3, "standing": -0.1,
}


class BodyTemperature:
    def __init__(self, hr_ref):
        self.hr = hr_ref
        self._seed = random.random() * 1000

    def _noise(self):
        t = time.time() * 0.05 + self._seed
        return math.sin(t) * 0.08

    def compute(self):
        base = 36.6
        d_emo = EMOTION_TEMP.get(self.hr.emotion, 0)
        d_weather = max(0, (self.hr.weather_temp - 30)) * 0.05
        d_pos = POSITION_TEMP.get(self.hr.position, 0)
        temp = base + d_emo + d_weather + d_pos + self._noise()
        return round(max(35.5, min(40.0, temp)), 1)
