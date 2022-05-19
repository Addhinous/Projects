from posixpath import split
import mysql.connector
from mysql.connector import Error
from person import Person
from domicile import Domicile
from record import Record
from register import Register
from enum import Enum
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TypeOfRecord(Enum):
    baptism = 'Záznam_o_křte'
    burial = 'Záznam_o_úmrti'
    marriage = 'Záznam_o_svatbe'


class RelationalDatabaseHandle:

    def __init__(self, json_data):
        self.connection = self.connect()
        self.cursor = self.create_cursor()
        self.host = ''
        self.user = ''
        self.password = ''
        self.port = ''
        self.name_database = ''
        self.json_data = json_data

    def connect(self):
        try:
            file_creed = open('mysql_cred', 'r')
            Lines = file_creed.readlines()
            for line in Lines:
                data = line.replace('\n', '')
                data = data.split("=")
                if data[0] == 'host':
                    self.host = data[1]
                if data[0] == 'port':
                    self.port = data[1]
                if data[0] == 'user':
                    self.user = data[1]
                if data[0] == 'password':
                    self.password = data[1]
                if data[0] == 'name_database':
                    self.name_database = data[1]
            self.check_creed()
        finally:
            file_creed.close()

        try:
            connection = mysql.connector.connect(user=self.user, password=self.password, host=self.host, port=self.port, database=self.name_database, get_warnings=True)
            return connection
        except Error as e:
            print("Error while connecting to MySQL", e)

    def check_creed(self):
        if self.host == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')
        if self.user == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')
        if self.password == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')
        if self.port == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')
        if self.name_database == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')

    def create_cursor(self):
        if self.connection.is_connected():
            return self.connection.cursor(dictionary=True)
        else:
            print('Nepripojeny do databazy')

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            self.cursor.close()

    def get_all_birth_records(self):
        self.cursor.execute("SELECT * FROM birth")
        return self.cursor.fetchall()

    def get_all_burial_records(self):
        self.cursor.execute("SELECT * FROM burial")
        return self.cursor.fetchall()

    def get_all_marriage_records(self):
        self.cursor.execute("SELECT * FROM marriage")
        return self.cursor.fetchall()

    def get_record_birth(self, record):
        new_record = Record(record['id'])
        new_record.number_scan = record['scan']
        new_record.position = record['pos']
        new_record.comment = record['comment']
        new_record.language = record['lang']
        new_record.register = self.get_register_info(record)
        new_record.persons = self.get_persons_birth(record)
        new_record.type = TypeOfRecord.baptism
        self.set_info_about_main_person_birth(record, new_record)
        return new_record

    def get_record_burial(self, record):
        new_record = Record(record['id'])
        new_record.number_scan = record['scan']
        new_record.position = record['pos']
        new_record.comment = record['comment']
        new_record.language = record['lang']
        new_record.register = self.get_register_info(record)
        new_record.persons = self.get_persons_burial(record)
        new_record.type = TypeOfRecord.burial
        self.set_info_about_main_person_burial(record, new_record)
        return new_record

    def get_record_marriage(self, record):
        new_record = Record(record['id'])
        new_record.number_scan = record['scan']
        new_record.position = record['pos']
        new_record.comment = record['comment']
        new_record.language = record['lang']
        new_record.register = self.get_register_info(record)
        new_record.persons = self.get_persons_marriage(record)
        new_record.type = TypeOfRecord.marriage
        self.set_info_about_main_person_marriage(record, new_record)
        return new_record

    def check_marriage_record(self, record_db):
        sql = "SELECT * FROM birthMarriage WHERE birth_id = %s"
        marriage = self.select_one(sql, record_db["id"])
        if marriage is not None:
            return True
        else:
            return False

    def set_info_about_main_person_birth(self, record_db, record_new):
        for person in record_new.persons:
            if person.relation_enum == 'main':
                self.set_all_possible_info_main_person_birth(record_db, person)
                self.set_person_surname(record_db, person, 'confirmation')

    def set_info_about_main_person_burial(self, record_db, record_new):
        for person in record_new.persons:
            if person.relation_enum == 'bur_main' or person.relation_enum == 'main':
                self.set_all_possible_info_main_person_burial(record_db, person)

    def set_info_about_main_person_marriage(self, record_db, record_new):
        for person in record_new.persons:
            if person.relation_enum == 'mar_groom':
                self.set_all_possible_info_groom(record_db, person)
            if person.relation_enum == 'mar_bride:':
                self.set_all_possible_info_bride(record_db, person)


    def get_register_info(self, record_db):
        sql = "SELECT * FROM register WHERE id = %s"
        register = self.select_one(sql, record_db["register_id"])
        register_new = Register(register['id'])
        if register is not None:
            self.set_all_possible_info_register(register, register_new)
            self.set_register_municipality(register, register_new)
            self.set_register_range(register, register_new)

        return register_new

    def get_persons_birth(self, record):
        sql = "SELECT * FROM person WHERE birth_id = %s"
        persons = self.select_multiple(sql, record["id"])
        list_person = []
        date_of_record = self.get_date_of_record_birth(record, persons)
        for person in persons:
            new_person = self.set_person(person, 'birth')
            if new_person.not_empty():
                new_person.all_dates.append(date_of_record)
                if new_person.all_dates[-1]:
                    self.guess_date_according_to_role_birth(new_person.all_dates[-1], new_person)
                list_person.append(new_person)
        return list_person

    def get_persons_burial(self, record):
        sql = "SELECT * FROM person WHERE burial_id = %s"
        persons = self.select_multiple(sql, record["id"])
        list_person = []
        date_of_record = self.get_date_of_record_burial(record, persons)
        for person in persons:
            new_person = self.set_person(person, 'burial')
            if new_person.not_empty():
                new_person.all_dates.append(date_of_record)
                if new_person.all_dates[-1]:
                    self.guess_date_according_to_role_burial(new_person.all_dates[-1], new_person)
                list_person.append(new_person)
        return list_person

    def get_persons_marriage(self, record):
        sql = "SELECT * FROM person WHERE marriage_id = %s"
        persons = self.select_multiple(sql, record["id"])
        list_person = []
        date_of_record = self.get_date_of_record_marriage(record)
        for person in persons:
            new_person = self.set_person(person, 'marriage')
            if new_person.not_empty():
                if new_person.relation_enum[0] == 'mar_svrel_1' or new_person.relation_enum[0] == 'mar_svrel_2' or new_person.relation_enum[0] == 'mar_svrel_3' or new_person.relation_enum[0] == 'mar_svrel_4' or new_person.relation_enum[0] == 'mar_g_fost' or new_person.relation_enum[0] == 'mar_b_fost':
                    continue
                new_person.all_dates.append(date_of_record)
                if new_person.all_dates[-1]:
                    self.guess_date_according_to_role_marriage(new_person.all_dates[-1], new_person)
                list_person.append(new_person)
        return list_person

    def set_person(self, person, type):
        new_person = Person(person['id'])
        self.set_person_name(person, new_person, 'person')
        self.set_person_surname(person, new_person, 'person')
        self.set_all_possible_info_person(person, new_person, type)
        self.set_person_occupation(person, new_person, 'person')
        self.set_person_domicile(person, new_person)
        self.set_person_relation(person, new_person)
        self.set_sex_of_person(new_person)
        return new_person

    def get_date_of_record_birth(self, record, people):
        if record['baptism_date']:
            if '?' in record['baptism_date']:
                record['baptism_date'] = self.replace_double_questionmarks(record['baptism_date'])
            split_date = record['baptism_date'].split('-')
            if int(split_date[1]) > 12 and int(split_date[2]) < 12:
                backup = split_date[2]
                split_date[2] = split_date[1]
                split_date[1] = backup
                record['baptism_date'] = '-'.join(split_date)
            if int(split_date[2]) > 31:
                split_date[2] = '01'
                record['baptism_date'] = '-'.join([split_date[0], split_date[1], split_date[2]])
            if int(split_date[1]) > 12:
                record['baptism_date'] = '-'.join([split_date[0], '01', split_date[2]])
            if int(split_date[2]) > 28 and int(split_date[2]) <= 31 and split_date[1] == '02':
                record['baptism_date'] = '-'.join([split_date[0], '03', split_date[2]])
            return datetime.strptime(record['baptism_date'], "%Y-%m-%d")
        for person in people:
            if person['rel'] == 'main' and person['birth_date']:
                if '?' in person['birth_date']:
                    person['birth_date'] = self.replace_double_questionmarks(person['birth_date'])
                split_date = person['birth_date'].split('-')
                if int(split_date[1]) > 12 and int(split_date[2]) < 12:
                    backup = split_date[2]
                    split_date[2] = split_date[1]
                    split_date[1] = backup
                    person['birth_date'] = '-'.join(split_date)
                if int(split_date[2]) > 31:
                    split_date[2] = '01'
                    person['birth_date'] = '-'.join([split_date[0], split_date[1], split_date[2]])
                if int(split_date[1]) > 12:
                    person['birth_date'] = '-'.join([split_date[0], '01', split_date[2]])
                if int(split_date[2]) > 28 and int(split_date[2]) <= 31 and split_date[1] == '02':
                    person['birth_date'] = '-'.join([split_date[0], '03', split_date[2]])
                return datetime.strptime(person['birth_date'], "%Y-%m-%d")
        return None

    def get_date_of_record_burial(self, record, people):
        if record['dead_date']:
            if '?' in record['dead_date']:
                record['dead_date'] = self.replace_double_questionmarks(record['dead_date'])
            split_date = record['dead_date'].split('-')
            if int(split_date[1]) > 12 and int(split_date[2]) < 12:
                backup = split_date[2]
                split_date[2] = split_date[1]
                split_date[1] = backup
                record['dead_date'] = '-'.join(split_date)
            if int(split_date[2]) > 31:
                split_date[2] = '01'
                record['dead_date'] = '-'.join([split_date[0], split_date[1], split_date[2]])
            if int(split_date[1]) > 12:
                record['dead_date'] = '-'.join([split_date[0], '01', split_date[2]])
            return datetime.strptime(record['dead_date'], "%Y-%m-%d")
        for person in people:
            if person['rel'] == 'bur_main' and person['dead_date'] is not None:
                return datetime.strptime(person['dead_date'], "%Y-%m-%d")
        if record['burial_date']:
            if '?' in record['burial_date']:
                record['burial_date'] = self.replace_double_questionmarks(record['burial_date'])
            split_date = record['burial_date'].split('-')
            if int(split_date[1]) > 12 and int(split_date[2]) < 12:
                backup = split_date[2]
                split_date[2] = split_date[1]
                split_date[1] = backup
                record['burial_date'] = '-'.join(split_date)
            if int(split_date[2]) > 31:
                split_date[2] = '01'
                record['burial_date'] = '-'.join([split_date[0], split_date[1], split_date[2]])
            if int(split_date[1]) > 12:
                record['burial_date'] = '-'.join([split_date[0], '01', split_date[2]])
            if int(split_date[2]) > 28 and int(split_date[2]) <= 31 and split_date[1] == '02':
                record['burial_date'] = '-'.join([split_date[0], '03', split_date[2]])
            if int(split_date[2]) == 31 and (split_date[1] == '04' or split_date[1] == '06' or split_date[1] == '09' or split_date[1] == '11'):
                split_date[2] = '01'
                split_date[1] = str(int(split_date[1]) + 1)
                record['burial_date'] = '-'.join(split_date)
            return datetime.strptime(record['burial_date'], "%Y-%m-%d")
        return None

    def get_date_of_record_marriage(self, record):
        if record['marriage_date']:
            if '?' in record['marriage_date']:
                record['marriage_date'] = self.replace_double_questionmarks(record['marriage_date'])
            if not record['marriage_date']:
                return None
            split_date = record['marriage_date'].split('-')
            if int(split_date[1]) > 12 and int(split_date[2]) < 12:
                backup = split_date[2]
                split_date[2] = split_date[1]
                split_date[1] = backup
                record['marriage_date'] = '-'.join(split_date)
            if int(split_date[2]) > 31:
                split_date[2] = '01'
                record['marriage_date'] = '-'.join([split_date[0], split_date[1], split_date[2]])
            if int(split_date[1]) > 12:
                record['marriage_date'] = '-'.join([split_date[0], '01', split_date[2]])
            if int(split_date[2]) > 28 and int(split_date[2]) <= 31 and split_date[1] == '02':
                record['marriage_date'] = '-'.join([split_date[0], '03', split_date[2]])
            if int(split_date[2]) == 31 and (split_date[1] == '04' or split_date[1] == '06' or split_date[1] == '09' or split_date[1] == '11'):
                split_date[2] = '01'
                split_date[1] = str(int(split_date[1]) + 1)
                record['marriage_date'] = '-'.join(split_date)
            return datetime.strptime(record['marriage_date'], "%Y-%m-%d")
        return None

    def get_person_by_id(self, person_id):
        sql = "SELECT * FROM person WHERE birth_id = %s"
        person = self.select_one(sql, person_id)
        new_person = self.set_person(person)
        return new_person

    def set_register_municipality(self, register_db, register_new):
        municipality = []

        sql = "SELECT * FROM register_municip WHERE reg_id = %s"
        register_municipalities = self.select_multiple(sql, register_db["id"])

        for register_municipality in register_municipalities:
            if register_municipality is not None:
                sql = "SELECT * FROM municipality WHERE id = %s"
                municipality_table = self.select_one(sql, register_municipality["mun_id"])

                if municipality_table is not None:
                    municipality.append(municipality_table['name'])

        register_new.municipality = municipality

    def set_register_range(self, register_db, register_new):
        dates = []
        sql = "SELECT * FROM registerRange WHERE reg_id = %s"
        registerRanges = self.select_multiple(sql, register_db["id"])

        for registerRange in registerRanges:
            if registerRange is not None:
                date = {'date_from': registerRange['dtm_from'], 'date_to': registerRange['dtm_to']}
                if self.check_if_range_not_exist(dates, date):
                    dates.append(date)
        register_new.ranges = dates

    @staticmethod
    def check_if_range_not_exist(dates, date):
        if len(dates) == 0:
            return True
        for d in dates:
            if date["date_from"] == d['date_from'] and date["date_to"] == d['date_to']:
                return False
        return True

    def set_person_name(self, person_db, person_new, name_type):
        person_name = None
        person_normalized_name = None
        person_sex = None

        if name_type == 'person':
            sql = "SELECT * FROM person_name WHERE person_id = %s"
        else:  # type = marriage
            sql = "SELECT * FROM birthMarriage_name WHERE marr_id = %s"
        person_names = self.select_multiple(sql, person_db["id"])

        for person_name in person_names:
            sql = "SELECT * FROM name WHERE id = %s"
            name = self.select_one(sql, person_name["name_id"])
            if name['sex'] == '[M]':
                name['sex'] = 'M'
            elif name['sex'] == '[F]':
                name['sex'] = 'F'
            if name is not None:
                person_name = name['name']
                person_sex = name['sex']
                person_normalized_name = self.get_normalized_form("normalizedName", name["norm_name_id"])

        if self.check_variable_to_no_value(person_sex):
            person_new.sex.append(person_sex)
        if self.check_variable_to_no_value(person_name):
            person_new.name.append(person_name)
        if self.check_variable_to_no_value(person_normalized_name):
            person_new.name_normalized.append(person_normalized_name)

    # type can be person, confirmation, marriage
    def set_person_surname(self, person_db, person_new, surname_type):
        person_surname = None
        person_normalized_surname = None
        person_sex = None

        if surname_type == 'person':
            id_table = 'sname'
        elif surname_type == 'confirmation':
            id_table = 'confirmation_sname'
        else:  #marriage
            id_table = 'm_sname'

        sql = "SELECT * FROM surname WHERE id = %s"
        surname = self.select_one(sql, person_db[id_table])
        
        if surname:
            if surname['sex'] == '[M]':
                surname['sex'] = 'M'
            elif surname['sex'] == '[F]':
                surname['sex'] = 'F'
            person_sex = surname['sex']
            person_surname = surname['name']
            person_normalized_surname = self.get_normalized_form("normalizedSurname", surname["norm_name_id"])

        if self.check_variable_to_no_value(person_sex):
            person_new.sex.append(person_sex)

        if self.check_variable_to_no_value(person_surname):
            person_new.surname.append(person_surname)

        if self.check_variable_to_no_value(person_normalized_surname):
            person_new.surname_normalized.append(person_normalized_surname)

    def set_person_occupation(self, person_db, person_new, occupation_type):
        person_occupation = None
        person_normalized_occupation = None

        if occupation_type == 'person':
            sql = "SELECT * FROM person_occup WHERE person_id = %s"
        else:  # occupation_type == marriage
            sql = "SELECT * FROM birthMarriage_occup WHERE marr_id = %s"
        birth_occups = self.select_multiple(sql, person_db["id"])

        for birth_occup in birth_occups:
            sql = "SELECT * FROM occupation WHERE id = %s"
            occupation = self.select_one(sql, birth_occup["occup_id"])

            if occupation is not None:
                person_occupation = occupation['name']
                person_normalized_occupation = self.get_normalized_form("normalizedOccupation", occupation["norm_name_id"])
        if self.check_variable_to_no_value(person_occupation):
            person_new.occupation.append(person_occupation)
        if self.check_variable_to_no_value(person_normalized_occupation):
            person_new.occupation_normalized.append(person_normalized_occupation)

    def set_person_domicile(self, person_db, person_new):
        sql = "SELECT * FROM domicile WHERE id = %s"
        domicile = self.select_one(sql, person_db["domicile"])

        if domicile is not None:
            index = len(person_new.domicile)
            person_new.domicile.append(Domicile(domicile['id']))
            person_new.domicile[index].town = domicile['name']
            person_new.domicile[index].normalized_town = self.get_normalized_form("normalizedDomicile", domicile["norm_name_id"])
            person_new.domicile[index].street = person_db['street']
            person_new.domicile[index].street_number = person_db['descr_num']
            person_new.domicile[index].set_gps_coordinates(self.json_data)

    def set_person_relation(self, person_db, person_new):
        person_relation = None
        person_relation_normalized = None

        sql = "SELECT * FROM personRelation WHERE id = %s"
        relation = self.select_one(sql, person_db["person_relation"])

        if relation is not None:
            person_relation = relation['name']
            person_relation_normalized = self.get_normalized_form("normalizedPersonRelation", relation["norm_name_id"])

        if self.check_variable_to_no_value(person_relation):
            person_new.relation.append(person_relation)
        if self.check_variable_to_no_value(person_relation_normalized):
            person_new.relation_normalized.append(person_relation_normalized)

    def set_death_cause(self, person_db, person_new):
        person_death_cause = None

        sql = "SELECT * FROM burialDeathCause WHERE id = %s"
        death_cause = self.select_one(sql, person_db["death_cause"])

        if death_cause:
            person_death_cause = death_cause['name']

        if self.check_variable_to_no_value(person_death_cause):
            person_new.death_cause.append(person_death_cause)

    def get_normalized_form(self, table, table_id):
        if table_id is not None:
            sql = f"SELECT * FROM {table} WHERE id = {table_id}"
            self.cursor.execute(sql)
            normalized_name = self.cursor.fetchone()
            return normalized_name['name']

    @staticmethod
    def check_if_birthMarriage_is_not_none(marriage):
        if marriage["m_where"] is None and marriage["m_when"] is None and marriage["street"] is None and marriage["decr_num"] is None:
            return True
        else:
            return False

    def select_one(self, sql, variable):
        variable = (variable,)
        self.cursor.execute(sql, variable)
        variables = self.cursor.fetchall()
        if len(variables) > 1:
            raise ValueError('V selecte v relacnej databaze navratilo viac tabuliek ako jednu!')
        for var in variables:
            return var

    def select_multiple(self, sql, variable):
        variable = (variable,)
        self.cursor.execute(sql, variable)
        return self.cursor.fetchall()

    @staticmethod
    def set_sex_of_person(person):
        if len(person.sex) == 1:
            if person.sex[0] == 'U':
                if person.relation_normalized == 'father' or person.relation_normalized == 'fathersFather' or \
                        person.relation_normalized == 'mothersFather' or person.relation_normalized == 'fathersMothersFather' \
                        or person.relation_normalized == 'mothersMothersFather':
                    person.sex[0] = 'M'
                elif person.relation_normalized == 'mother' or person.relation_normalized == 'fathersMother' or \
                        person.relation_normalized == 'mothersMother' or person.relation_normalized == 'fathersMothersMother' \
                        or person.relation_normalized == 'mothersMothersMother':
                    person.sex[0] = 'F'

            if person.sex[0] == 'U':
                if person.relation == 'f' or person.relation == 'f_f' or person.relation == 'f_m_f' or \
                        person.relation == 'm_f' or person.relation == 'm_m_f' or person.relation == 'husband':
                    person.sex[0] = 'M'
                elif person.relation == 'm' or person.relation == 'f_m' or person.relation == 'f_m_m' or \
                        person.relation == 'm_m' or person.relation == 'm_m_m' or person.relation == 'midwife':
                    person.sex[0] = 'F'

            if person.sex[0] == '[M]':
                person.sex[0] = 'M'
            elif person.sex[0] == '[F]':
                person.sex[0] = 'F'

        person.sex = list(dict.fromkeys(person.sex))
        if len(person.sex) > 1 and 'U' in person.sex:
            person.sex.remove('U')

    @staticmethod
    def set_all_possible_info_register(register_db, register_new):
        register_new.archive = register_db['archive_id']
        register_new.fond = register_db['fond_id']
        register_new.signature = register_db['signature']
        register_new.languages.extend([register_db['lang1'], register_db['lang2'], register_db['lang3']])
        register_new.scan_count = register_db['scan_count']

    def set_all_possible_info_main_person_birth(self, person_db, person_new: Person):
        if self.check_variable_to_no_value(person_db['baptism_date']):
            person_db['baptism_date'] = datetime.strptime(person_db['baptism_date'], "%Y-%m-%d")
            person_new.baptism_date.append(person_db['baptism_date'])
            person_new.update_date_guess(person_db['baptism_date'], 'baptism')
        if self.check_variable_to_no_value(person_db['sex']):
            person_new.sex.append(person_db['sex'])
        if self.check_variable_to_no_value(person_db['legitimate']):
            person_new.legitimate.append(person_db['legitimate'])
        if self.check_variable_to_no_value(person_db['mult']):
            person_new.multiple_kids.append(person_db['mult'])
        if self.check_variable_to_no_value(person_db['confirmation_when']):
            person_db['confirmation_when'] = datetime.strptime(person_db['confirmation_when'], "%Y-%m-%d")
            person_new.confirmation_date.append(person_db['confirmation_when'])
            person_new.update_date_guess(person_db['confirmation_when'], 'confirmation')
        if self.check_variable_to_no_value(person_db['church_getoff']):
            person_db['church_getoff'] = datetime.strptime(person_db['church_getoff'], "%Y-%m-%d")
            person_new.church_get_off_date.append(person_db['church_getoff'])
            person_new.update_date_guess(person_db['church_getoff'], 'church_getoff')
        if self.check_variable_to_no_value(person_db['church_reenter']):
            person_db['church_reenter'] = datetime.strptime(person_db['church_reenter'], "%Y-%m-%d")
            person_new.church_reenter_date.append(person_db['church_reenter'])
            person_new.update_date_guess(person_db['church_reenter'], 'church_reenter')
        if self.check_variable_to_no_value(person_db['parents_marr_when']):
            person_db['parents_marr_when'] = datetime.strptime(person_db['parents_marr_when'], "%Y-%m-%d")
            person_new.parents_marriage_date.append(person_db['parents_marr_when'])

    def set_all_possible_info_main_person_burial(self, person_db, person_new: Person):
        if self.check_variable_to_no_value(person_db['sex']):
            person_new.sex.append(person_db['sex'])
        if self.check_variable_to_no_value(person_db['legitimate']):
            person_new.legitimate.append(person_db['legitimate'])
        if self.check_variable_to_no_value(person_db['dead_date']):
            if (type(person_db['dead_date']) == str):
                if '?' in person_db['dead_date']:
                    person_db['dead_date'] = self.replace_double_questionmarks(person_db['dead_date'])
                person_db['dead_date'] = datetime.strptime(person_db['dead_date'], "%Y-%m-%d")
            person_new.dead_date.append(person_db['dead_date'])
            person_new.update_date_guess(person_db['dead_date'], 'dead')
        if self.check_variable_to_no_value(person_db['dead_born']):
            person_new.dead_born.append(person_db['dead_born'])
        if self.check_variable_to_no_value(person_db['viaticum']):
            person_new.viaticum.append(person_db['viaticum'])
            if self.check_variable_to_no_value(person_db['viaticum_date']):
                if (type(person_db['viaticum_date']) == str):
                    if '?' in person_db['viaticum_date']:
                        person_db['viaticum_date'] = self.replace_double_questionmarks(person_db['viaticum_date'])
                    person_db['viaticum_date'] = datetime.strptime(person_db['viaticum_date'], "%Y-%m-%d")
                person_new.viaticum_date.append(person_db['viaticum_date'])
                person_new.update_date_guess(person_db['viaticum_date'], 'viaticum')
        if self.check_variable_to_no_value(person_db['burial_date']):
            if (type(person_db['burial_date']) == str):
                if '?' in person_db['burial_date']:
                    person_db['burial_date'] = self.replace_double_questionmarks(person_db['burial_date'])
                person_db['burial_date'] = datetime.strptime(person_db['burial_date'], "%Y-%m-%d")
            person_new.burial_date.append(person_db['burial_date'])
            person_new.update_date_guess(person_db['burial_date'], 'burial')
        if self.check_variable_to_no_value(person_db['baptised']):
            person_new.baptised.append(person_db['baptised'])
        self.set_death_cause(person_db, person_new)
        if self.check_variable_to_no_value(person_db['examination']):
            person_new.examination.append(person_db['examination'])
        if self.check_variable_to_no_value(person_db['marriage_date']):
            if (type(person_db['marriage_date']) == str):
                if '?' in person_db['marriage_date']:
                    person_db['marriage_date'] = self.replace_double_questionmarks(person_db['marriage_date'])
                person_db['marriage_date'] = datetime.strptime(person_db['marriage_date'], "%Y-%m-%d")
            person_new.marriage_date.append(person_db['marriage_date'])
            person_new.update_date_guess(person_db['marriage_date'], 'marriage')
        if self.check_variable_to_no_value(person_db['years']):
            if self.check_variable_to_no_value(person_db['dead_date']):
                person_new.update_date_guess(person_db['dead_date'] - relativedelta(years=int(person_db['years'])), 'born')
            elif self.check_variable_to_no_value(person_db['burial_date']):
                person_new.update_date_guess(person_db['burial_date'] - relativedelta(years=int(person_db['years'])), 'born')

    def set_all_possible_info_groom(self, person_db, person_new: Person):
        if self.check_variable_to_no_value(person_db['marriage_date']):
            person_db['marriage_date'] = datetime.strptime(person_db['marriage_date'], "%Y-%m-%d")
            person_new.marriage_date.append(person_db['marriage_date'])
            person_new.update_date_guess(person_db['marriage_date'], 'marriage')
            if self.check_variable_to_no_value(person_db['groom_age_year']):
                if self.check_variable_to_no_value(person_db['groom_age_month']):
                    if self.check_variable_to_no_value(person_db['groom_age_day']):
                        person_new.birth_date = [person_new.marriage_date[-1] - relativedelta(years=int(person_db['groom_age_year']), months=int(person_db['groom_age_month']), days=int(person_db['groom_age_day']))]
                    else:
                        person_new.birth_date = [person_new.marriage_date[-1] - relativedelta(years=int(person_db['groom_age_year']), months=int(person_db['groom_age_month']))]
                else:
                    person_new.birth_date = [person_new.marriage_date[-1] - relativedelta(years=int(person_db['groom_age_year']))]
        if self.check_variable_to_no_value(person_db['divorce_date']):
            person_db['divorce_date'] = datetime.strptime(person_db['divorce_date'], "%Y-%m-%d")
            person_new.divorce_date.append(person_db['divorce_date'])
            person_new.update_date_guess(person_db['divorce_date'], 'marriage')
        person_new.sex = ['M']
        if self.check_variable_to_no_value(person_db['kinship_degree']):
            person_new.kinship_degree.append(person_db['kinship_degree'])

    def set_all_possible_info_bride(self, person_db, person_new: Person):
        if self.check_variable_to_no_value(person_db['marriage_date']):
            person_db['marriage_date'] = datetime.strptime(person_db['marriage_date'], "%Y-%m-%d")
            person_new.marriage_date.append(person_db['marriage_date'])
            person_new.update_date_guess(person_db['marriage_date'], 'marriage')
            if self.check_variable_to_no_value(person_db['bride_age_year']):
                if self.check_variable_to_no_value(person_db['bride_age_month']):
                    if self.check_variable_to_no_value(person_db['bride_age_day']):
                        person_new.birth_date = [person_new.marriage_date[-1] - relativedelta(years=int(person_db['bride_age_year']), months=int(person_db['bride_age_month']), days=int(person_db['bride_age_day']))]
                    else:
                        person_new.birth_date = [person_new.marriage_date[-1] - relativedelta(years=int(person_db['bride_age_year']), months=int(person_db['bride_age_month']))]
                else:
                    person_new.birth_date = [person_new.marriage_date[-1] - relativedelta(years=int(person_db['bride_age_year']))]
        if self.check_variable_to_no_value(person_db['divorce_date']):
            person_db['divorce_date'] = datetime.strptime(person_db['divorce_date'], "%Y-%m-%d")
            person_new.divorce_date.append(person_db['divorce_date'])
            person_new.update_date_guess(person_db['divorce_date'], 'marriage')
        person_new.sex = ['F']
        if self.check_variable_to_no_value(person_db['kinship_degree']):
            person_new.kinship_degree.append(person_db['kinship_degree'])

    def set_all_possible_info_person(self, person_db, person_new, type):
        if self.check_variable_to_no_value(person_db['title']):
            person_new.title.append(person_db['title'])
        if self.check_variable_to_no_value(person_db['religion']):
            person_new.religion.append(person_db['religion'])
        if self.check_variable_to_no_value(person_db['birth_date']):
            if '?' in person_db['birth_date']:
                person_db['birth_date'] = self.replace_double_questionmarks(person_db['birth_date'])
            try:
                person_db['birth_date'] = datetime.strptime(person_db['birth_date'], "%Y-%m-%d")
            except:
                split_date = person_db['birth_date'].split('-')
                if int(split_date[1]) == 2 and int(split_date[2]) > 28:
                    split_date[2] = '01'
                    split_date[1] = str(int(split_date[1]) + 1)
            person_new.birth_date.append(person_db['birth_date'])
        if self.check_variable_to_no_value(person_db['dead_date']):
            if '?' in person_db['dead_date']:
                person_db['dead_date'] = self.replace_double_questionmarks(person_db['dead_date'])
            person_db['dead_date'] = datetime.strptime(person_db['dead_date'], "%Y-%m-%d")
            person_new.dead_date.append(person_db['dead_date'])
        if self.check_variable_to_no_value(person_db['dead']):
            person_new.father_dead_flag.append(person_db['dead'])
        if self.check_variable_to_no_value(person_db['waif']):
            person_new.waif_flag.append(person_db['waif'])
        if self.check_variable_to_no_value(person_db['rel']):
            if type == 'burial':
                person_db['rel'] = self.normalize_role_burial(person_db['rel'])
            person_new.relation_enum.append(person_db['rel'])

    def normalize_role_burial(self, rel):
        if rel == 'bur_main':
            return 'main'
        elif rel == 'bur_f':
            return 'f'
        elif rel == 'bur_m':
            return 'm'
        elif rel == 'bur_f_f':
            return 'f_f'
        elif rel == 'bur_f_m':
            return 'f_m'
        elif rel == 'bur_m_f':
            return 'm_f'
        elif rel == 'bur_m_m':
            return 'm_m'
        else:
            return rel

    @staticmethod
    def replace_double_questionmarks(date):
        arr = date.split('-')
        if '?' in arr[0]:
            arr[0] = arr[0].replace('?', '0')
        if arr[0] == '':
            return None
        if arr[1] == '?' or arr[1] == '??':
            arr[1] = "01"
        elif '?' in arr[1]:
            if arr[1][0] == '?' and arr[1][1] != '0':
                char = arr[1][1]
                arr[1] = '0' + char
            elif arr[1][0] == '?' and arr[1][1] == '0':
                arr[1] = '10'
            if arr[1][1] == '?':
                char = arr[1][0]
                arr[1] = char + '1'
        if arr[2] == '?' or arr[2] == '??':
            arr[2] = "01"
        elif '?' in arr[2]:
            if arr[2][0] == '?':
                char = arr[2][1]
                arr[2] = '1'+char
            if arr[2][1] == '?':
                char = arr[2][0]
                arr[2] = char+'1'
        if int(arr[1]) > 12 and int(arr[2]) < 12:
            backup = arr[2]
            arr[2] = arr[1]
            arr[1] = backup
        else:
            
            if int(arr[1]) > 12:
                arr[1] = '01'
            if int(arr[2]) > 28 and int(arr[2]) <= 31 and arr[1] == '02':
                arr[1] = '03'
            elif int(arr[2]) > 31:
                arr[2] = '01'
            elif int(arr[2]) == 31 and (arr[1] == '04' or arr[1] == '06' or arr[1] == '09' or arr[1] == '11'):
                arr[1] = '01'
        return "-".join(arr)

    @staticmethod
    def guess_date_according_to_role_birth(date, person):
        if person.relation_enum[0] == 'main':
            person.update_date_guess(date, 'born')
        if person.relation_enum[0] == 'f':
            person.update_date_guess(date, 'father')
        if person.relation_enum[0] == 'm':
            person.update_date_guess(date, 'mother')
        if person.relation_enum[0] == 'midwife' or person.relation_enum[0] == 'granted':
            person.update_date_guess(date, 'granted')
        if person.relation_enum[0] == 'f_f' or person.relation_enum[0] == 'f_m' or person.relation_enum[0] == 'm_f' or person.relation_enum[0] == 'm_m':
            person.update_date_guess(date, 'grand_parent')
        if person.relation_enum[0] == 'f_m_f' or person.relation_enum[0] == 'f_m_m' or person.relation_enum[0] == 'm_m_f' or person.relation_enum[0] == 'm_m_m':
            person.update_date_guess(date, 'grand_grand_parent')
        if person.relation_enum[0] == 'gf_1' or person.relation_enum[0] == 'gf_2' or person.relation_enum[0] == 'gf_3' or person.relation_enum[0] == 'gf_4':
            person.update_date_guess(date, 'parent')
        if person.relation_enum[0] == 'gfrel_1' or person.relation_enum[0] == 'gfrel_2' or person.relation_enum[0] == 'gfrel_3' or person.relation_enum[0] == 'gfrel_4':
            person.update_date_guess(date, 'parent')
        if person.relation_enum[0] == 'husband':
            person.update_date_guess(date, 'mariage')

    @staticmethod
    def guess_date_according_to_role_burial(date, person):
        if person.relation_enum[0] == 'main':
            person.update_date_guess(date, 'dead')
        if person.relation_enum[0] == 'f':
            person.update_date_guess(date, 'father')
        if person.relation_enum[0] == 'm':
            person.update_date_guess(date, 'mother')
        if person.relation_enum[0] == 'bur_examinator' or person.relation_enum[0] == 'bur_gravedigger' or person.relation_enum[0] == 'bur_keeper':
            person.update_date_guess(date, 'granted')
        if person.relation_enum[0] == 'm_f' or person.relation_enum[0] == 'm_m' or person.relation_enum[0] == 'f_m' or person.relation_enum[0] == 'f_f':
            person.update_date_guess(date, 'grand_parent')
        if person.relation_enum[0] == 'bur_husband' or person.relation_enum[0] == 'bur_wife':
            person.update_date_guess(date, 'mariage')

    @staticmethod
    def guess_date_according_to_role_marriage(date, person):
        if person.relation_enum[0] == 'mar_groom' or person.relation_enum[0] == 'mar_bride' or person.relation_enum[0] == 'mar_bestman' or person.relation_enum[0] == 'mar_bridesmaid':
            person.update_date_guess(date, 'marriage')
        if person.relation_enum[0] == 'mar_g_f' or person.relation_enum[0] == 'mar_b_f':
            person.update_date_guess(date, 'father_marriage')
        if person.relation_enum[0] == 'mar_g_m' or person.relation_enum[0] == 'mar_b_m':
            person.update_date_guess(date, 'mother_marriage')
        if person.relation_enum[0] == 'mar_priest' or person.relation_enum[0] == 'mar_speaker':
            person.update_date_guess(date, 'granted')
        if person.relation_enum[0] == 'mar_widow' or person.relation_enum[0] == 'mar_widower':
            person.update_date_guess(date, 'dead')
        if person.relation_enum[0] == 'mar_b_m_f' or person.relation_enum[0] == 'mar_b_m_m' or person.relation_enum[0] == 'mar_b_f_m' or person.relation_enum[0] == 'mar_b_f_f' or person.relation_enum[0] == 'mar_g_m_f' or person.relation_enum[0] == 'mar_g_m_m' or person.relation_enum[0] == 'mar_g_f_m' or person.relation_enum[0] == 'mar_g_f_f':
            person.update_date_guess(date, 'grand_parent_marriage')
        


    @staticmethod
    def set_all_possible_info_marriage(person_db, person_new):
        person_new.num = person_db["num"]
        person_new.date = person_db["m_when"]
        person_new.place = person_db["m_where"]
        person_new.num = person_db["num"]

    @staticmethod
    def check_variable_to_no_value(variable):
        if (not variable) or (variable == 'None') or (variable == 'none'):
            return False
        return True
