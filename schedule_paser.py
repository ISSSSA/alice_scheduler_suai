import enum
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


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


def build_request_url(
        group: str = "",
        teacher: str = "",
        cathedra: str = "",
        classroom: str = "",
        # todo перенести в конфиг, не хардкодить
        base_url: str = "https://guap.ru/rasp?"
) -> str:
    params = {
        'gr': group,
        'pr': teacher,
        'ch': cathedra,
        'ad': classroom
    }
    query = "&".join(f"{key}={value}" for key, value in params.items() if value.strip())
    return f"{base_url}{query}"


def TypeOfWeek_from_class(_class: list) -> TypeOfWeek:
    if len(_class) == 0:
        return TypeOfWeek.ANY
    if _class[0].lower() == 'week1':
        return TypeOfWeek.RED
    if _class[0].lower() == 'week2':
        return TypeOfWeek.BLUE
    raise ValueError(f'Unknown type of week: {_class}')


def get_elements_between(list, start_condition, end_condition):
    start_index = None
    end_index = None

    for i, elem in enumerate(list):
        if start_condition(elem) and start_index is None:
            start_index = i
        elif end_condition(elem) and start_index is not None:
            end_index = i
            break

    if start_index is None or end_index is None:
        return []
    return list[start_index: end_index]


if '__main__' == __name__:
    response = requests.get(build_request_url(group='6427'))
    page = BeautifulSoup(response.text, 'lxml')

    container = page.find('div', class_='container-xxl document').find_all(recursive=False)

    schedule_elements = get_elements_between(
        list=list(container),
        start_condition=lambda item: item.name == 'h4',
        end_condition=lambda item: item.name == 'p'
    )

    schedule = []
    weekday = None
    number = None

    for block in schedule_elements:
        if block.name == 'h4':
            weekday = block.text
        elif block.name == 'div':
            para_block = list(block.find_all('div', recursive=False))
            if len(para_block) == 0:
                number = block.text
                continue
            para_type_of_week = TypeOfWeek_from_class(para_block[0]['class'])

            para_info = list(para_block[1].find_all('div', recursive=False))

            para_type = para_info[0].text
            para_name = para_info[1].text

            additional_info = list(para_info[2].find_all('a', recursive=False))

            para_classroom = additional_info[0].text
            para_teacher = additional_info[1].text

            schedule.append(Para(
                name=para_name,
                weekday=weekday,
                type_of_para=para_type,
                type_of_week=para_type_of_week,
                number=number,
                teacher=para_teacher,
                classroom=para_classroom
            ))

    print(schedule)