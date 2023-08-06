import json
import requests

def get_wan_ipv4(
    api_url: str,
    token: str,
    timeout: float = 3.0,
) -> str:
    payload = {
        'method': 'QuickSetupInfo',
        'id': 90,
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

    result = response['result']

    ipv4_addr = result['NET_WAN_IPv4_Address']
    return ipv4_addr
