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
    st.markdown("<h1 style='text-align: center; color: #FF8C00;'>BLOQUEO DE SEGURIDAD</h1>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        pin = st.text_input("Introduce el PIN de acceso", type="password")
        if pin == "1234":  # <--- TU PIN
            st.session_state.pin_correcto = True
            st.rerun()
        elif pin:
            st.error("PIN Incorrecto")
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

# 3. CSS CENTRADO TOTAL
def aplicar_estilos(archivo_fondo=None):
    b64 = ""
    if archivo_fondo and os.path.exists(archivo_fondo):
        with open(archivo_fondo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{ background: {f'url("data:image/png;base64,{b64}")' if b64 else "#121212"}; background-size: cover; background-position: center; }}
        [data-testid="stHeader"], .stDeployButton, header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
        .block-container {{ padding-top: 2rem !important; max-width: 600px !important; margin: auto !important; text-align: center !important; }}
        div[data-testid="stVerticalBlock"] > div {{ text-align: center !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        div.stButton > button {{ margin: 0 auto; display: block; width: 100% !important; background-color: #FF8C00 !important; color: white !important; font-weight: bold !important; border-radius: 12px !important; border: 2px solid black !important; }}
        [data-testid="stMetricValue"] {{ color: #FF8C00 !important; font-weight: 900 !important; }}
        [data-testid="stImage"] img {{ border-radius: 50% !important; border: 5px solid #FF8C00 !important; width: 180px !important; height: 180px !important; margin: 0 auto !important; }}
        .titulo-arriba {{ width: 100%; text-align: center; color: #FF8C00; font-size: 55px; font-weight: 900; text-shadow: 4px 4px 10px #000; margin-bottom: 20px; }}
        .stNumberInput, .stSelectbox, .stTextInput, .stSlider {{ width: 100% !important; text-align: center !important; }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. ACCESO ---
if not st.session_state.autenticado:
    aplicar_estilos("portada.png")
    st.markdown('<div class="titulo-arriba">CUCHITOS<br>GYM</div>', unsafe_allow_html=True)
    st.markdown("<br>"*12, unsafe_allow_html=True)
    col_izq, col_btn, col_der = st.columns([0.5, 3, 0.5])
    with col_btn:
        if st.button("ACCESO DAVID 👑"):
            st.session_state.usuario_actual = "David"; st.session_state.autenticado = True; st.rerun()
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("ACCESO MARIA JOSE 🎀"):
            st.session_state.usuario_actual = "Maria Jose"; st.session_state.autenticado = True; st.rerun()

else:
    aplicar_estilos() 
    user = st.session_state.usuario_actual
    datos = st.session_state.datos_usuarios[user]
    
    peso_v = float(datos.get("peso", 70.0))
    edad_v = int(datos.get("edad", 30))
    act_v = int(datos.get("actividad", 5))
    
    # Cálculo TMB Harris-Benedict
    base_cal = (10 * peso_v) + (6.25 * 170) - (5 * edad_v)
    adj = 5 if user == "David" else -161
    kcal_objetivo = (base_cal + adj) * (1.2 + (act_v * 0.05))

    tabs = st.tabs(["👤 Perfil", "🥗 Nutrición", "🏋️ Deporte", "💾 Alimentos", "📊 Historial"])

    with tabs[0]:
        st.markdown(f"## {user}")
        st.image(datos.get("foto") or "https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
        up = st.file_uploader("Foto", type=["jpg", "png"], key="up_p", label_visibility="collapsed")
        if up:
            st.session_state.datos_usuarios[user]["foto"] = f"data:image/png;base64,{base64.b64encode(up.read()).decode()}"
            guardar_usuarios(); st.rerun()
        n_p = st.number_input("Peso (kg)", value=peso_v, step=0.1)
        n_e = st.number_input("Edad", value=edad_v)
        n_a = st.slider("Actividad", 1, 10, value=act_v)
        if st.button("Guardar Datos 💾"):
            st.session_state.datos_usuarios[user].update({"peso": n_p, "edad": n_e, "actividad": n_a})
            guardar_usuarios(); st.success("¡Hecho!"); st.rerun()
        if st.button("Cerrar Sesión 🚪"): st.session_state.autenticado = False; st.rerun()

    with tabs[1]:
        st.markdown("### Balance de Hoy")
        hoy = str(date.today())
        regs = [r for r in datos["registros"] if r["Fecha"] == hoy]
        neto = sum(r.get("Kcal", 0) for r in regs)
        m1, m2, m3 = st.columns(3)
        m1.metric("Objetivo", f"{kcal_objetivo:.0f}")
        m2.metric("Consumo", f"{neto:.1f}")
        m3.metric("Faltan", f"{kcal_objetivo-neto:.0f}")
        
        st.divider()
        sel = st.selectbox("Alimento:", ["---"] + ["✨ MANUAL"] + sorted(list(st.session_state.base_alimentos.keys())))
        
        if sel == "✨ MANUAL":
            nom_m = st.text_input("¿Qué has comido?")
            kcal_m = st.number_input("Kcal totales:")
            if st.button("Añadir"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Momento": "Manual", "Alimento": nom_m or "Manual", "Kcal": round(kcal_m, 1)})
                guardar_usuarios(); st.rerun()
        elif sel != "---":
            m = st.session_state.base_alimentos.get(sel, {})
            cal_b, med = m.get('Calorías', 0), m.get('Medida', 'Gr')
            cant = st.number_input(f"Cantidad ({med})", min_value=0.0)
            if st.button("Añadir ✅"):
                factor = (cant/100) if med.lower() in ["gr", "ml"] else cant
                st.session_state.datos_usuarios[user]["registros"].append({
                    "Fecha": hoy, 
                    "Alimento": sel, 
                    "Kcal": round(cal_b * factor, 1)
                })
                guardar_usuarios(); st.rerun()

    with tabs[2]:
        st.markdown("### Registro de Deporte")
        tipo = st.selectbox("Entreno:", ["Gym", "Spinning", "Cardio", "Descanso"])
        if tipo == "Spinning":
            km = st.number_input("Km")
            kc = st.number_input("Kcal quemadas")
            if st.button("Guardar Spinning 🚴"):
                st.session_state.datos_usuarios[user]["registros"].append({
                    "Fecha": hoy, 
                    "Momento": "Deporte", 
                    "Alimento": f"Spinning ({km}km)", 
                    "Kcal": -abs(float(kc))
                })
                guardar_usuarios(); st.rerun()
        else:
            pasos = st.number_input("Pasos", value=8000)
            if st.button(f"Guardar {tipo} ✅"):
                st.session_state.datos_usuarios[user]["registros"].append({
                    "Fecha": hoy, 
                    "Momento": "Deporte", 
                    "Alimento": tipo, 
                    "Kcal": 0
                })
                guardar_usuarios(); st.rerun()

    with tabs[3]:
        st.markdown("### Base de Datos")
        df_base = pd.DataFrame(st.session_state.base_alimentos).T.reset_index().rename(columns={'index': 'Alimento'})
        df_base = df_base.drop(columns=[c for c in ['h','p','g','kcal','H','P','G','Kcal'] if c in df_base.columns])
        df_ed = st.data_editor(df_base, num_rows="dynamic", use_container_width=True, hide_index=True)
        if st.button("Guardar Tabla 💾"):
            st.session_state.base_alimentos = df_ed.set_index('Alimento').to_dict('index')
            guardar_alimentos(); st.rerun()

    with tabs[4]:
        st.markdown("### Historial")
        if datos["registros"]:
            f_s = st.date_input("Día:", value=date.today())
            df_h = pd.DataFrame(datos["registros"])
            df_d = df_h[df_h["Fecha"] == str(f_s)].copy()
            if not df_d.empty:
                df_dia_ed = st.data_editor(df_d, use_container_width=True, hide_index=True, num_rows="dynamic", key=f"h_{f_s}")
                if st.button("Guardar Cambios 💾"):
                    otros = [r for r in datos["registros"] if r["Fecha"] != str(f_s)]
                    st.session_state.datos_usuarios[user]["registros"] = otros + df_dia_ed.to_dict('records')
                    guardar_usuarios(); st.rerun()
                
                out = io.BytesIO()
                with pd.ExcelWriter(out, engine='xlsxwriter') as w:
                    df_d.to_excel(w, index=False)
                st.download_button("📥 Descargar Excel", data=out.getvalue(), file_name=f"Cuchitos_{user}_{f_s}.xlsx")
            else: st.info("Sin registros.")