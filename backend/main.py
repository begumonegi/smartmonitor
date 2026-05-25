from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import threading
from datetime import datetime, timedelta
from typing import Optional
import paho.mqtt.client as mqtt

from database import init_db, save_reading, get_readings, get_latest
from anomaly import AnomalyDetector

class ConnectionManager:
    def __init__(self):
        self.active = []
    async def connect(self, ws):
        await ws.accept()
        self.active.append(ws)
    def disconnect(self, ws):
        if ws in self.active:
            self.active.remove(ws)
    async def broadcast(self, data):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)

manager = ConnectionManager()
anomaly_detector = AnomalyDetector()
loop = None

def on_mqtt_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        data["is_anomaly"] = anomaly_detector.predict(data)
        save_reading(data)
        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(manager.broadcast(data), loop)
    except Exception as e:
        print(f"MQTT hata: {e}")

def start_mqtt():
    client = mqtt.Client(client_id="smartmonitor_backend")
    client.on_message = on_mqtt_message
    client.connect(os.environ.get("MQTT_HOST", "localhost"), 1883, 60)
    client.subscribe("smartmonitor/sensors/#")
    client.loop_forever()

@asynccontextmanager
async def lifespan(app):
    global loop
    loop = asyncio.get_event_loop()
    init_db()
    anomaly_detector.load_or_train()
    t = threading.Thread(target=start_mqtt, daemon=True)
    t.start()
    print("SmartMonitor backend basladi")
    yield

app = FastAPI(title="SmartMonitor API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/latest")
def api_latest():
    return get_latest()

@app.get("/api/readings")
def api_readings(room: Optional[str] = None, hours: int = 1, limit: int = 500):
    since = datetime.utcnow() - timedelta(hours=hours)
    return get_readings(room=room, since=since, limit=limit)

@app.get("/api/anomalies")
def api_anomalies(hours: int = 24):
    since = datetime.utcnow() - timedelta(hours=hours)
    readings = get_readings(since=since, limit=1000)
    return [r for r in readings if r.get("is_anomaly")]

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        for r in get_latest():
            await ws.send_json(r)
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

from fastapi.staticfiles import StaticFiles
import os
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
