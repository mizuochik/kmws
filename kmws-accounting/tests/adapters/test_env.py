from unittest import mock
import os
from kmws_accounting.adapters.env import Config
from kmws_accounting.application.model import PaymentRatio


@mock.patch.dict(
    os.environ,
    {
        "KMWS_UI_ORIGIN": "http://xxx.yyy",
        "PAYMENT_RATIO": "taro:60,hanako:40",
    },
)
def test_config_load():
    c = Config.load()
    assert c == Config(
        kmws_ui_origin="http://xxx.yyy",
        payment_ratio=PaymentRatio({"taro": 60, "hanako": 40}),
    )
