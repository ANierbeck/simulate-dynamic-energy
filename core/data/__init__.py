"""
Datenzugriffsmodule
"""

from .influxdb import get_influxdb_client, fetch_senec_house_power_data
from .influxdb_v1 import (get_influxdb_v1_client, fetch_senec_house_power_data_v1,
                          fetch_senec_solar_generated_power_v1,
                          fetch_senec_battery_power_v1,
                          fetch_senec_grid_power_v1)
from .providers import generate_sample_tariff_data, fetch_real_tariff_data

__all__ = [
    'get_influxdb_client',
    'fetch_senec_house_power_data',
    'get_influxdb_v1_client',
    'fetch_senec_house_power_data_v1',
    'fetch_senec_solar_generated_power_v1',
    'fetch_senec_battery_power_v1',
    'fetch_senec_grid_power_v1',
    'generate_sample_tariff_data',
    'fetch_real_tariff_data'
]