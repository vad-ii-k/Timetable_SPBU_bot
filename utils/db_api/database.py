from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, Sequence, String, ForeignKey, Boolean, Time)
from aiogram import types
from data.config import db_user, db_password, db_host, db_name

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
        return "<Settings(id={}, user_id={}, " \
               "daily_summary={}, notification_of_lesson={}, schedule_view_is_picture={})>".format(
                self.settings_id, self.user_id, self.daily_summary, self.notification_of_lesson, self.schedule_view_is_picture)


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
    name = Column(String(100))

    def __repr__(self):
        return "<Group(id={}, tt_id={}, name={})>".format(
            self.group_id, self.tt_id, self.name)


class Student(db_gino.Model):
    __tablename__ = "student"
    student_id = Column(Integer, Sequence("student_id_seq"), primary_key=True)
    user_id = Column(None, ForeignKey("user.user_id"))
    group_id = Column(None, ForeignKey("group.group_id"))

    def __repr__(self):
        return "<Student(id={}, user_id={}, group_id={})>".format(
            self.student_id, self.user_id, self.group_id)


class DBCommands:

    async def get_user(self, user_id) -> User:
        user = await User.query.where(User.tg_id == user_id).gino.first()
        return user

    async def add_new_user(self) -> User:
        user_tg = types.User.get_current()
        old_user = await self.get_user(user_tg.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.tg_id = user_tg.id
        new_user.full_name = user_tg.full_name
        new_user.language = user_tg.language_code
        new_user.username = user_tg.username
        await new_user.create()
        return new_user

    async def get_settings(self, user_db: User) -> Settings:
        settings = await Settings.query.where(Settings.user_id == user_db.user_id).gino.first()
        return settings

    async def set_settings(self, tg_user_id: int) -> Settings:
        user_db = await self.get_user(tg_user_id)
        old_settings = await self.get_settings(user_db)
        if old_settings:
            return old_settings
        new_settings = Settings()
        new_settings.user_id = user_db.user_id
        await new_settings.create()
        return new_settings

    async def get_teacher(self, user_db: User) -> Teacher:
        teacher = await Teacher.query.where(Teacher.user_id == user_db.user_id).gino.first()
        return teacher

    async def set_teacher(self, tt_id: int, full_name: str) -> Teacher:
        user_tg = types.User.get_current()
        user_db = await self.get_user(user_tg.id)
        old_teacher = await self.get_teacher(user_db)
        if old_teacher:
            await old_teacher.update(tt_id=tt_id, full_name=full_name).apply()
            return old_teacher
        new_teacher = Teacher()
        new_teacher.user_id = user_db.user_id
        new_teacher.tt_id = tt_id
        new_teacher.full_name = full_name
        await new_teacher.create()
        return new_teacher

    async def get_group(self, tt_id: int) -> Group:
        group = await Group.query.where(Group.tt_id == tt_id).gino.first()
        return group

    async def set_group(self, tt_id: int, group_name: str) -> Group:
        old_group = await self.get_group(tt_id)
        if old_group:
            return old_group
        new_group = Group()
        new_group.tt_id = tt_id
        new_group.name = group_name
        await new_group.create()
        return new_group

    async def get_student(self, user_db: User) -> Student:
        student = await Student.query.where(Student.user_id == user_db.user_id).gino.first()
        return student

    async def set_student(self, tt_id: int, group_name: str) -> Student:
        user_tg = types.User.get_current()
        user_db = await self.get_user(user_tg.id)
        old_student = await self.get_student(user_db)
        group = await self.set_group(tt_id, group_name)
        if old_student:
            await old_student.update(group_id=group.group_id).apply()
            return old_student
        new_student = Student()
        new_student.user_id = user_db.user_id
        new_student.group_id = group.group_id
        await new_student.create()
        return new_student


async def create_db():
    await db_gino.set_bind(f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}')

    # Create tables
    # db.gino: GinoSchemaVisitor
    # await db_gino.gino.drop_all()
    await db_gino.gino.create_all()
