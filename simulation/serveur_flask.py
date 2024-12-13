from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

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
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT id, longitude, latitude, intensité FROM capteurs"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{"id": row[0], "intensité": row[3]} for row in rows]
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
    data = get_all_sensors()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)  # Serveur Flask
