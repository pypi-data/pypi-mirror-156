"""Module containing DynamoDB Table helpers.

Author: Arbyn Acosta Argabioso
Date Created: May 01, 2022
"""

from __future__ import annotations

from typing import Any
import datetime as dtlib
import re

from pynamodb.attributes import NumberAttribute
from pynamodb.attributes import UnicodeAttribute
from pynamodb.attributes import UTCDateTimeAttribute
from pynamodb.expressions.condition import Condition
from pynamodb.expressions.update import Action
from pynamodb.models import Model
from pynamodb.settings import OperationSettings

from etl.ohlcv.util.datetime_util import get_datetime_now
from etl.ohlcv.util.datetime_util import get_milliseconds


class CustomModel(Model):
    @classmethod
    def fetch(cls, partition_key: Any, sort_key: Any) -> Any:
        item = None
        for item in cls.query(
            hash_key=partition_key,
            range_key_condition=(cls.sort_key == sort_key),
        ):
            pass

        return item


class ETLOHLCV(CustomModel):
    """Exchange Metadata table for keeping track of all our datasets."""

    class Meta:
        table_name = "etl-ohlcv"
        region = "us-east-2"


class ExchangeMetadataPartitionKey(UnicodeAttribute):
    """Exchange Metadata Partition Key Attribute."""

    KEY_PREFIX = "EXCHANGE_METADATA__"

    def serialize(self, value: str):
        value = re.sub(r"\\s+", "", value.lower())

        if not value.startswith(self.KEY_PREFIX):
            value = f"{self.KEY_PREFIX}{value}"

        return super().serialize(value)

    def deserialize(self, value):
        value = super().deserialize(value)
        if value.startswith(self.KEY_PREFIX):
            return value[len(self.KEY_PREFIX):]


class ExchangeMetadata(ETLOHLCV):
    """Exchange Metadata table for keeping track of all our datasets."""

    partition_key = ExchangeMetadataPartitionKey(hash_key=True)
    sort_key = UnicodeAttribute(range_key=True)

    symbol = UnicodeAttribute()
    base = UnicodeAttribute()
    quote = UnicodeAttribute()

    timestamp_oldest = NumberAttribute()
    timestamp_newest = NumberAttribute()
