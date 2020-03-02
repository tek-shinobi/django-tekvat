from __future__ import annotations
from django.conf import settings
import requests
from decimal import Decimal
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from typing import Dict, Any, List, Union, Callable
from tekmoney.flat_tax import flat_tax

Dint = Union[Decimal, int]

from .models import (
    TekvatVat,
    TekvatRateType,
    DEFAULT_TEKVAT_RATE_TYPES_INSTANCE_ID
)

JsonDict = Dict[str, Any]


ACCESS_KEY = getattr(settings, 'TEKVAT_APILAYER_ACCESS_KEY', None)
if ACCESS_KEY is None:
    raise ImproperlyConfigured(
        'API access key not found.'
    )
USE_HTTPS = getattr(settings, 'TEKVAT_APILAYER_USE_HTTPS', False)
PROTOCOL = 'https://' if USE_HTTPS else 'http://'
BASE_URL = PROTOCOL + getattr(settings, 'TEKVAT_APILAYER_BASE_URL', 'apilayer.net/api/')
RATE_LIST_ENDPOINT = getattr(settings, 'TEKVAT_APILAYER_RATE_LIST_ENDPOINT', 'rate_list')
RATE_TYPES_ENDPOINT = getattr(settings, 'TEKVAT_APILAYER_RATE_TYPES_ENDPOINT', 'types')

RATE_LIST_API = BASE_URL + RATE_LIST_ENDPOINT
RATE_TYPES_API = BASE_URL + RATE_TYPES_ENDPOINT


def check_api_response(response: Dict) -> bool:
    success = response.get('success', None)
    valid = response.get('valid', None)
    if success is None and valid is None:
        raise ImproperlyConfigured(
            'returned response is not valid'
        )
    if success is None:
        if valid:
            return True
    if valid is None:
        if success:
            return True
    return False


def validate_data(response: JsonDict) -> None:
    if not check_api_response(response):
        msg = response['error']['info']
        raise ImproperlyConfigured(msg)


def fetch_from_api(url: str) -> JsonDict:
    response = requests.get(url, params={'access_key': ACCESS_KEY})
    return response.json()


def fetch_rate_types() -> JsonDict:
    return fetch_from_api(RATE_TYPES_API)


def fetch_vat_rates() -> JsonDict:
    return fetch_from_api(RATE_LIST_API)

def save_vat_rate_types(json_response: JsonDict) -> None:
    validate_data(json_response)
    TekvatRateType.objects.update_or_create(
        id=DEFAULT_TEKVAT_RATE_TYPES_INSTANCE_ID,
        defaults={'data': json_response['types']}
    )

def save_vat_rate_by_country(json_response: JsonDict) -> None:
    validate_data(json_response)
    json_data = json_response['rates']

    for country_code, data in json_data.items():
        TekvatVat.objects.update_or_create(
            country_code=country_code,
            defaults={'data': data}
        )


def get_tax_rates_for_country(country_code: str) -> Dict[str, Any]:
    tax_rates = {}
    try:
        country_vat = TekvatVat.objects.get(country_code=country_code)
        tax_rates = country_vat.data
    except ObjectDoesNotExist:
        tax_rates = {}
    return tax_rates


def get_tax_rate_types() -> List[str]:
    rate_types = TekvatRateType.objects.default_instance()
    return rate_types.data if rate_types else []


def get_country_codes() -> List[str]:
    qs = TekvatVat.objects.values_list('country_code', flat=True)
    return list(set(qs)) if qs.exists() else []


def get_standard_tax_rate_for_country(country_code: str) -> Dint:
    rates_dict = get_tax_rates_for_country(country_code)
    return rates_dict.get('standard_rate', None) if rates_dict else 0


def get_reduced_tax_rates_for_country(country_code: str) -> Dict[str, Dint]:
    rates_dict = get_tax_rates_for_country(country_code)
    reduced_rates: Dict[str, Dint] = rates_dict.get('reduced_rates', None)
    return reduced_rates if reduced_rates else {}


def get_tax_rate(tax_rates: Dict[str, Any], rate_name: str = None) -> Dint:
    if tax_rates is None:
        return 0

    try:
        reduced_rates = tax_rates['reduced_rates']
        standard_rate = tax_rates['standard_rate']
    except KeyError:
        return 0

    rate = standard_rate
    if rate_name and reduced_rates and rate_name in reduced_rates:
        rate = reduced_rates[rate_name]

    return rate


def get_tax_for_rate(tax_rates, rate_name: str = None):
    rate = get_tax_rate(tax_rates, rate_name)
    if rate is None:
        return None

    final_tax_rate = Decimal(rate / 100)

    def tax(base, keep_gross: bool=False):
        return flat_tax(base, final_tax_rate, keep_gross=keep_gross)

    return tax