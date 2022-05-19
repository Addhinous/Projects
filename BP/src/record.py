from enum import Enum
import json

class TypeOfRecord(Enum):
    baptism = 'Záznam_o_křte'
    dead = 'Záznam_o_úmrti'
    marriage = 'Záznam_o_svatbe'

class Record:

    def __init__(self, id_record=None):
        self.id = id_record
        self.type = None
        self.number_scan = None
        self.position = None
        self.page = None
        self.language = None
        self.comment = None
        self.persons = []
        self.register = None
        self.date = None

    def print_record(self):
        print('*************** New record ************************')
        print('  Type of record = ' + str(self.type))
        print('  Number scan = ' + str(self.number_scan))
        print('  Position = ' + str(self.position))
        print('  Language = ' + str(self.language))
        print('  Comment = ' + str(self.comment))
        print('Info about register ----------------------------')
        if self.register is not None:
            self.register.print_register()
        print('Info about persons  ----------------------------')
        for person in self.persons:
            person.person_print()

    def print_czech_whole(self):
        self.register.print_register()
        self.print_czech()
        for person in self.persons:
            person.print_czech()
        print('----------------------------------------')

    def print_czech_csv(self):
        self.register.print_register()
        for person in self.persons:
            person.print_czech_cvs()
        print('----------------------------------------')

    def print_czech(self):
        if self.id:
            print('  ID záznamu = ' + str(self.id))
        if self.type is not None:
            print('  Typ matričního záznamu = ' + str(self.type))
        if self.number_scan is not None:
            print('  Sken = ' + str(self.number_scan))
        if self.page is not None:
            print('  Strana = ' + str(self.page))
        if self.position is not None:
            print('  Pozice = ' + str(self.position))
        if self.language is not None:
            print('  Jazyk záznamu = ' + str(self.language))

    def get_json(self):
        record_set = {
            "id": self.id,
            "sken": self.number_scan,
            "strana": self.page,
            "pozice": self.position,
            "jazyk": self.language
        }
        return record_set
        #return json.dumps(record_set, indent = 4, sort_keys=True, ensure_ascii=False)

    def create_node_record(self):
        self.comment = str(self.comment)
        if '\'' in self.comment:
            self.comment = self.comment.replace('\'', '\\\'')
        return ''.join(["CREATE (:", str(self.type.value), "{id_relačná_databáza:'", str(self.id), "',poradí_záznamu:'", str(self.number_scan), "',pozice:'", str(self.position), "',strana:'", str(self.page), "',jazyk:'", str(self.language), "',komentar:'", str(self.comment),"'})\n"])

    def get_record_from_graph_db(self, record_graph_db):
        self.id = record_graph_db.get('id_relačná_databáza')
        self.number_scan = record_graph_db.get('poradí_záznamu')
        self.position = record_graph_db.get('pozice')
        self.page = record_graph_db.get('strana')
        self.language = record_graph_db.get('jazyk')
        self.comment = record_graph_db.get('komentar')

