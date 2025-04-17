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
    number: int
    teacher: str
    classroom: str


def build_request_url(group: str, teacher: str, cathedra: str, classroom: str) -> str:
    # todo перенести в конфиг, не хардкодить
    url = 'https://guap.ru/rasp?'

    if group.strip() != '':
        url += f'gr={group}&'
    if teacher.strip() != '':
        url += f'pr={teacher}&'
    if cathedra.strip() != '':
        url += f'ch={cathedra}&'
    if classroom.strip() != '':
        url += f'ad={classroom}&'

    return url


def TypeOfWeek_from_class(_class: list) -> TypeOfWeek:
    if len(_class) == 0:
        return TypeOfWeek.ANY
    if _class[0].lower() == 'week1':
        return TypeOfWeek.RED
    if _class[0].lower() == 'week2':
        return TypeOfWeek.BLUE
    raise ValueError(f'Unknown type of week: {_class}')


if '__main__' == __name__:
    print(build_request_url('6427', '', '', ''))
    response = requests.get(build_request_url('6427', '', '', ''))
    page = BeautifulSoup(response.text, 'lxml')

    elems = page.find('div', class_='container-xxl document').find_all(recursive=False)

    in_schedule = False
    buffer = []
    for block in elems:
        if block.name == 'h4':
            if in_schedule:
                buffer.clear()
            in_schedule = True
        if block.name == 'p':
            in_schedule = False
            break

        if in_schedule and block.name == 'div':
            para_block = list(block.find_all('div', recursive=False))
            if len(para_block) == 0:
                continue

            para_type_of_week = TypeOfWeek_from_class(para_block[0]['class'])

            para_info = list(para_block[1].find_all('div', recursive=False))

            para_type = para_info[0].text
            para_name = para_info[1].text

            additional_info = list(para_info[2].find_all('a', recursive=False))

            para_classroom = additional_info[0].text
            para_teacher = additional_info[1].text

            para = Para(name=para_name, weekday='todo, делать буфферы понедельные', type_of_para=para_type,
                 type_of_week=para_type_of_week, number=-1, teacher=para_teacher, classroom=para_classroom)
            print(para)
