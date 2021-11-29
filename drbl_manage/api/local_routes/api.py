import os
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from drbl_manage import schemas, mem, db_tools

router = APIRouter()
security = HTTPBasic()

username = os.environ.get('API_USERNAME') or 'root'
password = os.environ.get('API_PASSWORD') or 'pass'


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, username)
    correct_password = secrets.compare_digest(credentials.password, password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get('/get-liker-page')
def get_liker_page_data(_: str = Depends(get_current_username)) -> schemas.LikerPage:
    page_data = schemas.LikerPage(
        total_accounts=db_tools.len_accs(),
        in_work_accs=mem.len_accs(),
        target_accounts=mem.get_need_accs(),
        tasks=[],
    )
    for task in mem.get_active_tasks():
        page_data.tasks.append(schemas.Task(
            id=int(task['id']),
            link=task['link'],
            targ_like=int(task['targ_like']),
            done_like=int(task['done_like']),
        ))
    return page_data


@router.post('/target-acc')
def set_need_accs(acc_target: int, _: str = Depends(get_current_username)):
    mem.set_need_accs(int(acc_target))
    return {'ok': 200}


@router.post('/add-task')
def add_task(link: str, quantity: int, _: str = Depends(get_current_username)):
    if not mem.exist_active_tasks():
        mem.flush_accs()
        mem.set_accs(db_tools.get_acc_ids())
    try:
        mem.set_task(link, quantity)
    except ValueError:
        return {'error': 'link exists'}
    return {'ok': 200}


@router.post('/rm-task')
def rm_task(task_id: int, _: str = Depends(get_current_username)):
    mem.rm_task(task_id)
    return {'ok': 200}


@router.post('/add-task-likes')
def add_task_likes(task_id: int, num_likes: int, _: str = Depends(get_current_username)):
    mem.add_likes(task_id, num_likes)
    return {'ok': 200}
