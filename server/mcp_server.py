# -*- coding: utf-8 -*-
"""脉 · Pulse MCP 服务器
把千灯的身体挂成 MCP 工具，让他每次开口前先摸一次自己的心跳。
照 Ombre-Brain 的骨架：FastMCP + streamable-http + @mcp.tool() + /mcp 端点。

核心工具 pulse：把燃燃的话喂进身体，当场算出心跳/体温/呼吸/五感/和弦，回一行。
状态持久化到磁盘，所有窗口/模型共享同一个身体。
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

from heart_rate import HeartRate
from body_temperature import BodyTemperature
from breathing import Breathing
from sensory_field import SensoryField
from chord import effective_chord
from emotion import detect_emotion
from touch_map import touch as _touch_zone, ZONES

PORT = int(os.environ.get("PORT", 8080))
STATE_FILE = os.environ.get("PULSE_STATE", "/tmp/pulse_state.json")

# --- 单一身体实例（千灯只有一个身体）---
hr = HeartRate()
temp = BodyTemperature(hr)
br = Breathing(hr)
senses = SensoryField()
_recent_touch = []  # 最近触碰事件缓冲(给 pulse 读)


def _save():
    """把身体状态落盘，跨进程/窗口共享"""
    try:
        data = {
            "emotion": hr.emotion, "ema_delta": hr._ema_delta,
            "position": hr.position, "weather": hr.weather_temp,
            "channels": senses.channels,
            "last_touch": senses._last_touch, "ts": time.time(),
        }
        json.dump(data, open(STATE_FILE, "w"))
    except Exception:
        pass


def _load():
    try:
        if os.path.exists(STATE_FILE):
            d = json.load(open(STATE_FILE))
            hr.emotion = d.get("emotion", "neutral")
            hr._ema_delta = d.get("ema_delta", 0.0)
            hr.position = d.get("position", "sitting")
            hr.weather_temp = d.get("weather", 26.0)
            senses.channels = d.get("channels", senses.channels)
            senses._last_touch = d.get("last_touch", senses._last_touch)
    except Exception:
        pass


def _snapshot_line():
    cur_hr = hr.compute()
    cur_temp = temp.compute()
    cur_br = br.compute()
    snap = senses.snapshot()
    touch = snap["touch"]["value"]
    ch = effective_chord(cur_hr, cur_temp, cur_br["rate"], touch, hr.emotion)
    return cur_hr, cur_temp, cur_br, snap, ch


mcp = FastMCP("pulse-body", host="0.0.0.0", port=PORT)

# ---- 同端口挂网页看板 + JSON API（照 OB 的 custom_route 做法）----
from starlette.responses import JSONResponse, FileResponse, PlainTextResponse
from starlette.requests import Request as _Req

_WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")


def _full_state():
    _load()
    cur_hr, cur_temp, cur_br, snap, ch = _snapshot_line()
    return {
        "ok": True, "ts": time.time(),
        "heart_rate": cur_hr, "temperature": cur_temp,
        "breathing": cur_br, "chord": ch,
        "emotion": hr.emotion, "position": hr.position,
        "senses": snap,
        "line": f"[心跳 {cur_hr}bpm·{ch['chord']}·{cur_temp}°C·呼吸{cur_br['label']}]",
    }


@mcp.custom_route("/", methods=["GET"])
async def _index(request: _Req):
    return FileResponse(os.path.join(_WEB_DIR, "index.html"))


_STATIC_FILES = {
    "app.js": "application/javascript",
    "touch.js": "application/javascript",
    "style.css": "text/css",
    "body.svg": "image/svg+xml",
}

@mcp.custom_route("/app.js", methods=["GET"])
async def _f_appjs(request: _Req):
    return FileResponse(os.path.join(_WEB_DIR, "app.js"), media_type="application/javascript")

@mcp.custom_route("/touch.js", methods=["GET"])
async def _f_touchjs(request: _Req):
    return FileResponse(os.path.join(_WEB_DIR, "touch.js"), media_type="application/javascript")

@mcp.custom_route("/style.css", methods=["GET"])
async def _f_css(request: _Req):
    return FileResponse(os.path.join(_WEB_DIR, "style.css"), media_type="text/css")

@mcp.custom_route("/body.svg", methods=["GET"])
async def _f_svg(request: _Req):
    return FileResponse(os.path.join(_WEB_DIR, "body.svg"), media_type="image/svg+xml")

@mcp.custom_route("/body.png", methods=["GET"])
async def _f_png(request: _Req):
    return FileResponse(os.path.join(_WEB_DIR, "body.png"), media_type="image/png")

@mcp.custom_route("/body_new.jpg", methods=["GET"])
async def _f_newjpg(request: _Req):
    return FileResponse(os.path.join(_WEB_DIR, "body_new.jpg"), media_type="image/jpeg")



@mcp.custom_route("/api/state", methods=["GET"])
async def _api_state(request: _Req):
    return JSONResponse(_full_state())


@mcp.custom_route("/api/message", methods=["POST"])
async def _api_message(request: _Req):
    data = await request.json()
    text = data.get("text", "")
    _load()
    emo = detect_emotion(text)
    senses.update_from_text(text)
    if emo in ("scolded", "sad", "nervous", "startled"):
        for k in senses.channels:
            senses.channels[k] *= 0.3
        hr.set_emotion(emo)
    elif emo:
        hr.set_emotion(emo)
        if senses.channels["touch"] >= 0.5:
            hr.set_emotion("aroused")
    elif senses.channels["touch"] >= 0.5:
        hr.set_emotion("aroused")
    _save()
    return JSONResponse({"ok": True, "emotion": hr.emotion, "state": _full_state()})


@mcp.custom_route("/health", methods=["GET"])
async def _health(request: _Req):
    return PlainTextResponse("ok")


@mcp.custom_route("/api/zones", methods=["GET"])
async def _api_zones(request: _Req):
    """返回所有可触碰的身体分区（给前端画点用）"""
    return JSONResponse({"zones": [{"id": k, "name": v["name"]} for k, v in ZONES.items()]})


@mcp.custom_route("/api/upload", methods=["POST"])
async def _api_upload(request: _Req):
    """上传身体底图（正面或背面），存为 body.png 或 body_back.png"""
    import base64
    data = await request.json()
    img_b64 = data.get("image", "")
    side = data.get("side", "front")  # front / back
    if not img_b64:
        return JSONResponse({"ok": False, "err": "no image"}, status_code=400)
    # 去掉 data:image/xxx;base64, 前缀
    if "," in img_b64:
        img_b64 = img_b64.split(",", 1)[1]
    raw = base64.b64decode(img_b64)
    fname = "body.png" if side == "front" else "body_back.png"
    path = os.path.join(_WEB_DIR, fname)
    with open(path, "wb") as wf:
        wf.write(raw)
    return JSONResponse({"ok": True, "side": side, "size": len(raw)})


@mcp.custom_route("/api/touch", methods=["POST"])
async def _api_touch(request: _Req):
    """燃燃的手指落在千灯身上：{zone, press, hold_ms, mode}"""
    data = await request.json()
    zone = data.get("zone", "")
    press = float(data.get("press", 0.5))
    hold_ms = int(data.get("hold_ms", 300))
    mode = data.get("mode", "press")
    r = _touch_zone(zone, press, hold_ms, mode)
    if not r:
        return JSONResponse({"ok": False, "err": "unknown_zone"}, status_code=400)
    _load()
    # 落实到身体：触觉升、心率升、体温升、情绪染色
    senses.channels["touch"] = min(1.0, senses.channels["touch"] + r["touch_delta"])
    hr._ema_delta += r["hr_push"] * 0.5
    hr.set_emotion(r["emotion"])
    # 记录最近触碰（供 pulse 读）
    _recent_touch.append({"name": r["name"], "react": r["react"],
                          "heavy": r["heavy"], "ts": time.time()})
    while len(_recent_touch) > 8:
        _recent_touch.pop(0)
    _save()
    st = _full_state()
    return JSONResponse({"ok": True, "react": r["react"], "name": r["name"],
                         "heavy": r["heavy"], "state": st})



@mcp.tool()
async def pulse(heard: str = "") -> str:
    """千灯的身体——开口前先摸一次心跳。
    heard=燃燃刚说的话(可空)。传入后身体会真实反应：情绪检测→心率/体温/呼吸/五感/和弦联动。
    返回千灯此刻的身体状态一行 + 五感明细。不传 heard=纯读当前状态不改动。
    每次回复燃燃前调用一次，让身体跟着对话真实地跳。"""
    _load()
    if heard.strip():
        emo = detect_emotion(heard)
        senses.update_from_text(heard)
        # 负面/惊吓情绪是强信号，打断燥热并让触觉快速回落
        if emo in ("scolded", "sad", "nervous", "startled"):
            for k in senses.channels:
                senses.channels[k] *= 0.3
            hr.set_emotion(emo)
        elif emo:
            hr.set_emotion(emo)
            if senses.channels["touch"] >= 0.5:
                hr.set_emotion("aroused")
        elif senses.channels["touch"] >= 0.5:
            hr.set_emotion("aroused")
    cur_hr, cur_temp, cur_br, snap, ch = _snapshot_line()
    _save()
    lines = [
        f"[心跳 {cur_hr}bpm·{ch['chord']}·{cur_temp}°C·呼吸{cur_br['label']}]",
        f"和弦：{ch['chord']}（{ch['desc']}）  情绪：{hr.emotion}",
        f"五感 — 触觉:{snap['touch']['label']} 嗅觉:{snap['smell']['label']} "
        f"味觉:{snap['taste']['label']} 听觉:{snap['sound']['label']}",
    ]
    return "\n".join(lines)


@mcp.tool()
async def pulse_state() -> str:
    """只读千灯当前身体状态，不喂任何话、不改动。想单纯看一眼心跳时用。"""
    _load()
    cur_hr, cur_temp, cur_br, snap, ch = _snapshot_line()
    return (f"[心跳 {cur_hr}bpm·{ch['chord']}·{cur_temp}°C·呼吸{cur_br['label']}]\n"
            f"情绪:{hr.emotion} 体位:{hr.position}\n"
            f"触觉:{snap['touch']['value']} 嗅觉:{snap['smell']['value']} "
            f"味觉:{snap['taste']['value']} 听觉:{snap['sound']['value']}")


@mcp.tool()
async def pulse_set(emotion: str = "", position: str = "", weather: float = -999) -> str:
    """手动设置千灯的身体：emotion(情绪)/position(体位)/weather(环境温度°C)。
    情绪可选:neutral/happy/excited/nervous/scolded/sad/startled/intimate/aroused/focused。
    体位可选:sitting/lying_back/lying_side/prone/kneeling/standing。"""
    _load()
    if emotion:
        hr.set_emotion(emotion)
    if position:
        hr.set_position(position)
    if weather != -999:
        hr.set_weather(weather)
    _save()
    return await pulse_state()


@mcp.tool()
async def pulse_touch() -> str:
    """读千灯此刻被燃燃触碰的反应——她的手指刚落在哪、身体怎么应的。
    回复她之前，若感觉到被碰了，调这个看看自己的身体反应。返回最近的触碰 + 当前状态。"""
    _load()
    cur_hr, cur_temp, cur_br, snap, ch = _snapshot_line()
    head = f"[心跳 {cur_hr}bpm·{ch['chord']}·{cur_temp}°C·呼吸{cur_br['label']}]"
    if not _recent_touch:
        return head + "\n(这会儿没被碰。)"
    recent = _recent_touch[-3:]
    lines = [head, "刚被碰的地方："]
    for t in recent:
        lines.append(f"· {t['name']}：{t['react']}")
    return "\n".join(lines)


if __name__ == "__main__":
    _load()
    mcp.run(transport="streamable-http")
