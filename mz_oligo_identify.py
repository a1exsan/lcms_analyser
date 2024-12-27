import pandas as pd
from oligoMass import molmassOligo as mmo
class mz_identifyer():

    def __init__(self, seq, rect={}):
        self.seq = seq
        self.rect = rect
        self.is_positive = False

    def get_mz_distribution(self):
        oligo = mmo.oligoNASequence(self.seq)
        mass = oligo.getAvgMass()

        out = []
        for charge in range(1, 101):
            d = {}
            d['mass'] = mass
            if self.is_positive:
                d['mz'] = (mass + charge) / charge
            else:
                d['mz'] = (mass - charge) / charge
            d['charge'] = charge
            out.append(d)

        df = pd.DataFrame(out)
        if self.rect != {}:
            conditions = (df['mz'] >= self.rect['mz_min'])&(df['mz'] <= self.rect['mz_max'])
            df = df[conditions]
        return df

    def get_data_frame(self, data):
        return pd.DataFrame({
            'rt': data[:, 0],
            'mz': data[:, 1],
            'intens': data[:, 2],
        })

    def get_local_max_tab(self, init_data, mz_find_wind, rect, mz_tab):
        out_list = []
        data = self.get_data_frame(init_data)
        cond = ((data['rt'] >= rect['rt_min']) & (data['rt'] <= rect['rt_max']) &
                (data['mz'] >= rect['mz_min']) & (data['mz'] <= rect['mz_max']))
        df = data[cond]
        for row in mz_tab:
            d = {}
            mz = row['mz']
            d['teor mz'] = mz
            ddf = df[(df['mz'] >= mz - mz_find_wind)&(df['mz'] <= mz + mz_find_wind)]
            if not ddf.empty:
                d['exp mz'] = ddf.loc[ddf['intens'].idxmax(), 'mz']
            else:
                d['exp mz'] = -1
            out_list.append(d)
        return out_list

class mz_tagger():

    def __init__(self, rect, data, mz_tab, mz_window, tag_name, sequence):
        self.rect = rect
        self.data = data
        self.mz_tab = mz_tab
        self.mz_window = mz_window
        self.tag_name = tag_name
        self.sequence = sequence

    def get_data_frame(self):
        return pd.DataFrame({
            'rt': self.data[:, 0],
            'mz': self.data[:, 1],
            'intens': self.data[:, 2],
        })

    def get_rect_integrals(self, data):
        cond = ((data['rt'] >= self.rect['rt_min'])&(data['rt'] <= self.rect['rt_max'])&
                (data['mz'] >= self.rect['mz_min'])&(data['mz'] <= self.rect['mz_max']))
        df = data[cond]
        s = 0
        for row in self.mz_tab:
            mz = row['mz']
            ddf = df[(df['mz'] >= mz - self.mz_window)&(df['mz'] <= mz + self.mz_window)]
            s += ddf['intens'].sum()

        return data['intens'].sum(), df['intens'].sum(), s

    def integrate(self):
        data = self.get_data_frame()
        total_intens, rect_intens, struct_sum = self.get_rect_integrals(data)
        tag_obj = {}
        tag_obj['tag name'] = self.tag_name
        tag_obj['sequence'] = self.sequence
        tag_obj['local area%'] = struct_sum * 100 / rect_intens
        tag_obj['global area%'] = struct_sum * 100 / total_intens
        tag_obj['rect area%'] = rect_intens * 100 / total_intens
        tag_obj['rect'] = self.rect
        tag_obj['mz window'] = self.mz_window
        return tag_obj


class mzIdentifying():

    def __init__(self, sequence='', mass=-1):
        self.seq = sequence
        self.oligo = mmo.oligoNASequence(self.seq)
        self.AvgMass = self.oligo.getAvgMass()

    def get_mz_tab(self, min_mz=500, max_mz=3200):

        d = {
                'mass': [],
                'mz': [],
                'charge': []
            }

        mz_forms = self.get_mz_forms(min_mz=min_mz, max_mz=max_mz)

        for mz, charge in zip(mz_forms['mz'], mz_forms['charge']):
            d['mass'].append(self.AvgMass)
            d['charge'].append(charge)
            d['mz'].append(mz)

        return pd.DataFrame(d)

    def get_mz_forms(self, min_mz=500, max_mz=3200):
        self.max_mz, self.min_mz = max_mz, min_mz
        self.forms = {'charge': [], 'mz': []}
        charge = 1
        while True:
            mz = (self.AvgMass - charge) / charge
            if mz >= min_mz and mz <= max_mz:
                self.forms['charge'].append(charge)
                self.forms['mz'].append(mz)
            elif mz < min_mz:
                break
            charge += 1
        return self.forms


def test():
    p = mz_identifyer('{H5P3O9}GrGrGrArUrArArUrGrGrArCrArUrUrUrGrCrUrUrCrUrGrArCrArCrArArCrUrGrUrGrUrUrCrArCrUrArGrCrArArCrCrUrCrArArArCrArGrArCrArCrC')
    print(p.get_mz_distribution())


if __name__=='__main__':
    test()

