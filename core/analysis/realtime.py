"""
Echtzeit-Analyse für Tarifvergleich
Vergleicht aktuellen Tarif mit EPEX Spot in Echtzeit
"""

import pandas as pd
import logging
from core.config import CONFIG

logger = logging.getLogger(__name__)

def analyze_realtime(consumption_data, tariff_data, current_tariff):
    """
    Analysiert in Echtzeit, ob Tarifwechsel sinnvoll ist
    
    Args:
        consumption_data: Aktuelle Verbrauchsdaten
        tariff_data: Aktuelle EPEX Spot Preise
        current_tariff: Aktueller Tarifpreis
        
    Returns:
        dict: Analyseergebnisse
    """
    try:
        if consumption_data is None or tariff_data is None:
            return None
        
        # Aktuellen Verbrauch berechnen (letzte Stunde)
        current_consumption = consumption_data.iloc[-1]['value']  # Aktueller Wert
        
        # Daten der letzten Viertelstunde extrahieren (15 Minuten) - zeitbasiert
        from datetime import timedelta
        last_quarter_hour_data = consumption_data[consumption_data.index > (consumption_data.index[-1] - timedelta(minutes=15))]
        
        # Statistiken für die letzte Viertelstunde
        avg_consumption_last_quarter = last_quarter_hour_data['value'].mean()
        max_consumption_last_quarter = last_quarter_hour_data['value'].max()
        min_consumption_last_quarter = last_quarter_hour_data['value'].min()
        # Korrekte kWh Berechnung: Durchschnittsleistung in kW * Zeit in Stunden
        # Für Viertelstunde: durchschnittliche Leistung in kW * 0.25 Stunden
        avg_power_kw_quarter = avg_consumption_last_quarter / 1000  # W zu kW
        total_consumption_last_quarter_kwh = avg_power_kw_quarter * 0.25  # kW * 0.25h = kWh
        
        # Daten der letzten Stunde extrahieren - zeitbasiert
        last_hour_data = consumption_data[consumption_data.index > (consumption_data.index[-1] - timedelta(hours=1))]
        
        # Statistiken für die letzte Stunde
        avg_consumption_last_hour = last_hour_data['value'].mean()
        max_consumption_last_hour = last_hour_data['value'].max()
        min_consumption_last_hour = last_hour_data['value'].min()
        # Korrekte kWh Berechnung: Durchschnittsleistung in kW * Zeit in Stunden
        # Für Stunde: durchschnittliche Leistung in kW * 1 Stunde
        avg_power_kw_hour = avg_consumption_last_hour / 1000  # W zu kW
        total_consumption_last_hour_kwh = avg_power_kw_hour * 1.0  # kW * 1h = kWh
        
        # Aktuellen EPEX Preis
        current_epex = tariff_data.iloc[-1]['value']  # Aktueller Spot-Preis
        
        # EPEX Preisentwicklung der letzten Viertelstunde
        last_quarter_epex = tariff_data.iloc[-15:]['value']
        avg_epex_last_quarter = last_quarter_epex.mean()
        max_epex_last_quarter = last_quarter_epex.max()
        min_epex_last_quarter = last_quarter_epex.min()
        
        # EPEX Preisentwicklung der letzten Stunde
        last_hour_epex = tariff_data.iloc[-60:]['value']
        avg_epex_last_hour = last_hour_epex.mean()
        max_epex_last_hour = last_hour_epex.max()
        min_epex_last_hour = last_hour_epex.min()
        
        # Kostenvergleich für aktuellen Moment
        current_cost = current_consumption / 1000 * current_tariff  # €/h
        epex_cost = current_consumption / 1000 * current_epex  # €/h
        
        # Kostenvergleich für die letzte Viertelstunde
        current_cost_last_quarter = total_consumption_last_quarter_kwh * current_tariff  # €
        epex_cost_last_quarter = total_consumption_last_quarter_kwh * current_epex  # €
        
        # Kostenvergleich für die letzte Stunde
        current_cost_last_hour = total_consumption_last_hour_kwh * current_tariff  # €
        epex_cost_last_hour = total_consumption_last_hour_kwh * current_epex  # €
        
        # Einsparung
        savings = current_cost - epex_cost
        savings_percent = (savings / current_cost * 100) if current_cost > 0 else 0
        
        # Einsparung für die letzte Viertelstunde
        savings_last_quarter = current_cost_last_quarter - epex_cost_last_quarter
        savings_percent_last_quarter = (savings_last_quarter / current_cost_last_quarter * 100) if current_cost_last_quarter > 0 else 0
        
        # Einsparung für die letzte Stunde
        savings_last_hour = current_cost_last_hour - epex_cost_last_hour
        savings_percent_last_hour = (savings_last_hour / current_cost_last_hour * 100) if current_cost_last_hour > 0 else 0
        
        # Empfehlung
        if savings > 0:
            recommendation = "🟢 Wechsel"
        else:
            recommendation = "🔴 Aktueller Tarif"
        
        return {
            'current_consumption': current_consumption,
            'current_tariff': current_tariff,
            'current_epex': current_epex,
            'current_cost': current_cost,
            'epex_cost': epex_cost,
            'savings': savings,
            'savings_percent': savings_percent,
            'recommendation': recommendation,
            # Letzte Viertelstunde Details
            'avg_consumption_last_quarter': avg_consumption_last_quarter,
            'max_consumption_last_quarter': max_consumption_last_quarter,
            'min_consumption_last_quarter': min_consumption_last_quarter,
            'total_consumption_last_quarter_kwh': total_consumption_last_quarter_kwh,
            'current_cost_last_quarter': current_cost_last_quarter,
            'epex_cost_last_quarter': epex_cost_last_quarter,
            'savings_last_quarter': savings_last_quarter,
            'savings_percent_last_quarter': savings_percent_last_quarter,
            'avg_epex_last_quarter': avg_epex_last_quarter,
            'max_epex_last_quarter': max_epex_last_quarter,
            'min_epex_last_quarter': min_epex_last_quarter,
            # Letzte Stunde Details
            'avg_consumption_last_hour': avg_consumption_last_hour,
            'max_consumption_last_hour': max_consumption_last_hour,
            'min_consumption_last_hour': min_consumption_last_hour,
            'total_consumption_last_hour_kwh': total_consumption_last_hour_kwh,
            'current_cost_last_hour': current_cost_last_hour,
            'epex_cost_last_hour': epex_cost_last_hour,
            'savings_last_hour': savings_last_hour,
            'savings_percent_last_hour': savings_percent_last_hour,
            'avg_epex_last_hour': avg_epex_last_hour,
            'max_epex_last_hour': max_epex_last_hour,
            'min_epex_last_hour': min_epex_last_hour
        }
        
        logger.info(f"Echtzeit-Analyse abgeschlossen - Letzte Stunde: {avg_consumption_last_hour:.0f} W → {total_consumption_last_hour_kwh:.3f} kWh")
        logger.info(f"Letzte Viertelstunde: {avg_consumption_last_quarter:.0f} W → {total_consumption_last_quarter_kwh:.3f} kWh")
        
    except Exception as e:
        logger.error(f"Fehler in Echtzeit-Analyse: {e}")
        return None

# Test
if __name__ == "__main__":
    import numpy as np
    from datetime import datetime, timedelta
    
    # Testdaten - genug für Viertelstunde und Stunde
    time_range = pd.date_range(datetime.now() - timedelta(hours=2), datetime.now(), freq='1min')
    consumption_data = pd.DataFrame({
        'time': time_range,
        'value': np.random.normal(800, 100, len(time_range))
    }).set_index('time')
    
    tariff_data = pd.DataFrame({
        'time': time_range,
        'value': np.random.normal(0.25, 0.05, len(time_range))
    }).set_index('time')
    
    result = analyze_realtime(consumption_data, tariff_data, 0.30)
    print("Echtzeit-Analyse:")
    print(result)