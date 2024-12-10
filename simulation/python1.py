from flask import Flask, jsonify
import psycopg2
import threading
import time
import requests  # Pour effectuer des requêtes HTTP

# Création de l'application Flask
app = Flask(__name__)
previous_states = {}


# Configuration de la base de données PostgreSQL
DB_CONFIG = {
    "dbname": "votre_nom_de_base",
    "user": "votre_utilisateur",
    "password": "votre_mot_de_passe",
    "host": "localhost",  # ou l'adresse IP de votre serveur
    "port": 5432          # Port par défaut pour PostgreSQL
}

# Fonction pour interroger la base de données et récupérer toute la table "capteurs"
def get_all_sensors():
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Requête SQL pour récupérer toutes les données de la table "capteurs"
        query = "SELECT id, coord_X, coord_Y, intensité FROM capteurs"
        cursor.execute(query)
        
        # Récupérer les résultats
        rows = cursor.fetchall()
        
        # Formater les résultats en JSON
        result = [
            {"id": row[0], "coord_X": row[1], "coord_Y": row[2], "intensité": row[3]}
            for row in rows
        ]
        return result

    except Exception as e:
        print(f"Erreur : {e}")
        return []

    finally:
        cursor.close()
        conn.close()


def process_sensor_data(sensor_data, previous_states):
    """
    Analyse le JSON des capteurs pour détecter les changements d'intensité.
    Si l'intensité d'un capteur est > 0, formate ses données dans une chaîne de caractères.
    
    Args:
        sensor_data (list): Liste de dictionnaires représentant les données des capteurs.
        previous_states (dict): Dictionnaire contenant l'état précédent des capteurs (par id).

    Returns:
        str: Une chaîne contenant les capteurs actifs au format "(id,coord_X,coord_Y,intensité)".
        dict: Le nouvel état des capteurs.
    """
    result = ""  # Chaîne pour stocker les capteurs actifs

    for sensor in sensor_data:
        sensor_id = sensor["id"]
        coord_X = sensor["coord_X"]
        coord_Y = sensor["coord_Y"]
        intensity = sensor["intensité"]

        # Vérifie si l'intensité a changé ou est supérieure à 0
        if intensity > 0 and (sensor_id not in previous_states or previous_states[sensor_id] != intensity):
            # Ajoute le capteur au résultat sous forme de chaîne
            result += f"({sensor_id},{coord_X},{coord_Y},{intensity})"

        # Met à jour l'état précédent pour ce capteur
        previous_states[sensor_id] = intensity

    return result, previous_states


# Endpoint API pour récupérer toutes les données de "capteurs"
@app.route('/api/capteurs', methods=['GET'])
def api_get_all_sensors():
    data = get_all_sensors()  # Appelle la fonction pour interroger la base
    return jsonify(data)      # Retourne les données au format JSON

# Tâche périodique pour interroger l'API toutes les 3 secondes
def periodic_query():
    while True:
        print("Interrogation de l'API...")
        try:
            # Effectuer une requête GET à l'API
            response = requests.get("http://127.0.0.1:5000/api/capteurs")
            
            if response.status_code == 200:
                data = response.json()  # Convertir la réponse JSON en dictionnaire Python
                result, previous_states = process_sensor_data(data, previous_states)
                print("Capteurs actifs :", result)  # Affiche les capteurs actifs
                print(data)  # Afficher les données dans la console
            else:
                print(f"Erreur API : {response.status_code}")
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API : {e}")
        
        time.sleep(3)  # Pause de 3 secondes avant la prochaine requête

# Lancer le serveur Flask et la tâche périodique
if __name__ == '__main__':
    # Lancer la tâche périodique dans un thread séparé
    thread = threading.Thread(target=periodic_query)
    thread.daemon = True
    thread.start()
    
    # Lancer le serveur Flask
    app.run(debug=True)
