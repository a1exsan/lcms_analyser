import mzdatapy
from tqdm import tqdm
import numpy as np
import pandas as pd
import lcms_db as db
from datetime import datetime
from oligoMass import molmassOligo as mmo
import json
import mz_oligo_identify as mzoi
import pickle

def substract_bkg(data, bkg, treshold=3000, rt_min=50, rt_max=1500):
    ret = []

    mz_list = [i for i, f in enumerate(bkg) if f >= treshold]

    for d in tqdm(data):
        if not (int(round(d[1], 0)) in mz_list):
            if d[0] >= rt_min and d[0] <= rt_max:
                ret.append(d)

    return np.array(ret)

def get_intensity_map(data, low_treshold=1000, param=3): #mod
    max_mz = int(round(max(data[:, 1])*param, 0))
    max_t = int(round(max(data[:, 0]), 0))
    out = [[0. for t in range(0, max_t + 10)] for mz in range(0, max_mz + 10)]

    for d in data:
        if d[2] >= low_treshold:
            mz, t = int(round(d[1]*param, 0)), int(round(d[0], 0))
            out[mz][t] = d[2]
    return out

def find_neighbor(mz, t, map, param=3): #mod
    count = 0
    mz, t = int(round(mz*param, 0)), int(round(t, 0))
    for i in range(-1, 2):
        for j in range(-1, 2):
            if map[mz + i][t + j] > 0:
                count += 1
    return count * 100 / 9

def find_inner_points(data, map, neighbor_treshold=60, param=3):
    out = []

    for d in data:
        if find_neighbor(d[1], d[0], map, param=param) >= neighbor_treshold:
            out.append(d)

    return np.array(out)

class oligo_properties():

    def __init__(self, sequence):
        self.seq = sequence
        self.oligo = mmo.oligoNASequence(self.seq)

    def get_props_dict(self):
        d = {}
        d['Mol Mass, Da:'] = round(self.oligo.getAvgMass(), 2)
        d['Extinction, OE/mol:'] = self.oligo.getExtinction()
        return d

    def __call__(self, *args, **kwargs):
        return self.get_props_dict()

class mzSpecDeconv():
    def __init__(self, mz_array, int_array, is_positive=False):
        self.data = pd.DataFrame({'mz': mz_array, 'intens': int_array,
                                  'class': np.zeros(mz_array.shape[0]),
                                  'mass': np.zeros(mz_array.shape[0])})
        self.is_positive = is_positive

    def __clusterize(self, data):

        clusters = []
        clusters.append([list(data.loc[0])])
        for index in range(1, data.shape[0]):
            finded = False
            for cl_index in range(len(clusters)):
                for mz_index in range(len(clusters[len(clusters) - cl_index - 1])):
                    mz_cl = clusters[len(clusters) - cl_index - 1][mz_index][0]
                    mz = data['mz'].loc[index]
                    if abs(mz - mz_cl) <= 1.05:
                        finded = True
                        clusters[len(clusters) - cl_index - 1].append(list(data.loc[index]))
                        data['class'].loc[index] = len(clusters) - cl_index - 1
                        break
                if finded:
                    break
            if not finded:
                clusters.append([list(data.loc[index])])
                data['class'].loc[index] = len(clusters) - 1

        return data

    def __clusterize_2(self, data):
        data['class'] = round(data['mz'], 0)
        return data

    def __compute_mass(self, data):

        classes = list(set(data['class']))
        data['charge'] = np.zeros(data['mz'].shape[0])
        data['mass'] = np.ones(data['mz'].shape[0])

        #print(data[data['class']==0.])

        if self.is_positive:
            sign = -1
        else:
            sign = 1

        for cl in classes:
            df = data[data['class'] == cl]
            if df.shape[0] > 3:
                df = df.sort_values(by='mz', ascending=False)
                #charge = round(1 / abs(df['mz'].values[0] - df['mz'].values[1]), 0)

                diff = pd.DataFrame(df['mz'])
                diff['diff'] = df['mz'].diff(periods=1)
                diff.dropna(inplace=True)
                diff = diff[diff['diff'] != 0]
                diff['charge'] = [abs(round(1/z, 0)) for z in diff['diff']]
                charge = diff['charge'].value_counts().idxmax()

                r_int = df['intens'] / df['intens'].sum()
                masses = df['mz'] * charge + sign * charge
                avg_mass = (masses * r_int).sum()

                data.loc[data['class'] == cl, 'charge'] = charge
                data.loc[data['class'] == cl, 'mass'] = avg_mass

        data['mono_mass'] = data['mz'] * data['charge'] + sign * data['charge']
        data = data[data['charge'] > 0]

        return data


    def deconvolute(self):
        self._data = self.data.sort_values(by='intens', ascending=False)
        self._data = self._data.reset_index()
        self._data = self._data.drop(['index'], axis=1)

        self._data = self.__clusterize(self._data)
        self._data = self.__compute_mass(self._data)

        #print(self._data)
        return self._data

    def deconvolute_2(self):
        self._data = self.data.sort_values(by='mz', ascending=True)
        self._data = self._data.reset_index()
        self._data = self._data.drop(['index'], axis=1)

        self._data = self.__clusterize_2(self._data)
        self._data = self.__compute_mass(self._data)

        #print(self._data)
        return self._data

    @staticmethod
    def drop_by_charge(data, max_charge=10):
        data = data[data['charge'] <= max_charge]
        return data

class oligosDeconvolution():
    def __init__(self, rt, mz, intens, is_positive=False, max_charge=10):
        rt = [round(i, 0) for i in rt]
        self.data = pd.DataFrame({'rt': rt, 'mz': mz, 'intens': intens})
        self.is_positive = is_positive
        self.max_charge = max_charge
        self.deconv_fast = True

    def deconvolute(self):
        rt_list = list(set(self.data['rt']))
        sum_data = np.array([])
        for rt in tqdm(rt_list, desc='Deconvolution:'):
            df = self.data[self.data['rt'] == rt]
            deconv = mzSpecDeconv(df['mz'], df['intens'], is_positive=self.is_positive)

            if self.deconv_fast:
                data = deconv.deconvolute_2()
            else:
                data = deconv.deconvolute()

            data = deconv.drop_by_charge(data, self.max_charge)
            data['rt'] = rt * np.ones(data['mz'].shape[0])

            if sum_data.shape[0] == 0:
                sum_data = data
            else:
                if data.shape[0] > 0:
                    sum_data = pd.concat([sum_data, data])

        sum_data = sum_data.sort_values(by='intens', ascending=False)
        sum_data = sum_data.reset_index()
        sum_data = sum_data.drop(['index'], axis=1)
        return sum_data

    @staticmethod
    def drop_data(data, mass_max, mass_min, rt_min, rt_max):
        df = data[data['mass'] <= mass_max]
        df = df[df['mass'] >= mass_min]
        df = df[df['rt'] <= rt_max]
        df = df[df['rt'] >= rt_min]
        return data.drop(list(df.index))

    @staticmethod
    def rt_filtration(data, rt_min, rt_max):
        df = data[data['rt'] <= rt_max]
        df = df[df['rt'] >= rt_min]
        return df
        
class mzdataBuilder():

    def __init__(self):
        self.fileName = ''
        self.int_treshold = 1000
        self.max_mz = 3200
        self.rt_left = 100
        self.rt_interval = [100, 1500]
        self.bkg_treshold = 1000
        self.init_data = np.array([[0, 0, 0]])
        self.new_file = False
        self.polish_param = 4
        self.delta_mass_treshold = 2
        self.selected_mass_points = []
        self.selected_mz_points = []
        self.mass_tags = []
        self.selected_tag_row = 0
        self.selected_db_tab_row = 0
        self.deconv_fast = True
        self.mz_tags = []
        self.deconv_data = pd.DataFrame()
        self.neighbor_treshold = 60
        self.low_intens_treshold = 1000
        self.bkg_polish_count = 1
        self.selected_mz_df = pd.DataFrame({})
        self.db_on = False
        self.db_admin = db.lcms_db_admin('oligo_lcms_0.db')

    def lcms_data_loading(self, data):
        self.mass_tags = data['mass_tags']
        self.mz_tags = data['mz_tags']

        df = pd.DataFrame(data['init_data'])
        self.init_data = np.array([[rt, mz, intens] for rt, mz, intens in zip(df['rt'], df['mz'], df['intens'])])
        self.data = np.array([[rt, mz, intens] for rt, mz, intens in zip(df['rt'], df['mz'], df['intens'])])
        #print(self.init_data)
        self.deconv_data = pd.DataFrame(data['deconv_data'])

        return f"sample position: {data['Position']}; order id: {data['Order id']}"

    def to_dict(self):
        d = {}
        #d['init_data'] = self.init_data
        d['init_data'] = pd.DataFrame({
            'rt': self.init_data[:, 0],
            'mz': self.init_data[:, 1],
            'intens': self.init_data[:, 2],
        }).to_dict('records')
        d['deconv_data'] = self.deconv_data.to_dict('records')
        d['mass_tags'] = self.text_to_mass_tags(self.mass_tags_to_text())
        d['mz_tags'] = self.mz_tags
        return d

    def to_pickle(self, fn):
        with open(fn, 'wb') as f:
            pickle.dump(self, f)

    def load_data(self, fn='', from_string='', description='', row_index=-1):
        if self.fileName != fn:
            #print(row_index)
            self.mass_tags = []
            self.fileName = fn
            self.new_file = True
            if self.fileName != '':
                spec = mzdatapy.mzdata(self.fileName, from_string=from_string)
                self.init_data, self.bkg = spec.mzdata2tab(int_treshold=self.int_treshold,
                                                       max_mz=self.max_mz,
                                                       rt_left=self.rt_interval[0])
            self.db_admin.get_flags(filecontent=from_string, row_index=row_index)
            self.db_admin.insert_init_spectra_2(self.fileName, from_string, datetime.now(), description)
            self.load_from_db_2()
        else:
            self.new_file = False
            self.db_admin.get_flags(filecontent=from_string, row_index=row_index)
            self.db_admin.insert_init_spectra_2(self.fileName, from_string, datetime.now(), description)
            self.load_from_db_2()

    def load_from_db(self):
        db_data = self.db_admin.extract_data_by_flags()
        if self.db_admin.flags['polishing'] > -1:
            self.data = self.string_to_data(db_data['polishing'])
            #print(self.data[:, 0])
            self.set_polishing_params(db_data['polish_params'])

            if self.db_admin.flags['deconvolution'] > -1:
                self.deconv_data = self.text_to_dataframe(db_data['deconvolution'])
                self.deconv = oligosDeconvolution(self.data[:, 0], self.data[:, 1], self.data[:, 2],
                                                  is_positive=db_data['deconv_params']['is_positive'])
                self.deconv.max_charge = db_data['deconv_params']['max_charge']

    def load_from_db_2(self):
        db_data = self.db_admin.extract_data_by_flags()
        if self.db_admin.flags['polishing'] > -1:
            self.data = self.string_to_data(db_data['polishing'])
            #print(self.data[:, 0])
            self.set_polishing_params(db_data['polish_params'])

            if self.db_admin.flags['deconvolution'] > -1:
                self.deconv_data = self.text_to_dataframe(db_data['deconvolution'])
                self.deconv = oligosDeconvolution(self.data[:, 0], self.data[:, 1], self.data[:, 2],
                                                  is_positive=db_data['deconv_params']['is_positive'])
                self.deconv.max_charge = db_data['deconv_params']['max_charge']

                if self.db_admin.flags['tagging'] > -1:
                    self.mass_tags = self.text_to_mass_tags(db_data['deconv_tags'])

    def substract_bkg(self):
        self.data = substract_bkg(self.init_data, self.bkg, treshold=self.bkg_treshold,
                                  rt_min=self.rt_interval[0], rt_max=self.rt_interval[1])

    def get_init_x(self):
        return self.init_data[:, 0]

    def get_init_y(self):
        return self.init_data[:, 1]

    def get_init_z(self):
        return self.init_data[:, 2]

    def get_x(self):
        return self.data[:, 0]

    def get_y(self):
        return self.data[:, 1]

    def get_z(self):
        return self.data[:, 2]

    def polish(self, rt_interval,
                    bkg_treshold,
               neighbor_treshold,
               neighbor_repeats,
               int_treshold):

        self.rt_interval = rt_interval
        self.bkg_treshold = bkg_treshold
        self.neighbor_treshold = neighbor_treshold
        self.low_intens_treshold = int_treshold
        self.bkg_polish_count = neighbor_repeats

        self.substract_bkg()

        for i in range(self.bkg_polish_count):
            map = get_intensity_map(self.data, low_treshold=self.low_intens_treshold, param=self.polish_param)
            self.data = find_inner_points(self.data, map, neighbor_treshold=self.neighbor_treshold, param=self.polish_param)

        params = self.get_polishing_params()
        data_text = self.data_to_string(self.data)
        self.db_admin.update_insert_polishing_2(data_text, datetime.now(), params)

    def get_polishing_params(self):
        return {
            'rt_interval': self.rt_interval,
            'bkg_treshold': self.bkg_treshold,
            'neighbor_treshold': self.neighbor_treshold,
            'low_intens_treshold': self.low_intens_treshold,
            'bkg_polish_count': self.bkg_polish_count,
            'polish_param': self.polish_param,
        }

    def set_polishing_params(self, params):
        self.rt_interval = params['rt_interval']
        self.bkg_treshold = params['bkg_treshold']
        self.neighbor_treshold = params['neighbor_treshold']
        self.low_intens_treshold = params['low_intens_treshold']
        self.bkg_polish_count = params['bkg_polish_count']
        self.polish_param = params['polish_param']

    def get_deconv_params(self):
        return {
            'max_charge': self.deconv.max_charge,
            'is_positive': self.deconv.is_positive
        }

    def set_deconvolution_params(self, params):
        self.deconv.max_charge = params['max_charge']
        self.deconv.is_positive = params['is_positive']
            
    def data_to_string(self, data):
        return data.tostring()

    def string_to_data(self, text):
        arr1D = np.fromstring(text)
        return arr1D.reshape(len(arr1D) // 3, 3)

    def dataframe_to_text(self, dataframe):
        return dataframe.to_json()

    def text_to_dataframe(self, text):
        #return pd.read_json(text)
        return pd.DataFrame(json.loads(text))

    def mass_tags_to_text(self):
        df = pd.DataFrame(self.mass_tags)
        return self.dataframe_to_text(df)

    def text_to_mass_tags(self, text):
        df = self.text_to_dataframe(text)
        self.mass_tags = list(df.T.to_dict().values())
        return self.mass_tags

    def deconvolution(self, is_positive=False):
        self.deconv = oligosDeconvolution(self.data[:, 0], self.data[:, 1], self.data[:, 2], is_positive=is_positive)
        if self.deconv_fast:
            self.deconv.deconv_fast = True
        else:
            self.deconv.deconv_fast = False
        self.deconv_data = self.deconv.deconvolute()

        params = self.get_deconv_params()
        content = self.dataframe_to_text(self.deconv_data)
        self.db_admin.update_insert_deconvolution(content, datetime.now(), params)

        return self.deconv_data, self.deconv

    def add_mass_tag(self, tag_name, sequence=''):
        if len(self.selected_mass_points) > 0:
            df = pd.DataFrame(self.selected_mass_points)
            d = {}
            d['tag name'] = tag_name
            d['avg mass'] = round(df['mass'].mean(), 1)
            d['max mass'] = round(df['mass'].max(), 2)
            d['min mass'] = round(df['mass'].min(), 2)
            d['rt min'] = round(df['rt'].min(), 2)
            d['rt max'] = round(df['rt'].max(), 2)
            d['intens sum'] = round(self.get_integral_intens_percent(d['max mass'], d['min mass'],
                                                                     d['rt max'], d['rt min'], self.deconv_data), 2)
            d['area%'] = round(d['intens sum'] * 100 / self.deconv_data['intens'].sum(), 3)
            d['seq'] = sequence
            d['intensed mass'] = round(self.get_max_intens_mass(d['max mass'], d['min mass'],
                                                                     d['rt max'], d['rt min'], self.deconv_data), 2)
            self.mass_tags.append(d)
            self.db_admin.last_spectra_id = self.db_admin.flags['init_spectra']
            self.db_admin.update_insert_tags(self.mass_tags_to_text(), datetime.now())

    def delete_tag(self):
        if len(self.mass_tags) > 0:
            self.mass_tags.pop(self.selected_tag_row)
            self.db_admin.update_insert_tags(self.mass_tags_to_text(), datetime.now())

    def get_integral_intens_percent(self, m_max, m_min, rt_max, rt_min, data_tab):
        conditions = (data_tab['mass'] <= m_max)&(data_tab['mass'] >= m_min)
        df = data_tab[conditions]
        conditions = (data_tab['rt'] <= rt_max)&(data_tab['rt'] >= rt_min)
        df = df[conditions]
        return df['intens'].sum()

    def get_max_intens_mass(self, m_max, m_min, rt_max, rt_min, data_tab):
        conditions = (data_tab['mass'] <= m_max)&(data_tab['mass'] >= m_min)
        df = data_tab[conditions]
        conditions = (data_tab['rt'] <= rt_max)&(data_tab['rt'] >= rt_min)
        df = df.loc[conditions]
        #print(df)
        return df[df['intens'] == df['intens'].max()]['mass'].max()

    def print_all_tags(self):
        text = ''
        for i in self.mass_tags:
            text += f"{i['tag name']}: mass:{i['avg mass']}, rt :[{i['rt min']} - {i['rt max']}] area %: {i['area%']}\n"
        return text

    def drop_points_from_mass_data(self):
        if len(self.selected_mass_points) > 0:
            df = pd.DataFrame(self.selected_mass_points)
            index_list = []
            for point in self.selected_mass_points:
                cond = (self.deconv_data['mass'] == point['mass'])&(self.deconv_data['rt'] == point['rt'])
                index_list.extend(list(self.deconv_data[cond].index))
                #self.deconv_data.drop(index=list(df['index']), inplace=True)
            #print(list(set(index_list)))
            index_list = list(set(index_list))
            self.deconv_data.drop(index=index_list, inplace=True)

            params = self.get_deconv_params()
            content = self.dataframe_to_text(self.deconv_data)
            self.db_admin.update_insert_deconvolution(content, datetime.now(), params)

    def get_active_seq(self):
        if len(self.mass_tags) > 0:
            if 'seq' in list(self.mass_tags[self.selected_tag_row].keys()):
                return self.mass_tags[self.selected_tag_row]['seq']
            else:
                return ''
        else:
            return ''

    def create_fragments_generator(self, sequence, types):
        self.frag_generator = fragment_generator(sequence)
        self.frag_generator.generate(types)

    def get_fragments_tab(self):
        return self.frag_generator.fragment_tab.to_dict('records')

    def get_rect_borders(self, points):
        df = pd.DataFrame(points)
        rect = {}
        if points is not None:
            if 'x' in list(df.keys()):
                rect['rt_min'] = df['x'].min()
                rect['rt_max'] = df['x'].max()
                rect['mz_min'] = df['y'].min()
                rect['mz_max'] = df['y'].max()
        return rect

    def get_selected_area(self, rect_points):
        rect = self.get_rect_borders(rect_points)
        df = pd.DataFrame({'mz': self.get_y(), 'rt': self.get_x(), 'intens': self.get_z()})
        total_intens = df['intens'].sum()
        conditions = ((df['mz'] >= rect['mz_min']) & (df['mz'] <= rect['mz_max']) &
                      (df['rt'] >= rect['rt_min']) & (df['rt'] <= rect['rt_max']))
        df = df[conditions]
        area_intens = df['intens'].sum()

        avg_mz = (df['mz'] * df['intens']).sum() / area_intens

        return area_intens, total_intens, avg_mz

    def get_selected_area_total(self, rect):
        df = pd.DataFrame({'mz': self.get_y(), 'rt': self.get_x(), 'intens': self.get_z()})
        total_intens = df['intens'].sum()
        conditions = ((df['mz'] >= rect['mz_min']) & (df['mz'] <= rect['mz_max']) &
                      (df['rt'] >= rect['rt_min']) & (df['rt'] <= rect['rt_max']))
        df = df[conditions]
        area_intens = df['intens'].sum()
        return area_intens, total_intens

    def get_total_area_adduct(self, rect, charge):
        r = rect.copy()
        r['mz_min'] = rect['mz_min'] * charge + charge
        r['mz_max'] = rect['mz_max'] * charge + charge

        s, total_intens = 0, 0
        for i in range(1, 101):
            rect_i = {
                'mz_min': (r['mz_min'] - i) / i,
                'mz_max': (r['mz_max'] - i) / i,
                'rt_min': r['rt_min'],
                'rt_max': r['rt_max']
            }
            area_intens, total_intens = self.get_selected_area_total(rect_i)
            #print(rect_i)
            #print(area_intens, total_intens, i)
            s += area_intens
        return s, total_intens

    def add_mz_area(self, name, sequence, rect_points):
        rect = self.get_rect_borders(rect_points)

        df = pd.DataFrame({'mz': self.get_y(), 'rt': self.get_x(), 'intens': self.get_z()})

        total_intens = df['intens'].sum()

        conditions = ((df['mz'] >= rect['mz_min']) & (df['mz'] <= rect['mz_max']) &
                      (df['rt'] >= rect['rt_min']) & (df['rt'] <= rect['rt_max']))
        df = df[conditions]

        area_intens = df['intens'].sum()

        d = {}
        d['tag name'] = name
        d['sequence'] = sequence
        d['local area%'] = area_intens * 100 / total_intens
        d['global area%'] = area_intens * 100 / total_intens
        d['rect area%'] = area_intens * 100 / total_intens
        self.mz_tags.append(d)
        out = []
        for tag in self.mz_tags:
            d = {}
            d['tag name'] = tag['tag name']
            d['sequence'] = tag['sequence']
            d['local area%'] = tag['local area%']
            d['global area%'] = tag['global area%']
            d['rect area%'] = tag['rect area%']
            out.append(d)
        return out

    def add_mz_adduct_to_tab(self, rowdata, rect_points):
        rect = self.get_rect_borders(rect_points['points'])
        sel_area, total_area, avg_mz = self.get_selected_area(rect_points['points'])

        if len(rowdata) > 0:
            out = rowdata.copy()
        else:
            out = []
        out.append(
            {
                'adduct name': 'new',
                'mz rect': json.dumps(rect),
                'mz': round(avg_mz, 2),
                'area': round(sel_area, 1),
                'charge': 1,
                'mass': round(avg_mz + 1, 1),
                'area%': round(sel_area * 100 / total_area, 2),
                'area total mz %': 0
            }
        )
        return out

    def update_mass_tab_(self, rowdata, selrowdata):
        out = []

        ref_mass = 0.

        if len(selrowdata) > 0:
            ref_mass = selrowdata[0]['mass']
        else:
            if len(rowdata) > 0:
                ref_mass = rowdata[0]['mass']

        for row in rowdata:
            d = row.copy()
            d['mass'] = round(row['mz'] * row['charge'] + row['charge'], 2)
            d['delta'] = round(d['mass'] - ref_mass, 2)
            area_, total_area_ = self.get_total_area_adduct(json.loads(row['mz rect']), row['charge'])
            d['area total mz %'] = round(area_ * 100 / total_area_, 2)
            d['norm area %'] = d['area total mz %']
            out.append(d)
        return out

    def get_total_adduct_area_purity(self, rowdata):
        s = 0.
        for row in rowdata:
            s += row['area total mz %'] / 100
        return round(s * 100, 2)

    def delete_lcms_adduct_tag(self, rowdata, selrowdata):
        out = []
        for row in rowdata:
            ctrl = True
            for sel in selrowdata:
                if row['mz rect'] == sel['mz rect']:
                    ctrl = False
                    break
            if ctrl:
                out.append(row)
        return out

    def normalization_adduct_purities(self, rowdata, norm_cf):
        out = []
        total = sum([row['area total mz %'] for row in rowdata])
        for row in rowdata:
            d = row.copy()
            d['norm area %'] = round(row['area total mz %'] * float(norm_cf) / total, 2)
            out.append(d)
        return out

    def save_adduct_report_to_csv(self, filename, rowdata):
        df = pd.DataFrame(rowdata)
        df.to_csv(filename, sep='\t', index=False)

    def get_mz_tab(self, sequence, rect_points, mz_find_wind):
        rect = self.get_rect_borders(rect_points)
        mz_ident = mzoi.mz_identifyer(sequence, rect=rect)
        tab = mz_ident.get_mz_distribution()
        local_mz_list = mz_ident.get_local_max_tab(self.data, mz_find_wind, rect, tab.to_dict('records'))
        return tab.to_dict('records'), rect, local_mz_list

    def add_mz_tag(self, name, sequence, rect, mz_window, mz_tab):
        tagger = mzoi.mz_tagger(rect, self.data, mz_tab, mz_window, name, sequence)
        tag_obj = tagger.integrate()
        self.mz_tags.append(tag_obj)
        out = []
        for tag in self.mz_tags:
            d = {}
            d['tag name'] = tag['tag name']
            d['sequence'] = tag['sequence']
            d['local area%'] = tag['local area%']
            d['global area%'] = tag['global area%']
            d['rect area%'] = tag['rect area%']
            out.append(d)
        return out

    def select_mz_intens_data(self, low_intens, points):
        rect = self.get_rect_borders(points)
        df = pd.DataFrame({'mz': self.get_y(), 'rt': self.get_x(), 'intens': self.get_z()})
        conditions = ((df['mz'] >= rect['mz_min'])&(df['mz'] <= rect['mz_max'])&
                      (df['rt'] >= rect['rt_min'])&(df['rt'] <= rect['rt_max'])&(df['intens'] >= low_intens))
        df = df[conditions]
        self.selected_mz_df = df
        return df

    def get_points_concentration(self, selections):
        #print(selections)
        if 'selections' in list(selections.keys()):
            rect = {}
            rect['rt_min'] = selections['selections'][0]['x0']
            rect['rt_max'] = selections['selections'][0]['x1']
            rect['mz_min'] = selections['selections'][0]['y1']
            rect['mz_max'] = selections['selections'][0]['y0']
        
            df = pd.DataFrame({'mz': self.get_y(), 'rt': self.get_x(), 'intens': self.get_z()})
            conditions = ((df['mz'] >= rect['mz_min']) & (df['mz'] <= rect['mz_max']) &
                               (df['rt'] >= rect['rt_min']) & (df['rt'] <= rect['rt_max']))
            df = df[conditions]
            area = (rect['mz_max'] - rect['mz_min']) * (rect['rt_max'] - rect['rt_min'])
            return df.shape[0] / area
        elif 'selections[0].x0' in list(selections.keys()):
            rect = {}
            rect['rt_min'] = selections['selections[0].x0']
            rect['rt_max'] = selections['selections[0].x1']
            rect['mz_min'] = selections['selections[0].y1']
            rect['mz_max'] = selections['selections[0].y0']
            df = pd.DataFrame({'mz': self.get_y(), 'rt': self.get_x(), 'intens': self.get_z()})
            conditions = ((df['mz'] >= rect['mz_min']) & (df['mz'] <= rect['mz_max']) &
                          (df['rt'] >= rect['rt_min']) & (df['rt'] <= rect['rt_max']))
            df = df[conditions]
            area = (rect['mz_max'] - rect['mz_min']) * (rect['rt_max'] - rect['rt_min'])
            return df.shape[0] / area
        else:
            return 0.


class fragment_generator():

    def __init__(self, sequence):
        self.sequence = sequence
        self.oligo = mmo.oligoNASequence(self.sequence)

    def generate(self, types):
        out = []
        for t in types:
            for i in range(self.oligo.size()):
                if t == 'prefix':
                    fragment = self.oligo.getPrefix(i)
                    d = {}
                    d['mass'] = fragment.getAvgMass()
                    d['seq'] = fragment.sequence
                    d['name'] = f'frag.prefix.{i}'
                    out.append(d)
                if t == 'suffix':
                    fragment = self.oligo.getSuffix(i)
                    d = {}
                    d['mass'] = fragment.getAvgMass()
                    d['seq'] = fragment.sequence
                    d['name'] = f'frag.suffix.{i}'
                    out.append(d)
                if t == 'deletion':
                    seq = self.oligo.getDeletion(i)
                    d = {}
                    d['mass'] = mmo.oligoNASequence(seq).getAvgMass()
                    d['seq'] = seq
                    d['name'] = f'frag.deletion.{i}'
                    out.append(d)
            if t == 'multimer':
                for n in [1,2,3,4,5]:
                    d = {}
                    d['mass'] = self.oligo.getAvgMass() * n
                    d['seq'] = self.oligo.sequence
                    d['name'] = f'multimer.{n}'
                    out.append(d)

        self.fragment_tab = pd.DataFrame(out)
        return self.fragment_tab.to_dict('records')


class reversPrimer():
    def __init__(self, seq):
        self.init_seq = seq

    def get_reverse_complement(self):
        seq = self.init_seq
        seq = seq.replace('A', 't')
        seq = seq.replace('T', 'a')
        seq = seq.replace('U', 'a')
        seq = seq.replace('C', 'g')
        seq = seq.replace('G', 'c')
        seq = list(seq.upper())
        return ''.join(seq[::-1])

    def convert2rna_seq(self):
        seq = self.init_seq
        seq = seq.replace('T', 'U')
        seq = [f'[r{i}]' for i in list(seq)]
        return ''.join(seq)

    def convert2rna_seq2(self):
        seq = self.init_seq
        seq = seq.replace('T', 'U')
        seq = [f'r{i}' for i in list(seq)]
        return ''.join(seq)
