from datetime import datetime, date, time
from dataclasses import dataclass
from typing import List

from tgbot import loader


@dataclass
class TeacherEvent:
    start_time: time
    end_time: time
    subject_name: str
    subject_format: str
    locations: str
    groups: str
    is_canceled: bool


@dataclass
class TeacherTimetableOneDay:
    date: date
    events: List[TeacherEvent]


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


async def get_teacher_timetable_day_from_db(teacher_db_id: int, current_date: date) -> List[TeacherTimetableOneDay]:
    timetable_info = []
    study_events = await loader.db.get_teacher_timetable_day(teacher_db_id, current_date)
    timetable_one_day = TeacherTimetableOneDay(date=current_date, events=[])
    for study_event in study_events:
        subject = await loader.db.get_subject(study_event.subject_id)
        event = TeacherEvent(start_time=study_event.start_time,
                             end_time=study_event.end_time,
                             subject_name=subject.subject_name,
                             subject_format=subject.subject_format,
                             locations=subject.locations,
                             groups=study_event.groups,
                             is_canceled=study_event.is_canceled)
        timetable_one_day.events.append(event)
    timetable_info.append(timetable_one_day)
    return timetable_info


async def get_teacher_timetable_week_from_db(teacher_db_id: int, monday: date, sunday: date)\
        -> List[TeacherTimetableOneDay]:
    timetable_info = []
    study_events = await loader.db.get_teacher_timetable_week(teacher_db_id, monday, sunday)
    i = 0
    while i < len(study_events):
        day = study_events[i].date
        timetable_one_day = TeacherTimetableOneDay(date=day, events=[])
        while i < len(study_events) and day == study_events[i].date:
            subject = await loader.db.get_subject(study_events[i].subject_id)
            event = TeacherEvent(start_time=study_events[i].start_time,
                                 end_time=study_events[i].end_time,
                                 subject_name=subject.subject_name,
                                 subject_format=subject.subject_format,
                                 locations=subject.locations,
                                 groups=study_events[i].groups,
                                 is_canceled=study_events[i].is_canceled)
            timetable_one_day.events.append(event)
            i += 1
        timetable_info.append(timetable_one_day)
    return timetable_info
