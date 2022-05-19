from datetime import datetime

class Domicile:

    def __init__(self, id_domicile=None, domicile=None, normalized_domicile=None, street=None, street_number=None):
        self.id = id_domicile
        self.street_number = street_number
        self.street = street
        self.town = domicile
        self.normalized_town = normalized_domicile
        self.gps_coordinates = {
            'latitude': 0.0,
            'longitude': 0.0
        }
        self.type = None
        self.date = None

    def print_address_long(self):
        print("".join(['      ID = ',str(self.id),'      Town = ',str(self.town),'      Normalized town = ',str(self.normalized_town),'      Street = ',str(self.street),'      Street number = ',str(self.street_number),'      GPS = ',str(self.gps_coordinates)]))

    def print_address(self):
        if self.town and self.town != "None":
            print(str(self.town), end='')
        if self.normalized_town and self.normalized_town != "None":
            print("-" + str(self.normalized_town), end='')
        if self.street and self.street != "None":
            print(" " + str(self.street), end='')
        if self.street_number and self.street_number != "None":
            print(" " + str(self.street_number), end='')

    def not_empty(self):
        if ((not self.street_number or self.street_number == ' ') and (not self.street or self.street == ' ') and (not self.town or self.town == ' ') and (not self.normalized_town or self.normalized_town == ' ')):
            return False
        return True

    def create_domicile_from_graph_db(self, domicile):
        for data in domicile['result']:
            if data['key'] == 'id_adresa':
                self.id = data['value']
            if data['key'] == 'popisne_cislo':
                self.street_number = data['value']
            if data['key'] == 'ulica':
                self.street = data['value']
            if data['key'] == 'popisne_cislo':
                self.street_number = data['value']
            if data['key'] == 'ulica':
                self.street = data['value']

    def create_town_node(self):
        gps_coordinates_list = [self.gps_coordinates['latitude'], self.gps_coordinates['longitude']]
        return "".join(["CREATE (:Mesto {nazov_mesta:'",str(self.town),"',","id_mesto:'",str(self.id),"',","gps_suradnice:",self.add_list_to_graph_db(gps_coordinates_list),",","nazov_mesta_normalizovany:'",str(self.normalized_town),"'})\n"])

    def save_town_from_graph_db(self, domicile_graph_db):
        self.id = domicile_graph_db.get('id_mesto')
        self.town = domicile_graph_db.get('nazov_mesta')
        self.normalized_town = domicile_graph_db.get('nazov_mesta_normalizovany')
        self.gps_coordinates['latitude'] = domicile_graph_db.get('gps_suradnice')[0]
        self.gps_coordinates['longitude'] = domicile_graph_db.get('gps_suradnice')[1]

    @staticmethod
    def add_list_to_graph_db(list_variables):
        string = "["
        for i in list_variables:
            string = "".join([string,"'",str(i),"', "])
        if len(list_variables) > 0:
            string = string[:-2]
        string += "]"
        return string

    def set_gps_coordinates(self, json_files):
        for file in json_files:
            if file['zdroj'] == 'opava':
                for register in file['matriky']:
                    if isinstance(register['obce_seznam'], str):
                        if register['obce_seznam'] == self.normalized_town or register['obce_seznam'] == self.town:
                            self.gps_coordinates['latitude'] = self.get_latitude(register['obce'])
                            self.gps_coordinates['longitude'] = self.get_longitude(register['obce'])
                            if self.gps_coordinates['latitude'] is not None:
                                return
                    else:
                        for town in register['obce_seznam']:
                            if town == self.normalized_town or town == self.town:
                                self.gps_coordinates['latitude'] = self.get_latitude(register['obce'])
                                self.gps_coordinates['longitude'] = self.get_longitude(register['obce'])
                                if self.gps_coordinates['latitude'] is not None:
                                    return
            if file['zdroj'] == 'actapublica':
                for register in file['matriky']:
                    for town in register['obce']:
                        if town == self.normalized_town or town == self.town:
                            if 'souradnice' not in register['obce'][town]:
                                continue
                            self.gps_coordinates['latitude'] = register['obce'][town]['souradnice']['lat']
                            self.gps_coordinates['longitude'] = register['obce'][town]['souradnice']['lon']
                            if self.gps_coordinates['latitude'] is not None:
                                return
        self.gps_coordinates['latitude'] = 0.0
        self.gps_coordinates['longitude'] = 0.0

    def get_latitude(self, town_json):
        for town in town_json:
            if town['umisteni']['obec'] == self.town or town['umisteni']['obec'] == self.normalized_town:
                return town['souradnice']['lat']
            if town['umisteni']['cast_obce'] == self.town or town['umisteni']['cast_obce'] == self.normalized_town:
                if 'lat' not in town['souradnice']:
                    continue
                return town['souradnice']['lat']

    def get_longitude(self, town_json):
        for town in town_json:
            if town['umisteni']['obec'] == self.town or town['umisteni']['obec'] == self.normalized_town:
                return town['souradnice']['lon']
            if town['umisteni']['cast_obce'] == self.town or town['umisteni']['cast_obce'] == self.normalized_town:
                if 'lon' not in town['souradnice']:
                    continue
                return town['souradnice']['lon']
