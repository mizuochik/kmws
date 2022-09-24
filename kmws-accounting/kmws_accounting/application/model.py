from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class EventType(Enum):
    CREATE = "create"
    UPDATE = "update"


@dataclass
class PaymentEvent:
    payment_id: UUID
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
        if events and any(e.payment_id != events[0].payment_id for e in events):
            raise ValueError("must all event ids are same")
        self._events = events

    def get_latest(self) -> PaymentEvent:
        return max(self._events, key=lambda v: v.created_at)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Payment):
            return self._events == o._events
        return False


class PaymentList:
    def __init__(self, payments: list[Payment]) -> None:
        self._payments = payments


class PaymentHistory:
    ...