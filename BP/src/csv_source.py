from person import Person
from domicile import Domicile
from record import Record
from register import Register
from enum import Enum
import pandas
from datetime import datetime
import uuid
import random
from dateutil.relativedelta import relativedelta

class TypeOfRecord(Enum):
    baptism = 'Záznam_o_křte'
    dead = 'Záznam_o_úmrti'
    marriage = 'Záznam_o_svatbe'


class ExcelDatabaseHandle(object):

    def __init__(self, file_name, json_file):
        self.file_name = file_name
        self.records = self.load_file()
        self.json_files = json_file
        self.number_of_people = 0

    def number_of_records(self):
        total_rows = len(self.records)
        return total_rows

    def load_file(self):
        return pandas.read_csv(self.file_name, delimiter=',', dtype=str) #N
        # old data
        #return pandas.read_csv(self.file_name, delimiter=';', encoding="cp1250", dtype=str)

    def replace_questionmarks(self, date):
        date_arr = date.split('.')
        if date_arr[0] == '?':
            date_arr[0] = '1'
        if date_arr[1] == '?':
            if date_arr[0] == '31':
                date_arr[1] = random.choice(['1', '3', '5', '7', '8', '10', '12'])
            elif date_arr[0] == '30':
                date_arr[1] = random.choice(['1', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
            else:
                date_arr[1] = random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
        return '.'.join([date_arr[0], date_arr[1], date_arr[2]])

    def get_record(self, row):  #Vytvorit nove funkcie pre manzelstva a umrtia
        register = Register()
        register.archive = [] if pandas.isna(self.records.at[row, 'Archiv']) else self.records.at[row, 'Archiv']
        register.fond = [] if pandas.isna(self.records.at[row, 'Fond']) else self.records.at[row, 'Fond']
        register.signature = [] if pandas.isna(self.records.at[row, 'Signatura']) else self.records.at[row, 'Signatura']
        register.id = [uuid.uuid1()] if pandas.isna(self.records.at[row, 'Signatura']) else self.records.at[row, 'Signatura']

        record = Record()
        record.id = row
        record.type = TypeOfRecord.baptism
        record.language = [] if pandas.isna(self.records.at[row, 'Jazyk záznamu']) else self.records.at[row, 'Jazyk záznamu']
        record.register = register
        record.number_scan = [] if pandas.isna(self.records.at[row, 'Pořadí scanu']) else self.records.at[row, 'Pořadí scanu']
        record.position = [] if pandas.isna(self.records.at[row, 'rozložení na scanu']) else self.records.at[row, 'rozložení na scanu']

        child = Person()
        child.id = uuid.uuid1()
        child.id_test = [] if pandas.isna(self.records.at[row, 'ID ditete']) else [self.records.at[row, 'ID ditete']]
        date = None if pandas.isna(self.records.at[row, 'Datum narození']) else self.records.at[row, 'Datum narození']
        if date is None:
            date = None if pandas.isna(self.records.at[row, 'Datum křtu']) else self.records.at[row, 'Datum křtu']
        if '?' in date:
            date = self.replace_questionmarks(date)
        birth_date_child = datetime.strptime(date, '%d.%m.%Y').date()
        child.birth_date = [birth_date_child]
        child.all_dates = [birth_date_child]
        child.name = [] if pandas.isna(self.records.at[row, 'Jméno dítěte']) else [self.records.at[row, 'Jméno dítěte']]
        child.surname = [] if pandas.isna(self.records.at[row, 'Příjmení dítěte']) else [self.records.at[row, 'Příjmení dítěte']]
        child.multiple_kids = [] if pandas.isna(self.records.at[row, 'vícerčata']) else [self.records.at[row, 'vícerčata']]
        child.sex = [] if pandas.isna(self.records.at[row, 'Pohlaví']) else [self.records.at[row, 'Pohlaví']]
        child.religion = [] if pandas.isna(self.records.at[row, 'Vyznání']) else [self.records.at[row, 'Vyznání']]
        child.multiple_kids = [] if pandas.isna(self.records.at[row, 'vícerčata']) else [self.records.at[row, 'vícerčata']]
        child.title = [] if pandas.isna(self.records.at[row, 'Titul křtěnce']) else [self.records.at[row, 'Titul křtěnce']]
        if not pandas.isna(self.records.at[row, 'mrtvěrozené']):
            child.dead_date = [birth_date_child]
        child_domicile = Domicile(uuid.uuid4())
        child_domicile.town = None if pandas.isna(self.records.at[row, 'Obec']) else self.records.at[row, 'Obec']
        child_domicile.street = None if pandas.isna(self.records.at[row, 'Ulice']) else self.records.at[row, 'Ulice']
        child_domicile.street_number = None if pandas.isna(self.records.at[row, 'Číslo popisné']) else self.records.at[row, 'Číslo popisné']
        child_domicile.set_gps_coordinates(self.json_files)
        if child_domicile.not_empty():
            child.domicile = [child_domicile]
        child.relation_enum = ['main']
        child.update_date_guess(birth_date_child, 'born')
        if child.not_empty():
            record.persons.append(child)

        baptist = Person()
        baptist.id = uuid.uuid1()
        baptist.id_test = [] if pandas.isna(self.records.at[row, 'ID krestitele']) else [self.records.at[row, 'ID krestitele']]
        baptist.name = [] if pandas.isna(self.records.at[row, 'křestitel jméno']) else [self.records.at[row, 'křestitel jméno']]
        baptist.surname = [] if pandas.isna(self.records.at[row, 'křestitel příjmení']) else [self.records.at[row, 'křestitel příjmení']]
        baptist.sex = ['M']
        baptist.all_dates = [birth_date_child]
        baptist.title = [] if pandas.isna(self.records.at[row, 'křestitel titul']) else [self.records.at[row, 'křestitel titul']]
        baptist.religion = ['K']
        baptist.relation_enum = ['granted']
        if baptist.not_empty():
            record.persons.append(baptist)
        
        midwife = Person()
        midwife.id = uuid.uuid1()
        midwife.id_test = [] if pandas.isna(self.records.at[row, 'ID porodni baby']) else [self.records.at[row, 'ID porodni baby']]
        midwife.name = [] if pandas.isna(self.records.at[row, 'Jméno porodní báby']) else [self.records.at[row, 'Jméno porodní báby']]
        midwife.surname = [] if pandas.isna(self.records.at[row, 'Příjmení porodní báby']) else [self.records.at[row, 'Příjmení porodní báby']]
        midwife.occupation = [] if pandas.isna(self.records.at[row, 'povolání porodní báby']) else [self.records.at[row, 'povolání porodní báby']]
        midwife_domicile = Domicile(uuid.uuid4())
        midwife_domicile.town = None if pandas.isna(self.records.at[row, 'obec porodní báby']) else self.records.at[row, 'obec porodní báby']
        midwife_domicile.street = None if pandas.isna(self.records.at[row, 'Ulice (porodní báby)']) else self.records.at[row, 'Ulice (porodní báby)']
        midwife_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. por. báby']) else self.records.at[row, 'č. p. por. báby']
        midwife_domicile.set_gps_coordinates(self.json_files)
        if midwife_domicile.not_empty():
            midwife.domicile = [midwife_domicile]
        midwife.update_date_guess(birth_date_child, 'midwife')
        midwife.relation_enum = ['midwife']
        midwife.all_dates = [birth_date_child]
        if midwife.not_empty():
            record.persons.append(midwife)
        
        father = Person()
        father.id = uuid.uuid1()
        father.id_test = [] if pandas.isna(self.records.at[row, 'ID otce']) else [self.records.at[row, 'ID otce']]
        father.title = [] if pandas.isna(self.records.at[row, 'Titul otce']) else [self.records.at[row, 'Titul otce']]
        father.name = [] if pandas.isna(self.records.at[row, 'Jméno otce']) else [self.records.at[row, 'Jméno otce']]
        father.surname = [] if pandas.isna(self.records.at[row, 'Příjmení otce']) else [self.records.at[row, 'Příjmení otce']]
        father.sex = ['M']
        father.all_dates = [birth_date_child]
        father.occupation = [] if pandas.isna(self.records.at[row, 'Povolání otce']) else self.records.at[row, 'Povolání otce'].split("; ")
        father_domicile = Domicile(uuid.uuid4())
        father_domicile.town = None if pandas.isna(self.records.at[row, 'Obec otce']) else self.records.at[row, 'Obec otce']
        father_domicile.street = None if pandas.isna(self.records.at[row, 'ulice otce']) else self.records.at[row, 'ulice otce']
        father_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. otce']) else self.records.at[row, 'č. p. otce']
        father_domicile.set_gps_coordinates(self.json_files)
        if father_domicile.not_empty():
            father.domicile = [father_domicile]
        father.religion = [] if pandas.isna(self.records.at[row, 'Vyznání otce']) else [self.records.at[row, 'Vyznání otce']]
        date_father = None if pandas.isna(self.records.at[row, 'datum narození otce']) else self.records.at[row, 'datum narození otce']
        if date_father is not None:
            if '?' in date_father:
                date_father = self.replace_questionmarks(date_father)
            birth_date_father = datetime.strptime(date_father, '%d.%m.%Y').date()
            father.birth_date = [birth_date_father]
        father.update_date_guess(birth_date_child, 'father')
        father.relation_enum = ['f']
        if father.not_empty():
            record.persons.append(father)

        father_father = Person()
        father_father.id = uuid.uuid1()
        father_father.id_test = [] if pandas.isna(self.records.at[row, 'ID otcova otce']) else [self.records.at[row, 'ID otcova otce']]
        father_father.name = [] if pandas.isna(self.records.at[row, 'Jméno otcova otce']) else [self.records.at[row, 'Jméno otcova otce']]
        father_father.surname = [] if pandas.isna(self.records.at[row, 'Příjmení otcova otce']) else [self.records.at[row, 'Příjmení otcova otce']]
        father_father.sex = ['M']
        father_father.all_dates = [birth_date_child]
        father_father.occupation = [] if pandas.isna(self.records.at[row, 'Povolání otcova otce']) else self.records.at[row, 'Povolání otcova otce'].split("; ")
        father_father_domicile = Domicile(uuid.uuid4())
        father_father_domicile.town = None if pandas.isna(self.records.at[row, 'Bydliště otcova otce']) else self.records.at[row, 'Bydliště otcova otce']
        father_father_domicile.street = None if pandas.isna(self.records.at[row, 'ulice otcova otce']) else self.records.at[row, 'ulice otcova otce']
        father_father_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. bydliště otcova otce']) else self.records.at[row, 'č. p. bydliště otcova otce']
        father_father_domicile.set_gps_coordinates(self.json_files)
        if father_father_domicile.not_empty():
            father_father.domicile = [father_father_domicile]
        father_father.update_date_guess(birth_date_child, 'grand_parent')
        father_father.relation_enum = ['f_f']
        if father_father.not_empty():
            record.persons.append(father_father)

        father_mother = Person()
        father_mother.id = uuid.uuid1()
        father_mother.id_test = [] if pandas.isna(self.records.at[row, 'ID otcovy matky']) else [self.records.at[row, 'ID otcovy matky']]
        father_mother.name = [] if pandas.isna(self.records.at[row, 'Jméno otcovy matky']) else [self.records.at[row, 'Jméno otcovy matky']]
        father_mother.surname = [] if pandas.isna(self.records.at[row, 'Příjmení otcovy matky']) else [self.records.at[row, 'Příjmení otcovy matky']]
        father_mother.sex = ['F']
        father_mother.all_dates = [birth_date_child]
        father_mother.occupation = [] if pandas.isna(self.records.at[row, 'Povolání otcovy matky']) else self.records.at[row, 'Povolání otcovy matky'].split("; ")
        father_mother_domicile = Domicile(uuid.uuid4())
        father_mother_domicile.town = None if pandas.isna(self.records.at[row, 'Bydliště otcovy matky']) else self.records.at[row, 'Bydliště otcovy matky']
        father_mother_domicile.street = None if pandas.isna(self.records.at[row, 'ulice otcovy matky']) else self.records.at[row, 'ulice otcovy matky']
        father_mother_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. bydliště otcovy matky']) else self.records.at[row, 'č. p. bydliště otcovy matky']
        father_mother_domicile.set_gps_coordinates(self.json_files)
        if father_mother_domicile.not_empty():
            father_mother.domicile = [father_mother_domicile]
        father_mother.update_date_guess(birth_date_child, 'grand_parent')
        father_mother.relation_enum = ['f_m']
        if father_mother.not_empty():
            record.persons.append(father_mother)

        mother = Person()
        mother.id = uuid.uuid1()
        mother.id_test = [] if pandas.isna(self.records.at[row, 'ID matky']) else [self.records.at[row, 'ID matky']]
        mother.name = [] if pandas.isna(self.records.at[row, 'Jméno matky']) else [self.records.at[row, 'Jméno matky']]
        mother.surname = [] if pandas.isna(self.records.at[row, 'Příjmení matky']) else [self.records.at[row, 'Příjmení matky']]
        mother.sex = ['F']
        mother.all_dates = [birth_date_child]
        mother.occupation = [] if pandas.isna(self.records.at[row, 'Povolání matky']) else self.records.at[row, 'Povolání matky'].split("; ")
        mother_domicile = Domicile(uuid.uuid4())
        mother_domicile.town = None if pandas.isna(self.records.at[row, 'Obec matky']) else self.records.at[row, 'Obec matky']
        mother_domicile.street = None if pandas.isna(self.records.at[row, 'ulice matky']) else self.records.at[row, 'ulice matky']
        mother_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. matky']) else self.records.at[row, 'č. p. matky']
        mother_domicile.set_gps_coordinates(self.json_files)
        if mother_domicile.not_empty():
            mother.domicile = [mother_domicile]
        mother.religion = [] if pandas.isna(self.records.at[row, 'Vyznání matky']) else [self.records.at[row, 'Vyznání matky']]
        date_mother = None if pandas.isna(self.records.at[row, 'datum narození matky']) else self.records.at[row, 'datum narození matky']
        if date_mother is not None:
            if '?' in date_mother:
                date_mother = self.replace_questionmarks(date_mother)
            birth_date_mother = datetime.strptime(date_mother, '%d.%m.%Y').date()
            mother.birth_date = [birth_date_mother]
        mother.update_date_guess(birth_date_child, 'mother')
        mother.relation_enum = ['m']
        if mother.not_empty():
            record.persons.append(mother)

        mother_father = Person()
        mother_father.id = uuid.uuid1()
        mother_father.id_test = [] if pandas.isna(self.records.at[row, 'ID matcina otce']) else [self.records.at[row, 'ID matcina otce']]
        mother_father.name = [] if pandas.isna(self.records.at[row, 'Jméno matčina otce']) else [self.records.at[row, 'Jméno matčina otce']]
        mother_father.surname = [] if pandas.isna(self.records.at[row, 'Příjmení matčina otce']) else [self.records.at[row, 'Příjmení matčina otce']]
        mother_father.sex = ['M']
        mother_father.all_dates = [birth_date_child]
        mother_father.occupation = [] if pandas.isna(self.records.at[row, 'Povolání matčina otce']) else self.records.at[row, 'Povolání matčina otce'].split("; ")
        mother_father_domicile = Domicile(uuid.uuid4())
        mother_father_domicile.town = None if pandas.isna(self.records.at[row, 'Bydliště matčina otce']) else self.records.at[row, 'Bydliště matčina otce']
        mother_father_domicile.street = None if pandas.isna(self.records.at[row, 'ulice matčina otce']) else self.records.at[row, 'ulice matčina otce']
        mother_father_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. matčina otce']) else self.records.at[row, 'č. p. matčina otce']
        mother_father_domicile.set_gps_coordinates(self.json_files)
        if mother_father_domicile.not_empty():
            mother_father.domicile = [mother_father_domicile]
        mother_father.update_date_guess(birth_date_child, 'grand_parent')
        mother_father.relation_enum = ['f_m']
        if mother_father.not_empty():
            record.persons.append(mother_father)

        mother_mother = Person()
        mother_mother.id = uuid.uuid1()
        mother_mother.id_test = [] if pandas.isna(self.records.at[row, 'ID matciny matky']) else [self.records.at[row, 'ID matciny matky']]
        mother_mother.name = [] if pandas.isna(self.records.at[row, 'Jméno matčiny matky']) else [self.records.at[row, 'Jméno matčiny matky']]
        mother_mother.surname = [] if pandas.isna(self.records.at[row, 'Příjmení matčiny matky']) else [self.records.at[row, 'Příjmení matčiny matky']]
        mother_mother.sex = ['F']
        mother_mother.all_dates = [birth_date_child]
        mother_mother.occupation = [] if pandas.isna(self.records.at[row, 'Povolání matčiny matky']) else self.records.at[row, 'Povolání matčiny matky'].split("; ")
        mother_mother_domicile = Domicile(uuid.uuid4())
        mother_mother_domicile.town = None if pandas.isna(self.records.at[row, 'Bydliště matčiny matky']) else self.records.at[row, 'Bydliště matčiny matky']
        mother_mother_domicile.street = None if pandas.isna(self.records.at[row, 'ulice matčiny matky']) else self.records.at[row, 'ulice matčiny matky']
        mother_mother_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. matčiny matky']) else self.records.at[row, 'č. p. matčiny matky']
        mother_mother_domicile.set_gps_coordinates(self.json_files)
        if mother_mother_domicile.not_empty():
            mother_father.domicile = [mother_mother_domicile]
        mother_mother.update_date_guess(birth_date_child, 'grand_parent')
        mother_mother.relation_enum = ['m_m']
        if mother_mother.not_empty():
            record.persons.append(mother_mother)
        
        godfather = Person()
        godfather.id = uuid.uuid1()
        godfather.id_test = [] if pandas.isna(self.records.at[row, 'ID kmotra 1']) else [self.records.at[row, 'ID kmotra 1']]
        godfather.title = [] if pandas.isna(self.records.at[row, 'Titul kmotra 1']) else [self.records.at[row, 'Titul kmotra 1']]
        godfather.name = [] if pandas.isna(self.records.at[row, 'Jméno kmotra 1']) else [self.records.at[row, 'Jméno kmotra 1']]
        godfather.surname = [] if pandas.isna(self.records.at[row, 'Příjmení kmotra 1']) else [self.records.at[row, 'Příjmení kmotra 1']]
        godfather.occupation = [] if pandas.isna(self.records.at[row, 'Povolání kmotra 1']) else [self.records.at[row, 'Povolání kmotra 1']]
        godfather.all_dates = [birth_date_child]
        godfather_domicile = Domicile(uuid.uuid4())
        godfather_domicile.town = None if pandas.isna(self.records.at[row, 'Bydliště kmotra 1']) else self.records.at[row, 'Bydliště kmotra 1']
        godfather_domicile.street = None if pandas.isna(self.records.at[row, 'ulice kmotra 1']) else self.records.at[row, 'ulice kmotra 1']
        godfather_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. kmotra 1']) else self.records.at[row, 'č. p. kmotra 1']
        if godfather_domicile.not_empty():
            godfather.domicile = [godfather_domicile]
        godfather.relation_enum = ['gf_1']
        godfather.update_date_guess(birth_date_child, 'granted')
        if godfather.not_empty():
            record.persons.append(godfather)

        godfather_relative = Person()
        godfather_relative.id = uuid.uuid1()
        godfather_relative.id_test = [] if pandas.isna(self.records.at[row, 'ID pribuzneho kmotra 1']) else [self.records.at[row, 'ID pribuzneho kmotra 1']]
        godfather_relative.title = [] if pandas.isna(self.records.at[row, 'Titul příbuzného kmotra 1']) else [self.records.at[row, 'Titul příbuzného kmotra 1']]
        godfather_relative.name = [] if pandas.isna(self.records.at[row, 'Jmeno pribuzneho 1']) else [self.records.at[row, 'Jmeno pribuzneho 1']]
        godfather_relative.surname = [] if pandas.isna(self.records.at[row, 'Prijmeni pribuzneho 1']) else [self.records.at[row, 'Prijmeni pribuzneho 1']]
        godfather_relative.occupation = [] if pandas.isna(self.records.at[row, 'Povolani pribuzneho 1']) else [self.records.at[row, 'Povolani pribuzneho 1']]
        godfather_relative.all_dates = [birth_date_child]
        godfather_relative_domicile = Domicile(uuid.uuid4())
        godfather_relative_domicile.town = None if pandas.isna(self.records.at[row, 'Obec pribuzneho 1']) else self.records.at[row, 'Obec pribuzneho 1']
        godfather_relative_domicile.street = None if pandas.isna(self.records.at[row, 'Ulice pribuzneho 1']) else self.records.at[row, 'Ulice pribuzneho 1']
        godfather_relative_domicile.street_number = None if pandas.isna(self.records.at[row, 'Č.p. pribuzneho 1']) else self.records.at[row, 'Č.p. pribuzneho 1']
        if godfather_relative_domicile.not_empty():
            godfather_relative.domicile = [godfather_relative_domicile]
        godfather_relative.update_date_guess(birth_date_child, 'granted')
        godfather_relative.relation_enum = ['gfrel_1']
        if godfather_relative.not_empty():
            record.persons.append(godfather_relative)
        
        godfather2 = Person()
        godfather2.id = uuid.uuid1()
        godfather2.id_test = [] if pandas.isna(self.records.at[row, 'ID kmotra 2']) else [self.records.at[row, 'ID kmotra 2']]
        godfather2.title = [] if pandas.isna(self.records.at[row, 'Titul kmotra 2']) else [self.records.at[row, 'Titul kmotra 2']]
        godfather2.name = [] if pandas.isna(self.records.at[row, 'Jméno kmotra 2']) else [self.records.at[row, 'Jméno kmotra 2']]
        godfather2.surname = [] if pandas.isna(self.records.at[row, 'Příjmení kmotra 2']) else [self.records.at[row, 'Příjmení kmotra 2']]
        godfather2.occupation = [] if pandas.isna(self.records.at[row, 'Povolání kmotra 2']) else [self.records.at[row, 'Povolání kmotra 2']]
        godfather2.all_dates = [birth_date_child]
        godfather2_domicile = Domicile(uuid.uuid4())
        godfather2_domicile.town = None if pandas.isna(self.records.at[row, 'Bydliště kmotra 2']) else self.records.at[row, 'Bydliště kmotra 2']
        godfather2_domicile.street = None if pandas.isna(self.records.at[row, 'ulice kmotra 2']) else self.records.at[row, 'ulice kmotra 2']
        godfather2_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. kmotra 2']) else self.records.at[row, 'č. p. kmotra 2']
        if godfather2_domicile.not_empty():
            godfather2.domicile = [godfather2_domicile]
        godfather2.update_date_guess(birth_date_child, 'granted')
        godfather2.relation_enum = ['gf_2']
        if godfather2.not_empty():
            record.persons.append(godfather2)

        godfather_relative2 = Person()
        godfather_relative2.id = uuid.uuid1()
        godfather_relative2.id_test = [] if pandas.isna(self.records.at[row, 'ID pribuzneho kmotra 2']) else [self.records.at[row, 'ID pribuzneho kmotra 2']]
        godfather_relative2.title = [] if pandas.isna(self.records.at[row, 'Titul příbuzného kmotra 2']) else [self.records.at[row, 'Titul příbuzného kmotra 2']]
        godfather_relative2.name = [] if pandas.isna(self.records.at[row, 'Jmeno pribuzneho 2']) else [self.records.at[row, 'Jmeno pribuzneho 2']]
        godfather_relative2.surname = [] if pandas.isna(self.records.at[row, 'Prijmeni pribuzneho 2']) else [self.records.at[row, 'Prijmeni pribuzneho 2']]
        godfather_relative2.occupation = [] if pandas.isna(self.records.at[row, 'Povolani pribuzneho 2']) else [self.records.at[row, 'Povolani pribuzneho 2']]
        godfather_relative2.all_dates = [birth_date_child]
        godfather_relative2_domicile = Domicile(uuid.uuid4())
        godfather_relative2_domicile.town = None if pandas.isna(self.records.at[row, 'Obec pribuzneho 2']) else self.records.at[row, 'Obec pribuzneho 2']
        godfather_relative2_domicile.street = None if pandas.isna(self.records.at[row, 'Ulice pribuzneho 2']) else self.records.at[row, 'Ulice pribuzneho 2']
        godfather_relative2_domicile.street_number = None if pandas.isna(self.records.at[row, 'Č.p. pribuzneho 2']) else self.records.at[row, 'Č.p. pribuzneho 2']
        if godfather_relative2_domicile.not_empty():
            godfather_relative.domicile = [godfather_relative2_domicile]
        godfather_relative2.update_date_guess(birth_date_child, 'granted')
        godfather_relative2.relation_enum = ['gfrel_2']
        if godfather_relative2.not_empty():
            record.persons.append(godfather_relative2)

        godfather3 = Person()
        godfather3.id = uuid.uuid1()
        godfather3.id_test = [] if pandas.isna(self.records.at[row, 'ID kmotra 3']) else [self.records.at[row, 'ID kmotra 3']]
        godfather3.title = [] if pandas.isna(self.records.at[row, 'Titul kmotra 3']) else [self.records.at[row, 'Titul kmotra 3']]
        godfather3.name = [] if pandas.isna(self.records.at[row, 'Jméno kmotra 3']) else [self.records.at[row, 'Jméno kmotra 3']]
        godfather3.surname = [] if pandas.isna(self.records.at[row, 'Příjmení kmotra 3']) else [self.records.at[row, 'Příjmení kmotra 3']]
        godfather3.occupation = [] if pandas.isna(self.records.at[row, 'Povolání kmotra 3']) else [self.records.at[row, 'Povolání kmotra 3']]
        godfather3_domicile = Domicile(uuid.uuid4())
        godfather3.all_dates = [birth_date_child]
        godfather3_domicile.town = None if pandas.isna(self.records.at[row, 'Bydliště kmotra 3']) else self.records.at[row, 'Bydliště kmotra 3']
        godfather3_domicile.street = None if pandas.isna(self.records.at[row, 'ulice kmotra 3']) else self.records.at[row, 'ulice kmotra 3']
        godfather3_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. kmotra 3']) else self.records.at[row, 'č. p. kmotra 3']
        if godfather3_domicile.not_empty():
            godfather3.domicile = [godfather3_domicile]
        godfather3.update_date_guess(birth_date_child, 'granted')
        godfather3.relation_enum = ['gf_3']
        if godfather3.not_empty():
            record.persons.append(godfather3)

        godfather_relative3 = Person()
        godfather_relative3.id = uuid.uuid1()
        godfather_relative3.id_test = [] if pandas.isna(self.records.at[row, 'ID pribuzneho kmotra 3']) else [self.records.at[row, 'ID pribuzneho kmotra 3']]
        godfather_relative3.title = [] if pandas.isna(self.records.at[row, 'Titul příbuzného kmotra 3']) else [self.records.at[row, 'Titul příbuzného kmotra 3']]
        godfather_relative3.name = [] if pandas.isna(self.records.at[row, 'Jmeno pribuzneho 3']) else [self.records.at[row, 'Jmeno pribuzneho 3']]
        godfather_relative3.surname = [] if pandas.isna(self.records.at[row, 'Prijmeni pribuzneho 3']) else [self.records.at[row, 'Prijmeni pribuzneho 3']]
        godfather_relative3.occupation = [] if pandas.isna(self.records.at[row, 'Povolani pribuzneho 3']) else [self.records.at[row, 'Povolani pribuzneho 3']]
        godfather_relative3.all_dates = [birth_date_child]
        godfather_relative3_domicile = Domicile(uuid.uuid4())
        godfather_relative3_domicile.town = None if pandas.isna(self.records.at[row, 'Obec pribuzneho 3']) else self.records.at[row, 'Obec pribuzneho 3']
        godfather_relative3_domicile.street = None if pandas.isna(self.records.at[row, 'Ulice pribuzneho 3']) else self.records.at[row, 'Ulice pribuzneho 3']
        godfather_relative3_domicile.street_number = None if pandas.isna(self.records.at[row, 'Č.p. pribuzneho 3']) else self.records.at[row, 'Č.p. pribuzneho 3']
        if godfather_relative3_domicile.not_empty():
            godfather_relative3.domicile = [godfather_relative3_domicile]
        godfather_relative3.update_date_guess(birth_date_child, 'granted')
        godfather_relative3.relation_enum = ['gfrel_3']
        if godfather_relative3.not_empty():
            record.persons.append(godfather_relative3)

        godfather4 = Person()
        godfather4.id = uuid.uuid1()
        godfather4.id_test = [] if pandas.isna(self.records.at[row, 'ID kmotra 4']) else [self.records.at[row, 'ID kmotra 4']]
        godfather4.title = [] if pandas.isna(self.records.at[row, 'Titul kmotra 4']) else [self.records.at[row, 'Titul kmotra 4']]
        godfather4.name = [] if pandas.isna(self.records.at[row, 'Jméno kmotra 4']) else [self.records.at[row, 'Jméno kmotra 4']]
        godfather4.surname = [] if pandas.isna(self.records.at[row, 'Příjmení kmotra 4']) else [self.records.at[row, 'Příjmení kmotra 4']]
        godfather4.occupation = [] if pandas.isna(self.records.at[row, 'Povolání kmotra 4']) else [self.records.at[row, 'Povolání kmotra 4']]
        godfather4.all_dates = [birth_date_child]
        godfather4_domicile = Domicile(uuid.uuid4())
        godfather4_domicile.town = None if pandas.isna(self.records.at[row, 'Bydliště kmotra 4']) else self.records.at[row, 'Bydliště kmotra 4']
        godfather4_domicile.street = None if pandas.isna(self.records.at[row, 'ulice kmotra 4']) else self.records.at[row, 'ulice kmotra 4']
        godfather4_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. kmotra 4']) else self.records.at[row, 'č. p. kmotra 4']
        if godfather4_domicile.not_empty():
            godfather4.domicile = [godfather4_domicile]
        godfather4.update_date_guess(birth_date_child, 'granted')
        godfather4.relation_enum = ['gf_4']
        if godfather4.not_empty():
            record.persons.append(godfather4)

        godfather_relative4 = Person()
        godfather_relative4.id = uuid.uuid1()
        godfather_relative4.id_test = [] if pandas.isna(self.records.at[row, 'ID pribuzneho kmotra 4']) else [self.records.at[row, 'ID pribuzneho kmotra 4']]
        godfather_relative4.title = [] if pandas.isna(self.records.at[row, 'Titul příbuzného kmotra 4']) else [self.records.at[row, 'Titul příbuzného kmotra 4']]
        godfather_relative4.name = [] if pandas.isna(self.records.at[row, 'Jmeno pribuzneho 4']) else [self.records.at[row, 'Jmeno pribuzneho 4']]
        godfather_relative4.surname = [] if pandas.isna(self.records.at[row, 'Prijmeni pribuzneho 4']) else [self.records.at[row, 'Prijmeni pribuzneho 4']]
        godfather_relative4.occupation = [] if pandas.isna(self.records.at[row, 'Povolani pribuzneho 4']) else [self.records.at[row, 'Povolani pribuzneho 4']]
        godfather_relative4.all_dates = [birth_date_child]
        godfather_relative4_domicile = Domicile(uuid.uuid4())
        godfather_relative4_domicile.town = None if pandas.isna(self.records.at[row, 'Obec pribuzneho 4']) else self.records.at[row, 'Obec pribuzneho 4']
        godfather_relative4_domicile.street = None if pandas.isna(self.records.at[row, 'Ulice pribuzneho 4']) else self.records.at[row, 'Ulice pribuzneho 4']
        godfather_relative4_domicile.street_number = None if pandas.isna(self.records.at[row, 'Č.p. pribuzneho 4']) else self.records.at[row, 'Č.p. pribuzneho 4']
        if godfather_relative4_domicile.not_empty():
            godfather_relative4.domicile = [godfather_relative4_domicile]
        godfather_relative4.update_date_guess(birth_date_child, 'granted')
        godfather_relative4.relation_enum = ['gfrel_4']
        if godfather_relative4.not_empty():
            record.persons.append(godfather_relative4)
        
        self.number_of_people = len(record.persons)
        return record

    def get_record_burial(self, row):
        register = Register()
        register.archive = [] if pandas.isna(self.records.at[row, 'Archiv']) else self.records.at[row, 'Archiv']
        register.fond = [] if pandas.isna(self.records.at[row, 'Fond']) else self.records.at[row, 'Fond']
        register.signature = [] if pandas.isna(self.records.at[row, 'Signatura']) else self.records.at[row, 'Signatura']
        register.id = [uuid.uuid1()] if pandas.isna(self.records.at[row, 'Signatura']) else self.records.at[row, 'Signatura']

        record = Record()
        record.id = row
        record.type = TypeOfRecord.baptism
        record.language = [] if pandas.isna(self.records.at[row, 'Jazyk záznamu']) else self.records.at[row, 'Jazyk záznamu']
        record.register = register
        record.number_scan = [] if pandas.isna(self.records.at[row, 'Pořadí scanu']) else self.records.at[row, 'Pořadí scanu']
        record.position = [] if pandas.isna(self.records.at[row, 'rozložení na scanu']) else self.records.at[row, 'rozložení na scanu']
        record.type = TypeOfRecord.dead

        dead = Person()
        dead.id = uuid.uuid1()
        dead.id_test = [] if pandas.isna(self.records.at[row, 'ID zemřelého']) else [self.records.at[row, 'ID zemřelého']]
        dead.burial_date = [] if pandas.isna(self.records.at[row, 'datum pohřbení']) else [datetime.strptime(self.records.at[row, 'datum pohřbení'], "%d.%m.%Y").date()]
        dead.dead_date = [] if pandas.isna(self.records.at[row, 'datum úmrtí']) else [datetime.strptime(self.records.at[row, 'datum úmrtí'], "%d.%m.%Y").date()]
        dead.all_dates = []
        if dead.dead_date:
            date = dead.dead_date
            dead.all_dates.append(dead.dead_date[0])
            dead.update_date_guess(dead.dead_date[0], 'dead')
        elif dead.burial_date:
            date = dead.burial_date
            dead.all_dates.append(dead.burial_date[0])
        if dead.dead_date:
            if '?' in str(dead.dead_date[0]):
                dead.dead_date[0] = datetime.strptime(self.replace_questionmarks(str(dead.dead_date[0])), "%d.%m.%Y")
        if dead.burial_date:
            if '?' in str(dead.burial_date[0]):
                dead.burial_date[0] = datetime.strptime(self.replace_questionmarks(str(dead.burial_date[0])), "%d.%m.%Y")
        if date:
            if '?' in str(date[0]):
                date = datetime.strptime(self.replace_questionmarks(str(date)), "%d.%m.%Y")
        dead.viaticum = [0] if pandas.isna(self.records.at[row, 'zaopatřen?']) else [self.records.at[row, 'zaopatřen?']]
        dead.name = [] if pandas.isna(self.records.at[row, 'jméno zemřelého']) else [self.records.at[row, 'jméno zemřelého']]
        dead.surname = [] if pandas.isna(self.records.at[row, 'příjmení zemřelého']) else [self.records.at[row, 'příjmení zemřelého']]
        dead.sex = ['U'] if pandas.isna(self.records.at[row, 'Pohlaví zemřelé/ho']) else [self.records.at[row, 'Pohlaví zemřelé/ho']]
        dead.religion = [] if pandas.isna(self.records.at[row, 'Vyznání']) else [self.records.at[row, 'Vyznání']]
        dead.occupation = [] if pandas.isna(self.records.at[row, 'povolání zemřelého']) else self.records.at[row, 'povolání zemřelého'].split(';')
        dead.legitimate = [] if pandas.isna(self.records.at[row, 'nemanželské']) else [self.records.at[row, 'nemanželské']]
        dead.father_dead_flag = [] if pandas.isna(self.records.at[row, 'otec zemřelého mrtev']) else [self.records.at[row, 'otec zemřelého mrtev']]
        years_old = 0 if pandas.isna(self.records.at[row, 'věk zemřelého roky']) else int(float(self.records.at[row, 'věk zemřelého roky']))
        if date:
            dead.birth_date = [date[0] - relativedelta(years=years_old)]
        dead_domicile = Domicile(uuid.uuid4())
        dead_domicile.town = None if pandas.isna(self.records.at[row, 'obec zemřelého']) else self.records.at[row, 'obec zemřelého']
        dead_domicile.street = None
        dead_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. zemřelého']) else self.records.at[row, 'č. p. zemřelého']
        dead_domicile.set_gps_coordinates(self.json_files)
        if dead_domicile.not_empty():
            dead.domicile = [dead_domicile]
        dead.relation_enum = ['main']
        if dead.not_empty():
            record.persons.append(dead)
        
        priest = Person()
        priest.id = uuid.uuid1()
        priest.id_test = [] if pandas.isna(self.records.at[row, 'ID zaopatrovatel']) else [self.records.at[row, 'ID zaopatrovatel']]
        priest.all_dates = date
        priest.name = [] if pandas.isna(self.records.at[row, 'Zaopatřovatel']) else [self.records.at[row, 'Zaopatřovatel']]
        priest.surname = [] if pandas.isna(self.records.at[row, 'zaopatřovatel příjmení']) else [self.records.at[row, 'zaopatřovatel příjmení']]
        priest.sex = ['M']
        priest.religion = ['K']
        priest.title = [] if pandas.isna(self.records.at[row, 'zaopatřovatel titul']) else self.records.at[row, 'zaopatřovatel titul'].split(';')
        priest.relation_enum = ['bur_keeper']
        if priest.not_empty():
            record.persons.append(priest)

        gravedigger = Person()
        gravedigger.id = uuid.uuid1()
        gravedigger.id_test = [] if pandas.isna(self.records.at[row, 'ID pohrbivajici']) else [self.records.at[row, 'ID pohrbivajici']]
        gravedigger.all_dates = date
        gravedigger.name = [] if pandas.isna(self.records.at[row, 'Pohřbívající']) else [self.records.at[row, 'Pohřbívající']]
        gravedigger.surname = [] if pandas.isna(self.records.at[row, 'pohřbívající příjmení']) else [self.records.at[row, 'pohřbívající příjmení']]
        gravedigger.sex = ['M']
        gravedigger.title = [] if pandas.isna(self.records.at[row, 'pohřbívající titul/povolání']) else self.records.at[row, 'pohřbívající titul/povolání'].split(';')
        gravedigger.relation_enum = ['bur_gravedigger']
        if gravedigger.not_empty():
            record.persons.append(priest)

        father = Person()
        father.id = uuid.uuid1()
        father.id_test = [] if pandas.isna(self.records.at[row, 'ID otce']) else [self.records.at[row, 'ID otce']]
        father.name = [] if pandas.isna(self.records.at[row, 'jméno otce zemřelého']) else [self.records.at[row, 'jméno otce zemřelého']]
        father.surname = [] if pandas.isna(self.records.at[row, 'příjmení otce zemřelého']) else [self.records.at[row, 'příjmení otce zemřelého']]
        father.sex = ['M']
        father.all_dates = date
        father.occupation = [] if pandas.isna(self.records.at[row, 'povolání otce zemřelého']) else self.records.at[row, 'povolání otce zemřelého'].split("; ")
        father_domicile = Domicile(uuid.uuid4())
        father_domicile.town = None if pandas.isna(self.records.at[row, 'obec otce zemřelého']) else self.records.at[row, 'obec otce zemřelého']
        father_domicile.set_gps_coordinates(self.json_files)
        if father_domicile.not_empty():
            father.domicile = [father_domicile]
        if dead.birth_date:
            father.update_date_guess(dead.birth_date[0], 'father')
        father.relation_enum = ['f']
        if father.not_empty():
            record.persons.append(father)

        mother = Person()
        mother.id = uuid.uuid1()
        mother.id_test = [] if pandas.isna(self.records.at[row, 'id matka']) else [self.records.at[row, 'id matka']]
        mother.name = [] if pandas.isna(self.records.at[row, 'jméno matky zemřelého']) else [self.records.at[row, 'jméno matky zemřelého']]
        mother.surname = [] if pandas.isna(self.records.at[row, 'příjmení matky zemřelého']) else [self.records.at[row, 'příjmení matky zemřelého']]
        mother.sex = ['F']
        mother.all_dates = date
        mother.occupation = [] if pandas.isna(self.records.at[row, 'povolání matky zemřelého']) else self.records.at[row, 'povolání matky zemřelého'].split("; ")
        mother_domicile = Domicile(uuid.uuid4())
        mother_domicile.town = None if pandas.isna(self.records.at[row, 'obec matky zemřelého']) else self.records.at[row, 'obec matky zemřelého']
        mother_domicile.set_gps_coordinates(self.json_files)
        if mother_domicile.not_empty():
            mother.domicile = [mother_domicile]
        if dead.birth_date:
            mother.update_date_guess(dead.birth_date[0], 'mother')
        mother.relation_enum = ['m']
        if mother.not_empty():
            record.persons.append(mother)

        husband = Person()
        husband.id = uuid.uuid1()
        husband.id_test = [] if pandas.isna(self.records.at[row, 'ID Manžela']) else [self.records.at[row, 'ID Manžela']]
        husband.name = [] if pandas.isna(self.records.at[row, 'jméno manžela zemřelé']) else [self.records.at[row, 'jméno manžela zemřelé']]
        husband.surname = [] if pandas.isna(self.records.at[row, 'příjmení manžela zemřelé']) else [self.records.at[row, 'příjmení manžela zemřelé']]
        husband.sex = ['M']
        husband.all_dates = date
        husband.occupation = [] if pandas.isna(self.records.at[row, 'povolání manžela zemřelé']) else self.records.at[row, 'povolání manžela zemřelé'].split("; ")
        husband_domicile = Domicile(uuid.uuid4())
        husband_domicile.town = None if pandas.isna(self.records.at[row, 'obec manžela zemřelé']) else self.records.at[row, 'obec manžela zemřelé']
        husband_domicile.set_gps_coordinates(self.json_files)
        if husband_domicile.not_empty():
            husband.domicile = [mother_domicile]
        if dead.birth_date:
            husband.update_date_guess(dead.birth_date[0], 'husband')
        husband.relation_enum = ['bur_husband']
        if husband.not_empty():
            record.persons.append(husband)

        self.number_of_people = len(record.persons)
        return record

    def get_record_marriage(self, row):
        register = Register()
        register.archive = [] if pandas.isna(self.records.at[row, 'Archiv']) else self.records.at[row, 'Archiv']
        register.fond = [] if pandas.isna(self.records.at[row, 'Fond']) else self.records.at[row, 'Fond']
        register.signature = [] if pandas.isna(self.records.at[row, 'Signatura']) else self.records.at[row, 'Signatura']
        register.id = [uuid.uuid1()] if pandas.isna(self.records.at[row, 'Signatura']) else self.records.at[row, 'Signatura']

        record = Record()
        record.id = row
        record.type = TypeOfRecord.baptism
        record.language = [] if pandas.isna(self.records.at[row, 'Jazyk záznamu']) else self.records.at[row, 'Jazyk záznamu']
        record.register = register
        record.number_scan = [] if pandas.isna(self.records.at[row, 'Pořadí scanu']) else self.records.at[row, 'Pořadí scanu']
        record.position = [] if pandas.isna(self.records.at[row, 'rozložení na scanu']) else self.records.at[row, 'rozložení na scanu']
        record.type = TypeOfRecord.marriage

        date = [] if pandas.isna(self.records.at[row, 'datum sňatku']) else [datetime.strptime(self.replace_questionmarks(self.records.at[row, 'datum sňatku']), "%d.%m.%Y").date()]

        priest = Person()
        priest.id = uuid.uuid1()
        priest.id_test = [] if pandas.isna(self.records.at[row, 'ID oddavajici']) else [self.records.at[row, 'ID oddavajici']]
        priest.all_dates = date
        priest.name = [] if pandas.isna(self.records.at[row, 'oddávající jméno']) else [self.records.at[row, 'oddávající jméno']]
        priest.surname = [] if pandas.isna(self.records.at[row, 'oddávající příjmení']) else [self.records.at[row, 'oddávající příjmení']]
        priest.sex = ['M']
        priest.religion = ['K']
        priest.title = [] if pandas.isna(self.records.at[row, 'oddávající titul']) else self.records.at[row, 'oddávající titul'].split(';')
        priest.relation_enum = ['mar_priest']
        if priest.not_empty():
            record.persons.append(priest)

        groom = Person()
        groom.id = uuid.uuid1()
        groom.id_test = [] if pandas.isna(self.records.at[row, 'ID']) else [self.records.at[row, 'ID']]
        groom.all_dates = date
        groom.name = [] if pandas.isna(self.records.at[row, 'Jméno ženicha']) else [self.records.at[row, 'Jméno ženicha']]
        groom.surname = [] if pandas.isna(self.records.at[row, 'Příjmení ženicha']) else [self.records.at[row, 'Příjmení ženicha']]
        groom.sex = [] if pandas.isna(self.records.at[row, 'Příjmení ženicha']) else [self.records.at[row, 'Příjmení ženicha']]
        groom.relation_enum = ['mar_groom']
        groom.religion = [] if pandas.isna(self.records.at[row, 'Vyznání ženicha']) else [self.records.at[row, 'Vyznání ženicha']]
        groom.birth_date = [] if pandas.isna(self.records.at[row, 'datum narozeni ženicha']) else [datetime.strptime(self.records.at[row, 'datum narozeni ženicha'], "%d.%m.%Y").date()]
        groom_age = None if pandas.isna(self.records.at[row, 'věk ženicha-roky']) else int(float(self.records.at[row, 'věk ženicha-roky']))
        if not groom.birth_date:
            if groom_age:
                groom.birth_date = [date[0] - relativedelta(years=groom_age)]
        groom.dead_date = [] if pandas.isna(self.records.at[row, 'datum úmrtí ženicha']) else [datetime.strptime(self.records.at[row, 'datum úmrtí ženicha'], "%d.%m.%Y").date()]
        groom_domicile = Domicile(uuid.uuid4())
        groom_domicile.town = None if pandas.isna(self.records.at[row, 'obec ženicha']) else self.records.at[row, 'obec ženicha']
        groom_domicile.street = None
        groom_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. ženicha']) else self.records.at[row, 'č. p. ženicha']
        groom_domicile.set_gps_coordinates(self.json_files)
        if groom_domicile.not_empty():
            groom.domicile = [groom_domicile]
        groom.occupation = [] if pandas.isna(self.records.at[row, 'povolání ženicha']) else self.records.at[row, 'povolání ženicha'].split(';')
        if groom.not_empty():
            record.persons.append(groom)

        bride = Person()
        bride.id = uuid.uuid1()
        bride.id_test = [] if pandas.isna(self.records.at[row, 'ID nevěsty']) else [self.records.at[row, 'ID nevěsty']]
        bride.all_dates = date
        bride.name = [] if pandas.isna(self.records.at[row, 'Jméno nevěsty']) else [self.records.at[row, 'Jméno nevěsty']]
        bride.surname = [] if pandas.isna(self.records.at[row, 'Příjmení ženicha']) else [self.records.at[row, 'Příjmení ženicha']]
        bride.sex = [] if pandas.isna(self.records.at[row, 'Příjmení nevěsty']) else [self.records.at[row, 'Příjmení nevěsty']]
        bride.relation_enum = ['mar_bride']
        bride.religion = [] if pandas.isna(self.records.at[row, 'Vyznání nevěsty']) else [self.records.at[row, 'Vyznání nevěsty']]
        bride.birth_date = [] if pandas.isna(self.records.at[row, 'datum narození nevěsty']) else [datetime.strptime(self.records.at[row, 'datum narození nevěsty'], "%d.%m.%Y").date()]
        bride_age = None if pandas.isna(self.records.at[row, 'věk nevěsty-roky']) else [self.records.at[row, 'věk nevěsty-roky']]
        if not bride.birth_date:
            if bride_age:
                bride.birth_date = [date[0] - relativedelta(bride_age)]
        bride.dead_date = [] if pandas.isna(self.records.at[row, 'datum úmrtí nevěsty']) else [datetime.strptime(self.records.at[row, 'datum úmrtí nevěsty'], "%d.%m.%Y").date()]
        bride_domicile = Domicile(uuid.uuid4())
        bride_domicile.town = None if pandas.isna(self.records.at[row, 'obec nevěsty']) else self.records.at[row, 'obec nevěsty']
        bride_domicile.street = None
        bride_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. nevěsty']) else self.records.at[row, 'č. p. nevěsty']
        bride_domicile.set_gps_coordinates(self.json_files)
        if bride_domicile.not_empty():
            bride.domicile = [bride_domicile]
        bride.occupation = [] if pandas.isna(self.records.at[row, 'povolání nevěsty']) else self.records.at[row, 'povolání nevěsty'].split(';')
        if bride.not_empty():
            record.persons.append(bride)

        father_groom = Person()
        father_groom.id = uuid.uuid1()
        father_groom.id_test = [] if pandas.isna(self.records.at[row, 'ID otce ženicha']) else [self.records.at[row, 'ID otce ženicha']]
        father_groom.name = [] if pandas.isna(self.records.at[row, 'Jméno otce ženicha']) else [self.records.at[row, 'Jméno otce ženicha']]
        father_groom.surname = [] if pandas.isna(self.records.at[row, 'Příjmení otce ženicha']) else [self.records.at[row, 'Příjmení otce ženicha']]
        father_groom.sex = ['M']
        father_groom.all_dates = date
        father_groom.birth_date = [] if pandas.isna(self.records.at[row, 'datum narození otce ženicha']) else [self.records.at[row, 'datum narození otce ženicha']]
        father_groom.occupation = [] if pandas.isna(self.records.at[row, 'Povolání otce ženicha']) else self.records.at[row, 'Povolání otce ženicha'].split("; ")
        father_groom_domicile = Domicile(uuid.uuid4())
        father_groom_domicile.town = None if pandas.isna(self.records.at[row, 'Obec otce ženicha']) else self.records.at[row, 'Obec otce ženicha']
        father_groom_domicile.set_gps_coordinates(self.json_files)
        father_groom_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. otce ženicha']) else self.records.at[row, 'č. p. otce ženicha']
        father_groom.religion = [] if pandas.isna(self.records.at[row, 'Vyznání otce ženicha']) else [self.records.at[row, 'Vyznání otce ženicha']]
        if father_groom_domicile.not_empty():
            father_groom.domicile = [father_groom_domicile]
        if date:
            father_groom.update_date_guess(date[0], 'father_marriage')
        father_groom.relation_enum = ['mar_g_f']    
        if father_groom.not_empty():
            record.persons.append(father_groom)

        mother_groom = Person()
        mother_groom.id = uuid.uuid1()
        mother_groom.id_test = [] if pandas.isna(self.records.at[row, 'ID matky ženicha']) else [self.records.at[row, 'ID matky ženicha']]
        mother_groom.name = [] if pandas.isna(self.records.at[row, 'Jméno matky ženicha']) else [self.records.at[row, 'Jméno matky ženicha']]
        mother_groom.surname = [] if pandas.isna(self.records.at[row, 'Příjmení matky ženicha']) else [self.records.at[row, 'Příjmení matky ženicha']]
        mother_groom.sex = ['F']
        mother_groom.all_dates = date
        mother_groom.birth_date = [] if pandas.isna(self.records.at[row, 'datum narození matky ženicha']) else [self.records.at[row, 'datum narození matky ženicha']]
        mother_groom.occupation = [] if pandas.isna(self.records.at[row, 'Povolání matky ženicha']) else self.records.at[row, 'Povolání matky ženicha'].split("; ")
        mother_groom_domicile = Domicile(uuid.uuid4())
        mother_groom_domicile.town = None if pandas.isna(self.records.at[row, 'Obec matky ženicha']) else self.records.at[row, 'Obec matky ženicha']
        mother_groom_domicile.set_gps_coordinates(self.json_files)
        mother_groom_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. matky ženicha']) else self.records.at[row, 'č. p. matky ženicha']
        father_groom.religion = [] if pandas.isna(self.records.at[row, 'Vyznání matky ženicha']) else [self.records.at[row, 'Vyznání matky ženicha']]
        if mother_groom_domicile.not_empty():
            mother_groom.domicile = [mother_groom_domicile]
        if date:
            mother_groom.update_date_guess(date[0], 'mother_marriage')
        mother_groom.relation_enum = ['mar_g_m']
        if mother_groom.not_empty():
            record.persons.append(mother_groom)

        father_bride = Person()
        father_bride.id = uuid.uuid1()
        father_bride.id_test = [] if pandas.isna(self.records.at[row, 'ID otce nevěsty']) else [self.records.at[row, 'ID otce nevěsty']]
        father_bride.name = [] if pandas.isna(self.records.at[row, 'Jméno otce nevěsty']) else [self.records.at[row, 'Jméno otce nevěsty']]
        father_bride.surname = [] if pandas.isna(self.records.at[row, 'Příjmení otce nevěsty']) else [self.records.at[row, 'Příjmení otce nevěsty']]
        father_bride.sex = ['M']
        father_bride.all_dates = date
        father_bride.birth_date = [] if pandas.isna(self.records.at[row, 'datum narození otce nevěsty']) else [self.records.at[row, 'datum narození otce ženicha']]
        father_bride.occupation = [] if pandas.isna(self.records.at[row, 'Povolání otce nevěsty']) else self.records.at[row, 'Povolání otce nevěsty'].split("; ")
        father_bride_domicile = Domicile(uuid.uuid4())
        father_bride_domicile.town = None if pandas.isna(self.records.at[row, 'Obec otce nevěsty']) else self.records.at[row, 'Obec otce nevěsty']
        father_bride_domicile.set_gps_coordinates(self.json_files)
        father_bride_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. otce nevěsty']) else self.records.at[row, 'č. p. otce nevěsty']
        father_bride.religion = [] if pandas.isna(self.records.at[row, 'Vyznání otce nevěsty']) else [self.records.at[row, 'Vyznání otce nevěsty']]
        if father_bride_domicile.not_empty():
            father_bride.domicile = [father_bride_domicile]
        if date:
            father_bride.update_date_guess(date[0], 'father_marriage')
        father_bride.relation_enum = ['mar_b_f']    
        if father_bride.not_empty():
            record.persons.append(father_bride)

        mother_bride = Person()
        mother_bride.id = uuid.uuid1()
        mother_bride.id_test = [] if pandas.isna(self.records.at[row, 'ID matky nevěsty']) else [self.records.at[row, 'ID matky nevěsty']]
        mother_bride.name = [] if pandas.isna(self.records.at[row, 'Jméno matky nevěsty']) else [self.records.at[row, 'Jméno matky nevěsty']]
        mother_bride.surname = [] if pandas.isna(self.records.at[row, 'Příjmení matky nevěsty']) else [self.records.at[row, 'Příjmení matky nevěsty']]
        mother_bride.sex = ['F']
        mother_bride.all_dates = date
        mother_bride.birth_date = [] if pandas.isna(self.records.at[row, 'datum narození matky nevěsty']) else [self.records.at[row, 'datum narození matky nevěsty']]
        mother_bride.occupation = [] if pandas.isna(self.records.at[row, 'Povolání matky nevěsty']) else self.records.at[row, 'Povolání matky nevěsty'].split("; ")
        mother_bride_domicile = Domicile(uuid.uuid4())
        mother_bride_domicile.town = None if pandas.isna(self.records.at[row, 'Obec matky nevěsty']) else self.records.at[row, 'Obec matky nevěsty']
        mother_bride_domicile.set_gps_coordinates(self.json_files)
        mother_bride_domicile.street_number = None if pandas.isna(self.records.at[row, 'č. p. matky nevěsty']) else self.records.at[row, 'č. p. matky nevěsty']
        mother_bride.religion = [] if pandas.isna(self.records.at[row, 'Vyznání matky nevěsty']) else [self.records.at[row, 'Vyznání matky nevěsty']]
        if mother_bride_domicile.not_empty():
            mother_bride.domicile = [mother_bride_domicile]
        if date:
            mother_bride.update_date_guess(date[0], 'mother_marriage')
        mother_bride.relation_enum = ['mar_b_m']
        if mother_bride.not_empty():
            record.persons.append(mother_bride)

        witness = Person()
        witness.id = uuid.uuid1()
        witness.id_test = [] if pandas.isna(self.records.at[row, 'ID Svedek 1']) else [self.records.at[row, 'ID Svedek 1']]
        witness.name = [] if pandas.isna(self.records.at[row, 'Jméno svědka 1']) else [self.records.at[row, 'Jméno svědka 1']]
        witness.surname = [] if pandas.isna(self.records.at[row, 'Příjmení svědka 1']) else [self.records.at[row, 'Příjmení svědka 1']]
        witness.all_dates = date
        witness.occupation = [] if pandas.isna(self.records.at[row, 'Povolání svědka 1']) else self.records.at[row, 'Povolání svědka 1'].split("; ")
        witness_domicile = Domicile(uuid.uuid4())
        witness_domicile.town = None if pandas.isna(self.records.at[row, 'Obec svědka 1']) else self.records.at[row, 'Obec svědka 1']
        witness_domicile.set_gps_coordinates(self.json_files)
        if witness_domicile.not_empty():
            witness.domicile = [witness_domicile]
        if date:
            witness.update_date_guess(date[0], 'marriage')
        witness.relation_enum = ['mar_sv1']
        if witness.not_empty():
            record.persons.append(witness)

        witness2 = Person()
        witness2.id = uuid.uuid1()
        witness2.id_test = [] if pandas.isna(self.records.at[row, 'ID svedek 2']) else [self.records.at[row, 'ID svedek 2']]
        witness2.name = [] if pandas.isna(self.records.at[row, 'Jméno svědka 2']) else [self.records.at[row, 'Jméno svědka 2']]
        witness2.surname = [] if pandas.isna(self.records.at[row, 'Příjmení svědka 2']) else [self.records.at[row, 'Příjmení svědka 2']]
        witness2.all_dates = date
        witness2.occupation = [] if pandas.isna(self.records.at[row, 'Povolání svědka 2']) else self.records.at[row, 'Povolání svědka 2'].split("; ")
        witness2_domicile = Domicile(uuid.uuid4())
        witness2_domicile.town = None if pandas.isna(self.records.at[row, 'Obec svědka 2']) else self.records.at[row, 'Obec svědka 2']
        witness2_domicile.set_gps_coordinates(self.json_files)
        if witness2_domicile.not_empty():
            witness2.domicile = [witness2_domicile]
        if date:
            witness2.update_date_guess(date[0], 'marriage')
        witness2.relation_enum = ['mar_sv2']
        if witness2.not_empty():
            record.persons.append(witness2)

        self.number_of_people = len(record.persons)
        return record
