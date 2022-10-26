from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Sequence
import typing
from uuid import UUID
from .ports import PaymentDao


class EventType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ValidationError(ValueError):
    def __init__(self, fields: dict[str, str]) -> None:
        self.fields = fields


@dataclass
class PaymentEvent:
    payment_id: UUID
    created_at: datetime
    editor: str

    def __post_init__(self) -> None:
        f = {}
        if not self.editor:
            f["editor"] = "is emtpy"
        if f:
            raise ValidationError(f)

    @property
    def event_type(self) -> EventType:
        ...

    def as_text(self) -> str:
        ...

    async def get_last_event(self, dao: PaymentDao) -> Optional[PaymentEvent]:
        if self.event_type == EventType.CREATE:
            return None
        p = await dao.read_by_id(self.payment_id)
        return p.get_last_event(self.created_at)


@dataclass
class PaymentCreateEvent(PaymentEvent):
    paid_at: datetime
    place: str
    payer: str
    item: str
    amount_yen: int

    def __post_init__(self) -> None:
        super().__post_init__()
        f = {}
        if not self.place:
            f["place"] = "is empty"
        if not self.payer:
            f["payer"] = "is empty"
        if not self.item:
            f["item"] = "is empty"
        if not self.amount_yen:
            f["amount_yen"] = "is empty"
        if f:
            raise ValidationError(f)

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
        self._events = sorted(events, key=lambda e: e.created_at, reverse=True)

    def is_deleted(self) -> bool:
        if not self._events:
            return True
        return self._get_latest().event_type == EventType.DELETE

    def get_latest(self) -> PaymentCreateEvent:
        assert not self.is_deleted()
        return typing.cast(PaymentCreateEvent, self._get_latest())

    def get_last_event(self, dt: datetime) -> PaymentEvent:
        idx = [e.created_at for e in self._events].index(dt)
        return self._events[idx + 1]

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
            if payment.is_deleted():
                continue
            p = payment.get_latest()
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
