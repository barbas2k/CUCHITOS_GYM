import streamlit as st
import base64
import pandas as pd
import json
import os
from datetime import date, timedelta
import io

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
        "David": {"foto": None, "edad": 30, "peso": 80.0, "actividad": 5, "registros": [], "historial_peso": []},
        "Maria Jose": {"foto": None, "edad": 25, "peso": 60.0, "actividad": 5, "registros": [], "historial_peso": []}
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

# --- 3. CSS: CENTRADO AGRESIVO, PIN ABAJO Y PESTAÑAS ANCHAS ---
def aplicar_estilos(archivo_fondo=None, estado="app"):
    b64 = ""
    if archivo_fondo and os.path.exists(archivo_fondo):
        with open(archivo_fondo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    
    bg_style = f'background: url("data:image/png;base64,{b64}"); background-size: cover; background-position: center;' if b64 else 'background-color: #121212;'
    
    justify_main = "flex-end" if estado == "portada" else "center"
    padding_main = "60px" if estado == "portada" else "0px"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} }}
        [data-testid="stHeader"], .stDeployButton, header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}

        [data-testid="stVerticalBlock"] {{
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }}

        .main .block-container {{
            max-width: 100vw !important;
            height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: {justify_main} !important; 
            align-items: center !important;
            text-align: center !important;
            padding-bottom: {padding_main} !important;
        }}

        [data-testid="stImage"] {{ display: flex !important; justify-content: center !important; margin: 0 auto !important; }}
        [data-testid="stImage"] img {{ border-radius: 50% !important; border: 4px solid #FF8C00 !important; }}

        div.stButton {{ text-align: center; display: flex; justify-content: center; }}
        .stButton button {{
            background-color: #FF8C00 !important; color: white !important; font-size: 20px !important;
            height: 60px !important; width: 85vw !important; max-width: 400px !important;
            border-radius: 15px !important; border: 2px solid black !important;
            font-weight: 900 !important; box-shadow: 4px 4px 0px #000;
            margin: 10px auto !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{ display: flex !important; justify-content: space-around !important; width: 100% !important; }}
        .stTabs [data-baseweb="tab"] {{ flex-grow: 1 !important; text-align: center !important; font-size: 28px !important; padding: 10px !important; }}

        .metric-container {{
            background-color: #1a1a1a; padding: 15px; border-radius: 15px;
            border: 2px solid #FF8C00; margin-bottom: 20px; width: 85vw; max-width: 450px;
            display: flex !important; flex-direction: column !important;
            align-items: center !important; justify-content: center !important;
            text-align: center !important;
        }}

        .stNumberInput, .stSlider, .stSelectbox, .stTextInput, .stFileUploader, .stDateInput, .stMultiSelect {{
            width: 85vw !important; max-width: 450px !important; margin: 8px auto !important;
        }}
        
        h1, h2, h3, h4, p, label {{ color: white !important; text-align: center !important; width: 100%; }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. FUNCIONES DE PESTAÑAS ---

def pestana_usuario(user, datos):
    st.title(f"👤 PERFIL: {user.upper()}")
    if datos.get("foto"): st.image(datos["foto"], width=180)
    up = st.file_uploader("Cambiar foto", type=["jpg", "png"], label_visibility="collapsed")
    if up:
        st.session_state.datos_usuarios[user]["foto"] = f"data:image/png;base64,{base64.b64encode(up.read()).decode()}"
        guardar_usuarios(); st.rerun()
    edad = st.number_input("EDAD", value=int(datos.get("edad", 30)))
    peso = st.number_input("PESO (kg)", value=float(datos.get("peso", 70.0)))
    act = st.slider("ACTIVIDAD (1-10)", 1, 10, value=int(datos.get("actividad", 5)))
    if st.button("GUARDAR DATOS"):
        st.session_state.datos_usuarios[user].update({"edad": edad, "peso": peso, "actividad": act})
        guardar_usuarios(); st.success("¡Guardado!"); st.rerun()

def pestana_nutricion(user, datos):
    st.title("🥗 NUTRICIÓN")
    hoy = str(date.today())
    cal_objetivo = round(((10 * datos['peso']) + (6.25 * 170) - (5 * datos['edad']) + 5) * (1.2 + (datos['actividad'] * 0.07)))
    reg_hoy = [r for r in datos.get("registros", []) if r["Fecha"] == hoy]
    cons = sum([r.get("Kcal", 0) for r in reg_hoy if r.get("Kcal", 0) > 0])
    st.markdown(f'<div class="metric-container"><h2 style="color:#FF8C00;">Restan: {cal_objetivo - cons} kcal</h2><p>Objetivo: {cal_objetivo} | Consumidas: {cons}</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.modo_crear:
        sel = st.selectbox("Selecciona alimento:", ["---"] + sorted(list(st.session_state.base_alimentos.keys())))
        if sel != "---":
            info = st.session_state.base_alimentos[sel]
            medida = info.get("Medida", "Gr")
            cant = st.number_input(f"Cantidad ({medida})", min_value=0.0)
            if st.button("REGISTRAR CONSUMO"):
                f = (cant/100 if medida in ["Gr", "Ml"] else cant)
                st.session_state.datos_usuarios[user]["registros"].append({
                    "Fecha": hoy, "Alimento": sel, "Kcal": round(info.get("Calorías", 0) * f), "Tipo": "Comida"
                })
                guardar_usuarios(); st.rerun()
        if st.button("➕ NUEVO ALIMENTO"): st.session_state.modo_crear = True; st.rerun()
    else:
        n = st.text_input("Nombre:")
        c = st.number_input("Kcal:")
        m = st.selectbox("Medida:", ["Gr", "Ml", "Taza", "Unidad", "Cucharada"])
        if st.button("💾 GUARDAR"):
            st.session_state.base_alimentos[n] = {"Calorías": c, "Medida": m, "Proteína":0, "Carbos":0, "Grasa":0}
            guardar_alimentos(); st.session_state.modo_crear = False; st.rerun()
        if st.button("❌ CANCELAR"): st.session_state.modo_crear = False; st.rerun()

def pestana_deporte(user, datos):
    st.title("🏋️ DEPORTE")
    dep = st.selectbox("Entrenamiento:", ["---", "PESAS", "SPINNING", "PASOS"])
    hoy = str(date.today())
    if dep == "PESAS":
        ejer = st.text_input("Ejercicio").upper()
        if st.button("➕ AÑADIR"):
            st.session_state.entrenamiento_actual.append({"Ejer": ejer})
            st.rerun()
        if st.session_state.entrenamiento_actual:
            st.table(pd.DataFrame(st.session_state.entrenamiento_actual))
            if st.button("💾 GUARDAR ENTRENAMIENTO"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": "Pesas", "Kcal": 0, "Tipo": "Deporte"})
                st.session_state.entrenamiento_actual = []; guardar_usuarios(); st.rerun()
    elif dep == "SPINNING":
        kcal = st.number_input("Kcal quemadas", 0)
        if st.button("REGISTRAR"):
            st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy, "Alimento": "Spinning", "Kcal": -kcal, "Tipo": "Deporte"})
            guardar_usuarios(); st.rerun()

def pestana_base_datos():
    st.title("💾 GESTIÓN BD")
    opciones = sorted(list(st.session_state.base_alimentos.keys()))
    sel = st.selectbox("Buscar para editar:", ["---"] + opciones)
    if sel != "---":
        info = st.session_state.base_alimentos[sel]
        c = st.number_input("Calorías", value=float(info.get("Calorías", 0)))
        lista_u = ["Gr", "Ml", "Taza", "Unidad", "Cucharada"]
        m_g = info.get("Medida", "Gr")
        idx = (lista_u.index(m_g) + 1) if m_g in lista_u else 0
        m = st.selectbox("Unidad:", ["---"] + lista_u, index=idx)
        if st.button("💾 ACTUALIZAR"):
            st.session_state.base_alimentos[sel].update({"Calorías": c, "Medida": m})
            guardar_alimentos(); st.success("Actualizado"); st.rerun()
        if st.button("🗑️ ELIMINAR"):
            del st.session_state.base_alimentos[sel]
            guardar_alimentos(); st.rerun()

def pestana_historial(user, datos):
    st.title("📊 HISTORIAL")
    fecha_sel = st.date_input("Fecha:", value=date.today())
    regs = [r for r in datos.get("registros", []) if r["Fecha"] == str(fecha_sel)]
    if regs:
        st.table(pd.DataFrame(regs)[["Alimento", "Kcal"]])
        idx = st.number_input("Fila a borrar", 0, len(regs)-1)
        if st.button("CONFIRMAR ELIMINACIÓN"):
            st.session_state.datos_usuarios[user]["registros"].remove(regs[idx])
            guardar_usuarios(); st.rerun()
    else: st.info("Sin registros.")

def pestana_carga_masiva():
    st.title("📥 CARGA EXCEL")
    archivo = st.file_uploader("Sube .xlsx", type=["xlsx"], label_visibility="collapsed")
    if archivo:
        df = pd.read_excel(archivo)
        if st.button("🚀 IMPORTAR"):
            for _, r in df.iterrows():
                st.session_state.base_alimentos[str(r["Nombre"])] = {"Calorías": float(r["Calorías"]), "Medida": str(r["Medida"]), "Proteína":0, "Carbos":0, "Grasa":0}
            guardar_alimentos(); st.success("Importado"); st.rerun()

def pestana_progreso(user, datos):
    st.title("📈 PROGRESO")
    
    # 1. Gráfico de Peso
    historial = datos.get("historial_peso", [])
    if historial:
        st.subheader("Báscula Semanal")
        df_p = pd.DataFrame(historial)
        df_p['Fecha'] = pd.to_datetime(df_p['Fecha'])
        df_p = df_p.sort_values('Fecha').tail(7)
        st.line_chart(df_p.set_index('Fecha'))
    
    st.write("---")
    
    # 2. Exportador Inteligente
    st.subheader("📥 Exportador Inteligente")
    col1, col2 = st.columns(2)
    with col1: fecha_i = st.date_input("Desde", date.today() - timedelta(days=7))
    with col2: fecha_f = st.date_input("Hasta", date.today())
    
    tipo_exp = st.multiselect("Datos a incluir:", ["Comida", "Deporte"], default=["Comida", "Deporte"])
    
    if st.button("🚀 GENERAR ARCHIVO EXCEL"):
        df_total = pd.DataFrame(datos.get("registros", []))
        if not df_total.empty:
            df_total['Fecha'] = pd.to_datetime(df_total['Fecha']).dt.date
            mask = (df_total['Fecha'] >= fecha_i) & (df_total['Fecha'] <= fecha_f) & (df_total['Tipo'].isin(tipo_exp))
            df_filtrado = df_total.loc[mask]
            
            if not df_filtrado.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_filtrado.to_excel(writer, index=False, sheet_name='Registros')
                
                st.download_button(
                    label="⬇️ DESCARGAR EXCEL",
                    data=output.getvalue(),
                    file_name=f"Progreso_{user}_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No hay datos en ese rango de fechas.")
        else:
            st.warning("No hay registros guardados para exportar.")

# --- 5. NAVEGACIÓN ---
if not st.session_state.pin_correcto:
    aplicar_estilos("portada.png", estado="portada")
    pin = st.text_input("", type="password", placeholder="PIN", key="login_pin")
    if pin == "1234": st.session_state.pin_correcto = True; st.rerun()
elif not st.session_state.autenticado:
    aplicar_estilos("portada.png", estado="seleccion")
    if st.button("DAVID"): st.session_state.usuario_actual = "David"; st.session_state.autenticado = True; st.rerun()
    if st.button("MARIA JOSE"): st.session_state.usuario_actual = "Maria Jose"; st.session_state.autenticado = True; st.rerun()
else:
    user = st.session_state.usuario_actual
    datos = st.session_state.datos_usuarios[user]
    if not any(r["Fecha"] == str(date.today()) for r in datos.get("historial_peso", [])):
        aplicar_estilos("portada.png", estado="portada")
        st.markdown(f"### HOLA {user.upper()} \n ¿Cuánto pesas hoy?")
        peso_h = st.number_input("", value=float(datos['peso']), step=0.1)
        if st.button("REGISTRAR Y ENTRAR"):
            if "historial_peso" not in st.session_state.datos_usuarios[user]: st.session_state.datos_usuarios[user]["historial_peso"] = []
            st.session_state.datos_usuarios[user]["historial_peso"].append({"Fecha": str(date.today()), "Peso": peso_h})
            st.session_state.datos_usuarios[user]["peso"] = peso_h
            guardar_usuarios(); st.rerun()
    else:
        aplicar_estilos(None)
        t = st.tabs(["👤", "🥗", "🏋️", "💾", "📊", "📥", "📈"])
        with t[0]: pestana_usuario(user, datos)
        with t[1]: pestana_nutricion(user, datos)
        with t[2]: pestana_deporte(user, datos)
        with t[3]: pestana_base_datos()
        with t[4]: pestana_historial(user, datos)
        with t[5]: pestana_carga_masiva()
        with t[6]: pestana_progreso(user, datos)
        if st.sidebar.button("LOGOUT"):
            st.session_state.autenticado = False; st.session_state.pin_correcto = False; st.rerun()