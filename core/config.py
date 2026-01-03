"""
Konfigurationsmodul für die Stromtarif-Analyse
"""

import os
from dotenv import load_dotenv

# Umgebungseinstellungen laden
load_dotenv()

# Hauptkonfiguration
CONFIG = {
    "current_tariff": float(os.getenv("CURRENT_TARIFF", "0.30")),  # Aktueller Strompreis in €/kWh
    "analysis_period": os.getenv("ANALYSIS_PERIOD", "30d"),  # Standard-Analysezeitraum
    "timezone": os.getenv("TIMEZONE", "Europe/Berlin"),
    "data_scaling_factor": float(os.getenv("DATA_SCALING_FACTOR", "1.0")),  # Skalierungsfaktor für Rohdaten (1.0 = W, 0.001 = kW, 1000 = Wh zu W)
    "data_sources": {
        "influxdb": {
            "enabled": os.getenv("INFLUXDB_ENABLED", "true").lower() == "true",
            "url": os.getenv("INFLUXDB_URL", "http://localhost:8086"),
            "token": os.getenv("INFLUXDB_TOKEN", ""),  # Optional
            "org": os.getenv("INFLUXDB_ORG", "homeassistant"),
            "bucket": os.getenv("INFLUXDB_BUCKET", "homeassistant"),
            "measurement": os.getenv("INFLUXDB_MEASUREMENT", "W"),
            "entity_id": os.getenv("INFLUXDB_ENTITY_ID", "senec_house_power"),
            "entity_ids": {
                "house_power": os.getenv("INFLUXDB_ENTITY_HOUSE_POWER", "senec_house_power"),
                "solar_generated": os.getenv("INFLUXDB_ENTITY_SOLAR_GENERATED", "senec_solar_generated_power"),
                "battery_power": os.getenv("INFLUXDB_ENTITY_BATTERY_POWER", "senec_battery_state_power"),
                "grid_power": os.getenv("INFLUXDB_ENTITY_GRID_POWER", "senec_grid_state_power")
            },
            "market_entity_ids": {
                "market_price": os.getenv("INFLUXDB_MARKET_PRICE", "epex_spot_data_market_price"),
                "total_price": os.getenv("INFLUXDB_TOTAL_PRICE", "epex_spot_data_total_price")
            }
        }
    }
}

# Unterstützte Tarif-Provider
TARIFF_PROVIDERS = {
    "Tiwatt": {
        "description": "Dynamischer Stromtarif mit stündlichen Preisen",
        "url": "https://www.tiwatt.de/",
        "color": "#FF6B35",
        "api_endpoint": "https://api.tiwatt.de/v1/prices"
    },
    "AWATTAR": {
        "description": "Österreichischer Spotmarkt-Tarif",
        "url": "https://www.awattar.de/",
        "color": "#4CAF50",
        "api_endpoint": "https://api.awattar.de/v1/marketdata"
    },
    "Tibber": {
        "description": "Intelligenter Stromtarif mit App-Steuerung",
        "url": "https://tibber.com/de",
        "color": "#2196F3",
        "api_endpoint": "https://api.tibber.com/v1-beta/gql"
    },
    "Rabot Energy": {
        "description": "Dynamischer Tarif mit KI-Optimierung",
        "url": "https://www.rabotenergy.com/",
        "color": "#9C27B0",
        "api_endpoint": "https://api.rabotenergy.com/v2/prices"
    },
    "Tado": {
        "description": "Smart Home integrierter Tarif",
        "url": "https://www.tado.com/",
        "color": "#FF9800",
        "api_endpoint": "https://api.tado.com/v2/energy-prices"
    }
}

def get_provider_config(provider_name):
    """Gibt die Konfiguration für einen bestimmten Provider zurück"""
    return TARIFF_PROVIDERS.get(provider_name, {})