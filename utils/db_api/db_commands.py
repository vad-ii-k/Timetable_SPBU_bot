import datetime
from sqlalchemy import and_

from aiogram import types

from data.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_HOST, POSTGRES_NAME
from utils.db_api.db_models import User, Settings, Teacher, Group, Student, StudentStudyEvent, db_gino


class DBCommands:

    async def get_user(self) -> User:
        user_tg = types.User.get_current()
        user = await User.query.where(User.tg_id == user_tg.id).gino.first()
        return user

    async def add_new_user(self) -> User:
        old_user = await self.get_user()
        if old_user:
            return old_user
        user_tg = types.User.get_current()
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

    async def set_settings(self) -> Settings:
        user_db = await self.get_user()
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
        user_db = await self.get_user()
        await self.clear_student(user_db)
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

    async def clear_teacher(self, user_db: User):
        old_teacher = await self.get_teacher(user_db)
        if old_teacher:
            await old_teacher.delete()

    async def get_group(self, group_id: int) -> Group:
        group = await Group.query.where(Group.group_id == group_id).gino.first()
        return group

    async def get_group_by_tt_id(self, tt_id: int) -> Group:
        group = await Group.query.where(Group.tt_id == tt_id).gino.first()
        return group

    async def get_groups_by_name(self, group_name: str) -> list:
        groups = await Group.query.where(Group.name.contains(group_name)).gino.all()
        return groups

    async def get_group_students(self, group_id: int) -> list:
        students = await Student.query.where(Student.group_id == group_id).gino.all()
        return students

    async def add_new_group(self, tt_id: int, group_name: str) -> Group:
        new_group = Group()
        new_group.tt_id = tt_id
        new_group.name = group_name
        await new_group.create()
        return new_group

    async def get_student(self, user_db: User) -> Student:
        student = await Student.query.where(Student.user_id == user_db.user_id).gino.first()
        return student

    async def clear_student(self, user_db: User):
        old_student = await self.get_student(user_db)
        if old_student:
            await old_student.delete()

    async def set_student(self, tt_id: int, group_name: str) -> Student:
        user_db = await self.get_user()
        await self.clear_teacher(user_db)
        await self.clear_student(user_db)
        old_student = await self.get_student(user_db)
        group = await self.get_group_by_tt_id(tt_id)
        if old_student:
            await old_student.update(group_id=group.group_id).apply()
            return old_student
        new_student = Student()
        new_student.user_id = user_db.user_id
        new_student.group_id = group.group_id
        await new_student.create()
        return new_student

    async def get_study_event(self, group_id: int, date: datetime.date, start_time: datetime.time,
                              subject_name: str, educator: str) -> StudentStudyEvent:
        study_event = await StudentStudyEvent.query.where(and_(
            StudentStudyEvent.group_id == group_id,
            StudentStudyEvent.date == date,
            StudentStudyEvent.start_time == start_time,
            StudentStudyEvent.subject_name == subject_name,
            StudentStudyEvent.educator == educator)).gino.first()
        return study_event

    async def add_new_study_event(
            self, tt_id: int, date: datetime.date, start_time: datetime.time, end_time: datetime.time, subject_name: str,
            subject_format: str, educator: str, locations: str, is_canceled: bool) -> StudentStudyEvent:

        group = await self.get_group_by_tt_id(tt_id)
        old_study_event = await self.get_study_event(group.group_id, date, start_time, subject_name, educator)
        if old_study_event:
            return old_study_event
        new_study_event = StudentStudyEvent()
        new_study_event.group_id = group.group_id
        new_study_event.date = date
        new_study_event.start_time = start_time
        new_study_event.end_time = end_time
        new_study_event.subject_name = subject_name
        new_study_event.subject_format = subject_format
        new_study_event.educator = educator
        new_study_event.locations = locations
        new_study_event.is_canceled = is_canceled
        await new_study_event.create()
        return new_study_event


async def create_db():
    pg_url = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}'
    await db_gino.set_bind(pg_url)

    # Create tables
    # db.gino: GinoSchemaVisitor
    # await db_gino.gino.drop_all()
    await db_gino.gino.create_all()
