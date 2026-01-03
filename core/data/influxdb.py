"""
InfluxDB Datenzugriffsmodul
"""

from influxdb_client import InfluxDBClient
from core.config import CONFIG
import logging

# Logging konfigurieren
logger = logging.getLogger(__name__)

def get_influxdb_client():
    """
    Erstellt und gibt einen InfluxDB Client zurück (mit optionalem Token)
    
    Returns:
        InfluxDBClient: Initialisierter InfluxDB Client oder None bei Fehler
    """
    try:
        influx_config = CONFIG["data_sources"]["influxdb"]
        token = influx_config["token"]
        
        if token:
            client = InfluxDBClient(
                url=influx_config["url"],
                token=token,
                org=influx_config["org"]
            )
        else:
            # Token-loser Zugriff für lokale InfluxDB Instanzen
            client = InfluxDBClient(
                url=influx_config["url"],
                org=influx_config["org"]
            )
        
        logger.info("InfluxDB Client erfolgreich erstellt")
        return client
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des InfluxDB Clients: {e}")
        return None

def fetch_senec_house_power_data(start_time, end_time):
    """
    Ruft die SENEC House Power Daten aus InfluxDB ab
    
    Args:
        start_time (datetime): Startzeitpunkt für die Abfrage
        end_time (datetime): Endzeitpunkt für die Abfrage
        
    Returns:
        DataFrame: Daten mit Zeitindex und Verbrauchswerten oder None bei Fehler
    """
    try:
        client = get_influxdb_client()
        if client is None:
            return None
        
        influx_config = CONFIG["data_sources"]["influxdb"]
        query_api = client.query_api()
        
        # Flux Query für SENEC House Power Daten
        flux_query = f'''
        from(bucket: "{influx_config["bucket"]}")
          |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
          |> filter(fn: (r) => r["_measurement"] == "{influx_config["measurement"]}")
          |> filter(fn: (r) => r["entity_id"] == "{influx_config["entity_id"]}")
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
        
        logger.info(f"Führe InfluxDB Query aus für Zeitraum: {start_time} bis {end_time}")
        
        # Query ausführen
        result = query_api.query(flux_query)
        
        # Ergebnisse in DataFrame konvertieren
        import pandas as pd
        data = []
        for table in result:
            for record in table.records:
                data.append({
                    "time": record.get_time(),
                    "value": record.get_value(),
                    "measurement": record.get_measurement()
                })
        
        if not data:
            logger.warning("Keine Daten gefunden für den angegebenen Zeitraum")
            return None
        
        df = pd.DataFrame(data)
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index)
        
        logger.info(f"Erfolgreich {len(df)} Datensätze abgerufen")
        return df
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der SENEC House Power Daten: {e}")
        
        # Spezifische Fehlerbehandlung für Flux
        if "Flux query service disabled" in str(e):
            logger.error("🔥 KRITISCHER FEHLER: Flux ist in Ihrer InfluxDB deaktiviert!")
            logger.error("💡 Lösung: Aktivieren Sie Flux in der InfluxDB-Konfiguration:")
            logger.error("   1. Öffnen Sie die InfluxDB-Konfiguration (influxdb.conf)")
            logger.error("   2. Suchen Sie den Abschnitt [http]")
            logger.error("   3. Setzen Sie flux-enabled = true")
            logger.error("   4. Starten Sie InfluxDB neu")
        
        return None
    finally:
        if 'client' in locals():
            client.close()