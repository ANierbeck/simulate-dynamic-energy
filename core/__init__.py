"""
Kernmodule für die dynamische Stromtarif-Analyse
"""

from .config import CONFIG, TARIFF_PROVIDERS
from .data import get_influxdb_client, fetch_senec_house_power_data
from .analysis import analyze_historical_consumption, calculate_costs

__version__ = "0.1.0"
__author__ = "Dynamic Energy Analysis Team"