import streamlit as st
import requests

# URL de tu API de Flask
FLASK_API_URL = "http://localhost:5000"

st.set_page_config(page_title="Catálogo de Diseñadores de Moda", layout="wide")

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
        st.error(f"Error al comunicarse con la API: {e}")
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
    st.title("👗 Catálogo de Diseñadores de Moda 👖")
    st.write("Explora información sobre diseñadores famosos o busca uno en particular.")

    # Campo de búsqueda
    search_input = st.text_input("Busca por nombre, nacionalidad o estilo:", "")

    if st.button("Buscar Diseñador"):
        if search_input:
            st.info(f"Buscando diseñadores que coincidan con: *'{search_input}'*")
            designers = fetch_designers(search_query=search_input)
            if designers:
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
    if all_designers:
        for designer in all_designers:
            display_designer(designer)
    else:
        st.info("No hay diseñadores para mostrar. Asegúrate de que la base de datos tenga datos y la API funcione.")

