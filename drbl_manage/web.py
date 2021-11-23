"""Web endpoints."""

import os
from loguru import logger

from flask import Flask, render_template, request, flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from drbl_manage import db_tools, mem
from urllib.parse import urlparse


app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY') or 'you-will-never-guess'
users = {
    os.environ.get('FLASK_LOGIN') or 'root': generate_password_hash(
        os.environ.get('FLASK_PASS') or 'pass'
    ),
}


def is_dribbble_link(uri):
    try:
        result = urlparse(uri)
        return result.netloc == 'dribbble.com'
    except AttributeError:
        return False


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@logger.catch
@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def index():
    if request.method == 'POST':
        acc_target = request.form.get('acc_target')
        add_link = request.form.get('add_link')
        add_quantity = request.form.get('add_quantity')
        rm = request.form.get('rm')
        form_dict = request.form.to_dict()
        if acc_target:
            try:
                acc_target = int(acc_target)
            except ValueError:
                flash('Use numbers, jerk!')
            else:
                if acc_target >= 0:
                    mem.set_need_accs(int(acc_target))
                else:
                    flash('Only positive numbers')
        elif add_link and add_quantity:
            try:
                add_quantity = int(add_quantity)
            except ValueError:
                flash('Use numbers, jerk!')
            else:
                if add_quantity < 1:
                    flash('Only positive numbers')
                else:
                    if is_dribbble_link(add_link):
                        if not mem.exist_active_tasks():
                            mem.flush_accs()
                            mem.set_accs(db_tools.get_acc_ids())
                        if not mem.set_task(add_link, add_quantity):
                            flash('Are you serious? This url has been added already!')

                    else:
                        flash("It isn't right url")
        elif rm and rm.isdigit():
            rm_id = int(rm)
            mem.rm_task(rm_id)
        elif form_dict:
            key_add = list(filter(lambda x: x.split(':')[0] == 'add', form_dict.keys()))[0]
            id_task = int(key_add.split(':')[-1])
            try:
                num = int(form_dict[key_add])
            except ValueError:
                flash('Use numbers, jerk!')
            else:
                mem.add_likes(id_task, num)

    total_accounts = db_tools.len_accs()
    in_work_accs = mem.len_accs()
    target_accounts = mem.get_need_accs()
    tasks = mem.get_active_tasks()
    return render_template(
        'index.html',
        total_accounts=total_accounts,
        in_work_accs=in_work_accs,
        target_accounts=target_accounts,
        tasks=tasks,
    )
