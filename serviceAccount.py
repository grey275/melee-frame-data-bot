import json
from config import Config

from authlib.client import AssertionSession


def createSession(subject=None):
    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    conf = Config.service_account_creds

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
