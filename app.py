import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import extras # Mantener solo esta
from dotenv import load_dotenv
from groq import Groq
import traceback # Importación necesaria para traceback.format_exc()

app = Flask(__name__)
app.config["DEBUG"] = True # Mantener en True para ver el debugger en logs de desarrollo

# Cargar las variables de entorno del archivo .env
load_dotenv()

# Configuración de la base de datos
DB_URL = os.getenv('DB_URL')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Configuración de Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Inicializo el cliente de Groq
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    app.logger.warning("GROQ_API_KEY no está configurada. La integración con Groq no funcionará.")
    groq_client = None

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    Prioriza DATABASE_URL si está disponible, de lo contrario usa variables individuales.
    """
    conn = None
    try:
        if DB_URL:
            # Si DATABASE_URL está configurada, la usamos directamente
            conn = psycopg2.connect(DB_URL)
            app.logger.info("Conexión a la base de datos exitosa usando DATABASE_URL!")
        else:
            # Si no hay DATABASE_URL, usamos las variables individuales
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            app.logger.info("Conexión a la base de datos exitosa usando variables individuales!")

        # Ejecutar una consulta simple para verificar la conexión
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        return conn
    except Exception as e:
        app.logger.error(f"Fallo al conectar a la base de datos: {e}")
        app.logger.error(traceback.format_exc())
        raise
    finally:
        pass

def log_llm_interaction(prompt, response, model, ip_address):
    """
    Registra la interacción del LLM en la base de datos.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql_insert_log = """
            INSERT INTO llm_interactions_log (user_prompt, llm_response, model_used, ip_address)
            VALUES (%s, %s, %s, %s);
        """
        cur.execute(sql_insert_log, (prompt, response, model, ip_address))
        conn.commit()
        cur.close()
        app.logger.info(f"Interacción LLM registrada: Prompt '{prompt[:50]}...'")
    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"No se pudo registrar la interacción LLM en la base de datos: {e}")
        app.logger.error(traceback.format_exc())
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
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, nationality, style, famous_works, website FROM designers;")
        designers = cur.fetchall()
        cur.close()
        return jsonify(designers)
    except Exception as e:
        app.logger.error(f"Error al obtener diseñadores: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "No se pudieron obtener los diseñadores", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/designers/<int:designer_id>', methods=['GET'])
def get_designer_by_id(designer_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, nationality, style, famous_works, website FROM designers WHERE id = %s;", (designer_id,))
        designer = cur.fetchone()
        cur.close()
        if designer:
            return jsonify(designer)
        else:
            return jsonify({"message": "Diseñador no encontrado"}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener diseñador por ID: {e}")
        app.logger.error(traceback.format_exc())
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
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Buscamos en nombre, nacionalidad y estilo
        sql_query = """
            SELECT id, name, nationality, style, famous_works, website FROM designers
            WHERE LOWER(name) LIKE %s OR LOWER(nationality) LIKE %s OR LOWER(style) LIKE %s;
        """
        search_pattern = f"%{query}%"
        cur.execute(sql_query, (search_pattern, search_pattern, search_pattern))
        designers = cur.fetchall()
        cur.close()
        return jsonify(designers)
    except Exception as e:
        app.logger.error(f"Error al buscar diseñadores: {e}")
        app.logger.error(traceback.format_exc())
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

    except psycopg2.Error as db_err:
        if conn: conn.rollback()
        app.logger.error(f"Error de base de datos al añadir diseñador: {db_err}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Error de base de datos al añadir diseñador", "details": str(db_err)}), 500
    except Exception as e:
        if conn: conn.rollback()
        app.logger.error(f"Error inesperado al añadir diseñador: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "No se pudo añadir el diseñador", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/generate_text', methods=['POST'])
def generate_text_with_llm():
    if not groq_client:
        return jsonify({"error": "La integración con Groq no está configurada. Falta GROQ_API_KEY."}), 503

    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "Parámetro 'prompt' requerido en el cuerpo de la solicitud."}), 400

        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', 'N/A')
        model_name = "llama3-8b-8192"
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
        )
        llm_response = chat_completion.choices[0].message.content
        log_llm_interaction(prompt, llm_response, model_name, ip_address)
        return jsonify({"generated_text": llm_response})

    except Exception as e:
        app.logger.error(f"Error al generar texto con Groq: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "No se pudo generar texto con el LLM", "details": str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_llm_logs():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, user_prompt, llm_response, model_used, timestamp, ip_address FROM llm_interactions_log ORDER BY timestamp DESC;")
        logs = cur.fetchall()
        cur.close()
        return jsonify(logs)
    except Exception as e:
        app.logger.error(f"Error al obtener logs de interacciones LLM: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "No se pudieron obtener los logs de interacciones LLM", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)