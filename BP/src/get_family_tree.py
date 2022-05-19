from graph_database import GraphDatabaseHandle
import sys
from copy import deepcopy
import json


def check_arguments():
    arguments = len(sys.argv) - 1

    if arguments != 2 and arguments != 3:
        raise Exception("You must set all arguments than necessary!")

    if sys.argv[1] != "-id":
        raise Exception("First argument must be -id!")
    
    if arguments == 3:
        if sys.argv[3] != '-j':
            raise Exception("Argument pre výpis vo formáte json je -j. Argument musí byť posledný.")
        return True
    return False


def print_children(graph_database, person, level):
    children = graph_database.get_children_of_person_from_graph_db(person.id)
    i = 1
    if len(children) > 0:
        if level > 2:
            print_tabs(level-2)
        print("Potomkovia: ", end="")
        print_name(person)
        print('')
        if level > 2:
            print_tabs(level - 2)
            print('----------------------------------------------')

    for child in children:
        child_new = graph_database.get_person_detail(child['osoba'])
        print_tabs(level)
        print('Prepojenie s osobou = ', end="")
        print_name(person)
        if('type' in child['relation']):
            print(' ' + str(child['relation'].type) + ' ', end="")
        print_name(child_new)
        child_new.print_czech(level)
        print_children(graph_database, child_new, level + 5)
        i += 1


def print_parents(graph_database, person, level):
    parents = graph_database.get_parents_of_person_from_graph_db(person.id)
    i = 1
    if len(parents) > 0:
        if level > 2:
            print_tabs(level - 2)
        print("Rodiče: ", end="")
        print_name(person)
        print('')
        if level > 2:
            print_tabs(level - 2)
        print('----------------------------------------------')

    for parent in parents:
        parent_new = graph_database.get_person_detail(parent['osoba'])
        print_tabs(level)
        print('Prepojenie s osobou = ', end="")
        print_name(parent_new)
        if('type' in parent['relation']):
            print(' ' + str(parent['relation'].type) + ' ', end="")
        print_name(person)
        parent_new.print_czech(level)
        print_parents(graph_database, parent_new, level + 5)
        i += 1

def get_parents(graph_database, person_dict):
    father = graph_database.get_father_of_person_from_graph_db(person_dict["id"])
    mother = graph_database.get_mother_of_person_from_graph_db(person_dict["id"])
    mother_dict = father_dict = None
    if father:
        father_dict = get_parents(graph_database, father.person_json_family())
    if mother:
        mother_dict = get_parents(graph_database, mother.person_json_family())
    if mother_dict:
        person_dict["matka"] = mother_dict
    if father_dict:
        person_dict["otec"] = father_dict
    return person_dict

def get_children(graph_database, person_dict):
    children = graph_database.get_children_of_person_from_graph_db(person_dict["id"])
    children_list = []
    for child in children:
        children_list.append(child.person_json_family())
    return children_list

def main():
    json_out = check_arguments()
    id_person = sys.argv[2]
    graph_database = GraphDatabaseHandle('get')
    person = graph_database.get_person_based_on_id_from_graph_db(id_person)
    if json_out:
        if person:
            person_children = get_children(graph_database, person.person_json_family())
            person_dict = get_parents(graph_database, person.person_json_family())
            if person_children:
                person_dict["deti"] = person_children
            
            print(json.dumps(person_dict, indent = 8, sort_keys=False, ensure_ascii=False))
    else:
        if person is None:
            print('Osoba sa v databáze nenachádza ')
        else:
            print("Hledaná osoba: ")
            person.print_czech(0)
            level = 2
            print("POTOMKOVIA")
            print_children(graph_database, person, level)
            print("RODIČE")
            print_parents(graph_database, person, level)

    graph_database.close()


def print_name(person):
    if len(person.name_normalized) != 0:
        print_list(person.name_normalized)
    else:
        print_list(person.name)
    if len(person.surname_normalized) != 0:
        print_list(person.surname_normalized)
    else:
        print_list(person.surname)
    print('(ID ', end="")
    if person.id is not None:
        print(str(person.id) + ') ', end="")


def print_list(words):
    if words is not None:
        for word in words:
            print(str(word) + ' ',  end="")


def print_tabs(tabs):
    while tabs:
        tabs -= 1
        print("\t", end="")


if __name__ == "__main__":
    main()
