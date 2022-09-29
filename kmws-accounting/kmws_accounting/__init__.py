from .adapters import graphql, dynamodb, env
from starlette.middleware.cors import CORSMiddleware

_payment_event_dao = dynamodb.PaymentEventDao("TestKmwsAccounting")
_payment_dao = dynamodb.PaymentDao(_payment_event_dao)

_config = env.Config.load()

app = CORSMiddleware(
    graphql.make_graphql_app(_payment_dao, _payment_event_dao),
    allow_methods=["GET", "POST"],
    allow_origins=[_config.kmws_ui_origin],
)
