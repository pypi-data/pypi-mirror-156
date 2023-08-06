import json
import requests

def get_token(
    api_url: str,
    hashed_password: str,
    timeout: float = 3.0,
) -> str:
    payload = {
        'method': 'login',
        'id': 1,
        'jsonrpc': '2.0',
        'params': {
            'id': 'admin',
            'password': hashed_password,
        },
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    res = requests.post(api_url,
        headers=headers,
        data=json.dumps(payload),
        timeout=timeout,
    )
    response = res.json()

    token = response['token']
    return token
