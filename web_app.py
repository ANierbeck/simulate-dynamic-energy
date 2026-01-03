#!/usr/bin/env python3
"""
Hauptanwendung für die Dynamische Stromtarif-Analyse
Reine Streamlit-Lösung - alle Funktionen in einer Weboberfläche
"""

import sys
import os
from datetime import datetime, timedelta
import logging

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importiere alle benötigten Module
from core import CONFIG, TARIFF_PROVIDERS
from core.data import (fetch_senec_house_power_data_v1, 
                      fetch_senec_solar_generated_power_v1,
                      fetch_senec_battery_power_v1,
                      fetch_senec_grid_power_v1,
                      generate_sample_tariff_data)
from core.data.providers_mock import MockTariffProvider
from core.data.influxdb_market import fetch_market_prices
from core.analysis.realtime import analyze_realtime
from core.analysis import analyze_historical_consumption, analyze_monthly_consumption, calculate_costs, find_best_alternative, get_consumption_by_hour

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion für die Streamlit Weboberfläche"""
    
    # Streamlit Konfiguration
    st.set_page_config(
        page_title="Dynamische Stromtarif-Analyse",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Auto-Refresh alle 60 Sekunden (standardmäßig aktiviert)
    st.markdown("""
    <script>
    // Funktion zum Auto-Refresh
    function startAutoRefresh() {
        // Speichere den Auto-Refresh-Status im sessionStorage
        const autoRefreshEnabled = sessionStorage.getItem('autoRefreshEnabled');
        
        if (autoRefreshEnabled === 'true' || autoRefreshEnabled === null) {
            // Standardmäßig aktiviert oder explizit aktiviert
            setTimeout(function() {
                window.location.reload();
            }, 60000); // 60 Sekunden = 60000 Millisekunden
        }
    }
    
    // Starte Auto-Refresh beim Laden der Seite
    window.onload = startAutoRefresh;
    </script>
    """, unsafe_allow_html=True)
    
    # Titel und Beschreibung
    st.title("⚡ Dynamische Stromtarif-Analyse")
    
    st.markdown("""
    Diese Anwendung analysiert Ihren Stromverbrauch und vergleicht verschiedene dynamische Stromtarife,
    um Einsparpotenziale zu identifizieren.
    """)
    
    # Initialize variables for data loading status
    consumption_data = None
    tariff_data = None
    start_time = None
    end_time = None
    
    # Determine time range first
    analysis_period = st.sidebar.selectbox(
        "Analysezeitraum",
        ["Letzte 7 Tage", "Letzte 30 Tage", "Letzter Monat", "Letzte 3 Monate", "Benutzerdefiniert"],
        index=1
    )
    
    # Benutzerdefinierter Zeitrahmen
    if analysis_period == "Benutzerdefiniert":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Startdatum", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("Enddatum", datetime.now())
        start_time = datetime.combine(start_date, datetime.min.time())
        end_time = datetime.combine(end_date, datetime.max.time())
    else:
        end_time = datetime.now()
        if analysis_period == "Letzte 7 Tage":
            start_time = end_time - timedelta(days=7)
        elif analysis_period == "Letzte 30 Tage":
            start_time = end_time - timedelta(days=30)
        elif analysis_period == "Letzter Monat":
            start_time = end_time - timedelta(days=30)
        elif analysis_period == "Letzte 3 Monate":
            start_time = end_time - timedelta(days=90)
        else:
            start_time = end_time - timedelta(days=30)
    
    # Load all data sources
    with st.spinner("Lade Energiedaten..."):
        # Fetch all power data sources
        house_power_data = fetch_senec_house_power_data_v1(start_time, end_time)
        solar_generated_data = fetch_senec_solar_generated_power_v1(start_time, end_time)
        battery_power_data = fetch_senec_battery_power_v1(start_time, end_time)
        grid_power_data = fetch_senec_grid_power_v1(start_time, end_time)
        tariff_data = fetch_market_prices(start_time, end_time)
        
        # Note: Raw data is in Wh, but our analysis expects W
        # Since we're dealing with power (instantaneous measurements), the values should be in W
        # If the data is actually in Wh, we need to understand the time interval
        # For now, we'll assume the data is correctly scaled or handle it in analysis
    
    # Sidebar für Benutzereingaben
    with st.sidebar:
        st.header("🎛️ Einstellungen")
        
        # Zeitrahmenauswahl
        st.subheader("Zeitrahmen")
        # Time range selection is already handled above, just show the current selection
        st.info(f"Ausgewählter Zeitraum: {analysis_period}")
        
        # Benutzerdefinierter Zeitrahmen
        if analysis_period == "Benutzerdefiniert":
            st.info(f"Zeitraum: {start_date} bis {end_date}")
        
        # Auto-Refresh Option
        st.subheader("🔄 Auto-Refresh")
        auto_refresh_enabled = st.checkbox("Daten alle 60 Sekunden automatisch aktualisieren", value=True)
        
        # Aktueller Tarif
        st.subheader("Aktueller Tarif")
        current_tariff = st.number_input(
            "Aktueller Strompreis (€/kWh)",
            min_value=0.10,
            max_value=1.00,
            value=float(CONFIG['current_tariff']),
            step=0.01,
            format="%.2f"
        )
        
        # Provider-Auswahl (entfernt - wir konzentrieren uns auf EPEX Spot)
        # selected_providers = st.multiselect(
        #     "Ausgewählte Provider",
        #     list(TARIFF_PROVIDERS.keys()),
        #     default=list(TARIFF_PROVIDERS.keys())
        # )
        selected_providers = ["EPEX Spot"]  # Nur EPEX Spot verwenden
        
        # Datenquellenstatus
        st.subheader("🔌 Datenquellen")
        if CONFIG["data_sources"]["influxdb"]["enabled"]:
            st.success("✅ InfluxDB verbunden")
            
            # Status messages moved from main content
            if consumption_data is not None and not consumption_data.empty:
                st.success("✅ Verbrauchsdaten erfolgreich geladen")
            else:
                st.warning("⚠️ Keine Verbrauchsdaten verfügbar")
            
            if tariff_data is not None and not tariff_data.empty:
                st.success(f"✅ EPEX Spot Daten geladen: {len(tariff_data)} Datensätze")
            else:
                st.warning("⚠️ Keine EPEX Spot Daten verfügbar")
        else:
            st.warning("⚠️ InfluxDB nicht konfiguriert")
    
    # Hauptinhalt
    st.header("📊 Verbrauchsanalyse")
    
    # Use grid power data for analysis (this is what matters for provider switching)
    consumption_data = grid_power_data if grid_power_data is not None else house_power_data
    
    # Add energy flow analysis section
    st.header("🔄 Energiefluss-Analyse")
    
    # Show data availability status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if house_power_data is not None and not house_power_data.empty:
            st.success("✅ Hausverbrauch")
        else:
            st.warning("⚠️ Hausverbrauch")
    
    with col2:
        if solar_generated_data is not None and not solar_generated_data.empty:
            st.success("✅ Solarerzeugung")
        else:
            st.warning("⚠️ Solarerzeugung")
    
    with col3:
        if battery_power_data is not None and not battery_power_data.empty:
            st.success("✅ Batterie")
        else:
            st.warning("⚠️ Batterie")
    
    with col4:
        if grid_power_data is not None and not grid_power_data.empty:
            st.success("✅ Netzbezug")
        else:
            st.warning("⚠️ Netzbezug")
    
    # Show energy flow visualization if we have data
    if (house_power_data is not None and not house_power_data.empty and
        grid_power_data is not None and not grid_power_data.empty):
        
        st.subheader("📊 Energiefluss-Vergleich")
        
        # Create a simple comparison of house power vs grid power
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Hausverbrauch (aktuell)", f"{house_power_data['value'].iloc[-1]:.0f} W")
            st.metric("Netzbezug (aktuell)", f"{grid_power_data['value'].iloc[-1]:.0f} W")
        
        with col2:
            house_avg = house_power_data['value'].mean()
            grid_avg = grid_power_data['value'].mean()
            st.metric("Hausverbrauch (⌀)", f"{house_avg:.0f} W")
            st.metric("Netzbezug (⌀)", f"{grid_avg:.0f} W")
        
        # Calculate self-consumption ratio
        if solar_generated_data is not None and not solar_generated_data.empty:
            solar_avg = solar_generated_data['value'].mean()
            if solar_avg > 0:
                self_consumption_ratio = max(0, (house_avg - grid_avg) / solar_avg)
                st.metric("Eigenverbrauch", f"{self_consumption_ratio:.1%}")
    
    if consumption_data is not None and not consumption_data.empty:
        if tariff_data is not None and not tariff_data.empty:
                
                # Echtzeit-Analyse
                realtime_result = analyze_realtime(consumption_data, tariff_data, CONFIG['current_tariff'])
                
                if realtime_result:
                    st.header("🔥 Echtzeit-Analyse - Letzte Stunde")
                    
                    # Aktuelle Werte
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Aktueller Verbrauch", f"{realtime_result['current_consumption']:.0f} W")
                    
                    with col2:
                        st.metric("Aktueller Tarif", f"{realtime_result['current_tariff']:.3f} €/kWh")
                    
                    with col3:
                        st.metric("EPEX Spot", f"{realtime_result['current_epex']:.3f} €/kWh")
                    
                    with col4:
                        st.metric("Empfehlung", realtime_result['recommendation'])
                    
                    # Letzte Viertelstunde - Verbrauch
                    st.subheader("⏱️ Letzte Viertelstunde - Verbrauchsstatistik")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("⌀ Verbrauch", f"{realtime_result['avg_consumption_last_quarter']:.0f} W")
                    
                    with col2:
                        st.metric("Max Verbrauch", f"{realtime_result['max_consumption_last_quarter']:.0f} W")
                    
                    with col3:
                        st.metric("Min Verbrauch", f"{realtime_result['min_consumption_last_quarter']:.0f} W")
                    
                    with col4:
                        st.metric("Gesamt", f"{realtime_result['total_consumption_last_quarter_kwh']:.3f} kWh")
                    
                    # Letzte Viertelstunde - EPEX Entwicklung
                    st.subheader("💰 Letzte Viertelstunde - EPEX Preisentwicklung")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("⌀ EPEX", f"{realtime_result['avg_epex_last_quarter']:.3f} €/kWh")
                    
                    with col2:
                        st.metric("Max EPEX", f"{realtime_result['max_epex_last_quarter']:.3f} €/kWh")
                    
                    with col3:
                        st.metric("Min EPEX", f"{realtime_result['min_epex_last_quarter']:.3f} €/kWh")
                    
                    # Letzte Viertelstunde Kostenvergleich
                    st.subheader("💵 Letzte Viertelstunde - Kostenvergleich")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Aktuelle Kosten", f"{realtime_result['current_cost_last_quarter']:.2f} €")
                    
                    with col2:
                        st.metric("EPEX Kosten", f"{realtime_result['epex_cost_last_quarter']:.2f} €")
                    
                    with col3:
                        if realtime_result['savings_last_quarter'] > 0:
                            st.metric("Einsparung", f"{realtime_result['savings_last_quarter']:.2f} €", delta=f"{realtime_result['savings_percent_last_quarter']:.1f}%")
                        else:
                            st.metric("Mehrkosten", f"{abs(realtime_result['savings_last_quarter']):.2f} €", delta=f"{-realtime_result['savings_percent_last_quarter']:.1f}%")
                    
                    st.markdown("---")
                    
                    # Letzte Stunde - Verbrauch
                    st.subheader("📊 Letzte Stunde - Verbrauchsstatistik")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("⌀ Verbrauch", f"{realtime_result['avg_consumption_last_hour']:.0f} W")
                    
                    with col2:
                        st.metric("Max Verbrauch", f"{realtime_result['max_consumption_last_hour']:.0f} W")
                    
                    with col3:
                        st.metric("Min Verbrauch", f"{realtime_result['min_consumption_last_hour']:.0f} W")
                    
                    with col4:
                        st.metric("Gesamt", f"{realtime_result['total_consumption_last_hour_kwh']:.3f} kWh")
                    
                    # Letzte Stunde - EPEX Entwicklung
                    st.subheader("💰 Letzte Stunde - EPEX Preisentwicklung")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("⌀ EPEX", f"{realtime_result['avg_epex_last_hour']:.3f} €/kWh")
                    
                    with col2:
                        st.metric("Max EPEX", f"{realtime_result['max_epex_last_hour']:.3f} €/kWh")
                    
                    with col3:
                        st.metric("Min EPEX", f"{realtime_result['min_epex_last_hour']:.3f} €/kWh")
                    
                    # Kostenvergleich
                    st.subheader("💵 Kostenvergleich")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Aktuelle Kosten", f"{realtime_result['current_cost']:.2f} €/h")
                    
                    with col2:
                        st.metric("EPEX Kosten", f"{realtime_result['epex_cost']:.2f} €/h")
                    
                    with col3:
                        if realtime_result['savings'] > 0:
                            st.metric("Einsparung", f"{realtime_result['savings']:.2f} €/h", delta=f"{realtime_result['savings_percent']:.1f}%")
                        else:
                            st.metric("Mehrkosten", f"{abs(realtime_result['savings']):.2f} €/h", delta=f"{-realtime_result['savings_percent']:.1f}%")
                    
                    # Letzte Stunde Kostenvergleich
                    st.subheader("📈 Letzte Stunde - Kostenvergleich")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Aktuelle Kosten", f"{realtime_result['current_cost_last_hour']:.2f} €")
                    
                    with col2:
                        st.metric("EPEX Kosten", f"{realtime_result['epex_cost_last_hour']:.2f} €")
                    
                    with col3:
                        if realtime_result['savings_last_hour'] > 0:
                            st.metric("Einsparung", f"{realtime_result['savings_last_hour']:.2f} €", delta=f"{realtime_result['savings_percent_last_hour']:.1f}%")
                        else:
                            st.metric("Mehrkosten", f"{abs(realtime_result['savings_last_hour']):.2f} €", delta=f"{-realtime_result['savings_percent_last_hour']:.1f}%")
                    
                    # Visualisierung der letzten Stunde
                    st.subheader("📊 Verbrauchsverlauf - Letzte Stunde")
                    
                    # Daten für die Visualisierung vorbereiten - zeitbasiert wie in den Berechnungen
                    last_hour_data = consumption_data[consumption_data.index > (consumption_data.index[-1] - timedelta(hours=1))]
                    
                    # If no data in the last hour, use the last available data point
                    if last_hour_data.empty:
                        st.warning("⚠️ Keine Verbrauchsdaten in der letzten Stunde verfügbar. Zeige letzte verfügbare Daten.")
                        # Use the last available data point and create a small time range around it
                        last_available_time = consumption_data.index[-1]
                        # Create a small time window around the last available data point
                        time_window = timedelta(minutes=30)
                        last_hour_data = consumption_data[
                            (consumption_data.index >= (last_available_time - time_window)) &
                            (consumption_data.index <= last_available_time)
                        ]
                    
                    # If still no data, use just the last data point
                    if last_hour_data.empty:
                        last_hour_data = consumption_data.tail(1)
                    
                    fig_consumption = go.Figure()
                    
                    fig_consumption.add_trace(go.Scatter(
                        x=last_hour_data.index,
                        y=last_hour_data['value'],
                        mode='lines',
                        name='Verbrauch',
                        line=dict(color='#1f77b4', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(31, 119, 180, 0.2)'
                    ))
                    
                    # Aktuellen Verbrauch als Marker hinzufügen
                    # Use the last available data point for the current marker
                    last_data_point_time = last_hour_data.index[-1]
                    last_data_point_value = last_hour_data['value'].iloc[-1]
                    
                    fig_consumption.add_trace(go.Scatter(
                        x=[last_data_point_time],
                        y=[last_data_point_value],
                        mode='markers',
                        name='Aktuell',
                        marker=dict(color='red', size=12, symbol='star')
                    ))
                    
                    fig_consumption.update_layout(
                        title='Stromverbrauch - Letzte Stunde',
                        xaxis_title='Zeit',
                        yaxis_title='Leistung (W)',
                        height=300,
                        hovermode='x unified',
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_consumption, width="stretch")
                    
                    # EPEX Preisverlauf
                    st.subheader("💰 EPEX Preisverlauf - Letzte Stunde")
                    
                    # Get last hour of data, or fallback to last available data if no recent data exists
                    last_hour_tariff = tariff_data[tariff_data.index > (tariff_data.index[-1] - timedelta(hours=1))]
                    
                    # If no data in the last hour, use the last available data point
                    if last_hour_tariff.empty:
                        st.warning("⚠️ Keine EPEX-Daten in der letzten Stunde verfügbar. Zeige letzte verfügbare Daten.")
                        # Use the last available data point and create a small time range around it
                        last_available_time = tariff_data.index[-1]
                        # Create a small time window around the last available data point
                        time_window = timedelta(minutes=30)
                        last_hour_tariff = tariff_data[
                            (tariff_data.index >= (last_available_time - time_window)) &
                            (tariff_data.index <= last_available_time)
                        ]
                    
                    # If still no data, use just the last data point
                    if last_hour_tariff.empty:
                        last_hour_tariff = tariff_data.tail(1)
                    
                    fig_epex = go.Figure()
                    
                    fig_epex.add_trace(go.Scatter(
                        x=last_hour_tariff.index,
                        y=last_hour_tariff['value'],
                        mode='lines',
                        name='EPEX Spot',
                        line=dict(color='#ff7f0e', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(255, 127, 14, 0.2)'
                    ))
                    
                    # Aktuellen EPEX Preis als Marker hinzufügen
                    # Use the last available data point for the current marker
                    last_data_point_time = last_hour_tariff.index[-1]
                    last_data_point_value = last_hour_tariff['value'].iloc[-1]
                    
                    fig_epex.add_trace(go.Scatter(
                        x=[last_data_point_time],
                        y=[last_data_point_value],
                        mode='markers',
                        name='Aktuell',
                        marker=dict(color='red', size=12, symbol='star')
                    ))
                    
                    # Aktuellen Tarif als Referenzlinie hinzufügen
                    fig_epex.add_hline(
                        y=current_tariff,
                        line_dash="dash",
                        line_color="gray",
                        annotation_text="Aktueller Tarif",
                        annotation_position="right"
                    )
                    
                    fig_epex.update_layout(
                        title='EPEX Spot Preis - Letzte Stunde',
                        xaxis_title='Zeit',
                        yaxis_title='Preis (€/kWh)',
                        height=300,
                        hovermode='x unified',
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_epex, width="stretch")
                    
                    # Kostenvergleich Visualisierung
                    st.subheader("💵 Kostenvergleich - Letzte Stunde")
                    
                    cost_data = pd.DataFrame({
                        'Zeitperiode': ['Aktuell', 'Letzte 15 Min', 'Letzte Stunde'],
                        'Aktuelle Kosten': [
                            realtime_result['current_cost'],
                            realtime_result['current_cost_last_quarter'],
                            realtime_result['current_cost_last_hour']
                        ],
                        'EPEX Kosten': [
                            realtime_result['epex_cost'],
                            realtime_result['epex_cost_last_quarter'],
                            realtime_result['epex_cost_last_hour']
                        ]
                    })
                    
                    fig_costs = go.Figure()
                    
                    fig_costs.add_trace(go.Bar(
                        x=cost_data['Zeitperiode'],
                        y=cost_data['Aktuelle Kosten'],
                        name='Aktuelle Kosten',
                        marker_color='lightcoral'
                    ))
                    
                    fig_costs.add_trace(go.Bar(
                        x=cost_data['Zeitperiode'],
                        y=cost_data['EPEX Kosten'],
                        name='EPEX Kosten',
                        marker_color='lightgreen'
                    ))
                    
                    fig_costs.update_layout(
                        title='Kostenvergleich: Aktuell vs EPEX Spot',
                        xaxis_title='Zeitperiode',
                        yaxis_title='Kosten (€)',
                        barmode='group',
                        height=300
                    )
                    
                    st.plotly_chart(fig_costs, width="stretch")
                    
                    # Empfehlung
                    if realtime_result['savings'] > 0:
                        st.success(f"🟢 {realtime_result['recommendation']} - Sie könnten {realtime_result['savings']:.2f} €/h sparen!")
                    else:
                        st.info(f"🔴 {realtime_result['recommendation']} - Ihr aktueller Tarif ist besser.")
                
                # Für den Vergleich: Alle Provider mit demselben EPEX-Preis (entfernt - wir nutzen nur EPEX)
                # for provider in ["Tiwatt", "AWATTAR", "Tibber", "Rabot Energy", "Tado"]:
                #     tariff_data[provider] = tariff_data['value']  # Alle haben denselben Spot-Preis
                
                # Tab-Navigation für verschiedene Analysen
                st.markdown("---")
                analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs(["📊 Historische Analyse", "📅 Monatliche Analyse", "📈 Zeitperioden-Vergleich"])
                
                with analysis_tab1:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    analysis_result = analyze_historical_consumption(consumption_data)
                    
                    if analysis_result:
                        with col1:
                            st.metric("Gesamtverbrauch", f"{analysis_result['total_consumption_kwh']:.2f} kWh")
                        with col2:
                            st.metric("Durchschnitt", f"{analysis_result['average_power_w'] / 1000:.2f} kW")
                        with col3:
                            st.metric("Maximum", f"{analysis_result['max_power_w'] / 1000:.2f} kW")
                        with col4:
                            st.metric("Minimum", f"{analysis_result['min_power_w'] / 1000:.2f} kW")
                        
                        # Verbrauchskurve
                        st.subheader("Stromverbrauch über Zeit")
                        fig_consumption = px.line(
                            consumption_data.reset_index(),
                            x='time',
                            y='value',
                            title='Stromverbrauch (Watt) über Zeit',
                            labels={'value': 'Leistung (W)', 'time': 'Zeit'}
                        )
                        fig_consumption.update_layout(
                            hovermode='x unified',
                            height=400
                        )
                        st.plotly_chart(fig_consumption, width="stretch")
                        
                        # Einfacher EPEX Vergleich (statt komplexer Provider-Vergleich)
                        st.header("💰 EPEX Spot Analyse")
                        
                        # EPEX Daten verwenden (bereits geladen)
                        if tariff_data is not None and not tariff_data.empty:
                            # Einfache Statistiken für EPEX
                            st.subheader("EPEX Spot Statistiken")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("⌀ EPEX Preis", f"{tariff_data['value'].mean():.3f} €/kWh")
                            
                            with col2:
                                st.metric("Max EPEX", f"{tariff_data['value'].max():.3f} €/kWh")
                            
                            with col3:
                                st.metric("Min EPEX", f"{tariff_data['value'].min():.3f} €/kWh")
                            
                            with col4:
                                st.metric("Spanne", f"{tariff_data['value'].max() - tariff_data['value'].min():.3f} €/kWh")
                            
                            # Einfache Kostenberechnung mit EPEX
                            total_consumption_kwh = analysis_result['total_consumption_kwh']
                            current_cost = total_consumption_kwh * current_tariff
                            epex_cost = total_consumption_kwh * tariff_data['value'].mean()
                            savings = current_cost - epex_cost
                            savings_percent = (savings / current_cost * 100) if current_cost > 0 else 0
                            
                            st.subheader("Kostenvergleich")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Aktuelle Kosten", f"{current_cost:.2f} €")
                            
                            with col2:
                                st.metric("EPEX Kosten", f"{epex_cost:.2f} €")
                            
                            with col3:
                                if savings > 0:
                                    st.metric("Einsparung", f"{savings:.2f} €", delta=f"{savings_percent:.1f}%")
                                else:
                                    st.metric("Mehrkosten", f"{abs(savings):.2f} €", delta=f"{-savings_percent:.1f}%")
                            
                            # EPEX Preisentwicklung
                            st.subheader("EPEX Preisentwicklung")
                            
                            fig_epex = px.line(
                                tariff_data.reset_index(),
                                x='time',
                                y='value',
                                title='EPEX Spot Preis über Zeit',
                                labels={'value': 'Preis (€/kWh)', 'time': 'Zeit'}
                            )
                            
                            # Aktuellen Tarif als Referenzlinie hinzufügen
                            fig_epex.add_hline(
                                y=current_tariff,
                                line_dash="dash",
                                line_color="red",
                                annotation_text="Aktueller Tarif",
                                annotation_position="right"
                            )
                            
                            fig_epex.update_layout(
                                hovermode='x unified',
                                height=400
                            )
                            
                            st.plotly_chart(fig_epex, width="stretch")
                            
                            # Kostenverteilung nach Tageszeit
                            st.subheader("🕒 Verbrauch nach Tageszeit")
                            
                            hourly_consumption = get_consumption_by_hour(consumption_data)
                            
                            if hourly_consumption is not None:
                                fig_hourly_costs = go.Figure()
                                
                                fig_hourly_costs.add_trace(go.Bar(
                                    x=hourly_consumption.index,
                                    y=hourly_consumption.values,
                                    name='Verbrauch',
                                    marker_color='lightblue'
                                ))
                                
                                fig_hourly_costs.update_layout(
                                    title='Stromverbrauch nach Stunde des Tages',
                                    xaxis_title='Stunde des Tages',
                                    yaxis_title='Verbrauch (kWh)',
                                    height=300,
                                    xaxis=dict(tickmode='linear', tick0=0, dtick=1)
                                )
                                
                                st.plotly_chart(fig_hourly_costs, width="stretch")
                        else:
                            st.warning("⚠️ Keine EPEX Daten verfügbar für historischen Vergleich")
                    else:
                        st.error("Fehler bei der Verbrauchsanalyse")
                        st.warning("Keine Verbrauchsdaten verfügbar. Bitte überprüfen Sie die InfluxDB-Verbindung und den Zeitrahmen.")
                
                with analysis_tab2:
                    # Monatliche Analyse
                    st.header("📅 Monatliche Verbrauchsanalyse")
                    
                    monthly_result = analyze_monthly_consumption(consumption_data)
                    
                    if monthly_result and len(monthly_result) > 0:
                        # Monatliche Statistiken anzeigen
                        st.subheader("Monatliche Übersicht")
                        
                        # Daten für die Tabelle vorbereiten
                        monthly_data = []
                        for month, data in monthly_result.items():
                            monthly_data.append({
                                'Monat': month,
                                'Verbrauch (kWh)': f"{data['total_consumption_kwh']:.2f}",
                                'Durchschnitt (kW)': f"{data['average_power_w'] / 1000:.2f}",
                                'Maximum (kW)': f"{data['max_power_w'] / 1000:.2f}",
                                'Kosten (€)': f"{data['cost_with_current_tariff']:.2f}"
                            })
                        
                        # Tabelle anzeigen
                        monthly_df = pd.DataFrame(monthly_data)
                        st.dataframe(monthly_df, width="stretch")
                        
                        # Monatlicher Verbrauchstrend
                        st.subheader("Monatlicher Verbrauchstrend")
                        
                        # Daten für das Diagramm vorbereiten
                        months = list(monthly_result.keys())
                        consumption_values = [data['total_consumption_kwh'] for data in monthly_result.values()]
                        cost_values = [data['cost_with_current_tariff'] for data in monthly_result.values()]
                        
                        fig_monthly = go.Figure()
                        
                        # Verbrauchskurve
                        fig_monthly.add_trace(go.Bar(
                            x=months,
                            y=consumption_values,
                            name='Verbrauch (kWh)',
                            marker_color='lightblue',
                            yaxis='y'
                        ))
                        
                        # Kostenkurve
                        fig_monthly.add_trace(go.Scatter(
                            x=months,
                            y=cost_values,
                            name='Kosten (€)',
                            line=dict(color='red', width=3),
                            yaxis='y2'
                        ))
                        
                        fig_monthly.update_layout(
                            title='Monatlicher Verbrauch und Kosten',
                            xaxis_title='Monat',
                            yaxis=dict(title='Verbrauch (kWh)', side='left'),
                            yaxis2=dict(title='Kosten (€)', overlaying='y', side='right'),
                            height=400,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_monthly, width="stretch")
                        
                        # Monatliche Statistiken
                        st.subheader("Monatliche Statistiken")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            total_consumption = sum(data['total_consumption_kwh'] for data in monthly_result.values())
                            st.metric("Gesamtverbrauch", f"{total_consumption:.2f} kWh")
                        
                        with col2:
                            total_cost = sum(data['cost_with_current_tariff'] for data in monthly_result.values())
                            st.metric("Gesamtkosten", f"{total_cost:.2f} €")
                        
                        with col3:
                            avg_monthly = total_consumption / len(monthly_result)
                            st.metric("Durchschnitt/Monat", f"{avg_monthly:.2f} kWh")
                        
                        st.success("📊 Monatliche Analyse erfolgreich! Diese Daten helfen Ihnen, langfristige Verbrauchsmuster zu erkennen.")
                    else:
                        st.warning("⚠️ Nicht genug Daten für monatliche Analyse verfügbar. Bitte wählen Sie einen längeren Zeitrahmen.")
        
                with analysis_tab3:
                    # Zeitperioden-Vergleich
                    st.header("📈 Zeitperioden-Vergleich")
                    
                    # Helper function to analyze a specific time period
                    def analyze_time_period(data, start_time, end_time, period_name):
                        """Analyze consumption data for a specific time period"""
                        # Make timezone-aware if data has timezone
                        if hasattr(data.index, 'tz') and data.index.tz is not None:
                            # Convert datetime objects to timezone-aware using pandas
                            if not isinstance(start_time, pd.Timestamp):
                                start_time = pd.Timestamp(start_time).tz_localize(data.index.tz)
                            if not isinstance(end_time, pd.Timestamp):
                                end_time = pd.Timestamp(end_time).tz_localize(data.index.tz)
                        
                        period_data = data[(data.index >= start_time) & (data.index <= end_time)]
                        
                        if period_data.empty:
                            return None
                            
                        # Calculate duration in hours
                        duration_hours = (period_data.index.max() - period_data.index.min()).total_seconds() / 3600
                        if duration_hours == 0:  # Handle case where all data points are at same timestamp
                            duration_hours = len(period_data) / 3600  # Assume 1 second intervals
                        
                        # Correct kWh calculation: average power (kW) * duration (hours)
                        average_power_w = period_data['value'].mean()
                        total_consumption_kwh = (average_power_w / 1000) * duration_hours  # (W → kW) * hours = kWh
                        
                        # Power metrics in kW
                        average_power_kw = average_power_w / 1000  # W to kW
                        max_power_kw = period_data['value'].max() / 1000  # W to kW
                        min_power_kw = period_data['value'].min() / 1000  # W to kW
                        cost = total_consumption_kwh * current_tariff
                        
                        return {
                            'period_name': period_name,
                            'total_consumption_kwh': total_consumption_kwh,
                            'average_power_kw': average_power_kw,
                            'max_power_kw': max_power_kw,
                            'min_power_kw': min_power_kw,
                            'cost': cost,
                            'data_points': len(period_data)
                        }
                    
                    # Define time periods
                    now = datetime.now()
                    
                    # Today
                    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    # Yesterday
                    yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    yesterday_end = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    # Current Week (Monday to today)
                    current_week_start = now - timedelta(days=now.weekday())
                    current_week_start = current_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                    current_week_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    # Last Week (Monday to Sunday)
                    last_week_end = current_week_start - timedelta(days=1)
                    last_week_start = last_week_end - timedelta(days=6)
                    last_week_start = last_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                    last_week_end = last_week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    # This Month
                    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    this_month_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    # Last Month
                    last_month_end = this_month_start - timedelta(days=1)
                    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    last_month_end = last_month_end.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    # Current Year
                    this_year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                    this_year_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    # Analyze all periods
                    periods = [
                        (today_start, today_end, "Heute"),
                        (yesterday_start, yesterday_end, "Gestern"),
                        (current_week_start, current_week_end, "Aktuelle Woche"),
                        (last_week_start, last_week_end, "Letzte Woche"),
                        (this_month_start, this_month_end, "Dieser Monat"),
                        (last_month_start, last_month_end, "Letzter Monat"),
                        (this_year_start, this_year_end, "Aktuelles Jahr")
                    ]
                    
                    period_results = []
                    for start, end, name in periods:
                        result = analyze_time_period(consumption_data, start, end, name)
                        if result:
                            period_results.append(result)
                    
                    if period_results:
                        # Create comparison table
                        st.subheader("📊 Zeitperioden im Vergleich")
                        
                        comparison_data = []
                        for result in period_results:
                            comparison_data.append({
                                'Zeitraum': result['period_name'],
                                'Verbrauch (kWh)': f"{result['total_consumption_kwh']:.2f}",
                                'Durchschnitt (kW)': f"{result['average_power_kw']:.2f}",
                                'Maximum (kW)': f"{result['max_power_kw']:.2f}",
                                'Minimum (kW)': f"{result['min_power_kw']:.2f}",
                                'Kosten (€)': f"{result['cost']:.2f}",
                                'Datenpunkte': result['data_points']
                            })
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(comparison_df, width="stretch")
                        
                        # Create comparison charts
                        st.subheader("📈 Visualisierung")
                        
                        # Bar chart for consumption comparison
                        fig_comparison = go.Figure()
                        
                        fig_comparison.add_trace(go.Bar(
                            x=[r['period_name'] for r in period_results],
                            y=[r['total_consumption_kwh'] for r in period_results],
                            name='Verbrauch (kWh)',
                            marker_color='lightblue'
                        ))
                        
                        fig_comparison.update_layout(
                            title='Verbrauch nach Zeitperiode',
                            xaxis_title='Zeitperiode',
                            yaxis_title='Verbrauch (kWh)',
                            height=400,
                            xaxis=dict(tickangle=-45)
                        )
                        
                        st.plotly_chart(fig_comparison, width="stretch")
                        
                        # Line chart for average power comparison
                        fig_avg_comparison = go.Figure()
                        
                        fig_avg_comparison.add_trace(go.Scatter(
                            x=[r['period_name'] for r in period_results],
                            y=[r['average_power_kw'] for r in period_results],
                            mode='lines+markers',
                            name='Durchschnittsleistung (kW)',
                            line=dict(color='green', width=3),
                            marker=dict(size=10)
                        ))
                        
                        fig_avg_comparison.update_layout(
                            title='Durchschnittsleistung nach Zeitperiode',
                            xaxis_title='Zeitperiode',
                            yaxis_title='Durchschnittsleistung (kW)',
                            height=400,
                            xaxis=dict(tickangle=-45)
                        )
                        
                        st.plotly_chart(fig_avg_comparison, width="stretch")
                        
                        # Cost comparison
                        fig_cost_comparison = go.Figure()
                        
                        fig_cost_comparison.add_trace(go.Bar(
                            x=[r['period_name'] for r in period_results],
                            y=[r['cost'] for r in period_results],
                            name='Kosten (€)',
                            marker_color='lightcoral'
                        ))
                        
                        fig_cost_comparison.update_layout(
                            title='Kosten nach Zeitperiode',
                            xaxis_title='Zeitperiode',
                            yaxis_title='Kosten (€)',
                            height=400,
                            xaxis=dict(tickangle=-45)
                        )
                        
                        st.plotly_chart(fig_cost_comparison, width="stretch")
                        
                        # Summary statistics
                        st.subheader("📊 Zusammenfassung")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            total_all_periods = sum(r['total_consumption_kwh'] for r in period_results)
                            st.metric("Gesamtverbrauch alle Perioden", f"{total_all_periods:.2f} kWh")
                        
                        with col2:
                            avg_consumption = total_all_periods / len(period_results)
                            st.metric("Durchschnitt pro Periode", f"{avg_consumption:.2f} kWh")
                        
                        with col3:
                            total_cost_all = sum(r['cost'] for r in period_results)
                            st.metric("Gesamtkosten alle Perioden", f"{total_cost_all:.2f} €")
                        
                        st.success("🎯 Zeitperioden-Vergleich erfolgreich! Diese Analyse hilft Ihnen, Verbrauchsmuster über verschiedene Zeiträume zu erkennen.")
                        
                    else:
                        st.warning("⚠️ Nicht genug Daten für Zeitperioden-Vergleich verfügbar. Bitte wählen Sie einen längeren Zeitrahmen oder überprüfen Sie Ihre Datenverfügbarkeit.")
        else:
            # No tariff data, but we have consumption data - use mock data
            st.warning("⚠️  Keine EPEX Spot Daten gefunden - Verwende MOCK-Daten")
            mock_provider = MockTariffProvider()
            tariff_data = mock_provider.generate(start_time, end_time)
    else:
        # No consumption data available
        st.error("❌ Keine Verbrauchsdaten verfügbar!")
        st.error("💡 Bitte überprüfen Sie:")
        st.error("   1. InfluxDB läuft und erreichbar ist")
        st.error("   2. Die Konfiguration in .env korrekt ist")
        st.error("   3. Die Datenbank 'homeassistant' existiert")
        st.error("   4. Die Messung 'W' mit entity_id='senec_house_power' vorhanden ist")
        st.stop()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Hinweis:** Die Tarifdaten sind derzeit Beispieldaten. Für eine genaue Analyse müssen die echten 
    API-Daten der Provider integriert werden.
    
    **Nächste Schritte:**
    - ✅ InfluxDB-Integration für Verbrauchsdaten
    - 🔄 Echte Tarif-APIs integrieren (Tiwatt, AWATTAR, etc.)
    - 📊 Historische Datenanalyse erweitern
    - 🏠 Home Assistant-Integration für Echtzeitdaten
    """)

if __name__ == "__main__":
    main()