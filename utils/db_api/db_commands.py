from datetime import time, date
from typing import List, Tuple

from aiogram import types
from sqlalchemy import and_, asc

from tgbot.config import PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_NAME
from utils.db_api.db_models import (
    User,
    Settings,
    TeacherSPBU,
    Group,
    Student,
    GroupStudyEvent,
    db_gino,
    Subject,
    TeacherStudyEvent,
    TeacherUser,
)


class DBCommands:
    @staticmethod
    async def get_user() -> User:
        user_tg = types.User.get_current()
        user = await User.query.where(User.tg_id == user_tg.id).gino.first()
        return user

    @staticmethod
    async def get_user_by_tg_id(tg_id: int) -> User:
        user = await User.query.where(User.tg_id == tg_id).gino.first()
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

    @staticmethod
    async def get_settings(user_db: User) -> Settings:
        settings = await Settings.query.where(
            Settings.user_id == user_db.user_id
        ).gino.first()
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

    @staticmethod
    async def get_teacher_spbu(teacher_spbu_id: int) -> TeacherSPBU:
        teacher = await TeacherSPBU.query.where(
            TeacherSPBU.teacher_spbu_id == teacher_spbu_id
        ).gino.first()
        return teacher

    @staticmethod
    async def get_teacher_spbu_by_tt_id(tt_id: int) -> TeacherSPBU:
        teacher = await TeacherSPBU.query.where(TeacherSPBU.tt_id == tt_id).gino.first()
        return teacher

    async def set_teacher_spbu(self, tt_id: int, full_name: str) -> TeacherSPBU:
        old_teacher_spbu = await self.get_teacher_spbu_by_tt_id(tt_id)
        if old_teacher_spbu:
            return old_teacher_spbu
        new_teacher_spbu = TeacherSPBU()
        new_teacher_spbu.tt_id = tt_id
        new_teacher_spbu.full_name = full_name
        await new_teacher_spbu.create()
        return new_teacher_spbu

    @staticmethod
    async def get_teacher_user(user_db: User) -> TeacherUser:
        teacher_user = await TeacherUser.query.where(
            TeacherUser.user_id == user_db.user_id
        ).gino.first()
        return teacher_user

    async def set_teacher_user(self, tt_id: int) -> TeacherUser:
        user_db = await self.get_user()
        await self._clear_teacher(user_db)
        await self._clear_student(user_db)
        old_teacher_user = await self.get_teacher_user(user_db)
        teacher_spbu = await self.get_teacher_spbu_by_tt_id(tt_id)
        if old_teacher_user:
            await old_teacher_user.update(
                teacher_spbu_id=teacher_spbu.teacher_spbu_id
            ).apply()
            return old_teacher_user
        new_teacher_user = TeacherUser()
        new_teacher_user.user_id = user_db.user_id
        new_teacher_user.teacher_spbu_id = teacher_spbu.teacher_spbu_id
        await new_teacher_user.create()
        return new_teacher_user

    async def _clear_teacher(self, user_db: User) -> None:
        old_teacher = await self.get_teacher_user(user_db)
        if old_teacher:
            await old_teacher.delete()

    @staticmethod
    async def get_group(group_id: int) -> Group:
        group = await Group.query.where(Group.group_id == group_id).gino.first()
        return group

    @staticmethod
    async def get_group_by_tt_id(tt_id: int) -> Group:
        group = await Group.query.where(Group.tt_id == tt_id).gino.first()
        return group

    @staticmethod
    async def get_groups_by_name(group_name: str) -> List[Group]:
        groups = (
            await Group.query.where(Group.name.contains(group_name))
                .order_by(asc(Group.name))
                .gino.all()
        )
        return groups

    async def add_new_group(self, tt_id: int, group_name: str) -> Group:
        old_group = await self.get_group_by_tt_id(tt_id)
        if old_group:
            return old_group
        new_group = Group()
        new_group.tt_id = tt_id
        new_group.name = group_name
        await new_group.create()
        return new_group

    @staticmethod
    async def get_student(user_db: User) -> Student:
        student = await Student.query.where(
            Student.user_id == user_db.user_id
        ).gino.first()
        return student

    async def _clear_student(self, user_db: User) -> None:
        old_student = await self.get_student(user_db)
        if old_student:
            await old_student.delete()

    async def set_student(self, tt_id: int) -> Student:
        user_db = await self.get_user()
        await self._clear_teacher(user_db)
        await self._clear_student(user_db)
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

    @staticmethod
    async def get_subject(subject_id: int) -> Subject:
        subject = await Subject.query.where(
            Subject.subject_id == subject_id
        ).gino.first()
        return subject

    @staticmethod
    async def _get_subject_from_full_info(
            subject_name: str, subject_format: str, locations: str
    ) -> Subject:
        subject = await Subject.query.where(
            and_(
                Subject.subject_name == subject_name,
                Subject.subject_format == subject_format,
                Subject.locations == locations,
            )
        ).gino.first()
        return subject

    async def add_new_subject(
            self, subject_name: str, subject_format: str, locations: str
    ) -> Subject:
        old_subject = await self._get_subject_from_full_info(
            subject_name, subject_format, locations
        )
        if old_subject:
            return old_subject
        new_subject = Subject()
        new_subject.subject_name = subject_name
        new_subject.subject_format = subject_format
        new_subject.locations = locations
        await new_subject.create()
        return new_subject

    @staticmethod
    async def _get_group_study_event(
            group_id: int,
            event_date: date,
            start_time: time,
            subject_id: int,
            educator: str,
    ) -> GroupStudyEvent:
        study_event = await GroupStudyEvent.query.where(
            and_(
                GroupStudyEvent.group_id == group_id,
                GroupStudyEvent.date == event_date,
                GroupStudyEvent.start_time == start_time,
                GroupStudyEvent.subject_id == subject_id,
                GroupStudyEvent.educator == educator,
            )
        ).gino.first()
        return study_event

    async def add_new_group_study_event(
            self,
            tt_id: int,
            subject_id: int,
            event_date: date,
            start_time: time,
            end_time: time,
            educator: str,
            is_canceled: bool,
    ) -> GroupStudyEvent:
        group = await self.get_group_by_tt_id(tt_id)
        old_study_event = await self._get_group_study_event(
            group.group_id, event_date, start_time, subject_id, educator
        )
        if old_study_event:
            return old_study_event
        new_study_event = GroupStudyEvent()
        new_study_event.group_id = group.group_id
        new_study_event.date = event_date
        new_study_event.start_time = start_time
        new_study_event.end_time = end_time
        new_study_event.subject_id = subject_id
        new_study_event.educator = educator
        new_study_event.is_canceled = is_canceled
        await new_study_event.create()
        return new_study_event

    @staticmethod
    async def get_group_timetable_day(
            group_id: int, day: date
    ) -> List[GroupStudyEvent]:
        study_events = (
            await GroupStudyEvent.join(
                Subject, Subject.subject_id == GroupStudyEvent.subject_id
            )
                .select()
                .where(
                and_(GroupStudyEvent.group_id == group_id, GroupStudyEvent.date == day)
            )
                .order_by(
                asc(GroupStudyEvent.date),
                asc(GroupStudyEvent.start_time),
                asc(Subject.subject_name),
            )
                .gino.all()
        )
        return study_events

    @staticmethod
    async def get_group_timetable_week(
            group_id: int, monday: date, sunday: date
    ) -> List[GroupStudyEvent]:
        study_events = (
            await GroupStudyEvent.join(
                Subject, Subject.subject_id == GroupStudyEvent.subject_id
            )
                .select()
                .where(
                and_(
                    GroupStudyEvent.group_id == group_id,
                    GroupStudyEvent.date >= monday,
                    GroupStudyEvent.date <= sunday,
                )
            )
                .order_by(
                asc(GroupStudyEvent.date),
                asc(GroupStudyEvent.start_time),
                asc(Subject.subject_name),
            )
                .gino.all()
        )
        return study_events

    @staticmethod
    async def _get_teacher_study_event(
            teacher_id: int,
            event_date: date,
            start_time: time,
            subject_id: int,
            groups: str,
    ) -> TeacherStudyEvent:
        study_event = await TeacherStudyEvent.query.where(
            and_(
                TeacherStudyEvent.teacher_id == teacher_id,
                TeacherStudyEvent.date == event_date,
                TeacherStudyEvent.start_time == start_time,
                TeacherStudyEvent.subject_id == subject_id,
                TeacherStudyEvent.groups == groups,
            )
        ).gino.first()
        return study_event

    async def add_new_teacher_study_event(
            self,
            tt_id: int,
            full_name: str,
            subject_id: int,
            event_date: date,
            start_time: time,
            end_time: time,
            groups: str,
            is_canceled: bool,
    ) -> TeacherStudyEvent:
        teacher_spbu = await self.set_teacher_spbu(tt_id, full_name)
        old_study_event = await self._get_teacher_study_event(
            teacher_spbu.teacher_spbu_id, event_date, start_time, subject_id, groups
        )
        if old_study_event:
            return old_study_event
        new_study_event = TeacherStudyEvent()
        new_study_event.teacher_id = teacher_spbu.teacher_spbu_id
        new_study_event.date = event_date
        new_study_event.start_time = start_time
        new_study_event.end_time = end_time
        new_study_event.subject_id = subject_id
        new_study_event.groups = groups
        new_study_event.is_canceled = is_canceled
        await new_study_event.create()
        return new_study_event

    @staticmethod
    async def get_teacher_timetable_day(
            teacher_id: int, day: date
    ) -> List[TeacherStudyEvent]:
        study_events = (
            await TeacherStudyEvent.join(
                Subject, Subject.subject_id == TeacherStudyEvent.subject_id
            )
                .select()
                .where(
                and_(
                    TeacherStudyEvent.teacher_id == teacher_id,
                    TeacherStudyEvent.date == day,
                )
            )
                .order_by(asc(TeacherStudyEvent.date), asc(TeacherStudyEvent.start_time))
                .gino.all()
        )
        return study_events

    @staticmethod
    async def get_teacher_timetable_week(
            teacher_id: int, monday: date, sunday: date
    ) -> List[TeacherStudyEvent]:
        study_events = (
            await TeacherStudyEvent.join(
                Subject, Subject.subject_id == TeacherStudyEvent.subject_id
            )
                .select()
                .where(
                and_(
                    TeacherStudyEvent.teacher_id == teacher_id,
                    TeacherStudyEvent.date >= monday,
                    TeacherStudyEvent.date <= sunday,
                )
            )
                .order_by(asc(TeacherStudyEvent.date), asc(TeacherStudyEvent.start_time))
                .gino.all()
        )
        return study_events

    @staticmethod
    async def get_active_groups_tt_ids() -> List[int]:
        active_students = await Student.select("group_id").gino.all()
        groups_db_ids = [int(group_id[0]) for group_id in active_students]
        active_groups = (
            await Group.select("tt_id")
                .where(Group.group_id.in_(groups_db_ids))
                .gino.all()
        )
        groups_tt_ids = list(map(lambda tt_id: int(tt_id[0]), active_groups))
        return groups_tt_ids

    @staticmethod
    async def get_active_teachers_tt_ids() -> List[int]:
        active_users = await TeacherUser.select("teacher_spbu_id").gino.all()
        db_ids = [int(teacher_id[0]) for teacher_id in active_users]
        active_spbu = (
            await TeacherSPBU.select("tt_id")
                .where(TeacherSPBU.teacher_spbu_id.in_(db_ids))
                .gino.all()
        )
        tt_ids = list(map(lambda tt_id: int(tt_id[0]), active_spbu))
        return tt_ids

    @staticmethod
    async def get_users_with_sign_to_summary(
            current_time: time,
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        users = (
            await Settings.select("user_id")
                .where(Settings.daily_summary == current_time)
                .gino.all()
        )
        users_ids = [int(user[0]) for user in users]
        students = (
            await Student.join(User, Student.user_id == User.user_id)
                .join(Group, Student.group_id == Group.group_id)
                .select()
                .where(Student.user_id.in_(users_ids))
                .gino.all()
        )
        list_tg_ids_with_group_tt_id = [
            (int(student[4]), int(student[9])) for student in students
        ]
        teachers = (
            await TeacherUser.join(User, TeacherUser.user_id == User.user_id)
                .join(TeacherSPBU, TeacherUser.teacher_spbu_id == TeacherSPBU.teacher_spbu_id)
                .select()
                .where(TeacherUser.user_id.in_(users_ids))
                .gino.all()
        )
        list_user_ids_with_teacher_id = [
            (int(teacher[4]), int(teacher[9])) for teacher in teachers
        ]
        return list_tg_ids_with_group_tt_id, list_user_ids_with_teacher_id

    @staticmethod
    async def clearing_unused_info():
        ids_of_student_groups = list(
            map(
                lambda student: int(student[0]),
                await Student.select("group_id").gino.all(),
            )
        )
        unused_groups_ids = list(
            map(
                lambda group: int(group[0]),
                await Group.select("group_id")
                    .where(
                    and_(
                        Group.is_received_schedule,
                        Group.group_id.notin_(ids_of_student_groups),
                    )
                )
                    .gino.all(),
            )
        )
        await Group.update.values(is_received_schedule=False).where(
            Group.group_id.in_(unused_groups_ids)
        ).gino.status()
        await GroupStudyEvent.delete.where(
            GroupStudyEvent.group_id.in_(unused_groups_ids)
        ).gino.status()


async def create_db() -> None:
    pg_url = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}"
    await db_gino.set_bind(pg_url)
    # Create tables
    # db.gino: GinoSchemaVisitor
    # await db_gino.gino.drop_all()
    await db_gino.gino.create_all()
