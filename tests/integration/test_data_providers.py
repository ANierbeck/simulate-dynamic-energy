"""
Integration tests for data providers
"""

import pytest
import pandas as pd
from datetime import datetime
from core.data.providers import generate_sample_tariff_data


def test_generate_sample_tariff_data_basic():
    """Test basic sample tariff data generation"""
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)
    
    tariff_data = generate_sample_tariff_data(start_time, end_time)
    
    assert isinstance(tariff_data, pd.DataFrame)
    assert len(tariff_data) > 0
    assert 'time' not in tariff_data.columns  # time should be the index
    
    # Check that we have data for known providers
    expected_providers = ["Tiwatt", "AWATTAR", "Tibber", "Rabot Energy", "Tado"]
    for provider in expected_providers:
        assert provider in tariff_data.columns


def test_generate_sample_tariff_data_time_range():
    """Test that the correct time range is generated"""
    start_time = datetime(2023, 1, 1, 0, 0, 0)
    end_time = datetime(2023, 1, 1, 23, 59, 59)
    
    tariff_data = generate_sample_tariff_data(start_time, end_time)
    
    # Should have 24 hours of data (one per hour)
    assert len(tariff_data) == 24
    
    # Check first and last timestamps
    first_time = tariff_data.index[0]
    last_time = tariff_data.index[-1]
    
    assert first_time.year == 2023
    assert first_time.month == 1
    assert first_time.day == 1
    assert last_time.year == 2023
    assert last_time.month == 1
    assert last_time.day == 1


def test_generate_sample_tariff_data_price_ranges():
    """Test that generated prices are within reasonable ranges"""
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)
    
    tariff_data = generate_sample_tariff_data(start_time, end_time)
    
    # Check price ranges for each provider
    for provider in tariff_data.columns:
        prices = tariff_data[provider]
        
        # All prices should be positive
        assert (prices > 0).all(), f"{provider} has non-positive prices"
        
        # Prices should be reasonable (between 0.10 and 0.50 €/kWh)
        assert (prices >= 0.10).all(), f"{provider} has prices below minimum"
        assert (prices <= 0.50).all(), f"{provider} has prices above maximum"


def test_generate_sample_tariff_data_reproducibility():
    """Test that data generation is reproducible with same seed"""
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)
    
    # Generate data twice
    tariff_data_1 = generate_sample_tariff_data(start_time, end_time)
    tariff_data_2 = generate_sample_tariff_data(start_time, end_time)
    
    # Should be identical due to fixed random seed
    pd.testing.assert_frame_equal(tariff_data_1, tariff_data_2)


def test_generate_sample_tariff_data_multi_day():
    """Test data generation over multiple days"""
    start_time = datetime(2023, 1, 1, 0, 0, 0)
    end_time = datetime(2023, 1, 7, 23, 59, 59)  # 7 full days
    
    tariff_data = generate_sample_tariff_data(start_time, end_time)
    
    # Should have 7 * 24 = 168 hours of data
    # Note: pandas date_range with freq='h' is inclusive, so we get exactly the expected number
    expected_hours = 7 * 24
    assert len(tariff_data) == expected_hours, f"Expected {expected_hours} hours, got {len(tariff_data)}"