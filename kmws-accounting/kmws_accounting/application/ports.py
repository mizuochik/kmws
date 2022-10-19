from typing import Protocol

from kmws_accounting.application.model import Payment, PaymentCreateEvent, PaymentEvent


class PaymentEventDao(Protocol):
    async def create(self, payment_event: PaymentCreateEvent) -> None:
        ...

    async def read_latest(self) -> list[PaymentCreateEvent]:
        ...

    async def read_by_month(self, year: int, month: int) -> list[PaymentEvent]:
        ...


class PaymentDao(Protocol):
    async def read_by_month(self, year: int, month: int) -> list[Payment]:
        ...
