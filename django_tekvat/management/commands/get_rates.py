from django.core.management.base import BaseCommand

from ...utils import (
    save_vat_rate_by_country,
    save_vat_rate_types,
    fetch_vat_rates,
    fetch_rate_types
)


class Command(BaseCommand):
    help = 'Gets current vat rate types and vat rates in EU and saves to database'

    def handle(self, *args, **options):
        json_response_rates = fetch_vat_rates()
        save_vat_rate_by_country(json_response_rates)

        json_response_types = fetch_rate_types()
        save_vat_rate_types(json_response_types)