from pprint import pprint
#Trieda reprezentujuca matriku
class Register:

    def __init__(self, id_register=None):
        self.id = id_register
        self.archive = None
        self.fond = None
        self.signature = None
        self.languages = []
        self.scan_count = None
        self.ranges = []
        self.municipality = []
        #######################

    def print_register(self):
        print('      Archive = ' + str(self.archive))
        print('      Fond = ' + str(self.fond))
        print('      Signature = ' + str(self.signature))
        print('      Language = ' + str(self.languages))
        print('      Number scan = ' + str(self.scan_count))
        print('      Ranges:')
        for date in self.ranges:
            print('         Date from = ' + str(date['date_from']))
            print('         Date to = ' + str(date['date_to']))
        print('      Municipality = ', end='')
        for mun in self.municipality:
            print(' ' + str(mun), end='')
        print('')

    def create_node_register(self):
        cqlCreate = "CREATE (:Matrika {Signatura:'" + str(self.signature) + "',"
        cqlCreate += "ID_matrika:'" + str(self.id) + "',"
        cqlCreate += "Fond:'" + str(self.fond) + "',"
        cqlCreate += "Archiv:'" + str(self.archive) + "',"
        cqlCreate += "Jazyky:" + self.add_list_to_graph_db(self.languages) + ","
        cqlCreate += "Obec:["
        for mun in self.municipality:
            cqlCreate += "'" + str(mun) + "', "
        if len(self.municipality) > 0:
            cqlCreate = cqlCreate[:-2]
        cqlCreate += "],"
        i = 1
        for date in self.ranges:
            cqlCreate += "Casove_obdobi_" + str(i) + ":['" + str(date['date_from']) + "', '" + str(date['date_to']) + "'], "
            i += 1
        if self.ranges:
            cqlCreate = cqlCreate[:-2]
        else:
            cqlCreate = cqlCreate[:-1]
        cqlCreate += "})\n"
        return cqlCreate

    @staticmethod
    def add_list_to_graph_db(list_variables):
        string = "["
        for i in list_variables:
            string += "'" + str(i) + "', "
        if len(list_variables) > 0:
            string = string[:-2]
        string += "]"
        return string
