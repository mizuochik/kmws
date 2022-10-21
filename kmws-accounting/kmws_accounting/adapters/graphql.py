from __future__ import annotations
from datetime import datetime
import uuid
import ariadne
from ariadne import QueryType, MutationType
from ariadne.asgi import GraphQL
from ariadne.types import Extension
from importlib import resources
import jwt
from kmws_accounting.application.use_cases import GetSharing
import kmws_accounting.adapters
from ariadne.asgi.handlers import GraphQLHTTPHandler
from kmws_accounting.application.model import PaymentCreateEvent, PaymentDeleteEvent
from kmws_accounting.application.ports import PaymentDao, PaymentEventDao

_USERNAME_KEY = "username"

with resources.open_text(kmws_accounting.adapters, "schema.graphql") as f:
    type_defs = f.read()

query = QueryType()


@query.field("payments")
async def resolve_payments(_, info, year: int, month: int) -> list[dict]:
    dao: PaymentDao = info.context[PaymentDao]
    payments = [
        payment.get_latest()
        for payment in await dao.read_by_month(year, month)
        if not payment.is_deleted()
    ]
    return [
        {
            "id": str(payment.payment_id),
            "date": payment.paid_at.isoformat(),
            "place": payment.place,
            "payer": payment.payer,
            "item": payment.item,
            "amountYen": payment.amount_yen,
        }
        for payment in sorted(payments, key=lambda p: p.paid_at)
    ]


@query.field("adjustments")
async def resolve_adjustments(_, info, year: int, month: int) -> list[dict]:
    get_sharing: GetSharing = info.context[GetSharing]
    sharing = await get_sharing.run(year, month)
    return [
        {
            "year": year,
            "month": month,
            "paid": [
                {
                    "name": payer,
                    "amount": sharing.paid[payer],
                }
                for payer in sharing.payers
            ],
            "adjustments": [
                {
                    "name": payer,
                    "amount": sharing.adjustments[payer],
                }
                for payer in sharing.payers
            ],
        }
    ]


@query.field("history")
async def resolve_history(_, info) -> list[dict]:
    dao: PaymentEventDao = info.context[PaymentEventDao]
    events = await dao.read_latest()
    return [
        {
            "timestamp": event.created_at.isoformat(),
            "editor": event.editor,
            "action": event.event_type.name,
            "before": None,
            "after": event.as_text(),
        }
        for event in events
    ]


mutation = MutationType()


@mutation.field("createPayment")
async def resolve_createPayment(_, info, input: dict) -> bool:
    dao: PaymentEventDao = info.context[PaymentEventDao]
    await dao.create(
        PaymentCreateEvent(
            payment_id=uuid.uuid4(),
            created_at=datetime.now(),
            editor=info.context[_USERNAME_KEY],
            paid_at=datetime.fromisoformat(input["date"]),
            place=input["place"],
            payer=info.context[_USERNAME_KEY],
            item=input["item"],
            amount_yen=input["amountYen"],
        )
    )
    return True


@mutation.field("deletePayment")
async def resolve_deletePayment(_, info, id: str) -> bool:
    dao: PaymentEventDao = info.context[PaymentEventDao]
    await dao.create(
        PaymentDeleteEvent(
            payment_id=uuid.UUID(id),
            created_at=datetime.now(),
            editor=info.context[_USERNAME_KEY],
        )
    )
    return True


def make_graphql_app(
    payment_dao: PaymentDao, payment_event_dao: PaymentEventDao, get_sharing: GetSharing
) -> GraphQL:
    class Injector(Extension):
        def request_started(self, context) -> None:
            context[PaymentDao] = payment_dao
            context[PaymentEventDao] = payment_event_dao
            context[GetSharing] = get_sharing

    class SetUsername(Extension):
        def request_started(self, context) -> None:
            auth_token = context["request"].headers["authorization"]
            username = jwt.decode(
                auth_token, algorithms=["HS256"], options={"verify_signature": False}
            )["cognito:username"]
            context[_USERNAME_KEY] = username

    schema = ariadne.make_executable_schema(type_defs, query, mutation)
    return GraphQL(
        schema,
        debug=True,
        http_handler=GraphQLHTTPHandler(extensions=[Injector, SetUsername]),
    )
