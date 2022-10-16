from unittest import mock
import os
from kmws_accounting.adapters.env import Config
from kmws_accounting.application.model import PaymentRatio


@mock.patch.dict(
    os.environ,
    {
        "PAYMENT_RATIO": "taro:60,hanako:40",
        "ACCOUNTING_TABLE": "TestKmwsAccounting",
    },
)
def test_config_load():
    c = Config.load()
    assert c == Config(
        payment_ratio=PaymentRatio({"taro": 60, "hanako": 40}),
        accounting_table="TestKmwsAccounting",
    )
