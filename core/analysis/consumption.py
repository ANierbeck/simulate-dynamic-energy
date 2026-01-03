"""
Verbrauchsanalysemodul
"""

import pandas as pd
import logging
from core.config import CONFIG
from datetime import datetime

# Logging konfigurieren
logger = logging.getLogger(__name__)

def analyze_historical_consumption(consumption_data):
    """
    Analysiert den historischen Verbrauch und berechnet Statistiken
    
    Args:
        consumption_data (DataFrame): Verbrauchsdaten mit Zeitindex und 'value' Spalte
        
    Returns:
        dict: Analyseergebnisse mit Statistiken
    """
    try:
        if consumption_data is None or consumption_data.empty:
            logger.warning("Keine Verbrauchsdaten für Analyse verfügbar")
            return None
        
        # Grundlegende Statistiken berechnen
        average_power_w = consumption_data['value'].mean()
        max_power_w = consumption_data['value'].max()
        min_power_w = consumption_data['value'].min()
        
        # Berechne die Dauer des Zeitraums in Stunden
        duration_hours = (consumption_data.index.max() - consumption_data.index.min()).total_seconds() / 3600
        
        # Korrekte kWh Berechnung: Durchschnittsleistung in kW * Dauer in Stunden
        total_consumption_kwh = (average_power_w / 1000) * duration_hours  # (W → kW) * Stunden = kWh
        
        # Zeitbasierte Statistiken
        start_time = consumption_data.index.min()
        end_time = consumption_data.index.max()
        duration_hours = len(consumption_data)
        
        # Kosten mit aktuellem Tarif berechnen
        current_cost = total_consumption_kwh * CONFIG['current_tariff']
        
        # Ergebnisse zurückgeben
        result = {
            'start_time': start_time,
            'end_time': end_time,
            'duration_hours': duration_hours,
            'total_consumption_kwh': total_consumption_kwh,
            'average_power_w': average_power_w,
            'max_power_w': max_power_w,
            'min_power_w': min_power_w,
            'current_cost': current_cost,
            'data_points': len(consumption_data),
            'raw_data': consumption_data
        }
        
        logger.info(f"Verbrauchsanalyse abgeschlossen: {total_consumption_kwh:.2f} kWh, {current_cost:.2f} €")
        return result
        
    except Exception as e:
        logger.error(f"Fehler bei der Verbrauchsanalyse: {e}")
        return None

def get_consumption_by_hour(consumption_data):
    """
    Berechnet den Verbrauch nach Tageszeit
    
    Args:
        consumption_data (DataFrame): Verbrauchsdaten
        
    Returns:
        DataFrame: Verbrauch nach Stunde des Tages
    """
    try:
        consumption_data['hour'] = consumption_data.index.hour
        hourly_consumption = consumption_data.groupby('hour')['value'].sum() / 1000  # kWh
        return hourly_consumption
    except Exception as e:
        logger.error(f"Fehler bei Stundenanalyse: {e}")
        return None


def analyze_monthly_consumption(consumption_data):
    """
    Analysiert den monatlichen Verbrauch und aggregiert Daten
    
    Args:
        consumption_data (DataFrame): Verbrauchsdaten mit Zeitindex und 'value' Spalte
        
    Returns:
        dict: Monatliche Analyseergebnisse
    """
    try:
        if consumption_data is None or consumption_data.empty:
            logger.warning("Keine Verbrauchsdaten für monatliche Analyse verfügbar")
            return None
            
        # Monatliche Aggregation - korrekte kWh Berechnung
        consumption_data['month'] = consumption_data.index.to_period('M')
        
        # Ergebnisse formatieren
        monthly_results = {}
        for month_period, month_data in consumption_data.groupby('month'):
            month_key = month_period.strftime('%Y-%m')
            
            # Korrekte kWh Berechnung: Durchschnittsleistung * Dauer
            # Berechne die tatsächliche Dauer basierend auf den Datenpunkten
            if len(month_data) > 1:
                # Wenn wir mehrere Datenpunkte haben, berechne die tatsächliche Dauer
                time_deltas = month_data.index.to_series().diff().dropna()
                total_seconds = time_deltas.sum().total_seconds()
                duration_hours = total_seconds / 3600
            else:
                # Wenn nur ein Datenpunkt, gehe von 1 Stunde aus
                duration_hours = 1.0
                
            # Mindestens 1 Stunde annehmen, um Division durch 0 zu vermeiden
            duration_hours = max(duration_hours, 1.0)
            
            average_power_w = month_data['value'].mean()
            total_consumption_kwh = (average_power_w / 1000) * duration_hours  # (W → kW) * Stunden = kWh
            
            monthly_results[month_key] = {
                'total_consumption_kwh': total_consumption_kwh,
                'average_power_w': month_data['value'].mean(),
                'max_power_w': month_data['value'].max(),
                'min_power_w': month_data['value'].min(),
                'cost_with_current_tariff': total_consumption_kwh * CONFIG['current_tariff']
            }
        
        logger.info(f"Monatliche Analyse abgeschlossen für {len(monthly_results)} Monate")
        return monthly_results
        
    except Exception as e:
        logger.error(f"Fehler bei der monatlichen Analyse: {e}")
        return None