import requests
import json
import pandas as pd

class oligomaps_local_db():

    def __init__(self, db_IP, db_port):
        self.db_IP = db_IP
        self.db_port = db_port
        self.maps_db_name = 'asm2000_map_1.db'
        self.api_db_url = f'http://{self.db_IP}:{self.db_port}'

    def get_oligomaps(self):
        url = f'{self.api_db_url}/get_all_tab_data/{self.maps_db_name}/main_map'
        ret = requests.get(url)
        if ret.status_code == 200:
            out = []
            for r in ret.json():
                d = {}
                d['#'] = r[0]
                d['Map name'] = r[2]
                d['Synth number'] = r[3]
                d['Date'] = r[1]
                out.append(d)
            return out
        else:
            return []

    def load_oligomap(self, seldata):
        if len(seldata) > 0:
            url = f"{self.api_db_url}/get_keys_data/{self.maps_db_name}/main_map/id/{seldata[0]['#']}"
            ret = requests.get(url)
            if ret.status_code == 200:
                return json.loads(ret.json()[0][4])
            else:
                return []