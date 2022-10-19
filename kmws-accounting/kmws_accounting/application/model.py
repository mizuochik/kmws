from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Sequence
import typing
from uuid import UUID


class EventType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class PaymentEvent:
    payment_id: UUID
    created_at: datetime

    @property
    def event_type(self) -> EventType:
        ...

    def as_text(self) -> str:
        ...


@dataclass
class PaymentCreateEvent(PaymentEvent):
    paid_at: datetime
    place: str
    payer: str
    item: str
    amount_yen: int

    @property
    def event_type(self) -> EventType:
        return EventType.CREATE

    def as_text(self) -> str:
        return f"{self.paid_at.date().isoformat()}/{self.place}/{self.payer}/{self.item}/¥{self.amount_yen}"


@dataclass
class PaymentDeleteEvent(PaymentEvent):
    @property
    def event_type(self) -> EventType:
        return EventType.DELETE

    def as_text(self) -> str:
        return f"[DELETED]"


class Payment:
    def __init__(self, events: Sequence[PaymentEvent]) -> None:
        if events and any(e.payment_id != events[0].payment_id for e in events):
            raise ValueError("must all event ids are same")
        self._events = events

    def is_deleted(self) -> bool:
        if not self._events:
            return True
        return self._get_latest().event_type == EventType.DELETE

    def get_latest(self) -> PaymentCreateEvent:
        assert not self.is_deleted()
        return typing.cast(PaymentCreateEvent, self._get_latest())

    def _get_latest(self) -> PaymentEvent:
        return max(self._events, key=lambda v: v.created_at)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Payment):
            return self._events == o._events
        return False


class PaymentList:
    def __init__(self, payments: list[Payment]) -> None:
        self._payments = payments

    def summarize_paid(self) -> dict[str, int]:
        cnt: Counter[str] = Counter()
        for payment in self._payments:
            p = payment.get_latest()
            if p:
                cnt[p.payer] += p.amount_yen
        return cnt

    def summarize_adjustments(self, ratio: PaymentRatio) -> dict[str, int]:
        paid = self.summarize_paid()
        ratio_total = sum(r for r in ratio.values())
        paid_total = sum(p for p in paid.values())
        adjustments = {}
        for account in ratio.get_payers():
            if ratio_total <= 0:
                due_amount = 0.0
            else:
                due_amount = paid_total * ratio[account] / ratio_total
            adjustments[account] = round(paid[account] - due_amount)
        return adjustments


class PaymentRatio(dict[str, int]):
    def get_payers(self) -> list[str]:
        return list(self.keys())


class PaymentHistory:
    ...
