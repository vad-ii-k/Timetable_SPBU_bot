from datetime import datetime, date, time
from dataclasses import dataclass
from typing import List

from tgbot import loader


@dataclass
class StudyEvent:
    start_time: time
    end_time: time
    subject_name: str
    subject_format: str
    locations: str
    contingent: str
    is_canceled: bool


@dataclass
class TimetableOneDay:
    date: date
    events: List[StudyEvent]


async def add_group_timetable_to_db(events: dict, tt_id: int) -> None:
    for event in events:
        subject: str = event.get("Subject")
        subject_name, subject_format = subject.rsplit(sep=", ", maxsplit=1)\
            if subject.rfind(', ') != -1 else (subject, '—')
        locations: str = event.get("LocationsDisplayText")
        db_subject = await loader.db.add_new_subject(subject_name, subject_format, locations)

        start: datetime = datetime.strptime(event.get("Start"), "%Y-%m-%dT%H:%M:%S")
        end: datetime = datetime.strptime(event.get("End"), "%Y-%m-%dT%H:%M:%S")
        event_date: date = start.date()
        educator: str = ''.join(educator.rsplit(sep=", ", maxsplit=1)[0] + ', '
                                for educator in event.get("EducatorsDisplayText").split(sep=";"))[:-2]
        is_cancelled: bool = event.get("IsCancelled")
        await loader.db.add_new_group_study_event(int(tt_id), db_subject.subject_id, event_date, start,
                                                  end, educator, is_cancelled)


async def get_group_timetable_day_from_db(group_db_id: int, current_date: date) -> List[TimetableOneDay]:
    timetable_info = []
    study_events = await loader.db.get_group_timetable_day(group_db_id, current_date)
    timetable_one_day = TimetableOneDay(date=current_date, events=[])
    for study_event in study_events:
        event = StudyEvent(start_time=study_event.start_time,
                           end_time=study_event.end_time,
                           subject_name=study_event.subject_name,
                           subject_format=study_event.subject_format,
                           locations=study_event.locations,
                           contingent=study_event.educator,
                           is_canceled=study_event.is_canceled)
        timetable_one_day.events.append(event)
    timetable_info.append(timetable_one_day)
    return timetable_info


async def get_group_timetable_week_from_db(group_db_id: int, monday: date, sunday: date) -> List[TimetableOneDay]:
    timetable_info = []
    study_events = await loader.db.get_group_timetable_week(group_db_id, monday, sunday)
    i = 0
    while i < len(study_events):
        day = study_events[i].date
        timetable_one_day = TimetableOneDay(date=day, events=[])
        while i < len(study_events) and day == study_events[i].date:
            event = StudyEvent(start_time=study_events[i].start_time,
                               end_time=study_events[i].end_time,
                               subject_name=study_events[i].subject_name,
                               subject_format=study_events[i].subject_format,
                               locations=study_events[i].locations,
                               contingent=study_events[i].educator,
                               is_canceled=study_events[i].is_canceled)
            timetable_one_day.events.append(event)
            i += 1
        timetable_info.append(timetable_one_day)
    return timetable_info


async def add_teacher_timetable_to_db(events: dict, tt_id: int, full_name: str) -> None:
    for event in events:
        subject: str = event.get("Subject")
        subject_name, subject_format = subject.rsplit(sep=", ", maxsplit=1)\
            if subject.rfind(', ') != -1 else (subject, '—')
        locations: str = event.get("LocationsDisplayText")
        db_subject = await loader.db.add_new_subject(subject_name, subject_format, locations)

        start: datetime = datetime.strptime(event.get("Start"), "%Y-%m-%dT%H:%M:%S")
        end: datetime = datetime.strptime(event.get("End"), "%Y-%m-%dT%H:%M:%S")
        event_date: date = start.date()
        groups: str = event.get("ContingentUnitName")
        is_cancelled: bool = event.get("IsCancelled")
        await loader.db.add_new_teacher_study_event(int(tt_id), full_name, db_subject.subject_id, event_date, start,
                                                    end, groups, is_cancelled)


async def get_teacher_timetable_day_from_db(teacher_db_id: int, current_date: date) -> List[TimetableOneDay]:
    timetable_info = []
    study_events = await loader.db.get_teacher_timetable_day(teacher_db_id, current_date)
    timetable_one_day = TimetableOneDay(date=current_date, events=[])
    for study_event in study_events:
        event = StudyEvent(start_time=study_event.start_time,
                           end_time=study_event.end_time,
                           subject_name=study_event.subject_name,
                           subject_format=study_event.subject_format,
                           locations=study_event.locations,
                           contingent=study_event.groups,
                           is_canceled=study_event.is_canceled)
        timetable_one_day.events.append(event)
    timetable_info.append(timetable_one_day)
    return timetable_info


async def get_teacher_timetable_week_from_db(teacher_db_id: int, monday: date, sunday: date) -> List[TimetableOneDay]:
    timetable_info = []
    study_events = await loader.db.get_teacher_timetable_week(teacher_db_id, monday, sunday)
    i = 0
    while i < len(study_events):
        day = study_events[i].date
        timetable_one_day = TimetableOneDay(date=day, events=[])
        while i < len(study_events) and day == study_events[i].date:
            event = StudyEvent(start_time=study_events[i].start_time,
                               end_time=study_events[i].end_time,
                               subject_name=study_events[i].subject_name,
                               subject_format=study_events[i].subject_format,
                               locations=study_events[i].locations,
                               contingent=study_events[i].groups,
                               is_canceled=study_events[i].is_canceled)
            timetable_one_day.events.append(event)
            i += 1
        timetable_info.append(timetable_one_day)
    return timetable_info
