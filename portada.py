import streamlit as st
import base64
import pandas as pd
import json
import os
from datetime import date

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CUCHITOS GYM", layout="wide")

# --- 2. PERSISTENCIA DE DATOS ---
def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        try:
            with open("usuarios.json", "r") as f:
                return json.load(f)
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

# Inicialización de estados
if "datos_usuarios" not in st.session_state: st.session_state.datos_usuarios = cargar_usuarios()
if "base_alimentos" not in st.session_state: st.session_state.base_alimentos = cargar_alimentos()
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "pin_correcto" not in st.session_state: st.session_state.pin_correcto = False
if "modo_crear" not in st.session_state: st.session_state.modo_crear = False
if "entrenamiento_actual" not in st.session_state: st.session_state.entrenamiento_actual = []

# --- 3. CSS: CENTRADO Y POSICIÓN DEL PIN ---
def aplicar_estilos(archivo_fondo=None, estado="app"):
    b64 = ""
    if archivo_fondo and os.path.exists(archivo_fondo):
        with open(archivo_fondo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    
    bg_style = f'background: url("data:image/png;base64,{b64}"); background-size: cover; background-position: center;' if b64 else 'background-color: #121212;'

    # Ajuste de altura para el PIN (pegado abajo si es portada)
    justify_content = "flex-end" if estado == "portada" else "center"
    padding_bottom = "50px" if estado == "portada" else "0px"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} }}
        [data-testid="stHeader"], .stDeployButton, header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}

        /* Contenedor principal */
        .main .block-container {{
            max-width: 100vw !important;
            height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: {justify_content} !important; 
            align-items: center !important;
            text-align: center !important;
            padding-bottom: {padding_bottom} !important;
        }}

        /* Bloques verticales centrados */
        [data-testid="stVerticalBlock"] {{
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }}

        [data-testid="stImage"] {{ display: flex !important; justify-content: center !important; margin: 0 auto !important; width: 100% !important; }}
        [data-testid="stImage"] img {{ border-radius: 50% !important; border: 4px solid #FF8C00 !important; }}

        /* Centrado de botones */
        div.stButton {{
            text-align: center;
            display: flex;
            justify-content: center;
        }}

        .stButton button {{
            background-color: #FF8C00 !important; color: white !important; font-size: 20px !important;
            height: 60px !important; width: 85vw !important; max-width: 400px !important;
            border-radius: 15px !important; border: 2px solid black !important;
            font-weight: 900 !important; box-shadow: 4px 4px 0px #000;
            margin: 10px auto !important;
        }}

        .stNumberInput, .stSlider, .stSelectbox, .stTextInput, .stFileUploader, .stDateInput {{
            width: 85vw !important; max-width: 450px !important; margin: 8px auto !important;
        }}
        
        h1, h2, h3, h4, p, label {{ color: white !important; text-align: center !important; width: 100%; }}
        
        /* Pestañas */
        .stTabs [data-baseweb="tab-list"] {{
            display: flex !important;
            justify-content: space-around !important;
            width: 100% !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            flex-grow: 1 !important;
            text-align: center !important;
            font-size: 28px !important; 
            padding: 10px !important;
        }}

        /* Caja métrica */
        .metric-container {{
            background-color: #1a1a1a; padding: 15px; border-radius: 15px;
            border: 2px solid #FF8C00; margin-bottom: 20px; width: 85vw; max-width: 450px;
            text-align: center !important;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. FUNCIONES DE PESTAÑAS ---

def pestana_usuario(user, datos):
    st.title(f"PERFIL: {user.upper()}")
    if datos.get("foto"): st.image(datos["foto"], width=180)
    nueva_foto = st.file_uploader("Cambiar foto", type=["jpg", "png"], label_visibility="collapsed")
    if nueva_foto:
        img_b64 = base64.b64encode(nueva_foto.read()).decode()
        st.session_state.datos_usuarios[user]["foto"] = f"data:image/png;base64,{img_b64}"
        guardar_usuarios(); st.rerun()

    edad = st.number_input("EDAD", value=int(datos.get("edad", 30)), min_value=1)
    peso = st.number_input("PESO (kg)", value=float(datos.get("peso", 70.0)), step=0.1)
    act = st.slider("ACTIVIDAD (1-10)", 1, 10, value=int(datos.get("actividad", 5)))
    
    if st.button("GUARDAR DATOS"):
        st.session_state.datos_usuarios[user].update({"edad": edad, "peso": peso, "actividad": act})
        guardar_usuarios(); st.success("¡Datos actualizados!"); st.rerun()

def pestana_nutricion(user, datos):
    st.title("🥗 NUTRICIÓN")
    hoy = str(date.today())
    # Cálculo objetivo
    cal_objetivo = round(((10 * datos['peso']) + (6.25 * 170) - (5 * datos['edad']) + 5) * (1.2 + (datos['actividad'] * 0.07)))
    registros_hoy = [r for r in datos.get("registros", []) if r["Fecha"] == hoy]
    cal_consumidas = sum([r.get("Kcal", 0) for r in registros_hoy])

    st.markdown(f"""<div class="metric-container">
        <h2 style='margin:0; color:#FF8C00;'>Restan: {cal_objetivo - cal_consumidas} kcal</h2>
        <p style='margin:0;'>Objetivo: {cal_objetivo} | Consumidas: {cal_consumidas}</p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.modo_crear:
        opciones = sorted(list(st.session_state.base_alimentos.keys()))
        sel = st.selectbox("Selecciona alimento:", ["---"] + opciones)

        if sel != "---":
            info = st.session_state.base_alimentos[sel]
            unidades_v = ["Gr", "Ml", "Taza", "Unidad", "Cucharada"]
            medida = str(info.get("Medida", "")).strip()

            if medida not in unidades_v:
                st.warning(f"⚠️ '{sel}' sin unidad.")
                nueva_m = st.selectbox("Asignar unidad:", ["---"] + unidades_v, key="nut_un")
                if nueva_m != "---":
                    if st.button("GUARDAR UNIDAD"):
                        st.session_state.base_alimentos[sel]["Medida"] = nueva_m
                        guardar_alimentos(); st.rerun()
            else:
                st.info(f"{medida} | {info.get('Calorías', 0)} kcal/100 o u.")
                cant = st.number_input(f"Cantidad ({medida})", min_value=0.0, step=1.0)
                if st.button("REGISTRAR CONSUMO"):
                    f = (cant/100 if medida in ["Gr", "Ml"] else cant)
                    st.session_state.datos_usuarios[user]["registros"].append({
                        "Fecha": hoy, "Alimento": sel, "Kcal": round(info.get("Calorías", 0) * f),
                        "Proteína": round(info.get("Proteína", 0) * f, 1),
                        "Carbos": round(info.get("Carbos", 0) * f, 1),
                        "Grasa": round(info.get("Grasa", 0) * f, 1)
                    })
                    guardar_usuarios(); st.rerun()
        
        st.write("---")
        if st.button("➕ AÑADIR NUEVO ALIMENTO"): st.session_state.modo_crear = True; st.rerun()
    else:
        st.markdown("### 🆕 Nuevo Alimento")
        n_n = st.text_input("Nombre:").title()
        c_n = st.number_input("Kcal:", min_value=0.0)
        p_n = st.number_input("Proteína:", min_value=0.0)
        h_n = st.number_input("Carbos:", min_value=0.0)
        g_n = st.number_input("Grasa:", min_value=0.0)
        u_n = st.selectbox("Unidad:", ["Gr", "Ml", "Taza", "Unidad", "Cucharada"])
        if st.button("💾 GUARDAR BASE"):
            if n_n:
                st.session_state.base_alimentos[n_n] = {"Calorías": c_n, "Proteína": p_n, "Carbos": h_n, "Grasa": g_n, "Medida": u_n}
                guardar_alimentos(); st.session_state.modo_crear = False; st.rerun()
        if st.button("❌ CANCELAR"): st.session_state.modo_crear = False; st.rerun()

def pestana_deporte(user, datos):
    st.title("🏋️ DEPORTE")
    deporte = st.selectbox("Entrenamiento:", ["---", "PESAS", "SPINNING", "PASOS"])
    hoy = str(date.today())

    if deporte == "PESAS":
        ejer = st.text_input("Ejercicio").upper()
        col1, col2, col3 = st.columns(3)
        with col1: s = st.number_input("Series", 0)
        with col2: r = st.number_input("Reps", 0)
        with col3: p = st.number_input("Kg", 0.0)
        if st.button("➕ AÑADIR EJERCICIO"):
            if ejer:
                st.session_state.entrenamiento_actual.append({"Ejercicio": ejer, "S": s, "R": r, "Kg": p})
                st.rerun()
        if st.session_state.entrenamiento_actual:
            st.table(pd.DataFrame(st.session_state.entrenamiento_actual))
            if st.button("💾 GUARDAR TODO"):
                res = f"PESAS: {len(st.session_state.entrenamiento_actual)} ejer."
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": res, "Kcal": 0, "Detalle": st.session_state.entrenamiento_actual})
                st.session_state.entrenamiento_actual = []
                guardar_usuarios(); st.rerun()

    elif deporte == "SPINNING":
        t = st.number_input("Tiempo (min)", 0)
        k = st.number_input("Km", 0.0)
        c = st.number_input("Kcal quemadas", 0)
        if st.button("REGISTRAR SPINNING"):
            st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": "🔥 SPINNING", "Kcal": -c, "Detalle": f"{t}min | {k}km"})
            guardar_usuarios(); st.rerun()

    elif deporte == "PASOS":
        p = st.number_input("Pasos diarios", 0)
        if st.button("REGISTRAR PASOS"):
            st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": "🔥 PASOS", "Kcal": -int(p*0.04), "Cantidad": p})
            guardar_usuarios(); st.rerun()

def pestana_base_datos():
    st.title("💾 GESTIÓN BD")
    opciones = sorted(list(st.session_state.base_alimentos.keys()))
    sel = st.selectbox("Buscar para editar:", ["---"] + opciones)
    if sel != "---":
        info = st.session_state.base_alimentos[sel]
        c = st.number_input("Calorías", value=float(info.get("Calorías", 0)))
        p = st.number_input("Proteína", value=float(info.get("Proteína", 0)))
        lista_u = ["Gr", "Ml", "Taza", "Unidad", "Cucharada"]
        med_g = str(info.get("Medida", "")).strip()
        idx = (lista_u.index(med_g) + 1) if med_g in lista_u else 0
        m = st.selectbox("Unidad:", ["---"] + lista_u, index=idx)
        if st.button("💾 ACTUALIZAR"):
            if m != "---":
                st.session_state.base_alimentos[sel].update({"Calorías": c, "Proteína": p, "Medida": m})
                guardar_alimentos(); st.success("Actualizado"); st.rerun()
        if st.button("🗑️ ELIMINAR"):
            del st.session_state.base_alimentos[sel]
            guardar_alimentos(); st.rerun()

def pestana_historial(user, datos):
    st.title("📊 HISTORIAL")
    fecha_sel = st.date_input("Fecha:", value=date.today())
    registros = [r for r in datos.get("registros", []) if r["Fecha"] == str(fecha_sel)]
    if registros:
        st.table(pd.DataFrame(registros)[["Alimento", "Kcal"]])
        idx = st.number_input("Fila a borrar (0, 1...)", 0, max(0, len(registros)-1))
        if st.button("CONFIRMAR ELIMINACIÓN"):
            st.session_state.datos_usuarios[user]["registros"].remove(registros[idx])
            guardar_usuarios(); st.rerun()

# --- 5. NAVEGACIÓN ---
if not st.session_state.pin_correcto:
    aplicar_estilos("portada.png", estado="portada")
    # El PIN aparecerá abajo por el flex-end del CSS
    pin = st.text_input("", type="password", placeholder="PIN", key="login_pin")
    if pin == "1234": st.session_state.pin_correcto = True; st.rerun()
elif not st.session_state.autenticado:
    aplicar_estilos("portada.png", estado="seleccion")
    if st.button("DAVID"): st.session_state.usuario_actual = "David"; st.session_state.autenticado = True; st.rerun()
    if st.button("Mª JOSE"): st.session_state.usuario_actual = "Maria Jose"; st.session_state.autenticado = True; st.rerun()
else:
    aplicar_estilos(None)
    user = st.session_state.usuario_actual
    datos = st.session_state.datos_usuarios[user]
    t1, t2, t3, t4, t5 = st.tabs(["👤", "🥗", "🏋️", "💾", "📊"])
    with t1: pestana_usuario(user, datos)
    with t2: pestana_nutricion(user, datos)
    with t3: pestana_deporte(user, datos)
    with t4: pestana_base_datos()
    with t5: pestana_historial(user, datos)

    if st.sidebar.button("LOGOUT"):
        st.session_state.autenticado = False; st.session_state.pin_correcto = False; st.rerun()