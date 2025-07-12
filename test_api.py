import requests
import pytest
import time # Para pausas cortas si es necesario

# URL base de tu API de Flask

FLASK_API_BASE_URL = "http://localhost:5000"

# --- Tests para la API de Diseñadores ---

# Test para la ruta raíz (inicio)
def test_root_endpoint():
    """
    Verifica que la ruta raíz de la API devuelve el mensaje esperado.
    """
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/")
        response.raise_for_status() # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        assert response.status_code == 200
        assert "Inicio de la API de designers" in response.text
        print(f"\nTest 'test_root_endpoint' PASSED: {response.text}")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_root_endpoint' FAILED: {e}")

# Test para obtener todos los diseñadores
def test_get_all_designers():
    """
    Verifica que la ruta /designers (GET) devuelve una lista de diseñadores.
    Asume que hay al menos un diseñador en la base de datos.
    """
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/designers")
        response.raise_for_status()
        assert response.status_code == 200
        designers = response.json()
        assert isinstance(designers, list)
        # Opcional: Si esperas que haya al menos 3 diseñadores (los de ejemplo)
        assert len(designers) >= 3
        print(f"\nTest 'test_get_all_designers' PASSED. Total diseñadores: {len(designers)}")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_get_all_designers' FAILED: {e}")

# Test para añadir un nuevo diseñador y luego verificar su existencia
def test_add_and_get_new_designer():
    """
    Verifica la ruta /designers (POST) añadiendo un nuevo diseñador
    y luego verifica que se puede recuperar por su ID.
    """
    new_designer_data = {
        "name": "Test Designer",
        "nationality": "Testland",
        "style": "Experimental",
        "famous_works": "Test Collection",
        "website": "http://www.test.com"
    }
    designer_id = None
    try:
        # Añadir el diseñador (POST)
        post_response = requests.post(f"{FLASK_API_BASE_URL}/designers", json=new_designer_data)
        post_response.raise_for_status()
        assert post_response.status_code == 201 # 201 Created
        response_json = post_response.json()
        assert "id" in response_json
        assert "message" in response_json
        assert response_json["message"] == "Diseñador añadido con éxito"
        designer_id = response_json["id"]
        print(f"\nTest 'test_add_and_get_new_designer' (POST) PASSED. ID: {designer_id}")

        # Verifica que el diseñador se puede obtener por ID (GET)
        get_response = requests.get(f"{FLASK_API_BASE_URL}/designers/{designer_id}")
        get_response.raise_for_status()
        assert get_response.status_code == 200
        retrieved_designer = get_response.json()
        assert retrieved_designer["id"] == designer_id
        assert retrieved_designer["name"] == new_designer_data["name"]
        print(f"Test 'test_add_and_get_new_designer' (GET by ID) PASSED. Recuperado: {retrieved_designer['name']}")

    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_add_and_get_new_designer' FAILED: {e}")
    finally:
        # Opcional: Limpiar el diseñador de prueba si se añadió correctamente
        if designer_id:
            try:
                
                pass # Eliminado para que el test no falle si no hay DELETE endpoint
            except Exception as e:
                print(f"Advertencia: No se pudo limpiar el diseñador de prueba con ID {designer_id}: {e}")


# Test para obtener un diseñador por ID existente
def test_get_designer_by_existing_id():
    """
    Verifica que la ruta /designers/<id> (GET) devuelve un diseñador existente.
    Asume que el ID 1 existe en la base de datos.
    """
    designer_id = 1 # Asume que el ID 1 (Coco Chanel) existe
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/designers/{designer_id}")
        response.raise_for_status()
        assert response.status_code == 200
        designer = response.json()
        assert designer["id"] == designer_id
        assert "name" in designer
        print(f"\nTest 'test_get_designer_by_existing_id' PASSED. Diseñador: {designer['name']}")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_get_designer_by_existing_id' FAILED: {e}")

# Test para obtener un diseñador por ID inexistente
def test_get_designer_by_non_existing_id():
    """
    Verifica que la ruta /designers/<id> (GET) devuelve 404 para un ID inexistente.
    """
    non_existing_id = 999999 # Un ID que es muy poco probable que exista
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/designers/{non_existing_id}")
        assert response.status_code == 404
        assert "Diseñador no encontrado" in response.json().get("message", "")
        print(f"\nTest 'test_get_designer_by_non_existing_id' PASSED. Mensaje: {response.json().get('message')}")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_get_designer_by_non_existing_id' FAILED: {e}")

# Test para buscar diseñadores con un término de búsqueda válido
def test_search_designers_valid_query():
    """
    Verifica que la ruta /designers/search (GET) devuelve resultados para una búsqueda válida.
    """
    search_term = "chanel" # O cualquier término que sepas que está en tus datos
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/designers/search?query={search_term}")
        response.raise_for_status()
        assert response.status_code == 200
        designers = response.json()
        assert isinstance(designers, list)
        assert len(designers) > 0 # Esperamos al menos un resultado
        assert any(search_term.lower() in d.get('name', '').lower() for d in designers)
        print(f"\nTest 'test_search_designers_valid_query' PASSED. Resultados: {len(designers)}")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_search_designers_valid_query' FAILED: {e}")

# Test para buscar diseñadores sin término de búsqueda (debe devolver 400)
def test_search_designers_no_query_param():
    """
    Verifica que la ruta /designers/search (GET) devuelve 400 si no hay parámetro 'query'.
    """
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/designers/search")
        assert response.status_code == 400
        assert "Parámetro 'query' requerido" in response.json().get("message", "")
        print(f"\nTest 'test_search_designers_no_query_param' PASSED. Mensaje: {response.json().get('message')}")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_search_designers_no_query_param' FAILED: {e}")

# Test para buscar diseñadores con un término de búsqueda que no existe
def test_search_designers_no_results():
    """
    Verifica que la ruta /designers/search (GET) devuelve una lista vacía para una búsqueda sin resultados.
    """
    search_term = "xyz_nonexistent_designer_123" # Un término que no debería existir
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/designers/search?query={search_term}")
        response.raise_for_status()
        assert response.status_code == 200
        designers = response.json()
        assert isinstance(designers, list)
        assert len(designers) == 0 # Esperamos 0 resultados
        print(f"\nTest 'test_search_designers_no_results' PASSED. Resultados: {len(designers)}")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_search_designers_no_results' FAILED: {e}")

# Test para añadir un diseñador con datos incompletos (POST)
def test_add_designer_incomplete_data():
    """
    Verifica que la ruta /designers (POST) devuelve 400 para datos incompletos.
    """
    incomplete_data = {
        "name": "Incomplete Designer",
        "nationality": "Unknown"
        # Faltan style, famous_works, website
    }
    try:
        response = requests.post(f"{FLASK_API_BASE_URL}/designers", json=incomplete_data)
        assert response.status_code == 400
        assert "Falta el campo" in response.json().get("error", "")
        print(f"\nTest 'test_add_designer_incomplete_data' PASSED. Mensaje: {response.json().get('error')}")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_add_designer_incomplete_data' FAILED: {e}")

# Test para la integración con el LLM (Groq)
def test_generate_text_with_llm():
    """
    Verifica el endpoint /generate_text (POST) con un prompt simple para el LLM.
    Requiere que GROQ_API_KEY esté configurada y que el LLM responda.
    """
    llm_prompt_data = {
        "prompt": "Dime un dato interesante sobre la moda."
    }
    try:
        response = requests.post(f"{FLASK_API_BASE_URL}/generate_text", json=llm_prompt_data)
        response.raise_for_status() # Lanza un error para 4xx/5xx
        assert response.status_code == 200
        response_json = response.json()
        assert "generated_text" in response_json
        assert isinstance(response_json["generated_text"], str)
        assert len(response_json["generated_text"]) > 10 # Asegura que la respuesta no esté vacía o sea muy corta
        print(f"\nTest 'test_generate_text_with_llm' PASSED. Respuesta del LLM: {response_json['generated_text'][:50]}...")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_generate_text_with_llm' FAILED: {e}")

# Verifica el registro de interacciones LLM en la base de datos
def test_llm_interaction_logging():
   
    initial_logs_count = 0
    try:
        # Obtener el número inicial de logs
        response_initial = requests.get(f"{FLASK_API_BASE_URL}/logs")
        response_initial.raise_for_status()
        initial_logs = response_initial.json()
        initial_logs_count = len(initial_logs)
        print(f"\nTest 'test_llm_interaction_logging': Logs iniciales: {initial_logs_count}")

    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_llm_interaction_logging' FAILED during initial log fetch: {e}")


    llm_prompt_data = {
        "prompt": "Genera una frase corta sobre moda para un test de registro."
    }
    try:
        # Realizar una solicitud a /generate_text para generar un log
        response_llm = requests.post(f"{FLASK_API_BASE_URL}/generate_text", json=llm_prompt_data)
        response_llm.raise_for_status() # Asegura que la llamada al LLM fue exitosa
        assert response_llm.status_code == 200
        print(f"Test 'test_llm_interaction_logging': Solicitud LLM enviada.")

        # Pequeña pausa para asegurar que la DB tenga tiempo de procesar (raramente necesario, pero buena práctica)
        time.sleep(0.5)

        # Obtengo el número final de logs
        response_final = requests.get(f"{FLASK_API_BASE_URL}/logs")
        response_final.raise_for_status()
        final_logs = response_final.json()
        final_logs_count = len(final_logs)
        print(f"Test 'test_llm_interaction_logging': Logs finales: {final_logs_count}")

        # Verifico que el número de logs ha aumentado en 1
        assert final_logs_count == initial_logs_count + 1, "El número de logs no aumentó como se esperaba."

        # Opcional: Verificar el contenido del último log
        if final_logs_count > 0:
            last_log = final_logs[0] # Asumiendo que ORDER BY timestamp DESC trae el más reciente primero
            assert last_log.get('user_prompt') == llm_prompt_data['prompt']
            assert 'llm_response' in last_log
            assert 'model_used' in last_log
            assert 'timestamp' in last_log
            print(f"Test 'test_llm_interaction_logging' PASSED. Nuevo log verificado.")

    except requests.exceptions.ConnectionError:
        pytest.fail(f"No se pudo conectar con la API de Flask en {FLASK_API_BASE_URL}. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        pytest.fail(f"Test 'test_llm_interaction_logging' FAILED: {e}")
