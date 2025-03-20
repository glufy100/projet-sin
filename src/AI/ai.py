# src/AI/ai.py
import json
import datetime
from database import database
import ollama

def get_ai_forecast():
    sensor_data = database.get_sensor_data_for_ai()
    now = datetime.datetime.now()

    # Generate hourly forecast:
    # 1. For the current day: from next full hour until midnight.
    hourly_forecast = []
    next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    end_of_today = now.replace(hour=23, minute=0, second=0, microsecond=0)
    dt = next_hour
    while dt <= end_of_today:
        hourly_forecast.append({
            "forecast_datetime": dt.strftime("%Y-%m-%d %H:%M"),
            "temperature_air": "Predicted",
            "humidity": "Predicted",
            "pressure": "Predicted",
            "precipitation": "Predicted",
            "wind_speed": "Predicted",
            "wind_direction": "Predicted",
            "uv_index": "Predicted",
            "pm25": "Predicted",
            "temperature_soil": "Predicted"
        })
        dt += datetime.timedelta(hours=1)

    # 2. For the next day: every hour.
    next_day = now.date() + datetime.timedelta(days=1)
    dt = datetime.datetime.combine(next_day, datetime.time(0, 0))
    end_of_next_day = dt.replace(hour=23)
    while dt <= end_of_next_day:
        hourly_forecast.append({
            "forecast_datetime": dt.strftime("%Y-%m-%d %H:%M"),
            "temperature_air": "Predicted",
            "humidity": "Predicted",
            "pressure": "Predicted",
            "precipitation": "Predicted",
            "wind_speed": "Predicted",
            "wind_direction": "Predicted",
            "uv_index": "Predicted",
            "pm25": "Predicted",
            "temperature_soil": "Predicted"
        })
        dt += datetime.timedelta(hours=1)

    # Daily forecast placeholders for the two following days (unchanged)
    daily_forecast = []
    for i in range(2):
        day = (now + datetime.timedelta(days=i+2)).strftime("%Y-%m-%d")
        daily_forecast.append({
            "day": day,
            "temperature_air_min": "Predicted",
            "temperature_air_max": "Predicted",
            "humidity_avg": "Predicted",
            "pressure_avg": "Predicted",
            "precipitation": "Predicted",
            "wind_speed_avg": "Predicted",
            "wind_direction": "Predicted",
            "uv_index_max": "Predicted",
            "pm25_avg": "Predicted",
            "temperature_soil_avg": "Predicted"
        })

    prompt = {
        "instruction": "Respond strictly in JSON without any additional text or comments.",
        "context": "You specialize in short-term weather analysis and forecasting.",
        "task": ("Analyze the provided data (current_sensor_data, historical_data, location, timestamp) "
                 "and replace 'Predicted' values with realistic ones based on the data analysis."),
        "data": {
            "current_sensor_data": sensor_data.get("current_sensor_data", {}),
            "historical_data": sensor_data.get("historical_data", [])
        },
        "forecasts": {
            "hourly": hourly_forecast,
            "daily": daily_forecast
        }
    }

    prompt_str = json.dumps(prompt)

    with open('ai_prompt.log', 'w') as log_file:
        log_file.write(prompt_str)

    response = ollama.generate(model="qwen2.5:3b", prompt=prompt_str, format="json")

    try:
        forecast = json.loads(response.response)
    except json.JSONDecodeError:
        with open('ai_response.log', 'w') as log_file:
            log_file.write(response.response)
        forecast = {"error": "Invalid JSON response from AI", "raw_response": response.response}

    return forecast