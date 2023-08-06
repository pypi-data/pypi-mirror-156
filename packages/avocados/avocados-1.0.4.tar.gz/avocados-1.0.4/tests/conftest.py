import pytest

@pytest.fixture
def supply_valid_data():
    return {'date': '01-29-2013', 
            'total_volume': 12.0, 
            'small_hass': 1.0, 
            'large_hass': 3.0, 
            'xlarge_hass': 6.0, 
            'total_bags': 49.0,
            'small_bags': 32.0,
            'large_bags': 5.0,
            'xlarge_bags': 12.0,
            'avocado_type': 'conventional',
            'year': 2013,
            'region': 'Albany' }

@pytest.fixture
def supply_expected_output():
    return {'date': '2013-01-29',
            'average_price': 1.135671615600586,
            'total_volume': 12.0, 
            'small_hass': 1.0, 
            'large_hass': 3.0, 
            'xlarge_hass': 6.0,
            'total_bags': 49.0,
            'small_bags': 32.0,
            'large_bags': 5.0,
            'xlarge_bags': 12.0,
            'avocado_type': 'conventional',
            'year': 2013,
            'region': 'Albany' }

@pytest.fixture
def supply_invalid_date_field():
    return {'date': '20dsa29', 
            'total_volume': 12.0, 
            'small_hass': 1.0, 
            'large_hass': 3.0, 
            'xlarge_hass': 6.0,
            'total_bags': 49.0,
            'small_bags': 32.0,
            'large_bags': 5.0,
            'xlarge_bags': 12.0,
            'avocado_type': 'conventional',
            'year': 2013,
            'region': 'Albany'}

@pytest.fixture
def supply_invalid_float_field():
    return {'date': '01-29-2013', 
            'total_volume': 'bla', 
            'small_hass': 1.0, 
            'large_hass': 3.0, 
            'x_large_hass': 6.0,
            'total_bags': 49.0,
            'small_bags': 32.0,
            'large_bags': 5.0,
            'x_large_bags': 12.0,
            'avocado_type': 'conventional',
            'year': 2013,
            'region': 'Albany'}