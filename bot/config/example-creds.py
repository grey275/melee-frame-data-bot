import json


class Creds:
    discord_token = ""

    service_account_file = "./google-service-account.json"

    service_account_creds = json.loads(open(service_account_file, "r").read())
