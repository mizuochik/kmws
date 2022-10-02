from datetime import datetime
import uuid

from kmws_accounting.application.model import (
    Payment,
    PaymentList,
    PaymentEvent,
    ShareRatio,
    EventType,
)


SOMETIME = datetime.now()


class TestPaymentList:
    def test_summarize_paid(self) -> None:
        payments = PaymentList(
            [
                Payment(
                    [
                        PaymentEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Hanako",
                            "Apple",
                            EventType.CREATE,
                            100,
                        )
                    ]
                ),
                Payment(
                    [
                        PaymentEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Hanako",
                            "Apple",
                            EventType.CREATE,
                            200,
                        )
                    ]
                ),
                Payment(
                    [
                        PaymentEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Taro",
                            "Apple",
                            EventType.CREATE,
                            300,
                        ),
                    ]
                ),
                Payment(
                    [
                        PaymentEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Taro",
                            "Apple",
                            EventType.CREATE,
                            400,
                        ),
                    ]
                ),
            ]
        )
        assert payments.summarize_paid() == {
            "Hanako": 300,
            "Taro": 700,
        }
