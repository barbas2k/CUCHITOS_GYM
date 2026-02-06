import streamlit as st
import base64
import pandas as pd
import json
import os
import io
from datetime import date

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CUCHITOS GYM", layout="centered")

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

# 3. CSS
def aplicar_estilos(archivo_fondo=None):
    b64 = ""
    if archivo_fondo and os.path.exists(archivo_fondo):
        with open(archivo_fondo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{ background: {f'url("data:image/png;base64,{b64}")' if b64 else "#121212"}; background-size: cover; background-position: center; }}
        [data-testid="stHeader"], .stDeployButton, header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
        .block-container {{ padding-top: 1.5rem !important; }}
        
        [data-testid="stImage"] {{ display: flex; justify-content: center; }}
        [data-testid="stImage"] img {{ 
            border-radius: 50% !important; 
            border: 4px solid #FF8C00 !important; 
            object-fit: cover !important; 
            width: 180px !important; 
            height: 180px !important; 
        }}
        
        .titulo-arriba {{ position: fixed; top: 30px; left: 0; width: 100%; text-align: center; color: #FF8C00; font-size: 50px; font-weight: 900; text-shadow: 4px 4px 10px #000; z-index: 1000; }}
        .stButton > button {{ background-color: #FF8C00 !important; color: white !important; font-weight: bold !important; border: 2px solid black !important; border-radius: 12px !important; width: 100%; }}
        [data-testid="stMetricValue"] {{ color: #FF8C00 !important; font-weight: bold; text-align: center; }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. ACCESO ---
if not st.session_state.autenticado:
    aplicar_estilos("portada.png")
    st.markdown('<div class="titulo-arriba">CUCHITOS<br>GYM</div>', unsafe_allow_html=True)
    st.markdown("<br>"*14, unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("ACCESO DAVID 👑", use_container_width=True):
            st.session_state.usuario_actual = "David"; st.session_state.autenticado = True; st.rerun()
    with col_b:
        if st.button("ACCESO MARIA JOSE 🎀", use_container_width=True):
            st.session_state.usuario_actual = "Maria Jose"; st.session_state.autenticado = True; st.rerun()

else:
    aplicar_estilos() 
    user = st.session_state.usuario_actual
    datos = st.session_state.datos_usuarios[user]
    pe_actual = datos.get("peso", 80.0)
    tabs = st.tabs(["👤 Perfil", "🥗 Nutrición", "🏋️ Deporte", "💾 Alimentos", "📊 Historial"])

    # --- TAB 1: PERFIL ---
    with tabs[0]:
        st.markdown(f"### Perfil de {user}")
        foto_url = datos.get("foto") or "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
        st.image(foto_url)
        up_f = st.file_uploader("Cambiar Foto", type=["jpg", "png"], key="up_p_v15", label_visibility="collapsed")
        if up_f:
            st.session_state.datos_usuarios[user]["foto"] = f"data:image/png;base64,{base64.b64encode(up_f.read()).decode()}"
            guardar_usuarios(); st.rerun()

        with st.container(border=True):
            new_pe = st.number_input("Peso Actual (kg)", value=float(datos.get("peso", 80.0)), step=0.1)
            new_ed = st.number_input("Edad", value=int(datos.get("edad", 30)))
            if st.button("Guardar Perfil 💾"):
                st.session_state.datos_usuarios[user].update({"peso": new_pe, "edad": new_ed})
                guardar_usuarios(); st.success("¡Perfil actualizado!")
        if st.button("Cerrar Sesión 🚪"): st.session_state.autenticado = False; st.rerun()

    # --- TAB 2: NUTRICIÓN ---
    with tabs[1]:
        st.markdown("#### Registro de Comidas")
        hoy_str = str(date.today())
        regs_hoy = [r for r in datos["registros"] if r["Fecha"] == hoy_str]
        total_k = sum(r.get("Kcal", 0) for r in regs_hoy)
        st.metric("🔥 BALANCE HOY", f"{total_k:.1f} Kcal")
        opciones = ["--- Seleccionar ---", "✨ ENTRADA MANUAL", "➕ NUEVO ALIMENTO BASE"] + sorted(list(st.session_state.base_alimentos.keys()))
        seleccion = st.selectbox("Buscar:", opciones)
        if seleccion == "✨ ENTRADA MANUAL":
            with st.container(border=True):
                nom_m = st.text_input("Concepto:")
                c1, c2, c3, c4 = st.columns(4)
                p_m, h_m, g_m, k_m = c1.number_input("P"), c2.number_input("H"), c3.number_input("G"), c4.number_input("Calorías")
                if st.button("Añadir Pack ✅"):
                    val_kcal = k_m if k_m > 0 else (p_m*4 + h_m*4 + g_m*9)
                    st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy_str, "Momento": "Manual", "Alimento": nom_m or "Manual", "Cantidad": 1, "Medida": "Pack", "Kcal": round(val_kcal, 1), "Peso": pe_actual})
                    guardar_usuarios(); st.rerun()
        elif seleccion != "--- Seleccionar ---" and seleccion != "➕ NUEVO ALIMENTO BASE":
            m = st.session_state.base_alimentos[seleccion]
            cal_base, med = m.get('Calorías', 0), m.get('Medida', 'Gr')
            with st.container(border=True):
                mom = st.selectbox("Momento", ["Desayuno", "Comida", "Cena", "Snack"])
                cant = st.number_input(f"Cantidad ({med})", min_value=0.0)
                if st.button("Añadir ✅"):
                    val_k = cal_base * (cant/100) if med.lower() in ["gr", "ml"] else cal_base * cant
                    st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy_str, "Momento": mom, "Alimento": seleccion, "Cantidad": cant, "Medida": med, "Kcal": round(val_k, 1), "Peso": pe_actual})
                    guardar_usuarios(); st.rerun()

    # --- TAB 3: DEPORTE ---
    with tabs[2]:
        st.markdown("#### Registro de Deporte")
        tipo_e = st.selectbox("Tipo:", ["Descanso", "Gym", "Spinning", "Running", "Cardio"])
        if tipo_e == "Spinning":
            c1, c2, c3 = st.columns(3)
            km, tm, kc = c1.number_input("Km", 0.0), c2.number_input("Min", 0), c3.number_input("Kcal", 0)
            if st.button("Guardar Spinning ✅"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy_str, "Momento": "Deporte", "Alimento": f"Spinning ({km}km)", "Cantidad": tm, "Medida": "min", "Kcal": -abs(float(kc)), "Peso": pe_actual})
                guardar_usuarios(); st.rerun()
        else:
            pasos = st.number_input("Pasos", value=8000)
            if st.button(f"Guardar {tipo_e} ✅"):
                st.session_state.datos_usuarios[user]["registros"].append({"Fecha": hoy_str, "Momento": "Deporte", "Alimento": tipo_e, "Cantidad": pasos, "Medida": "pasos", "Kcal": 0, "Peso": pe_actual})
                guardar_usuarios(); st.rerun()

    # --- TAB 4: ALIMENTOS ---
    with tabs[3]:
        st.markdown("#### 💾 Base de Alimentos")
        df_base = pd.DataFrame(st.session_state.base_alimentos).T.reset_index().rename(columns={'index': 'Alimento'})
        df_base = df_base.drop(columns=[c for c in ['h','p','g','kcal'] if c in df_base.columns])
        df_ed_ali = st.data_editor(df_base, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_base_v15")
        if st.button("Guardar Cambios en Base 💾"):
            st.session_state.base_alimentos = df_ed_ali.set_index('Alimento').to_dict('index')
            guardar_alimentos(); st.rerun()

    # --- TAB 5: HISTORIAL (CON EXPORTACIÓN EXCEL) ---
    with tabs[4]:
        st.markdown("### 📊 Historial")
        if datos["registros"]:
            f_sel = st.date_input("Selecciona Día:", value=date.today())
            df_hist = pd.DataFrame(datos["registros"])
            df_dia = df_hist[df_hist["Fecha"] == str(f_sel)].copy()
            if not df_dia.empty:
                st.metric("Balance del día", f"{df_dia['Kcal'].sum():.1f} Kcal")
                df_editado = st.data_editor(df_dia, use_container_width=True, hide_index=True, num_rows="dynamic", key=f"ed_h_{f_sel}")
                if st.button("Confirmar y Guardar Cambios 💾"):
                    otros_dias = [r for r in datos["registros"] if r["Fecha"] != str(f_sel)]
                    st.session_state.datos_usuarios[user]["registros"] = otros_dias + df_editado.to_dict('records')
                    guardar_usuarios(); st.success("¡Guardado!"); st.rerun()
                
                # FUNCIÓN EXPORTAR A EXCEL (Añadido)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_dia.to_excel(writer, index=False, sheet_name='Diario')
                
                st.download_button(
                    label="📥 Exportar este día a Excel",
                    data=output.getvalue(),
                    file_name=f"CuchitosGym_{user}_{f_sel}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else: st.info("Sin registros este día.")
            
            st.divider()
            if st.button("🗑️ Vaciar Historial Completo"):
                st.session_state.datos_usuarios[user]["registros"] = []
                guardar_usuarios(); st.rerun()