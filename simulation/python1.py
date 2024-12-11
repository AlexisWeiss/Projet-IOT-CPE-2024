from flask import Flask, jsonify
import psycopg2
import threading
import time
import requests
import os


app = Flask(__name__)
previous_states = {}


DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

def get_all_sensors():
    conn = None
    cursor = None
    try:
        #print("Tentative de connexion à la base de données PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        #print("Connexion réussie à PostgreSQL.")
        cursor = conn.cursor()
        query = "SELECT id, longitude, latitude, intensité FROM capteurs"
        cursor.execute(query)
        rows = cursor.fetchall()
        #print(f"Données récupérées : {rows}")
        return [{"id": row[0], "longitude": row[1], "latitude": row[2], "intensité": row[3]} for row in rows]
    except Exception as e:
        print(f"Erreur lors de la connexion à PostgreSQL : {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        #print("Connexion à la base de données fermée.")


def process_sensor_data(sensor_data):
    global previous_states  # Ajout de l'accès global à previous_states
    result = ""  # Stocke les capteurs actifs sous forme de chaîne
    new_previous_states = {}  # Nouveau dictionnaire temporaire

    for sensor in sensor_data:
        sensor_id = sensor["id"]
        longitude = sensor["longitude"]
        latitude = sensor["latitude"]
        intensity = sensor["intensité"]

        if intensity > 0:  # Si le capteur est actif
            if sensor_id not in previous_states or previous_states[sensor_id] != intensity:
                print(f"Capteur actif ou changé : ID={sensor_id}, Intensité={intensity}")  # DEBUG
                result += f"({sensor_id},{longitude},{latitude},{intensity})"
            new_previous_states[sensor_id] = intensity  # Mise à jour des capteurs actifs

    previous_states = new_previous_states  # Mise à jour globale après traitement
    print(f"Previous states mis à jour : {previous_states}")  # DEBUG
    return result



@app.route('/api/capteurs', methods=['GET'])
def api_get_all_sensors():
    print("Ok "+str(os.getpid()))
    #print("Appel reçu sur /api/capteurs")  # Debug
    data = get_all_sensors()
    return jsonify(data)

# Tâche périodique pour interroger l'API toutes les 3 secondes
def periodic_query():
    print("Pouet"+str(threading.current_thread().ident))
    global previous_states
    while True:
        #print("Interrogation périodique de l'API...")
        try:
            # Corrigez l'URL pour utiliser le bon port
            response = requests.get("http://127.0.0.1:5001/api/capteurs")
            #print(f"Statut API : {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                result = process_sensor_data(data)
                #print(f"Données reçues de l'API : {data}")
                print("Capteurs actifs :", result)
            else:
                print(f"Erreur API : {response.status_code}")
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API : {e}")
        print("################################################")
        time.sleep(3)


if __name__ == '__main__':
    print(os.getpid())
    thread = threading.Thread(target=periodic_query)
    thread.daemon = True
    thread.start()
    app.run(debug=False, host='0.0.0.0', port=5001)  # Changez de 5000 à 5001
