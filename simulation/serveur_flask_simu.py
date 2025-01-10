from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

DB_CONFIG = {
    "dbname": "simu",
    "user": "postgres",
    "password": "password",
    "host": "192.168.21.153",
    "port": 5432
}

def get_all_sensors():
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT id, long, lat, intensite FROM capteur"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{"id": row[0], "intensite": row[3]} for row in rows]
    except Exception as e:
        print(f"Erreur lors de la connexion à PostgreSQL : {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/capteurs', methods=['GET'])
def api_get_all_sensors():
    print("Requête GET reçue pour /api/capteurs")
    data = get_all_sensors()
    print(f"Renvoi des données : {data}")
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)  # Serveur Flask
