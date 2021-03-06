import os
import django
import pytest


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    django.setup()


@pytest.fixture
def json_error():
    data = {'success': False, 'error': {'info': 'Invalid json'}}
    return data


@pytest.fixture
def json_success():
    data = {
        'success': True, 'rates': {
            'AT': {
                'country_name': 'Austria', 'standard_rate': 20,
                'reduced_rates': {'foodstuffs': 10, 'books': 10}},
            "BE": {
                "country_name": "Belgium",
                "standard_rate": 21,
                "reduced_rates": {
                    "restaurants": 12,
                    "foodstuffs": 6,
                    "books": 6,
                    "water": 6,
                    "pharmaceuticals": 6,
                    "medical": 6,
                    "newspapers": 6,
                    "hotels": 6,
                    "admission to cultural events": 6,
                    "admission to entertainment events": 6
                }
            },
        }}
    return data


@pytest.fixture
def json_success_without_reduced_rates():
    data = {
        'success': True, 'rates': {
            'AZ': {
                'country_name': 'Austria', 'standard_rate': 20,
                'reduced_rates': None}}}
    return data


@pytest.fixture
def json_types_success():
    data = {'success': True, 'types': ['books', 'wine', 'medicine']}
    return data

