import json
import requests
from typing import Dict, Any

def reboot_router(
    api_url: str,
    token: str,
    timeout: float = 3.0,
) -> Dict[str, Any]:
    payload = {
        'method': 'System.reboot',
        'id': 24,
        'jsonrpc': '2.0',
        'token': token,
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

    # result = response['result']

    return response
