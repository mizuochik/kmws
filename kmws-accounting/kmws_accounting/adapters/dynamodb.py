import asyncio
from kmws_accounting.application.model import Payment, PaymentEvent
import boto3  # type: ignore

_EVENT_PK = "PaymentEvent"


class PaymentEventDao:
    def __init__(self, table_name: str) -> None:
        self._table = boto3.resource("dynamodb").Table(table_name)

    async def add(self, payment_event: PaymentEvent) -> None:
        def put() -> None:
            self._table.put_item(
                Item={
                    "PK": _EVENT_PK,
                    "SK": payment_event.id,
                    "Timestamp": payment_event.timestamp.isoformat(),
                    "Action": payment_event.action.value,
                    "Place": payment_event.place,
                    "Payer": payment_event.payer,
                    "Item": payment_event.item,
                    "AmountYen": payment_event.amount_yen,
                }
            )

        await asyncio.get_event_loop().run_in_executor(None, put)

    async def get_by_month(self, year: int, month: int) -> list[PaymentEvent]:
        ...


class PaymentDao:
    def get_by_month(self, year: int, month: int) -> list[Payment]:
        ...
