from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EventType(Enum):
    ADD = "add"
    UPDATE = "update"


@dataclass
class PaymentEvent:
    id: str
    created_at: datetime
    paid_at: datetime
    place: str
    payer: str
    item: str
    event_type: EventType
    amount_yen: int

    def get_as_text(self) -> str:
        return (
            f"{self.paid_at}/{self.place}/{self.payer}/{self.item}/¥{self.amount_yen}"
        )


class Payment:
    def __init__(self, events: list[PaymentEvent]) -> None:
        if events and any(e.id != events[0].id for e in events):
            raise ValueError("must all event ids are same")
        self._events = events

    def get_latest(self) -> Optional[PaymentEvent]:
        return max(self._events, key=lambda v: v.created_at)


class PaymentList:
    def __init__(self, payments: list[Payment]) -> None:
        self._payments = payments


class PaymentHistory:
    ...
