# SmartMonitor 🏢📡

> Real-time IoT building monitoring system with MQTT data transmission, ML anomaly detection, and live web dashboard.

<img width="1822" height="934" alt="dashboard" src="https://github.com/user-attachments/assets/954b181c-c1cc-4e1e-a2d5-3a2b153cf221" />



## Overview

SmartMonitor is a full-stack IoT monitoring system that simulates building sensors, transmits data over MQTT protocol, processes it with a FastAPI backend, detects anomalies using machine learning, and visualizes everything on a real-time web dashboard via WebSocket.

Built as a practical application of **Telecommunication Technologies & Data Transmission Engineering** concepts at RTU.

## Architecture Sensor Simulator
│  MQTT Protocol (paho-mqtt)
▼
Mosquitto Broker  :1883
│
▼
FastAPI Backend   :8000
├── SQLite (time-series storage)
├── Isolation Forest (anomaly detection)
└── WebSocket → Live Dashboard

## Features

| Feature | Description |
|---------|-------------|
| 📡 MQTT Data Transmission | Real-time sensor data over industry-standard MQTT protocol |
| 🌡️ Multi-sensor Monitoring | Temperature, humidity, CO₂, motion across 5 rooms |
| 🤖 ML Anomaly Detection | Isolation Forest model detects abnormal sensor readings |
| ⚡ WebSocket Streaming | Zero-latency live updates to the dashboard |
| 🗄️ Time-series Storage | SQLite database with indexed time-series data |
| 🌐 Web Dashboard | Dark-themed real-time dashboard with Chart.js |

## Tech Stack

- **Backend**: Python, FastAPI, paho-mqtt, scikit-learn, SQLite
- **Frontend**: Vanilla JS, Chart.js, WebSocket API
- **Protocol**: MQTT (Mosquitto broker)
- **ML**: Isolation Forest anomaly detection

## Project Structure smartmonitor/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── anomaly.py
│   └── requirements.txt
├── simulator/
│   ├── sensor_simulator.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── docs/images/
│   └── dashboard.png
└── README.md

## Getting Started

### 1. Install Mosquitto
```bash
sudo apt-get install -y mosquitto mosquitto-clients
sudo systemctl start mosquitto
```

### 2. Set up environment
```bash
git clone https://github.com/begumonegi/smartmonitor.git
cd smartmonitor
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r simulator/requirements.txt
pip install websockets
```

### 3. Run
```bash
# Terminal 1 - Backend
cd backend && uvicorn main:app --port 8000

# Terminal 2 - Simulator
cd simulator && python sensor_simulator.py
```

Open `http://localhost:8000` in your browser.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /api/latest | Latest reading per room |
| GET /api/readings | Historical readings with filters |
| GET /api/anomalies | Anomaly history |
| WS /ws | Live WebSocket stream |

## Anomaly Detection

Two-layer detection system:
1. **Rule-based**: Immediate alerts for out-of-range values (temp > 35°C, CO₂ > 1500ppm)
2. **ML-based**: Isolation Forest trained on normal sensor distributions (5% contamination rate)

## Roadmap

- [x] Phase 1 — MQTT simulator + FastAPI backend + SQLite
- [x] Phase 2 — WebSocket dashboard + real-time charts
- [x] Phase 3 — ML anomaly detection + alert system
- [x] Phase 4 — Docker Compose deployment
- [x] Phase 5 — Raspberry Pi integration (DHT22, MQ-135, PIR)

## Author

**Begum Onegi** — Telecommunication Technologies & Data Transmission Engineering @ RTU

[![LinkedIn](https://img.shields.io/badge/LinkedIn-begumonegi-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/begumonegi)
[![GitHub](https://img.shields.io/badge/GitHub-begumonegi-black?style=flat&logo=github)](https://github.com/begumonegi)
