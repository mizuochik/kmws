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
        await dao.add(
            PaymentEvent(
                id="xxx",
                timestamp=datetime.now(),
                place="Rinkan",
                payer="taro",
                item="Apple",
                action=EventType.ADD,
                amount_yen=10,
            )
        )
