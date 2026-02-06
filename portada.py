import streamlit as st
import base64
import pandas as pd
import json
import os
import io
from datetime import date

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CUCHITOS GYM", layout="centered")

# --- SEGURIDAD: PIN DE ACCESO ---
if "pin_correcto" not in st.session_state:
    st.session_state.pin_correcto = False

if not st.session_state.pin_correcto:
    st.markdown("<h1 style='text-align: center; color: #FF8C00;'>BLOQUEO</h1>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns([0.1, 0.8, 0.1])
    with col_p2:
        pin = st.text_input("PIN", type="password")
        if pin == "1234":
            st.session_state.pin_correcto = True
            st.rerun()
        elif pin:
            st.error("Error")
    st.stop()

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

# 3. CSS RESPONSIVO (MEJORADO PARA MÓVIL)
def aplicar_estilos(archivo_fondo=None):
    b64 = ""
    if archivo_fondo and os.path.exists(archivo_fondo):
        with open(archivo_fondo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{ background: {f'url("data:image/png;base64,{b64}")' if b64 else "#121212"}; background-size: cover; background-position: center; }}
        [data-testid="stHeader"], .stDeployButton, header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
        
        /* Ajuste del contenedor principal para que no se salga de la pantalla */
        .block-container {{ 
            padding: 1rem 0.5rem !important; 
            max-width: 100% !important; 
            overflow-x: hidden !important;
        }}
        
        /* Ajuste de fuentes para pantallas pequeñas */
        @media (max-width: 480px) {{
            .titulo-arriba {{ font-size: 35px !important; }}
            [data-testid="stMetricValue"] {{ font-size: 1.5rem !important; }}
            .stTabs [data-baseweb="tab-list"] {{ gap: 5px !important; }}
            .stTabs [data-baseweb="tab"] {{ font-size: 12px !important; padding: 5px !important; }}
        }}

        div[data-testid="stVerticalBlock"] > div {{ text-align: center !important; width: 100%; }}
        div.stButton > button {{ width: 100% !important; background-color: #FF8C00 !important; color: white !important; font-weight: bold !important; border-radius: 12px !important; border: 1px solid black !important; }}
        
        [data-testid="stImage"] img {{ 
            border-radius: 50% !important; 
            border: 4px solid #FF8C00 !important; 
            max-width: 150px !important; 
            height: auto !important; 
            margin: 0 auto !important; 
        }}
        
        .titulo-arriba {{ width: 100%; text-align: center; color: #FF8C00; font-size: 50px; font-weight: 900; text-shadow: 2px 2px 5px #000; margin-bottom: 10px; }}
        .stNumberInput, .stSelectbox, .stTextInput, .stSlider {{ width: 100% !important; }}
        
        /* Forzar tablas a ser responsivas */
        [data-testid="stTable"], [data-testid="stDataFrame"] {{ width: 100% !important; overflow-x: auto !important; }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. ACCESO ---
if not st.session_state.autenticado:
    aplicar_estilos("portada.png")
    st.markdown('<div class="titulo-arriba">CUCHITOS<br>GYM</div>', unsafe_allow_html=True)
    st.markdown("<br>"*8, unsafe_allow_html=True)
    
    col_izq, col_btn, col_der = st.columns([0.1, 0.8, 0.1])
    with col_btn:
        if st.button("DAVID 👑"):
            st.session_state.usuario_actual = "David"; st.session_state.autenticado = True; st.rerun()
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("MARIA JOSE 🎀"):
            st.session_state.usuario_actual = "Maria Jose"; st.session_state.autenticado = True; st.rerun()

else:
    aplicar_estilos() 
    user = st.session_state.usuario_actual
    datos = st.session_state.datos_usuarios[user]
    
    # --- CÁLCULO TMB ---
    peso_v = float(datos.get("peso", 70.0))
    edad_v = int(datos.get("edad", 30))
    act_v = int(datos.get("actividad", 5))
    base_cal = (10 * peso_v) + (6.25 * 170) - (5 * edad_v)
    adj = 5 if user == "David" else -161
    kcal_obj = (base_cal + adj) * (1.2 + (act_v * 0.05))

    tabs = st.tabs(["👤", "🥗", "🏋️", "💾", "📊"])

    with tabs[0]: # PERFIL
        st.markdown(f"### {user}")
        st.image(datos.get("foto") or "https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
        up = st.file_uploader("Foto", type=["jpg", "png"], key="up_p", label_visibility="collapsed")
        if up:
            st.session_state.datos_usuarios[user]["foto"] = f"data:image/png;base64,{base64.b64encode(up.read()).decode()}"
            guardar_usuarios(); st.rerun()
        n_p = st.number_input("Peso (kg)", value=peso_v)
        n_e = st.number_input("Edad", value=edad_v)
        n_a = st.slider("Actividad", 1, 10, value=act_v)
        if st.button("Guardar 💾"):
            st.session_state.datos_usuarios[user].update({"peso": n_p, "edad": n_e, "actividad": n_a})
            guardar_usuarios(); st.success("¡Hecho!"); st.rerun()
        if st.button("Cerrar Sesión 🚪"): st.session_state.autenticado = False; st.rerun()

    with tabs[1]: # NUTRICIÓN
        hoy = str(date.today())
        regs = [r for r in datos["registros"] if r["Fecha"] == hoy]
        neto = sum(r.get("Kcal", 0) for r in regs)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Meta", f"{kcal_obj:.0f}")
        c2.metric("Neto", f"{neto:.0f}")
        c3.metric("Diff", f"{kcal_obj-neto:.0f}")
        
        sel = st.selectbox("Comida:", ["---"] + ["✨ MANUAL"] + sorted(list(st.session_state.base_alimentos.keys())))
        if sel == "✨ MANUAL":
            kcal_m = st.number_input("Kcal:")
            if st.button("Añadir"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": "Manual", "Kcal": round(kcal_m, 1)})
                guardar_usuarios(); st.rerun()
        elif sel != "---":
            m = st.session_state.base_alimentos.get(sel, {})
            cal_b, med = m.get('Calorías', 0), m.get('Medida', 'Gr')
            cant = st.number_input(f"Cant. ({med})")
            if st.button("Añadir ✅"):
                factor = (cant/100) if med.lower() in ["gr", "ml"] else cant
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": sel, "Kcal": round(cal_b * factor, 1)})
                guardar_usuarios(); st.rerun()

    with tabs[2]: # DEPORTE
        tipo = st.selectbox("Entreno:", ["Gym", "Spinning", "Descanso"])
        if tipo == "Spinning":
            kc = st.number_input("Kcal quemadas:")
            if st.button("Guardar 🚴"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Momento": "Deporte", "Alimento": "Spinning", "Kcal": -abs(float(kc))})
                guardar_usuarios(); st.rerun()
        else:
            if st.button(f"Registrar {tipo} ✅"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Momento": "Deporte", "Alimento": tipo, "Kcal": 0})
                guardar_usuarios(); st.rerun()

    with tabs[3]: # ALIMENTOS
        df_b = pd.DataFrame(st.session_state.base_alimentos).T.reset_index().rename(columns={'index': 'Alimento'})
        df_b = df_b.drop(columns=[c for c in ['h','p','g','kcal','H','P','G','Kcal'] if c in df_b.columns])
        df_ed = st.data_editor(df_b, num_rows="dynamic", use_container_width=True)
        if st.button("Guardar Base"):
            st.session_state.base_alimentos = df_ed.set_index('Alimento').to_dict('index')
            guardar_alimentos(); st.rerun()

    with tabs[4]: # HISTORIAL
        if datos["registros"]:
            f_s = st.date_input("Día:", value=date.today())
            df_h = pd.DataFrame(datos["registros"])
            df_d = df_h[df_h["Fecha"] == str(f_s)].copy()
            if not df_d.empty:
                st.data_editor(df_d, use_container_width=True, key=f"h_{f_s}")
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='xlsxwriter') as w:
                    df_d.to_excel(w, index=False)
                st.download_button("📥 Excel", data=out.getvalue(), file_name=f"{user}_{f_s}.xlsx")