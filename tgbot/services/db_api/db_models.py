from gino import Gino
from sqlalchemy import Column, Integer, BigInteger, Sequence, String, ForeignKey, Boolean, Time, Date

from tgbot.config import config

db_gino = Gino()


class User(db_gino.Model):
    __tablename__ = "user"

    user_id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    tg_id = Column(BigInteger)
    full_name = Column(String(100))
    language = Column(String(10))
    username = Column(String(50))


class Settings(db_gino.Model):
    __tablename__ = "settings"

    settings_id = Column(Integer, Sequence("settings_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"))
    daily_summary = Column(Time)
    notification_of_lesson = Column(Time)
    schedule_view_is_picture = Column(Boolean, default=False)


class TeacherSPBU(db_gino.Model):
    __tablename__ = "teacher_spbu"

    teacher_spbu_id = Column(Integer, Sequence("teacher_spbu_id_seq"), primary_key=True)
    tt_id = Column(Integer)
    full_name = Column(String(100))


class Group(db_gino.Model):
    __tablename__ = "group"

    group_id = Column(Integer, Sequence("group_id_seq"), primary_key=True)
    tt_id = Column(Integer)
    name = Column(String(150))
    is_received_schedule = Column(Boolean, default=False)


class TeacherUser(db_gino.Model):
    __tablename__ = "teacher_user"

    teacher_user_id = Column(Integer, Sequence("teacher_user_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"))
    teacher_spbu_id = Column(None, ForeignKey("teacher_spbu.teacher_spbu_id"))


class Student(db_gino.Model):
    __tablename__ = "student"

    student_id = Column(Integer, Sequence("student_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"))
    group_id = Column(None, ForeignKey("group.group_id"))


class Subject(db_gino.Model):
    __tablename__ = "subject"

    subject_id = Column(Integer, Sequence("subject_id_seq"), primary_key=True)
    subject_name = Column(String(150))
    subject_format = Column(String(150))
    locations = Column(String(1000))


class GroupStudyEvent(db_gino.Model):
    __tablename__ = "student_study_event"

    student_event_id = Column(Integer, Sequence("student_event_id_seq"), primary_key=True)
    group_id = Column(None, ForeignKey("group.group_id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    subject_id = Column(None, ForeignKey("subject.subject_id"))
    educator = Column(String(300))
    is_canceled = Column(Boolean)


class TeacherStudyEvent(db_gino.Model):
    __tablename__ = "teacher_study_event"

    teacher_event_id = Column(Integer, Sequence("teacher_event_id_seq"), primary_key=True)
    teacher_id = Column(None, ForeignKey("teacher_spbu.teacher_spbu_id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    subject_id = Column(None, ForeignKey("subject.subject_id"))
    groups = Column(String(300))
    is_canceled = Column(Boolean)


async def create_db() -> None:
    pg_url = config.database.get_connection_url()
    await db_gino.set_bind(pg_url)
    await db_gino.gino.create_all()
