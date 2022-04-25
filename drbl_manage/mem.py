import os
from urllib.parse import urlparse
from loguru import logger

import redis

ACCOUNTS = 'accounts'
DR_TASK = 'task'
NEED_ACC = 'need_accs'

REDIS = os.environ.get('REDIS_TLS_URL')
if REDIS:
    parsed_redis_url = urlparse(REDIS)
    r = redis.Redis(
        host=parsed_redis_url.hostname,
        port=parsed_redis_url.port,
        username=parsed_redis_url.username,
        password=parsed_redis_url.password,
        ssl=True,
        ssl_cert_reqs=None,
        decode_responses=True,
    )
else:
    r = redis.Redis(
        host=os.environ.get('REDIS') or 'localhost',
        decode_responses=True,
    )


def set_need_accs(num):
    r.set(NEED_ACC, num)


def get_need_accs():
    if r.exists(NEED_ACC):
        return int(r.get(NEED_ACC))
    else:
        set_need_accs(0)
        return 0


def flush_accs():
    r.delete(ACCOUNTS)


def flush_tasks_in_work():
    task_keys = r.keys(f'{DR_TASK}:*')
    for task_key in task_keys:
        r.hset(task_key, mapping={'in_work': 0})


def len_accs():
    return r.llen(ACCOUNTS)


def set_accs(acc_ids):
    if acc_ids:
        r.lpush(ACCOUNTS, *acc_ids)


def pop_acc_id():
    return int(r.lpop(ACCOUNTS))


def set_task(link, likes):
    task_keys = r.keys(f'{DR_TASK}:*')
    for task_key in task_keys:
        if r.hget(task_key, 'link') == link:
            raise ValueError
    task_nums = list(map(lambda task: int(task.split(':')[-1]), task_keys))
    max_num = max(task_nums) if task_nums else 0
    next_num = max_num + 1
    r.hset(f'{DR_TASK}:{next_num}', mapping={'link': link, 'likes': likes, 'in_work': 0, 'done': 0})


def task_done(task_key):
    task_keys = r.keys(f'{DR_TASK}:*')
    if task_key in task_keys:
        task_done = int(r.hget(task_key, 'done'))
        r.hset(task_key, mapping={'done': task_done + 1})


def rm_task(task_id):
    r.delete(f'{DR_TASK}:{task_id}')


def add_likes(task_id, num):
    task_key = f'{DR_TASK}:{task_id}'
    task_keys = r.keys(f'{DR_TASK}:*')
    if task_key in task_keys:
        likes = int(r.hget(task_key, 'likes'))
        r.hset(task_key, mapping={'likes': likes + num})


def tasks_unreserve(tasks, num):
    for task in tasks:
        task_key, _ = task
        task_keys = r.keys(f'{DR_TASK}:*')
        if task_key in task_keys:
            need_likes = int(r.hget(task_key, 'likes'))
            task_done = int(r.hget(task_key, 'done'))
            if task_done >= need_likes:
                r.delete(task_key)
            else:
                task_in_work = int(r.hget(task_key, 'in_work'))
                r.hset(task_key, mapping={'in_work': task_in_work - num})


def _task_reserve(task_key, num):
    task_keys = r.keys(f'{DR_TASK}:*')
    if task_key in task_keys:
        task_in_work = int(r.hget(task_key, 'in_work'))
        need_likes = int(r.hget(task_key, 'likes'))
        task_done = int(r.hget(task_key, 'done'))
        logger.debug({
            'task_in_work': task_in_work,
            'need_likes': need_likes,
            'task_done': task_done,
        })
        if task_in_work > 0:
            return False
        r.hset(task_key, mapping={'in_work': task_in_work + num})
        return True


def set_tasks_in_work(num):
    task_keys = r.keys(f'{DR_TASK}:*')
    tasks = []
    for task_key in task_keys:
        if _task_reserve(task_key, num):
            link = r.hget(task_key, 'link')
            tasks.append((task_key, link))
    return tasks


def get_active_tasks():
    task_keys = r.keys(f'{DR_TASK}:*')
    tasks = []
    if not task_keys:
        return tasks
    for task_key in task_keys:
        task_id = task_key.split(':')[-1]
        link = r.hget(task_key, 'link')
        likes = r.hget(task_key, 'likes')
        done = r.hget(task_key, 'done')
        tasks.append({
            'id': task_id,
            'link': link,
            'targ_like': likes,
            'done_like': done
        })
    return tasks


def exist_active_tasks():
    task_keys = r.keys(f'{DR_TASK}:*')
    if task_keys:
        return True
    else:
        return False


def exist_active_accs():
    len_accs = r.llen(ACCOUNTS)
    if len_accs > 0:
        return True
    else:
        return False


flush_tasks_in_work()
