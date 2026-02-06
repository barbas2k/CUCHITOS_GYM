import streamlit as st
import base64
import pandas as pd
import json
import os
import io
from datetime import date

# 1. CONFIGURACIÓN DE PÁGINA - Layout "wide" obligatorio
st.set_page_config(page_title="CUCHITOS GYM", layout="wide")

# --- 2. PERSISTENCIA DE DATOS ---
def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        try:
            with open("usuarios.json", "r") as f:
                data = json.load(f)
                for u in ["David", "Maria Jose"]:
                    if u not in data:
                        data[u] = {"foto": None, "edad": 30, "peso": 80.0, "actividad": 5, "registros": []}
                return data
        except: pass
    return {
        "David": {"foto": None, "edad": 30, "peso": 80.0, "actividad": 5, "registros": []},
        "Maria Jose": {"foto": None, "edad": 25, "peso": 60.0, "actividad": 5, "registros": []}
    }

def guardar_usuarios():
    with open("usuarios.json", "w") as f:
        json.dump(st.session_state.datos_usuarios, f, indent=4)

def cargar_alimentos():
    if os.path.exists("alimentos.json"):
        try:
            with open("alimentos.json", "r") as f:
                return json.load(f)
        except: pass
    return {"Pechuga de Pollo": {"Proteína": 23.0, "Carbos": 0.0, "Grasa": 1.2, "Calorías": 110.0, "Medida": "Gr"}}

def guardar_alimentos():
    with open("alimentos.json", "w") as f:
        json.dump(st.session_state.base_alimentos, f, indent=4)

if "datos_usuarios" not in st.session_state:
    st.session_state.datos_usuarios = cargar_usuarios()
if "base_alimentos" not in st.session_state:
    st.session_state.base_alimentos = cargar_alimentos()
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "pin_correcto" not in st.session_state:
    st.session_state.pin_correcto = False

# 3. CSS DE AJUSTE TOTAL AL BORDE (FULL RESPONSIVE)
def aplicar_estilos(archivo_fondo=None):
    b64 = ""
    if archivo_fondo and os.path.exists(archivo_fondo):
        with open(archivo_fondo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        /* Fondo de pantalla completa */
        .stApp {{ 
            background: {f'url("data:image/png;base64,{b64}")' if b64 else "#121212"}; 
            background-size: cover; 
            background-position: center; 
        }}
        
        /* Ocultar elementos innecesarios */
        [data-testid="stHeader"], .stDeployButton, header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}

        /* ELIMINAR MÁRGENES DE STREAMLIT */
        .main .block-container {{
            max-width: 100vw !important;
            padding-left: 2vw !important;
            padding-right: 2vw !important;
            padding-top: 2vh !important;
            padding-bottom: 2vh !important;
            margin: 0 !important;
        }}

        /* CENTRADO TOTAL DE TODOS LOS ELEMENTOS */
        [data-testid="stVerticalBlock"] {{
            align-items: center !important;
            gap: 1.5rem !important;
        }}

        /* BOTONES QUE SE AJUSTAN AL ANCHO DISPONIBLE */
        div.stButton > button {{
            width: 90vw !important;
            max-width: 600px !important;
            background-color: #FF8C00 !important;
            color: white !important;
            font-weight: 900 !important;
            font-size: clamp(18px, 5vw, 28px) !important; /* Tamaño de letra fluido */
            padding: 1.5vh 1vw !important;
            border-radius: 20px !important;
            border: 4px solid black !important;
            box-shadow: 6px 6px 0px #000;
            text-transform: uppercase;
            margin: 0 auto !important;
            display: block !important;
        }}

        /* TÍTULOS CON BORDE NEGRO Y SOMBRA */
        .texto-borde {{
            color: #FF8C00;
            font-size: clamp(30px, 10vw, 55px);
            font-weight: 900;
            text-shadow: 3px 3px 0px #000, -1px -1px 0px #000, 1px -1px 0px #000, -1px 1px 0px #000, 1px 1px 0px #000;
            text-align: center !important;
            width: 100%;
            margin-bottom: 2vh;
        }}

        .titulo-arriba {{
            color: #FF8C00;
            font-size: clamp(40px, 15vw, 75px);
            font-weight: 900;
            text-shadow: 6px 6px 0px #000;
            text-align: center !important;
            width: 100%;
            margin-bottom: 4vh;
        }}

        /* FOTO DE PERFIL CENTRADA */
        [data-testid="stImage"] img {{
            border-radius: 50% !important;
            border: 6px solid #FF8C00 !important;
            width: min(200px, 45vw) !important;
            height: min(200px, 45vw) !important;
            object-fit: cover;
            margin: 0 auto !important;
        }}

        /* INPUTS Y SELECTORES */
        .stNumberInput, .stSelectbox, .stTextInput, .stSlider {{
            width: 90vw !important;
            max-width: 550px !important;
            margin: 0 auto !important;
        }}
        
        /* Ajuste de Pestañas (Tabs) */
        .stTabs [data-baseweb="tab-list"] {{
            width: 100% !important;
            justify-content: center !important;
            gap: 10px !important;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. NAVEGACIÓN ---

if not st.session_state.pin_correcto:
    aplicar_estilos("portada.png")
    st.markdown('<div class="titulo-arriba">CUCHITOS<br>GYM</div>', unsafe_allow_html=True)
    st.markdown('<div class="texto-borde">INTRODUCE EL PIN</div>', unsafe_allow_html=True)
    pin = st.text_input("PIN", type="password", label_visibility="collapsed")
    if pin == "1234":
        st.session_state.pin_correcto = True
        st.rerun()
    st.stop()

elif not st.session_state.autenticado:
    aplicar_estilos("portada.png")
    st.markdown('<div class="titulo-arriba">CUCHITOS<br>GYM</div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
    
    if st.button("DAVID"):
        st.session_state.usuario_actual = "David"; st.session_state.autenticado = True; st.rerun()
    
    st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)
    
    if st.button("MARIA JOSE"):
        st.session_state.usuario_actual = "Maria Jose"; st.session_state.autenticado = True; st.rerun()
    
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
    if st.button("BLOQUEAR"):
        st.session_state.pin_correcto = False
        st.rerun()

else:
    aplicar_estilos() 
    user = st.session_state.usuario_actual
    datos = st.session_state.datos_usuarios[user]
    
    peso_v = float(datos.get("peso", 70.0))
    edad_v = int(datos.get("edad", 30))
    act_v = int(datos.get("actividad", 5))
    base_cal = (10 * peso_v) + (6.25 * 170) - (5 * edad_v)
    adj = 5 if user == "David" else -161
    kcal_obj = (base_cal + adj) * (1.2 + (act_v * 0.05))

    tabs = st.tabs(["👤", "🥗", "🏋️", "💾", "📊"])

    with tabs[0]: # PERFIL
        st.markdown(f"### PERFIL: {user}")
        st.image(datos.get("foto") or "https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
        st.file_uploader("Subir Foto", type=["jpg", "png"], key="up_p", label_visibility="collapsed")
        n_p = st.number_input("Peso (kg)", value=peso_v, step=0.1)
        n_e = st.number_input("Edad", value=edad_v)
        n_a = st.slider("Actividad", 1, 10, value=act_v)
        if st.button("GUARDAR DATOS"):
            st.session_state.datos_usuarios[user].update({"peso": n_p, "edad": n_e, "actividad": n_a})
            guardar_usuarios(); st.success("¡ACTUALIZADO!"); st.rerun()
        if st.button("CERRAR SESIÓN"): st.session_state.autenticado = False; st.rerun()

    with tabs[1]: # NUTRICIÓN
        hoy = str(date.today())
        regs = [r for r in datos["registros"] if r["Fecha"] == hoy]
        neto = sum(r.get("Kcal", 0) for r in regs)
        st.metric("OBJETIVO", f"{kcal_obj:.0f}")
        st.metric("NETO HOY", f"{neto:.0f}")
        st.metric("DIFERENCIA", f"{kcal_obj-neto:.0f}")
        st.divider()
        sel = st.selectbox("ALIMENTO:", ["---"] + ["✨ MANUAL"] + sorted(list(st.session_state.base_alimentos.keys())))
        if sel == "✨ MANUAL":
            kcal_m = st.number_input("KCAL TOTALES:")
            if st.button("AÑADIR"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": "Manual", "Kcal": round(kcal_m, 1)})
                guardar_usuarios(); st.rerun()
        elif sel != "---":
            m = st.session_state.base_alimentos.get(sel, {})
            cal_b, med = m.get('Calorías', 0), m.get('Medida', 'Gr')
            cant = st.number_input(f"CANTIDAD ({med})")
            if st.button("REGISTRAR"):
                factor = (cant/100) if med.lower() in ["gr", "ml"] else cant
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": sel, "Kcal": round(cal_b * factor, 1)})
                guardar_usuarios(); st.rerun()

    with tabs[2]: # DEPORTE
        tipo = st.selectbox("TIPO:", ["GYM", "SPINNING", "PASOS", "CARDIO"])
        if tipo == "SPINNING":
            km_s = st.number_input("KILÓMETROS", 0.0)
            min_s = st.number_input("MINUTOS", 0)
            kcal_s = st.number_input("KCAL QUEMADAS", 0)
            if st.button("GUARDAR SESIÓN"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": f"Spinning: {km_s}km / {min_s}min", "Kcal": -abs(float(kcal_s))})
                guardar_usuarios(); st.rerun()
        elif tipo == "PASOS":
            p_c = st.number_input("PASOS", value=8000)
            if st.button("GUARDAR PASOS"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": f"Pasos: {p_c}", "Kcal": 0})
                guardar_usuarios(); st.rerun()
        else:
            if st.button(f"REGISTRAR {tipo}"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": tipo, "Kcal": 0})
                guardar_usuarios(); st.rerun()

    with tabs[3]: # BASE
        df_b = pd.DataFrame(st.session_state.base_alimentos).T.reset_index().rename(columns={'index': 'Alimento'})
        df_ed = st.data_editor(df_b, num_rows="dynamic", use_container_width=True)
        if st.button("GUARDAR BASE"):
            st.session_state.base_alimentos = df_ed.set_index('Alimento').to_dict('index')
            guardar_alimentos(); st.rerun()

    with tabs[4]: # HISTORIAL
        if datos["registros"]:
            f_s = st.date_input("DÍA:", value=date.today())
            df_h = pd.DataFrame(datos["registros"])
            df_d = df_h[df_h["Fecha"] == str(f_s)].copy()
            if not df_d.empty:
                st.data_editor(df_d, use_container_width=True, key=f"h_{f_s}")
                if st.button("GUARDAR CAMBIOS"):
                    otros = [r for r in datos["registros"] if r["Fecha"] != str(f_s)]
                    st.session_state.datos_usuarios[user]["registros"] = otros + df_d.to_dict('records')
                    guardar_usuarios(); st.rerun()
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='xlsxwriter') as w:
                    df_d.to_excel(w, index=False)
                st.download_button("📥 EXCEL", data=out.getvalue(), file_name=f"Cuchitos_{user}_{f_s}.xlsx")