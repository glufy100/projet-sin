# src/Generator/sensordatagenerator.py
import random
from datetime import datetime, timedelta

def generate_sensor_data():
    """
    Generates fake weather sensor data for the past 3 days (72 hours).

    Returns:
        list: A list containing sensor data dictionaries for 72 hours.
    """
    sensor_data_historical = []
    now = datetime.now()

    # Generate historical data for past 3 days (72 measurements)
    for i in range(72):
        ts = now - timedelta(hours=72 - i)
        sensor = {
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_air": round(random.uniform(-10, 40), 2),
            "humidity": round(random.uniform(20, 100), 2),
            "pressure": round(random.uniform(980, 1050), 2),
            "wind_speed": round(random.uniform(0, 100), 2),
            "wind_direction": random.randint(0, 360),
            "precipitation": round(random.uniform(0, 20), 2),
            "uv_index": round(random.uniform(0, 11), 2),
            "pm25": round(random.uniform(0, 250), 2),
            "temperature_soil": round(random.uniform(-5, 35), 2)
        }
        sensor_data_historical.append(sensor)

    return sensor_data_historical