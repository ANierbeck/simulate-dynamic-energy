"""
MOCK Provider-Daten für Entwicklung
DIESE DATEN SIND ERFUNDEN - NICHT ECHT!

Dies ist ein Platzhalter, bis wir echte API-Integrationen haben.
Jeder Provider hat unterschiedliche APIs und viele haben keine öffentlichen APIs.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MockTariffProvider:
    """Erzeugt ERFUNDENE Tarifdaten für Entwicklung und Testing"""
    
    def __init__(self):
        self.providers = [
            {"name": "Tiwatt", "base": 0.25, "variation": 0.05},
            {"name": "AWATTAR", "base": 0.22, "variation": 0.04},
            {"name": "Tibber", "base": 0.28, "variation": 0.03},
            {"name": "Rabot Energy", "base": 0.20, "variation": 0.035},
            {"name": "Tado", "base": 0.30, "variation": 0.04}
        ]
    
    def generate(self, start_time, end_time):
        """Generiert ERFUNDENE Daten - NICHT ECHT!"""
        try:
            time_range = pd.date_range(start=start_time, end=end_time, freq='H')
            
            data = {'time': time_range}
            
            for provider in self.providers:
                # ERFUNDENE Preise - NICHT ECHT!
                base = provider["base"]
                variation = provider["variation"]
                
                # Sinus-Muster für "realistische" Schwankungen
                data[provider["name"]] = np.maximum(
                    0.10,  # Mindestpreis
                    base + np.sin(np.arange(len(time_range)) * 0.1) * variation + 
                    np.random.normal(0, variation/2, len(time_range))
                )
            
            df = pd.DataFrame(data).set_index('time')
            
            logger.warning("⚠️  ACHTUNG: Diese Tarifdaten sind ERFUNDEN!")
            logger.warning("⚠️  ECHTE Tarif-APIs müssen noch integriert werden!")
            logger.info(f"Generierte MOCK-Daten: {len(df)} Datensätze")
            
            return df
            
        except Exception as e:
            logger.error(f"Fehler in MOCK-Daten: {e}")
            return None

# Test
if __name__ == "__main__":
    mock = MockTariffProvider()
    start = datetime.now() - timedelta(days=7)
    end = datetime.now()
    data = mock.generate(start, end)
    print("⚠️  ACHTUNG: Diese Daten sind ERFUNDEN!")
    print(data.head())
