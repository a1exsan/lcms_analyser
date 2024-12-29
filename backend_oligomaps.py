from json import JSONEncoder

import requests
import json
import pandas as pd
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class oligomaps_local_db():

    def __init__(self, db_IP, db_port):
        self.db_IP = db_IP
        self.db_port = db_port
        self.maps_db_name = 'asm2000_map_1.db'
        self.api_db_url = f'http://{self.db_IP}:{self.db_port}'
        self.oligo_map_id = -1
        self.oligo_id = -1

    def map_in_progress(self, mapdata):
        map = json.loads(mapdata)
        df = pd.DataFrame(map)
        try:
            ctrl = df.shape[0] != df[df['Status'] == 'finished'].shape[0]
        except:
            ctrl = False
        return ctrl

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
                d['in progress'] = self.map_in_progress(r[4])
                out.append(d)
            return out
        else:
            return []

    def load_oligomap(self, seldata):
        if len(seldata) > 0:
            url = f"{self.api_db_url}/get_keys_data/{self.maps_db_name}/main_map/id/{seldata[0]['#']}"
            ret = requests.get(url)
            if ret.status_code == 200:
                self.oligo_map_id = seldata[0]['#']
                return json.loads(ret.json()[0][4])
            else:
                self.oligo_map_id = -1
                return []

    def save_map(self, map_data):
        if self.oligo_map_id > -1:
            url = f'{self.api_db_url}/update_data/{self.maps_db_name}/main_map/{self.oligo_map_id}'
            ret = requests.put(url, json=json.dumps({'name_list':['map_tab'],
                                                     'value_list':[json.dumps(map_data)]}))
            return ret.status_code
        return 404

    def sel_done(self, data, sel_rows):
        df = pd.DataFrame(data)
        for r in sel_rows:
            df.loc[df['#'] == r['#'], 'DONE'] = True
        return df.to_dict('records')

    def show_map_list_in_progress(self):
        maps = self.get_oligomaps()
        df = pd.DataFrame(maps)
        return df[df['in progress'] == True].to_dict('records')

    def send_lcms_data(self, json_data, selrows):
        if self.oligo_map_id > -1 and len(selrows) > 0:
            self.oligo_id = selrows[0]['Order id']
            self.oligo_pos = selrows[0]['Position']

            json_data['map id'] = self.oligo_map_id
            json_data['Order id'] = self.oligo_id
            json_data['Position'] = self.oligo_pos

            file_name = f'{self.oligo_map_id}_{self.oligo_id}_{self.oligo_pos}'
            url = f'{self.api_db_url}/post_lcms_json_data/{file_name}'
            ret = requests.post(url, json=json.dumps(json_data, cls=NumpyEncoder))
            return ret

        return 404