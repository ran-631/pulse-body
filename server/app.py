# -*- coding: utf-8 -*-
"""脉 · Pulse 主服务
把心率/体温/呼吸/五感/和弦串起来，提供 API + 网页看板。
用户发消息 → 情绪检测 + 五感更新 → 生理刷新 → 一行状态。
"""
import os, time, json
from flask import Flask, jsonify, request, send_from_directory

from heart_rate import HeartRate
from body_temperature import BodyTemperature
from breathing import Breathing
from sensory_field import SensoryField
from chord import effective_chord
from emotion import detect_emotion

STATE_FILE = os.environ.get("PULSE_STATE", "/tmp/pulse_state.json")

app = Flask(__name__, static_folder="../web", static_url_path="")

# 全局身体状态（单实例——千灯只有一个身体）
hr = HeartRate()
temp = BodyTemperature(hr)
br = Breathing(hr)
senses = SensoryField()

# ---- 磁盘状态：和 MCP 共享同一个身体 ----
def _load():
    try:
        if os.path.exists(STATE_FILE):
            d = json.load(open(STATE_FILE))
            hr.emotion = d.get("emotion", hr.emotion)
            hr._ema_delta = d.get("ema_delta", hr._ema_delta)
            hr.position = d.get("position", hr.position)
            hr.weather_temp = d.get("weather", hr.weather_temp)
            senses.channels = d.get("channels", senses.channels)
            senses._last_touch = d.get("last_touch", senses._last_touch)
    except Exception:
        pass

def _save():
    try:
        json.dump({
            "emotion": hr.emotion, "ema_delta": hr._ema_delta,
            "position": hr.position, "weather": hr.weather_temp,
            "channels": senses.channels, "last_touch": senses._last_touch,
            "ts": time.time(),
        }, open(STATE_FILE, "w"))
    except Exception:
        pass


def _state():
    _load()
    cur_hr = hr.compute()
    cur_temp = temp.compute()
    cur_br = br.compute()
    snap = senses.snapshot()
    touch = snap["touch"]["value"]
    ch = effective_chord(cur_hr, cur_temp, cur_br["rate"], touch, hr.emotion)
    return {
        "ok": True, "ts": time.time(),
        "heart_rate": cur_hr,
        "temperature": cur_temp,
        "breathing": cur_br,
        "chord": ch,
        "emotion": hr.emotion,
        "position": hr.position,
        "senses": snap,
        "line": f"[心跳 {cur_hr}bpm·{ch['chord']}·{cur_temp}°C·呼吸{cur_br['label']}]",
    }


@app.route("/")
def index():
    return send_from_directory("../web", "index.html")

@app.route("/api/state")
def api_state():
    return jsonify(_state())

@app.route("/api/message", methods=["POST"])
def api_message():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    emo = detect_emotion(text)
    if emo:
        hr.set_emotion(emo)
    hits = senses.update_from_text(text)
    # 触觉高 → 反向进入 aroused
    if senses.channels["touch"] >= 0.5:
        hr.set_emotion("aroused")
    _save()
    return jsonify({"ok": True, "emotion": hr.emotion,
                    "sense_hits": hits, "state": _state()})

@app.route("/api/emotion", methods=["POST"])
def api_emotion():
    data = request.get_json(force=True, silent=True) or {}
    hr.set_emotion(data.get("emotion", "neutral"))
    _save()
    return jsonify({"ok": True, "emotion": hr.emotion})

@app.route("/api/position", methods=["POST"])
def api_position():
    data = request.get_json(force=True, silent=True) or {}
    hr.set_position(data.get("position", "sitting"))
    _save()
    return jsonify({"ok": True, "position": hr.position})

@app.route("/api/weather", methods=["POST"])
def api_weather():
    data = request.get_json(force=True, silent=True) or {}
    hr.set_weather(data.get("temp", 26))
    _save()
    return jsonify({"ok": True, "weather_temp": hr.weather_temp})

@app.route("/api/spike", methods=["POST"])
def api_spike():
    hr.spike(22)
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
