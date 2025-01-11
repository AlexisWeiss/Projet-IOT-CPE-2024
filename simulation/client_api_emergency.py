import requests
import serial
import json
import time
import paho.mqtt.client as mqtt

# Configuration du port série
SERIAL_PORT = "/dev/tty.usbmodem11102"  # Adaptez au port série utilisé
BAUD_RATE = 115200  # Adaptez si nécessaire

# Configuration MQTT
MQTT_BROKER = "localhost"  # Adresse du broker MQTT
MQTT_PORT = 1883  # Port par défaut de Mosquitto
MQTT_TOPIC = "microbit/data"  # Sujet MQTT où publier les messages

# Configuration de l'API
API_ENDPOINT = "http://127.0.0.1:5002/api/emergency"  # Endpoint pour envoyer les données

# Initialisation du port série
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Port série {SERIAL_PORT} ouvert avec succès.")
except Exception as e:
    print(f"Erreur lors de l'ouverture du port série : {e}")
    exit()

# Initialisation MQTT
mqtt_client = mqtt.Client()
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("Connexion au broker MQTT réussie.")
except Exception as e:
    print(f"Erreur de connexion au broker MQTT : {e}")
    exit()

def send_to_api(data):
    """
    Envoie les données lues depuis le port série au serveur Flask.
    """
    try:
        # Préparer les données à envoyer sous forme de liste
        headers = {'Content-Type': 'application/json'}
        response = requests.put(API_ENDPOINT, headers=headers, json=data)  # Envoie une liste complète

        # Vérifier le statut de la réponse
        if response.status_code == 200:
            print("Données envoyées avec succès :", data)
        else:
            print(f"Erreur lors de l'envoi des données : {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Erreur lors de l'appel à l'API : {e}")

def publish_to_mqtt(sensor_data_list):
    """
    Publie les données des capteurs sur MQTT.
    """
    try:
        for sensor_data in sensor_data_list:
            mqtt_payload = {
                "sensor_id": sensor_data["id"],
                "intensity": sensor_data["intensite"],
                "timestamp": int(time.time())
            }
            mqtt_client.publish(MQTT_TOPIC, json.dumps(mqtt_payload))
            print(f"Données publiées sur MQTT : {mqtt_payload}")
    except Exception as e:
        print(f"Erreur lors de la publication sur MQTT : {e}")


def read_serial():
    """
    Lit les données depuis le port série, les parse, puis les envoie à l'API.
    """
    while True:
        try:
            if ser.in_waiting > 0:  # Vérifie si des données sont disponibles
                line = ser.readline().decode('utf-8').strip()  # Lit une ligne du port série
                print(f"Données reçues sur le port série : {line}")

                # Parse la ligne pour extraire les informations
                # Exemple attendu : "(id,intensite)(id,intensite)..."
                if line.startswith("(") and line.endswith(")"):
                    try:
                        # Séparer les blocs de capteurs
                        blocks = [block + ")" for block in line.split(")") if block]
                        
                        # Extraire les données de chaque bloc
                        sensor_data_list = []
                        for block in blocks:
                            block = block.strip("()")  # Supprimer les parenthèses
                            values = block.split(",")
                            sensor_data = {
                                "id": int(values[0]),
                                "intensite": int(values[1])
                            }
                            sensor_data_list.append(sensor_data)
                        
                        # Envoyer la liste complète à l'API et MQTT
                        send_to_api(sensor_data_list)
                        publish_to_mqtt(sensor_data_list)
                    except (ValueError, IndexError) as parse_error:
                        print(f"Erreur de parsing des données : {parse_error}")
                else:
                    print("Format des données non valide, ignoré.")

        except Exception as e:
            print(f"Erreur lors de la lecture du port série : {e}")

        time.sleep(0.1)  # Petite pause pour éviter une boucle trop rapide

if __name__ == '__main__':
    print("Démarrage de la lecture sur le port série...")
    read_serial()




#FAIRE UN ENVOI EN MQTT VERS INFLUXDB

