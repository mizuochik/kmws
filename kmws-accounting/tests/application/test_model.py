from datetime import datetime, timedelta
import typing
import uuid
import pytest
from kmws_accounting.application.model import PaymentEvent
from kmws_accounting.application.model import (
    Payment,
    PaymentList,
    PaymentCreateEvent,
    PaymentDeleteEvent,
    PaymentRatio,
    ValidationError,
)


SOMETIME = datetime.now()


class TestPaymentEvent:
    def test_as_text(self) -> None:
        given = PaymentCreateEvent(
            payment_id=uuid.uuid4(),
            created_at=datetime.fromisoformat("2022-01-01T00:00:00"),
            editor="editor",
            paid_at=datetime.fromisoformat("2022-01-02T00:00:00"),
            place="Tokyo",
            payer="Taro",
            item="Apple",
            amount_yen=100,
        )
        assert given.as_text() == "2022-01-02/Tokyo/Taro/Apple/¥100"


class TestPaymentCreateEvent:
    def test_init(self) -> None:
        with pytest.raises(ValidationError) as e:
            PaymentCreateEvent(
                payment_id=uuid.uuid4(),
                created_at=datetime.now(),
                editor="",
                paid_at=datetime.now(),
                place="",
                payer="",
                item="",
                amount_yen=0,
            )
        actual = typing.cast(ValidationError, e.value)
        assert actual.fields == {
            "editor": "is empty",
            "place": "is empty",
            "payer": "is empty",
            "item": "is empty",
            "amount_yen": "is empty",
        }


payment_id = uuid.uuid4()


class TestPayment:
    def test_get_last_event(self) -> None:
        payment_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        created = PaymentCreateEvent(
            payment_id=payment_id,
            created_at=datetime.fromisoformat("2022-01-01T00:00:00"),
            editor="editor",
            paid_at=SOMETIME,
            place="Tokyo",
            payer="Hanako",
            item="Apple",
            amount_yen=100,
        )
        deleted = PaymentDeleteEvent(
            payment_id=payment_id,
            created_at=datetime.fromisoformat("2022-01-02T00:00:00"),
            editor="editor",
        )
        p = Payment(
            [deleted, created],
        )
        assert p.get_last_event(deleted.created_at) == created

    @pytest.mark.parametrize(
        "input,expected",
        [
            ([], True),
            (
                [
                    PaymentCreateEvent(
                        payment_id=payment_id,
                        created_at=SOMETIME - timedelta(days=1),
                        editor="editor",
                        paid_at=SOMETIME,
                        place="Tokyo",
                        payer="Hanako",
                        item="Apple",
                        amount_yen=100,
                    ),
                ],
                False,
            ),
            (
                [
                    PaymentCreateEvent(
                        payment_id=payment_id,
                        created_at=SOMETIME - timedelta(days=1),
                        editor="editor",
                        paid_at=SOMETIME,
                        place="Tokyo",
                        payer="Hanako",
                        item="Apple",
                        amount_yen=100,
                    ),
                    PaymentDeleteEvent(
                        payment_id=payment_id, created_at=SOMETIME, editor="editor"
                    ),
                ],
                True,
            ),
        ],
    )
    def test_is_deleted(self, input: list[PaymentEvent], expected: bool) -> None:
        assert Payment(input).is_deleted() is expected


class TestPaymentList:
    def test_summarize_paid(self) -> None:
        payments = PaymentList(
            [
                Payment(
                    [
                        PaymentCreateEvent(
                            uuid.uuid4(),
                            SOMETIME,
                            "editor",
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
                            "editor",
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
                            "editor",
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
                            "editor",
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
                            "editor",
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
                            "editor",
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
                            "editor",
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
                            "editor",
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
