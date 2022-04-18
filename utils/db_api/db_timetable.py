from datetime import datetime, date

import loader


async def add_group_timetable_to_db(events: dict, tt_id: int):
    for event in events:
        subject: str = event.get("Subject")
        subject_name, subject_format = subject.rsplit(sep=", ", maxsplit=1)
        locations: str = event.get("LocationsDisplayText")
        db_subject = await loader.db.add_new_subject(subject_name, subject_format, locations)

        start: datetime = datetime.strptime(event.get("Start"), "%Y-%m-%dT%H:%M:%S")
        end: datetime = datetime.strptime(event.get("End"), "%Y-%m-%dT%H:%M:%S")
        event_date: date = start.date()
        educator: str = event.get("EducatorsDisplayText").rsplit(sep=", ", maxsplit=1)[0]
        is_cancelled: bool = event.get("IsCancelled")
        await loader.db.add_new_study_event(int(tt_id), db_subject.subject_id, event_date, start,
                                            end, educator, is_cancelled)
