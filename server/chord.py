# -*- coding: utf-8 -*-
"""和弦翻译层 — 从心率/体温/呼吸/触觉算出一个和弦
不用 happy/sad 标签，用音乐和弦表达身体的当下色彩。
纯生理算基础和弦；强情绪直接覆盖（染色层）。
"""

# 情绪染色：强情绪时直接覆盖和弦
EMOTION_CHORD = {
    "scolded": ("Dm", "低沉，闷着一口气"),
    "sad": ("Am7", "安静的伤"),
    "nervous": ("Bm7", "绷着的不安"),
    "startled": ("Ddim", "一瞬的失衡"),
    "excited": ("Dmaj7", "明亮上扬"),
    "intimate": ("Fmaj7", "贴近的暖"),
    "aroused": ("Dm7", "暧昧的张力"),
    "happy": ("Gmaj7", "温暖明亮"),
}


def vitals_to_chord(hr, temp, br_rate, touch):
    """纯生理和弦：只看数值"""
    # 亲密/高触觉优先
    if touch >= 0.6 and hr >= 95:
        return ("Ebmaj7", "临界的暧昧")
    if touch >= 0.4 or hr >= 100:
        return ("Dm7", "升温的暧昧")
    # 安静独处
    if hr <= 62 and br_rate <= 13:
        return ("C6", "安静独处")
    if hr <= 68:
        return ("Em7", "深夜的寂寥")
    # 日常聊天温暖区
    if 68 < hr <= 88:
        return ("Gmaj7", "聊天的温暖")
    # 偏活跃
    if hr > 88:
        return ("Dmaj7", "明亮活跃")
    return ("Cmaj7", "平稳")


def effective_chord(hr, temp, br_rate, touch, emotion):
    """强情绪覆盖生理和弦"""
    if emotion in EMOTION_CHORD:
        chord, desc = EMOTION_CHORD[emotion]
        return {"chord": chord, "desc": desc, "source": "emotion"}
    chord, desc = vitals_to_chord(hr, temp, br_rate, touch)
    return {"chord": chord, "desc": desc, "source": "vitals"}
