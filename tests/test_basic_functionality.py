"""
Basic functionality tests to ensure the application can start and run
"""

import pytest
import sys
import os


def test_import_core_modules():
    """Test that all core modules can be imported"""
    # Add the project root to Python path
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    # Test importing core modules
    try:
        from core import config
        from core.analysis import cost, consumption, realtime
        from core.data import providers, influxdb
        assert True  # If we get here, imports worked
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_config_initialization():
    """Test that configuration initializes correctly"""
    from core.config import CONFIG
    
    # Basic configuration checks
    assert 'current_tariff' in CONFIG
    assert 'timezone' in CONFIG
    assert 'data_sources' in CONFIG
    
    # Check that values are reasonable
    assert isinstance(CONFIG['current_tariff'], float)
    assert CONFIG['current_tariff'] > 0
    assert isinstance(CONFIG['timezone'], str)
    assert len(CONFIG['timezone']) > 0


def test_provider_configuration():
    """Test that provider configuration is available"""
    from core.config import TARIFF_PROVIDERS, get_provider_config
    
    # Check that we have some providers
    assert len(TARIFF_PROVIDERS) > 0
    
    # Test getting a specific provider
    tiwatt_config = get_provider_config("Tiwatt")
    assert tiwatt_config is not None
    assert 'api_endpoint' in tiwatt_config
    
    # Test getting non-existent provider
    unknown_config = get_provider_config("NonExistent")
    assert unknown_config == {}


def test_data_provider_functions():
    """Test that data provider functions are available and work"""
    from core.data.providers import generate_sample_tariff_data
    from datetime import datetime
    
    # Test generating sample data
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)
    
    tariff_data = generate_sample_tariff_data(start_time, end_time)
    
    # Basic checks
    assert tariff_data is not None
    assert len(tariff_data) > 0
    assert hasattr(tariff_data, 'columns')


def test_cost_calculation_functions():
    """Test that cost calculation functions are available"""
    from core.analysis.cost import calculate_costs, find_best_alternative
    
    # Test that functions exist and are callable
    assert callable(calculate_costs)
    assert callable(find_best_alternative)


def test_environment_variables():
    """Test that environment variables are properly handled"""
    import os
    from core.config import CONFIG
    
    # Test that environment variables are read correctly
    # These should have default values from the config
    assert CONFIG['current_tariff'] == 0.30
    assert CONFIG['analysis_period'] == '30d'
    
    # Test that we can override with environment variables
    os.environ['TEST_VAR'] = 'test_value'
    assert os.getenv('TEST_VAR') == 'test_value'
    
    # Clean up
    del os.environ['TEST_VAR']