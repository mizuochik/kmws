from typing import Protocol

from kmws_accounting.application.model import Payment, PaymentEvent


class PaymentEventDao(Protocol):
    def add(self, payment_event: PaymentEvent) -> None:
        ...

    def get_by_month(self, year: int, month: int) -> list[PaymentEvent]:
        ...


class PaymentDao(Protocol):
    def get_by_month(self, year: int, month: int) -> list[Payment]:
        ...
