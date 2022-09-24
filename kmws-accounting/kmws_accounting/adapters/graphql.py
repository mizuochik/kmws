from __future__ import annotations
from ast import arg
from dataclasses import dataclass
from typing import Optional
import ariadne
from ariadne import QueryType
from ariadne.asgi import GraphQL
from ariadne.types import Extension, ContextValue
from importlib import resources
import kmws_accounting.adapters
from ariadne.asgi.handlers import GraphQLHTTPHandler
from kmws_accounting.application.ports import PaymentDao, PaymentEventDao

with resources.open_text(kmws_accounting.adapters, "schema.graphql") as f:
    type_defs = f.read()

query = QueryType()


@dataclass
class PageInfo:
    hasNextPage: bool
    endCursor: str


@dataclass
class PaymentConnection:
    pageInfo: PageInfo
    edges: Optional[list[PaymentEdge]]


@dataclass
class PaymentEdge:
    cursor: str
    node: Optional[Payment]


@dataclass
class Payment:
    id: str
    date: str
    place: str
    payer: str
    item: str
    amount: int


@query.field("payments")
async def resolve_payments(_, info, **keywords) -> PaymentConnection:
    return PaymentConnection(
        pageInfo=PageInfo(hasNextPage=False, endCursor=""),
        edges=[
            PaymentEdge(
                cursor="",
                node=Payment(
                    id="",
                    date="2022",
                    place="foo",
                    payer="foo",
                    item="foo",
                    amount=10,
                ),
            )
        ],
    )


class _InejctComponents(Extension):
    def __init__(self):
        self._payment_dao = ...
        self._payment_event_dao = ...

    def request_started(self, context) -> None:
        context[PaymentDao] = self._payment_dao
        context[PaymentEventDao] = self._payment_event_dao


schema = ariadne.make_executable_schema(type_defs, query)
app = GraphQL(
    schema,
    debug=True,
    http_handler=GraphQLHTTPHandler(extensions=[_InejctComponents]),
)
