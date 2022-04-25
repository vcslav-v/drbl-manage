import os
import threading

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger

from drbl_manage import db_tools, dribbble, mem
from drbl_manage.droplet import Droplet

sched = BlockingScheduler()

ACC_BY_DROPLET = 5
MAX_DROPLETS = 10


def send_tg_alarm(message):
    requests.post(
        'https://api.telegram.org/bot{token}/sendMessage?chat_id={tui}&text={text}'.format(
            token=os.environ.get('ALLERT_BOT_TOKEN'),
            tui=os.environ.get('ADMIN_TUI'),
            text=message,
        ))


@sched.scheduled_job('interval', minutes=6)
@logger.catch
def reg_new_accs():
    logger.debug('check for new accs')
    if db_tools.len_accs() - mem.get_need_accs() < 0:
        logger.debug('start for new accs')
        with Droplet() as do_drop:
            for _ in range(ACC_BY_DROPLET):
                try:
                    dribbble.make_new_user(do_drop.ip)
                except Exception:
                    logger.error('make_new_user Exception')


@sched.scheduled_job('interval', minutes=1)
@logger.catch
def do_like_tasks():
    logger.debug('check for tasks')
    if not mem.exist_active_tasks() or not mem.exist_active_accs():
        return
    for _ in range(MAX_DROPLETS):
        tasks = mem.set_tasks_in_work(ACC_BY_DROPLET)
        if tasks:
            thread = threading.Thread(target=do_tasks, args=(tasks,))
            thread.start()
        else:
            break


def do_tasks(tasks):
    with Droplet() as do_drop:
        logger.debug('start for tasks')
        for _ in range(ACC_BY_DROPLET):
            try:
                dribbble.do_tasks(do_drop.ip, tasks)
            except Exception as e:
                logger.error(e.__repr__())
                break
            finally:
                mem.tasks_unreserve(tasks, 1)


if __name__ == "__main__":
    logger.add(sink=send_tg_alarm, level='INFO')
    sched.start()
