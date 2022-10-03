from __future__ import annotations
from dataclasses import dataclass
import os
from kmws_accounting.application.model import PaymentRatio

TEST = "test"


@dataclass
class Config:
    kmws_ui_origin: str
    payment_ratio: PaymentRatio

    @classmethod
    def load(cls) -> Config:
        ratio = PaymentRatio()
        for sec in os.environ["PAYMENT_RATIO"].split(","):
            k, v = sec.split(":")
            ratio[k] = int(v)

        return Config(
            kmws_ui_origin=os.environ["KMWS_UI_ORIGIN"],
            payment_ratio=PaymentRatio(ratio),
        )
