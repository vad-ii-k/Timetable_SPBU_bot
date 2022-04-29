from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, Sequence, String, ForeignKey, Boolean, Time, Date)

db_gino = Gino()


class User(db_gino.Model):
    __tablename__ = "user"
    user_id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    tg_id = Column(BigInteger)
    full_name = Column(String(100))
    language = Column(String(2))
    username = Column(String(50))

    def __repr__(self):
        return "<User(id={}, tg_id={}, fullname={}, username={})>".format(
            self.user_id, self.tg_id, self.full_name, self.username)


class Settings(db_gino.Model):
    __tablename__ = "settings"
    settings_id = Column(Integer, Sequence("settings_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"))
    daily_summary = Column(Time)
    notification_of_lesson = Column(Time)
    schedule_view_is_picture = Column(Boolean, default=False)

    def __repr__(self):
        return "<Settings(id={}, user_id={}, daily_summary={}," \
               "notification_of_lesson={}, schedule_view_is_picture={})>".format(
                self.settings_id, self.user_id, self.daily_summary,
                self.notification_of_lesson, self.schedule_view_is_picture)


class Teacher(db_gino.Model):
    __tablename__ = "teacher"
    teacher_id = Column(Integer, Sequence("teacher_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"))
    tt_id = Column(Integer)
    full_name = Column(String(100))

    def __repr__(self):
        return "<Teacher(id={}, tt_id={}, user_id={}, full_name={})>".format(
            self.teacher_id, self.tt_id, self.user_id, self.full_name)


class Group(db_gino.Model):
    __tablename__ = "group"
    group_id = Column(Integer, Sequence("group_id_seq"), primary_key=True)
    tt_id = Column(Integer)
    name = Column(String(150))
    is_received_schedule = Column(Boolean, default=False)

    def __repr__(self):
        return "<Group(id={}, tt_id={}, name={}, is_received_schedule={})>".format(
            self.group_id, self.tt_id, self.name, self.is_received_schedule)


class Student(db_gino.Model):
    __tablename__ = "student"
    student_id = Column(Integer, Sequence("student_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"))
    group_id = Column(None, ForeignKey("group.group_id"))

    def __repr__(self):
        return "<Student(id={}, user_id={}, group_id={})>".format(
            self.student_id, self.user_id, self.group_id)


class Subject(db_gino.Model):
    __tablename__ = "subject"
    subject_id = Column(Integer, Sequence("subject_id_seq"), primary_key=True)
    subject_name = Column(String(150))
    subject_format = Column(String(150))
    locations = Column(String(300))

    def __repr__(self):
        return "<Subject(id={}, subject_name={}, subject_format={}, locations={})>".format(
            self.subject_id, self.subject_name, self.subject_format, self.locations)


class StudentStudyEvent(db_gino.Model):
    __tablename__ = "student_study_event"
    student_event_id = Column(Integer, Sequence("student_event_id_seq"), primary_key=True)
    group_id = Column(None, ForeignKey("group.group_id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    subject_id = Column(None, ForeignKey("subject.subject_id"))
    educator = Column(String(300))
    is_canceled = Column(Boolean)

    def __repr__(self):
        return "<StudentStudyEvent(id={}, group_id={}, date={}, subject_id={}, is_canceled={})>".format(
            self.student_event_id, self.group_id, self.date, self.subject_id, self.is_canceled)
