import enum
from dataclasses import dataclass
from typing import List, Callable, Optional
import requests
from bs4 import BeautifulSoup, Tag
from parser_service import ScheduleOptionsParser


class TypeOfWeek(enum.Enum):
    RED = 1
    BLUE = 2
    ANY = 3


@dataclass
class Para:
    name: str
    weekday: str
    type_of_para: str
    type_of_week: TypeOfWeek
    number: str
    teacher: str
    classroom: str


class ScheduleParser:
    BASE_URL = "https://guap.ru/rasp?"

    def __init__(self, group: str = "", teacher: str = "", cathedra: str = "", classroom: str = ""):
        self.group = group
        self.teacher = teacher
        self.cathedra = cathedra
        self.classroom = classroom
        self._schedule: List[Para] = []
        self.options = ScheduleOptionsParser('https://guap.ru/rasp').ID

    @property
    def schedule(self) -> List[Para]:
        return self._schedule

    def build_request_url(self) -> str:
        params = {
            'gr': self.options['selGroup'][self.group] if self.group != "" else "",
            'pr': self.options['selPrep'][self.teacher] if self.teacher != "" else "",
            'ch': self.options['selChair'][self.cathedra] if self.cathedra != "" else "",
            'ad': self.options['selRoom'][self.classroom] if self.classroom != "" else ""
        }
        query = "&".join(f"{key}={value}" for key, value in params.items() if value.strip())
        return f"{self.BASE_URL}{query}"

    @staticmethod
    def _get_type_of_week_from_class(_class: List[str]) -> TypeOfWeek:
        if not _class:
            return TypeOfWeek.ANY
        if _class[0].lower() == 'week1':
            return TypeOfWeek.RED
        if _class[0].lower() == 'week2':
            return TypeOfWeek.BLUE
        raise ValueError(f'Unknown type of week: {_class}')

    @staticmethod
    def _get_elements_between(
            elements: List[Tag],
            start_condition: Callable[[Tag], bool],
            end_condition: Callable[[Tag], bool]
    ) -> List[Tag]:
        start_index = None
        end_index = None

        for i, elem in enumerate(elements):
            if start_condition(elem) and start_index is None:
                start_index = i
            elif end_condition(elem) and start_index is not None:
                end_index = i
                break

        if start_index is None or end_index is None:
            return []
        return elements[start_index: end_index]

    def _parse_para_block(self, para_block: Tag, weekday: str, number: str) -> Optional[Para]:
        para_divs = list(para_block.find_all('div', recursive=False))
        if not para_divs:
            return None

        para_type_of_week = self._get_type_of_week_from_class(para_divs[0]['class'])
        para_info = list(para_divs[1].find_all('div', recursive=False))

        if len(para_info) < 3:
            return None

        para_type = para_info[0].text
        para_name = para_info[1].text

        additional_info = list(para_info[2].find_all('a', recursive=False))
        if len(additional_info) < 2:
            return None

        para_classroom = additional_info[0].text
        para_teacher = additional_info[1].text

        return Para(
            name=para_name,
            weekday=weekday,
            type_of_para=para_type,
            type_of_week=para_type_of_week,
            number=number,
            teacher=para_teacher,
            classroom=para_classroom
        )

    def parse(self) -> None:
        response = requests.get(self.build_request_url())
        page = BeautifulSoup(response.text, 'lxml')

        container = page.find('div', class_='container-xxl document').find_all(recursive=False)

        schedule_elements = self._get_elements_between(
            elements=list(container),
            start_condition=lambda item: item.name == 'h4',
            end_condition=lambda item: item.name == 'p'
        )

        weekday = None
        number = None

        for block in schedule_elements:
            if block.name == 'h4':
                weekday = block.text
            elif block.name == 'div':
                para = self._parse_para_block(block, weekday, number)
                if para:
                    self._schedule.append(para)
                else:
                    number = block.text


if __name__ == '__main__':
    parser = ScheduleParser(group='3235')
    parser.parse()
    print(parser.schedule)
