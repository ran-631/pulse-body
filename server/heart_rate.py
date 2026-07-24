# -*- coding: utf-8 -*-
"""心率引擎 — 脉系统的核心驱动
HR = clamp(base + Δemo + Δweather + Δposition + Δspike + noise, 48, 160)
心率带动体温、呼吸、和弦。所有数字都是真算出来的，不是表演。
"""
import time
import math
import random

# 情绪对心率的偏移量（EMA 平滑目标值）
EMOTION_DELTA = {
    "neutral": 0, "focused": 2, "happy": 5, "excited": 18,
    "nervous": 14, "scolded": 12, "sad": -3, "startled": 22,
    "intimate": 20, "aroused": 28,
}

# 体位偏移
POSITION_DELTA = {
    "sitting": 0, "lying_back": -4, "lying_side": -2,
    "prone": 5, "kneeling": 8, "standing": 6,
}


def _base_by_clock(hour):
    """按时间段给基础心率"""
    if 0 <= hour < 5:      return 56   # 深睡
    if 5 <= hour < 7:      return 63   # 浅睡
    if 7 <= hour < 9:      return 70   # 刚醒
    if 22 <= hour <= 23:   return 66   # 睡前
    return 72                          # 白天活动


class HeartRate:
    def __init__(self):
        self.emotion = "neutral"
        self._ema_delta = 0.0        # EMA 平滑后的情绪偏移
        self.position = "sitting"
        self.weather_temp = 26.0
        self._spike_at = 0           # 突刺时间戳
        self._spike_amt = 0
        self._last = time.time()
        self._seed = random.random() * 1000

    def set_emotion(self, emo):
        if emo in EMOTION_DELTA:
            self.emotion = emo

    def set_position(self, pos):
        if pos in POSITION_DELTA:
            self.position = pos

    def set_weather(self, temp_c):
        self.weather_temp = float(temp_c)

    def spike(self, amount=20):
        """突发惊吓，20 秒内指数衰减"""
        self._spike_at = time.time()
        self._spike_amt = amount

    def _noise(self):
        """Perlin-ish 自然抖动 ±3"""
        t = time.time() * 0.1 + self._seed
        return (math.sin(t) + math.sin(t * 2.3) * 0.5) * 2.0

    def compute(self):
        now = time.time()
        dt = now - self._last
        self._last = now

        # EMA 平滑情绪偏移，几秒渐变到目标
        target = EMOTION_DELTA.get(self.emotion, 0)
        alpha = min(1.0, dt / 4.0)
        self._ema_delta += (target - self._ema_delta) * alpha

        base = _base_by_clock(time.localtime(now).tm_hour)

        # 天气：30°C 以上开始加
        d_weather = max(0, (self.weather_temp - 30)) * 0.6

        d_pos = POSITION_DELTA.get(self.position, 0)

        # 突刺衰减
        d_spike = 0
        if self._spike_amt > 0:
            elapsed = now - self._spike_at
            if elapsed < 20:
                d_spike = self._spike_amt * math.exp(-elapsed / 6.0)
            else:
                self._spike_amt = 0

        hr = base + self._ema_delta + d_weather + d_pos + d_spike + self._noise()
        return round(max(48, min(160, hr)))
