from graph_database import GraphDatabaseHandle
from relational_database_birth import RelationalDatabaseHandle
from create_database import NewDatabase
from csv_source import ExcelDatabaseHandle
from time import time
from sys import argv
from json import load

# Vetva main pre spustenie nad sql databazou
def main():
    start_time = time()
    graph_database = GraphDatabaseHandle('create')
    json_files = get_json_files()
    relational_database = RelationalDatabaseHandle(json_files)
    new_database = NewDatabase(relational_database, graph_database, 'database')
    new_database.create_new_graph_database()
    relational_database.close()
    graph_database.close()
    print("Time of comparing " + str(time() - start_time) + "\n")

# Vetva main pre spustenie nad testovacou sadou
def main_testing_precision():
    precision = 0.9    #0.85
    precision_potential = 0.7  #0.7 before and 0.65 before that
    json_files = get_json_files()

    file_names = ['datasety/N_Bukovinka_vsechny signatury dohromady - aktualni sablona podle webu 5.2.2020.csv', 'datasety/Z_Bukovinka_vsechny signatury dohromady.csv', 'datasety/O_Bukovinka_vsechny signatury dohromady.csv']
    #file_names = ['datasety/Bukovinka - matriky - otec a matka.csv']
    f = open("Testing_result_one_file.txt", "w")
    f.write('File name ' + file_names[0] + '\n')
    f.close()

    #while precision < 0.96:
    f = open("Testing_result_one_file.txt", "a")
    f.write('\nPrecision - ' + str(round(precision, 2)) + '\n')
    f.write('Potential precision - ' + str(round(precision_potential, 2)) + '\n')
    f.close()
    start_time = time()
    graph_database = GraphDatabaseHandle('create')
    excel_file = ExcelDatabaseHandle(file_names[0], json_files)
    excel_file_burial = ExcelDatabaseHandle(file_names[1], json_files)
    excel_file_marriage = ExcelDatabaseHandle(file_names[2], json_files)
    excel_files = [excel_file, excel_file_burial, excel_file_marriage]
    new_database = NewDatabase(excel_files, graph_database, 'csv', precision, precision_potential)
    new_database.create_new_graph_database_test()
    new_database.write_stats_to_file('Testing_result_one_file.txt')
    graph_database.close()
    print('Time of comparing ' + str(time() - start_time) + '\n\n')
    f = open("Testing_result_one_file.txt", "a")
    f.write('Time of comparing ' + str(time() - start_time) + '\n\n')
    f.close()
    if (precision * 100) % 5 == 0:
        precision += 0.02
        precision_potential += 0.02
    else:
        precision += 0.03
        precision_potential += 0.03

def main_testing():
    f = open("Testing_result.txt", "w")
    f.write("")
    f.close()
    precision = 0.95
    precision_potential = 0.7
    json_files = get_json_files()

    file_names = ['datasety/Bukovinka - matriky - 4 prarodice.csv', 'datasety/Bukovinka - matriky - otec matky.csv',
                  'datasety/Bukovinka - matriky - prijmeni matky.csv', 'datasety/Bukovinka - matriky - otec a matka.csv',
                  'datasety/BukovinkaOut RAW - promazane.csv', 'datasety/BukovinkaOut RAW - promazane - otec matky.csv',
                  'datasety/BukovinkaOut RAW - promazane - prijmeni matky.csv', 'datasety/Bukovinka - matriky - otec a matka.csv']

    for file in file_names:
        f = open("Testing_result.txt", "a")
        f.write('\nFile name ' + file + '\n')
        f.close()
        start_time = time()
        print('Spracuváva sa súbor: ' + str(file) + '\n')
        graph_database = GraphDatabaseHandle('create')
        excel_file = ExcelDatabaseHandle(file, json_files)
        new_database = NewDatabase(excel_file, graph_database, 'csv', precision, precision_potential)
        new_database.create_new_graph_database_test()
        new_database.write_stats_to_file('Testing_result.txt')
        graph_database.close()
        f = open("Testing_result.txt", "a")
        f.write('Time of comparation ' + str(time() - start_time) + '\n')
        f.close()

# Funkcia nacita JSON subory s GPS suradnicami miest a vrati ich v liste
def get_json_files():
    json_files = []
    with open('json/actapublica_ruian.json') as json_file:
        json_file2 = load(json_file)
    with open('json/opava-ruian.json') as json_file:
        json_file1 = load(json_file)

    json_files.append(json_file1)
    json_files.append(json_file2)
    return json_files

# Spustenie s parametrom -database pusta skript nad sql databazou a spustenie s parametrom -test pusta skript nad testovacou sadou
if __name__ == "__main__":
    if (len(argv) - 1) != 1:
        raise Exception('Zle zadane argumenty programu!')

    if argv[1] == "-database":
        main()
    elif argv[1] == "-test":
        main_testing_precision()
    else:
        print('Zle zadane argumenty programu!')