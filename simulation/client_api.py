import requests
import time
import serial

# Configuration du port série
SERIAL_PORT = "/dev/tty.usbmodem111302"  # Adaptez à votre configuration
BAUD_RATE = 115200  # Adaptez si nécessaire

# Initialisation du port série
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

previous_states = {}

def process_sensor_data(sensor_data):
    global previous_states
    result = ""
    new_previous_states = {}

    for sensor in sensor_data:
        sensor_id = sensor["id"]
        intensity = sensor["intensité"]

        if intensity > 0:
            if sensor_id not in previous_states or previous_states[sensor_id] != intensity:
                print(f"Capteur actif ou changé : ID={sensor_id}, Intensité={intensity}")
                result += f"({sensor_id},{intensity})"
                #result = f"({sensor_id},{intensity})"
                new_previous_states[sensor_id] = intensity
                previous_states = new_previous_states
    
    ser.write(result.encode() + b"\n")  # Ajoute un saut de ligne pour le séparateur
           
    
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

#décommenter le code pour essayer la nouvelle veresion avec l'envoi des données sur le port série