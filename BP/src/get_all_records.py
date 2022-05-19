from graph_database import GraphDatabaseHandle
from record import Record
import sys
from datetime import datetime
import json

def check_arguments():
    arguments = len(sys.argv) - 1

    if arguments != 2 and arguments != 3:
        raise Exception("Musíte zadať všetky potrebné argumenty!")

    if sys.argv[1] != "-id":
        raise Exception("Prvý argument musí byť -id!")

    if arguments == 3:
        if sys.argv[3] != "-j":
            raise Exception("Argument pre výpis vo formáte json je -j. Argument musí byť posledný.")
        return True
    return False

def main():
    json_out = check_arguments()
    id_person = sys.argv[2]
    graph_database = GraphDatabaseHandle('get')
    person = graph_database.get_person_based_on_id_from_graph_db(id_person)
    records = []

    records_b = graph_database.get_all_birth_records_of_person_from_graph_db(id_person)
    for record in records_b:
        if record:
            record['type'] = 'narodenie'
            if record["relation.date"] and record['relation.date'] != 'None' and record['relation.date'] != 'none':
                tmp = datetime.strptime(record['relation.date'][:-9], "%Y-%m-%d")
                record['relation.date'] = datetime.strftime(tmp, "%d.%m.%Y")

    records_d = graph_database.get_all_dead_records_of_person_from_graph_db(id_person)
    for record in records_d:
        if record:
            record['type'] = 'umrtie'
            if record["relation.date"] and record['relation.date'] != 'None' and record['relation.date'] != 'none':
                tmp = datetime.strptime(record['relation.date'][:-9], "%Y-%m-%d")
                record['relation.date'] = datetime.strftime(tmp, "%d.%m.%Y")

    records_m = graph_database.get_all_marriage_records_of_person_from_graph_db(id_person)
    for record in records_m:
        if record:
            record['type'] = 'sobas'
            if record["relation.date"] and record['relation.date'] != 'None' and record['relation.date'] != 'none':
                tmp = datetime.strptime(record['relation.date'][:-9], "%Y-%m-%d")
                record['relation.date'] = datetime.strftime(tmp, "%d.%m.%Y")

    records = records_b + records_d + records_m
    if json_out:
        for record in records:
            if record:
                new_record = Record()
                new_record.get_record_from_graph_db(record['record'])
                record_dict = new_record.get_json()
                record_dict['rola'] = str(record['relation'][1])
                record_dict['datum'] = str(record['relation.date'])
                record_dict["typ"] = record['type']
                record_dict['id'] = record['record']['id_relačná_databáza']
                print(json.dumps(record_dict, indent = 4, sort_keys=True, ensure_ascii=False))
    else:
        print("Hledaná osoba: ")
        person.print_czech()
        print("\nNalezena v následujících záznamech: ")
        i = 1
        for record in records:
            if len(record) != 0:
                print('....................................')
                print(str(i) + '. záznam ')
                print('  Rola osoby v zázname = ' + str(record['relation'][1]))
                print('  Dátum záznamu = ' + str(record['relation.date']))
                new_record = Record()
                new_record.get_record_from_graph_db(record['record'])
                new_record.print_czech()
                i += 1

    graph_database.close()


if __name__ == "__main__":
    main()
