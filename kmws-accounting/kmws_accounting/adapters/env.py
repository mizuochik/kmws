from __future__ import annotations
from dataclasses import dataclass
import os

TEST = "test"


@dataclass
class Config:
    kmws_ui_origin: str

    @classmethod
    def load(cls) -> Config:
        return Config(kmws_ui_origin=os.environ["KMWS_UI_ORIGIN"])
