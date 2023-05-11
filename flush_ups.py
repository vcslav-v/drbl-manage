import requests
import os
import json
from loguru import logger

DO_TOKEN = os.environ.get('DO_TOKEN', '')


def do_req(type_req, end_point, payloads=None) -> requests.Response:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DO_TOKEN}',
    }
    if type_req == 'post':
        resp = requests.post(
            f'https://api.digitalocean.com/v2/{end_point}',
            headers=headers,
            json=payloads,
        )
    elif type_req == 'del':
        resp = requests.delete(
            f'https://api.digitalocean.com/v2/{end_point}',
            headers=headers,
            json=payloads,
        )
    elif type_req == 'get':
        resp = requests.get(
            f'https://api.digitalocean.com/v2/{end_point}',
            headers=headers,
            json=payloads,
        )
    return resp


def main():
    resp = do_req('get', 'apps')
    for app_info in json.loads(resp.content)['apps']:
        if app_info['spec']['name'].startswith('temp'):
            resp = do_req('del', f'apps/{app_info["id"]}')
            if resp.ok:
                logger.info(f'App {app_info["spec"]["name"]} deleted')
            else:
                logger.error(f'App {app_info["spec"]["name"]} not deleted')


if __name__ == "__main__":
    main()