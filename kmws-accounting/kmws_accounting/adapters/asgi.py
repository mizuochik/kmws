from . import graphql, dynamodb, env
from starlette.middleware.cors import CORSMiddleware
from ..application.use_cases import GetSharing

_config = env.Config.load()


_payment_event_dao = dynamodb.PaymentEventDao(_config.accounting_table)
_payment_dao = dynamodb.PaymentDao(_payment_event_dao)

_get_sharing = GetSharing(_payment_dao, _config.payment_ratio)


app = CORSMiddleware(
    graphql.make_graphql_app(_payment_dao, _payment_event_dao, _get_sharing),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)
