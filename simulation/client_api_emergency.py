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

#==============================================================================

# Chargement des coordonnées des capteurs depuis un fichier JSON
#try:
#    with open("coordonates.json", "r") as file:
#        SENSOR_COORDINATES = json.load(file)
#        print("Coordonnées des capteurs chargées avec succès.")
#except Exception as e:
#    print(f"Erreur lors du chargement des coordonnées : {e}")
SENSOR_COORDINATES = {
    1:{"longitude": 4.788541313460655, "latitude": 45.75707789477852},
    2:{"longitude": 4.799470242742586, "latitude": 45.75707789477852},
    3:{"longitude": 4.799470242742586, "latitude": 45.76738430073763},
    4:{"longitude": 4.799470242742586, "latitude": 45.777690706696745},
    5:{"longitude": 4.810399172024518, "latitude": 45.75707789477852},
    6:{"longitude": 4.810399172024518, "latitude": 45.76738430073763},
    7:{"longitude": 4.810399172024518, "latitude": 45.777690706696745},
    8:{"longitude": 4.810399172024518, "latitude": 45.78799711265586},
    9:{"longitude": 4.821328101306449, "latitude": 45.72615867690118},
    10:{ "longitude": 4.821328101306449, "latitude": 45.73646508286029},
    11:{ "longitude": 4.821328101306449, "latitude": 45.746771488819405},
    12:{ "longitude": 4.821328101306449, "latitude": 45.75707789477852},
    13:{ "longitude": 4.821328101306449, "latitude": 45.76738430073763},
    14:{ "longitude": 4.821328101306449, "latitude": 45.777690706696745},
    15:{ "longitude": 4.821328101306449, "latitude": 45.78799711265586},
    16:{ "longitude": 4.821328101306449, "latitude": 45.79830351861497},
    17:{ "longitude": 4.83225703058838, "latitude": 45.72615867690118},
    18:{ "longitude": 4.83225703058838, "latitude": 45.73646508286029},
    19:{ "longitude": 4.83225703058838, "latitude": 45.746771488819405},
    20:{ "longitude": 4.83225703058838, "latitude": 45.75707789477852},
    21:{ "longitude": 4.83225703058838, "latitude": 45.76738430073763},
    22:{ "longitude": 4.83225703058838, "latitude": 45.777690706696745},
    23:{ "longitude": 4.83225703058838, "latitude": 45.78799711265586},
    24:{ "longitude": 4.83225703058838, "latitude": 45.808609924574085},
    25:{ "longitude": 4.843185959870311, "latitude": 45.72615867690118},
    26:{ "longitude": 4.843185959870311, "latitude": 45.73646508286029},
    27:{ "longitude": 4.843185959870311, "latitude": 45.746771488819405},
    28:{ "longitude": 4.843185959870311, "latitude": 45.75707789477852},
    29:{ "longitude": 4.843185959870311, "latitude": 45.76738430073763},
    30:{ "longitude": 4.843185959870311, "latitude": 45.777690706696745},
    31:{ "longitude": 4.843185959870311, "latitude": 45.78799711265586},
    32:{ "longitude": 4.8541148891522425, "latitude": 45.72615867690118},
    33:{ "longitude": 4.8541148891522425, "latitude": 45.73646508286029},
    34:{ "longitude": 4.8541148891522425, "latitude": 45.746771488819405},
    35:{ "longitude": 4.8541148891522425, "latitude": 45.75707789477852},
    36:{ "longitude": 4.8541148891522425, "latitude": 45.76738430073763},
    37:{ "longitude": 4.8541148891522425, "latitude": 45.777690706696745},
    38:{ "longitude": 4.865043818434174, "latitude": 45.73646508286029},
    39:{ "longitude": 4.865043818434174, "latitude": 45.746771488819405},
    40:{ "longitude": 4.865043818434174, "latitude": 45.75707789477852},
    41:{ "longitude": 4.865043818434174, "latitude": 45.76738430073763},
    42:{ "longitude": 4.865043818434174, "latitude": 45.777690706696745},
    43:{ "longitude": 4.865043818434174, "latitude": 45.78799711265586},
    44:{ "longitude": 4.875972747716105, "latitude": 45.72615867690118},
    45:{ "longitude": 4.875972747716105, "latitude": 45.73646508286029},
    46:{ "longitude": 4.875972747716105, "latitude": 45.746771488819405},
    47:{ "longitude": 4.875972747716105, "latitude": 45.75707789477852},
    48:{ "longitude": 4.875972747716105, "latitude": 45.76738430073763},
    49:{ "longitude": 4.875972747716105, "latitude": 45.777690706696745},
    50:{ "longitude": 4.875972747716105, "latitude": 45.78799711265586},
    51:{ "longitude": 4.886901676998036, "latitude": 45.72615867690118},
    52:{ "longitude": 4.886901676998036, "latitude": 45.73646508286029},
    53:{ "longitude": 4.886901676998036, "latitude": 45.746771488819405},
    54:{ "longitude": 4.886901676998036, "latitude": 45.75707789477852},
    55:{ "longitude": 4.886901676998036, "latitude": 45.76738430073763},
    56:{ "longitude": 4.886901676998036, "latitude": 45.777690706696745},
    57:{ "longitude": 4.8978306062799675, "latitude": 45.73646508286029},
    58:{ "longitude": 4.8978306062799675, "latitude": 45.746771488819405},
    59:{ "longitude": 4.8978306062799675, "latitude": 45.75707789477852},
    60:{ "longitude": 4.8978306062799675, "latitude": 45.76738430073763}
}

#==============================================================================


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

#==============================================================================

def publish_to_mqtt(sensor_data_list):
    """
    Publie les données des capteurs sur MQTT avec les coordonnées.
    """
    try:
        for sensor_data in sensor_data_list:
            sensor_id = sensor_data["id"]
            if sensor_id in SENSOR_COORDINATES:
                mqtt_payload = {
                    "sensor_id": sensor_id,
                    "intensity": sensor_data["intensite"],
                    "latitude": SENSOR_COORDINATES[sensor_id]["latitude"],
                    "longitude": SENSOR_COORDINATES[sensor_id]["longitude"],
                    "timestamp": int(time.time())
                }
                mqtt_client.publish(MQTT_TOPIC, json.dumps(mqtt_payload))
                print(f"Données publiées sur MQTT : {mqtt_payload}")
            else:
                print(f"Aucune coordonnée pour le capteur {sensor_id}, données ignorées.")
    except Exception as e:
        print(f"Erreur lors de la publication sur MQTT : {e}")


#def publish_to_mqtt(sensor_data_list):
#    """
#    Publie les données des capteurs sur MQTT.
#    """
#    try:
#        for sensor_data in sensor_data_list:
#            mqtt_payload = {
#               se:{sor_data["id"],
#                "intensity": sensor_data["intensite"],
#                "timestamp": int(time.time())
#            }
#            mqtt_client.publish(MQTT_TOPIC, json.dumps(mqtt_payload))
#            print(f"Données publiées sur MQTT : {mqtt_payload}")
#    except Exception as e:
#        print(f"Erreur lors de la publication sur MQTT : {e}")

#==============================================================================


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

