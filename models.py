# -*- coding: utf-8 -*-

# Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
#
# This file is part of math_bot.
#
# math_bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#
# math_bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from datetime import datetime
from functools import wraps

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

from config import Config


engine = create_engine(Config.DATABASE_URI)

Base = declarative_base()
session_factory = sessionmaker(engine)
Session = scoped_session(session_factory)


class User (Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    last_name = Column(String(64))
    first_name = Column(String(64))
    username = Column(String(32))

    @classmethod
    def new(cls, user_id: int, last_name: str, first_name: str, username: str):
        return cls(id=user_id, last_name=last_name, first_name=first_name, username=username)


class LogRecord (Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref=backref('requests', lazy='dynamic'), uselist=False)

    in_chat_id = Column(Integer)

    command = Column(String(128))
    timestamp = Column(DateTime, default=datetime.now)
    info = Column(Text, default="{}")

    def __init__(self, *args, **kwargs):
        super(LogRecord, self).__init__(*args, **kwargs)

    @classmethod
    def new(cls, user: "User", command: str, chat_id: int, info: dict):
        return cls(
            user_id=user.id,
            command=command,
            info=json.dumps(info, default=lambda obj: str(obj)),
            in_chat_id=chat_id,
        )


def get_db():
    session = Session()
    return session


def close_db():
    Session.remove()


def db_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        res = func(*args, **kwargs, db=session)
        Session.remove()
        return res
    return wrapper


def get_user(db, user_id):
    user = db.query(User).get(user_id)
    if not user:
        return None
    return user


def create_all():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all()
