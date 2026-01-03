"""
InfluxDB v1 API Integration (ohne Flux)
Für InfluxDB 1.x Systeme
"""

import logging
from datetime import datetime
from influxdb import InfluxDBClient as InfluxDBClientV1
from core.config import CONFIG
import pandas as pd

# Logging konfigurieren
logger = logging.getLogger(__name__)

def get_influxdb_v1_client():
    """
    Erstellt einen InfluxDB v1 Client
    """
    try:
        influx_config = CONFIG["data_sources"]["influxdb"]
        
        # Parse URL richtig
        from urllib.parse import urlparse
        parsed_url = urlparse(influx_config["url"])
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 8086
        
        logger.info(f"Versuche Verbindung zu InfluxDB v1: {host}:{port}")
        
        # InfluxDB v1 Client erstellen
        client = InfluxDBClientV1(
            host=host,
            port=port,
            username='',  # Standard für v1
            password='',  # Standard für v1
            database=influx_config["bucket"],  # Bucket = Database in v1
            ssl=False,
            timeout=10
        )
        
        # Testverbindung
        try:
            databases = client.get_list_database()
            logger.info(f"Verbindung erfolgreich! Verfügbare Datenbanken: {databases}")
        except Exception as test_e:
            logger.error(f"Testverbindung fehlgeschlagen: {test_e}")
        
        return client
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des InfluxDB v1 Clients: {e}")
        return None

def fetch_senec_house_power_data_v1(start_time, end_time):
    """
    Ruft SENEC House Power Daten über InfluxDB v1 API ab
    """
    return fetch_senec_power_data_v1(start_time, end_time, CONFIG['data_sources']['influxdb']['entity_ids']['house_power'])

def fetch_senec_solar_generated_power_v1(start_time, end_time):
    """
    Ruft SENEC Solar Generated Power Daten über InfluxDB v1 API ab
    """
    return fetch_senec_power_data_v1(start_time, end_time, CONFIG['data_sources']['influxdb']['entity_ids']['solar_generated'])

def fetch_senec_battery_power_v1(start_time, end_time):
    """
    Ruft SENEC Battery Power Daten über InfluxDB v1 API ab
    """
    return fetch_senec_power_data_v1(start_time, end_time, CONFIG['data_sources']['influxdb']['entity_ids']['battery_power'])

def fetch_senec_grid_power_v1(start_time, end_time):
    """
    Ruft SENEC Grid Power Daten über InfluxDB v1 API ab
    """
    return fetch_senec_power_data_v1(start_time, end_time, CONFIG['data_sources']['influxdb']['entity_ids']['grid_power'])

def fetch_senec_power_data_v1(start_time, end_time, entity_id):
    """
    Generische Funktion zum Abrufen von SENEC Power Daten über InfluxDB v1 API
    """
    try:
        client = get_influxdb_v1_client()
        if client is None:
            return None
        
        # Query für v1 API - genau wie Grafana!
        # Einfache Query ohne GROUP BY für bessere Kompatibilität
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        query = f'''
        SELECT "value" 
        FROM "{CONFIG['data_sources']['influxdb']['measurement']}" 
        WHERE "entity_id" = '{entity_id}' 
        AND time >= '{start_time.strftime(time_format)}' 
        AND time <= '{end_time.strftime(time_format)}'
        '''
        
        logger.info(f"Ausführende Query für {entity_id}: {query}")
        
        logger.info(f"Führe InfluxDB v1 Query aus für {entity_id} im Zeitraum: {start_time} bis {end_time}")
        
        # Query ausführen
        result = client.query(query)
        
        if not result:
            logger.warning(f"Keine Daten gefunden für {entity_id}")
            return None
        
        # Ergebnisse in DataFrame konvertieren
        data = []
        for point in result.get_points():
            data.append({
                "time": point['time'],
                "value": point['value']  # Direkt den Wert nehmen, nicht mean
            })
        
        if not data:
            logger.warning(f"Keine Datensätze gefunden für {entity_id}")
            return None
        
        df = pd.DataFrame(data)
        # Flexibles Zeitstempel-Parsing für verschiedene Formate
        df['time'] = pd.to_datetime(df['time'], format='mixed', errors='coerce')
        # Filtere ungültige Zeitstempel
        df = df.dropna(subset=['time'])
        df.set_index('time', inplace=True)
        
        # Skalierungsfaktor anwenden (falls Daten in Wh statt W gespeichert sind)
        scaling_factor = float(CONFIG.get("data_scaling_factor", 1.0))
        if scaling_factor != 1.0:
            df['value'] = df['value'] * scaling_factor
            logger.info(f"Daten skaliert mit Faktor {scaling_factor} (z.B. Wh zu W)")
        
        logger.info(f"Erfolgreich {len(df)} Datensätze abgerufen für {entity_id}")
        return df
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Daten für {entity_id} mit v1 API: {e}")
        return None
    finally:
        if 'client' in locals():
            client.close()