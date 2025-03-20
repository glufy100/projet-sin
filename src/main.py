import schedule
import time
import datetime
from database import database, interface
from AI import ai

def run_forecast_job():
    # Compute a forecast_cycle identifier (format: YYYY-MM-DD-HH)
    forecast_cycle = datetime.datetime.now().strftime("%Y-%m-%d-%H")
    print(f"Updating forecast for cycle: {forecast_cycle}")

    # Remove only future and current predictions from this cycle
    database.clear_future_predictions(forecast_cycle)

    print("Generating sensor data...")
    sensor_data = interface.generate_sensor_data()

    print("Inserting sensor data into the database...")
    database.insert_sensor_data(sensor_data)

    print("Retrieving AI forecast...")
    forecast = ai.get_ai_forecast()

    print("Storing new forecast predictions...")
    database.store_predictions(forecast, forecast_cycle)

    print(f"Weather Forecast for cycle {forecast_cycle} Updated:")
    print(forecast)

def main():
    print("Initializing the database...")
    database.init_db()
    # Schedule the forecast job at :50 minutes of every hour
    schedule.every().hour.at(":50").do(run_forecast_job)
    print("Scheduler started. Waiting for scheduled time...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()