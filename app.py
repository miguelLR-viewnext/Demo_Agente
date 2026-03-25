import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd

# --- 1. CONFIGURACIÓN AVANZADA DE PÁGINA ---
st.set_page_config(
    page_title="Asistente de Procesos | Viewnext", 
    page_icon="🏢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GESTIÓN DE CREDENCIALES ---
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("🛑 Error Crítico: No se han encontrado las credenciales de la API en los secretos del sistema.")
    st.stop()

# --- 3. CONFIGURACIÓN DEL MODELO E INSTRUCCIONES DE SISTEMA ---
genai.configure(api_key=api_key)

# Le damos una personalidad y contexto profesional oculto al usuario
system_instruction = """
Eres un asistente experto en automatización de procesos, RPA y análisis de datos. 
Te comunicas de forma profesional, estructurada y orientada a la resolución de problemas empresariales. 
Tienes capacidad para analizar documentos y extraer rutas de carpetas, nombres de archivos y gestionar flujos de trabajo de directorios locales (ej: Desktop/Working Docs).
"""

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=system_instruction
)

# --- 4. INICIALIZACIÓN DE VARIABLES DE SESIÓN (STATE MANAGEMENT) ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_context" not in st.session_state:
    st.session_state.document_context = ""

# --- 5. INTERFAZ: BARRA LATERAL (WORKING DOCS & UPLOAD) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png", width=50)
    st.title("Gestor de Archivos")
    st.caption("Directorio virtual: ~/Desktop/Working_Docs")
    st.divider()
    
    st.markdown("### 📄 Cargar Contexto")
    st.write("Abre el cuadro de diálogo para seleccionar archivos PDF o Excel. El robot extraerá la información y la guardará en una variable de memoria.")
    
    uploaded_file = st.file_uploader("Selecciona un archivo", type=['pdf', 'xlsx'], help="Ejemplo: Project_Plan.xlsx")
    
    if uploaded_file is not None:
        with st.spinner("Procesando y extrayendo datos..."):
            try:
                # Lógica para extraer texto de PDF
                if uploaded_file.name.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    st.session_state.document_context = text
                    
                # Lógica para extraer datos de Excel
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                    st.session_state.document_context = df.to_string()
                
                # Simulación visual de guardado con opción de sobreescritura
                st.success(f"✅ ¡Archivo '{uploaded_file.name}' procesado correctamente!")
                
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

# --- 6. INTERFAZ PRINCIPAL: ÁREA DE CHAT ---
st.title("🤖 Asistente Analítico Avanzado")
st.markdown("Plataforma de asistencia impulsada por IA para análisis de documentos y soporte operativo.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 7. LÓGICA DE PROCESAMIENTO (CORE ENGINE) ---
if prompt := st.chat_input("Escribe tu consulta o pide un análisis del documento..."):
    
    # 7.1 Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 7.2 Preparar el prompt enriquecido (RAG - Retrieval-Augmented Generation)
    final_prompt = prompt
    if st.session_state.document_context != "":
        final_prompt = f"""
        Basándote en la siguiente información del documento procesado en el área de trabajo:
        {st.session_state.document_context}
        
        Responde a la siguiente consulta del usuario de forma precisa: {prompt}
        """

    # 7.3 Generar respuesta con spinner de carga
    with st.chat_message("assistant"):
        with st.spinner("Analizando requerimientos..."):
            try:
                # Enviamos el prompt enriquecido a la sesión de chat (que tiene memoria)
                response = st.session_state.chat_session.send_message(final_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Se ha producido un error de conexión: {e}")