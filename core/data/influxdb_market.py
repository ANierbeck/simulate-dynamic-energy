"""
InfluxDB Integration für echte Marktdaten (EPEX Spot)
"""

import pandas as pd
from datetime import datetime
from influxdb import InfluxDBClient
from core.config import CONFIG
import logging

logger = logging.getLogger(__name__)

def fetch_market_prices(start_time, end_time):
    """
    Ruft echte EPEX Spot-Marktdaten aus InfluxDB ab
    """
    try:
        influx_config = CONFIG["data_sources"]["influxdb"]
        
        # Parse URL
        from urllib.parse import urlparse
        parsed_url = urlparse(influx_config["url"])
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 8086
        
        # Verbindung herstellen
        client = InfluxDBClient(
            host=host,
            port=port,
            database=influx_config["bucket"]
        )
        
        # Query für EPEX Spot Daten - Verwende den korrekten Total Price
        # Genau wie in Grafana: SELECT distinct("value") FROM "€/kWh" WHERE ("entity_id"::tag = 'epex_spot_data_total_price')
        query = f'''
        SELECT "value" 
        FROM "€/kWh" 
        WHERE "entity_id" = '{CONFIG["data_sources"]["influxdb"]["market_entity_ids"]["total_price"]}' 
        AND time >= '{start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}' 
        AND time <= '{end_time.strftime("%Y-%m-%dT%H:%M:%SZ")}'
        '''
        
        logger.info(f"Lade EPEX Spot Daten: {query}")
        
        # Query ausführen
        result = client.query(query)
        
        if not result:
            logger.warning("Keine EPEX Spot Daten gefunden")
            return None
        
        # Daten verarbeiten
        data = []
        for point in result.get_points():
            data.append({
                "time": point['time'],
                "value": point['value']  # Preis in €/kWh
            })
        
        if not data:
            return None
        
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], format='mixed', errors='coerce')
        df = df.dropna(subset=['time'])
        df.set_index('time', inplace=True)
        
        logger.info(f"✅ EPEX Spot Daten geladen: {len(df)} Datensätze")
        return df
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der EPEX Spot Daten: {e}")
        return None
    finally:
        if 'client' in locals():
            client.close()

# Test
if __name__ == "__main__":
    from datetime import timedelta
    start = datetime.now() - timedelta(days=7)
    end = datetime.now()
    data = fetch_market_prices(start, end)
    if data is not None:
        print("✅ EPEX Spot Daten:")
        print(data.head())
