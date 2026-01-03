"""
Unit tests for cost calculation functions
"""

import pytest
import pandas as pd
import numpy as np
from core.analysis.cost import calculate_costs, find_best_alternative
from tests.test_config import create_test_consumption_data, create_test_tariff_data


def test_calculate_costs_basic():
    sample_consumption_data = create_test_consumption_data()
    sample_tariff_data = create_test_tariff_data()
    """Test basic cost calculation functionality"""
    costs = calculate_costs(sample_consumption_data, sample_tariff_data)
    
    assert isinstance(costs, dict)
    assert 'Aktueller Tarif' in costs
    assert len(costs) > 1  # Should have current tariff + provider tariffs
    
    # Check that costs are reasonable (not negative, not zero)
    for provider, cost in costs.items():
        assert cost > 0, f"Cost for {provider} should be positive"
        assert cost < 1000, f"Cost for {provider} seems unreasonably high"


def test_calculate_costs_with_zero_consumption():
    """Test cost calculation with zero consumption"""
    # Create empty consumption data
    time_range = pd.date_range(start='2023-01-01', end='2023-01-02', freq='h')
    consumption_data = pd.DataFrame({'value': [0] * len(time_range)}, index=time_range)
    
    # Create simple tariff data
    tariff_data = pd.DataFrame({
        'time': time_range,
        'Tiwatt': [0.25] * len(time_range)
    }).set_index('time')
    
    costs = calculate_costs(consumption_data, tariff_data)
    
    # All costs should be zero
    for cost in costs.values():
        assert cost == 0, "Costs should be zero for zero consumption"


def test_find_best_alternative():
    """Test finding the best alternative tariff"""
    sample_consumption_data = create_test_consumption_data()
    sample_tariff_data = create_test_tariff_data()
    costs = calculate_costs(sample_consumption_data, sample_tariff_data)
    best_provider, savings, savings_percent = find_best_alternative(costs)
    
    assert best_provider is not None
    assert isinstance(savings, (int, float))
    assert isinstance(savings_percent, (int, float))
    assert savings >= 0
    assert savings_percent >= 0


def test_find_best_alternative_no_alternatives():
    """Test when there are no alternatives to current tariff"""
    costs = {'Aktueller Tarif': 100.0}
    best_provider, savings, savings_percent = find_best_alternative(costs)
    
    assert best_provider is None
    assert savings == 0
    assert savings_percent == 0


def test_find_best_alternative_with_negative_savings():
    """Test when all alternatives are more expensive"""
    costs = {
        'Aktueller Tarif': 100.0,
        'Tiwatt': 150.0,
        'AWATTAR': 120.0
    }
    best_provider, savings, savings_percent = find_best_alternative(costs)
    
    # Should find the "best" (least expensive) alternative even if it's more expensive
    assert best_provider == 'AWATTAR'
    assert savings == -20.0  # Negative savings means it's more expensive
    assert savings_percent == -20.0


def test_cost_calculation_timezone_handling():
    """Test that timezone handling works correctly"""
    # Create consumption data with timezone
    time_range = pd.date_range(start='2023-01-01', end='2023-01-02', freq='h', tz='Europe/Berlin')
    consumption_data = pd.DataFrame({'value': [500] * len(time_range)}, index=time_range)
    
    # Create tariff data with timezone
    tariff_data = pd.DataFrame({
        'time': time_range,
        'Tiwatt': [0.25] * len(time_range)
    }).set_index('time')
    
    # Should handle timezone conversion without error
    costs = calculate_costs(consumption_data, tariff_data)
    assert costs is not None
    assert 'Tiwatt' in costs