import sqlite3
import os
from datetime import datetime
import json
import pandas as pd
import hashlib

class part_of_filename():
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.extension = os.path.splitext(self.name)[1]
        self.db_content_tab = pd.DataFrame()

    def __call__(self, *args, **kwargs):
        return self.name, self.extension

class lcms_db_admin():

    def __init__(self, db_name):
        self.db_name = db_name
        self.last_spectra_id = -1


    def get_flags(self, filecontent='', row_index=-1):

        self.flags = {
            'init_spectra': -1,
            'polishing': -1,
            'deconvolution': -1,
            'tagging': -1
                      }
        if filecontent != '':
            self.flags['init_spectra'] = self.is_filecontent_in_db_2(filecontent)
            self.last_spectra_id = self.flags['init_spectra']
            if self.flags['init_spectra'] > -1:
                self.flags['polishing'] = self.is_polishing_in_db(self.flags['init_spectra'])
                self.flags['deconvolution'] = self.is_deconvolution_in_db(self.flags['init_spectra'])
                self.flags['tagging'] = self.is_tags_in_db(self.flags['init_spectra'])
        else:
            if row_index > -1:
                db_row_data = self.get_data_from_db_tab_by_row_index(row_index)
                self.last_spectra_id = row_index
                if db_row_data != {}:
                    self.flags['init_spectra'] = int(db_row_data['id'])
                    self.flags['polishing'] = self.is_polishing_in_db(self.flags['init_spectra'])
                    self.flags['deconvolution'] = self.is_deconvolution_in_db(self.flags['init_spectra'])
                    self.flags['tagging'] = self.is_tags_in_db(self.flags['init_spectra'])
    def extract_data_by_flags(self):

        return_dict = {
            'polishing': '',
            'polish_params': {},
            'deconvolution': '',
            'deconv_params': {},
            'deconv_tags': []
        }

        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        if self.flags['polishing'] > -1:
            cursor.execute(f'SELECT id, content, polish_params FROM polishing WHERE id = ?',
                           [self.flags['polishing']])
            results = cursor.fetchall()
            if len(results) > 0:
                return_dict['polishing'] = results[0][1]
                return_dict['polish_params'] = self.text_to_params(results[0][2])

        if self.flags['deconvolution'] > -1:
            cursor.execute(f'SELECT id, content, deconv_params FROM deconvolution WHERE id = ?',
                           [self.flags['deconvolution']])
            results = cursor.fetchall()
            if len(results) > 0:
                return_dict['deconvolution'] = results[0][1]
                return_dict['deconv_params'] = self.text_to_params(results[0][2])

        if self.flags['tagging'] > -1:
            cursor.execute(f'SELECT id, tags FROM tagging_deconv WHERE id = ?',
                           [self.flags['tagging']])
            results = cursor.fetchall()
            if len(results) > 0:
                return_dict['deconv_tags'] = results[0][1]

        connection.close()
        return return_dict

    def is_filecontent_in_db(self, content):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(f'SELECT id, filename FROM init_spectra WHERE content = ?', [content])
        results = cursor.fetchall()
        connection.close()
        if len(results) == 0:
            return -1
        else:
            return results[0][0]

    def is_filecontent_in_db_2(self, content):

        content_hash = self.get_content_hash(content)

        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(f'SELECT id, filename FROM init_spectra WHERE hash = ?', [content_hash])
        results = cursor.fetchall()
        connection.close()
        if len(results) == 0:
            return -1
        else:
            return results[0][0]

    def is_polishing_in_db(self, spectra_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(f'SELECT id, polish_params FROM polishing WHERE init_spectra_id = ?', [spectra_id])
        results = cursor.fetchall()
        connection.close()
        if len(results) == 0:
            return -1
        else:
            return results[0][0]

    def is_deconvolution_in_db(self, spectra_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(f'SELECT id, deconv_params FROM deconvolution WHERE init_spectra_id = ?',
                       [spectra_id])
        results = cursor.fetchall()

        connection.close()
        if len(results) == 0:
            return -1
        else:
            return results[0][0]

    def is_tags_in_db(self, spectra_id):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(f'SELECT id, tags FROM tagging_deconv WHERE init_spectra_id = ?', [spectra_id])
        results = cursor.fetchall()
        connection.close()
        if len(results) == 0:
            return -1
        else:
            return results[0][0]

    def params_to_text(self, param_dict):
        return json.dumps(param_dict)

    def text_to_params(self, text):
        return json.loads(text)

    def insert_init_spectra(self,
                            filename,
                            file_content,
                            date,
                            description):

        out = False
        f_name, f_ext = part_of_filename(filename)()

        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute(f'SELECT * FROM init_spectra WHERE content = ?', [file_content])
        results = cursor.fetchall()

        if len(results) == 0:
            out = True
            cursor.execute("""INSERT INTO init_spectra (
                                    filename, fileextension, content, loaded_at, description) 
                                    VALUES (?, ?, ?, ?, ?)""",
                            (f_name, f_ext, file_content, date, description))
            self.last_spectra_id = cursor.lastrowid
        else:
            self.last_spectra_id = results[0][0]

        connection.commit()
        connection.close()
        return out

    def get_content_hash(self, content):
        return hashlib.md5(bytes(content, encoding='utf-8')).hexdigest()
    def insert_init_spectra_2(self,
                            filename,
                            file_content,
                            date,
                            description):

        out = False
        f_name, f_ext = part_of_filename(filename)()

        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        content_hash = self.get_content_hash(file_content)

        cursor.execute(f'SELECT * FROM init_spectra WHERE hash = ?', [content_hash])
        results = cursor.fetchall()

        if len(results) == 0:
            out = True
            cursor.execute("""INSERT INTO init_spectra (
                                    filename, fileextension, content, hash, loaded_at, description) 
                                    VALUES (?, ?, ?, ?, ?, ?)""",
                            (f_name, f_ext, '', content_hash, date, description))
            self.last_spectra_id = cursor.lastrowid
        else:
            self.last_spectra_id = results[0][0]

        connection.commit()
        connection.close()
        return out

    def insert_polishing(self,
                        content,
                        changed_at,
                        polish_params):

        if self.last_spectra_id > -1:

            out = False
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()

            cursor.execute(f'SELECT * FROM polishing WHERE init_spectra_id = ?',
                           [self.last_spectra_id])
            results = cursor.fetchall()

            if len(results) == 0:
                out = True
                cursor.execute("""INSERT INTO polishing (
                                    init_spectra_id, content, changed_at, polish_params) 
                                    VALUES (?, ?, ?, ?)""",
                            (self.last_spectra_id, content, changed_at,
                                        self.params_to_text(polish_params)))
            connection.commit()
            connection.close()
        return out

    def update_insert_polishing_2(self,
                        content,
                        changed_at,
                        polish_params):

        if self.last_spectra_id > -1:

            out = False
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()

            cursor.execute(f'SELECT * FROM polishing WHERE init_spectra_id = ?',
                           [self.last_spectra_id])
            results = cursor.fetchall()

            if len(results) == 0:
                out = True
                cursor.execute("""INSERT INTO polishing (
                                    init_spectra_id, content, changed_at, polish_params) 
                                    VALUES (?, ?, ?, ?)""",
                            (self.last_spectra_id, '', changed_at,
                                        self.params_to_text(polish_params)))
            else:
                cursor.execute("""UPDATE polishing set content = ?, changed_at = ?, polish_params = ?
                                                                        WHERE init_spectra_id = ? """,
                               ('', changed_at, self.params_to_text(polish_params),
                                self.last_spectra_id))
            connection.commit()
            connection.close()
        return out

    def update_insert_deconvolution(self,
                        content,
                        changed_at,
                        deconv_params):

        if self.last_spectra_id > -1:

            out = False
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()

            cursor.execute(f'SELECT * FROM deconvolution WHERE init_spectra_id = ?',
                           [self.last_spectra_id])
            results = cursor.fetchall()

            if len(results) == 0:
                out = True
                cursor.execute("""INSERT INTO deconvolution (
                                    init_spectra_id, content, changed_at, deconv_params) 
                                    VALUES (?, ?, ?, ?)""",
                            (self.last_spectra_id, content, changed_at,
                                        self.params_to_text(deconv_params)))
            else:
                cursor.execute("""UPDATE deconvolution set content = ?, changed_at = ?, deconv_params = ?
                                                        WHERE init_spectra_id = ? """,
                               (content, changed_at, self.params_to_text(deconv_params),
                               self.last_spectra_id))
            connection.commit()
            connection.close()
        return out

    def update_insert_tags(self, content, changed_at):
        out = False

        if self.last_spectra_id > -1:

            out = False
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()

            cursor.execute(f'SELECT * FROM tagging_deconv WHERE init_spectra_id = ?',
                           [self.last_spectra_id])
            results = cursor.fetchall()

            if len(results) == 0:
                out = True
                cursor.execute("""INSERT INTO tagging_deconv (
                                    init_spectra_id, tags, changed_at) 
                                    VALUES (?, ?, ?)""",
                            (self.last_spectra_id, content, changed_at))
            else:
                cursor.execute("""UPDATE tagging_deconv SET tags = ?, changed_at = ?
                                        WHERE init_spectra_id = ? """,
                               (content, changed_at, self.last_spectra_id))
            connection.commit()
            connection.close()


        return out

    def show_all_data_in_table(self, table_name):

        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        if table_name == 'init_spectra':
            cursor.execute(f'SELECT id, filename, fileextension, hash, loaded_at FROM {table_name}')
        elif table_name == 'polishing':
            cursor.execute(f'SELECT id, init_spectra_id, changed_at, polish_params FROM {table_name}')
        elif table_name == 'deconvolution':
            cursor.execute(f'SELECT id, init_spectra_id, changed_at, deconv_params FROM {table_name}')
        elif table_name == 'tagging_deconv':
            cursor.execute(f'SELECT id, init_spectra_id, changed_at, tags FROM {table_name}')

        results = cursor.fetchall()

        text = ''
        for row in results:
            text += f' {row} \n'

        connection.close()
        return text

    def get_content_tab(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute(f'SELECT id, filename, loaded_at FROM init_spectra')
        results = cursor.fetchall()

        if len(results) == 0:
            connection.commit()
            connection.close()
            return pd.DataFrame(
            {
                'id': [],
                'filename': [],
                'date': [],
                'deconv': [],
                'tagged': []
            })
        else:
            res = []
            for result in results:
                d = {}
                d['id'] = result[0]
                d['filename'] = result[1]
                d['date'] = result[2]
                cursor.execute(f'SELECT id FROM deconvolution WHERE init_spectra_id = ?',
                               [result[0]])
                res_deconv = cursor.fetchall()
                d['deconv'] = not len(res_deconv) == 0
                if d['deconv']:
                    d['deconv'] = res_deconv[0][0]
                cursor.execute(f'SELECT id FROM tagging_deconv WHERE init_spectra_id = ?',
                               [result[0]])
                res_tag = cursor.fetchall()
                d['tagged'] = not len(res_tag) == 0
                if d['tagged']:
                    d['tagged'] = res_tag[0][0]
                res.append(d)
            connection.close()

            self.db_content_tab = pd.DataFrame(res)
            return pd.DataFrame(res)

    def get_data_from_db_tab_by_row_index(self, row_index):
        if not self.db_content_tab.empty:
            return dict(self.db_content_tab.loc[row_index])
        else:
            return {}

def test():
    now = datetime.now()

    lcms_db = lcms_db_admin('oligo_lcms_2.db')
    lcms_db.insert_init_spectra('test.mzml',
                                'test content',
                                now,
                                'test description')
    print(lcms_db.show_all_data_in_table('init_spectra'))
    print(lcms_db.show_all_data_in_table('polishing'))
    print(lcms_db.show_all_data_in_table('deconvolution'))
    print(lcms_db.show_all_data_in_table('tagging_deconv'))

if __name__ == '__main__':
    test()