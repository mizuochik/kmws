from datetime import datetime
from unittest.mock import Mock
import uuid
from kmws_accounting.application.use_cases import GetSharing
import pytest
from kmws_accounting.application import use_cases
from kmws_accounting.application.ports import PaymentDao
from kmws_accounting.application.model import (
    PaymentRatio,
    Payment,
    PaymentEvent,
    EventType,
)


class TestGetSharing:
    @pytest.fixture
    def payment_dao_mock(self) -> Mock:
        return Mock(PaymentDao)

    async def test_run(self, payment_dao_mock: Mock) -> None:
        payment_dao_mock.read_by_month.return_value = [
            Payment(
                [
                    PaymentEvent(
                        payment_id=uuid.uuid4(),
                        created_at=datetime.now(),
                        paid_at=datetime.now(),
                        place="",
                        payer="Taro",
                        item="",
                        event_type=EventType.CREATE,
                        amount_yen=700,
                    ),
                ]
            ),
            Payment(
                [
                    PaymentEvent(
                        payment_id=uuid.uuid4(),
                        created_at=datetime.now(),
                        paid_at=datetime.now(),
                        place="",
                        payer="Hanako",
                        item="",
                        event_type=EventType.CREATE,
                        amount_yen=300,
                    ),
                ],
            ),
        ]
        payment_ratio = PaymentRatio({"Taro": 60, "Hanako": 40})

        use_case = use_cases.GetSharing(payment_dao_mock, payment_ratio)

        assert (await use_case.run(2021, 1)) == GetSharing.Output(
            payers=["Taro", "Hanako"],
            paid={"Taro": 700, "Hanako": 300},
            adjustments={"Taro": 100, "Hanako": -100},
        )
        payment_dao_mock.read_by_month.assert_called_with(2021, 1)
