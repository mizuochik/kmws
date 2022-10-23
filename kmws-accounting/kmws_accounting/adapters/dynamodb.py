import asyncio
from collections import defaultdict
import datetime
from typing import Any
from kmws_accounting.application.model import (
    Payment,
    PaymentCreateEvent,
    PaymentEvent,
    PaymentDeleteEvent,
    EventType,
)
from kmws_accounting.application import ports
import boto3  # type: ignore
from uuid import UUID

_EVENT_PK = "PaymentEvent"


class PaymentEventDao:
    def __init__(self, table_name: str) -> None:
        self._table = boto3.resource("dynamodb").Table(table_name)

    async def create(self, payment_event: PaymentEvent) -> None:
        def create() -> None:
            item: dict[str, Any] = dict(
                PK=_EVENT_PK,
                SK=payment_event.created_at.isoformat(),
                PaymentId=str(payment_event.payment_id),
                EventType=payment_event.event_type.value,
                Editor=payment_event.editor,
            )
            if isinstance(payment_event, PaymentCreateEvent):
                item = dict(
                    PaidAt=payment_event.paid_at.isoformat(),
                    Place=payment_event.place,
                    Payer=payment_event.payer,
                    Item=payment_event.item,
                    AmountYen=payment_event.amount_yen,
                    **item,
                )
            self._table.put_item(Item=item)

        await asyncio.get_event_loop().run_in_executor(None, create)

    async def read_latest(self) -> list[PaymentEvent]:
        def get() -> list[PaymentEvent]:
            got = self._table.query(
                KeyConditionExpression="PK = :pk",
                ExpressionAttributeValues={
                    ":pk": _EVENT_PK,
                },
                ScanIndexForward=False,
                Limit=100,
            )
            return [self._to_model(item) for item in got["Items"]]

        return await asyncio.get_event_loop().run_in_executor(None, get)

    async def read_by_month(self, year: int, month: int) -> list[PaymentEvent]:
        if not datetime.MINYEAR <= year < datetime.MAXYEAR:
            raise ValueError("year is out of range")
        if not 1 <= month <= 12:
            raise ValueError("month is out of range")

        def get() -> list[PaymentEvent]:
            next_year = year + (0 if month < 12 else 1)
            next_month = (month + 1) % 13
            payment_ids = {
                item["PaymentId"]
                for item in self._table.query(
                    KeyConditionExpression="PK = :pk and PaidAt between :month_start and :month_end",
                    IndexName="PK-PaidAt-index",
                    ExpressionAttributeValues={
                        ":pk": _EVENT_PK,
                        ":month_start": f"{year}-{month:02}",
                        ":month_end": f"{next_year}-{next_month:02}",
                    },
                )["Items"]
            }
            items = (
                item
                for payment_id in payment_ids
                for item in self._table.query(
                    KeyConditionExpression="PK = :pk and PaymentId = :payment_id",
                    IndexName="PK-PaymentId-index",
                    ExpressionAttributeValues={
                        ":pk": _EVENT_PK,
                        ":payment_id": payment_id,
                    },
                )["Items"]
            )
            return sorted(
                (self._to_model(item) for item in items), key=lambda e: e.created_at
            )

        return await asyncio.get_event_loop().run_in_executor(None, get)

    def _to_model(self, item) -> PaymentEvent:
        kv: dict[str, Any] = dict(
            created_at=datetime.datetime.fromisoformat(item["SK"]),
            payment_id=UUID(item["PaymentId"]),
            editor=item["Editor"],
        )
        event_type = EventType(item["EventType"])
        if event_type == EventType.CREATE:
            return PaymentCreateEvent(
                paid_at=datetime.datetime.fromisoformat(item["PaidAt"]),
                place=item["Place"],
                payer=item["Payer"],
                item=item["Item"],
                amount_yen=item["AmountYen"],
                **kv,
            )
        elif event_type == EventType.DELETE:
            return PaymentDeleteEvent(**kv)
        else:
            raise ValueError("must not happen")


class PaymentDao:
    def __init__(self, payment_event_dao: ports.PaymentEventDao) -> None:
        self._payment_event_dao = payment_event_dao

    async def read_by_month(self, year: int, month: int) -> list[Payment]:
        events = await self._payment_event_dao.read_by_month(year, month)
        payments = defaultdict(lambda: [])
        for e in events:
            payments[e.payment_id].append(e)
        return [Payment(payments[payment_id]) for payment_id in payments.keys()]
