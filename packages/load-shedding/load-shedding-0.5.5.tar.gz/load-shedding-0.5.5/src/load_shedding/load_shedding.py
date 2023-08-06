#      A python library for getting Load Shedding schedules.
#      Copyright (C) 2021  Werner Pieterson
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
import errno
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Final

from load_shedding.providers import eskom
from load_shedding.providers.eskom import Province, Stage, Suburb, Provider, ProviderError

CACHE_TTL: Final = 86400


class StageError(Exception):
    pass


def get_stage(provider: Provider) -> Stage:
    try:
        stage = provider.get_stage()
    except ProviderError as e:
        raise StageError(f"Unable to get stage from {provider.name}") from e
    return stage


def get_schedule(provider: Provider, province: Province, suburb: Suburb, stage: Stage = None, cached: bool = True) -> List: # Dict[Stage, list]:
    now = datetime.now(timezone.utc)
    try:
        os.makedirs('.cache')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if stage in [None, Stage.UNKNOWN]:
        stage = get_stage(provider)

    if stage in [None, Stage.UNKNOWN, Stage.NO_LOAD_SHEDDING]:
        raise StageError(f"{Stage.NO_LOAD_SHEDDING}")

    cached_schedules = {}
    cached_schedule = []
    try:
        cache_file = ".cache/{suburb_id}.json".format(suburb_id=suburb.id)
        with open(cache_file, "r") as cache:
            for k, v in json.loads(cache.read()).items():
                cached_schedules[Stage(int(k)).value] = v

            cached_schedule = cached_schedules.get(stage.value, {})

        if not isinstance(cached_schedule, dict) or len(cached_schedule) == 0:
            """ Upgrade from previous list """
            cached = False

        if cached and cached_schedule:
            updated_at = datetime.fromisoformat(cached_schedule.get("updated_at", None))

            if (now - updated_at).seconds < CACHE_TTL:
                return cached_schedule.get("schedule", {})
    except FileNotFoundError as e:
        logging.log(logging.DEBUG, "Unable to get schedule from cache. {e}".format(e=e))

    try:
        schedule = provider.get_schedule(province=province, suburb=suburb, stage=stage)
    except ProviderError as e:
        logging.log(logging.DEBUG, "Unable to get schedule from {provider.name}. {e}".format(provider=provider, e=e))
        if cached_schedule:
            return cached_schedule  # best effort
        raise
    else:
        cache_file = ".cache/{suburb_id}.json".format(suburb_id=suburb.id)
        with open(cache_file, "w") as cache:
            cached_schedules[stage.value] = {
                "updated_at": str(now),
                "schedule": schedule,
            }
            cache.write(json.dumps(cached_schedules))
        return schedule


def list_to_dict(schedule: list) -> Dict:
    schedule_dict = {}
    now = datetime.now(timezone.utc)
    for item in schedule:
        start = datetime.fromisoformat(item[0])
        end = datetime.fromisoformat(item[1])

    schedule_dict[start.strftime("%Y-%m-%d")] = (
        start.replace(second=now.second).strftime("%H:%M"),
        end.replace(second=now.second).strftime("%H:%M"),
    )
    return schedule_dict


def get_providers() -> List[Provider]:
    return [eskom.Eskom]
