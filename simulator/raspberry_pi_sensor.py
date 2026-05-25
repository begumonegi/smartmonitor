#!/usr/bin/env python3
"""
SmartMonitor — Raspberry Pi Real Sensor Integration
Supports: DHT22 (temp/humidity), MQ-135 (CO2), PIR (motion)

Hardware connections:
  DHT22  → GPIO 4  (data pin)
  MQ-135 → MCP3008 SPI (analog via ADC)
  PIR    → GPIO 17 (digital)

Run on Raspberry Pi:
  pip install adafruit-circuitpython-dht adafruit-circuitpython-mcp3xxx paho-mqtt
  python3 raspberry_pi_sensor.py
"""

import json
import time
import os
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER_HOST = os.environ.get("MQTT_HOST", "localhost")
BROKER_PORT = 1883
PUBLISH_INTERVAL = 2
ROOM_NAME = os.environ.get("ROOM_NAME", "living_room")

# Try to import real hardware libraries
# Falls back to simulation if not on Raspberry Pi
try:
    import board
    import adafruit_dht
    import RPi.GPIO as GPIO
    import busio
    import adafruit_mcp3xxx.mcp3008 as MCP
    from adafruit_mcp3xxx.analog_in import AnalogIn
    import digitalio
    REAL_HARDWARE = True
    print("Running on real Raspberry Pi hardware")
except ImportError:
    REAL_HARDWARE = False
    print("Hardware libraries not found — running in simulation mode")

# ── Hardware setup ─────────────────────────────────────────────────────────

if REAL_HARDWARE:
    # DHT22 temperature & humidity sensor on GPIO 4
    dht_device = adafruit_dht.DHT22(board.D4)

    # PIR motion sensor on GPIO 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN)

    # MQ-135 CO2 sensor via MCP3008 ADC on SPI
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.CE0)
    mcp = MCP.MCP3008(spi, cs)
    co2_channel = AnalogIn(mcp, MCP.P0)

# ── Sensor reading functions ───────────────────────────────────────────────

def read_temperature_humidity():
    """Read from DHT22 sensor."""
    if REAL_HARDWARE:
        try:
            return dht_device.temperature, dht_device.humidity
        except RuntimeError:
            return None, None
    else:
        import random, math
        t = 21 + math.sin(time.time() / 300) * 3 + random.gauss(0, 0.3)
        h = 50 + random.gauss(0, 2)
        return round(t, 2), round(h, 2)

def read_co2():
    """Read CO2 from MQ-135 via MCP3008 ADC."""
    if REAL_HARDWARE:
        raw = co2_channel.value
        voltage = co2_channel.voltage
        # Convert voltage to ppm (calibration needed for real sensor)
        ppm = (voltage / 3.3) * 1000 + 400
        return round(ppm, 1)
    else:
        import random
        return round(500 + random.gauss(0, 30), 1)

def read_motion():
    """Read PIR motion sensor."""
    if REAL_HARDWARE:
        return bool(GPIO.input(17))
    else:
        import random
        return random.random() > 0.7

def read_all_sensors():
    """Read all sensors and return data dict."""
    temp, humidity = read_temperature_humidity()
    if temp is None:
        return None

    return {
        "room": ROOM_NAME,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "temperature": temp,
        "humidity": humidity,
        "co2": read_co2(),
        "motion": read_motion(),
        "sensor_id": f"rpi_{ROOM_NAME}_001",
        "hardware": REAL_HARDWARE,
    }

# ── MQTT ───────────────────────────────────────────────────────────────────

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"Connection failed: {rc}")

def main():
    client = mqtt.Client(client_id=f"rpi_{ROOM_NAME}")
    client.on_connect = on_connect
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    print(f"SmartMonitor Raspberry Pi sensor started")
    print(f"Room: {ROOM_NAME} | Hardware: {REAL_HARDWARE}\n")

    try:
        while True:
            data = read_all_sensors()
            if data:
                topic = f"smartmonitor/sensors/{ROOM_NAME}"
                client.publish(topic, json.dumps(data))
                print(f"[{data['timestamp'][11:19]}] "
                      f"Temp:{data['temperature']:5.1f}°C "
                      f"Hum:{data['humidity']:4.1f}% "
                      f"CO2:{data['co2']:6.0f}ppm "
                      f"Motion:{'YES' if data['motion'] else 'NO'}")
            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        print("\nSensor stopped.")
        if REAL_HARDWARE:
            dht_device.exit()
            GPIO.cleanup()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
