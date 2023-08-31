""" Database Model definition """
from gino import Gino
from sqlalchemy import BigInteger, Boolean, Column, Date, ForeignKey, Index, Integer, Sequence, String, Time, func

from tgbot.config import app_config

db_gino = Gino()


class User(db_gino.Model):
    """User"""

    __tablename__ = "user"

    user_id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=True)
    start_date = Column(Date, default=func.current_date())
    is_bot_blocked = Column(Boolean, nullable=False, default=False)


class Settings(db_gino.Model):
    """User settings"""

    __tablename__ = "settings"

    settings_id = Column(Integer, Sequence("settings_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"), nullable=False)
    daily_summary = Column(Time, nullable=True)
    notification_of_lesson = Column(Time, nullable=True)
    schedule_view_is_picture = Column(Boolean, default=False)
    language = Column(String(2), nullable=False)


class Group(db_gino.Model):
    """Group"""

    __tablename__ = "group"

    group_id = Column(Integer, Sequence("group_id_seq"), primary_key=True)
    tt_id = Column(Integer, nullable=False)
    name = Column(String(150), nullable=False)

    _idx1 = Index("group_idx_name", "name")


class MainScheduleInfo(db_gino.Model):
    """Information about main schedule of user"""

    __tablename__ = "main_schedule_info"

    user_id = Column(None, ForeignKey("user.user_id"), nullable=False)
    timetable_id = Column(Integer, nullable=False)
    user_type_is_student = Column(Boolean, nullable=False)
    name = Column(String(150), nullable=False)

    _idx1 = Index("main_schedule_info_idx_user_id", "user_id", unique=True)


async def connect_to_db() -> None:
    """Connecting to database"""
    await db_gino.set_bind(app_config.database.connection_url)
