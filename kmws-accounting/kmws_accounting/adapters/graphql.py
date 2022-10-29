from __future__ import annotations
import asyncio
from datetime import datetime
import typing
import uuid
import ariadne
from ariadne import QueryType, MutationType
from ariadne.asgi import GraphQL
from ariadne.types import Extension
from importlib import resources
from graphql import GraphQLError
import jwt
from kmws_accounting.application.use_cases import GetSharing
import kmws_accounting.adapters
from ariadne.asgi.handlers import GraphQLHTTPHandler
from kmws_accounting.application.model import (
    PaymentCreateEvent,
    PaymentDeleteEvent,
    ValidationError,
)
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
    event_dao: PaymentEventDao = info.context[PaymentEventDao]
    dao: PaymentDao = info.context[PaymentDao]
    events = await event_dao.read_latest()
    last_events = await asyncio.gather(*(e.get_last_event(dao) for e in events))
    return [
        {
            "timestamp": e.created_at.isoformat(),
            "editor": e.editor,
            "action": e.event_type.name,
            "before": le.as_text() if le else None,
            "after": e.as_text(),
        }
        for e, le in zip(events, last_events)
    ]


mutation = MutationType()


@mutation.field("createPayment")
async def resolve_createPayment(_, info, input: dict) -> bool:
    dao: PaymentEventDao = info.context[PaymentEventDao]
    try:
        datetime.fromisoformat(input["date"])
    except ValueError:
        raise ValidationError({"date": "is not isoformat"})
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


def format_error(error: GraphQLError, debug: bool) -> dict:
    if isinstance(error.original_error, ValidationError):
        ex = error.extensions or {}
        ex["fields"] = error.original_error.fields
        error.extensions = ex
        error.message = ValidationError.__name__
    return typing.cast(dict, error.formatted)


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
        error_formatter=format_error,
    )
