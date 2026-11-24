import folium
from folium.plugins import HeatMap
import os

class MapView:
    def __init__(self, output_file="mapa_riesgo_nino.html"):
        self.output_file = output_file
        
    def generate_heat_map(self, df):
        print("Generando mapa de calor de precipitaciones...")
        
        # Uso de API de mapas gratuita Esri (no requiere API key y no bloquea acceso)
        esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
        esri_attr = "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community"
        
        m = folium.Map(location=[-9.19, -75.0152], zoom_start=5, tiles=esri_tiles, attr=esri_attr)
        
        heat_data = list(map(
            lambda row: [row['lat'], row['lon'], row['precipitation_mm']], 
            df.to_dict('records')
        ))
        
        HeatMap(heat_data, radius=25, blur=15, max_zoom=1).add_to(m)
        
        for _, row in df.iterrows():
            if row['risk_level'] != "Riesgo Normal":
                color = 'red' if 'Extremo' in row['risk_level'] else ('orange' if 'Alto' in row['risk_level'] else 'yellow')
                
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=10,
                    popup=f"{row['region']}: {row['risk_level']} ({row['precipitation_mm']:.1f} mm)",
                    color=color,
                    fill=True,
                    fill_color=color
                ).add_to(m)
                
        m.save(self.output_file)
        print(f"Mapa generado exitosamente en: {os.path.abspath(self.output_file)}")
        return os.path.abspath(self.output_file)
