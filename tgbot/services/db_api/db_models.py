from gino import Gino
from sqlalchemy import Column, Integer, BigInteger, Sequence, String, ForeignKey, Boolean, Time, Index

from tgbot.config import app_config

db_gino = Gino()


class User(db_gino.Model):
    __tablename__ = "user"

    user_id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    tg_id = Column(BigInteger)
    full_name = Column(String(100))
    username = Column(String(50))


class Settings(db_gino.Model):
    __tablename__ = "settings"

    settings_id = Column(Integer, Sequence("settings_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"))
    daily_summary = Column(Time)
    notification_of_lesson = Column(Time)
    schedule_view_is_picture = Column(Boolean, default=False)
    language = Column(String(2))


class Group(db_gino.Model):
    __tablename__ = "group"

    group_id = Column(Integer, Sequence("group_id_seq"), primary_key=True)
    tt_id = Column(Integer)
    name = Column(String(150))

    _idx1 = Index('group_idx_name', 'name')


class MainScheduleInfo(db_gino.Model):
    __tablename__ = "main_schedule_info"

    user_id = Column(None, ForeignKey("user.user_id"))
    timetable_id = Column(Integer)
    user_type_is_student = Column(Boolean)
    name = Column(String(150))

    _idx1 = Index('main_schedule_info_idx_user_id', 'user_id', unique=True)


async def create_db() -> None:
    await db_gino.set_bind(app_config.database.connection_url)
    await db_gino.gino.create_all()
