from dataclasses import dataclass
from datetime import datetime, date, time
from typing import List, Dict

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


async def add_timetable_to_db(
    events: List[Dict[str, str | bool]], tt_id: int, user_type: str, full_name: str = None
) -> None:
    for event in events:
        subject: str = event.get("Subject")
        subject_name, subject_format = (
            subject.rsplit(sep=", ", maxsplit=1)
            if subject.rfind(", ") != -1
            else (subject, "—")
        )
        locations: str = event.get("LocationsDisplayText")
        db_subject = await loader.db.add_new_subject(subject_name, subject_format, locations)

        start: datetime = datetime.strptime(event.get("Start"), "%Y-%m-%dT%H:%M:%S")
        end: datetime = datetime.strptime(event.get("End"), "%Y-%m-%dT%H:%M:%S")
        event_date: date = start.date()
        is_cancelled: bool = event.get("IsCancelled")

        if user_type == "student":
            educator: str = "".join(educator.rsplit(sep=", ", maxsplit=1)[0] + ", "
                                    for educator in event.get("EducatorsDisplayText").split(sep=";")
                                    )[:-2]
            await loader.db.add_new_group_study_event(
                int(tt_id),
                db_subject.subject_id,
                event_date,
                start,
                end,
                educator,
                is_cancelled,
            )
        else:
            groups: str = event.get("ContingentUnitName")
            await loader.db.add_new_teacher_study_event(
                int(tt_id),
                full_name,
                db_subject.subject_id,
                event_date,
                start,
                end,
                groups,
                is_cancelled,
            )


async def get_timetable_day_from_db(
        db_id: int, current_date: date, user_type: str
) -> List[TimetableOneDay]:
    timetable_info = []
    if user_type == "student":
        study_events = await loader.db.get_group_timetable_day(db_id, current_date)
    else:
        study_events = await loader.db.get_teacher_timetable_day(db_id, current_date)
    timetable_one_day = TimetableOneDay(date=current_date, events=[])
    for study_event in study_events:
        event = StudyEvent(
            start_time=study_event.start_time,
            end_time=study_event.end_time,
            subject_name=study_event.subject_name,
            subject_format=study_event.subject_format,
            locations=study_event.locations,
            contingent=study_event.educator
            if user_type == "student"
            else study_event.groups,
            is_canceled=study_event.is_canceled,
        )
        timetable_one_day.events.append(event)
    timetable_info.append(timetable_one_day)
    return timetable_info


async def get_timetable_week_from_db(
        db_id: int, monday: date, sunday: date, user_type: str
) -> List[TimetableOneDay]:
    timetable_info = []
    if user_type == "student":
        study_events = await loader.db.get_group_timetable_week(db_id, monday, sunday)
    else:
        study_events = await loader.db.get_teacher_timetable_week(db_id, monday, sunday)
    i = 0
    while i < len(study_events):
        day = study_events[i].date
        timetable_one_day = TimetableOneDay(date=day, events=[])
        while i < len(study_events) and day == study_events[i].date:
            event = StudyEvent(
                start_time=study_events[i].start_time,
                end_time=study_events[i].end_time,
                subject_name=study_events[i].subject_name,
                subject_format=study_events[i].subject_format,
                locations=study_events[i].locations,
                contingent=study_events[i].educator
                if user_type == "student"
                else study_events[i].groups,
                is_canceled=study_events[i].is_canceled,
            )
            timetable_one_day.events.append(event)
            i += 1
        timetable_info.append(timetable_one_day)
    return timetable_info
