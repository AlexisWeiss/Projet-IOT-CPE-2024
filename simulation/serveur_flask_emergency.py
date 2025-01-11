from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    #"password": "password",
    #"host": "192.168.21.153", #IP BDD GLOBAL
    # "host": "10.42.225.195", #IP BDD MATHIEU"
    "host": "localhost",
    "port": 5432
    # "port": 5050
}

def update_sensor_data(sensor_data):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        for sensor in sensor_data:
            sensor_id = sensor["id"]
            intensity = sensor["intensite"]
            query = "UPDATE capteur SET intensite = %s WHERE id = %s"
            cursor.execute(query, (intensity, sensor_id))
        conn.commit()  # Valide toutes les modifications dans la base
        return {"success": True, "message": "capteur mis à jour avec succès."}
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la base : {e}")
        return {"success": False, "message": str(e)}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/emergency', methods=['PUT'])
def api_update_sensors():
    try:
        # Récupération des données JSON envoyées par le client
        sensor_data = request.get_json()
        
        if not isinstance(sensor_data, list):  # Vérifie si on a bien une liste de capteur
            return jsonify({"success": False, "message": "Données invalides, une liste est attendue."}), 400
        
        # Mise à jour des capteur dans la base
        result = update_sensor_data(sensor_data)
        return jsonify(result)
    except Exception as e:
        print(f"Erreur dans l'endpoint /api/emergency : {e}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5002)  # Serveur Flask
