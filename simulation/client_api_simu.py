import requests
import time
import serial

# Configuration du port série
SERIAL_PORT = "/dev/tty.usbmodem11302"  # Adaptez à votre configuration
BAUD_RATE = 115200  # Adaptez si nécessaire

# Initialisation du port série
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

previous_states = {}

def process_sensor_data(sensor_data):
    global previous_states  # Accès au dictionnaire global
    result = ""  # Stocke les capteurs actifs sous forme de chaîne
    new_previous_states = {}  # Nouveau dictionnaire temporaire

    for sensor in sensor_data:
        sensor_id = sensor["id"]
        intensity = sensor["intensite"]

        # Cas où l'intensité est supérieure à 0
        if intensity > 0:
            if sensor_id not in previous_states or previous_states[sensor_id] != intensity:
                print(f"Capteur actif ou changé : ID={sensor_id}, intensite={intensity}")
                result += f"({sensor_id},{intensity})"
                ser.write(result.encode() + b"\n")  # Envoie sur le port série
                print(f"Résultat envoyé au port série : {result}")
            # Mise à jour des capteurs actifs dans `new_previous_states`
            new_previous_states[sensor_id] = intensity

        # Cas où l'intensité est 0
        elif intensity == 0:
            if sensor_id in previous_states:
                print(f"Capteur désactivé : ID={sensor_id}, intensite=0")
                result += f"({sensor_id},{intensity})"
                ser.write(result.encode() + b"\n")  # Envoie sur le port série
                print(f"Résultat envoyé au port série : {result}")

    # Mise à jour de `previous_states` avec les nouveaux capteurs actifs
    previous_states = new_previous_states
    print(f"Previous states mis à jour : {previous_states}")
    return result




def periodic_query():
    global previous_states
    while True:
        try:
            response = requests.get("http://127.0.0.1:5001/api/capteurs")
            if response.status_code == 200:
                data = response.json()
                result = process_sensor_data(data)
                print("Capteurs actifs :", result)
            else:
                print(f"Erreur API : {response.status_code}")
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API : {e}")
        time.sleep(3)

if __name__ == '__main__':
    periodic_query()

