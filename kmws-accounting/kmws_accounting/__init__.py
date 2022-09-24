from .adapters import graphql, dynamodb

_payment_event_dao = dynamodb.PaymentEventDao("TestKmwsAccounting")
_payment_dao = dynamodb.PaymentDao(_payment_event_dao)

app = graphql.make_graphql_app(_payment_dao, _payment_event_dao)
