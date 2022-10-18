import asyncio
from datetime import datetime
import time
import uuid
import pytest
from kmws_accounting.application.model import EventType, Payment, PaymentCreateEvent
from kmws_accounting.application.ports import PaymentEventDao, PaymentDao
from kmws_accounting.adapters import dynamodb
import boto3  # type: ignore

_TEST_ACCOUNTING_TABLE = "TestKmwsAccounting"


class TestPaymentEventDao:
    @pytest.fixture
    def dao(self) -> PaymentEventDao:
        table = boto3.resource("dynamodb").Table(_TEST_ACCOUNTING_TABLE)
        for item in table.scan()["Items"]:
            table.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
        return dynamodb.PaymentEventDao(_TEST_ACCOUNTING_TABLE)

    async def test_create_read_by_month(self, dao: PaymentEventDao) -> None:
        given = [
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.uuid4(),
                paid_at=datetime.fromisoformat("2021-12-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.uuid4(),
                paid_at=datetime.fromisoformat("2022-01-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.uuid4(),
                paid_at=datetime.fromisoformat("2022-01-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.uuid4(),
                paid_at=datetime.fromisoformat("2022-02-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
        ]
        for e in given:
            await dao.create(e)
        await asyncio.sleep(0.1)
        got = await dao.read_by_month(2022, 1)
        assert got == given[1:3]

    async def test_read_latest(self, dao: PaymentEventDao) -> None:
        given = [
            PaymentCreateEvent(
                created_at=datetime.fromisoformat("2022-01-01T00:00:00"),
                payment_id=uuid.uuid4(),
                paid_at=datetime.fromisoformat("2023-01-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.fromisoformat("2022-01-01T00:00:01"),
                payment_id=uuid.uuid4(),
                paid_at=datetime.fromisoformat("2023-01-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
        ]
        for e in given:
            await dao.create(e)
        await asyncio.sleep(0.1)
        got = await dao.read_latest()
        assert got == list(reversed(given))


class TestPaymentDao:
    @pytest.fixture
    def dao(self, event_dao: PaymentEventDao) -> PaymentDao:
        return dynamodb.PaymentDao(event_dao)

    @pytest.fixture
    def event_dao(self) -> PaymentEventDao:
        table = boto3.resource("dynamodb").Table(_TEST_ACCOUNTING_TABLE)
        for item in table.scan()["Items"]:
            table.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
        return dynamodb.PaymentEventDao(_TEST_ACCOUNTING_TABLE)

    async def test_read_by_month(
        self, dao: PaymentDao, event_dao: PaymentEventDao
    ) -> None:
        id = uuid.uuid4()
        given = [
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=id,
                paid_at=datetime.fromisoformat("2021-12-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=id,
                paid_at=datetime.fromisoformat("2022-01-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=id,
                paid_at=datetime.fromisoformat("2022-01-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=id,
                paid_at=datetime.fromisoformat("2022-02-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
        ]
        for e in given:
            await event_dao.create(e)
        got = await dao.read_by_month(2022, 1)
        assert got == [Payment(given[1:3])]
