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

from datetime import datetime, timedelta, timezone
import json
from typing import List, Tuple, Any

import certifi
import urllib3
from bs4 import BeautifulSoup

from .provider import Suburb, Municipality, Provider, Province, ProviderError, Stage


class AreaInfo:
    def __init__(self, /, **kwargs):
        province = kwargs.get("Province", {})
        self.province = Province(province.get("Id"))
        self.municipality = Municipality(**kwargs.get("Municipality", {}))
        self.suburb = Suburb(**kwargs.get("Suburb", {}), municipality=self.municipality.name, province=self.province.name)
        self.period = kwargs.get("Period")

    def __str__(self):
        return str(self.suburb)

    def __repr__(self):
        return f"AreaInfo({self.suburb}, {self.municipality}, {self.province})"


class Suburb(Suburb):
    def __init__(self, /, **kwargs):
        self.id = kwargs.get("Id", kwargs.get("id"))
        self.name = kwargs.get("Name", kwargs.get("name"))
        self.municipality = Municipality(name=kwargs.get("MunicipalityName"))
        self.province = Eskom.province_from_name(kwargs.get("ProvinceName"))
        self.total = kwargs.get("Total")

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"Suburb({self.id}, {self.name}, {self.municipality}, {self.province})"


class Municipality(Municipality):
    def __init__(self, /, **kwargs):
        self.id = kwargs.get("Value", kwargs.get("Id"))
        self.name = kwargs.get("Text", kwargs.get("Name", kwargs.get("name")))
        self.selected = kwargs.get("Selected")
        self.group = kwargs.get("Group")
        self.disabled = kwargs.get("Disabled")

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"Municipality({self.id}, {self.name}"


class Eskom(Provider):
    name = "Eskom"
    base_url = "https://loadshedding.eskom.co.za/LoadShedding"

    @classmethod
    def province_from_name(cls, name: str) -> Province:
        return Provider.province_from_name(name)

    @classmethod
    def stage_from_status(cls, status: str) -> Stage:
        return {
            "-1": Stage.UNKNOWN,
            "1": Stage.NO_LOAD_SHEDDING,
            "2": Stage.STAGE_1,
            "3": Stage.STAGE_2,
            "4": Stage.STAGE_3,
            "5": Stage.STAGE_4,
            "6": Stage.STAGE_5,
            "7": Stage.STAGE_6,
            "8": Stage.STAGE_7,
            "9": Stage.STAGE_8,
        }.get(status, Stage.UNKNOWN)

    @classmethod
    def call(cls, url: str) -> Any:
        try:
            retries = urllib3.Retry(total=3)
            with urllib3.PoolManager(retries=retries, ca_certs=certifi.where()) as conn:
                r = conn.request('GET', url)
                if r.status != 200:
                    raise urllib3.response.HTTPError(r.status)
                return r.data
        except Exception as e:
            raise ProviderError("Eskom is unavailable.") from e

    @classmethod
    def parse_schedule_data(cls, data: str) -> List[List]:
        try:
            schedule = []
            soup = BeautifulSoup(data, "html.parser")
            days_soup = soup.find_all("div", attrs={"class": "scheduleDay"})

            sast = timezone(timedelta(hours=+2), 'SAST')
            utc = timezone.utc
            now = datetime.now(sast)
            for day in days_soup:
                date_soup = day.find("div", attrs={"class": "dayMonth"})
                date_str = date_soup.get_text().strip()
                date = datetime.strptime(date_str, "%a, %d %b")
                date = date.replace(year=now.year)

                time_soup = day.find_all("a")
                for time_tag in time_soup:
                    start_str, end_str = time_tag.get_text().strip().split(" - ")
                    start = datetime.strptime(start_str, "%H:%M").replace(
                        year=date.year, month=date.month, day=date.day, second=0, microsecond=0, tzinfo=sast
                    ).astimezone(utc)
                    end = datetime.strptime(end_str, "%H:%M").replace(
                        year=date.year, month=date.month, day=date.day, second=0, microsecond=0, tzinfo=sast
                    ).astimezone(utc)
                    if end < start:
                        end = end + timedelta(days=1)
                    schedule.append([start.isoformat(), end.isoformat()])
        except Exception as e:
            raise ProviderError(f"Unable to parse schedule data.") from e
        else:
            return schedule

    @classmethod
    def parse_area_info_data(cls, data: str) -> AreaInfo:
        try:
            soup = BeautifulSoup(data, "html.parser")
            items = soup.find_all("div", attrs={"class": "areaInfoItem"})
            area_info = {
                "Province": {
                    "Id": int(items[0].find("input", attrs={"id": "provinceId"}).get('value').strip()),
                    "Name": items[0].find("input", attrs={"id": "province"}).get('value').strip(),
                },
                "Municipality": {
                    "Id": int(items[1].find("input", attrs={"id": "municipalityId"}).get('value').strip()),
                    "Name": items[1].find("input", attrs={"id": "municipality"}).get('value').strip(),
                },
                "Suburb": {
                    "Id": int(items[2].find("input", attrs={"id": "suburbId"}).get('value').strip()),
                    "Name": items[2].find("input", attrs={"id": "suburbName"}).get('value').strip(),
                },
                "Period": items[3].contents[2].strip().split("\xa0to\xa0"),
            }
        except Exception as e:
            raise ProviderError(f"Unable to parse area info data.") from e
        else:
            return AreaInfo(**area_info)

    def find_suburbs(self, search_text: str, max_results: int = 10) -> List[Suburb]:
        url = "{base_url}/FindSuburbs?searchText={search_text}&maxResults={max_results}".format(
            base_url=self.base_url,
            search_text=search_text,
            max_results=max_results,
        )
        data = Eskom.call(url)
        return json.loads(data, object_hook=lambda d: Suburb(**d))

    def get_municipalities(self, province: Province) -> List[Municipality]:
        url = "{base_url}/GetMunicipalities/?Id={province}".format(
            base_url=self.base_url,
            province=province.value,
        )
        data = Eskom.call(url)
        return json.loads(data, object_hook=lambda d: Municipality(**d))

    def get_schedule(self, province: Province, suburb: Suburb, stage: Stage) -> Tuple[tuple]:
        url = "{base_url}/GetScheduleM/{suburb_id}/{stage}/{province}/3252".format(
            base_url=self.base_url,
            suburb_id=suburb.id,
            province=province.value,
            stage=stage.value,
        )
        data = Eskom.call(url)
        return Eskom.parse_schedule_data(data)

    def get_schedule_area_info(self, suburb_id: int) -> AreaInfo:
        url = "{base_url}/GetScheduleAreaInfo/?Id={suburb_id}".format(
            base_url=self.base_url,
            suburb_id=suburb_id,
        )
        data = Eskom.call(url)
        return Eskom.parse_area_info_data(data)

    def get_stage(self) -> Stage:
        url = "{base_url}/GetStatus".format(
            base_url=self.base_url,
        )
        data = Eskom.call(url)
        return Eskom.stage_from_status(data.decode("utf-8"))
