from json import JSONEncoder

import requests
import json
import pandas as pd
import numpy as np

from oligoMass import molmassOligo as mmo
from datetime import datetime

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
        self.db_name = 'stock_oligolab_5.db'
        self.api_db_url = f'http://{self.db_IP}:{self.db_port}'
        self.oligo_map_id = -1
        self.oligo_id = -1
        self.pincode = ''

    def headers(self):
        return {'Authorization': f'Pincode {self.pincode}'}

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
        ret = requests.get(url, headers=self.headers())
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
            ret = requests.get(url, headers=self.headers())
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
                                                     'value_list':[json.dumps(map_data)]}), headers=self.headers())
            return ret.status_code
        return 404

    def sel_done(self, data, sel_rows):
        df = pd.DataFrame(data)
        for r in sel_rows:
            df.loc[df['#'] == r['#'], 'DONE'] = True
        return df.to_dict('records')

    def get_oligomaps_data(self):
        url = f'{self.api_db_url}/get_all_tab_data/{self.maps_db_name}/main_map'
        ret = requests.get(url, headers=self.headers())
        if ret.status_code == 200:
            out = []
            for r in ret.json():
                d = {}
                d['#'] = r[0]
                d['Map name'] = r[2]
                d['Synth number'] = r[3]
                d['Date'] = r[1]
                d['in progress'] = self.map_in_progress(r[4])
                d['map data'] = pd.DataFrame(json.loads(r[4]))
                out.append(d)
            return out
        else:
            return []

    def show_map_list_in_progress(self):
        total_maps = self.get_oligomaps_data()
        if len(total_maps) > 0:
            out = []
            for row in total_maps:
                df = row['map data']
                if df.shape[0] > 0:
                    if df[(df['DONE'] == True) | (df['Wasted'] == True)].shape[0] != df.shape[0]:
                        d = {}
                        d['#'] = row['#']
                        d['Map name'] = row['Map name']
                        d['Synth number'] = row['Synth number']
                        d['Date'] = row['Date']
                        d['in progress'] = row['in progress']
                        out.append(d)
            return out
        else:
            return []

    def send_lcms_data(self, json_data, selrows, maprows):
        df = pd.DataFrame(maprows)
        if self.oligo_map_id > -1 and len(selrows) > 0:
            self.oligo_id = selrows[0]['Order id']
            self.oligo_pos = selrows[0]['Position']

            json_data['map id'] = self.oligo_map_id
            json_data['Order id'] = self.oligo_id
            json_data['Position'] = self.oligo_pos

            file_name = f'{self.oligo_map_id}_{self.oligo_id}_{self.oligo_pos}'
            url = f'{self.api_db_url}/post_lcms_json_data/{file_name}'
            #ret = requests.post(url, json=json.dumps(json_data, cls=NumpyEncoder))
            #print(json_data)
            ret = requests.post(url, json=json.dumps(json_data), headers=self.headers())

            if ret.status_code == 200:
                df.loc[df['Position'] == self.oligo_pos, 'Done LCMS'] = True

            return ret, df.to_dict('records')

        return '', df.to_dict('records')

    def load_lcms_data(self, map_list_selection, map_selection):
        if (len(map_list_selection) > 0) and (len(map_selection) > 0):
            self.oligo_map_id = map_list_selection[0]['#']
            self.oligo_id = map_selection[0]['Order id']
            self.oligo_pos = map_selection[0]['Position']

            file_name = f'{self.oligo_map_id}_{self.oligo_id}_{self.oligo_pos}'
            url = f'{self.api_db_url}/get_lcms_json_data/{file_name}'
            ret = requests.get(url, headers=self.headers())

            return ret

    def add_data_to_purity_tab(self, mass_tags, row_index, rowdata):
        df = pd.DataFrame(rowdata)
        if self.oligo_id > -1:
            df.loc[df['Position'] == self.oligo_pos, 'Purity, %'] = round(float(mass_tags[row_index]['area%']), 0)
        return df.to_dict('records')

    def update_map_flags(self, type_flags, rowData, selrowData):

        if len(selrowData) == 0:
            index_list = list(pd.DataFrame(rowData)['#'])
        else:
            index_list = list(pd.DataFrame(selrowData)['#'])

        out = []
        for row in rowData:
                d = row.copy()
                if row['#'] in index_list:
                    if type_flags in list(row.keys()):
                        d[type_flags] = not d[type_flags]
                    else:
                        d[type_flags] = True
                out.append(d)
        return out

    def get_order_status(self, row):
        state_list = ['synth', 'sed', 'click', 'cart', 'hplc', 'paag', 'LCMS', 'subl']
        flag_list = []
        for state in state_list:
            flag_list.append(row[f'Do {state}'] == row[f'Done {state}'])
        status = 'synthesis'
        for i in range(8):
            if not flag_list[i]:
                if i < 3:
                    status = 'synthesis'
                elif i > 2 and i < 6:
                    status = 'purification'
                elif i == 7:
                    status = 'formulation'
                return status
            else:
                if i == 7:
                    status = 'finished'
                    return status
        return status


    def update_oligomap_status(self, rowData):
        if len(rowData) > 0:
            if 'map #' in list(rowData[0].keys()):
                for row in rowData:
                    if row['map #'] != '':
                        self.oligo_map_id = int(row['map #'])
                        print(f'MAP ID: {self.oligo_map_id}')
                        break
        if self.oligo_map_id > -1:
            out = []
            for row in rowData:
                out.append(row)
                #if not out[-1]['DONE']:
                out[-1]['Date'] = datetime.now().date().strftime('%d.%m.%Y')
                out[-1]['Status'] = self.get_order_status(row)
                if out[-1]['Status'] == 'finished':
                    out[-1]['DONE'] = True
                else:
                    out[-1]['DONE'] = False

            url = f"{self.api_db_url}/update_data/{self.maps_db_name}/main_map/{self.oligo_map_id}"
            r = requests.put(url,
                              json=json.dumps({
                                  'name_list': ['map_tab'],
                                  'value_list': [
                                      json.dumps(out)
                                  ]
                              })
                             , headers=self.headers())
            print(f'update status {self.oligo_map_id}: {r.status_code}')
            return out
        else:
            return rowData

    def update_order_status(self, rowData):
        if len(rowData) > 0:
            for row in rowData:
                order_id = row['Order id']
                order_date = row['Date']
                order_status = row['Status']

                url = f"{self.api_db_url}/update_data/{self.db_name}/orders_tab/{order_id}"
                r = requests.put(url,
                    json=json.dumps({
                        'name_list': ['output_date', 'status'],
                        'value_list': [order_date, order_status]
                    })
                , headers=self.headers())

    def setup_map_volumes(self, volume_input, map_rowdata, sel_map_rowdata):
        if len(sel_map_rowdata) == 0:
            index_list = list(pd.DataFrame(map_rowdata)['#'])
        else:
            index_list = list(pd.DataFrame(sel_map_rowdata)['#'])

        out = []
        for row in map_rowdata:
                d = row.copy()
                if row['#'] in index_list:
                    d['Vol, ml'] = float(volume_input)
                out.append(d)
        return out

    def check_pincode(self):
            url = f"{self.api_db_url}/get_keys_data/{self.db_name}/users/pin/{self.pincode}"
            r = requests.get(url, headers=self.headers())
            if r.status_code == 200:
                return True
            else:
                return False

    def add_new_modification(self, rowData):
        if self.check_pincode():
            out = []
            out.append({'code': '', 'mass': 0., 'ext_cf': 0, 'formula+': '', 'formula-': '', 'in_base': True})
            for row in rowData:
                out.append(row)
            return out
        else:
            return rowData

    def save_modification_table(self, rowData):
        if self.check_pincode():
            df = pd.DataFrame(rowData)
            #df = df[df['in_base'] == True]
            df.to_csv('external_mods.csv', index=False, sep='\t')
            df = pd.read_csv('external_mods.csv', sep='\t')
            return df.to_dict('records')
        else:
            return rowData


    def  print_pass(self, rowData):
        out_tab = []
        index_ = 1
        for row in rowData:
            o = mmo.oligoNASequence(row['Sequence'])
            d = {}
            d['#'] = index_
            index_ += 1
            d['Position'] = row['Position']
            d['Name'] = row['Name'] + f"  ({row['Synt number']}_{row['Position']})"
            d['Sequence'] = row['Sequence']
            d['Amount,_oe'] = int(round(row['Dens, oe/ml'] * row['Vol, ml'], 0))
            if o.getExtinction() > 0:
                d['Amount,_nmol'] = int(round(d['Amount,_oe'] * 1e6 / o.getExtinction(), 0))
            else:
                d['Amount,_nmol'] = 0.
            d['Desolving'] = int(d['Amount,_nmol'] * 10)

            d['Purification'] = row['Purif type']
            d['order_ID'] = row['Order id']
            try:
                d['Mass,_Da'] = round(o.getAvgMass(), 2)
            except:
                d['Mass,_Da'] = 'unknown modiff'
            d['Extinction'] = o.getExtinction()

            out_tab.append(d)

        return out_tab
