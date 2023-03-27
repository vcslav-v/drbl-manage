import json
import os
from random import randint
from time import sleep

import requests
from loguru import logger

DROP_PREFIX = 'temp-browser'
DO_TOKEN = os.environ.get('DO_TOKEN', '')


class DOApp:
    def __init__(self, **envs) -> None:
        payloads = {'spec': {
            'name': f'{DROP_PREFIX}-{randint(1,100)}',
            'region': 'fra',
            'services': [{
                'http_port': 4444,
                'name': 'browser',
                'image': {
                    'registry_type': 'DOCKER_HUB',
                    'registry': 'selenoid',
                    'repository': 'chrome',
                    'tag': 'latest',
                },
                'instance_size_slug': 'basic-m',
                'envs': []
            }]
        }
        }
        for env_key in envs:
            payloads['spec']['services'][0]['envs'].append(
                {'key': env_key, 'value': envs[env_key]}
            )
        resp = self._do_req('post', 'apps', payloads)
        if resp.ok:
            self.id = json.loads(resp.content)['app']['id']
            self._get_app_url()
            sleep(10)
        else:
            self.id = None

    def close(self):
        self._do_req('del', f'apps/{self.id}')

    def _get_app_url(self):
        url = ''
        while not url:
            sleep(10)
            resp = self._do_req('get', 'apps')
            for app_info in json.loads(resp.content)['apps']:
                if app_info['id'] == self.id and app_info.get('live_url_base'):
                    url = app_info['live_url_base']
                    break
        self.url = url

    def _do_req(self, type_req, end_point, payloads=None) -> requests.Response:
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            logger.error(exc_tb)