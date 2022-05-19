from copy import deepcopy
from record import TypeOfRecord
from person import Person
from record import Record
from enum import Enum
from domicile import Domicile
import uuid
import gc



# Trieda reprezentujuca uzly a vztahy databazy neo4j pomocou python objektov.
class DataRepresentation:
    def __init__(self,):
        self.registers = []
        self.records = []
        self.people = []
        self.towns = []
        self.women = []
        self.men = []
        self.undefined = []
        self.current = []

    # Metoda ulozi zaznam do listu zaznamov a v pripade ze matrika z ktorej zaznam pochadza este nie je ulozena v liste 
    # matrik, prida tuto matriku do listu.
    def save_record(self, record):
        self.records.append(record)
        if record.register.id is not None:
            for register in self.registers:
                if self.compare_registers(register, record.register):
                    return
            self.registers.append(record.register)

    # Metoda pre porovnanie dvoch matrik
    def compare_registers(self, reg1, reg2):
        if reg1.id != reg2.id or reg1.archive != reg2.archive or reg1.fond != reg2.fond or reg1.signature != reg2.signature or reg1.languages != reg2.languages or reg1.scan_count != reg2.scan_count or reg1.municipality != reg2.municipality or reg1.ranges != reg2.ranges:
            return False
        return True

    # Metoda pre pridane novo vzniknutej osoby do zoznamu vsetkych osob aj do zoznamu osob urciteho pohlavia.
    # Ak adresa osoby este nie je v strukture reprezentujucej mesta/ulice/popis. c. tak sa tam tato adresa vlozi
    def create_person(self, person_old):
        person = deepcopy(person_old)
        self.people.append(person)
        self.current.append(person)
        if len(person.sex) == 1:
            if person.sex[0] == 'F' or person.sex[0] == 'Z':
                self.women.append(person)
            elif person.sex[0] == 'M':
                self.men.append(person)
            else:
                self.undefined.append(person)
        elif len(person.sex) == 2:
            if (person.sex[0] == 'Z' and person.sex[1] == 'F') or (person.sex[0] == 'F' and person.sex[1] == 'Z'):
                self.women.append(person)
            else:
                self.undefined.append(person)
        else:
            self.undefined.append(person)
            
        for domicile in person.domicile:
            self.create_domicile(domicile)
            if person.all_dates[-1] != None:
                domicile.date = person.all_dates[-1].strftime("%d.%m.%Y")

    # Metoda pre aktualizovanie osoby pri spajani dvoch uzlov osob
    def update_person(self, old, new):
        for person in self.people:
            if person == old:
                person.update_node_info(new)
                return person                    

    # Metoda skontroluje ci dana adresa uz v strukture adries existuje a v pripade ze nie tak ju tam vlozi
    def create_domicile(self, domicile):
        num_tuple = None
        street_tuple = None
        if domicile is not None:
            if domicile.street_number:
                num_tuple = (domicile.street_number, uuid.uuid4())
                domicile.street_number = num_tuple
            if domicile.street:
                street_tuple = (str(domicile.street), uuid.uuid4())
                domicile.street = street_tuple
            if domicile.normalized_town:
                if domicile.street:
                    if domicile.street_number:
                        for town in self.towns:
                            if town["normalized_name"] == domicile.normalized_town:
                                for street in town["streets"]:
                                    if street["street_name"][0] == domicile.street[0]:
                                        for num in street["numbers"]:
                                            if num[0] == domicile.street_number[0]:
                                                return
                                        street["numbers"].append(num_tuple)
                                        return
                                town["streets"].append({"street_name": street_tuple, "numbers": [num_tuple]})
                                return
                        self.towns.append({"id": uuid.uuid4(), "name": domicile.town, "normalized_name": domicile.normalized_town, "gps": domicile.gps_coordinates, "streets": [{"street_name": street_tuple, "numbers": [num_tuple]}], "numbers": []})
                        return
                    else:
                        for town in self.towns:
                            if town["normalized_name"] == domicile.normalized_town:
                                for street in town["streets"]:
                                    if street["street_name"][0] == domicile.street[0]:
                                        return
                                town["streets"].append({"street_name": street_tuple, "numbers": []})
                                return
                        self.towns.append({"id": uuid.uuid4(), "name": domicile.town, "normalized_name": domicile.normalized_town, "gps": domicile.gps_coordinates, "streets": [{"street_name": street_tuple, "numbers": []}], "numbers": []})
                        return
                else:
                    if domicile.street_number:
                        for town in self.towns:
                            if town["normalized_name"] == domicile.normalized_town:
                                for num in town["numbers"]:
                                    if num[0] == domicile.street_number[0]:
                                        return
                                town["numbers"].append(num_tuple)
                                return
                        self.towns.append({"id": uuid.uuid4(), "name": domicile.town, "normalized_name": domicile.normalized_town, "gps": domicile.gps_coordinates, "streets": [], "numbers": [num_tuple]})
                        return
                    else:
                        for town in self.towns:
                            if town["normalized_name"] == domicile.normalized_town:
                                return
                        self.towns.append({"id": uuid.uuid4(), "name": domicile.town, "normalized_name": domicile.normalized_town, "gps": domicile.gps_coordinates, "streets": [], "numbers": []})
                        return
            elif domicile.town:
                if domicile.street:
                    if domicile.street_number:
                        for town in self.towns:
                            if town["name"] == domicile.town:
                                for street in town["streets"]:
                                    if street["street_name"][0] == domicile.street[0]:
                                        for num in street["numbers"]:
                                            if num[0] == domicile.street_number[0]:
                                                return
                                        street["numbers"].append(num_tuple)
                                        return
                                town["streets"].append({"street_name": street_tuple, "numbers": [num_tuple]})
                                return
                        self.towns.append({"id": uuid.uuid4(), "name": domicile.town, "normalized_name": domicile.normalized_town, "gps": domicile.gps_coordinates, "streets": [{"street_name": street_tuple, "numbers": [num_tuple]}], "numbers": []})
                        return
                    else:
                        for town in self.towns:
                            if town["name"] == domicile.town:
                                for street in town["streets"]:
                                    if street["street_name"][0] == domicile.street[0]:
                                        return
                                town["streets"].append({"street_name": street_tuple, "numbers": []})
                                return
                        self.towns.append({"id": uuid.uuid4(), "name": domicile.town, "normalized_name": domicile.normalized_town, "gps": domicile.gps_coordinates, "streets": [{"street_name": street_tuple, "numbers": []}], "numbers": []})
                        return
                else:
                    if domicile.street_number:
                        for town in self.towns:
                            if town["name"] == domicile.town:
                                for num in town["numbers"]:
                                    if num[0] == domicile.street_number[0]:
                                        return
                                town["numbers"].append(num_tuple)
                                return
                        self.towns.append({"id": uuid.uuid4(), "name": domicile.town, "normalized_name": domicile.normalized_town, "gps": domicile.gps_coordinates, "streets": [], "numbers": [num_tuple]})
                        return
                    else:
                        for town in self.towns:
                            if town["name"] == domicile.town:
                                return
                        self.towns.append({"id": uuid.uuid4(), "name": domicile.town, "normalized_name": domicile.normalized_town, "gps": domicile.gps_coordinates, "streets": [], "numbers": []})
                        return

    # Metoda vrati vsetky osoby vo vztahu potencionalnej zhody ku osobe predanej parametrom
    def get_potential_matches_of_person_from_graph_db(self, person_id):
        matches = []
        person = None
        for p in self.people:
            if p.id == person_id:
                person = p
                break
        if not person:
            return matches

        for relationship in person.potential_matches:
            matches.append(relationship["person"])
        return matches

    # Metoda pre zjednotenia dvoch uzlov osob. Najprv je osoba odstranena z listov osob, nasledne su odstranene vztahy medzi
    # oboma uzlami osob a vsetky vztahy odstranenej osoby su presunute na prvu osobu. Na zaver sa zostavajuca osoba aktualizuje
    # o udaje odstranenej osoby
    def unite_potential_matches_nodes(self, person1_id, person2_id):
        person1 = person2 = None

        for person in self.people:
            if person.id == person1_id:
                person1 = person
            if person.id == person2_id:
                person2 = person
            if person1 and person2:
                break

        if person2 in self.women:
            self.women.remove(person2)
        if person2 in self.men:
            self.men.remove(person2)
        if person2 in self.undefined:
            self.undefined.remove(person2)
        self.people.remove(person2)
 
        for match in person1.potential_matches:
            if match["person"].id == person2_id:
                person1.potential_matches.remove(match)
                break

        for match in person2.potential_matches:
            if match["person"].id == person1.id:
                person2.potential_matches.remove(match)
                break

        for match in list(person2.potential_matches):
            for rel in list(match["person"].potential_matches):
                if rel["person"].id == person2.id:
                    for rel2 in match["person"].potential_matches:
                        if rel2["person"].id == person1.id:
                            if rel["score"] > rel2["score"]:
                                match["person"].potential_matches.remove(rel2)
                                rel["person"] = person1
                                break
                            else:
                                match["person"].potential_matches.remove(rel)
                                rel2["score"] = rel["score"]
                                break
                    else:
                        person1.potential_matches.append(match)
                        rel["person"] = person1

        for relationship in person2.relationships_to:
            for rel in relationship["person"].relationships:
                if rel['type'] == 'MANŽEL_ZESNULÉHO' \
                    or rel['type'] == 'MANŽELKA_ZESNULÉHO' \
                    or rel["type"] == "KŘTENEC" \
                    or rel["type"] == "OTEC" \
                    or rel["type"] == "MATKA" \
                    or rel["type"] == "PORODNI_BABA" \
                    or rel["type"] == "KŘTITEL" \
                    or rel["type"] == "OTCUV_OTEC" \
                    or rel["type"] == "OTCOVA_MATKA" \
                    or rel["type"] == "MATCIN_OTEC" \
                    or rel["type"] == "MATCINA_MATKA" \
                    or rel["type"] == "OTEC_MATCINHO_OTCA" \
                    or rel["type"] == "OTEC_MATCINY_MATKY" \
                    or rel["type"] == "MATKA_MATCINHO_OTCA" \
                    or rel["type"] == "MATKA_MATCINY_MATKY" \
                    or rel["type"] == "KMOTR" \
                    or rel["type"] == "PRIBUZNY_KMOTRA" \
                    or rel["type"] == "SYN_ZESNULÉHO" \
                    or rel["type"] == "DCERA_ZESNULÉHO" \
                    or rel["type"] == "PŘÍBUZNÝ_ZESNULÉHO" \
                    or rel["type"] == "HROBNÍK" \
                    or rel["type"] == "ZAOPATŘOVATEL" \
                    or rel["type"] == "ZESNULÝ" \
                    or rel['type'] == 'ŽENÍCH' \
                    or rel['type'] == 'NEVĚSTA' \
                    or rel['type'] == 'SVĚDEK' \
                    or rel['type'] == 'ODDÁVAJÍCÍ' \
                    or rel['type'] == 'DRUŽIČKA' \
                    or rel['type'] == 'ŽENICHUV_SVĚDEK' \
                    or rel['type'] == 'NEVĚSTINA_MATKA' \
                    or rel['type'] == 'NEVĚSTIN_OTEC' \
                    or rel['type'] == 'MATKA_NEVĚSTINY_MATKY' \
                    or rel['type'] == 'OTEC_NEVĚSTINY_MATKY' \
                    or rel['type'] == 'MATKA_NEVĚSTINA_OTCE' \
                    or rel['type'] == 'OTEC_NEVĚSTINA_OTCE' \
                    or rel['type'] == 'ŽENICHOVA_MATKA' \
                    or rel['type'] == 'ŽENICHUV_OTEC' \
                    or rel['type'] == 'MATKA_ŽENICHOVY_MATKY' \
                    or rel['type'] == 'OTEC_ŽENICHOVY_MATKY' \
                    or rel['type'] == 'MATKA_ŽENICHOVA_OTCE' \
                    or rel['type'] == 'OTEC_ŽENICHOVA_OTCE' \
                    or rel['type'] == 'NEVĚSTIN_ZESNULÝ_MANŽEL' \
                    or rel['type'] == 'ŽENICHOVA_ZESNULÁ_ŽENA' \
                    or rel["type"] == "MANZEL_MATKY":
                    continue
                if rel["person"].id == person2.id:
                    rel["person"] = person1
            person1.relationships_to.append(relationship)

        for relationship in person2.relationships:
            person1.relationships.append(relationship)

        person1.update_node_info(person2)
        del(person2)
        gc.collect()
        
    # Metoda pre aktualizovanie vztahu potencionalnej zhody medzi dvoma osobami s novou pravdepodobnostou zhody.
    def update_potential_matches_relationship(self, person1_id, person2_id, result):
        person1 = None
        for person in self.people:
            if person.id == person1_id:
                person1 = person
        if not person1:
            return
        for match in person1.potential_matches:
            if match["person"].id == person2_id:
                match["score"] = result

    # Metoda pre zmazanie vztahu potencionalnej zhody medzi dvoma osobami
    def delete_potential_matches_relationship(self, person1_id, person2_id):
        person1 = None
        for person in self.people:
            if person.id == person1_id:
                person1 = person
                break
        
        for match in person1.potential_matches:
            if match["person"].id == person2_id:
                person1.potential_matches.remove(match)
                break

    # Metoda prepoji osobu so zaznamom
    def connect_person_and_record(self, person, record,  relationship, date):
        if {"type": relationship, "record": record, "date": date} not in person.relationships:
            person.relationships.append({"type": relationship, "record": record, "date": date})

    @staticmethod
    def get_date_from_main_person_birth(persons):
        for person in persons:
            if person.relation_enum[0] == 'main':
                if len(person.birth_date) > 0:
                    if person.birth_date[0]:
                        return person.birth_date[-1]
                    else:
                        return person.baptism_date[-1]

    @staticmethod
    def get_date_from_main_person_burial(persons):
        for person in persons:
            if person.relation_enum[0] == 'main':
                if len(person.dead_date) > 0:
                    if person.dead_date[0]:
                        return person.dead_date[-1]
                    else:
                        return person.burial_date[-1]

    @staticmethod
    def get_date_from_main_person_marriage(persons):
        for person in persons:
            if person.relation_enum[0] == 'mar_groom' or person.relation_enum == 'mar_braid':
                if len(person.marriage_date) > 0:
                    return person.marriage_date[-1]

    # Metoda na prepojenie dvoch ludi
    def connect_two_people(self, person1, person2, relationship):
        if not person1 or not person2:
            return
        if {"type": relationship, "person": person2} not in person1.relationships:
            person1.relationships.append({"type": relationship, "person": person2})
        if {"type": relationship, "person": person1} not in person2.relationships_to:
            person2.relationships_to.append({"type": relationship, "person": person1})

    # Vytvorenie vsetkych vztahov zo zaznamu o krste
    def create_connection_with_person_in_birth_record(self, persons, record):
        main = father = mother = mother_father = mother_mother = None
        goth_father_1 = goth_father_2 = goth_father_3 = goth_father_4 = None
        date = self.get_date_from_main_person_birth(persons)
        for person in persons:
            if person.relation_enum[0] == 'main':
                main = person
                self.connect_person_and_record(main, record, "KŘTENEC", date)
        for person in persons:
            if person.relation_enum[0] == 'f':
                father = person
                self.connect_two_people(father, main, "JE_OTEC")
                self.connect_person_and_record(father, record, "OTEC", date)
            elif person.relation_enum[0] == 'm':
                mother = person
                self.connect_two_people(mother, main, "JE_MATKA")
                self.connect_person_and_record(mother, record, "MATKA", date)
            elif person.relation_enum[0] == 'midwife':
                midwife = person
                self.connect_two_people(midwife, main, "ODRODILA")
                self.connect_person_and_record(midwife, record, "PORODNI_BABA", date)
            elif person.relation_enum[0] == 'granted':
                granted = person
                self.connect_two_people(granted, main, "KŘTIL")
                self.connect_person_and_record(granted, record, "KŘTITEL", date)
            elif person.relation_enum[0] == 'f_f':
                father_father = person
                self.connect_two_people(father_father, father, "JE_OTEC")
                self.connect_person_and_record(father_father, record, "OTCUV_OTEC", date)
            elif person.relation_enum[0] == 'f_m':
                father_mother = person
                self.connect_two_people(father_mother, father, "JE_MATKA")
                self.connect_person_and_record(father_mother, record, "OTCOVA_MATKA", date)
            elif person.relation_enum[0] == 'm_f':
                mother_father = person
                self.connect_two_people(mother_father, mother, "JE_OTEC")
                self.connect_person_and_record(mother_father, record, "MATCIN_OTEC", date)
            elif person.relation_enum[0] == 'm_m':
                mother_mother = person
                self.connect_two_people(mother_mother, mother, "JE_MATKA")
                self.connect_person_and_record(mother_mother, record, "MATCINA_MATKA", date)
            elif person.relation_enum[0] == 'f_m_f':
                father_mother_father = person
                self.connect_two_people(father_mother_father, mother_father, "JE_OTEC")
                self.connect_person_and_record(father_mother_father, record, "OTEC_MATCINHO_OTCA", date)
            elif person.relation_enum[0] == 'f_m_m':
                father_mother_mother = person
                self.connect_two_people(father_mother_mother, mother_mother, "JE_OTEC")
                self.connect_person_and_record(father_mother_mother, record, "OTEC_MATCINY_MATKY", date)
            elif person.relation_enum[0] == 'm_m_f':
                mother_mother_father = person
                self.connect_two_people(mother_mother_father, mother_father, "JE_MATKA")
                self.connect_person_and_record(mother_mother_father, record, "MATKA_MATCINHO_OTCA", date)
            elif person.relation_enum[0] == 'm_m_m':
                mother_mother_mother = person
                self.connect_two_people(mother_mother_mother, mother_mother, "JE_MATKA")
                self.connect_person_and_record(mother_mother_mother, record, "MATKA_MATCINY_MATKY", date)
            elif person.relation_enum[0] == 'gf_1':
                goth_father_1 = person
                self.connect_two_people(goth_father_1, main, "JE_KMOTR")
                self.connect_person_and_record(goth_father_1, record, "KMOTR", date)
            elif person.relation_enum[0] == 'gf_2':
                goth_father_2 = person
                self.connect_two_people(goth_father_2, main, "JE_KMOTR")
                self.connect_person_and_record(goth_father_2, record, "KMOTR", date)
            elif person.relation_enum[0] == 'gf_3':
                goth_father_3 = person
                self.connect_two_people(goth_father_3, main, "JE_KMOTR")
                self.connect_person_and_record(goth_father_3, record, "KMOTR", date)
            elif person.relation_enum[0] == 'gf_4':
                goth_father_4 = person
                self.connect_two_people(goth_father_4, main, "JE_KMOTR")
                self.connect_person_and_record(goth_father_4, record, "KMOTR", date)
            elif person.relation_enum[0] == 'gfrel_1':
                goth_father_relative_1 = person
                self.connect_two_people(goth_father_relative_1, goth_father_1, "JE_PRÍBUZNÝ")
                self.connect_person_and_record(goth_father_relative_1, record, "PRIBUZNY_KMOTRA", date)
            elif person.relation_enum[0] == 'gfrel_2':
                goth_father_relative_2 = person
                self.connect_two_people(goth_father_relative_2, goth_father_2, "JE_PRÍBUZNÝ")
                self.connect_person_and_record(goth_father_relative_2, record, "PRIBUZNY_KMOTRA", date)
            elif person.relation_enum[0] == 'gfrel_3':
                goth_father_relative_3 = person
                self.connect_two_people(goth_father_relative_3, goth_father_3, "JE_PRÍBUZNÝ")
                self.connect_person_and_record(goth_father_relative_3, record, "PRIBUZNY_KMOTRA", date)
            elif person.relation_enum[0] == 'gfrel_4':
                goth_father_relative_4 = person
                self.connect_two_people(goth_father_relative_4, goth_father_4, "JE_PRÍBUZNÝ")
                self.connect_person_and_record(goth_father_relative_4, record, "PRIBUZNY_KMOTRA", date)
            elif person.relation_enum[0] == 'husband':
                husband = person
                self.connect_two_people(husband, mother, "JSOU_MANŽELÉ")
                self.connect_person_and_record(husband, record, "MANZEL_MATKY", date)

    # Vytvorenie vsetkych prepojeni zo zaznamu o umrti
    def create_connection_with_person_in_burial_record(self, persons, record):
        main = father = mother = mother_father = mother_mother = None
        date = self.get_date_from_main_person_burial(persons)
        for person in persons:
            if person.relation_enum[0] == 'main':
                main = person
                self.connect_person_and_record(main, record, "ZESNULÝ", date)
        for person in persons:
            if person.relation_enum[0] == 'f':
                father = person
                self.connect_two_people(father, main, "JE_OTEC")
                self.connect_person_and_record(father, record, "OTEC", date)
            elif person.relation_enum[0] == 'm':
                mother = person
                self.connect_two_people(mother, main, "JE_MATKA")
                self.connect_person_and_record(mother, record, "MATKA", date)
            elif person.relation_enum[0] == 'f_f':
                father_father = person
                self.connect_two_people(father_father, father, "JE_OTEC")
                self.connect_person_and_record(father_father, record, "OTCUV_OTEC", date)
            elif person.relation_enum[0] == 'f_m':
                father_mother = person
                self.connect_two_people(father_mother, father, "JE_MATKA")
                self.connect_person_and_record(father_mother, record, "OTCOVA_MATKA", date)
            elif person.relation_enum[0] == 'm_f':
                mother_father = person
                self.connect_two_people(mother_father, mother, "JE_OTEC")
                self.connect_person_and_record(mother_father, record, "MATCIN_OTEC", date)
            elif person.relation_enum[0] == 'm_m':
                mother_mother = person
                self.connect_two_people(mother_mother, mother, "JE_MATKA")
                self.connect_person_and_record(mother_mother, record, "MATCINA_MATKA", date)
            elif person.relation_enum[0] == 'bur_husband':
                husband = person
                self.connect_two_people(husband, main, "JSOU_MANŽELÉ")
                self.connect_person_and_record(husband, record, "MANŽEL_ZESNULÉHO", date)
            elif person.relation_enum[0] == 'bur_wife':
                wife = person
                self.connect_two_people(wife, main, "JSOU_MANŽELÉ")
                self.connect_person_and_record(wife, record, "MANŽELKA_ZESNULÉHO", date)
            elif person.relation_enum[0] == 'bur_son':
                son = person
                self.connect_two_people(main, son, "JE_OTEC")
                self.connect_person_and_record(son, record, "SYN_ZESNULÉHO", date)
            elif person.relation_enum[0] == 'bur_daughter':
                daughter = person
                self.connect_two_people(main, daughter, "JE_OTEC")
                self.connect_person_and_record(daughter, record, "DCERA_ZESNULÉHO", date)
            elif person.relation_enum[0] == 'bur_rel1':
                relative = person
                self.connect_two_people(relative, main, "JE_PŘÍBUZNÝ")
                self.connect_person_and_record(relative, record, "PŘÍBUZNÝ_ZESNULÉHO", date)
            elif person.relation_enum[0] == 'bur_gravedigger':
                self.connect_two_people(person, main, "POCHOVAL")
                self.connect_person_and_record(person, record, "HROBNÍK", date)
            elif person.relation_enum[0] == 'bur_keeper':
                keeper = person
                self.connect_two_people(keeper, main, "ZAOPATŘIL")
                self.connect_person_and_record(keeper, record, "ZAOPATŘOVATEL", date)

    # Vytvorenie vsetkych prepojeni zo zaznamu o sobasi
    def create_connection_with_person_in_marriage_record(self, persons, record):
        groom = bride = groom_mother = groom_father = groom_mother_mother = groom_mother_father = None
        groom_father_mother = groom_father_father = bride_mother = bride_father = bride_mother_mother = None
        bride_mother_father = bride_father_mother = bride_father_father = bestman = bridesmaid = None
        date = self.get_date_from_main_person_marriage(persons)
        for person in persons:
            if person.relation_enum[0] == 'mar_groom':
                groom = person
                self.connect_person_and_record(groom, record, "ŽENÍCH", date)
            elif person.relation_enum[0] == 'mar_bride':
                bride = person
                self.connect_person_and_record(bride, record, "NEVĚSTA", date)
            elif person.relation_enum[0] == 'mar_g_f':
                groom_father = person
                self.connect_person_and_record(groom_father, record, "ŽENICHUV_OTEC", date)
            elif person.relation_enum[0] == 'mar_g_m':
                groom_mother = person
                self.connect_person_and_record(groom_mother, record, "ŽENICHOVA_MATKA", date)
            elif person.relation_enum[0] == 'mar_b_f':
                bride_father = person
                self.connect_person_and_record(bride_father, record, "NEVĚSTIN_OTEC", date)
            elif person.relation_enum[0] == 'mar_b_m':
                bride_mother = person
                self.connect_person_and_record(bride_mother, record, "NEVĚSTINA_MATKA", date)
            elif person.relation_enum[0] == 'mar_priest':
                self.connect_person_and_record(person, record, "ODDÁVAJÍCÍ", date)
        for person in persons:
            if person.relation_enum[0] == 'mar_groom':
                self.connect_two_people(groom, bride, "JE_MANŽEL")
            elif person.relation_enum[0] == 'mar_bride':
                self.connect_two_people(bride, groom, "JE_MANŽELKA")
            elif person.relation_enum[0] == 'mar_g_f':
                self.connect_two_people(groom_father, groom, "JE_OTEC")
            elif person.relation_enum[0] == 'mar_g_m':
                self.connect_two_people(groom_mother, groom, "JE_MATKA")
            elif person.relation_enum[0] == 'mar_g_f_m':
                groom_father_mother = person
                self.connect_two_people(groom_father_mother, groom_father, "JE_MATKA")
                self.connect_person_and_record(groom_father_mother, record, "MATKA_ŽENICHOVA_OTCE", date)
            elif person.relation_enum[0] == 'mar_g_f_f':
                groom_father_father = person
                self.connect_two_people(groom_father_father, groom_father, "JE_OTEC")
                self.connect_person_and_record(groom_father_father, record, "OTEC_ŽENICHOVA_OTCE", date)
            elif person.relation_enum[0] == 'mar_g_m_m':
                groom_mother_mother = person
                self.connect_two_people(groom_mother_mother, groom_mother, "JE_MATKA")
                self.connect_person_and_record(groom_mother_mother, record, "MATKA_ŽENICHOVY_MATKY", date)
            elif person.relation_enum[0] == 'mar_g_m_f':
                groom_mother_father = person
                self.connect_two_people(groom_mother_father, groom_mother, "JE_OTEC")
                self.connect_person_and_record(groom_mother_father, record, "OTEC_ŽENICHOVY_MATKY", date)
            elif person.relation_enum[0] == 'mar_b_f':
                self.connect_two_people(bride_father, bride, "JE_OTEC")
            elif person.relation_enum[0] == 'mar_b_m':
                self.connect_two_people(bride_mother, bride, "JE_MATKA")
            elif person.relation_enum[0] == 'mar_b_f_m':
                bride_father_mother = person
                self.connect_two_people(bride_father_mother, bride_father, "JE_MATKA")
                self.connect_person_and_record(bride_father_mother, record, "MATKA_NEVĚSTINA_OTCE", date)
            elif person.relation_enum[0] == 'mar_b_f_f':
                bride_father_father = person
                self.connect_two_people(bride_father_father, bride_father, "JE_OTEC")
                self.connect_person_and_record(bride_father_father, record, "OTEC_NEVĚSTINA_OTCE", date)
            elif person.relation_enum[0] == 'mar_b_m_m':
                bride_mother_mother = person
                self.connect_two_people(bride_mother_mother, bride_mother, "JE_MATKA")
                self.connect_person_and_record(bride_mother_mother, record, "MATKA_NEVĚSTINY_MATKY", date)
            elif person.relation_enum[0] == 'mar_b_m_f':
                bride_mother_father = person
                self.connect_two_people(bride_mother_father, bride_mother, "JE_OTEC")
                self.connect_person_and_record(bride_mother_father, record, "OTEC_NEVĚSTINY_MATKY", date)
            elif person.relation_enum[0] == 'mar_bestman':
                bestman = person
                self.connect_two_people(bestman, groom, "BYL_SVĚDEK")
                self.connect_person_and_record(bestman, record, "ŽENICHUV_SVĚDEK", date)
            elif person.relation_enum[0] == 'mar_bridesmaid':
                bridesmaid = person
                self.connect_two_people(bridesmaid, bride, "BYLA_DRUŽIČKOU")
                self.connect_person_and_record(bridesmaid, record, "DRUŽIČKA", date)
            elif person.relation_enum[0] == 'mar_sv_1' or person.relation_enum[0] == 'mar_sv_2' or person.relation_enum[0] == 'mar_sv_3' or person.relation_enum[0] == 'mar_sv4':
                self.connect_person_and_record(person, record, "SVĚDEK", date)
            elif person.relation_enum[0] == 'mar_widow':
                dead_husband = person
                self.connect_person_and_record(dead_husband, record, "NEVĚSTIN_ZESNULÝ_MANŽEL", date)
                self.connect_two_people(bride, dead_husband, "VDOVA_PO")
            elif person.relation_enum[0] == 'mar_widower':
                dead_wife = person
                self.connect_person_and_record(dead_wife, record, "ŽENICHOVA_ZESNULÁ_ŽENA", date)
                self.connect_two_people(groom, dead_wife, "VDOVEC_PO")

    # Ziskanie otca osoby      
    def get_father_of_person_from_graph_db(self, person):
        for relation in person.relationships_to:
            if relation["type"] == "JE_OTEC":
                return relation["person"]
        return []

    # Ziskanie matky osoby
    def get_mother_of_person_from_graph_db(self, person):
        for relation in person.relationships_to:
            if relation["type"] == "JE_MATKA":
                return relation["person"]
        return []

    # Vytvorenie potencionalnej zhody medzi osobami
    def connect_two_people_potential(self, person1_id, person2_id, score):
        person1 = person2 = None
        for person in self.people:
            if person.id == person1_id:
                person1 = person
            if person.id == person2_id:
                person2 = person
            if person1 and person2:
                break

        person1.potential_matches.append({"person": person2, "score": score})