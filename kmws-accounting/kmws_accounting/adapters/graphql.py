from __future__ import annotations
from datetime import datetime
import uuid
import ariadne
from ariadne import QueryType, MutationType
from ariadne.asgi import GraphQL
from ariadne.types import Extension
from importlib import resources

from kmws_accounting.application.use_cases import GetSharing
import kmws_accounting.adapters
from ariadne.asgi.handlers import GraphQLHTTPHandler
from kmws_accounting.application.model import PaymentEvent, EventType
from kmws_accounting.application.ports import PaymentDao, PaymentEventDao

with resources.open_text(kmws_accounting.adapters, "schema.graphql") as f:
    type_defs = f.read()

query = QueryType()


@query.field("payments")
async def resolve_payments(_, info, year: int, month: int) -> list[dict]:
    dao: PaymentDao = info.context[PaymentDao]
    payments = [
        payment.get_latest() for payment in await dao.read_by_month(year, month)
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
            "editor": event.payer,
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
        PaymentEvent(
            payment_id=uuid.uuid4(),
            created_at=datetime.now(),
            paid_at=datetime.fromisoformat(input["date"]),
            place=input["place"],
            payer=input["payer"],
            item=input["item"],
            event_type=EventType.CREATE,
            amount_yen=input["amountYen"],
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

    schema = ariadne.make_executable_schema(type_defs, query, mutation)
    return GraphQL(
        schema,
        debug=True,
        http_handler=GraphQLHTTPHandler(extensions=[Injector]),
    )
