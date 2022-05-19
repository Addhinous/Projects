from curses.ascii import isdigit
import Levenshtein
import geopy.distance
from domicile import Domicile
from person import Person
from datetime import datetime
from datetime import date
import numpy
from copy import deepcopy
from pyjarowinkler import distance as dst
import jellyfish

# comparation result
# -1 - neporovnavalo sa lebo neboli hodnoty
#  0 - ziadna zhoda
#  1 - uplna zhoda

# Zakladne porovnanie normalizovane
def basic_check_of_two_person(person1: Person(), person2: Person()):
    if len(person1.name_normalized) > 0 and len(person2.name_normalized) > 0:
        if compare_exact(person1.name_normalized, person2.name_normalized):
            return True
    if len(person1.surname_normalized) > 0 and len(person2.surname_normalized) > 0:
        if compare_exact(person1.surname_normalized, person2.surname_normalized):
            return True
    if len(person1.occupation_normalized) > 0 and len(person2.occupation_normalized) > 0:
        if compare_exact(person1.occupation_normalized, person2.occupation_normalized):
            return True
    if len(person1.domicile) > 0 and len(person2.domicile) > 0:
        if compare_exact_town(person1.domicile, person2.domicile):
            return True
    return False

# Zakladne porovnanie nenormalizovane
def basic_check_of_two_person_not_normalized(person1: Person(), person2: Person()):
    if len(person1.name) > 0 and len(person2.name) > 0:
        if compare_exact(person1.name, person2.name):
            return True
    if len(person1.surname) > 0 and len(person2.surname) > 0:
        if compare_exact(person1.surname, person2.surname):
            return True
    if len(person1.occupation) > 0 and len(person2.occupation) > 0:
        if compare_exact(person1.occupation, person2.occupation):
            return True
    if len(person1.domicile) > 0 and len(person2.domicile) > 0:
        if compare_exact_town(person1.domicile, person2.domicile):
            return True
    return False

# Detailne porovnanie
def detailed_comparison_of_two_persons(person1: Person(), person2: Person()):
    p1_domicile_list = []
    p2_domicile_list = []
    tmp = Domicile()
    for domicile in person2.domicile:
        if domicile.normalized_town:
            tmp.normalized_town = domicile.normalized_town
        else:
            tmp.normalized_town = None
        if domicile.town:
            tmp.town = domicile.town
        else:
            tmp.town = None
        if not tmp.normalized_town and not tmp.town:
            continue
        if domicile.street:
            tmp.street = domicile.street[0]
        else:
            tmp.street = None
        if domicile.street_number and domicile.street_number != '?':
            tmp.street_number = domicile.street_number[0]
        else:
            tmp.street_number = None
        p2_domicile_list.append(deepcopy(tmp))
    for domicile in person1.domicile:
        if domicile.normalized_town:
            tmp.normalized_town = domicile.normalized_town
        else:
            tmp.normalized_town = None
        if domicile.town:
            tmp.town = domicile.town
        else:
            tmp.town = None
        if not tmp.normalized_town and not tmp.town:
            continue
        if domicile.street:
            tmp.street = domicile.street[0]
        else:
            tmp.street = None
        if domicile.street_number and domicile.street_number != '?':
            tmp.street_number = domicile.street_number[0]
        else:
            tmp.street_number = None
        p1_domicile_list.append(deepcopy(tmp))
    comparison = {
        "name": compare_exact(person1.name_normalized, person2.name_normalized),
        "surname": compare_exact(person1.surname_normalized, person2.surname_normalized),
        "occupation": compare_exact(person1.occupation_normalized, person2.occupation_normalized),
        "title": compare_string(person1.title, person2.title),
        "birth_date": compare_birth_date(person1.birth_date, person2.birth_date),
        "dead_date": compare_date(person1.dead_date, person2.dead_date),
        "street_number": compare_street_number(p1_domicile_list, p2_domicile_list),
        "street": compare_street(p1_domicile_list, p2_domicile_list),
        "town": compare_town(p1_domicile_list, p2_domicile_list),
        "religion": compare_string(person1.religion, person2.religion),
        "waif_flag": compare_exact(person1.waif_flag, person2.waif_flag),
        "father_dead_flag": compare_exact(person1.father_dead_flag, person2.father_dead_flag),
        "church_get_off_date": compare_date(person1.church_get_off_date, person2.church_get_off_date),
        "church_reenter_date": compare_date(person1.church_reenter_date, person2.church_reenter_date),
        "baptism_date": compare_date(person1.baptism_date, person2.baptism_date),
        "legitimate": compare_exact(person1.legitimate, person2.legitimate),
        "multiple_kids": compare_exact(person1.multiple_kids, person2.multiple_kids),
        "parents_marriage_date": compare_date(person1.parents_marriage_date, person2.parents_marriage_date),
        "burial_date": compare_date(person1.burial_date, person2.burial_date),
        "death_cause": compare_exact(person1.death_cause, person2.death_cause),
        "viaticum": compare_exact(person1.viaticum, person2.viaticum),
        "viaticum_date": compare_date(person1.viaticum_date, person2.viaticum_date),
        "examination": compare_exact(person1.examination, person2.examination),
        "marriage_date": compare_date(person1.marriage_date, person2.marriage_date),
        "dead_born": compare_exact(person1.dead_born, person2.dead_born),
        "divorce_date": compare_date(person1.divorce_date, person2.divorce_date)
        }

    # ak neexistuju normalizovane hodnoty
    if comparison['name'] == -1:
        comparison['name'] = compare_string(person1.name, person2.name)

    if comparison['surname'] == -1:
        if len(person1.sex) > 0:
            for sex in person1.sex[0]:
                if sex == 'F' or sex == 'Z':
                    comparison['surname'] = compare_string(person1.surname, person2.surname, 'surname')
                    break
                else:
                    comparison['surname'] = compare_string(person1.surname, person2.surname)
                    break

    if comparison['occupation'] == -1:
        comparison['occupation'] = compare_string(person1.occupation, person2.occupation)

    return comparison

# Vypocitanie klasifikacneho skore
def probabilistic_classification_people(comparison_results):
    final_result = {
        'score': 0.0,
        'reliability': 0.0
    }

    sum_comparison_stat = {
        'all_values': 0,
        'filled_values': 0,
        'unfilled_values': 0,
        'match': 0,
        'non_match': 0,
        'result': 0,
        'possible_result': 0
    }

    comparison_stats = []
    for comparison_result in comparison_results:
        comparison_stats.append(count_matches_and_filled_values(comparison_result))

    for comparison_stat in comparison_stats:
        sum_comparison_stat['all_values'] += comparison_stat['all_values']
        sum_comparison_stat['unfilled_values'] += comparison_stat['unfilled_values']
        sum_comparison_stat['filled_values'] += comparison_stat['filled_values']
        sum_comparison_stat['match'] += comparison_stat['match']
        sum_comparison_stat['non_match'] += comparison_stat['non_match']
        sum_comparison_stat['result'] += comparison_stat['result']
        sum_comparison_stat['possible_result'] += comparison_stat['possible_result']

    if sum_comparison_stat['non_match'] > 0:
        final_result['score'] = sum_comparison_stat['result'] / sum_comparison_stat['possible_result']
    else:
        final_result['score'] = 1

    if sum_comparison_stat['filled_values'] > 0:
        final_result['reliability'] = sum_comparison_stat['filled_values'] / sum_comparison_stat['all_values']
    else:
        final_result['reliability'] = 0
    return final_result


def count_matches_and_filled_values(comparison_result):
    final_result = {
        'all_values': len(comparison_result),
        'filled_values': 0,
        'unfilled_values': 0,
        'match': 0,
        'non_match': 0,
        'result': 0,
        'possible_result': 0
    }

    for value in comparison_result:
        if comparison_result[value] == -1:
            final_result['unfilled_values'] += 1
        else:
            final_result['filled_values'] += 1
            final_result['result'] += add_value_multiplied_by_weight(comparison_result, value)
            final_result['possible_result'] += add_possible_value_multiplied_by_weight(value)
            if comparison_result[value] > 0.5:
                final_result['match'] += 1
            else:
                final_result['non_match'] += 1
    return final_result


def add_value_multiplied_by_weight(comparison_result, value):
    if value == 'name' or value == 'surname':
        return comparison_result[value] * 1
    if value == 'occupation':
        return comparison_result[value] * 0.5
    if value == 'street_number' or value == 'street' or value == 'town':
        return comparison_result[value] * 0.5
    if value == 'religion':
        return comparison_result[value] * 0.1
    return comparison_result[value]


def add_possible_value_multiplied_by_weight(value):
    if value == 'name' or value == 'surname' or value == 'birth_date':
        return 1
    if value == 'occupation':
        return 0.5
    if value == 'street_number' or value == 'street' or value == 'town':
        return 0.5
    if value == 'religion':
        return 0.1
    return 0.5


def compare_street_number(first, second):
    result = -1
    for domicile1 in first:
        for domicile2 in second:
            if domicile1.not_empty() and domicile2.not_empty():
                if not domicile1.street_number or domicile1.street_number == '?' or not domicile2.street_number or domicile2.street_number == '?':
                    continue
                result1 = number_distance(domicile1.street_number, domicile2.street_number)
                result2 = levenshtein_distance(domicile1.street_number, domicile2.street_number, 'number')
                if result1 > result:
                    result = result1
                if result2 > result:
                    result = result2
    return result


def compare_street(first, second):
    result = -1
    best_distance = -1
    for domicile1 in first:
        for domicile2 in second:
            if domicile1.not_empty() and domicile2.not_empty():
                result = levenshtein_distance(domicile1.street, domicile2.street, 'string')
                if result > best_distance:
                    best_distance = result
    return best_distance


def compare_string(first, second, surname=None):
    result = -1
    if check_list(first, second):
        result = levenshtein_distance_list(first, second, surname)
    return result


def compare_town(first, second):
    result = -1
    best_distance = -1
    for domicile1 in first:
        for domicile2 in second:
            if domicile1.not_empty() and domicile2.not_empty():
                result = compare_exact_one_value(domicile1.normalized_town, domicile2.normalized_town)
                if result == -1:
                    result = compare_exact_one_value(domicile1.town, domicile2.town)
                if result < 1:
                    result = town_distance(domicile1, domicile2)
                if result > best_distance:
                    best_distance = result
    return best_distance


def compare_date(first, second):
    result = -1
    if check_date_list(first, second):
        result1 = levenshtein_distance_list(first, second, 'date')
        result2 = check_date(first, second)
        if result1 > result2:
            result = result1
        else:
            result = result2
    return result


def compare_birth_date(first, second):
    result = -1
    if check_date_list(first, second):
        result1 = compare_date(first, second)
        result2 = age_distance(first, second)
        if result1 > result2:
            result = result1
        else:
            result = result2
    return result


def compare_exact(first, second):
    if check_list(first, second):
        for word1 in first:
            for word2 in second:
                if word1 == word2:
                    return 1
        return 0
    return -1


def compare_exact_one_value(first, second):
    if first is not None and second is not None:
        if first == second:
            return 1
        return 0
    return -1


def compare_exact_town(first, second):
    for domicile1 in first:
        for domicile2 in second:
            if domicile1.not_empty or domicile2.not_empty:
                word1 = domicile1.normalized_town
                word2 = domicile2.normalized_town
                if word1 == word2:
                    return 1
                word1 = domicile1.town
                word2 = domicile2.town
                if word1 == word2:
                    return 1
        return 0
    return -1


def levenshtein_distance_list(first, second, type_distance=None):
    best_distance = 0.0
    for word1 in first:
        for word2 in second:
            distance = levenshtein_distance(word1, word2, type_distance)
            if distance > best_distance:
                best_distance = distance
    return best_distance


def levenshtein_distance(first, second, type_distance=None):    #similiarity, not distance
    distance = -1
    if first is not None and second is not None:
        if type_distance == 'date':
            first = first.strftime("%m/%d/%Y")
            second = second.strftime("%m/%d/%Y")
        if type_distance == 'number':
            first = str(first)
            second = str(second)
        if type_distance == 'surname':
            if first[-3:] == 'ová' or first[-3:] == 'ova':
                first = first[:-3]
            if second[-3:] == 'ová' or second[-3:] == 'ova':
                second = second[:-3]

        distance = 1.0 - (Levenshtein.distance(first, second) / max(len(first), len(second)))
    return distance

def jaro_sim_list(first, second, type_distance=None):
    best_distance = 0.0
    for word1 in first:
        for word2 in second:
            distance = jaro_sim(word1, word2, type_distance)
            if distance > best_distance:
                best_distance = distance
    return best_distance

def jaro_sim(first, second, type_distance=None):
    dist = -1
    if first is not None and second is not None:
        #Comment this block if not using dates and numbers
        '''
        if type_distance == 'date':
            first = first.strftime("%m/%d/%Y")
            second = second.strftime("%m/%d/%Y")
        if type_distance == 'number':
            first = str(first)
            second = str(second)
        '''
        #############################################
        if type_distance == 'surname':
            if first[-3:] == 'ová' or first[-3:] == 'ova':
                first = first[:-3]
            if second[-3:] == 'ová' or second[-3:] == 'ova':
                second = second[:-3]

        #dist = jellyfish.jaro_winkler_similarity(first, second)
        dist = Levenshtein.jaro(first, second)
    return dist

def age_distance(first, second):
    best_distance = 0.0
    max_distance = 10
    for date1 in first:
        for date2 in second:
            age1 = calculate_age(date1)
            age2 = calculate_age(date2)
            difference = (abs(age1 - age2) / max(abs(age1), abs(age2)))*100
            if difference < max_distance:
                distance = 1 - (difference / max_distance)
            else:
                distance = 0

            if distance > best_distance:   #distance.days ???
                best_distance = distance   #
    return best_distance


def number_distance(first, second):
    max_distance = 10
    distance = -1
    if first is not None and second is not None and first != '?' and second != '?':
        if first.isdigit() and second.isdigit():
            difference = abs(int(first) - int(second))
        else:
            num1 = ''.join(filter(str.isdigit, first))
            num2 = ''.join(filter(str.isdigit, second))
            if not num1 or not num2:
                return distance
            difference = abs(int(num1)) - int(num2)
        if difference < max_distance:
            distance = 1 - (difference / max_distance)
        else:
            distance = 0
    return distance

def town_distance(first, second):
    distance = 0.0
    if first.gps_coordinates['latitude'] != 0.0 and first.gps_coordinates['longitude'] != 0.0:
        coords_1 = (float(first.gps_coordinates['latitude']), float(first.gps_coordinates['longitude']))
        coords_2 = (float(second.gps_coordinates['latitude']), float(second.gps_coordinates['longitude']))
        distance = geopy.distance.geodesic(coords_1, coords_2).km   #Changed from vincenty to geodesic https://stackoverflow.com/questions/62858552/why-cant-i-import-geopy-distance-vincenty-on-jupyter-notebook-i-installed-ge
        exponential_probability(distance)
    return distance

def exponential_probability(distance):
    max_distance = 100
    if distance != 0:
        if distance < max_distance:
            exp_distance = numpy.exp(distance)
            exp_max = numpy.exp(max_distance)
            probability = 1 - (exp_distance / exp_max)
        else:
            probability = 0
    else:
        probability = 1
    return probability

def check_date(first, second):
    best_distance = 0.0
    for date1 in first:
        for date2 in second:
            if date1.day == date2.month:
                best_distance = 0.5
            if date1.month == date2.day:
                best_distance = 0.5
    return best_distance

def check_date_list(first, second):
    if check_list(first, second):
        for word in first:
            if word is None:
                return False
        for word in second:
            if word is None:
                return False
        return True
    return False

def check_list(first, second):
    if not first or not second:
        return False
    for word in first:
        if not word or word == 'None':
            return False
    for word in second:
        if not word or word == 'None':
            return False
    return True

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))