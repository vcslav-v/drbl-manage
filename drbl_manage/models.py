"""DataBase models."""
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Account(Base):
    """Dribbble account."""

    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)

    name = Column(Text)
    username = Column(Text, unique=True)
    password = Column(Text)
    email = Column(Text)

    cookies = relationship('Cookie', back_populates='account')


class Cookie(Base):
    """Cookie."""

    __tablename__ = 'cookies'

    id = Column(Integer, primary_key=True)

    data = Column(Text)

    account_id = Column(Integer, ForeignKey('accounts.id'))
    account = relationship('Account', back_populates='cookies')
