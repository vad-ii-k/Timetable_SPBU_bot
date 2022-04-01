from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, Sequence, String, ForeignKey)
from aiogram import types
from data.config import db_user, db_pass, db_host, db_name


db_gino = Gino()


class User(db_gino.Model):

    __tablename__ = "user"
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    tg_id = Column(BigInteger)
    full_name = Column(String(100))
    language = Column(String(2))
    username = Column(String(50))

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)


class Settings(db_gino.Model):

    __tablename__ = "settings"
    id = Column(Integer, Sequence("settings_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey('user.id'))

    def __repr__(self):
        return "<Settings()>".format()


class DBCommands:

    async def get_user(self, user_id) -> User:
        user = await User.query.where(User.tg_id == user_id).gino.first()
        return user

    async def add_new_user(self):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.tg_id = user.id
        new_user.full_name = user.full_name
        new_user.language = user.language_code
        new_user.username = user.username
        await new_user.create()
        return new_user


async def create_db():
    await db_gino.set_bind(f'postgresql://{db_user}:{db_pass}@{db_host}/{db_name}')

    # Create tables
    # db.gino: GinoSchemaVisitor
    await db_gino.gino.drop_all()
    await db_gino.gino.create_all()
