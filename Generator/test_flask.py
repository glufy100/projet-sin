from flask import Flask, jsonify
import random
import time
import threading

app = Flask(__name__)

current_data = {}

def generate_data():
    global current_data
    while True:

        current_data = {
            "timestamp": time.time(),
            "température": random.uniform(-10, 40),  
            "humidity": random.uniform(0, 100),       
            "pressure": random.uniform(950, 1050),   
            "wind_speed": random.uniform(0, 20),     
            "wind_direction": random.uniform(0, 360),
            "precipitation": random.uniform(0, 100),
            "uv_index": random.uniform(0, 11),       
            "pm25": random.uniform(0, 500),         
            "temperature_soil": random.uniform(-5, 30)
        }
        time.sleep(10)  # Attendre 10 secondes avant de générer de nouvelles données

@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    return jsonify(current_data)

if __name__ == '__main__':
    data_thread = threading.Thread(target=generate_data, daemon=True)
    data_thread.start()

    app.run(host='0.0.0.0', port=5000)