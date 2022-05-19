import neo4j
from person import Person
from record import Record
from enum import Enum
from domicile import Domicile

class TypeOfRecord(Enum):
    baptism = 'Záznam_o_křte'
    dead = 'Záznam_o_úmrti'
    marriage = 'Záznam_o_svatbe'


class GraphDatabaseHandle:

    def __init__(self, task_to_database='create'):
        self.NEO4J_HOST = ''
        self.NEO4J_PORT = ''
        self.NEO4J_USERNAME = ''
        self.NEO4J_PASSWORD = ''
        self.connection = self.connect()
        self.cqlCreate = ''
        self.cqlConnect = ''
        self.cqlFind = ''
        self.cqlUpdate = ''

        if task_to_database == 'create':
            self.delete_graph_database()

    def connect(self,):
        try:
            file_creed = open('neo_cred', 'r')
            lines = file_creed.readlines()
            for line in lines:
                data = line.replace('\n', '')
                data = data.split("=")
                if data[0] == 'server':
                    self.NEO4J_HOST = data[1]
                if data[0] == 'port':
                    self.NEO4J_PORT = data[1]
                if data[0] == 'username':
                    self.NEO4J_USERNAME = data[1]
                if data[0] == 'password':
                    self.NEO4J_PASSWORD = data[1]
            self.check_creed()
        finally:
            file_creed.close()

        NEO4J_URI = "bolt://{NEO4J_HOST}:{NEO4J_PORT}".format(NEO4J_HOST=self.NEO4J_HOST, NEO4J_PORT=self.NEO4J_PORT)

        try:
            connection = neo4j.GraphDatabase.driver(
                uri=NEO4J_URI,
                auth=(self.NEO4J_USERNAME, self.NEO4J_PASSWORD),
                encrypted=False,
            )
            return connection
        except:
            raise Exception('Error while connecting to Neo4j!')

    def check_creed(self):
        if self.NEO4J_HOST == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')
        if self.NEO4J_PORT == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')
        if self.NEO4J_USERNAME == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')
        if self.NEO4J_PASSWORD == '':
            raise Exception('Nezadane potrebne udaje k prihlaseniu!')

    def close(self):
        self.connection.close()

    def delete_graph_database(self):
        self.cqlCreate = "MATCH (n) WITH n LIMIT 1 RETURN n"
        tmp = self.run_cql_with_return_create()
        while tmp:
            print("Deleting node batch...")
            self.cqlCreate = "MATCH (n) WITH n LIMIT 1000 DETACH DELETE n"
            self.run_delete_cql()
            self.cqlCreate = "MATCH (n) WITH n LIMIT 1 RETURN n"
            tmp = self.run_cql_with_return_create()

    def save_record(self, record):
        self.create_record(record)
        if record.register.id is not None:
            self.connect_record_to_register(record.id, record.register.id, record.type)

    def unite_potential_matches_nodes(self, person1_id, person2_id):
        self.delete_potential_matches_relationship(person1_id, person2_id)
        self.delete_potential_matches_relationship(person2_id, person1_id)
        person1 = self.get_person_based_on_id_from_graph_db(person1_id)
        person2 = self.get_person_based_on_id_from_graph_db(person2_id)
        relationships_to = self.get_all_relationship_to_node(person2_id)
        relationships_from = self.get_all_relationship_from_node(person2_id)
        self.delete_person_node(person2_id)
        self.create_relationships_to_node(person1_id, relationships_to)
        self.create_relationships_from_node(person1_id, relationships_from)
        self.update_info_about_person(person2, person1)

    def get_person_detail(self, person):
        new_person = Person()
        new_person.get_person_from_graph_db(person)
        self.get_addresses_of_person(new_person, person)
        return new_person

    @staticmethod
    def get_person_basic(person):
        new_person = Person()
        new_person.get_person_from_graph_db(person)
        return new_person

    def get_addresses_of_person(self, person_new, person_graph_db):
        addresses = self.get_addresses_of_person_from_graph_db(person_graph_db)
        for address in addresses:
            domicile = Domicile()
            self.get_address(address['address'], domicile)
            person_new.domicile.append(domicile)

    def get_address(self, address_node, domicile_new):
        for key in address_node:
            if key == 'popisne_cislo':
                domicile_new.street_number = address_node.get('popisne_cislo')
                self.get_street(address_node['id'], domicile_new)
            elif key == 'Ulica':
                domicile_new.street = address_node.get('ulica')
                self.get_town(address_node['id'], domicile_new)
            elif key == 'nazov_mesta':
                domicile_new.save_town_from_graph_db(address_node)

    def get_street(self, id_address, domicile_new):
        street_node = self.get_street_from_graph_db(id_address)
        if len(street_node) == 0:
            self.get_town(id_address, domicile_new)
        else:
            street_node = street_node[0]['street']
            domicile_new.street = street_node.get('ulica')
            self.get_town(street_node.id, domicile_new)

    def get_town(self, id_street, domicile_new):
        town_node = self.get_town_from_graph_db(id_street)
        town_node = town_node[0]['town']
        if len(town_node) != 0:
            domicile_new.save_town_from_graph_db(town_node)

    def create_person(self, person):
        self.cqlCreate = person.create_node_person()
        self.run_create_cql()

    def create_record(self, record: Record):
        self.cqlCreate = record.create_node_record()
        self.run_create_cql()

    def create_register(self, register):
        self.cqlCreate = register.create_node_register()
        self.run_create_cql()

    def insert_town_into_graph_db(self, town):
        gps_coordinates_list = [town["gps"]['latitude'], town["gps"]['longitude']]
        self.cqlCreate = "".join(["CREATE (:Mesto {nazov_mesta:'",str(town["name"]),"',","id_mesto:'",str(town["id"]),"',","gps_suradnice:",self.add_list_to_graph_db(gps_coordinates_list),",","nazov_mesta_normalizovany:'",str(town["normalized_name"]),"'})\n"])
        self.run_create_cql()

    @staticmethod
    def add_list_to_graph_db(list_variables):
        string = "["
        for i in list_variables:
            string = "".join([string, "'", str(i), "', "])
        if len(list_variables) > 0:
            string = string[:-2]
        string += "]"
        return string

    def insert_street_into_graph_db(self, town, street):
        self.cqlCreate = "".join(["CREATE (:Ulica {ulica:'",street["street_name"][0],"', id:'",str(street["street_name"][1]),"'})\n"])
        self.run_create_cql()
        self.cqlConnect = "".join(["MATCH (a:Ulica), (b:Mesto)\nWHERE a.id = '",str(street["street_name"][1]),"' AND b.id_mesto = '",str(town["id"]),"'\nCREATE (a)-[:JE_V]->(b)\n"])
        self.run_connect_cql()

    def insert_street_number_into_graph_db(self, street, number):
        self.cqlCreate = "".join([self.cqlCreate, "CREATE (:Popisné_číslo {popisne_cislo:'",str(number[0]),"', id:'",str(number[1]),"'})\n"])
        self.run_create_cql()
        self.cqlConnect = "".join(["MATCH (a:Popisné_číslo), (b:Ulica)\nWHERE a.id = '",str(number[1]),"' AND b.id = '",str(street["street_name"][1]),"'\nCREATE (a)-[:JE_V]->(b)\n"])
        self.run_connect_cql()
    
    def insert_number_into_graph_db(self, town, number):
        self.cqlCreate = "".join([self.cqlCreate, "CREATE (:Popisné_číslo {popisne_cislo:'",str(number[0]),"', id:'",str(number[1]),"'})\n"])
        self.run_create_cql()
        if town["normalized_name"]:
            self.cqlConnect = "".join(["MATCH (a:Popisné_číslo), (b:Mesto)\nWHERE a.id = '",str(number[1]),"' AND b.nazov_mesta_normalizovany = '",str(town["normalized_name"]),"'\nCREATE (a)-[:JE_V]->(b)\n"])
        else:
            self.cqlConnect = "".join(["MATCH (a:Popisné_číslo), (b:Mesto)\nWHERE a.id = '",str(number[1]),"' AND b.nazov_mesta = '",str(town["name"]),"'\nCREATE (a)-[:JE_V]->(b)\n"])
        self.run_connect_cql()

    def create_domicile(self, domicile, person):
        if domicile is not None:
            if self.check_if_street_number_exist_in_graph(domicile):
                self.cqlCreate = "".join([self.cqlCreate, "CREATE (:Popisné_číslo {popisne_cislo:'",str(domicile.street_number),"'})\n"])

            if self.check_if_street_exist_in_graph(domicile):
                self.cqlCreate = "".join([self.cqlCreate, "CREATE (:Ulica {ulica:'",str(domicile.street),"'})\n"])

            if domicile.town is not None and domicile.town != '' and domicile.town != ' ':
                if domicile.normalized_town is not None and domicile.normalized_town != '' and domicile.normalized_town != ' ':
                    if self.check_if_town_exist_in_graph(domicile.normalized_town, 'normalized'):
                        self.cqlCreate += domicile.create_town_node()
                elif self.check_if_town_exist_in_graph(domicile.town, 'original'):
                    self.cqlCreate += domicile.create_town_node()
            elif domicile.normalized_town is not None and domicile.normalized_town != '' and domicile.normalized_town != ' ':
                if self.check_if_town_exist_in_graph(domicile.normalized_town, 'normalized'):
                    self.cqlCreate += domicile.create_town_node()

            if len(self.cqlCreate) > 0:
                self.run_create_cql()
                self.connect_domicile(domicile)
            self.connect_person_to_domicile(person, domicile)

    def create_relationships_from_node(self, person_id, relationships):
        for relationship in relationships:
            relation = relationship['relation']
            self.cqlConnect = "".join([self.cqlConnect, "MATCH (a:Osoba),(b)\nWHERE '",str(person_id),"' IN a.id_relačná_databáza AND ID(b) = ",str(relation.end),"\nMERGE (a)-[:",str(relation.type),"]->(b)\n"])
            self.run_connect_cql()

    def create_relationships_to_node(self, person_id, relationships):
        for relationship in relationships:
            relation = relationship['relation']
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a),(b:Osoba)\nWHERE '",str(person_id),"' IN b.id_relačná_databáza AND ID(a) = ",str(relation.start),"\nMERGE (a)-[:",str(relation.type),"]->(b)\n"])
            self.run_connect_cql()

    def get_all_relationship_from_node(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation]->(osoba2)\nWHERE '",str(person_id),"' IN osoba.id_relačná_databáza\nRETURN relation \n"])
        return self.run_cql_with_return_person()

    def get_all_relationship_to_node(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation]->(osoba2)\nWHERE '",str(person_id),"' IN osoba2.id_relačná_databáza\nRETURN relation \n"])
        return self.run_cql_with_return_person()

    def delete_person_node(self, person_id):
        self.cqlUpdate = "".join(["MATCH (osoba:Osoba)\nWHERE '",str(person_id),"' IN osoba.id_relačná_databáza \nDETACH DELETE osoba \n"])
        self.run_update_cql()

    def delete_potential_matches_relationship(self, person1_id, person2_id):
        self.cqlUpdate = "".join(["MATCH (osoba:Osoba)-[relation:POTENCIONALNÍ_ZHODA]->(osoba2:Osoba)\nWHERE '",str(person1_id),"' IN osoba.id_relačná_databáza AND '",str(person2_id),"' IN osoba2.id_relačná_databáza \nDELETE relation \n"])
        self.run_update_cql()

    def get_person_based_on_name_and_surname_from_graph_db(self, name, surname):
        self.cqlFind = "".join(["MATCH (person:Osoba)\nWHERE ('",name,"' IN person.jméno OR '",name,"' IN person.normalizované_jméno) AND ('",surname,"' IN person.příjmení OR '",surname,"' IN person.normalizované_příjmení)\nRETURN person \n"])
        people = self.run_cql_with_return_person()
        return people

    def get_town_from_graph_db(self, street_id):
        self.cqlFind = "".join(["MATCH (a)-[relation]->(town:Mesto)\nWHERE a.id = '",str(street_id),"' AND type(relation)=~ 'JE_V'\nRETURN town  \n"])
        return self.run_cql_with_return_person()

    def get_street_from_graph_db(self, street_number_id):
        self.cqlFind = "".join(["MATCH (a:Popisné_číslo)-[relation]->(street:Ulica)\nWHERE a.id = '",str(street_number_id),"' AND type(relation)=~ 'JE_V'\nRETURN street  \n"])
        return self.run_cql_with_return_person()

    def get_addresses_of_person_from_graph_db(self, person):
        self.cqlFind = "".join(["MATCH (res:Osoba)-[relation:BÝVÁ]->(address)\nWHERE ID(res) = ",str(person['id'])," \nRETURN address  \n"])
        return self.run_cql_with_return_person()

    def connect_person_and_record(self, person_id, record,  relationship, date):
        self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Osoba),(b:",record.type.value,")\nWHERE '",str(person_id),"' IN a.id_relačná_databáza AND b.id_relačná_databáza = '",str(record.id),"'\nCREATE (a)-[:",str(relationship),"{date:'",str(date),"'}]->(b)\n"])
        self.run_connect_cql()

    def connect_two_people(self, person1_id, person2_id, relationship):
        self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Osoba),(b:Osoba)\nWHERE '",str(person1_id),"' IN a.id_relačná_databáza AND '",str(person2_id),"' IN b.id_relačná_databáza \nCREATE (a)-[:",relationship,"]->(b)\n"])
        self.run_connect_cql()

    def connect_two_people_potential(self, person1_id, person2_id, percentage):
        self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Osoba),(b:Osoba)\nWHERE '",str(person1_id),"' IN a.id_relačná_databáza AND '",str(person2_id),"' IN b.id_relačná_databáza \nCREATE (a)-[:POTENCIONALNÍ_ZHODA {pravděpodobnost_shody:'",str(percentage),"'}]->(b)\n"])
        self.run_connect_cql()

    # OUTDATED
    def connect_domicile(self, domicile):
        # prepojenie adresy (popisneho cisla) na vyssiu uroven
        if (domicile.street_number is not None and domicile.street_number != '' and domicile.street_number != ' ') and (domicile.street is not None and domicile.street != '' and domicile.street != ' '):
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Popisné_číslo),(b:Ulica)\nWHERE a.popisne_cislo = '",str(domicile.street_number),"' AND b.ulica = '",str(domicile.street),"'\nCREATE (a)-[:JE_V]->(b)\n"])

        elif (domicile.street_number is not None and domicile.street_number != '' and domicile.street_number != ' ') and (domicile.normalized_town is not None and domicile.normalized_town != '' and domicile.normalized_town != ' '):
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Popisné_číslo),(b:Mesto)\nWHERE a.popisne_cislo = '",str(domicile.street_number),"' AND b.nazov_mesta_normalizovany = '",str(domicile.normalized_town),"'\n"])

        elif (domicile.street_number is not None and domicile.street_number != '' and domicile.street_number != ' ') and (domicile.town is not None and domicile.town != '' and domicile.town != ' '):
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Popisné_číslo),(b:Mesto)\nWHERE a.popisne_cislo = '",str(domicile.street_number),"' AND b.nazov_mesta= '",str(domicile.town),"'\n"])

        if len(self.cqlConnect) > 0:
            self.cqlConnect += "CREATE (a)-[:JE_V]->(b)\n"
            self.run_connect_cql()

        if (domicile.street is not None and domicile.street != '' and domicile.street != ' ') and (domicile.normalized_town is not None and domicile.normalized_town != '' and domicile.normalized_town != ' '):
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Ulica),(b:Mesto)\nWHERE a.ulica = '",str(domicile.street),"' AND b.nazov_mesta_normalizovany = '",str(domicile.normalized_town),"'\n"])

        elif (domicile.street is not None and domicile.street != '' and domicile.street != ' ') and (domicile.town is not None and domicile.town != '' and domicile.town != ' '):
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Ulica),(b:Mesto)\nWHERE a.ulica = '",str(domicile.street),"' AND b.nazov_mesta= '",str(domicile.town),"'\n"])

        if len(self.cqlConnect) > 0:
            self.cqlConnect += "CREATE (a)-[:JE_V]->(b)\n"
            self.run_connect_cql()

    def connect_person_to_domicile(self, person, domicile, date):
        if domicile.street_number is not None and domicile.street_number != '' and domicile.street_number != ' ':
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Osoba),(b:Popisné_číslo)\nWHERE '",str(person.id),"' IN a.id_relačná_databáza AND b.id = '",str(domicile.street_number[1]),"'\nCREATE (a)-[:BÝVÁ {date:'",str(date),"'}]->(b)\n"])
            self.run_connect_cql()
        elif domicile.street is not None and domicile.street != '' and domicile.street != ' ':
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Osoba),(b:Ulica)\nWHERE '",str(person.id),"' IN a.id_relačná_databáza AND b.id = '",str(domicile.street[1]),"'\nCREATE (a)-[:BÝVÁ {date:'",str(date),"'}]->(b)\n"])
            self.run_connect_cql()
        elif domicile.town is not None and domicile.town != '' and domicile.town != ' ':
            if domicile.normalized_town is not None and domicile.normalized_town != '' and domicile.normalized_town != ' ':
                self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Osoba),(b:Mesto)\nWHERE '",str(person.id),"' IN a.id_relačná_databáza AND b.nazov_mesta_normalizovany = '",str(domicile.normalized_town),"'\nCREATE (a)-[:BÝVÁ {date:'",str(date),"'}]->(b)\n"])
                self.run_connect_cql()
            else:
                self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Osoba),(b:Mesto)\nWHERE '",str(person.id),"' IN a.id_relačná_databáza AND b.nazov_mesta = '",str(domicile.town),"'\nCREATE (a)-[:BÝVÁ {date:'",str(date),"'}]->(b)\n"])
                self.run_connect_cql()
        elif domicile.normalized_town is not None and domicile.normalized_town != '' and domicile.normalized_town != ' ':
            self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:Osoba),(b:Mesto)\nWHERE '",str(person.id),"' IN a.id_relačná_databáza AND b.nazov_mesta_normalizovany = '",str(domicile.normalized_town),"'\nCREATE (a)-[:BÝVÁ {date:'",str(date),"'}]->(b)\n"])
            self.run_connect_cql()

    def connect_record_to_register(self, record_id, register_id, type_of_record):
        self.cqlConnect = "".join([self.cqlConnect,"MATCH (a:",type_of_record.value,"),(b:Matrika)\nWHERE a.id_relačná_databáza = '",str(record_id),"' AND b.ID_matrika = '",str(register_id),"'\nCREATE (a)-[:JE_V]->(b)\n"])
        self.run_connect_cql()

    def get_all_person(self):
        self.cqlFind += "MATCH (person:Osoba)\nRETURN person  \n"
        return self.run_cql_with_return_person()

    def get_all_person_undefined(self):
        self.cqlFind += "MATCH (person:Osoba)\nWHERE 'U' IN person.pohlaví \nRETURN person \n"
        return self.run_cql_with_return_person()

    def get_node_by_id(self, id):
        self.cqlFind = "".join([self.cqlFind, "MATCH (node:Osoba)\nWHERE id(node) = ",str(id),"\nRETURN node \n"])
        return self.run_cql_with_return_person()

    def get_all_women(self):
        self.cqlFind += "MATCH (person:Osoba)\nWHERE 'F' IN person.pohlaví OR 'Z' IN person.pohlaví \nRETURN person, id(person) \n"
        return self.run_cql_with_return_person()

    def get_all_men(self):
        self.cqlFind += "MATCH (person:Osoba)\nWHERE 'M' IN person.pohlaví \nRETURN person \n"
        return self.run_cql_with_return_person()

    def get_person_based_on_id_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (person:Osoba)\nWHERE ",str(person_id)," IN person.id \nRETURN person \n"])
        person = self.run_cql_with_return_person()
        if len(person) == 0:
            return None
        else:
            return self.get_person_detail(person[0]['person'])

    def get_all_birth_records_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation]->(record:Záznam_o_křte)\nWHERE ",str(person_id)," IN osoba.id\nRETURN record, relation, relation.date  \n"])
        records = self.run_cql_with_return()
        return records

    def get_all_marriage_records_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation]->(record:Záznam_o_svatbe)\nWHERE ",str(person_id)," IN osoba.id\nRETURN record, relation, relation.date  \n"])
        records = self.run_cql_with_return()
        return records

    def get_all_dead_records_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation]->(record:Záznam_o_úmrti)\nWHERE ",str(person_id)," IN osoba.id\nRETURN record, relation, relation.date  \n"])
        records = self.run_cql_with_return()
        return records

    def get_children_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba1:Osoba)-[relation]->(osoba:Osoba)\nWHERE ",str(person_id)," IN osoba1.id AND (type(relation)=~ 'JE_MATKA' OR type(relation)=~ 'JE_OTEC' )\nRETURN osoba, relation  \n"])
        people = self.run_cql_with_return_person()
        children = []
        if len(people) > 0:
            children.append(self.get_person_detail(people[0]['osoba']))
        return children

    def get_partner_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba1:Osoba)-[relation:JSOU_MANŽELÉ]->(osoba:Osoba)\nWHERE ",str(person_id)," IN osoba.id\nRETURN osoba, relation  \n"])
        people = self.run_cql_with_return_person()
        return people

    def get_parents_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation]->(osoba2:Osoba)\nWHERE ",str(person_id)," IN osoba2.id AND (type(relation)=~ 'JE_MATKA' OR type(relation)=~ 'JE_OTEC' )\nRETURN osoba, relation  \n"])
        people = self.run_cql_with_return_person()
        return people

    def get_father_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation:JE_OTEC]->(osoba2:Osoba)\nWHERE ",str(person_id)," IN osoba2.id\nRETURN osoba  \n"])
        people = self.run_cql_with_return_person()
        if len(people) > 0:
            father = self.get_person_detail(people[0]['osoba'])
        else:
            father = []
        return father

    def get_mother_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation:JE_MATKA]->(osoba2:Osoba)\nWHERE ",str(person_id)," IN osoba2.id\nRETURN osoba  \n"])
        people = self.run_cql_with_return_person()
        if len(people) > 0:
            mother = self.get_person_detail(people[0]['osoba'])
        else:
            mother = []
        return mother

    def get_potential_matches_of_person_from_graph_db(self, person_id):
        self.cqlFind = "".join(["MATCH (osoba:Osoba)-[relation:POTENCIONALNI_ZHODA]->(osoba2:Osoba)\nWHERE '",str(person_id),"' IN osoba2.id_relačná_databáza\nRETURN osoba  \n"])
        people = self.run_cql_with_return_person()
        matches = []
        if len(people) > 0:
            for person in people:
                matches.append(self.get_person_detail(person['osoba']))
        return matches

    def update_potential_matches_relationship(self, person1_id, person2_id, result):
        self.cqlUpdate = "".join(["MATCH (osoba:Osoba)-[relation:POTENCIONALNÍ_ZHODA]->(osoba2:Osoba)\nWHERE '",str(person1_id),"' IN osoba.id_relačná_databáza AND '",str(person2_id),"' IN osoba2.id_relačná_databáza \nSET relation.pravděpodobnost_shody = '",str(result),"' \nRETURN relation \n"])
        self.run_update_cql()

    def check_if_town_exist_in_graph(self, town, type_of_town):
        self.cqlFind += "MATCH (a:Mesto)\n"

        if type_of_town == 'original':
            self.cqlFind = "".join([self.cqlFind, "WHERE a.nazov_mesta = '",str(town),"' \n"])
        elif type_of_town == 'normalized':
            self.cqlFind = "".join([self.cqlFind, "WHERE a.nazov_mesta_normalizovany = '",str(town),"' \n"])
        else:
            raise Exception('Unknown kind of town! (different that original or normalized)')

        self.cqlFind += "RETURN a \n"
        result = self.run_cql_with_return()
        if len(result) == 0:
            return True
        else:
            return False

    def check_if_register_exist_in_graph(self, register):
        self.cqlFind = "".join([self.cqlFind, "MATCH (a:Matrika)\nWHERE a.ID_matrika = '",str(register.id),"' \nRETURN a \n"])
        result = self.run_cql_with_return()
        if len(result) == 0:
            return True
        else:
            return False

    def check_if_record_exist_in_graph(self, record):
        self.cqlFind = "".join([self.cqlFind,"MATCH (a:Záznam_o_křte)\nWHERE a.id_relačná_databáza = '",str(record.id),"' \nRETURN a \n"])
        result = self.run_cql_with_return()
        if len(result) == 0:
            return True
        else:
            return False

    def check_if_street_exist_in_graph(self, domicile):
        match = ""
        where = ""
        if domicile.street:
            if domicile.normalized_town:
                match = ",(b:Mesto )"
                where = "".join([" AND b.nazov_mesta_normalizovany = '",str(domicile.normalized_town),"'"])
            elif domicile.town:
                match = ",(b:Mesto )\n"
                where = "".join([" AND b.nazov_mesta = '",str(domicile.town),"'"])

            self.cqlFind = "".join([self.cqlFind, "MATCH (a:Ulica)",match,"\nWHERE a.ulica = '",str(domicile.street),"'",where," \nRETURN a \n"])
            result = self.run_cql_with_return()
            if len(result) == 0:
                return True
            else:
                return False
        else:
            return False

    def check_if_street_number_exist_in_graph(self, domicile):
        match = ""
        where = ""
        if domicile.street_number:
            if domicile.street:
                match = ",(b:Ulica )"
                where = "".join([" AND b.ulica = '", str(domicile.street), "'"])
            if domicile.normalized_town:
                match += ",(c:Mesto )"
                where = "".join([where, " AND c.nazov_mesta_normalizovany = '", str(domicile.normalized_town), "'"])
            elif domicile.town:
                match += ",(c:Mesto )\n"
                where = "".join([where, " AND c.nazov_mesta = '", str(domicile.town), "'"])
            self.cqlFind = "".join([self.cqlFind,"MATCH (a:Popisné_číslo)",match,"\nWHERE a.popisne_cislo = '",str(domicile.street_number),"'",where," \nRETURN a \n"])
            result = self.run_cql_with_return()
            if len(result) == 0:
                return True
            else:
                return False
        else:
            return False

    def update_info_about_person(self, person_new, person_old):
        self.cqlUpdate = "".join(["MATCH (osoba:Osoba)\nWHERE '", str(person_old.id), "' IN osoba.id_relačná_databáza \n", person_old.update_node_info(person_new), "RETURN osoba \n"])
        self.run_update_cql()

    def create_connection_with_person_in_birth_record(self, persons, record):
        main = father = mother = mother_father = mother_mother = ''
        goth_father_1 = goth_father_2 = goth_father_3 = goth_father_4 = ''
        date = self.get_date_from_main_person(persons)

        for person in persons:
            if person.relation_enum[0] == 'main':
                main = person.id
                self.connect_person_and_record(main, record, "KŘTENEC", date)
            if person.relation_enum[0] == 'f':
                father = person.id
                self.connect_two_people(father, main, "JE_OTEC")
                self.connect_person_and_record(father, record, "KŘTENEC", date)
            if person.relation_enum[0] == 'm':
                mother = person.id
                self.connect_two_people(mother, main, "JE_MATKA")
                self.connect_person_and_record(mother, record, "MATKA", date)
            if person.relation_enum[0] == 'midwife':
                midwife = person.id
                self.connect_two_people(midwife, main, "ODRODILA")
                self.connect_person_and_record(midwife, record, "PORODNI_BABA", date)
            if person.relation_enum[0] == 'granted':  # kaplan
                granted = person.id
                self.connect_two_people(granted, main, "KŘTIL")
                self.connect_person_and_record(granted, record, "KŘTITEL", date)
            if person.relation_enum[0] == 'f_f':
                father_father = person.id
                self.connect_two_people(father_father, father, "JE_OTEC")
                self.connect_person_and_record(father_father, record, "OTCUV_OTEC", date)
            if person.relation_enum[0] == 'f_m':
                father_mother = person.id
                self.connect_two_people(father_mother, father, "JE_MATKA")
                self.connect_person_and_record(father_mother, record, "OTCOVA_MATKA", date)
            if person.relation_enum[0] == 'm_f':
                mother_father = person.id
                self.connect_two_people(mother_father, mother, "JE_OTEC")
                self.connect_person_and_record(mother_father, record, "MATCIN_OTEC", date)
            if person.relation_enum[0] == 'm_m':
                mother_mother = person.id
                self.connect_two_people(mother_mother, mother, "JE_MATKA")
                self.connect_person_and_record(mother_mother, record, "MATCINA_MATKA", date)
            if person.relation_enum[0] == 'f_m_f':
                father_mother_father = person.id
                self.connect_two_people(father_mother_father, mother_father, "JE_OTEC")
                self.connect_person_and_record(father_mother_father, record, "OTEC_MATCINHO_OTCA", date)
            if person.relation_enum[0] == 'f_m_m':
                father_mother_mother = person.id
                self.connect_two_people(father_mother_mother, mother_mother, "JE_OTEC")
                self.connect_person_and_record(father_mother_mother, record, "OTEC_MATCINY_MATKY", date)
            if person.relation_enum[0] == 'm_m_f':
                mother_mother_father = person.id
                self.connect_two_people(mother_mother_father, mother_father, "JE_MATKA")
                self.connect_person_and_record(mother_mother_father, record, "MATKA_MATCINHO_OTCA", date)
            if person.relation_enum[0] == 'm_m_m':
                mother_mother_mother = person.id
                self.connect_two_people(mother_mother_mother, mother_mother, "JE_MATKA")
                self.connect_person_and_record(mother_mother_mother, record, "MATKA_MATKCINY_MATKY", date)
            if person.relation_enum[0] == 'gf_1':
                goth_father_1 = person.id
                self.connect_two_people(goth_father_1, main, "KMOTR")
                self.connect_person_and_record(goth_father_1, record, "KMOTR", date)
            if person.relation_enum[0] == 'gf_2':
                goth_father_2 = person.id
                self.connect_two_people(goth_father_2, main, "KMOTR")
                self.connect_person_and_record(goth_father_2, record, "KMOTR", date)
            if person.relation_enum[0] == 'gf_3':
                goth_father_3 = person.id
                self.connect_two_people(goth_father_3, main, "KMOTR")
                self.connect_person_and_record(goth_father_3, record, "KMOTR", date)
            if person.relation_enum[0] == 'gf_4':
                goth_father_4 = person.id
                self.connect_two_people(goth_father_4, main, "KMOTR")
                self.connect_person_and_record(person.id, record, "KMOTR", date)
            if person.relation_enum[0] == 'gfrel_1':
                goth_father_relative_1 = person.id
                self.connect_two_people(goth_father_relative_1, goth_father_1, "JE_PRÍBUZNÝ")
                self.connect_person_and_record(goth_father_relative_1, record, "PRIBUZNY_KMOTRA", date)
            if person.relation_enum[0] == 'gfrel_2':
                goth_father_relative_2 = person.id
                self.connect_two_people(goth_father_relative_2, goth_father_2, "JE_PRÍBUZNÝ")
                self.connect_person_and_record(goth_father_relative_2, record, "PRIBUZNY_KMOTRA", date)
            if person.relation_enum[0] == 'gfrel_3':
                goth_father_relative_3 = person.id
                self.connect_two_people(goth_father_relative_3, goth_father_3, "JE_PRÍBUZNÝ")
                self.connect_person_and_record(goth_father_relative_3, record, "PRIBUZNY_KMOTRA", date)
            if person.relation_enum[0] == 'gfrel_4':
                goth_father_relative_4 = person.id
                self.connect_two_people(goth_father_relative_4, goth_father_4, "JE_PRÍBUZNÝ")
                self.connect_person_and_record(goth_father_relative_4, record, "PRIBUZNY_KMOTRA", date)
            if person.relation_enum[0] == 'husband':
                husband = person.id
                self.connect_two_people(husband, mother, "JSOU_MANŽELÉ")
                self.connect_person_and_record(husband, record, "MANZEL_MATKY", date)

    @staticmethod
    def get_date_from_main_person(persons):
        for person in persons:
            if person.relation_enum[0] == 'main':
                if len(person.birth_date) > 0:
                    if person.birth_date[0].date is not None:
                        return person.birth_date[-1].date
                    else:
                        return person.baptism_date[-1].date

    def run_delete_cql(self):
        if len(self.cqlCreate) > 0:
            with self.connection.session() as graph_database_session:
                graph_database_session.run(self.cqlCreate)
            self.cqlCreate = ''

    def run_create_cql(self):
        if len(self.cqlCreate) > 0:
            with self.connection.session() as graph_database_session:
                graph_database_session.run(self.cqlCreate[:-1])
            self.cqlCreate = ''

    def run_connect_cql(self):
        if len(self.cqlConnect) > 0:
            with self.connection.session() as graph_database_session:
                graph_database_session.run(self.cqlConnect[:-1])
            self.cqlConnect = ''

    def run_update_cql(self):
        if len(self.cqlUpdate) > 0:
            with self.connection.session() as graph_database_session:
                graph_database_session.run(self.cqlUpdate).data()
            self.cqlUpdate = ''

    def run_cql_with_return(self):
        if len(self.cqlFind) > 0:
            with self.connection.session() as graph_database_session:
                result = graph_database_session.run(self.cqlFind).data()
            self.cqlFind = ''
            return result

    def run_cql_with_return_create(self):
        if len(self.cqlCreate) > 0:
            with self.connection.session() as graph_database_session:
                result = graph_database_session.run(self.cqlCreate).data()
            self.cqlCreate = ''
            return result

    def run_cql_with_return_person(self):
        if len(self.cqlFind) > 0:
            with self.connection.session() as graph_database_session:
                result = graph_database_session.run(self.cqlFind).data()
            self.cqlFind = ''
            return result
