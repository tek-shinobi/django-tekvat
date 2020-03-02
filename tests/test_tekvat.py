import pytest
from tekmoney.currency import Currency
from tekmoney.currency_tax import CurrencyWithTax

from django_tekvat import utils
from django_tekvat.models import (
    TekvatVat,
    TekvatRateType,
    DEFAULT_TEKVAT_RATE_TYPES_INSTANCE_ID
)

@pytest.fixture
def fetch_vat_rates_success(monkeypatch, json_success):
    monkeypatch.setattr(utils, 'fetch_vat_rates', lambda: json_success)

@pytest.fixture
def fetch_vat_rates_error(monkeypatch, json_error):
    monkeypatch.setattr(utils, 'fetch_vat_rates', lambda: json_error)

@pytest.fixture
def fetch_rate_types_success(monkeypatch, json_types_success):
    monkeypatch.setattr(utils, 'fetch_rate_types', lambda: json_types_success)


@pytest.fixture
def fetch_rate_types_error(monkeypatch, json_error):
    monkeypatch.setattr(utils, 'fetch_rate_types', lambda: json_error)

@pytest.fixture
def rate_type(db):
    return TekvatRateType.objects.create(data=['protein', 'cola'])

@pytest.fixture
def set_country_codes(db, json_success):
    utils.save_vat_rate_by_country(json_success)

@pytest.fixture
def vat_country(db, json_success):
    data = json_success['rates']['AT']
    return TekvatVat.objects.create(country_code='AT', data=data)

@pytest.fixture
def set_vat_country_code_default1():
    rate = {
        'AT': {
            'country_name': 'Austria', 'standard_rate': 20,
            'reduced_rates': {'foodstuffs': 10, 'books': 10}}
    }
    return rate

@pytest.fixture
def set_vat_country_code_default():
    rate = {
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
        }
    return rate

def test_fetch_vat_rates_success(fetch_vat_rates_success, json_success):
    data = utils.fetch_vat_rates()
    assert data == json_success

def test_fetch_vat_rates_error(fetch_vat_rates_error, json_error):
    data = utils.fetch_vat_rates()
    assert data == json_error

def test_fetch_rate_types_success(fetch_rate_types_success, json_types_success):
    data = utils.fetch_rate_types()
    assert data == json_types_success

def test_fetch_rate_types_error(fetch_rate_types_error, json_error):
    data = utils.fetch_rate_types()
    assert data == json_error

@pytest.mark.django_db
def test_get_tax_rate_types(rate_type):
    rate_types = utils.get_tax_rate_types()
    assert rate_types == rate_type.data

@pytest.mark.django_db
def test_get_country_codes(set_country_codes, set_vat_country_code_default):
    codes_ref = [*set_vat_country_code_default]
    codes = utils.get_country_codes()
    if not set(codes) == set(codes_ref) or len(codes_ref) != len(codes):
        pytest.raises(AssertionError)


@pytest.mark.django_db
def test_get_reduced_tax_rates_for_country(set_country_codes, set_vat_country_code_default1):
    country_code = [*set_vat_country_code_default1][0]
    rates_ref = set_vat_country_code_default1.get(country_code, None).get('reduced_rates', None)
    rates = utils.get_reduced_tax_rates_for_country(country_code)
    assert rates == rates_ref

@pytest.mark.django_db
def test_get_standard_tax_rate_for_country(set_country_codes, set_vat_country_code_default1):
    country_code = [*set_vat_country_code_default1][0]
    rates_ref = set_vat_country_code_default1.get(country_code, None).get('standard_rate', None)
    rates = utils.get_standard_tax_rate_for_country(country_code)
    assert rates == rates_ref

@pytest.mark.django_db
def test_get_tax_rate(set_country_codes, set_vat_country_code_default1):
    country_code = [*set_vat_country_code_default1][0]
    ## test fallback standard tax rate
    rates_ref = set_vat_country_code_default1.get(country_code, None).get('standard_rate', None)
    rates = utils.get_tax_rates_for_country(country_code)
    rate = utils.get_tax_rate(rates)
    assert rate == rates_ref
    ## test reduced tax rate
    rates_ref = set_vat_country_code_default1.get(country_code, None)\
        .get('reduced_rates')\
        .get('books')
    rate = utils.get_tax_rate(rates, 'books')
    assert rate == rates_ref


@pytest.mark.django_db
def test_get_tax_for_rate(set_country_codes, set_vat_country_code_default1):
    country_code = [*set_vat_country_code_default1][0]
    rates_ref = set_vat_country_code_default1.get(country_code, None).get('standard_rate', None)
    rates = utils.get_tax_rates_for_country(country_code)
    # test standard tax
    tax_func = utils.get_tax_for_rate(rates)
    assert tax_func(Currency(100, 'USD')) == CurrencyWithTax(
        net=Currency(100, 'USD'), gross=Currency(120, 'USD'))

