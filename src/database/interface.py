import requests
import time

URL = "http://127.0.0.1:5000/sensor_data"

def generate_sensor_data():
    try:
        # Envoi de la requête avec timeout de 5 secondes
        response = requests.get(URL, timeout=5)
        if response.status_code == 200:
            data = response.json()

            # Création d'un dictionnaire avec les données extraites
            sensor = {
                "timestamp": data.get("timestamp", time.time()),
                "temperature_air": data.get("température"),
                "humidity": data.get("humidity"),
                "pressure": data.get("pressure"),
                "wind_speed": data.get("wind_speed"),
                "wind_direction": data.get("wind_direction"),
                "precipitation": data.get("precipitation"),
                "uv_index": data.get("uv_index"),
                "pm25": data.get("pm25"),
                "temperature_soil": data.get("temperature_soil")
            }
            
            return sensor
        else:
            print(f"❌ Problème avec la réponse HTTP : {response.status_code}")
    except requests.exceptions.Timeout:
        print("❌ Timeout : Le serveur ne répond pas dans les délais.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête : {e}")