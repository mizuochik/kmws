from datetime import datetime
import uuid
import pytest
from kmws_accounting.application.model import EventType, PaymentEvent
from kmws_accounting.application.ports import PaymentEventDao, PaymentDao
from kmws_accounting.adapters import dynamodb
import boto3

_TEST_ACCOUNTING_TABLE = "TestKmwsAccounting"


class TestPaymentEventDao:
    @pytest.fixture
    def dao(self) -> PaymentEventDao:
        table = boto3.resource("dynamodb").Table(_TEST_ACCOUNTING_TABLE)
        for item in table.scan()["Items"]:
            table.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
        return dynamodb.PaymentEventDao(_TEST_ACCOUNTING_TABLE)

    async def test_add_get_by_month(self, dao: PaymentEventDao) -> None:
        given = [
            PaymentEvent(
                id=uuid.uuid4(),
                created_at=datetime.now(),
                paid_at=datetime.fromisoformat("2021-12-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                event_type=EventType.ADD,
                amount_yen=10,
            ),
            PaymentEvent(
                id=uuid.uuid4(),
                created_at=datetime.now(),
                paid_at=datetime.fromisoformat("2022-01-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                event_type=EventType.ADD,
                amount_yen=10,
            ),
            PaymentEvent(
                id=uuid.uuid4(),
                created_at=datetime.now(),
                paid_at=datetime.fromisoformat("2022-01-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                event_type=EventType.ADD,
                amount_yen=10,
            ),
            PaymentEvent(
                id=uuid.uuid4(),
                created_at=datetime.now(),
                paid_at=datetime.fromisoformat("2022-02-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                event_type=EventType.ADD,
                amount_yen=10,
            ),
        ]
        for e in given:
            await dao.add(e)
        got = await dao.get_by_month(2022, 1)
        assert got == given[1:3]
