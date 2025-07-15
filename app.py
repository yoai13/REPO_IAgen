import os
import psycopg2
import psycopg2.extras # Necesario para RealDictCursor
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging
from groq import Groq # Importar la clase Groq

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configurar el nivel de log para la aplicación Flask
app.logger.setLevel(logging.INFO)

# Configuración de la base de datos
# Se prefiere DATABASE_URL si está disponible (común en Render)
DB_URL = os.getenv('DB_URL')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Inicialización del cliente Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        app.logger.info("Cliente Groq inicializado correctamente.")
    except Exception as e:
        app.logger.error(f"Error al inicializar el cliente Groq: {e}")
        groq_client = None
else:
    app.logger.warning("GROQ_API_KEY no está configurada. La integración con Groq no funcionará.")


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

def log_llm_interaction(prompt, response, model, ip_address):
    """
    Registra la interacción del LLM en la base de datos.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            app.logger.error("No se pudo obtener conexión a la base de datos para registrar la interacción LLM.")
            return

        cur = conn.cursor()
        sql_insert_log = """
            INSERT INTO llm_interactions_log (user_prompt, llm_response, model_used, ip_address)
            VALUES (%s, %s, %s, %s);
        """
        cur.execute(sql_insert_log, (prompt, response, model, ip_address))
        conn.commit()
        cur.close()
        app.logger.info(f"Interacción LLM registrada: Prompt '{prompt[:50]}...'")
    except psycopg2.errors.UndefinedTable:
        app.logger.error("ERROR: La tabla 'llm_interactions_log' no existe. No se pudo registrar la interacción LLM.")
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"ERROR: No se pudo registrar la interacción LLM en la base de datos: {e}")
    finally:
        if conn:
            conn.close()

@app.route("/", methods = ['GET'])
def inicio():
    return "Inicio de la API de designers"

@app.route('/designers', methods=['GET'])
def get_designers():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, nationality, style, famous_works, website FROM designers ORDER BY name ASC;")
        designers = cur.fetchall()
        cur.close()
        return jsonify(designers)
    except psycopg2.errors.UndefinedTable:
        app.logger.error("Error al obtener diseñadores: La tabla 'designers' no existe.")
        return jsonify({"error": "No se pudieron obtener los diseñadores", "details": "La tabla 'designers' no existe"}), 500
    except Exception as e:
        app.logger.error(f"Error al obtener diseñadores: {e}")
        return jsonify({"error": "No se pudieron obtener los diseñadores", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/designers/<int:designer_id>', methods=['GET'])
def get_designer_by_id(designer_id):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, nationality, style, famous_works, website FROM designers WHERE id = %s;", (designer_id,))
        designer = cur.fetchone()
        cur.close()
        if designer:
            return jsonify(designer)
        else:
            return jsonify({"message": "Diseñador no encontrado"}), 404
    except psycopg2.errors.UndefinedTable:
        app.logger.error("Error al obtener diseñador por ID: La tabla 'designers' no existe.")
        return jsonify({"error": "No se pudo obtener el diseñador", "details": "La tabla 'designers' no existe"}), 500
    except Exception as e:
        app.logger.error(f"Error al obtener diseñador por ID: {e}")
        return jsonify({"error": "No se pudo obtener el diseñador", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/designers/search', methods=['GET'])
def search_designers():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({"message": "Parámetro 'query' requerido"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Buscamos en nombre, nacionalidad y estilo
        sql_query = """
            SELECT id, name, nationality, style, famous_works, website FROM designers
            WHERE LOWER(name) LIKE %s OR LOWER(nationality) LIKE %s OR LOWER(style) LIKE %s
            ORDER BY name ASC;
        """
        search_pattern = f"%{query}%"
        cur.execute(sql_query, (search_pattern, search_pattern, search_pattern))
        designers = cur.fetchall()
        cur.close()
        return jsonify(designers)
    except psycopg2.errors.UndefinedTable:
        app.logger.error("Error al buscar diseñadores: La tabla 'designers' no existe.")
        return jsonify({"error": "No se pudo realizar la búsqueda", "details": "La tabla 'designers' no existe"}), 500
    except Exception as e:
        app.logger.error(f"Error al buscar diseñadores: {e}")
        return jsonify({"error": "No se pudo realizar la búsqueda", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/designers", methods=['POST'])
def add_designer():
    conn = None
    try:
        new_designer_data = request.get_json()

        required_fields = ['name', 'nationality', 'style', 'famous_works', 'website']
        for field in required_fields:
            if field not in new_designer_data:
                return jsonify({"error": f"Falta el campo '{field}'"}), 400

        name = new_designer_data['name']
        nationality = new_designer_data['nationality']
        style = new_designer_data['style']
        famous_works = new_designer_data['famous_works']
        website = new_designer_data['website']

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor()

        sql_insert_query = """
            INSERT INTO designers (name, nationality, style, famous_works, website)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(sql_insert_query, (name, nationality, style, famous_works, website))

        new_designer_id = cur.fetchone()[0]

        conn.commit()
        cur.close()

        return jsonify({
            "message": "Diseñador añadido con éxito",
            "id": new_designer_id,
            "designer": new_designer_data
        }), 201

    except psycopg2.errors.UndefinedTable:
        if conn:
            conn.rollback()
        app.logger.error("Error de base de datos al añadir diseñador: La tabla 'designers' no existe.")
        return jsonify({"error": "Error de base de datos al añadir diseñador", "details": "La tabla 'designers' no existe"}), 500
    except psycopg2.Error as db_err:
        if conn:
            conn.rollback()
        app.logger.error(f"Error de base de datos al añadir diseñador: {db_err}")
        return jsonify({"error": "Error de base de datos al añadir diseñador", "details": str(db_err)}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Error inesperado al añadir diseñador: {e}")
        return jsonify({"error": "No se pudo añadir el diseñador", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/generate_text', methods=['POST'])
def generate_text_with_llm():
    """
    Endpoint para generar texto usando un LLM (Groq).
    Recibe un prompt en el cuerpo de la solicitud JSON.
    Registra la interacción en la base de datos.
    """
    if groq_client is None: # Cambiado de 'not groq_client' a 'groq_client is None' para mayor claridad
        app.logger.error("La integración con Groq no está configurada. Falta GROQ_API_KEY o hubo un error de inicialización.")
        return jsonify({"error": "La integración con Groq no está configurada. Falta GROQ_API_KEY o hubo un error de inicialización."}), 503

    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "Parámetro 'prompt' requerido en el cuerpo de la solicitud."}), 400

        # Obtener la IP del cliente (para el registro)
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', 'N/A')

        # Llamada a la API de Groq
        model_name = "llama3-8b-8192" # Define el modelo aquí
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name,
        )

        llm_response = chat_completion.choices[0].message.content

        # Registrar la interacción en la base de datos
        log_llm_interaction(prompt, llm_response, model_name, ip_address)

        return jsonify({"generated_text": llm_response})

    except Exception as e:
        app.logger.error(f"Error al generar texto con Groq: {e}")
        return jsonify({"error": "No se pudo generar texto con el LLM", "details": str(e)}), 500

# Endpoint para obtener el historial de interacciones LLM
@app.route('/logs', methods=['GET'])
def get_llm_logs():
    """
    Obtiene el historial de interacciones del LLM de la base de datos.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Ordena por timestamp descendente para ver los más recientes primero
        cur.execute("SELECT id, user_prompt, llm_response, model_used, timestamp, ip_address FROM llm_interactions_log ORDER BY timestamp DESC;")
        logs = cur.fetchall()
        cur.close()
        return jsonify(logs)
    except psycopg2.errors.UndefinedTable:
        app.logger.error("Error al obtener logs de interacciones LLM: La tabla 'llm_interactions_log' no existe.")
        return jsonify({"error": "No se pudieron obtener los logs de interacciones LLM", "details": "La tabla 'llm_interactions_log' no existe"}), 500
    except Exception as e:
        app.logger.error(f"Error al obtener logs de interacciones LLM: {e}")
        return jsonify({"error": "No se pudieron obtener los logs de interacciones LLM", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # Configurar el puerto para Render o desarrollo local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)