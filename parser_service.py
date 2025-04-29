import requests
from bs4 import BeautifulSoup


class ScheduleOptionsParser:
    ID = {
        'selGroup': {},
        'selChair': {},
        'selPrep': {},
        'selRoom': {}
    }

    def __init__(self, schedule_url: str):
        response = requests.get(schedule_url)
        self.url = schedule_url
        self.parsing_page = BeautifulSoup(response.text, 'lxml')
        self.get_options()

    def parsing_options(self, options_id: str):
        options_list = self.parsing_page.find('select', id=options_id).find_all('option')
        name_list = [obj.text for obj in options_list]
        id_list = [obj['value'] for obj in options_list]
        return {group_name: group_id for (group_name, group_id) in zip(name_list, id_list)}

    def get_options(self):
        for idx in self.ID.keys():
            self.ID[idx] = self.parsing_options(idx)






if '__main__' == __name__:
    parser = ScheduleOptionsParser('https://guap.ru/rasp')
    print(parser.ID)
