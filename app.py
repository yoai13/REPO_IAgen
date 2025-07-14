import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
from groq import Groq
import traceback

app = Flask(__name__)
app.config["DEBUG"] = True

# Cargar las variables de entorno del archivo .env
load_dotenv()

# Configuración de la base de datos
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
    print("WARNING: GROQ_API_KEY no está configurada. La integración con Groq no funcionará.")
    groq_client = None # Para evitar errores si la clave no está presente

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    Configura el cursor para devolver diccionarios.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.cursor().execute("SELECT 1;") # Intenta una operación simple
        print("INFO: ¡Conexión a la base de datos exitosa!")
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise

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
        print(f"Interacción LLM registrada: Prompt '{prompt[:50]}...'")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"ERROR: No se pudo registrar la interacción LLM en la base de datos: {e}")
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
        # Usamos RealDictCursor para obtener filas como diccionarios, más fácil de manejar
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, nationality, style, famous_works, website FROM designers;")
        designers = cur.fetchall()
        cur.close()
        return jsonify(designers)
    except Exception as e:
        print(f"Error al obtener diseñadores: {e}")
        return jsonify({"error": "No se pudieron obtener los diseñadores"}), 500
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
        print(f"Error al obtener diseñador por ID: {e}")
        return jsonify({"error": "No se pudo obtener el diseñador"}), 500
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
        print(f"Error al buscar diseñadores: {e}")
        return jsonify({"error": "No se pudo realizar la búsqueda"}), 500
    finally:
        if conn:
            conn.close()

@app.route("/designers", methods=['POST'])
def add_designer():
    conn = None
    try:
        # Obtengo los datos del diseñador del cuerpo de la solicitud JSON
        new_designer_data = request.get_json()

        # Valido que los campos necesarios estén presentes
        required_fields = ['name', 'nationality', 'style', 'famous_works', 'website']
        for field in required_fields: 
            if field not in new_designer_data:
                return jsonify({"error": f"Falta el campo '{field}'"}), 400

        # Extrae los datos
        name = new_designer_data['name']
        nationality = new_designer_data['nationality']
        style = new_designer_data['style']
        famous_works = new_designer_data['famous_works']
        website = new_designer_data['website']

        conn = get_db_connection()
        cur = conn.cursor() 

        # Construyo y ejecuto la consulta SQL para insertar los datos
        sql_insert_query = """
            INSERT INTO designers (name, nationality, style, famous_works, website)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(sql_insert_query, (name, nationality, style, famous_works, website))

        # Obtengo el ID del diseñador recién insertado
        new_designer_id = cur.fetchone()[0]

        # Confirma la transacción
        conn.commit()
        cur.close()

        # Devuelve una respuesta exitosa
        return jsonify({
            "message": "Diseñador añadido con éxito",
            "id": new_designer_id,
            "designer": new_designer_data
        }), 201

    except psycopg2.Error as db_err:
        conn.rollback()
        print(f"Error de base de datos al añadir diseñador: {db_err}")
        return jsonify({"error": "Error de base de datos al añadir diseñador", "details": str(db_err)}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error inesperado al añadir diseñador: {e}")
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
    if not groq_client:
        return jsonify({"error": "La integración con Groq no está configurada. Falta GROQ_API_KEY."}), 503

    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "Parámetro 'prompt' requerido en el cuerpo de la solicitud."}), 400

        # Obtener la IP del cliente (para el registro)
        # request.remote_addr puede ser None en algunos entornos de proxy,
        # request.headers.get('X-Forwarded-For') es más robusto en producción
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
        print(f"Error al generar texto con Groq: {e}")
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
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Ordena por timestamp descendente para ver los más recientes primero
        cur.execute("SELECT id, user_prompt, llm_response, model_used, timestamp, ip_address FROM llm_interactions_log ORDER BY timestamp DESC;")
        logs = cur.fetchall()
        cur.close()
        return jsonify(logs)
    except Exception as e:
        print(f"Error al obtener logs de interacciones LLM: {e}")
        return jsonify({"error": "No se pudieron obtener los logs de interacciones LLM"}), 500
    finally:
        if conn:
            conn.close()


if __name__ == '__main__': 
    app.run(debug=True, host='0.0.0.0', port=5000) # Añadido host y port para fácil acceso