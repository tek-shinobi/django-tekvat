from django.db import models
from jsonfield import JSONField
from typing import Any

DEFAULT_TEKVAT_RATE_TYPES_INSTANCE_ID = 1


class TekvatVat(models.Model):
    country_code = models.CharField(max_length=3, db_index=True)
    data = JSONField()


class TekvatRateTypeQuerySet(models.QuerySet):
    def default_instance(self):
        return self.filter(id=DEFAULT_TEKVAT_RATE_TYPES_INSTANCE_ID).first()


class TekvatRateType(models.Model):
    data = JSONField()

    objects = TekvatRateTypeQuerySet.as_manager()

