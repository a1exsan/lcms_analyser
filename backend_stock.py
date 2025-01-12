import json

import pandas as pd
import datetime
import requests

class api_db_interface():

    def __init__(self, db_IP, db_port):
        self.db_IP = db_IP
        self.db_port = db_port
        self.api_db_url = f'http://{self.db_IP}:{self.db_port}'
        self.pincode = ''

    def headers(self):
        return {'Authorization': f'Pincode {self.pincode}'}

class stock_manager(api_db_interface):

    def __init__(self, db_IP, db_port):
        super().__init__(db_IP, db_port)

        self.db_name = 'stock_oligolab_5.db'
        self.strftime_format = "%Y-%m-%d"
        self.time_format = "%H:%M:%S"

    def get_remaining_stock(self, unicode):
        url = f"{self.api_db_url}/get_remaining_stock/{self.db_name}/{unicode}"
        input_ret = requests.get(url, headers=self.headers())
        try:
            return input_ret.json()
        except:
            return {'exist': 0.}


    def get_all_data_in_tab(self, tab_name):
        url = f'{self.api_db_url}/get_all_tab_data/{self.db_name}/{tab_name}'
        ret = requests.get(url, headers=self.headers())
        return ret.json()


    def show_main_tab_data(self, rates={}):
        rowData = self.get_all_data_in_tab('total_tab')

        main_tab = {
                '#': [],
                'Name': [],
                "units": [],
                'Unicode': [],
                "Description": [],
                'low limit': [],
                'Exist on stock': [],
                'E-L': [],
                'SUB': [],
                'last rate': [],
                'Exist/rate': []
            }

        #print(rowData)

        for i, row in enumerate(rowData):
            if row[2] in list(rates.keys()):
                if rates[row[2]][-2] == 0:
                    main_tab['last rate'].append(max(rates[row[2]]))
                    rate = max(rates[row[2]])
                else:
                    main_tab['last rate'].append(rates[row[2]][-2])
                    rate = rates[row[2]][-2]
            else:
                main_tab['last rate'].append(0.)
                rate = 0

            main_tab['SUB'].append(0.)
            main_tab['#'].append(row[0])
            main_tab['Name'].append(row[1])
            main_tab['units'].append(row[3])
            main_tab['Unicode'].append(row[2])
            main_tab['Description'].append(row[4])
            main_tab['low limit'].append(row[5])

            exist = self.get_remaining_stock(row[2])['exist']
            main_tab['Exist on stock'].append(exist)

            if rate == 0:
                main_tab['Exist/rate'].append(exist)
            else:
                main_tab['Exist/rate'].append(exist / rate)

            #print(row[2], exist, rate, main_tab['Exist/rate'][-1])

            if main_tab['low limit'][i] > 0:
                main_tab['E-L'].append(round((main_tab['Exist on stock'][i] - main_tab['low limit'][i]) * 100
                                       / main_tab['low limit'][i], 1))
            else:
                main_tab['E-L'].append(0)

        output_tab = {
            '#': [],
            'Name': [],
            "Amount": [],
            'Unicode': [],
            "Date": [],
            "Time": [],
            'User': []
        }

        input_tab = {
            '#': [],
            'Name': [],
            "Amount": [],
            'Unicode': [],
            "Date": [],
            "Time": [],
            'User': []
        }

        users = {
            '#': [],
            'Name': [],
            'Telegram id': [],
            'Status': []
        }

        for row in self.get_all_data_in_tab('users'):
            users['#'].append(row[0])
            users['Name'].append(row[1])
            users['Telegram id'].append(row[2])
            users['Status'].append(row[3])

        df_users = pd.DataFrame(users)

        for row in self.get_all_data_in_tab('output_tab'):
            output_tab['#'].append(row[0])
            output_tab['Name'].append(row[1])
            output_tab['Unicode'].append(row[2])
            output_tab['Amount'].append(row[3])
            output_tab['Date'].append(row[4])
            output_tab['Time'].append(row[5])
            output_tab['User'].append(df_users[df_users['Telegram id'] == row[6]]['Name'].max())

        for row in self.get_all_data_in_tab('input_tab'):
            input_tab['#'].append(row[0])
            input_tab['Name'].append(row[1])
            input_tab['Unicode'].append(row[2])
            input_tab['Amount'].append(row[3])
            input_tab['Date'].append(row[4])
            input_tab['Time'].append(row[5])
            input_tab['User'].append(df_users[df_users['Telegram id'] == row[6]]['Name'].max())

        return (pd.DataFrame(main_tab).to_dict('records'), pd.DataFrame(output_tab).to_dict('records'),
                pd.DataFrame(input_tab).to_dict('records'), pd.DataFrame(users).to_dict('records'))

    def update_tab(self, rowData):
        for row in rowData:
            url = f"{self.api_db_url}/update_data/{self.db_name}/total_tab/{row['#']}"
            ret = requests.put(url, json=json.dumps(
                {
                    'name_list': ['pos_name', 'unicode', 'units', 'description', 'lower_limit'],
                    'value_list': [row['Name'], row['Unicode'],
                                           row['units'], row['Description'],
                                           row['low limit']]
                }
            ), headers=self.headers())
        return self.show_main_tab_data()

    def add_row(self):
        url = f"{self.api_db_url}/insert_data/{self.db_name}/total_tab"
        r = requests.post(url,
                          json=json.dumps(
                              [
                                  'new', 'default', 'шт', 'default', '1'
                              ]
                          )
                          , headers=self.headers())
        return self.show_main_tab_data()

    def delete_rows(self, selrowdata):
        for row in selrowdata:
            url = f"{self.api_db_url}/delete_data/{self.db_name}/total_tab/{row['#']}"
            r = requests.delete(url, headers=self.headers())
        return self.show_main_tab_data()

    def substruct_from_stock(self, user_id, tab_name, rowdata):
        for row in rowdata:
            if row['SUB'] > 0:
                url = f"{self.api_db_url}/insert_data/{self.db_name}/{tab_name}"
                r = requests.post(url,
                json=json.dumps(
                        [
                        row['Name'], row['Unicode'], row['SUB'],
                        datetime.datetime.now().date().strftime(self.strftime_format),
                        datetime.datetime.now().time().strftime(self.time_format),
                        #user_id
                        self.get_user_id()
                        ]
                    )
                , headers=self.headers())
        return self.show_main_tab_data()

    def get_user_id(self):
        url = f"{self.api_db_url}/get_keys_data/{self.db_name}/users/pin/{self.pincode}"
        r = requests.get(url, headers=self.headers())
        return r.json()[0][2]
