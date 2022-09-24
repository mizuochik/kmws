import asyncio
import datetime
from kmws_accounting.application.model import EventType, Payment, PaymentEvent
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
                    "CreatedAt": payment_event.created_at.isoformat(),
                    "PaidAt": payment_event.paid_at.isoformat(),
                    "EventType": payment_event.event_type.value,
                    "Place": payment_event.place,
                    "Payer": payment_event.payer,
                    "Item": payment_event.item,
                    "AmountYen": payment_event.amount_yen,
                }
            )

        await asyncio.get_event_loop().run_in_executor(None, put)

    async def get_by_month(self, year: int, month: int) -> list[PaymentEvent]:
        if not datetime.MINYEAR <= year < datetime.MAXYEAR:
            raise ValueError("year is out of range")
        if not 1 <= month <= 12:
            raise ValueError("month is out of range")

        def get() -> list[PaymentEvent]:
            next_year = year + (0 if month < 12 else 1)
            next_month = (month + 1) % 12
            got = self._table.query(
                KeyConditionExpression="PK = :pk and PaidAt between :month_start and :month_end",
                IndexName='PK-PaidAt-index',
                ExpressionAttributeValues={
                    ":pk": _EVENT_PK,
                    ":month_start": f"{year}-{month}",
                    ":month_end": f"{next_year}-{next_month}",
                },
            )
            return [self._to_model(item) for item in got["Items"]]

        return await asyncio.get_event_loop().run_in_executor(None, get)

    def _to_model(self, item) -> PaymentEvent:
        return PaymentEvent(
            id=item["SK"],
            created_at=datetime.datetime.fromisoformat(item["CreatedAt"]),
            paid_at=datetime.datetime.fromisoformat(item["PaidAt"]),
            place=item["Place"],
            payer=item["Payer"],
            item=item["Item"],
            event_type=EventType(item["EventType"]),
            amount_yen=item["AmountYen"],
        )


class PaymentDao:
    def get_by_month(self, year: int, month: int) -> list[Payment]:
        ...
