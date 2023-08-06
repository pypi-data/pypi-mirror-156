import json
import requests

def get_salt(
    api_url: str,
    timeout: float = 3.0,
) -> str:
    payload = {
        'method': 'Device.getDBInfo',
        'id': 90,
        'jsonrpc': '2.0',
        'params': {
            'WEB_KEY': '',
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

    result = response['result']
    webkey = result['WEB_KEY']

    return webkey
