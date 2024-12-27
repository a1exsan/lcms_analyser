import requests

class oligomaps_local_db():

    def __init__(self, db_IP, db_port):
        self.db_IP = db_IP
        self.db_port = db_port
        self.maps_db_name = 'asm_2000_map_1.db'
        self.api_db_url = f'http://{self.db_IP}:{self.db_port}'

    def get_oligomaps(self):
        url = f'{self.api_db_url}/{self.maps_db_name}/main_map'
        ret = requests.get(url)
        for r in ret.json():
            print(r)