""" Module for getting bot statistics """
import csv
from dataclasses import dataclass
from datetime import date, time


@dataclass(slots=True, frozen=True)
class UserStatistics:
    """ Dataclass for user statistics """
    username: str
    start_date: date
    schedule_name: str | None
    daily_summary: time | None
    schedule_view_is_picture: bool
    language: str


async def writing_statistics_to_csv(full_statistics: list[UserStatistics]) -> None:
    """
    Writing statistics to a csv file
    :param full_statistics:
    """
    with open('data/statistics.csv', 'w', encoding='utf-8', newline='') as csvfile:
        dict_writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames=[
            "Username", "Start date", "Schedule name", "Daily summary time", "Default schedule view", "Language"
        ])
        dict_writer.writeheader()

        writer = csv.writer(csvfile, delimiter='\t')
        for user in full_statistics:
            writer.writerow([
                user.username,
                user.start_date,
                user.schedule_name,
                user.daily_summary,
                'image' if user.schedule_view_is_picture else 'text',
                user.language
            ])