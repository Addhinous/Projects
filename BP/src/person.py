from datetime import datetime
from dateutil.relativedelta import relativedelta
from copy import deepcopy
import json
# Modul s triedou 'Person', ktora reprezentuje osobu z matrik

class Person:

    def __init__(self, id_person=None):
        self.id = id_person
        self.id_test = []
        self.compared = False
        self.title = []
        self.name = []
        self.name_normalized = []
        self.surname = []
        self.surname_normalized = []
        self.sex = []
        self.occupation = []
        self.occupation_normalized = []
        self.domicile = []
        self.all_dates = []
        self.birth_date = []
        self.birth_date_guess = {
            "from": None,
            "to": None,
            "correct": False
        }
        self.religion = []
        self.waif_flag = []
        self.father_dead_flag = []
        self.relation_enum = []
        self.relation = []
        self.relation_normalized = []
        self.dead_date = []
        self.dead_date_guess = {
            "from": None,
            "to": None,
            "correct": False
        }
        self.church_get_off_date = []
        self.church_reenter_date = []
        self.confirmation_date = []
        self.marriage = []
        self.baptised = []
        self.baptism_date = []
        self.legitimate = []
        self.multiple_kids = []
        self.parents_marriage_date = []
        self.burial_date = []
        self.death_cause = []
        self.viaticum = []
        self.marriage_date = []
        self.examination = []
        self.viaticum_date = []
        self.dead_born = []
        self.divorce_date = []
        self.kinship_degree = []
        ##############################################
        self.relationships = [] #List slovnikov reprezentujucich vsetky vztahy veduce z uzlu osoby, okrem vztahov potencionalnych zhod
        self.relationships_to = [] #List slovnikov reprezentujucich vsetky vztahy veduce do uzlu osoby, vratane vztahov potencionalnych zhod
        self.potential_matches = [] #List slovnikov reprezentujucich vsetky vztahy potencionalnych zhod veducich z uzlu osoby

    # Funkcia vypocita novy odhad datumov narodenia/umrtia osoby na zaklade jej ulohy v zazname. Nasledne funkcia vola funkciu pre aktualizovanie rozsahu
    def update_date_guess(self, date, date_type):
        if date:
            if date_type == 'dead':
                self.set_birth_guess_date(date - relativedelta(years=100), date)
                self.dead_date_guess['from'] = date
                self.dead_date_guess['to'] = date
                self.dead_date_guess['correct'] = True

            elif date_type == 'born':
                self.birth_date_guess['from'] = date
                self.birth_date_guess['to'] = date
                self.birth_date_guess['correct'] = True
                self.set_dead_guess_date(date, date + relativedelta(years=100))

            else:
                new_death_guess_date_from = date
                if date_type == 'baptism':
                    new_birth_guess_date_to = date
                    new_birth_guess_date_from = date - relativedelta(months=1)
                    new_death_guess_date_to = date + relativedelta(years=100)
                elif date_type == 'granted' or date_type == 'midwife':
                    new_birth_guess_date_to = date - relativedelta(years=20)
                    new_birth_guess_date_from = date - relativedelta(years=80)
                    new_death_guess_date_to = date + relativedelta(years=80)
                elif date_type == 'grand_parent':
                    new_birth_guess_date_to = date - relativedelta(years=30)
                    new_birth_guess_date_from = date - relativedelta(years=70)
                    new_death_guess_date_to = date + relativedelta(years=70)
                elif date_type == 'grand_grand_parent':
                    new_birth_guess_date_to = date - relativedelta(years=45)
                    new_birth_guess_date_from = date - relativedelta(years=55)
                    new_death_guess_date_to = date + relativedelta(years=55)
                elif date_type == 'mother':
                    new_birth_guess_date_to = date - relativedelta(years=15)
                    new_birth_guess_date_from = date - relativedelta(years=45)
                    new_death_guess_date_to = date + relativedelta(years=85)
                elif date_type == 'father':
                    new_birth_guess_date_to = date - relativedelta(years=15)
                    new_birth_guess_date_from = date - relativedelta(years=55)
                    new_death_guess_date_to = date + relativedelta(years=85)
                elif date_type == 'grand_parent_marriage':
                    new_birth_guess_date_to = date - relativedelta(years=45)
                    new_birth_guess_date_from = date - relativedelta(years=85)
                    new_death_guess_date_to = date + relativedelta(years=55)
                elif date_type == 'mother_marriage':
                    new_birth_guess_date_to = date - relativedelta(years=30)
                    new_birth_guess_date_from = date - relativedelta(years=60)
                    new_death_guess_date_to = date + relativedelta(years=70)
                elif date_type == 'father_marriage':
                    new_birth_guess_date_to = date - relativedelta(years=30)
                    new_birth_guess_date_from = date - relativedelta(years=70)
                    new_death_guess_date_to = date + relativedelta(years=70)
                elif date_type == 'viaticum':
                    new_birth_guess_date_from = self.birth_date_guess['from']
                    new_birth_guess_date_to = date
                    new_death_guess_date_to = date + relativedelta(months=1)
                elif date_type == 'burial':
                    new_birth_guess_date_from = self.birth_date_guess['from']
                    new_birth_guess_date_to = date
                    new_death_guess_date_to = date
                    new_death_guess_date_from = date - relativedelta(months=1)
                else:  # date_type == 'confirmation' or date_type == 'marriage' or date_type == 'parent':
                    new_birth_guess_date_to = date - relativedelta(years=15)
                    new_birth_guess_date_from = date - relativedelta(years=85)
                    new_death_guess_date_to = date + relativedelta(years=85)

                self.set_birth_guess_date(new_birth_guess_date_from, new_birth_guess_date_to)
                self.set_dead_guess_date(new_death_guess_date_from, new_death_guess_date_to)
                
    # Metoda pre aktualizovanie odhadu datumu narodenia osoby. Ako parametre dostane nove vypocitane rozsahy odhadu,
    # ktore nasledne porovna s aktualnym rozsahom odhadu a ako novy rozsah sa nastavi najpresnejsi odhad (tzn. najmensi casovy interval aky mame)
    def set_birth_guess_date(self, new_birth_guess_date_from, new_birth_guess_date_to):
        if not self.birth_date_guess['correct']:
            if self.birth_date_guess['from'] is not None:
                if self.birth_date_guess['from'] < new_birth_guess_date_from:
                    self.birth_date_guess['from'] = new_birth_guess_date_from
            else:
                self.birth_date_guess['from'] = new_birth_guess_date_from

            if self.birth_date_guess['to'] is not None:
                if self.birth_date_guess['to'] > new_birth_guess_date_to:
                    self.birth_date_guess['to'] = new_birth_guess_date_to
            else:
                self.birth_date_guess['to'] = new_birth_guess_date_to

    # Metoda pre aktualizovanie odhadu datumu umrtia osoby. Ako parametre dostane nove vypocitane rozsahy odhadu,
    # ktore nasledne porovna s aktualnym rozsahom odhadu a ako novy rozsah sa nastavi najpresnejsi odhad (tzn. najmensi casovy interval aky mame)
    def set_dead_guess_date(self, date, new_death_guess_date_to):
        if not self.dead_date_guess['correct']:
            if self.dead_date_guess['from'] is not None:
                if self.dead_date_guess['from'] < date:
                    self.dead_date_guess['from'] = date
            else:
                self.dead_date_guess['from'] = date

            if self.dead_date_guess['to'] is not None:
                if self.dead_date_guess['to'] < new_death_guess_date_to:
                    self.dead_date_guess['to'] = new_death_guess_date_to
            else:
                self.dead_date_guess['to'] = new_death_guess_date_to


    # Metoda pre zjednotenie dvoch odhadov pre casovy interval. Vysledkom je casovy odhad rovnakeho formatu vytvoreny
    # prienikom dvoch vstupnych intervalov pre ziskanie najuzsieho rozsahu odhadu
    @staticmethod
    def merge_two_date_guess(date_guess_1, date_guess_2):
        date_guess = {
            "from": None,
            "to": None,
            "correct": False
        }

        if date_guess_1['correct']:
            date_guess = date_guess_1
        elif date_guess_2['correct']:
            date_guess = date_guess_2
        # Pridana kontrola pre chybajuce datumy, kedze niektore zaznamy v databaze nemaju uvedeny ziaden datum
        ########################################################################################
        elif date_guess_1['from'] == None or date_guess_1['to'] == None or date_guess_2['from'] == None or date_guess_2['to'] == None:
            if date_guess_1['from'] != None and date_guess_2['from'] != None:
                if date_guess_1['from'] < date_guess_2['from']:
                    date_guess['from'] = date_guess_2['from']
                else:
                    date_guess['from'] = date_guess_1['from']
            elif date_guess_1['from'] == None and date_guess_2['from'] != None:
                date_guess['from'] = date_guess_2['from']
            elif date_guess_1['from'] != None and date_guess_2['from'] == None:
                date_guess['from'] = date_guess_1['from']
            else:
                date_guess['from'] = None
            
            if date_guess_1['to'] != None and date_guess_2['to'] != None:
                if date_guess_1['to'] < date_guess_2['to']:
                    date_guess['to'] = date_guess_1['to']
                else:
                    date_guess['to'] = date_guess_2['to']
            elif date_guess_1['to'] == None and date_guess_2['to'] != None:
                date_guess['to'] = date_guess_2['to']
            elif date_guess_1['to'] != None and date_guess_2['to'] == None:
                date_guess['to'] = date_guess_1['to']
            else:
                date_guess['to'] = None
        ########################################################################################  
        else:
            if date_guess_1['from'] < date_guess_2['from']:
                date_guess['from'] = date_guess_2['from']
            else:
                date_guess['from'] = date_guess_1['from']

            if date_guess_1['to'] < date_guess_2['to']:
                date_guess['to'] = date_guess_1['to']
            else:
                date_guess['to'] = date_guess_2['to']

        return date_guess

    # Metoda vracia retazec v jazyku Cypher s vsetkymi hodnotami atributov osoby. Retazec je nasledne mozne pouzit pre vytvorenie
    # uzlu s danou osobou v grafovej databaze Neo4j.
    def create_node_person(self):
        guess_born = [self.birth_date_guess['from'], self.birth_date_guess['to']]
        guess_dead = [self.dead_date_guess['from'], self.dead_date_guess['to']]
        return "".join(["CREATE (a:Osoba {id_relačná_databáza:['",str(self.id),"'], ",
                        "id_cvs_testovanie:", self.add_list_to_graph_db(self.id_test), ", ",
                        "titul:", self.add_list_to_graph_db(self.title), ", ",
                        "jméno:", self.add_list_to_graph_db(self.name), ", ",
                        "normalizované_jméno:", self.add_list_to_graph_db(self.name_normalized), ", ",
                        "příjmení:", self.add_list_to_graph_db(self.surname), ", ",
                        "normalizované_příjmení:", self.add_list_to_graph_db(self.surname_normalized), ", ",
                        "pohlaví:", self.add_list_to_graph_db(self.sex), ", ",
                        "povolaní:", self.add_list_to_graph_db(self.occupation), ", ",
                        "normalizované_povolaní:", self.add_list_to_graph_db(self.occupation_normalized), ", ",
                        "datum_narodení:", self.add_list_date_to_cql(self.birth_date), ", ",
                        "odhad_narodení:", self.add_list_date_to_cql(guess_born), ", ",
                        "viera:", self.add_list_to_graph_db(self.religion), ", ",
                        "nalezenec:", self.add_list_to_graph_db(self.waif_flag), ", ",
                        "otec_mrtev:", self.add_list_to_graph_db(self.father_dead_flag), ", ",
                        "datum_úmrtí:", self.add_list_date_to_cql(self.dead_date), ", ",
                        "odhad_úmrtí:", self.add_list_date_to_cql(guess_dead), ", ",
                        "datum_vystoupení_z_církve:", self.add_list_date_to_cql(self.church_get_off_date), ", ",
                        "datum_návratu_do_církve:", self.add_list_date_to_cql(self.church_reenter_date), ", ",
                        "datum_biřmován:", self.add_list_date_to_cql(self.confirmation_date), ", ",
                        "datum_křtu:", self.add_list_date_to_cql(self.baptism_date), ", ",
                        "manželské:", self.add_list_to_graph_db(self.legitimate), ", ",
                        "vícerčatá:", self.add_list_to_graph_db(self.multiple_kids),", ",
                        "datum_pohřbu:", self.add_list_date_to_cql(self.burial_date), ", "
                        "příčina_úmrtí:", self.add_list_to_graph_db(self.death_cause), ", ",
                        "viatikum:", self.add_list_to_graph_db(self.viaticum), ", ",
                        "datum_viatika:", self.add_list_date_to_cql(self.viaticum_date), ", ",
                        "mrtvěrozené:", self.add_list_to_graph_db(self.dead_born), ", ",
                        "datum_sňatku:", self.add_list_date_to_cql(self.marriage_date), ", ",
                        "prohlídka_tela:", self.add_list_to_graph_db(self.examination), ", ",
                        "datum_rozvodu:", self.add_list_date_to_cql(self.divorce_date), "})\nset a.id = id(a)\n"])

    # Metoda pre aktualizaciu atributov osoby pri zjednocovani uzlov osob. Atributy osoby predanej parametrom su pridane do atributov (listy) prvej osoby.
    def update_node_info(self, person_new):
        self.check_person()
        if person_new.id_test and len(person_new.id_test) > 0 and person_new.id_test[0] not in self.id_test:
            self.id_test.append(person_new.id_test[0])
        if person_new.title and len(person_new.title) > 0 and person_new.title[0] not in self.title:
            self.title.append(person_new.title[0])
        if person_new.name and len(person_new.name) > 0 and person_new.name[0] not in self.name:
            self.name.append(person_new.name[0])
        if person_new.name_normalized and len(person_new.name_normalized) > 0 and person_new.name_normalized[0] not in self.name_normalized:
            self.name_normalized.append(person_new.name_normalized[0])
        if person_new.surname and len(person_new.surname) > 0 and person_new.surname[0] not in self.surname:
            self.surname.append(person_new.surname[0])
        if person_new.surname_normalized and len(person_new.surname_normalized) > 0 and person_new.surname_normalized[0] not in self.surname_normalized:
            self.surname_normalized.append(person_new.surname_normalized[0])
        if person_new.sex and len(person_new.sex) > 0 and person_new.sex[0] not in self.sex:
            self.sex.append(person_new.sex[0])
        if person_new.occupation and len(person_new.occupation) > 0 and person_new.occupation[0] not in self.occupation:
            self.occupation.append(person_new.occupation[0])
        if person_new.occupation_normalized and len(person_new.occupation_normalized) > 0 and person_new.occupation_normalized[0] not in self.occupation_normalized:
            self.occupation_normalized.append(person_new.occupation_normalized[0])
        if person_new.birth_date and len(person_new.birth_date) > 0 and person_new.birth_date[0] not in self.birth_date:
            self.birth_date.append(person_new.birth_date[0])
            self.birth_date = list(filter(None, self.birth_date))
        if person_new.birth_date_guess:
            self.birth_date_guess = self.merge_two_date_guess(self.birth_date_guess, person_new.birth_date_guess)
        if person_new.religion and len(person_new.religion) > 0 and person_new.religion[0] not in self.religion:
            self.religion.append(person_new.religion[0])
        if person_new.waif_flag and len(person_new.waif_flag) > 0 and person_new.waif_flag[0] not in self.waif_flag:
            self.waif_flag.append(person_new.waif_flag[0])
        if person_new.father_dead_flag and len(person_new.father_dead_flag) > 0 and person_new.father_dead_flag[0] not in self.father_dead_flag:
            self.father_dead_flag.append(person_new.father_dead_flag[0])
        if person_new.dead_date and len(person_new.dead_date) > 0 and person_new.dead_date[0] not in self.dead_date:
            self.dead_date.append(person_new.dead_date[0])
            self.dead_date = list(filter(None, self.dead_date))
        if person_new.dead_date_guess:
            self.dead_date_guess = self.merge_two_date_guess(self.dead_date_guess, person_new.dead_date_guess)
        if person_new.church_get_off_date and len(person_new.church_get_off_date) > 0 and person_new.church_get_off_date[0] not in self.church_get_off_date:
            self.church_get_off_date.append(person_new.church_get_off_date[0])
            self.church_get_off_date = list(filter(None, self.church_get_off_date))
        if person_new.church_reenter_date and len(person_new.church_reenter_date) > 0 and person_new.church_reenter_date[0] not in self.church_reenter_date:
            self.church_reenter_date.append(person_new.church_reenter_date[0])
            self.church_reenter_date = list(filter(None, self.church_reenter_date))
        if person_new.confirmation_date and len(person_new.confirmation_date) > 0 and person_new.confirmation_date[0] not in self.confirmation_date:
            self.confirmation_date.append(person_new.confirmation_date[0])
            self.confirmation_date = list(filter(None, self.confirmation_date))
        if person_new.baptism_date and len(person_new.baptism_date) > 0 and person_new.baptism_date[0] not in self.baptism_date:
            self.baptism_date.append(person_new.baptism_date[0])
            self.baptism_date = list(filter(None, self.baptism_date))
        if person_new.legitimate and len(person_new.legitimate) > 0 and person_new.legitimate[0] not in self.legitimate:
            self.legitimate.append(person_new.legitimate[0])
        if person_new.multiple_kids and len(person_new.multiple_kids) > 0 and person_new.multiple_kids[0] not in self.multiple_kids:
            self.multiple_kids.append(person_new.multiple_kids[0])
        if person_new.burial_date and len(person_new.burial_date) > 0 and person_new.burial_date[0] not in self.burial_date:
            self.burial_date.append(person_new.burial_date[0])
            self.burial_date = list(filter(None, self.burial_date))
        if person_new.death_cause and len(person_new.death_cause) > 0 and person_new.death_cause[0] not in self.death_cause:
            self.death_cause.append(person_new.death_cause[0])
        if person_new.viaticum and len(person_new.viaticum) > 0 and person_new.viaticum[0] not in self.viaticum:
            self.viaticum.append(person_new.viaticum[0])
        if person_new.marriage_date and len(person_new.marriage_date) > 0 and person_new.marriage_date[0] not in self.marriage_date:
            self.marriage_date.append(person_new.marriage_date[0])
            self.marriage_date = list(filter(None, self.marriage_date))
        if person_new.examination and len(person_new.examination) > 0 and person_new.examination[0] not in self.examination:
            self.examination.append(person_new.examination[0])
        if person_new.viaticum_date and len(person_new.viaticum_date) > 0 and person_new.viaticum_date[0] not in self.viaticum_date:
            self.viaticum_date.append(person_new.viaticum_date[0])
            self.viaticum_date = list(filter(None, self.viaticum_date))
        if person_new.dead_born and len(person_new.dead_born) > 0 and person_new.dead_born[0] not in self.dead_born:
            self.dead_born.append(person_new.dead_born[0])
        if person_new.divorce_date and len(person_new.divorce_date) > 0 and person_new.divorce_date[0] not in self.divorce_date:
            self.divorce_date.append(person_new.divorce_date[0])
            self.divorce_date = list(filter(None, self.divorce_date))

    def check_person(self):
        if self.id_test is None:
            self.id_test = []
        if self.title is None:
            self.title = []
        if self.name is None:
            self.name = []
        if self.name_normalized is None:
            self.name_normalized = []
        if self.name_normalized is None:
            self.name_normalized = []
        if self.surname_normalized is None:
            self.surname_normalized = []
        if self.sex is None:
            self.sex = []
        if self.occupation is None:
            self.occupation = []
        if self.occupation_normalized is None:
            self.occupation_normalized = []
        if self.birth_date is None:
            self.birth_date = []
        if self.religion is None:
            self.religion = []
        if self.waif_flag is None:
            self.waif_flag = []
        if self.father_dead_flag is None:
            self.father_dead_flag = []
        if self.dead_date is None:
            self.dead_date = []
        if self.church_get_off_date is None:
            self.church_get_off_date = []
        if self.church_reenter_date is None:
            self.church_reenter_date = []
        if self.confirmation_date is None:
            self.confirmation_date = []
        if self.baptism_date is None:
            self.baptism_date = []
        if self.legitimate is None:
            self.legitimate = []
        if self.multiple_kids is None:
            self.multiple_kids = []

    @staticmethod
    def add_list_to_graph_db(list_variables):
        string = "["
        for i in list_variables:
            string = "".join([string, "'", str(i), "', "])
        if len(list_variables) > 0:
            string = string[:-2]
        string += "]"
        return string

    @staticmethod
    def print_domicile(domicile):
        for dom in domicile:
            if dom is not None:
                dom.print_address()

    def get_person_from_graph_db(self, person):
        self.id = person.get('id')
        self.id_test = person.get('id_cvs_testovanie')
        self.title = person.get('titul')
        self.name = person.get('jméno')
        self.name_normalized = person.get('normalizované_jméno')
        self.surname = person.get('příjmení')
        self.surname_normalized = person.get('normalizované_příjmení')
        self.sex = person.get('pohlaví')
        self.occupation = person.get('povolaní')
        self.occupation_normalized = person.get('normalizované_povolaní')
        self.birth_date = self.get_list_of_dates(person.get('datum_narodení'))
        new_date_birth_from = datetime.strptime(person.get('odhad_narodení')[0], "%d %m %Y")
        self.birth_date_guess['from'] = new_date_birth_from
        new_date_birth_to = datetime.strptime(person.get('odhad_narodení')[1], "%d %m %Y")
        self.birth_date_guess['to'] = new_date_birth_to
        if self.birth_date_guess['from'] == self.birth_date_guess['to']:
            self.birth_date_guess['correct'] = True
        else:
            self.birth_date_guess['correct'] = False
        self.religion = person.get('viera')
        self.waif_flag = person.get('nalezenec')
        self.father_dead_flag = person.get('otec_mrtev')
        self.dead_date = self.get_list_of_dates(person.get('datum_úmrtí'))
        new_date_dead_from = datetime.strptime(person.get('odhad_úmrtí')[0], "%d %m %Y")
        self.dead_date_guess['from'] = new_date_dead_from
        new_date_dead_to = datetime.strptime(person.get('odhad_úmrtí')[1], "%d %m %Y")
        self.dead_date_guess['to'] = new_date_dead_to
        if self.dead_date_guess['from'] == self.dead_date_guess['to']:
            self.dead_date_guess['correct'] = True
        else:
            self.dead_date_guess['correct'] = False
        self.church_get_off_date = self.get_list_of_dates(person.get('datum_vystoupení_z_církve'))
        self.church_reenter_date = self.get_list_of_dates(person.get('datum_návratu_do_církve'))
        self.confirmation_date = self.get_list_of_dates(person.get('datum_biřmován'))
        self.legitimate = person.get('manželské')
        self.multiple_kids = person.get('vícerčatá')
        self.burial_date = self.get_list_of_dates(person.get('datum_pohřbu'))
        self.death_cause = person.get("příčina_úmrtí")
        self.viaticum = person.get('viaticum')
        self.marriage_date = self.get_list_of_dates(person.get('datum_sňatku'))
        self.examination = person.get('prohlídka_tela')
        self.viaticum_date = self.get_list_of_dates(person.get('datum_viatika'))
        self.dead_born = person.get('mrtvěrozené')
        self.divorce_date = self.get_list_of_dates(person.get("datum_rozvodu"))
    
    @staticmethod
    def get_list_of_dates(list_unprocessed_dates):
        result = []
        for date in list_unprocessed_dates:
            result.append(datetime.strptime(date, '%d %m %Y'))
        return result

    @staticmethod
    def add_list_date_to_cql(dates):
        string = "["
        for date in dates:
            if date != None:
                string += "'"
                if not date.day:
                    string += " - "
                else:
                    string += str(date.day) + " "
                if not date.month:
                    string += " - "
                else:
                    string += str(date.month) + " "
                if not date.year:
                    string += " - ', "
                else:
                    string += str(date.year) + "', "                    
            else:
                string += "'None', "
        if len(dates) > 0:
            string = string[:-2]
        string += "]"
        return string

    # Metoda na kontrolu ci dana rola v zazname je zastupena osobou.
    # V pripade ze je aspon jedno policko danej roly vyplnene vracia True, inak False
    def not_empty(self):
        if len(self.name) != 0:
            return True
        if len(self.surname) != 0:
            return True
        if len(self.occupation) != 0:
            return True
        if len(self.occupation_normalized) != 0:
            return True
        if len(self.surname_normalized) != 0:
            return True
        if len(self.name_normalized) != 0:
            return True
        return False

    def print_date(self, date, type, tabs):
        for d in date:
            if d is not None:
                print("")
                self.print_tabs(tabs)
                print(type + ' date = ' + d.strftime("%d.%m.%Y")), 

    def print_czech(self, tabs=0):
        print("")
        self.print_tabs(tabs)
        print('ID = ' + str(self.id), end="")
        self.print_variable('ID', self.title, tabs)
        self.print_variable('Titul', self.title, tabs)
        self.print_variable('Jméno', self.name, tabs)
        self.print_variable_normalized(self.name_normalized)
        self.print_variable('Přímení', self.surname, tabs)
        self.print_variable_normalized(self.surname_normalized)
        self.print_variable('Pohlaví', self.sex, tabs)
        self.print_variable('Povolání', self.occupation, tabs)
        self.print_variable_normalized(self.occupation_normalized)
        if self.domicile:
            print("")
            self.print_tabs(tabs)
            print('Adresy = ', end=""), self.print_domicile(self.domicile)
            print("")
        self.print_date(self.birth_date, 'Birth', tabs)
        self.print_variable('Vyznání', self.religion, tabs)
        self.print_date(self.dead_date, 'Datum úmrtí', tabs)
        self.print_date(self.church_get_off_date, 'Datum vystoupení z cirkve', tabs)
        self.print_date(self.church_reenter_date, 'Datum znovavstoupení do cirkve', tabs)
        self.print_date(self.confirmation_date, 'Datum konfirmace', tabs)
        self.print_date(self.baptism_date, 'Datum křtu', tabs)
        self.print_date(self.parents_marriage_date, 'Datum sňatku rodiču', tabs)
        self.print_variable('Manželské', self.legitimate, tabs)
        self.print_variable('Vícerčata', self.multiple_kids, tabs)
        self.print_variable('Otec mrtev', self.father_dead_flag, tabs)
        self.print_variable('Nalezenec', self.waif_flag, tabs)
        print('\n')

    def print_czech_cvs(self, tabs=0):
        self.print_variable('ID', self.id, tabs)
        self.print_variable('Jméno', self.name_normalized, tabs)
        self.print_variable('Přímení', self.surname_normalized, tabs)
        self.print_variable('Pohlaví', self.sex, tabs)
        self.print_variable('Povolání', self.occupation_normalized, tabs)
        if self.domicile is not None and len(self.domicile) != 0:
            print("")
            self.print_tabs(tabs)
            print('Adresy = ', end=""), self.print_domicile(self.domicile)
            print("")
        self.print_date(self.birth_date, 'Birth', tabs)
        self.print_variable('Vyznání', self.religion, tabs)
        self.print_variable('Manželské', self.legitimate, tabs)
        self.print_variable('Vícerčata', self.multiple_kids, tabs)
        self.print_variable('Otec mrtev', self.father_dead_flag, tabs)
        self.print_variable('Nalezenec', self.waif_flag, tabs)
        print('\n')

    def person_json(self,):
        addresses = []
        for dom in self.domicile:
            address = []
            if dom.town:
                address.append(dom.town)
            if dom.street:
                address.append(dom.street)
            if dom.street_number:
                address.append(dom.street_number)
            addresses.append(deepcopy(address))
        person_set = {
                        "id": self.id, 
                        "titul": self.title,
                        "jméno": self.name,
                        "normalizované_jméno": self.name_normalized,
                        "příjmení": self.surname,
                        "normalizované_příjmení": self.surname_normalized,
                        "pohlaví": self.sex,
                        "povolaní": self.occupation,
                        "normalizované_povolaní": self.occupation_normalized,
                        "adresy": addresses,
                        "datum_narodení": self.birth_date,
                        "viera": self.religion,
                        "datum_úmrtí": self.dead_date,
                        "datum_vystoupení_z_církve": self.church_get_off_date,
                        "datum_návratu_do_církve": self.church_reenter_date,
                        "manželské": self.legitimate,
                        "vícerčatá": self.multiple_kids,
                        "otec_mrtev": self.father_dead_flag,
                        "nalezenec": self.waif_flag
                     }
        return json.dumps(person_set, indent = 4, sort_keys=True, ensure_ascii=False)

    def person_json_family(self,):
        addresses = []
        for dom in self.domicile:
            address = []
            if dom.town:
                address.append(dom.town)
            if dom.street:
                address.append(dom.street)
            if dom.street_number:
                address.append(dom.street_number)
            addresses.append(deepcopy(address))
        person_set = {
                        "id": self.id, 
                        "titul": self.title,
                        "jméno": self.name,
                        "normalizované_jméno": self.name_normalized,
                        "příjmení": self.surname,
                        "normalizované_příjmení": self.surname_normalized,
                        "pohlaví": self.sex,
                        "povolaní": self.occupation,
                        "normalizované_povolaní": self.occupation_normalized,
                        "adresy": addresses,
                        "datum_narodení": datetime.strftime(self.birth_date[0], "%d.%m.%Y") if len(self.birth_date) > 0 else [],
                        "viera": self.religion,
                        "datum_úmrtí": datetime.strftime(self.dead_date[0], "%d.%m.%Y") if len(self.dead_date) > 0 else [],
                        "datum_vystoupení_z_církve": datetime.strftime(self.church_get_off_date[0], "%d.%m.%Y") if len(self.church_get_off_date) > 0 else [],
                        "datum_návratu_do_církve": datetime.strftime(self.church_reenter_date[0], "%d.%m.%Y") if len(self.church_reenter_date) > 0 else [],
                        "manželské": self.legitimate,
                        "vícerčatá": self.multiple_kids,
                        "otec_mrtev": self.father_dead_flag,
                        "nalezenec": self.waif_flag
                     }
        return person_set

    def print_variable_normalized(self, variable):
        if variable is not None and len(variable) != 0:
            print('- ', end=""), self.print_list(variable)

    def print_variable(self, name, variable, tabs=0):
        if variable is not None and len(variable) != 0:
            print("")
            self.print_tabs(tabs)
            print(name + ' = ', end=""), self.print_list(variable)

    @staticmethod
    def print_tabs(tabs):
        while tabs:
            tabs -= 1
            print("\t", end="")

    @staticmethod
    def print_list(words):
        if words is not None:
            for word in words[:-1]:
                print(str(word) + ', ',  end="")
            print(str(words[-1]) + ' ', end="")

    def person_print(self):
        print('.................................')
        print('      ID = ', end='')
        for i in self.id:
            print(' ' + str(i), end='')
        print('')
        print('      Title = ' + str(self.title))
        print('      Name = ' + str(self.name))
        print('      Normalized name = ' + str(self.name_normalized))
        print('      Surname = ' + str(self.surname))
        print('      Normalized surname = ' + str(self.surname_normalized))
        print('      Sex = ' + str(self.sex))
        print('      Occupation = ' + str(self.occupation))
        print('      Normalized occupation = ' + str(self.occupation_normalized))
        self.print_domicile(self.domicile)
        self.print_date(self.birth_date, 'Birth', 0)
        print('      Relation = ' + str(self.relation))
