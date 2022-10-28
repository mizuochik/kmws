import asyncio
from datetime import datetime
from pprint import pp
import time
import uuid
import pytest
from kmws_accounting.application.model import (
    Payment,
    PaymentCreateEvent,
    PaymentDeleteEvent,
)
from kmws_accounting.application.ports import PaymentEventDao, PaymentDao
from kmws_accounting.adapters import dynamodb
import boto3  # type: ignore

_TEST_ACCOUNTING_TABLE = "TestKmwsAccounting"
_RETRY_COUNT = 3


class TestPaymentEventDao:
    @pytest.fixture
    def dao(self) -> PaymentEventDao:
        table = boto3.resource("dynamodb").Table(_TEST_ACCOUNTING_TABLE)
        for item in table.scan()["Items"]:
            table.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
        time.sleep(0.1)
        return dynamodb.PaymentEventDao(_TEST_ACCOUNTING_TABLE)

    async def test_read_by_id(self, dao: PaymentEventDao) -> None:
        given = [
            PaymentCreateEvent(
                created_at=datetime.fromisoformat("2022-01-01T00:00:00"),
                payment_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                editor="editor",
                paid_at=datetime.fromisoformat("2021-12-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentDeleteEvent(
                created_at=datetime.fromisoformat("2022-01-02T00:00:00"),
                payment_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                editor="editor",
            ),
        ]
        for e in given:
            await dao.create(e)
        await asyncio.sleep(0.1)
        actual = await dao.read_by_id(uuid.UUID("00000000-0000-0000-0000-000000000000"))
        assert actual == sorted(given, key=lambda e: e.created_at, reverse=True)

    async def test_create_read_by_month(self, dao: PaymentEventDao) -> None:
        given = [
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.uuid4(),
                editor="editor",
                paid_at=datetime.fromisoformat("2021-12-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.uuid4(),
                editor="editor",
                paid_at=datetime.fromisoformat("2022-01-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.uuid4(),
                editor="editor",
                paid_at=datetime.fromisoformat("2022-01-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.uuid4(),
                editor="editor",
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
                editor="editor",
                paid_at=datetime.fromisoformat("2023-01-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.fromisoformat("2022-01-01T00:00:01"),
                payment_id=uuid.uuid4(),
                editor="editor",
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

    async def test_read_by_id(
        self, dao: PaymentDao, event_dao: PaymentEventDao
    ) -> None:
        created_at = datetime.fromisoformat("2022-01-01T00:00:00")
        deleted_at = datetime.fromisoformat("2022-01-02T00:00:00")
        id = uuid.UUID("70b7369a-c0bf-4c5f-a07a-45045ea2f336")
        given = [
            PaymentCreateEvent(
                created_at=created_at,
                payment_id=id,
                editor="editor",
                paid_at=datetime.fromisoformat("2021-12-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentDeleteEvent(
                created_at=deleted_at,
                payment_id=id,
                editor="editor",
            ),
        ]
        for e in given:
            await event_dao.create(e)
        cnt = 0
        while True:
            actual = await dao.read_by_id(id)
            try:
                assert actual == Payment(
                    sorted(given, key=lambda e: e.created_at, reverse=True)
                )
            except AssertionError as e:
                if cnt >= 3:
                    raise e
                await asyncio.sleep(cnt**2)
                cnt += 1
            else:
                break

    async def test_read_by_month(
        self, dao: PaymentDao, event_dao: PaymentEventDao
    ) -> None:
        given = [
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                editor="editor",
                paid_at=datetime.fromisoformat("2021-12-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                editor="editor",
                paid_at=datetime.fromisoformat("2022-01-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
                editor="editor",
                paid_at=datetime.fromisoformat("2022-01-31T23:59:59"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
            PaymentCreateEvent(
                created_at=datetime.now(),
                payment_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
                editor="editor",
                paid_at=datetime.fromisoformat("2022-02-01T00:00:00"),
                place="Rinkan",
                payer="taro",
                item="Apple",
                amount_yen=10,
            ),
        ]
        for e in given:
            await event_dao.create(e)
        cnt = 0
        while True:
            try:
                got = await dao.read_by_month(2022, 1)
                assert got == [
                    Payment([given[1], given[0]]),
                    Payment([given[3], given[2]]),
                ]
            except AssertionError as e:
                if cnt >= _RETRY_COUNT:
                    raise e
                await asyncio.sleep(2**cnt)
                cnt += 1
            else:
                break
