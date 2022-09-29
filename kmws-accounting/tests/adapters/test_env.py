from unittest import mock
import os
from kmws_accounting.adapters.env import Config


@mock.patch.dict(
    os.environ,
    {
        "KMWS_UI_ORIGIN": "http://xxx.yyy",
    },
)
def test_config_load():
    c = Config.load()
    assert c == Config(kmws_ui_origin="http://xxx.yyy")
