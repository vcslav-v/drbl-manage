import json
import os

from drbl_manage import db, models
from cryptography.fernet import Fernet


def get_cookies(domain: str, username: str) -> list[dict]:
    domain_cookies: list = []
    with db.SessionLocal() as session:
        account = session.query(models.Account).filter_by(
            username=username,
        ).first()
        if not account:
            return domain_cookies

        key = os.environ.get('KEY') or 'secret'
        fernet = Fernet(key.encode('UTF-8'))

        cookies = session.query(models.Cookie).filter_by(
            account=account,
        ).all()
        for cookie in cookies:
            domain_cookies.append(
                json.loads(fernet.decrypt(cookie.data.encode('UTF-8')).decode('UTF-8'))
            )
    return domain_cookies


def set_cookies(domain: str, username: str, cookies: list):
    with db.SessionLocal() as session:
        delete_cookies(domain, username)

        key = os.environ.get('KEY') or 'secret'
        fernet = Fernet(key.encode('UTF-8'))

        account = session.query(models.Account).filter_by(
            username=username,
        ).first()
        if not account:
            return

        for cookie in cookies:
            session.add(models.Cookie(
                account=account,
                data=fernet.encrypt(json.dumps(cookie).encode('UTF-8')).decode('utf-8'),
            ))
        session.commit()


def delete_cookies(domain: str, username: str):
    with db.SessionLocal() as session:
        account = session.query(models.Account).filter_by(
            username=username,
        ).first()
        if not account:
            return
        current_cookies = session.query(models.Cookie).filter_by(
            account=account,
        ).all()

        for cookie in current_cookies:
            session.delete(cookie)
        session.commit()


def is_new_email(new_email: str) -> bool:
    with db.SessionLocal() as session:
        if session.query(models.Account).filter_by(email=new_email).first():
            return False
        else:
            return True


def add_account(person):
    with db.SessionLocal() as session:
        acc = models.Account(
            name=person['name'],
            username=person['username'],
            password=person['password'],
            email=person['email'],
        )
        session.add(acc)
        session.commit()


def get_acc(acc_id):
    if not acc_id:
        return
    with db.SessionLocal() as session:
        acc = session.query(models.Account).filter_by(id=acc_id).first()
    return acc


def get_acc_ids():
    with db.SessionLocal() as session:
        result = []
        accs = session.query(models.Account).all()
        for acc in accs:
            result.append(acc.id)
    return result


def len_accs():
    with db.SessionLocal() as session:
        return session.query(models.Account).count()
