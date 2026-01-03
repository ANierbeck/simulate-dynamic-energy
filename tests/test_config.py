"""
Test configuration for the dynamic energy analysis application
"""

import os
import pytest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set test environment variables
os.environ['CURRENT_TARIFF'] = '0.30'
os.environ['ANALYSIS_PERIOD'] = '7d'
os.environ['TIMEZONE'] = 'Europe/Berlin'
os.environ['DATA_SCALING_FACTOR'] = '1.0'

# Test data constants
TEST_PROVIDERS = ["Tiwatt", "AWATTAR", "Tibber"]
TEST_START_TIME = datetime(2023, 1, 1, 0, 0, 0)
TEST_END_TIME = datetime(2023, 1, 7, 23, 59, 59)

def create_test_consumption_data():
    """Create test consumption data"""
    time_range = pd.date_range(start=TEST_START_TIME, end=TEST_END_TIME, freq='h')
    consumption_values = np.random.normal(500, 100, len(time_range))  # Average 500W with some variation
    consumption_values = np.maximum(0, consumption_values)  # Ensure no negative values
    
    return pd.DataFrame({
        'value': consumption_values
    }, index=time_range)

def create_test_tariff_data():
    """Create test tariff data for multiple providers"""
    time_range = pd.date_range(start=TEST_START_TIME, end=TEST_END_TIME, freq='h')
    
    data = {'time': time_range}
    
    # Create realistic tariff data for each provider
    np.random.seed(42)  # For reproducible tests
    
    for provider in TEST_PROVIDERS:
        if provider == "Tiwatt":
            # Tiwatt has more variation with some low prices
            base_prices = np.random.normal(0.25, 0.08, len(time_range))
            # Add some low-price periods (early morning)
            for i, time in enumerate(time_range):
                if time.hour in [2, 3, 4]:  # Early morning discount
                    base_prices[i] = max(0.15, base_prices[i] * 0.7)
        elif provider == "AWATTAR":
            # AWATTAR has generally lower but more stable prices
            base_prices = np.random.normal(0.22, 0.06, len(time_range))
        elif provider == "Tibber":
            # Tibber has higher average but more predictable
            base_prices = np.random.normal(0.28, 0.05, len(time_range))
        
        # Ensure minimum price of 0.10 €/kWh
        data[provider] = np.maximum(0.10, base_prices)
    
    return pd.DataFrame(data).set_index('time')

@pytest.fixture
def sample_consumption_data():
    """Pytest fixture for sample consumption data"""
    return create_test_consumption_data()

@pytest.fixture
def sample_tariff_data():
    """Pytest fixture for sample tariff data"""
    return create_test_tariff_data()

@pytest.fixture
def sample_config():
    """Pytest fixture for sample configuration"""
    from core.config import CONFIG
    return CONFIG