from datetime import datetime
import uuid

from kmws_accounting.application.model import (
    Payment,
    PaymentList,
    PaymentCreateEvent,
    PaymentRatio,
    EventType,
)


SOMETIME = datetime.now()


class TestPaymentEvent:
    def test_as_text(self) -> None:
        given = PaymentCreateEvent(
            payment_id=uuid.uuid4(),
            created_at=datetime.fromisoformat("2022-01-01T00:00:00"),
            paid_at=datetime.fromisoformat("2022-01-02T00:00:00"),
            place="Tokyo",
            payer="Taro",
            item="Apple",
            amount_yen=100,
        )
        assert given.as_text() == "2022-01-02/Tokyo/Taro/Apple/¥100"


class TestPaymentList:
    def test_summarize_paid(self) -> None:
        payments = PaymentList(
            [
                Payment(
                    [
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Hanako",
                            "Apple",
                            100,
                        )
                    ]
                ),
                Payment(
                    [
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Hanako",
                            "Apple",
                            200,
                        )
                    ]
                ),
                Payment(
                    [
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Taro",
                            "Apple",
                            300,
                        ),
                    ]
                ),
                Payment(
                    [
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Taro",
                            "Apple",
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
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Hanako",
                            "Apple",
                            100,
                        )
                    ]
                ),
                Payment(
                    [
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Hanako",
                            "Apple",
                            200,
                        )
                    ]
                ),
                Payment(
                    [
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Taro",
                            "Apple",
                            300,
                        ),
                    ]
                ),
                Payment(
                    [
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            SOMETIME,
                            "Tokyo",
                            "Taro",
                            "Apple",
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
