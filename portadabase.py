import streamlit as st
import base64

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CUCHITOS GYM", layout="centered")

# 2. FUNCIÓN PARA EL FONDO Y CSS
def aplicar_interfaz(archivo):
    try:
        with open(archivo, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
    except:
        b64 = ""

    st.markdown(
        f"""
        <style>
        /* 1. FONDO DE PANTALLA */
        .stApp {{
            background: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
        }}
        
        /* 2. OCULTAR TODO LO QUE NO NECESITAMOS */
        header, footer, #MainMenu {{visibility: hidden;}}
        .stDeployButton {{display:none;}}

        /* 3. TÍTULO SUPERIOR */
        .titulo-arriba {{
            position: fixed;
            top: 40px;
            left: 0;
            width: 100%;
            text-align: center;
            color: #FF8C00;
            font-size: 65px;
            font-weight: 900;
            font-family: 'Arial Black', sans-serif;
            text-shadow: 4px 4px 10px #000;
            z-index: 1000;
        }}

        /* 4. BOTÓN LOG IN (CENTRADO HORIZONTAL MATEMÁTICO) */
        div.stButton {{
            position: fixed;
            bottom: 60px;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: auto !important;
            z-index: 1001;
        }}

        div.stButton > button {{
            background-color: #FF8C00 !important;
            color: white !important;
            font-size: 26px !important;
            font-weight: bold !important;
            width: 260px !important;
            height: 75px !important;
            border-radius: 50px !important;
            border: 4px solid black !important;
            box-shadow: 0px 10px 20px rgba(0,0,0,0.7) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Ejecutar interfaz
aplicar_interfaz("portada.png")

# --- ELEMENTOS ---

# Título
st.markdown('<div class="titulo-arriba">CUCHITOS<br>GYM</div>', unsafe_allow_html=True)

# Botón (Streamlit lo renderiza y el CSS lo mueve al centro exacto)
if st.button("LOG IN"):
    st.write("¡Botón pulsado!") # Aquí pondremos el cambio a la pestaña de usuario