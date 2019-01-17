# -*- coding: utf-8 -*-

import requests
import re
import json
from bs4 import BeautifulSoup


class WebScrapper:

    def __init__(self):
        self.session = requests.Session()
        self.link_main = ''
        self.login = ''
        self.password = ''
        self.limit = '20'
        self.offset = '0'
        self.more = '0'

    # get table data from site
    def get_table_data(self, html, table_class):
        try:
            soup = BeautifulSoup(html, 'lxml')
            data = soup.find('table', class_=table_class).find('tbody').find_all('tr')
            client_list = []
            for tr in data:
                client = {}
                tds = tr.find_all('td')
                user_id = tr.get('id').split('item-')[1]
                user_name = tds[1].find('div', class_='line-name').find('a').text
                user_phone = self.trim_string(tds[1].find('div', class_='line-phone').text)
                last_visit = self.trim_string(tds[3].text)
                user_master = self.get_master(user_id)
                if len(last_visit) > 10:
                    last_visit = last_visit[:10]
                client['id'] = user_id
                client['name'] = user_name
                client['phone'] = user_phone
                client['last_visit'] = last_visit
                client['master'] = user_master

                client_list.append(client)

            return client_list
        except Exception as e:
            print(e)

    # remove whitespace, \n, \r
    @staticmethod
    def trim_string(string):
        result_str = re.sub("^\s+|\n|\r|\s|\s+$", '', string)

        return result_str

    # export data from site by type
    def get_export_data(self, type_='csv'):
        try:
            file_csv = self.session.get('{}&type={}'.format(link_2_export, type_))
            file_csv_list = file_csv.text.split('\n')

            return file_csv_list
        except Exception as e:
            print(e)

    # getting master to do the work for current client
    def get_master(self, user_id):
        try:
            param = {'tabs': True}
            client_master = self.session.post(link_2_client_history + user_id + '/?tab=history', data=param,
                                              headers={'X-Requested-With': 'XMLHttpRequest'})
            html = json.loads(client_master.text)['html']
            soup = BeautifulSoup(html, 'lxml')
            td = soup.find('table', class_='table').find('tbody').find('tr').find('td', class_='username')
            if td:
                return td.text
            return ''
        except Exception as e:
            print(e)

    # getting schedule all masters
    def get_master_schedule(self):
        try:
            schedule = self.session.get(link_2_masters_schedule)
            html = schedule.text
            soup = BeautifulSoup(html, 'lxml')
            rows = soup.find('div', class_='sch_sheet').find_all('div', class_='sch_sheet--row')

            return rows
        except Exception as e:
            print(e)

    # start for web scrapping
    def parse(self, link_2_login):
        params = {'login': self.login, 'password': self.password}
        self.session.post(link_2_login, data=params)
        clients = self.session.get(link_2_clients+'&limit='+self.limit+'&offset='+self.offset+'&more='+self.more)
        clients_data = self.get_table_data(clients.text, table_class='table')
        masters_schedule = self.get_master_schedule()

        return clients_data, masters_schedule

    def main(self):
        self.parse(self.link_main)


if __name__ == '__main__':
    scrapper = WebScrapper()
    scrapper.link_main = '<link_main>'
    scrapper.login = '<login>'
    scrapper.password = '<password>'
    scrapper.main()
