import json, time, random, math
from datetime import datetime
import os
import paho.mqtt.client as mqtt

import os; BROKER_HOST = os.environ.get("MQTT_HOST", "localhost")
BROKER_PORT = 1883
PUBLISH_INTERVAL = 2

ROOMS = {
    "living_room": {"base_temp": 21.0, "base_humidity": 45, "base_co2": 450},
    "kitchen":     {"base_temp": 23.0, "base_humidity": 55, "base_co2": 600},
    "bedroom":     {"base_temp": 19.5, "base_humidity": 50, "base_co2": 400},
    "office":      {"base_temp": 22.0, "base_humidity": 42, "base_co2": 700},
    "bathroom":    {"base_temp": 24.0, "base_humidity": 75, "base_co2": 380},
}

def generate_sensor_data(room_name, config, t):
    hour = datetime.now().hour
    daily_cycle = math.sin((hour - 6) * math.pi / 12)
    temp = config["base_temp"] + daily_cycle * 2.5 + random.gauss(0, 0.3)
    humidity = config["base_humidity"] + random.gauss(0, 2) + math.sin(t / 300) * 5
    co2 = config["base_co2"] + random.gauss(0, 30) + (50 if 8 <= hour <= 18 else -50)
    motion = random.random() > 0.7
    if random.random() < 0.02:
        anomaly = random.choice(["temp", "co2", "humidity"])
        if anomaly == "temp": temp += random.uniform(8, 15)
        elif anomaly == "co2": co2 += random.uniform(500, 1000)
        else: humidity -= random.uniform(20, 35)
    return {
        "room": room_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "temperature": round(temp, 2),
        "humidity": round(max(0, min(100, humidity)), 2),
        "co2": round(max(300, co2), 1),
        "motion": motion,
        "sensor_id": f"sensor_{room_name}_001",
    }

def on_connect(client, userdata, flags, rc):
    print("MQTT connected" if rc == 0 else f"Connection error: {rc}")

def main():
    client = mqtt.Client(client_id="smartmonitor_simulator")
    client.on_connect = on_connect
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()
    t = 0
    print(f"Simulator started - {len(ROOMS)} rooms\n")
    try:
        while True:
            for room_name, config in ROOMS.items():
                data = generate_sensor_data(room_name, config, t)
                client.publish(f"smartmonitor/sensors/{room_name}", json.dumps(data))
                print(f"[{data['timestamp'][11:19]}] {room_name:15} "
                      f"Temp:{data['temperature']:5.1f}C "
                      f"Hum:{data['humidity']:4.1f}% "
                      f"CO2:{data['co2']:6.0f}ppm")
            print()
            time.sleep(PUBLISH_INTERVAL)
            t += PUBLISH_INTERVAL
    except KeyboardInterrupt:
        print("Simulator stopped.")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
