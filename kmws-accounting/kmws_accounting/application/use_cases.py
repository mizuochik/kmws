from __future__ import annotations
from dataclasses import dataclass
from kmws_accounting.application.model import PaymentList, PaymentRatio
from kmws_accounting.application.ports import PaymentDao


class GetSharing:
    @dataclass
    class Output:
        payers: list[str]
        paid: dict[str, int]
        adjustments: dict[str, int]

    def __init__(self, payment_dao: PaymentDao, payment_ratio: PaymentRatio) -> None:
        self._payment_dao = payment_dao
        self._payment_ratio = payment_ratio

    async def run(self, year: int, month: int) -> GetSharing.Output:
        payments = PaymentList(await self._payment_dao.read_by_month(year, month))
        paid = payments.summarize_paid()
        adjustments = payments.summarize_adjustments(self._payment_ratio)
        return GetSharing.Output(
            payers=self._payment_ratio.get_payers(), paid=paid, adjustments=adjustments
        )
