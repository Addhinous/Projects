from enum import Enum
from hmac import new
import comparator
from data_representation import DataRepresentation
from person import Person
from datetime import datetime
from domicile import Domicile
import gc
from copy import deepcopy
from record import TypeOfRecord



class NewDatabase:

    def __init__(self, source_database, graph_database, type_of_source, precision_match=0.95, precision_potential=0.7):
        self.graph_database = graph_database
        self.source = type_of_source
        if type_of_source == 'database':
            self.relational_database = source_database
            self.excel_database = None
        else:
            self.relational_database = None
            if type(source_database) == list:
                if len(source_database) > 1:
                    self.excel_database_birth = source_database[0]
                    self.excel_database_burial = source_database[1]
                    self.excel_database_marriage = source_database[2]
                else:
                    self.excel_database = source_database
        self.true_positive = 0
        self.false_positive = 0
        self.true_negative = 0
        self.false_negative = 0
        self.potential_match = 0
        self.potential_no_match = 0
        self.not_tested_positive = 0
        self.not_tested_negative = 0
        self.precision_potential = precision_potential
        self.precision_match = precision_match
        self.precision = 0
        self.recall = 0
        self.f_measure = 0
        # Not loading entire graph database with each record processed but using python objects to store all people being compared
        self.datarep = DataRepresentation()

    # Hlavná metóda zodpovedná za riadenie celého procesu porovnávania. Načíta dáta z MySQL databázy pomocou metód objektu RelationalDatabaseHandle, a potom
    # volá metódu zodpovednú za porovnávanie osôb zo záznamu v cykle, pre všetky záznamy. Nakoniec po skončení procesu porovnávania vloží všetky osoby z objektu
    # DataRepresentation do Neo4j databázy.
    def create_new_graph_database(self):
        print('Spracováva sa relačná databáza demos')
        records_birth = self.relational_database.get_all_birth_records()
        records_burial = self.relational_database.get_all_burial_records()
        records_marriage = self.relational_database.get_all_marriage_records()
        rec_birth = str(len(records_birth))
        rec_burial = str(len(records_burial))
        rec_marriage = str(len(records_marriage))
        i = 1
        print("Matriky úmrtí")
        for unprocessed_record in records_burial:
            print(' '.join(['Spracováva sa záznam číslo:', str(i), 'z', rec_burial]))
            record = self.relational_database.get_record_burial(unprocessed_record)
            self.compare_record_with_graph_database(record)
            i += 1

        i = 1
        print("Matriky narodení: ")
        for unprocessed_record in records_birth:
            print(' '.join(['Spracováva sa záznam číslo:', str(i), 'z', rec_birth]))
            record = self.relational_database.get_record_birth(unprocessed_record)
            self.compare_record_with_graph_database(record)
            i += 1
        
        i = 1
        print("Matriky sobášov")
        for unprocessed_record in records_marriage:
            print(' '.join(['Spracováva sa záznam číslo:', str(i), 'z', rec_marriage]))
            record = self.relational_database.get_record_marriage(unprocessed_record)
            self.compare_record_with_graph_database(record)
            i += 1

        self.insert_all_into_graph_db()
        del self.datarep
        gc.collect()

    # Metóda vykonáva rovnakú funkcionalitu ako metóda create_new_graph_database(), ale vstupné dáta sú načítané z csv súborov, namiesto MySQL databázy.
    def create_new_graph_database_test(self):
        records = self.excel_database_birth.number_of_records()
        rec = str(records)
        records_burial = self.excel_database_burial.number_of_records()
        rec1 = str(records_burial)
        records_marriage = self.excel_database_marriage.number_of_records()
        rec2 = str(records_marriage)
        
        i = 1
        print("Matriky narodení: ")
        for unprocessed_record in range(records):
            print(' '.join(['Spracováva sa záznam číslo:', str(i), 'z', rec]))
            i += 1
            record = self.excel_database_birth.get_record(unprocessed_record)
            self.compare_record_with_graph_database(record)

        i = 1
        print("Matriky úmrtí: ")
        for unprocessed_record in range(records_burial):
            print(' '.join(['Spracováva sa záznam číslo:', str(i), 'z', rec1]))
            i += 1
            record = self.excel_database_burial.get_record_burial(unprocessed_record)
            self.compare_record_with_graph_database(record)
        
        i = 1
        print("Matriky sobášov: ")
        for unprocessed_record in range(records_marriage):
            print(' '.join(['Spracováva sa záznam číslo:', str(i), 'z', rec2]))
            i += 1
            record = self.excel_database_marriage.get_record_marriage(unprocessed_record)
            self.compare_record_with_graph_database(record)
        
        self.insert_all_into_graph_db()
        del self.datarep
        gc.collect()
        self.count_statistic_values()
        self.print_test_result()

    # Metóda vloží všetky dáta z objektu DataRepresentation do grafovej databázy Neo4j.
    def insert_all_into_graph_db(self,):
        print("Inserting registers...")
        #Nahranie registrov do Neo4j
        num_of_registers = str(len(self.datarep.registers))
        num_of_records = str(len(self.datarep.records))
        num_of_towns = str(len(self.datarep.towns))
        num_of_people = str(len(self.datarep.people))
        i = 1
        for register in self.datarep.registers:
            print(str(i) + "/" + num_of_registers)
            i += 1
            self.graph_database.create_register(register)
        
        i = 1
        print("Vkladajú sa záznamy a prepájajú sa s matrikami...")
        #Nahranie zaznamov a prepojenie s registrami do Neo4j
        for record in self.datarep.records:
            print(str(i) + "/" + num_of_records)
            i += 1
            self.graph_database.save_record(record)
            self.graph_database.connect_record_to_register(record, record.register, record.type)

        i = 1
        print("Vkladajú a prepájajú sa mestá, ulice a popisné čísla...")
        #Nahranie miest, ulic a popisnych cisel do Neo4j
        for town in self.datarep.towns:
            print(str(i) + "/" + num_of_towns)
            i += 1
            self.graph_database.insert_town_into_graph_db(town)
            for street in town["streets"]:
                self.graph_database.insert_street_into_graph_db(town, street)
                for number in street["numbers"]:
                    self.graph_database.insert_street_number_into_graph_db(street, number)
            for number in town["numbers"]:
                self.graph_database.insert_number_into_graph_db(town, number)

        i = 1
        print("Vkladajú sa osoby...")
        #Nahranie osob do Neo4j
        for person in self.datarep.people:
            print(str(i) + "/" + num_of_people)
            i += 1
            self.graph_database.create_person(person)

        i = 1
        print("Vkladajú sa prepojenia všetkých osôb...")
        #Vytvorenie prepojeni medzi osobami, adresami a zaznamami
        for person in self.datarep.people:
            print(str(i) + "/" + num_of_people)
            i += 1
            for relation in person.relationships:
                if relation["type"] == "KŘTENEC" \
                    or relation["type"] == "ZESNULÝ" \
                    or relation["type"] == "OTEC" \
                    or relation["type"] == "MATKA" \
                    or relation["type"] == "PORODNI_BABA" \
                    or relation["type"] == "KŘTITEL" \
                    or relation["type"] == "OTCUV_OTEC" \
                    or relation["type"] == "OTCOVA_MATKA" \
                    or relation["type"] == "MATCIN_OTEC" \
                    or relation["type"] == "MATCINA_MATKA" \
                    or relation["type"] == "OTEC_MATCINHO_OTCA" \
                    or relation["type"] == "OTEC_MATCINY_MATKY" \
                    or relation["type"] == "MATKA_MATCINHO_OTCA" \
                    or relation["type"] == "MATKA_MATCINY_MATKY" \
                    or relation["type"] == "KMOTR" \
                    or relation["type"] == "PRIBUZNY_KMOTRA" \
                    or relation['type'] == 'MANŽEL_ZESNULÉHO' \
                    or relation['type'] == 'MANŽELKA_ZESNULÉHO' \
                    or relation['type'] == 'SYN_ZESNULÉHO' \
                    or relation['type'] == 'DCERA_ZESNULÉHO' \
                    or relation['type'] == 'PŘÍBUZNÝ_ZESNULÉHO' \
                    or relation['type'] == 'ZAOPATŘOVATEL' \
                    or relation['type'] == 'HROBNÍK' \
                    or relation['type'] == 'ŽENÍCH' \
                    or relation['type'] == 'ŽENICHOVA_MATKA' \
                    or relation['type'] == 'ŽENICHUV_OTEC' \
                    or relation['type'] == 'MATKA_ŽENICHOVY_MATKY' \
                    or relation['type'] == 'OTEC_ŽENICHOVY_MATKY' \
                    or relation['type'] == 'MATKA_ŽENICHOVA_OTCE' \
                    or relation['type'] == 'OTEC_ŽENICHOVA_OTCE' \
                    or relation['type'] == 'NEVĚSTA' \
                    or relation['type'] == 'NEVĚSTINA_MATKA' \
                    or relation['type'] == 'NEVĚSTIN_OTEC' \
                    or relation['type'] == 'MATKA_NEVĚSTINY_MATKY' \
                    or relation['type'] == 'OTEC_NEVĚSTINY_MATKY' \
                    or relation['type'] == 'MATKA_NEVĚSTINA_OTCE' \
                    or relation['type'] == 'OTEC_NEVĚSTINA_OTCE' \
                    or relation['type'] == 'ODDÁVAJÍCÍ' \
                    or relation['type'] == 'DRUŽIČKA' \
                    or relation['type'] == 'ŽENICHUV_SVĚDEK' \
                    or relation['type'] == 'SVĚDEK' \
                    or relation['type'] == 'NEVĚSTIN_ZESNULÝ_MANŽEL' \
                    or relation['type'] == 'ŽENICHOVA_ZESNULÁ_ŽENA' \
                    or relation["type"] == "MANZEL_MATKY":
                    self.graph_database.connect_person_and_record(person.id, relation["record"], relation["type"], relation["date"])
                else:
                    self.graph_database.connect_two_people(person.id, relation["person"].id, relation["type"])          
            
            for match in person.potential_matches:
                self.graph_database.connect_two_people_potential(person.id, match["person"].id, match["score"])
                
            for domicile in person.domicile:
                self.graph_database.connect_person_to_domicile(person, domicile, domicile.date)

    # Metóda uloží záznam i matriku do objektu DataRepresentation, a potom porovná všetky osoby zo záznamu so všetkými osobami, ktoré už boli spracované (uložené v DataRepresentation objekte).
    # Potom metóda vytvorí prepojenia osôb medzi sebou a medzi osobami a záznamom.
    def compare_record_with_graph_database(self, record):
        self.datarep.save_record(record)
        self.datarep.current = []
        for person in record.persons:
            # na zaklade pohlavia hladame zhodu v osobách
            if len(person.sex) > 0:
                if len(person.sex) == 1:
                    if person.sex[0] == 'Z' or person.sex[0] == 'F':
                        people_graph_db = self.datarep.women + self.datarep.undefined
                    elif person.sex[0] == 'M':
                        people_graph_db = self.datarep.men + self.datarep.undefined
                    else:
                        people_graph_db = self.datarep.people
                elif len(person.sex) == 2:
                    if (person.sex[0] == 'F' and person.sex[1] == 'Z') or (person.sex[0] == 'Z' and person.sex[1] == 'F'):
                        people_graph_db = self.datarep.women + self.datarep.undefined
                    else:
                        people_graph_db = self.datarep.people
            else:
                people_graph_db = self.datarep.people
            self.handle_result_of_comparison(person, record, [person for person in people_graph_db if person not in self.datarep.current])
        # nove prepojenia
        if record.type.name == TypeOfRecord.baptism.name:
            self.datarep.create_connection_with_person_in_birth_record(self.datarep.current, record)
        elif record.type.value == TypeOfRecord.dead.value:
            self.datarep.create_connection_with_person_in_burial_record(self.datarep.current, record)
        elif record.type.value == TypeOfRecord.marriage.value:
            self.datarep.create_connection_with_person_in_marriage_record(self.datarep.current, record)

    # Funkcia zodpovedná za jedno porovnanie, zavolá metódu pre porovnanie a vyhodnotí výsledok (nezhoda, potencionalna zhoda a zhoda).
    def handle_result_of_comparison(self, new_person, record, people_graph_db):
        if self.source == 'database':
            positive_results = self.get_result_of_comparison(new_person, record, people_graph_db)
        else:
            positive_results = self.get_result_of_comparison_test(new_person, record, people_graph_db)
        new_person.compared = True
        # no match
        if len(positive_results) == 0:
            self.datarep.create_person(new_person)

        # match
        elif positive_results[0] == -1:
            positive_results[1].update_node_info(new_person)
            self.check_potential_matches(positive_results[1])
            self.datarep.current.append(positive_results[1])
            self.datarep.current[-1].relation_enum[0] = new_person.relation_enum[0]

        # potential match
        else:
            self.datarep.create_person(new_person)
            self.add_connection_potential_match(self.datarep.people[-1], positive_results)

    # Metóda vykonáva porovnanie dvoch osôb a vráti výsledok
    def get_result_of_comparison(self, new_person, record, people_graph_db):
        matches = []
        for person_graph_db in people_graph_db:
            if self.control_if_compare(new_person, person_graph_db):
                result = self.comparison_of_two_person_with_ancestors(new_person, record, person_graph_db)
                # match
                if result['score'] > self.precision_match:
                    # na prve miesto si dam flag aby som vedela ze som nasla zhodu
                    return [-1, person_graph_db]
                # potential match
                elif result['score'] > self.precision_potential:
                    matches.append({"person": person_graph_db, "score": result['score']})
        return matches

    # Metóda má rovnakú funkcionalitu ako metóda get_result_of_comparison(), ale je použitá pri testovacích dátach a počíta hodnoty
    # použie pri výpočte štatistických údajov (ture positive, false positive, true negative, false negative)
    def get_result_of_comparison_test(self, new_person, record, people_graph_db):
        matches = []
        for person_graph_db in people_graph_db:
            if new_person.compared == False:
                if self.control_if_compare(new_person, person_graph_db):
                    result = self.comparison_of_two_person_with_ancestors(new_person, record, person_graph_db)
                    # match
                    if result['score'] > self.precision_match:
                        # na prve miesto si dam flag aby som vedela ze som nasla zhodu
                        if len(new_person.id_test) > 0 and len(person_graph_db.id_test) > 0:
                            self.check_id_positive(new_person.id_test, person_graph_db.id_test)
                        return [-1, person_graph_db]
                    # potential match
                    elif result['score'] > self.precision_potential:
                        matches.append({"person": person_graph_db, "score": result['score']})
                        self.check_id_potential(new_person.id_test, person_graph_db.id_test)
                    # no match
                    else:
                        if len(new_person.id_test) > 0 and len(person_graph_db.id_test) > 0:
                            self.check_id_negative(new_person.id_test, person_graph_db.id_test)
                else:
                    # not tested
                    self.check_id_not_tested(new_person.id_test, person_graph_db.id_test)
        return matches

    # Metóda prehodnotí vzťahy potencionálnych zhôd osoby podľa porovnávacieho skóre osôb
    def check_potential_matches(self, new_person):
        matches = self.datarep.get_potential_matches_of_person_from_graph_db(new_person.id)
        for potential_match in matches:
            if self.check_if_person_can_live(new_person.all_dates[-1], potential_match):
                if comparator.basic_check_of_two_person(new_person, potential_match):
                    result = self.comparison_of_two_person(new_person, potential_match)
                    # match
                    if result['score'] > self.precision_match:
                        self.datarep.unite_potential_matches_nodes(new_person.id, potential_match.id)
                    # potential match
                    elif result['score'] > self.precision_potential:
                        self.datarep.update_potential_matches_relationship(new_person.id, potential_match.id, result['score'])
                        self.datarep.update_potential_matches_relationship(potential_match.id, new_person.id, result['score'])
                    else:
                        self.datarep.delete_potential_matches_relationship(new_person.id, potential_match.id)
                        self.datarep.delete_potential_matches_relationship(potential_match.id, new_person.id)
        return matches

    def control_if_compare(self, new_person, person_graph_db):
        if self.check_if_person_can_live(new_person.all_dates[-1], person_graph_db):
            if self.relational_database is not None:
                if comparator.basic_check_of_two_person(new_person, person_graph_db):
                    return True
            else:
                if comparator.basic_check_of_two_person_not_normalized(new_person, person_graph_db):
                    return True
        return False

    @staticmethod
    def comparison_of_two_person(person_relation, person_graph):
        comparison_all = []
        comparison = comparator.detailed_comparison_of_two_persons(person_relation, person_graph)
        comparison_all.append(comparison)

        result = comparator.probabilistic_classification_people(comparison_all)
        return result

    def check_id_positive(self, id_list1, id_list2):
        for id1 in id_list1:
            for id2 in id_list2:
                if id1 == id2:
                    self.true_positive += 1
                    return
        self.false_positive += 1

    def check_id_potential(self, id_list1, id_list2):
        for id1 in id_list1:
            for id2 in id_list2:
                if id1 == id2:
                    self.potential_match += 1
                    return
        self.potential_no_match += 1

    def check_id_not_tested(self, id_list1, id_list2):
        for id1 in id_list1:
            for id2 in id_list2:
                if id1 == id2:
                    self.not_tested_positive += 1
                    return
        self.not_tested_negative += 1

    def check_id_negative(self, id_list1, id_list2):
        for id1 in id_list1:
            for id2 in id_list2:
                if id1 == id2:
                    self.false_negative += 1
                    return
        self.true_negative += 1

    # Metoda pre porovnanie dvoch osob aj s ich predkami
    def comparison_of_two_person_with_ancestors(self, person_relation, record, person_graph):
        comparison_all = []
        comparison_all.append(comparator.detailed_comparison_of_two_persons(person_relation, person_graph))

        if person_relation.relation_enum[0] == 'main':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'm')
            comparison_all.append(comparison_mother)

            father = self.get_father(person_graph)
            mother = self.get_mother(person_graph)

            if father != -1:
                comparison_father_father = self.compare_according_to_role_father(record, father, 'f_f')
                comparison_all.append(comparison_father_father)
                comparison_mother_father = self.compare_according_to_role_mother(record, father, 'f_m')
                comparison_all.append(comparison_mother_father)

            if mother != -1:
                comparison_mother_mother = self.compare_according_to_role_mother(record, mother, 'm_m')
                comparison_all.append(comparison_mother_mother)
                comparison_father_mother = self.compare_according_to_role_father(record, mother, 'm_f')
                comparison_all.append(comparison_father_mother)

        elif person_relation.relation_enum[0] == 'm':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'm_f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'm_m')
            comparison_all.append(comparison_mother)

        elif person_relation.relation_enum[0] == 'f':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'f_f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'f_m')
            comparison_all.append(comparison_mother)

        elif person_relation.relation_enum[0] == 'mar_groom':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'mar_g_f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'mar_g_m')
            comparison_all.append(comparison_mother)
            
            father = self.get_father(person_graph)
            mother = self.get_mother(person_graph)

            if father != -1:
                comparison_father_father = self.compare_according_to_role_father(record, father, 'mar_g_f_f')
                comparison_all.append(comparison_father_father)
                comparison_mother_father = self.compare_according_to_role_mother(record, father, 'mar_g_f_m')
                comparison_all.append(comparison_mother_father)

            if mother != -1:
                comparison_mother_mother = self.compare_according_to_role_mother(record, mother, 'mar_g_m_m')
                comparison_all.append(comparison_mother_mother)
                comparison_father_mother = self.compare_according_to_role_father(record, mother, 'mar_g_m_f')
                comparison_all.append(comparison_father_mother)

        elif person_relation.relation_enum[0] == 'mar_bride':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'mar_b_f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'mar_b_m')
            comparison_all.append(comparison_mother)
            
            father = self.get_father(person_graph)
            mother = self.get_mother(person_graph)

            if father != -1:
                comparison_father_father = self.compare_according_to_role_father(record, father, 'mar_b_f_f')
                comparison_all.append(comparison_father_father)
                comparison_mother_father = self.compare_according_to_role_mother(record, father, 'mar_b_f_m')
                comparison_all.append(comparison_mother_father)

            if mother != -1:
                comparison_mother_mother = self.compare_according_to_role_mother(record, mother, 'mar_b_m_m')
                comparison_all.append(comparison_mother_mother)
                comparison_father_mother = self.compare_according_to_role_father(record, mother, 'mar_b_m_f')
                comparison_all.append(comparison_father_mother)

        elif person_relation.relation_enum[0] == 'mar_g_m':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'mar_g_m_f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'mar_g_m_m')
            comparison_all.append(comparison_mother)

        elif person_relation.relation_enum[0] == 'mar_b_m':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'mar_b_m_f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'mar_b_m_m')
            comparison_all.append(comparison_mother)

        elif person_relation.relation_enum[0] == 'mar_g_f':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'mar_g_f_f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'mar_g_f_m')
            comparison_all.append(comparison_mother)

        elif person_relation.relation_enum[0] == 'mar_b_f':
            comparison_father = self.compare_according_to_role_father(record, person_graph, 'mar_b_f_f')
            comparison_all.append(comparison_father)
            comparison_mother = self.compare_according_to_role_mother(record, person_graph, 'mar_b_f_m')
            comparison_all.append(comparison_mother)

        result = comparator.probabilistic_classification_people(comparison_all)
        return result

    def compare_according_to_role_father(self, record, person_graph, role):
        father_relation = []
        for person in record.persons:
            if person.relation_enum[0] == role:
                father_relation = person
                break
        father_graph = self.datarep.get_father_of_person_from_graph_db(person_graph)
        if isinstance(father_graph, Person) and isinstance(father_relation, Person):
            comparison_father = comparator.detailed_comparison_of_two_persons(father_relation, father_graph)
            return comparison_father
        return []

    def get_father(self, person_graph):
        father = self.datarep.get_father_of_person_from_graph_db(person_graph)
        if isinstance(father, Person):
            return father
        return -1

    def get_mother(self, person_graph):
        mother = self.datarep.get_mother_of_person_from_graph_db(person_graph)
        if isinstance(mother, Person):
            return mother
        return -1

    def compare_according_to_role_mother(self, record, person_graph, role):
        mother_relation = []
        for person in record.persons:
            if person.relation_enum[0] == role:
                mother_relation = person
                break
        father_graph = self.datarep.get_mother_of_person_from_graph_db(person_graph)
        if isinstance(father_graph, Person) and isinstance(mother_relation, Person):
            comparison_father = comparator.detailed_comparison_of_two_persons(mother_relation, father_graph)
            return comparison_father
        return []

    def add_connection_potential_match(self, new_person, results):
        for result in results:
            self.datarep.connect_two_people_potential(new_person.id, result['person'].id, result['score'])
            self.datarep.connect_two_people_potential(result['person'].id, new_person.id, result['score'])

    def count_statistic_values(self):
        self.precision = self.true_positive / (self.true_positive + self.false_positive)
        self.recall = self.true_positive / (self.true_positive + self.false_negative)
        self.f_measure = 2 * ((self.precision * self.recall) / (self.precision + self.recall))

    def write_stats_to_file(self, name_file):
        f = open(name_file, "a")
        f.write('Statistics -----------------------------' + '\n')
        f.write('True positive - ' + str(round(self.true_positive, 4)) + '\n')
        f.write('False positive - ' + str(round(self.false_positive, 4)) + '\n')
        f.write('True negative - ' + str(round(self.true_negative, 4)) + '\n')
        f.write('False negative - ' + str(round(self.false_negative, 4)) + '\n')
        f.write('Potential match - ' + str(round(self.potential_match, 4)) + '\n')
        f.write('Potential no match - ' + str(round(self.potential_no_match, 4)) + '\n\n')
        f.write('Precision - ' + str(round(self.precision, 4)) + '\n')
        f.write('Recall - ' + str(round(self.recall, 4)) + '\n')
        f.write('F_measure - ' + str(round(self.f_measure, 4)) + '\n')
        f.close()

    def print_test_result(self):
        print('Výsledné štatisiky spracovaného súboru ------------------')
        print('True positive ' + str(self.true_positive))
        print('False positive ' + str(self.false_positive))
        print('True negative ' + str(self.true_negative))
        print('False negative ' + str(self.false_negative))
        print('Potential match' + str(self.potential_match))
        print('Potential no match' + str(self.potential_no_match))
        print('\nPrecision ' + str(self.precision))
        print('Recall' + str(self.recall))
        print('F-measure' + str(self.f_measure))
        print()

    # Metóda skontroluje či v danom dátume mohla osoba žiť
    @staticmethod
    def check_if_person_can_live(date, person):
        if date == None or person.birth_date_guess["from"] == None:
            return True
        if date < person.birth_date_guess['from']:
            return False
        if person.birth_date_guess["to"] == None:
            return True
        if date > person.dead_date_guess['to']:
            return False
        return True