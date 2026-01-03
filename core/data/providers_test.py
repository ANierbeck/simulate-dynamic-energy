"""
Test-Provider-Daten für Entwicklung
Simuliert echte Tarifdaten, bis wir die APIs integrieren
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.config import TARIFF_PROVIDERS
import logging

logger = logging.getLogger(__name__)

def generate_realistic_tariff_data(start_time, end_time):
    """
    Generiert realistische Tarifdaten basierend auf echten Marktmustern
    """
    try:
        # Zeitachse erstellen
        time_range = pd.date_range(start=start_time, end=end_time, freq='H')
        
        # Basispreise für verschiedene Provider (realistische Muster)
        np.random.seed(42)  # Für reproduzierbare Ergebnisse
        
        data = {'time': time_range}
        
        # Tiwatt - Dynamisch mit Spitzen und Tälern
        base_tiwatt = 0.25
        data['Tiwatt'] = np.maximum(0.15, base_tiwatt + np.sin(np.arange(len(time_range)) * 0.1) * 0.05 + np.random.normal(0, 0.02, len(time_range)))
        
        # AWATTAR - Spotmarkt-basiert
        base_awattar = 0.22
        data['AWATTAR'] = np.maximum(0.10, base_awattar + np.sin(np.arange(len(time_range)) * 0.15) * 0.04 + np.random.normal(0, 0.015, len(time_range)))
        
        # Tibber - Stabiler mit leichten Schwankungen
        base_tibber = 0.28
        data['Tibber'] = np.maximum(0.18, base_tibber + np.sin(np.arange(len(time_range)) * 0.12) * 0.03 + np.random.normal(0, 0.01, len(time_range)))
        
        # Rabot Energy - KI-optimiert
        base_rabot = 0.20
        data['Rabot Energy'] = np.maximum(0.12, base_rabot + np.sin(np.arange(len(time_range)) * 0.18) * 0.035 + np.random.normal(0, 0.018, len(time_range)))
        
        # Tado - Smart Home integriert
        base_tado = 0.30
        data['Tado'] = np.maximum(0.20, base_tado + np.sin(np.arange(len(time_range)) * 0.1) * 0.04 + np.random.normal(0, 0.012, len(time_range)))
        
        df = pd.DataFrame(data).set_index('time')
        
        logger.info(f"Generierte realistische Tarifdaten für {len(TARIFF_PROVIDERS)} Provider")
        logger.info(f"Zeitraum: {start_time} bis {end_time}")
        logger.info(f"Datensätze: {len(df)}")
        
        return df
        
    except Exception as e:
        logger.error(f"Fehler beim Generieren von Tarifdaten: {e}")
        return None

# Testfunktion
if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    start = datetime.now() - timedelta(days=7)
    end = datetime.now()
    
    data = generate_realistic_tariff_data(start, end)
    if data is not None:
        print("✅ Tarifdaten generiert:")
        print(data.head())
        print(f"\nStatistiken:")
        for provider in TARIFF_PROVIDERS.keys():
            if provider in data.columns:
                print(f"  {provider}: {data[provider].mean():.3f} €/kWh (∅)")
