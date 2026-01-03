"""
Kostenanalysemodul
"""

import logging
from core.config import CONFIG

# Logging konfigurieren
logger = logging.getLogger(__name__)

def calculate_costs(consumption_data, tariff_data):
    """
    Berechnet die Kosten für verschiedene Tarife
    
    Args:
        consumption_data (DataFrame): Verbrauchsdaten
        tariff_data (DataFrame): Tarifdaten mit Provider-Spalten
        
    Returns:
        dict: Kosten pro Provider
    """
    try:
        costs = {}
        
        # Aktueller Tarif
        total_consumption_kwh = consumption_data['value'].sum() / 1000
        current_cost = total_consumption_kwh * CONFIG['current_tariff']
        costs['Aktueller Tarif'] = current_cost
        
        # Dynamische Tarife
        for provider in tariff_data.columns:
            if provider != 'time':  # Zeitspalte überspringen
                # Zeitstempel synchronisieren (gleiche Zeitzone)
                consumption_copy = consumption_data.copy()
                tariff_copy = tariff_data[[provider]].copy()
                
                # Zeitstempel ohne Zeitzone verwenden
                if consumption_copy.index.tz is not None:
                    consumption_copy.index = consumption_copy.index.tz_localize(None)
                if tariff_copy.index.tz is not None:
                    tariff_copy.index = tariff_copy.index.tz_localize(None)
                
                # Stündliche Kosten berechnen
                hourly_costs = (consumption_copy['value'] / 1000) * tariff_copy[provider]
                total_cost = hourly_costs.sum()
                costs[provider] = total_cost
        
        logger.info(f"Kostenberechnung abgeschlossen für {len(costs)} Tarife")
        return costs
        
    except Exception as e:
        logger.error(f"Fehler bei der Kostenberechnung: {e}")
        return None

def find_best_alternative(costs):
    """
    Findet die beste Alternative zum aktuellen Tarif
    
    Args:
        costs (dict): Kosten pro Provider
        
    Returns:
        tuple: (best_provider, savings, savings_percent)
    """
    try:
        if not costs or 'Aktueller Tarif' not in costs:
            return None, 0, 0
        
        current_cost = costs['Aktueller Tarif']
        
        # Beste Alternative finden (niedrigste Kosten, nicht der aktuelle Tarif)
        alternatives = {k: v for k, v in costs.items() if k != 'Aktueller Tarif'}
        
        if not alternatives:
            return None, 0, 0
        
        best_provider = min(alternatives.items(), key=lambda x: x[1])[0]
        best_cost = alternatives[best_provider]
        
        savings = current_cost - best_cost
        savings_percent = (savings / current_cost * 100) if current_cost > 0 else 0
        
        logger.info(f"Beste Alternative: {best_provider} (Einsparung: {savings:.2f} €, {savings_percent:.1f}%)")
        
        return best_provider, savings, savings_percent
        
    except Exception as e:
        logger.error(f"Fehler bei der Suche nach bester Alternative: {e}")
        return None, 0, 0