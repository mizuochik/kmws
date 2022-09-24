from typing import Protocol

from kmws_accounting.application.model import Payment, PaymentEvent


class PaymentEventDao(Protocol):
    async def add(self, payment_event: PaymentEvent) -> None:
        ...

    async def get_by_month(self, year: int, month: int) -> list[PaymentEvent]:
        ...


class PaymentDao(Protocol):
    async def get_by_month(self, year: int, month: int) -> list[Payment]:
        ...
