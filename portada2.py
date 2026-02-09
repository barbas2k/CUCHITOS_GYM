import streamlit as st
import base64
import pandas as pd
import json
import os
import io
from datetime import date

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CUCHITOS GYM", layout="wide")

# --- 2. PERSISTENCIA DE DATOS ---
if "pin_correcto" not in st.session_state:
    st.session_state.pin_correcto = False
if "pin_input" not in st.session_state:
    st.session_state.pin_input = ""
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# 3. CSS DE INGENIERÍA: CENTRADO TOTAL Y BOTONES MASIVOS
def aplicar_estilos(archivo_fondo=None):
    b64 = ""
    if archivo_fondo and os.path.exists(archivo_fondo):
        with open(archivo_fondo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{ 
            background: {f'url("data:image/png;base64,{b64}")' if b64 else "#121212"}; 
            background-size: cover; background-position: center; 
        }}
        [data-testid="stHeader"], .stDeployButton, header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}

        /* CONTENEDOR MAESTRO */
        .main .block-container {{
            height: 100vh !important;
            max-width: 100vw !important;
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            align-items: center !important;
        }}

        /* TÍTULO SUPERIOR */
        .titulo-superior {{
            color: #FF8C00;
            font-size: clamp(35px, 12vw, 75px);
            font-weight: 900;
            text-shadow: 4px 4px 0px #000;
            text-align: center !important;
            width: 100%;
            margin-top: 20px !important;
            white-space: nowrap;
        }}

        /* BLOQUE INFERIOR */
        .bloque-inferior {{
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-bottom: 40px !important;
        }}

        .texto-seguridad {{
            color: white;
            font-weight: bold;
            font-size: 26px;
            text-shadow: 2px 2px 4px black;
            text-align: center !important;
            width: 100%;
            margin-bottom: 10px;
        }}

        .pin-display {{
            font-size: 60px;
            letter-spacing: 15px;
            color: #FF8C00;
            text-shadow: 4px 4px 0px #000;
            text-align: center !important;
            width: 100%;
            margin-bottom: 15px;
        }}

        /* --- TECLADO NUMÉRICO: BOTONES GRANDES Y CENTRADOS --- */
        [data-testid="stHorizontalBlock"] {{
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 12px !important;
            width: 92vw !important;
            max-width: 400px !important;
            margin: 0 auto !important;
        }}

        /* Forzar que el contenido de la columna se centre */
        [data-testid="column"] {{
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
        }}

        /* ESTILO DE BOTÓN DEL TECLADO */
        div[data-testid="column"] button {{
            background-color: #1a1a1a !important;
            color: white !important;
            border: 1px solid #444 !important;
            border-radius: 12px !important;
            height: 85px !important; /* Altura masiva */
            width: 100% !important;  /* Ancho total de la celda */
            font-size: 32px !important;
            font-weight: bold !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.9) !important;
        }}

        /* BOTONES DE USUARIO (CUANDO DESBLOQUEA) */
        .boton-usuario button {{
            background-color: #FF8C00 !important;
            color: white !important;
            font-size: 30px !important;
            height: 95px !important;
            width: 90vw !important;
            max-width: 450px !important;
            border: 3px solid black !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            box-shadow: 6px 6px 0px #000 !important;
            margin-bottom: 20px !important;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. LÓGICA DE NAVEGACIÓN ---

if not st.session_state.pin_correcto:
    aplicar_estilos("portada.png")
    
    # 1. ARRIBA
    st.markdown('<div class="titulo-superior">CUCHITOS GYM</div>', unsafe_allow_html=True)
    
    # 2. ABAJO
    st.markdown('<div class="bloque-inferior">', unsafe_allow_html=True)
    st.markdown('<div class="texto-seguridad">SEGURIDAD REQUERIDA</div>', unsafe_allow_html=True)
    puntos = " ".join(["●" if i < len(st.session_state.pin_input) else "○" for i in range(4)])
    st.markdown(f'<div class="pin-display">{puntos}</div>', unsafe_allow_html=True)

    # Teclado Numérico
    teclas = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "DEL", "0", "OK"]
    cols = st.columns(3)
    
    for i, t in enumerate(teclas):
        if cols[i % 3].button(t, key=f"key_{t}"):
            if t == "DEL":
                st.session_state.pin_input = st.session_state.pin_input[:-1]
            elif t == "OK":
                if st.session_state.pin_input == "1234":
                    st.session_state.pin_correcto = True
                else:
                    st.error("PIN INCORRECTO")
                    st.session_state.pin_input = ""
            else:
                if len(st.session_state.pin_input) < 4:
                    st.session_state.pin_input += t
                    if st.session_state.pin_input == "1234":
                        st.session_state.pin_correcto = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

elif not st.session_state.autenticado:
    aplicar_estilos("portada.png")
    st.markdown('<div class="titulo-superior">CUCHITOS GYM</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="bloque-inferior">', unsafe_allow_html=True)
    st.markdown('<div class="boton-usuario">', unsafe_allow_html=True)
    if st.button("DAVID"):
        st.session_state.usuario_actual = "David"; st.session_state.autenticado = True; st.rerun()
    if st.button("MARIA JOSE"):
        st.session_state.usuario_actual = "Maria Jose"; st.session_state.autenticado = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("BLOQUEAR"):
        st.session_state.pin_correcto = False
        st.session_state.pin_input = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    aplicar_estilos()
    st.markdown('<div class="titulo-superior">CUCHITOS GYM</div>', unsafe_allow_html=True)
    st.write(f"Sesión iniciada: {st.session_state.usuario_actual}")
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()