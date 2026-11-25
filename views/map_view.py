"""
Vista Cartográfica Geoespacial con Folium
Genera mapas interactivos con capas de calor, marcadores clasificados por severidad,
ventanas emergentes descriptivas, leyenda cartográfica y advertencia de fuente simulada/real.
"""

from datetime import datetime
import os
from typing import Optional
import folium
from folium.plugins import HeatMap
import pandas as pd
from branca.element import MacroElement, Template


class MapView:
    """
    Generador de visualización geoespacial interactiva para el monitoreo de El Niño.
    """

    DEFAULT_OUTPUT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "mapa_riesgo_nino.html")
    )

    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file or self.DEFAULT_OUTPUT

    def generate_heat_map(
        self,
        df: pd.DataFrame,
        source_title: str = "Simulación Estocástica",
        is_simulation: bool = True
    ) -> str:
        """
        Construye el mapa interactivo con Leaflet/Folium, integrando:
        - Capa base topográfica de Esri
        - Capa de densidad de calor (HeatMap) de precipitaciones
        - Marcadores circulares con colores por severidad
        - Popups con detalles meteorológicos
        - Leyenda cartográfica
        - Banner de trazabilidad (Simulado vs Real)
        
        Returns:
            str: Ruta absoluta del archivo HTML generado.
        """
        # Centro geográfico aproximado del Perú
        center_lat, center_lon = -9.19, -75.0152
        
        # Tiles gratuitos de alta resolución Esri World Topo Map
        esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
        esri_attr = "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN"

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles=esri_tiles,
            attr=esri_attr
        )

        # 1. Capa de Calor (HeatMap) ponderada por precipitación en mm
        if not df.empty and "precipitation_mm" in df.columns:
            heat_data = [
                [float(row["lat"]), float(row["lon"]), float(row["precipitation_mm"])]
                for _, row in df.iterrows()
                if pd.notnull(row.get("lat")) and pd.notnull(row.get("lon"))
            ]
            if heat_data:
                HeatMap(
                    heat_data,
                    name="Mapa de Calor de Lluvias",
                    radius=28,
                    blur=16,
                    max_zoom=6
                ).add_to(m)

        # 2. Marcadores por Nivel de Riesgo
        color_map = {
            "Riesgo de Inundacion Extremo": "#D32F2F",   # Rojo
            "Riesgo de Inundacion Alto": "#F57C00",      # Naranja
            "Riesgo Moderado": "#FBC02D",              # Amarillo
            "Riesgo Normal": "#388E3C",                # Verde
            "Dato Invalido": "#757575",                # Gris
        }

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for _, row in df.iterrows():
            lat = row.get("lat")
            lon = row.get("lon")
            if pd.isnull(lat) or pd.isnull(lon):
                continue

            region = str(row.get("region", "Desconocido"))
            risk = str(row.get("risk_level", "Riesgo Normal"))
            rain = float(row.get("precipitation_mm", 0.0))
            temp = float(row.get("temperature_c", 0.0))
            engine = str(row.get("engine_used", "Python RuleEngine"))
            
            color = color_map.get(risk, "#757575")

            popup_html = f"""
            <div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.5; min-width: 220px;">
                <h4 style="margin: 0 0 6px 0; color: #1E3A8A; border-bottom: 2px solid {color}; padding-bottom: 3px;">
                    {region}
                </h4>
                <b>Nivel de Riesgo:</b> <span style="color: {color}; font-weight: bold;">{risk}</span><br>
                <b>Precipitación:</b> {rain:.2f} mm<br>
                <b>Temperatura:</b> {temp:.2f} °C<br>
                <b>Motor de Inferencia:</b> {engine}<br>
                <b>Tipo de Fuente:</b> {'Simulación Estocástica' if is_simulation else 'Medición Real'}<br>
                <small style="color: #666;">Generado: {timestamp_str}</small>
            </div>
            """

            folium.CircleMarker(
                location=[lat, lon],
                radius=11 if "Extremo" in risk or "Alto" in risk else 8,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{region}: {risk} ({rain:.1f} mm)",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                weight=2
            ).add_to(m)

        # 3. Leyenda Cartográfica y Banner Flotante
        banner_badge = (
            '<span style="background-color: #EF4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">SIMULACIÓN ACADÉMICA</span>'
            if is_simulation else
            '<span style="background-color: #10B981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">DATOS EN VIVO</span>'
        )

        legend_html = f"""
        {{% macro html(this, kwargs) %}}
        <div style="
            position: fixed; 
            bottom: 30px; left: 30px; width: 280px; height: auto;
            background-color: rgba(255, 255, 255, 0.95);
            border: 2px solid #CBD5E1;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            z-index: 9999;
            font-size: 12px;
            padding: 12px;
            font-family: Arial, sans-serif;
        ">
            <h4 style="margin: 0 0 8px 0; color: #0F172A; font-size: 13px;">
                🌊 Fenómeno de El Niño - Perú
            </h4>
            <div style="margin-bottom: 8px;"><b>Fuente:</b> {banner_badge}</div>
            <div style="margin-bottom: 4px;"><span style="color: #D32F2F; font-size: 16px;">●</span> <b>Extremo:</b> > 120 mm y > 30°C</div>
            <div style="margin-bottom: 4px;"><span style="color: #F57C00; font-size: 16px;">●</span> <b>Alto:</b> > 80 mm (o >120mm sin calor)</div>
            <div style="margin-bottom: 4px;"><span style="color: #FBC02D; font-size: 16px;">●</span> <b>Moderado:</b> 40 a 80 mm</div>
            <div style="margin-bottom: 4px;"><span style="color: #388E3C; font-size: 16px;">●</span> <b>Normal:</b> &le; 40 mm</div>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #E2E8F0;">
            <small style="color: #64748B;">Mapa interactivo generado con Folium / Esri</small>
        </div>
        {{% endmacro %}}
        """

        macro = MacroElement()
        macro._template = Template(legend_html)
        m.get_root().add_child(macro)

        folium.LayerControl().add_to(m)
        m.save(self.output_file)
        return os.path.abspath(self.output_file)
