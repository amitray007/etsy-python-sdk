from os import environ as os_environ


class BaseEnvironment(object):
    authorization_url = "https://www.etsy.com/oauth/connect"
    base_token_url = "https://api.etsy.com"
    base_request_url = "https://openapi.etsy.com"


class Production(BaseEnvironment):
    token_url = f"{BaseEnvironment.base_token_url}/v3/public/oauth/token"
    request_url = f"{BaseEnvironment.base_request_url}/v3/application"


ENVIRONMENTS = dict(PROD=Production)
environment = ENVIRONMENTS.get(os_environ.get("ETSY_ENV", "PROD"), Production)
