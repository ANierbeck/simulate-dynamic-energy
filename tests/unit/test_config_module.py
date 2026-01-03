"""
Unit tests for the config module
"""

import pytest
from core.config import CONFIG, get_provider_config, TARIFF_PROVIDERS


def test_config_loading():
    """Test that configuration loads correctly"""
    assert isinstance(CONFIG, dict)
    assert 'current_tariff' in CONFIG
    assert 'analysis_period' in CONFIG
    assert 'timezone' in CONFIG
    assert 'data_sources' in CONFIG


def test_default_values():
    """Test that default values are set correctly"""
    assert CONFIG['current_tariff'] == 0.30
    assert CONFIG['analysis_period'] == '30d'
    assert CONFIG['timezone'] == 'Europe/Berlin'
    assert CONFIG['data_scaling_factor'] == 1.0


def test_provider_config():
    """Test provider configuration"""
    assert isinstance(TARIFF_PROVIDERS, dict)
    assert len(TARIFF_PROVIDERS) > 0
    
    # Test that known providers are present
    expected_providers = ["Tiwatt", "AWATTAR", "Tibber", "Rabot Energy", "Tado"]
    for provider in expected_providers:
        assert provider in TARIFF_PROVIDERS
        provider_config = TARIFF_PROVIDERS[provider]
        assert 'description' in provider_config
        assert 'url' in provider_config
        assert 'color' in provider_config
        assert 'api_endpoint' in provider_config


def test_get_provider_config():
    """Test the get_provider_config function"""
    # Test existing provider
    tiwatt_config = get_provider_config("Tiwatt")
    assert isinstance(tiwatt_config, dict)
    assert tiwatt_config['description'] == "Dynamischer Stromtarif mit stündlichen Preisen"
    
    # Test non-existing provider
    unknown_config = get_provider_config("UnknownProvider")
    assert unknown_config == {}


def test_data_sources_config():
    """Test data sources configuration"""
    data_sources = CONFIG['data_sources']
    assert 'influxdb' in data_sources
    
    influxdb_config = data_sources['influxdb']
    assert 'enabled' in influxdb_config
    assert 'url' in influxdb_config
    assert 'token' in influxdb_config
    assert 'org' in influxdb_config
    assert 'bucket' in influxdb_config
    assert 'measurement' in influxdb_config
    assert 'entity_id' in influxdb_config
    assert 'entity_ids' in influxdb_config
    assert 'market_entity_ids' in influxdb_config