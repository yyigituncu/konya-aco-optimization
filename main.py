# main.py
import streamlit as st
import pandas as pd
import pydeck as pdk 

# --- MODÜL YÜKLEME ---
try:
    from data.locations import LOCATIONS
    from core.google_maps import get_coordinates, get_distance_matrix
    from core.aco import AntColonyOptimizer
except ImportError as e:
    st.error(f"Dosya hatası: {e}")
    st.stop()

st.set_page_config(page_title="Konya Yemek Dağıtım", layout="wide", page_icon="🐜")
st.title("🐜 Konya Yemek Dağıtım Optimizasyonu (ACO)")
st.markdown("**Senaryo:** Yemek firmasının 20 öğrenci yurduna kuş uçuşu mesafelerle en kısa rotayı bulması.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Parametreler")
    n_ants = st.slider("Karınca Sayısı", 10, 100, 30)
    n_iterations = st.slider("İterasyon Sayısı", 10, 200, 50)
    run_btn = st.button("🚀 Rotayı Hesapla", type="primary")

# --- VERİ HAZIRLIĞI ---
if 'coords_df' not in st.session_state:
    with st.spinner('📍 Veriler yükleniyor...'):
        coords_df = get_coordinates(LOCATIONS)
        
        # --- RENK VE BOYUT AYARLARI ---
        # Varsayılan olarak herkes MAVİ [0, 120, 255] ve yarıçap 200
        coords_df['color_r'] = 0
        coords_df['color_g'] = 120
        coords_df['color_b'] = 255
        coords_df['radius'] = 200
        
        # 0. indeks MERKEZ olduğu için onu KIRMIZI [255, 0, 0] ve BÜYÜK yapalım
        coords_df.loc[0, 'name'] = "MERKEZ (Yemek Firması)"
        coords_df.loc[0, 'color_r'] = 255
        coords_df.loc[0, 'color_g'] = 0
        coords_df.loc[0, 'color_b'] = 0
        coords_df.loc[0, 'radius'] = 400

        st.session_state['coords_df'] = coords_df
        st.session_state['dist_matrix'] = get_distance_matrix(coords_df)

coords_df = st.session_state['coords_df']
dist_matrix = st.session_state['dist_matrix']

# --- HESAPLAMA ---
if run_btn:
    with st.spinner('🐜 Karıncalar çalışıyor...'):
        aco = AntColonyOptimizer(
            distances=dist_matrix, 
            n_ants=n_ants, 
            n_best=10, 
            n_iterations=n_iterations, 
            decay=0.6
        )
        best_path, best_dist, history = aco.run()
        
        st.session_state['best_path'] = best_path
        st.session_state['best_dist'] = best_dist
        st.session_state['history'] = history
        st.success(f"✅ Rota Bulundu! Toplam Mesafe: {best_dist/1000:.2f} km")

# --- HARİTA KATMANLARI ---
layers = []

# 1. NOKTA KATMANI (Renkli Daireler)
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=coords_df,
    get_position='[lon, lat]',
    get_fill_color='[color_r, color_g, color_b, 200]', # Veriden renk al
    get_radius='radius', # Veriden boyut al
    pickable=True,
    auto_highlight=True,
)
layers.append(scatter_layer)

# 2. MERKEZ YAZISI (Sadece merkezde yazı olsun)
center_df = coords_df.iloc[[0]]
text_layer = pdk.Layer(
    "TextLayer",
    data=center_df,
    get_position='[lon, lat]',
    get_text='name',
    get_color=[0, 0, 0],
    get_size=18,
    get_alignment_baseline="'top'",
    get_text_anchor="'middle'",
    background_color=[255, 255, 255, 200],
    font_family="Arial",
    font_weight="bold",
    pixel_offset=[0, 20]
)
layers.append(text_layer)

# 3. ROTA ÇİZGİLERİ (Hesaplandıysa)
if 'best_path' in st.session_state:
    best_path = st.session_state['best_path']
    
    line_data = []
    for i in range(len(best_path) - 1):
        start_idx = best_path[i]
        end_idx = best_path[i+1]
        
        line_data.append({
            "start": [coords_df.iloc[start_idx]['lon'], coords_df.iloc[start_idx]['lat']],
            "end": [coords_df.iloc[end_idx]['lon'], coords_df.iloc[end_idx]['lat']]
        })
        
    line_layer = pdk.Layer(
        "LineLayer",
        data=line_data,
        get_source_position="start",
        get_target_position="end",
        get_color=[255, 50, 50], # Kırmızı Çizgi
        get_width=4,
        pickable=False,
    )
    layers.insert(0, line_layer)

# --- HARİTAYI ÇİZ ---
view_state = pdk.ViewState(
    latitude=coords_df.loc[0, 'lat'],
    longitude=coords_df.loc[0, 'lon'],
    zoom=11, 
    pitch=0
)

# Tooltip: Üzerine gelince isim görünsün
r = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style=None, 
    tooltip={"text": "{name}"} 
)

st.pydeck_chart(r)

# --- GRAFİK VE LİSTE ---
if 'best_path' in st.session_state:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Optimizasyon Grafiği")
        st.line_chart(st.session_state['history'])
        
    with col2:
        st.subheader("📋 Rota Sıralaması")
        rota_isimleri = [coords_df.loc[i, 'name'] for i in st.session_state['best_path']]
        
        txt_output = ""
        for i, yer in enumerate(rota_isimleri):
            if i == 0: 
                txt_output += f"🔴 **BAŞLANGIÇ (MERKEZ):** {yer}\n\n"
            elif i == len(rota_isimleri)-1:
                txt_output += f"🔴 **BİTİŞ (MERKEZ):** {yer}"
            else:
                txt_output += f"🔵 {i}. {yer}\n\n"
        
        st.markdown(txt_output)
else:
    st.info("👈 Sol taraftaki 'Rotayı Hesapla' butonuna basarak en kısa yolu bulabilirsin.")