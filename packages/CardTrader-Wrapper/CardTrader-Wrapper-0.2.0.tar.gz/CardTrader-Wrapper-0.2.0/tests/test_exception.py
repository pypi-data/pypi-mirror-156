import pytest

from cardtrader.exceptions import ServiceError
from cardtrader.service import CardTrader
from cardtrader.sqlite_cache import SQLiteCache


def test_unauthorized():
    session = CardTrader("Invalid", cache=SQLiteCache("tests/cache.sqlite", expiry=None))
    with pytest.raises(ServiceError):
        session.info()
