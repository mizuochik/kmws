from datetime import datetime
import pytest
from kmws_accounting.application.model import EventType, PaymentEvent
from kmws_accounting.application.ports import PaymentEventDao, PaymentDao
from kmws_accounting.adapters import dynamodb


class TestPaymentEventDao:
    @pytest.fixture
    def dao(self) -> PaymentEventDao:
        return dynamodb.PaymentEventDao("TestKmwsAccounting")

    async def test_add_get_by_month(self, dao: PaymentEventDao) -> None:
        given = [
            PaymentEvent(
                id="xxx",
                created_at=datetime.now(),
                paid_at=datetime.now(),
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
        assert got == given
