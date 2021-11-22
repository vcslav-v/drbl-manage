from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if environ.get('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL').replace(  # type: ignore
        'postgres', 'postgresql+psycopg2'
    )
else:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}/{dbname}'.format(
            user='postgres',
            password='mysecretpassword',
            host='0.0.0.0',
            dbname='postgres',
        )

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
