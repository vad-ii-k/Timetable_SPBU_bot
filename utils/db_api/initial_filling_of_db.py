import asyncio
import math
import aiohttp

from utils.tt_api import get_study_divisions, get_study_levels, get_groups


async def collecting_groups_info():
    program_ids = await collecting_program_ids()
    groups = []
    for program_id in program_ids:
        program_groups = await get_groups(program_id)
        if len(program_groups) != 0:
            groups.append(program_groups)
        print(program_groups)


async def collecting_program_ids() -> list:
    aliases = [item['Alias'] for item in (await get_study_divisions())]
    program_ids = []
    for alias in aliases:
        temp, response = await get_study_levels(alias)
        for level in response:
            program_combinatons = level['StudyProgramCombinations']
            for program_combinaton in program_combinatons:
                years = program_combinaton['AdmissionYears']
                for year in years:
                    program_ids.append(year['StudyProgramId'])
    return program_ids
