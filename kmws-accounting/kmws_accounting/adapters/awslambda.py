from . import asgi
from mangum import Mangum
from mangum.handlers import ALB, HTTPGateway, APIGateway, LambdaAtEdge


handler = Mangum(asgi.app)
