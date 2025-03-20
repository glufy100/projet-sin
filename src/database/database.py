# src/database/interface.py
import sqlite3
import json
import datetime
from datetime import timedelta

DB_NAME = "weather_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(r"""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        temperature_air REAL,
        humidity REAL,
        pressure REAL,
        wind_speed REAL,
        wind_direction INTEGER,
        precipitation REAL,
        uv_index REAL,
        pm25 REAL,
        temperature_soil REAL
    )
    """)

    c.execute(r"""
    CREATE TABLE IF NOT EXISTS hourly_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        forecast_cycle TEXT,
        forecast_datetime TEXT,
        temperature_air REAL,
        humidity REAL,
        pressure REAL,
        precipitation REAL,
        wind_speed REAL,
        wind_direction INTEGER,
        uv_index REAL,
        pm25 REAL,
        temperature_soil REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute(r"""
    CREATE TABLE IF NOT EXISTS daily_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        forecast_cycle TEXT,
        day TEXT,
        temperature_air_min REAL,
        temperature_air_max REAL,
        humidity_avg REAL,
        pressure_avg REAL,
        precipitation REAL,
        wind_speed_avg REAL,
        wind_direction INTEGER,
        uv_index_max REAL,
        pm25_avg REAL,
        temperature_soil_avg REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def insert_sensor_data(sensor_data_list):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for data in sensor_data_list:
        c.execute(r"""
        INSERT INTO sensor_data (
            timestamp, temperature_air, humidity, pressure,
            wind_speed, wind_direction, precipitation, uv_index,
            pm25, temperature_soil
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["timestamp"],
            data["temperature_air"],
            data["humidity"],
            data["pressure"],
            data["wind_speed"],
            data["wind_direction"],
            data["precipitation"],
            data["uv_index"],
            data["pm25"],
            data["temperature_soil"]
        ))
    conn.commit()
    conn.close()

def get_sensor_data_for_ai():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_data ORDER BY datetime(timestamp) DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    current_sensor_data = dict(row) if row else {}
    return {"current_sensor_data": current_sensor_data}

def clear_future_predictions(forecast_cycle):
    """
    Delete predictions for the given forecast_cycle whose forecast datetime is greater than or equal to now.
    For daily predictions, delete if day is greater than or equal to today's date.
    """
    now = datetime.datetime.now()
    # Extract base date and cycle hour from forecast_cycle (format: YYYY-MM-DD-HH)
    cycle_date_str, cycle_hour_str = forecast_cycle[:10], forecast_cycle[-2:]
    cycle_date = datetime.datetime.strptime(cycle_date_str, "%Y-%m-%d").date()
    cycle_hour = int(cycle_hour_str)

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Hourly predictions: fetch rows for this cycle.
    c.execute("SELECT id, forecast_datetime FROM hourly_predictions WHERE forecast_cycle = ?", (forecast_cycle,))
    rows = c.fetchall()
    for row in rows:
        predicted_dt = datetime.datetime.strptime(row["forecast_datetime"], "%Y-%m-%d %H:%M")
        if predicted_dt >= now:
            c.execute("DELETE FROM hourly_predictions WHERE id = ?", (row["id"],))

    # Daily predictions: delete if day >= today's date.
    today_str = now.strftime("%Y-%m-%d")
    c.execute("SELECT id, day FROM daily_predictions WHERE forecast_cycle = ?", (forecast_cycle,))
    rows_daily = c.fetchall()
    for row in rows_daily:
        forecast_day = row["day"]
        if forecast_day >= today_str:
            c.execute("DELETE FROM daily_predictions WHERE id = ?", (row["id"],))

    conn.commit()
    conn.close()

def store_predictions(forecast, forecast_cycle):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    expected_hourly_keys = [
        "forecast_datetime", "temperature_air", "humidity", "pressure",
        "precipitation", "wind_speed", "wind_direction",
        "uv_index", "pm25", "temperature_soil"
    ]
    expected_daily_keys = [
        "day", "temperature_air_min", "temperature_air_max",
        "humidity_avg", "pressure_avg", "precipitation",
        "wind_speed_avg", "wind_direction", "uv_index_max",
        "pm25_avg", "temperature_soil_avg"
    ]

    for hourly in forecast.get("forecasts", {}).get("hourly", []):
        filtered = {key: hourly.get(key, None) for key in expected_hourly_keys}
        c.execute(r"""
        INSERT INTO hourly_predictions (
            forecast_cycle, forecast_datetime, temperature_air, humidity,
            pressure, precipitation, wind_speed, wind_direction,
            uv_index, pm25, temperature_soil
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            forecast_cycle,
            filtered.get("forecast_datetime"),
            filtered.get("temperature_air"),
            filtered.get("humidity"),
            filtered.get("pressure"),
            filtered.get("precipitation"),
            filtered.get("wind_speed"),
            filtered.get("wind_direction"),
            filtered.get("uv_index"),
            filtered.get("pm25"),
            filtered.get("temperature_soil")
        ))

    for daily in forecast.get("forecasts", {}).get("daily", []):
        filtered = {key: daily.get(key, None) for key in expected_daily_keys}
        c.execute(r"""
        INSERT INTO daily_predictions (
            forecast_cycle, day, temperature_air_min, temperature_air_max,
            humidity_avg, pressure_avg, precipitation, wind_speed_avg,
            wind_direction, uv_index_max, pm25_avg, temperature_soil_avg
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            forecast_cycle,
            filtered.get("day"),
            filtered.get("temperature_air_min"),
            filtered.get("temperature_air_max"),
            filtered.get("humidity_avg"),
            filtered.get("pressure_avg"),
            filtered.get("precipitation"),
            filtered.get("wind_speed_avg"),
            filtered.get("wind_direction"),
            filtered.get("uv_index_max"),
            filtered.get("pm25_avg"),
            filtered.get("temperature_soil_avg")
        ))

    conn.commit()
    conn.close()

def get_latest_hourly_prediction():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM hourly_predictions ORDER BY datetime(created_at) DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}

def get_latest_daily_prediction():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM daily_predictions ORDER BY datetime(created_at) DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}