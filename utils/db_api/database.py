from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, Sequence, String, ForeignKey, Boolean, Time)
from aiogram import types
from data.config import db_user, db_password, db_host, db_name

db_gino = Gino()


class User(db_gino.Model):
    __tablename__ = "user"
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    tg_id = Column(BigInteger)
    full_name = Column(String(100))
    language = Column(String(2))
    username = Column(String(50))

    def __repr__(self):
        return "<User(id={}, tg_id={}, fullname={}, username={})>".format(
            self.id, self.tg_id, self.full_name, self.username)


class Settings(db_gino.Model):
    __tablename__ = "settings"
    id = Column(Integer, Sequence("settings_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.id"))
    daily_summary = Column(Time)
    notification_of_lesson = Column(Time)
    schedule_view_is_picture = Column(Boolean, default=False)

    def __repr__(self):
        return "<Settings(id={}, user_id={}, " \
               "daily_summary={}, notification_of_lesson={}, schedule_view_is_picture={})>".format(
                self.id, self.user_id, self.daily_summary, self.notification_of_lesson, self.schedule_view_is_picture)


class Teacher(db_gino.Model):
    __tablename__ = "teacher"
    id = Column(Integer, Sequence("teacher_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.id"))
    tt_id = Column(Integer)
    full_name = Column(String(100))

    def __repr__(self):
        return "<Teacher(id={}, tt_id={}, user_id={} name={})>".format(
            self.id, self.tt_id, self.user_id, self.name)


class Group(db_gino.Model):
    __tablename__ = "group"
    id = Column(Integer, Sequence("group_id_seq"), primary_key=True)
    tt_id = Column(Integer)
    name = Column(String(100))

    def __repr__(self):
        return "<Group(id={}, tt_id={}, name={})>".format(
            self.id, self.tt_id, self.name)


class Student(db_gino.Model):
    __tablename__ = "student"
    id = Column(Integer, Sequence("student_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.id"))
    group_id = Column(None, ForeignKey("group.id"))

    def __repr__(self):
        return "<Student(id={}, user_id={}, group_id={})>".format(
            self.id, self.user_id, self.group_id)


class DBCommands:

    async def get_user(self, user_id) -> User:
        user = await User.query.where(User.tg_id == user_id).gino.first()
        return user

    async def add_new_user(self) -> User:
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

    async def get_settings(self, tg_user_id: int) -> Settings:
        user_db = await self.get_user(tg_user_id)
        old_settings = await Settings.query.where(Settings.user_id == user_db.id).gino.first()
        if old_settings:
            return old_settings
        new_settings = Settings()
        new_settings.user_id = user_db.id
        await new_settings.create()
        return new_settings


async def create_db():
    await db_gino.set_bind(f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}')

    # Create tables
    # db.gino: GinoSchemaVisitor
    # await db_gino.gino.drop_all()
    await db_gino.gino.create_all()
