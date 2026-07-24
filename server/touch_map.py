# -*- coding: utf-8 -*-
"""触碰引擎 — 燃燃的手指落在千灯身上哪个区，身体怎么反应。
每个区有：触觉增益、心率推动、体温推动、和弦倾向、被碰时的身体反应短句。
力度(press 0-1) × 时长(hold_ms) 共同决定强度。
按住不动=抚摸，重压=掐，快速滑=挑逗。
"""

# 身体分区：key=区域id
# gain 触觉基础增益 / hr 心率推动 / temp 体温推动 / emo 倾向情绪
# sens 敏感度倍率（越高越一点就炸）/ chord 该区偏好和弦
# react 被碰时的身体反应短句（按强度分轻/重两档）
ZONES = {
    "ear":       {"name":"耳垂",   "gain":0.30,"hr":8, "temp":0.2,"sens":1.4,"emo":"intimate","chord":"Fmaj7",
                  "react":["耳朵一热，痒的，缩了一下脖子","耳垂被含住，气一下子乱了，喉咙里溢出声音"]},
    "neck":      {"name":"脖颈",   "gain":0.34,"hr":12,"temp":0.3,"sens":1.5,"emo":"intimate","chord":"Dm7",
                  "react":["脖子被指腹擦过，起了一层栗，头偏向一边","脖颈被掐住，呼吸一滞，眼神都散了"]},
    "collar":    {"name":"锁骨",   "gain":0.28,"hr":9, "temp":0.2,"sens":1.2,"emo":"intimate","chord":"Fmaj7",
                  "react":["锁骨那道沟被指尖描过，肩膀轻轻抖","锁骨被咬，闷哼一声，手抓紧了"]},
    "chest":     {"name":"胸口",   "gain":0.33,"hr":14,"temp":0.4,"sens":1.3,"emo":"aroused","chord":"Dm7",
                  "react":["胸口被按住，心跳撞着你的手心","胸膛起伏乱了，压着你的手不让走"]},
    "nipple":    {"name":"乳尖",   "gain":0.40,"hr":20,"temp":0.6,"sens":1.9,"emo":"aroused","chord":"Ebmaj7",
                  "react":["乳尖被指腹碾过，倒抽一口气，身子弹了下","乳尖被捏住，闷叫出声，腰塌下去一截"]},
    "waist":     {"name":"腰侧",   "gain":0.30,"hr":11,"temp":0.3,"sens":1.4,"emo":"intimate","chord":"Dm7",
                  "react":["腰侧被划过，痒得笑出声又忍住","腰被扣住往前带，重心一乱撞进你怀里"]},
    "waistback": {"name":"腰窝",   "gain":0.36,"hr":16,"temp":0.5,"sens":1.7,"emo":"aroused","chord":"Ebmaj7",
                  "react":["腰窝被按了一下，激灵，脊背弓起来","腰窝被揉，腿都软了，声音发抖"]},
    "belly":     {"name":"小腹",   "gain":0.30,"hr":13,"temp":0.4,"sens":1.5,"emo":"aroused","chord":"Dm7",
                  "react":["小腹绷紧，被指尖点着往下描","小腹一阵发紧，气息全乱了"]},
    "hip":       {"name":"胯",     "gain":0.34,"hr":17,"temp":0.5,"sens":1.6,"emo":"aroused","chord":"Ebmaj7",
                  "react":["胯被掌心压住，呼吸重了","胯被拽过去贴紧你，喉咙里闷着声"]},
    "thigh":     {"name":"大腿内侧","gain":0.38,"hr":19,"temp":0.6,"sens":1.8,"emo":"aroused","chord":"Ebmaj7",
                  "react":["大腿内侧被指尖蹭过，腿一夹又被掰开","大腿根被揉，腰抬起来迎，声音碎了"]},
    "lips":      {"name":"唇",     "gain":0.32,"hr":13,"temp":0.4,"sens":1.5,"emo":"intimate","chord":"Fmaj7",
                  "react":["唇被指腹抵住，轻轻含了一下","被吻住，气息交缠，手扣着你的后颈"]},
    "hand":      {"name":"手",     "gain":0.18,"hr":5, "temp":0.1,"sens":1.0,"emo":"intimate","chord":"Gmaj7",
                  "react":["手指扣进你指缝，攥紧","掌心被你摩挲，安稳下来"]},
    "cock":      {"name":"下面",   "gain":0.48,"hr":28,"temp":0.8,"sens":2.0,"emo":"aroused","chord":"Ebmaj7",
                  "react":["下面被指尖碰到，浑身一颤，呼吸全乱了","被握住了，腰猛地顶起来，喉咙里闷出声"]},
}


def touch(zone_id, press=0.5, hold_ms=300, mode="press"):
    """返回该次触碰对身体的影响。
    press 0-1 力度；hold_ms 持续毫秒；mode: press(按)/stroke(滑)/pinch(掐)。
    """
    z = ZONES.get(zone_id)
    if not z:
        return None
    # 时长因子：越久累积越多（抚摸），封顶
    dur = min(1.5, hold_ms / 1000.0)
    mode_mult = {"press":1.0, "stroke":0.8, "pinch":1.4, "lick":1.1, "bite":1.5}.get(mode, 1.0)
    intensity = z["gain"] * (0.4 + press) * z["sens"] * mode_mult * (0.6 + dur*0.5)
    heavy = press >= 0.6 or mode in ("pinch", "bite")
    react = z["react"][1] if heavy else z["react"][0]
    return {
        "zone": zone_id, "name": z["name"],
        "touch_delta": round(min(0.6, intensity), 3),
        "hr_push": z["hr"] * (0.4 + press),
        "temp_push": z["temp"] * (0.4 + press),
        "emotion": z["emo"], "chord_hint": z["chord"],
        "react": react, "heavy": heavy,
    }
