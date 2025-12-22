# core/google_maps.py
import googlemaps
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv 
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

# .env dosyasını güvenli bir şekilde yükle
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GOOGLE_API_KEY")

def get_coordinates(locations):
    coords = []
    
    # Anahtarı kontrol et (Hata ayıklama için terminale yazdırır)
    if not API_KEY:
        print("❌ HATA: API Key okunamadı!")
        return pd.DataFrame() # Boş dön
    
    try:
        gmaps = googlemaps.Client(key=API_KEY)
    except Exception as e:
        print(f"❌ CLIENT HATASI: {e}")
        return pd.DataFrame()

    print("📍 Google Maps'ten veri çekiliyor...")
    for loc in locations:
        try:
            geocode_result = gmaps.geocode(loc)
            if geocode_result:
                lat = geocode_result[0]['geometry']['location']['lat']
                lng = geocode_result[0]['geometry']['location']['lng']
                coords.append({'name': loc, 'lat': lat, 'lon': lng})
            else:
                # Bulamazsa varsayılan
                coords.append({'name': loc, 'lat': 37.8716, 'lon': 32.4852})
        except Exception as e:
            print(f"Hata ({loc}): {e}")
            coords.append({'name': loc, 'lat': 37.8716, 'lon': 32.4852})
            
    return pd.DataFrame(coords)

def get_distance_matrix(coords_df):
    if coords_df.empty: return np.zeros((1, 1))
    n = len(coords_df)
    dist_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                lat1, lon1 = coords_df.iloc[i]['lat'], coords_df.iloc[i]['lon']
                lat2, lon2 = coords_df.iloc[j]['lat'], coords_df.iloc[j]['lon']
                
                R = 6371000 
                phi1, phi2 = radians(lat1), radians(lat2)
                dphi = radians(lat2 - lat1)
                dlambda = radians(lon2 - lon1)
                a = sin(dphi/2)**2 + cos(phi1)*cos(phi2) * sin(dlambda/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                dist = R * c
                
                dist_matrix[i][j] = dist
            else:
                dist_matrix[i][j] = 999999999 

    return dist_matrix