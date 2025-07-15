import streamlit as st
import requests
import json # Importar para manejar JSON en las solicitudes POST

# URL de tu API de Flask
FLASK_API_URL = "https://repo-iagen-2.onrender.com"

st.set_page_config(page_title="Catálogo de Diseñadores de Moda y Generador de Texto", layout="wide")

def fetch_designers(search_query=None):
    """Obtiene diseñadores de la API de Flask, opcionalmente con un término de búsqueda."""
    try:
        if search_query:
            response = requests.get(f"{FLASK_API_URL}/designers/search?query={search_query}")
        else:
            response = requests.get(f"{FLASK_API_URL}/designers")

        response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"No se pudo conectar con la API de Flask en {FLASK_API_URL}. Asegúrate de que esté ejecutándose.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error al comunicarse con la API de diseñadores: {e}")
        return None

def generate_text_with_llm_api(prompt, max_length):
    """
    Envía una solicitud POST a la API de Flask para generar texto con el LLM.
    """
    endpoint = f"{FLASK_API_URL}/generate_text"
    payload = {
        "prompt": prompt,
        "max_length": max_length
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Realiza la solicitud POST con el cuerpo JSON
        response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Lanza un error para códigos de estado HTTP 4xx/5xx
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"No se pudo conectar con la API de Flask en {FLASK_API_URL}. Asegúrate de que esté ejecutándose.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error al generar texto con el LLM: {e}")
        return None

def display_designer(designer):
    """Muestra la información de un diseñador en un formato agradable."""
    st.markdown(f"### {designer.get('name', 'N/A')}")
    if designer.get('nationality'):
        st.write(f"*Nacionalidad:* {designer['nationality']}")
    if designer.get('style'):
        st.write(f"*Estilo:* {designer['style']}")
    if designer.get('famous_works'):
        st.write(f"*Obras Notables:* {designer['famous_works']}")
    if designer.get('website'):
        st.write(f"*Web:* [{designer['website']}]({designer['website']})")
    st.markdown("---")


def main():
    st.title("👗 Catálogo de Diseñadores de Moda y Generador de Texto con IA 👖")
    st.write("Explora información sobre diseñadores famosos o genera texto creativo con un modelo de IA.")

    # --- Sección de Generación de Texto con LLM ---
    st.header("Generador de Texto con IA")
    st.write("Introduce un 'prompt' y el modelo de IA generará texto para ti.")

    llm_prompt = st.text_area("Introduce tu prompt aquí:", "Pon aquí tu pregunta sobre moda.")
    llm_max_length = st.slider("Longitud máxima del texto generado:", min_value=50, max_value=500, value=200, step=10)

    if st.button("Generar Texto"):
        if llm_prompt:
            with st.spinner("Generando texto..."):
                generated_data = generate_text_with_llm_api(llm_prompt, llm_max_length)

            if generated_data:
                if "generated_text" in generated_data:
                    st.subheader("Texto Generado:")
                    st.info(generated_data["generated_text"])
                else:
                    st.error("La API no devolvió el campo 'generated_text' esperado.")
                    st.json(generated_data) # Muestra la respuesta completa para depuración
            else:
                st.warning("No se pudo generar texto. Revisa los logs de la API de Flask.")
        else:
            st.warning("Por favor, introduce un prompt para generar texto.")

    st.markdown("---") # Separador para separar secciones

    # --- Sección de Catálogo de Diseñadores ---
    st.header("Catálogo de Diseñadores de Moda")
    st.write("Explora información sobre diseñadores famosos o busca uno en particular.")

    # Campo de búsqueda
    search_input = st.text_input("Busca diseñadores por nombre, nacionalidad o estilo:", "")

    if st.button("Buscar Diseñador"):
        if search_input:
            st.info(f"Buscando diseñadores que coincidan con: *'{search_input}'*")
            designers = fetch_designers(search_query=search_input)
            if designers is not None:
                if designers:
                    st.success(f"Se encontraron {len(designers)} diseñadores:")
                    for designer in designers:
                        display_designer(designer)
                else:
                    st.warning(f"No se encontraron diseñadores que coincidan con '{search_input}'.")
            else:
                st.info("Intenta otra búsqueda o consulta todos los diseñadores.")
        else:
            st.warning("Por favor, introduce un término de búsqueda.")

    st.markdown("---") # Separador

    st.subheader("Todos los Diseñadores (o resultados de la última búsqueda)")
    # Muestra todos los diseñadores al inicio o después de una búsqueda vacía
    all_designers = fetch_designers() # Llama sin query para obtener todos
    if all_designers is not None:
        if all_designers:
            for designer in all_designers:
                display_designer(designer)
        else:
            st.info("No hay diseñadores para mostrar. La base de datos puede estar vacía.")
    else:
        st.info("No hay diseñadores para mostrar. Asegúrate de que la API de Flask funcione y la base de datos tenga datos.")


if __name__ == "__main__":
    main()