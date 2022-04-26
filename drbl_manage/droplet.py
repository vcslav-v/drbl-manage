import json
import os
from time import sleep
from loguru import logger
from random import choice, randint

import requests

DROP_PREFIX = 'temp-selenoid-dribbble'


class Droplet:
    def __init__(self) -> None:
        regions = ['nyc1', 'nyc3', 'sfo3', 'ams3', 'sgp1', 'lon1', 'fra1', 'tor1', 'blr1']
        payloads = {
            'name': f'{DROP_PREFIX}-{randint(1,100)}',
            'region': choice(regions),
            'size': 's-1vcpu-2gb',
            'image': 'selenoid-18-04',
            'ipv6': True,
        }
        resp = do_req('post', 'droplets', payloads)
        if resp.ok:
            self.id = json.loads(resp.content)['droplet']['id']
            self._get_droplet_ip()
            sleep(30)
        else:
            self.id = None

    def close(self):
        do_req('del', f'droplets/{self.id}')

    def _get_droplet_ip(self):
        status = 'new'
        while status == 'new':
            sleep(10)
            resp = do_req('get', 'droplets')
            logger.debug(resp.content)
            for droplet_info in json.loads(resp.content)['droplets']:
                if droplet_info['id'] == self.id:
                    for ip_info in droplet_info['networks']['v4']:
                        if ip_info['type'] == 'public':
                            droplet_ip = ip_info['ip_address']
                    status = droplet_info['status']
                    break
        self.ip = droplet_ip


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            logger.error(exc_tb)



def do_req(type_req, end_point, payloads=None) -> requests.Response:
        api_token = os.environ.get('DO_TOKEN')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}',
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


def flush_droplets():
    resp = do_req('get', 'droplets')
    for droplet_info in json.loads(resp.content)['droplets']:
        if droplet_info['name'].startswith(DROP_PREFIX):
            do_req('del', f'droplets/{droplet_info["id"]}')