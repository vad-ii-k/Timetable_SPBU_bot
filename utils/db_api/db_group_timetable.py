from datetime import datetime, date, time
from dataclasses import dataclass
from typing import List

from tgbot import loader


@dataclass
class GroupEvent:
    start_time: time
    end_time: time
    subject_name: str
    subject_format: str
    locations: str
    educator: str
    is_canceled: bool


@dataclass
class GroupTimetableOneDay:
    date: date
    events: List[GroupEvent]


async def add_group_timetable_to_db(events: dict, tt_id: int):
    for event in events:
        subject: str = event.get("Subject")
        subject_name, subject_format = subject.rsplit(sep=", ", maxsplit=1) if subject.rfind(', ') != -1 else (subject, '—')
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


async def get_group_timetable_day_from_db(group_db_id: int, current_date: date) -> List[GroupTimetableOneDay]:
    timetable_info = []
    study_events = await loader.db.get_group_timetable_day(group_db_id, current_date)
    timetable_one_day = GroupTimetableOneDay(date=current_date, events=[])
    for study_event in study_events:
        subject = await loader.db.get_subject(study_event.subject_id)
        event = GroupEvent(start_time=study_event.start_time,
                           end_time=study_event.end_time,
                           subject_name=subject.subject_name,
                           subject_format=subject.subject_format,
                           locations=subject.locations,
                           educator=study_event.educator,
                           is_canceled=study_event.is_canceled)
        timetable_one_day.events.append(event)
    timetable_info.append(timetable_one_day)
    return timetable_info


async def get_group_timetable_week_from_db(group_db_id: int, monday: date, sunday: date) -> List[GroupTimetableOneDay]:
    timetable_info = []
    study_events = await loader.db.get_group_timetable_week(group_db_id, monday, sunday)
    i = 0
    while i < len(study_events):
        day = study_events[i].date
        timetable_one_day = GroupTimetableOneDay(date=day, events=[])
        while i < len(study_events) and day == study_events[i].date:
            subject = await loader.db.get_subject(study_events[i].subject_id)
            event = GroupEvent(start_time=study_events[i].start_time,
                               end_time=study_events[i].end_time,
                               subject_name=subject.subject_name,
                               subject_format=subject.subject_format,
                               locations=subject.locations,
                               educator=study_events[i].educator,
                               is_canceled=study_events[i].is_canceled)
            timetable_one_day.events.append(event)
            i += 1
        timetable_info.append(timetable_one_day)
    return timetable_info
