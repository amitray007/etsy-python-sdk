from os import environ as os_environ


class Production(object):
    authorization_url = "https://www.etsy.com/oauth/connect"
    token_url = "https://api.etsy.com/v3/public/oauth/token"
    request_url = "https://openapi.etsy.com/v3/application"


ENVIRONMENTS = dict(PROD=Production)


environment = ENVIRONMENTS.get(os_environ.get("ETSY_ENV", "PROD"), Production)
