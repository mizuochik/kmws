from __future__ import annotations
from typing import Protocol
from uuid import UUID
from kmws_accounting.application import model


class PaymentEventDao(Protocol):
    async def create(self, payment_event: model.PaymentEvent) -> None:
        ...

    async def read_by_id(self, payment_id: UUID) -> list[model.PaymentEvent]:
        ...

    async def read_latest(self) -> list[model.PaymentEvent]:
        ...

    async def read_by_month(self, year: int, month: int) -> list[model.PaymentEvent]:
        ...


class PaymentDao(Protocol):
    async def read_by_id(self, payment_id: UUID) -> model.Payment:
        ...

    async def read_by_month(self, year: int, month: int) -> list[model.Payment]:
        ...
