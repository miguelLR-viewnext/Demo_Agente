import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="Mi Agente Demo", page_icon="🤖")
st.title("Mi Agente en Modo Demo")

# 2. Obtener la API Key de los secretos (esto lo configuraremos en el despliegue)
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.warning("⚠️ Por favor, configura tu GEMINI_API_KEY")
    st.stop()

# 3. Configurar el modelo
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash') # Modelo rápido y gratuito

# 4. Inicializar el historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Interfaz de entrada del usuario
if prompt := st.chat_input("¿En qué te puedo ayudar hoy?"):
    # Guardar y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar y mostrar la respuesta del agente
    with st.chat_message("assistant"):
        try:
            # En un agente real pasaríamos todo el historial, aquí lo simplificamos
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error al conectar con la IA: {e}")