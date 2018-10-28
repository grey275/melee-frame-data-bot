import json

from authlib.client import AssertionSession
from gspread import Client

from config import conf



def createAssertionSession(conf_file=conf.service_account_file, subject=None):
    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]

    with open(conf_file, 'r') as f:
        conf = json.loads(f.read())

    token_url = conf['token_uri']
    issuer = conf['client_email']
    key = conf['private_key']
    key_id = conf.get('private_key_id')

    header = {'alg': 'RS256'}
    if key_id:
        header['kid'] = key_id

    # Google puts scope in payload
    claims = {'scope': ' '.join(scopes)}
    return AssertionSession(
        grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
        token_url=token_url,
        issuer=issuer,
        audience=token_url,
        claims=claims,
        subject=subject,
        key=key,
        header=header,
    )
# session = createAssertionSession()

# gc = Client(None, session)

# sheets = gc.open_by_key(conf.sheet_id)

