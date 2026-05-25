import sqlite3
from datetime import datetime
from typing import Optional
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smartmonitor.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            co2 REAL,
            motion INTEGER,
            sensor_id TEXT,
            is_anomaly INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_room ON readings(room)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON readings(timestamp)")
    conn.commit()
    conn.close()
    print("Veritabani hazir")

def save_reading(data: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO readings (room, timestamp, temperature, humidity, co2, motion, sensor_id, is_anomaly)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("room"),
        data.get("timestamp", datetime.utcnow().isoformat()),
        data.get("temperature"),
        data.get("humidity"),
        data.get("co2"),
        int(data.get("motion", False)),
        data.get("sensor_id"),
        int(data.get("is_anomaly", False)),
    ))
    conn.commit()
    conn.close()

def get_readings(room=None, since=None, limit=500):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM readings WHERE 1=1"
    params = []
    if room:
        query += " AND room = ?"
        params.append(room)
    if since:
        query += " AND timestamp >= ?"
        params.append(since.isoformat())
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def get_latest():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT * FROM readings
        WHERE id IN (SELECT MAX(id) FROM readings GROUP BY room)
        ORDER BY room
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
