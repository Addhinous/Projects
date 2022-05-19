from graph_database import GraphDatabaseHandle
import sys


def check_arguments():
    arguments = len(sys.argv) - 1

    if arguments != 4 and arguments != 5:
        raise Exception("Musite zadať všetky potrebné argumenty!")

    if sys.argv[1] != "-name":
        raise Exception("Prvy argument musi byt -name!")

    if not isinstance(sys.argv[2], str):
        raise Exception("Meno musi byt slovo!")

    if sys.argv[3] != "-surname":
        raise Exception("Druhy argument musi byt -surname!")

    if not isinstance(sys.argv[4], str):
        raise Exception("Priezvisko nie je slovo!")

    if arguments == 5:
        if sys.argv[5] != "-j":
            raise Exception("Nespravne zadany posledny argument. Pre vypis osoby vo formate json pouzite -j")
        return True
    return False

def main():
    print_json = check_arguments()
    name = sys.argv[2]
    surname = sys.argv[4]
    
    graph_database = GraphDatabaseHandle('get')
    people = graph_database.get_person_based_on_name_and_surname_from_graph_db(name, surname)
    i = 1
    for person in people:
        person_to_print = graph_database.get_person_detail(person['person'])
        if not print_json:
            print("Hledaná osoba " + str(name) + " " + str(surname))
            print('....................................')
            print(str(i) + '.  nalezena osoba ')
            person_to_print.print_czech()
        else:
            print(person_to_print.person_json())
        i += 1

    graph_database.close()


if __name__ == "__main__":
    main()



