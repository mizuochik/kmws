from datetime import datetime
import uuid

from kmws_accounting.application.model import (
    Payment,
    PaymentList,
    PaymentEvent,
    PaymentRatio,
    EventType,
)


SOMETIME = datetime.now()


class TestPaymentEvent:
    def test_as_text(self) -> None:
        given = PaymentEvent(
            payment_id=uuid.uuid4(),
            created_at=datetime.fromisoformat("2022-01-01T00:00:00"),
            paid_at=datetime.fromisoformat("2022-01-02T00:00:00"),
            place="Tokyo",
            payer="Taro",
            item="Apple",
            event_type=EventType.CREATE,
            amount_yen=100,
        )
        assert given.as_text() == "2022-01-02/Tokyo/Taro/Apple/¥100"


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

    def test_summarize_adjustments(self) -> None:
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
        assert payments.summarize_adjustments(
            PaymentRatio({"Taro": 60, "Hanako": 40})
        ) == {
            "Hanako": -100,
            "Taro": 100,
        }
