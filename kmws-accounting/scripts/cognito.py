import boto3, os

cognito_idp = boto3.client("cognito-idp")
cognito_identity = boto3.client("cognito-identity")

auth = cognito_idp.initiate_auth(
    AuthFlow="USER_PASSWORD_AUTH",
    AuthParameters={
        "USERNAME": os.environ["COGNITO_USERNAME"],
        "PASSWORD": os.environ["COGNITO_PASSWORD"],
    },
    ClientId=os.environ["AUTH_USER_POOL_WEB_CLIENT_ID"],
)
id_token = auth["AuthenticationResult"]["IdToken"]

print(id_token)
