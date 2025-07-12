# REPO_IAgen
# **Catálogo de Diseñadores de Moda 👗✨**

![alt text](image-1.png)

## **Descripción del Proyecto** 🚀
Este proyecto es una aplicación completa que permite explorar y gestionar un catálogo de diseñadores de moda. Combina una API robusta construida con Flask, una base de datos PostgreSQL para el almacenamiento de datos, integración con un Modelo de Lenguaje Grande (LLM) a través de Groq para funcionalidades de IA, y una interfaz de usuario interactiva desarrollada con Streamlit. Todo el sistema está diseñado para ser fácilmente desplegable y gestionable utilizando Docker y Docker Compose.

### **Características Principales** 🌟
**API RESTful con Flask**: 🌐

Obtención de todos los diseñadores. 🧑‍🎨

Obtención de diseñadores por ID. 🆔

Búsqueda de diseñadores por nombre, nacionalidad o estilo. 🔎

Añadir nuevos diseñadores al catálogo. ➕

Generación de texto mediante un LLM (Groq) con un endpoint dedicado. 🧠

Registro histórico de las interacciones con el LLM en la base de datos. 📝

Consulta del historial de interacciones del LLM. 📜

**Base de Datos PostgreSQL**: 🗄️

Almacenamiento persistente de la información de los diseñadores.

Registro de las consultas y respuestas del LLM.

**Integración con LLM (Groq)**: 🤖

Utiliza modelos de lenguaje pre-entrenados para generar respuestas basadas en prompts de usuario.

**Aplicación Web con Streamlit**: 🖥️

Interfaz de usuario intuitiva para visualizar y buscar diseñadores.

Conecta con la API de Flask para obtener y mostrar los datos.

**Dockerización**: 🐳

Contenedorización de la API de Flask y la base de datos PostgreSQL para un despliegue y ejecución consistentes en cualquier entorno.

Orquestación sencilla con Docker Compose.

Tecnologías Utilizadas 🛠️
Backend: Python, Flask 🐍

Base de Datos: PostgreSQL 🐘

ORM/Conector DB: Psycopg2

Variables de Entorno: python-dotenv

LLM: Groq (con el modelo llama3-8b-8192) 🧠

Frontend: Streamlit 📊

Contenedorización: Docker, Docker Compose 🐳

Testing: Pytest, Requests ✅

**Estructura del Proyecto** 📂
mi_proyecto/
├── .venv/                   
├── app_streamlit/           
│   └── app_streamlit.py
├── data/                    
├── .env                     
├── app.py                   
├── dockerfile               
├── docker-compose.yml       
├── requirements.txt         
└── test_api.py              

## **Configuración del Entorno** ⚙️
### **1. Requisitos Previos** ✅
Asegúrate de tener instalados los siguientes componentes:

Python 3.8+: Descargar Python 🐍

pip: Gestor de paquetes de Python (viene con Python). 📦

Docker Desktop: Incluye Docker Engine y Docker Compose. Descargar Docker Desktop 🐳

pgAdmin 4 (Opcional): Para gestionar la DB. Descargar pgAdmin 📊

Thunder Client (extensión de VS Code) o Postman (Opcional): Para probar la API. ⚡

### **2. Archivo .env*** 🔑
Crea un archivo llamado .env en la raíz de la carpeta mi_proyecto con el siguiente contenido. Es crucial que uses tus propias credenciales y claves API.

### **3. Entorno Virtual de Python** 🌳
Se recomienda encarecidamente usar un entorno virtual para gestionar las dependencias.

Abre tu terminal en la raíz del proyecto (mi_proyecto). 💻

Crea el entorno virtual:

python -m venv .venv

Activa el entorno virtual:

.\.venv\Scripts\activate

(En Linux/macOS: source ./.venv/bin/activate)
Tu prompt debería mostrar (.venv) al principio.

Instala las dependencias del proyecto:

pip install -r requirements.txt
pip install pytest # Asegúrate de que pytest esté instalado para los tests

### **4. Configuración de la Base de Datos PostgreSQL** 🗄️
Si usas Docker Compose, la base de datos se configurará automáticamente. Si usas una base de datos en la nube (ej. Render.com), asegúrate de que tu .env apunte a sus credenciales.

Para crear las tablas designers y llm_interactions_log (si no existen), conéctate a tu base de datos (local o remota) usando pgAdmin y ejecuta las siguientes consultas SQL:

Tabla designers: 🧑‍🎨

CREATE TABLE designers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    nationality VARCHAR(100),
    style TEXT,
    famous_works TEXT,
    website VARCHAR(255)
);

-- Datos de ejemplo (opcional)
INSERT INTO designers (name, nationality, style, famous_works, website) VALUES
('Coco Chanel', 'Francesa', 'Elegancia, minimalismo, comodidad', 'Little Black Dress, Traje de tweed', 'https://www.chanel.com'),
('Alexander McQueen', 'Británico', 'Gótico, dramático, vanguardista', 'Colecciones "Highland Rape", "Plato''s Atlantis"', 'https://www.alexandermcqueen.com'),
('Virgil Abloh', 'Estadounidense', 'Streetwear de lujo, deconstrucción', 'Off-White, colecciones para Louis Vuitton', 'https://www.off---white.com');

Tabla llm_interactions_log: 📝

CREATE TABLE llm_interactions_log (
    id SERIAL PRIMARY KEY,
    user_prompt TEXT NOT NULL,
    llm_response TEXT NOT NULL,
    model_used VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

### **5. Ejecución de la Aplicación** ▶️
Puedes ejecutar la aplicación de dos maneras: localmente (para desarrollo rápido) o usando Docker Compose (recomendado para un entorno de desarrollo/producción más consistente).

## **5.1. Ejecución Local (sin Docker Compose)** 🏠
Iniciar la API de Flask: 🌐

Abre una terminal en la raíz del proyecto (mi_proyecto).

Activa tu entorno virtual: .\.venv\Scripts\activate

Ejecuta: python app.py

La API estará disponible en http://localhost:5000.

Iniciar la Aplicación Streamlit: 📊

Abre otra terminal separada en la raíz del proyecto (mi_proyecto).

Activa tu entorno virtual: .\.venv\Scripts\activate

Navega a la carpeta app_streamlit: cd app_streamlit

Ejecuta: streamlit run app_streamlit.py

Streamlit se abrirá en tu navegador (normalmente http://localhost:8501).

## **5.2. Ejecución con Docker Compose (Recomendado)** 🐳
Asegúrate de que Docker Desktop esté en ejecución.

Abre tu terminal en la raíz del proyecto (mi_proyecto). 💻

Ejecuta el siguiente comando para construir las imágenes y levantar los contenedores (API y DB):

docker-compose up --build -d

Verifica que los contenedores estén corriendo:

docker ps

Deberías ver postgres_db_container y flask_app_container.

Tu API de Flask estará disponible en http://localhost:5000.

Para detener y limpiar los contenedores:

docker-compose down

Para eliminar también los datos de la base de datos (volumen db_data):

docker-compose down -v

### **6. Endpoints de la API (Flask)** 🔗
La API expone los siguientes puntos de acceso:

GET /: Mensaje de bienvenida. 👋

GET /designers: Obtiene todos los diseñadores. 🧑‍🎨

GET /designers/<ID>: Obtiene un diseñador por ID. 🆔

GET /designers/search?query=<término>: Busca diseñadores. 🔎

POST /designers: Añade un nuevo diseñador (requiere JSON en el cuerpo). ➕

POST /generate_text: Genera texto con IA (requiere JSON {"prompt": "..."} en el cuerpo). 💬

GET /logs: Obtiene el historial de interacciones con la IA. 📜

### **7. Testeo del Código** ✅
Los tests unitarios y de integración para la API están definidos en test_api.py y utilizan pytest.

Abre una terminal en la raíz del proyecto (mi_proyecto). 💻

Activa tu entorno virtual: .\.venv\Scripts\activate

Asegúrate de que tu API de Flask (app.py) esté ejecutándose en otra terminal separada (con su entorno virtual activado).

Ejecuta los tests:

pytest

### **8. Solución de Problemas Comunes** ❓
ModuleNotFoundError / pytest no reconocido: Asegúrate de que el entorno virtual esté activado ((.venv) en el prompt) y que todas las dependencias estén instaladas (pip install -r requirements.txt y pip install pytest). ❌

500 INTERNAL SERVER ERROR en la API: Revisa la terminal donde se ejecuta app.py para ver el error detallado de Python/PostgreSQL. Verifica credenciales de DB y que la DB esté activa y accesible. 🚨

405 METHOD NOT ALLOWED: La API no está configurada para el método HTTP que usas en esa ruta. Asegúrate de que app.py tenga la ruta y método correctos y reinicia el servidor si hiciste cambios. 🚫

docker-compose up falla con "empty compose file": Verifica que docker-compose.yml esté en la raíz del proyecto y contenga el YAML completo y correcto. 📁

Problemas de conexión a la DB remota (Render): Revisa el DB_HOST, DB_NAME, DB_USER, DB_PASSWORD en tu .env. Considera la configuración SSL y posibles firewalls en el proveedor de la base de datos. 📡