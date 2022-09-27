from tgbot.misc.states import UserType
from tgbot.services.timetable_api.timetable_api import get_schedule_from_tt


async def get_schedule(tt_id: int, user_type: UserType) -> str:
    response = await get_schedule_from_tt(tt_id=tt_id, user_type=user_type)
    info_about_events = response["Days"] if user_type == UserType.STUDENT else response["EducatorEventsDays"]
    return str(response)[:4096]
