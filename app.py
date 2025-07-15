import os
import psycopg2
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configurar el nivel de log para la aplicación Flask
app.logger.setLevel(logging.INFO)

# Configuración de la base de datos
# Se prefiere DATABASE_URL si está disponible (común en Render)
DB_URL = os.getenv('DATABASE_URL')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    conn = None
    try:
        if DB_URL:
            conn = psycopg2.connect(DB_URL)
            app.logger.info("Conexión a la base de datos exitosa usando DATABASE_URL!")
        else:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            app.logger.info("Conexión a la base de datos exitosa usando variables individuales!")
        return conn
    except Exception as e:
        app.logger.error(f"Error al conectar a la base de datos: {e}")
        return None

@app.route('/')
def home():
    """Ruta raíz para verificar que la API está funcionando."""
    return "API de Diseñadores de Moda está funcionando!"

@app.route('/designers', methods=['GET'])
def get_all_designers():
    """
    Obtiene todos los diseñadores de la base de datos.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    designers = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, nationality, style, famous_works, website FROM designers ORDER BY name ASC")
        rows = cur.fetchall()
        for row in rows:
            designers.append({
                "id": row[0],
                "name": row[1],
                "nationality": row[2],
                "style": row[3],
                "famous_works": row[4],
                "website": row[5]
            })
        cur.close()
    except psycopg2.errors.UndefinedTable:
        app.logger.error("Error al buscar diseñadores: relation \"designers\" does not exist")
        return jsonify({"error": "No se pudieron obtener los diseñadores", "details": "relation \"designers\" does not exist"}), 500
    except Exception as e:
        app.logger.error(f"Error al buscar diseñadores: {e}")
        return jsonify({"error": "No se pudieron obtener los diseñadores", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(designers)


@app.route('/designers/search', methods=['GET'])
def search_designers():
    """
    Busca diseñadores por nombre, nacionalidad o estilo.
    Parámetros de consulta:
    - query: El término de búsqueda.
    """
    search_query = request.args.get('query', '').strip()
    if not search_query:
        return jsonify({"error": "Parámetro 'query' es requerido para la búsqueda"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    designers = []
    try:
        cur = conn.cursor()
        # Usar ILIKE para búsqueda insensible a mayúsculas/minúsculas
        # y % para búsqueda de subcadenas
        search_pattern = f"%{search_query}%"
        sql_query = """
        SELECT id, name, nationality, style, famous_works, website
        FROM designers
        WHERE name ILIKE %s OR nationality ILIKE %s OR style ILIKE %s
        ORDER BY name ASC;
        """
        cur.execute(sql_query, (search_pattern, search_pattern, search_pattern))
        rows = cur.fetchall()
        for row in rows:
            designers.append({
                "id": row[0],
                "name": row[1],
                "nationality": row[2],
                "style": row[3],
                "famous_works": row[4],
                "website": row[5]
            })
        cur.close()
    except psycopg2.errors.UndefinedTable:
        app.logger.error("Error al buscar diseñadores: relation \"designers\" does not exist")
        return jsonify({"error": "No se pudo realizar la búsqueda", "details": "relation \"designers\" does not exist"}), 500
    except Exception as e:
        app.logger.error(f"Error al buscar diseñadores: {e}")
        return jsonify({"error": "No se pudo realizar la búsqueda", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(designers)

if __name__ == '__main__':
    # Configurar el puerto para Render o desarrollo local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)