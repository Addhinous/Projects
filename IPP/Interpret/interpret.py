import sys
import xml.etree.ElementTree as et
import re

#Funkcia nahradzujuca utf-8 escape sekvencie v retazci 's' prislusnym znakom.
def string_escape(s):
    liststring = list(s)
    for i in range(0, len(liststring) - 1):
        numstr = []
        if(liststring[i] == "\\"):
            if liststring[i+2] == "0":
                s = re.sub(r"\\00[0-9]{1}", "", s)
            elif liststring[i+2] == "1":
                if(liststring[i+3] == "0"):
                    s = re.sub(r"\\010", "\n", s)
                else:
                    s = re.sub(r"\\01[0-9]{1}", "", s)
            elif liststring[i+2] == "2":
                s = re.sub(r"\\02[0-9]{1}", "", s)
            elif liststring[i+2] == "3":
                if liststring[i+3] == "0":
                    s = re.sub(r"\\030", "", s)
                elif liststring[i+3] == "1":
                    s = re.sub(r"\\031", "", s)
                elif liststring[i+3] == "2":
                    s = re.sub(r"\\032", " ", s)
                elif liststring[i+3] == "5":
                    s = re.sub(r"\\035", "#", s)
            elif liststring[i+2] == "9":
                if liststring[i+3] == "2":
                    s = re.sub(r"\\092", "\\", s)
            elif re.search(r"\\[0-9]{3}", s):
                numstr.append(liststring[i + 1])
                numstr.append(liststring[i + 2])
                numstr.append(liststring[i + 3])
                numstr = "".join(numstr)
                s = re.sub(r"\\[0-9]{3}", chr(int(numstr)), s)
                numstr = []
            else:
                continue
    return s

source_found = False
input_found = False
sourcef = ""
inputf = ""

symb = re.compile(r"^([LGT]F{1}@{1}[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$)|(^((([^#\\\s])|([\\][0-9]{3}))*$)|^([+-]?[0-9]+$)|^((\bfalse\b|\btrue\b)$)|^(\bnil\b)$)")
var = re.compile(r"^[LGT]F{1}@{1}[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$")
type_re = re.compile(r"^(\bint\b)$|^(\bstring\b)$|^(\bbool\b)$|^(\bnil\b)$")
label = re.compile(r"^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$")
Gvar = re.compile(r"^G{1}F{1}@{1}[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$")
Tvar = re.compile(r"^T{1}F{1}@{1}[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$")
Lvar = re.compile(r"^L{1}F{1}@{1}[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$")
String = re.compile(r"^(([^#\\\s])|([\\][0-9]{3}))*$")
Int = re.compile(r"^([+-]?[0-9]+$)")
Bool = re.compile(r"^(\bfalse\b|\btrue\b)$")
Nil = re.compile(r"^(\bnil\b)$")
Arg_re = re.compile(r"^a{1}r{1}g{1}[1-9]{1}$")

if(len(sys.argv) == 2):
    arr = sys.argv[1].split('=')
    if(sys.argv[1] == "--help"):
        print("Skript interpret.py načíta zo štandardného vstupu xml reprezentáciu kódu v IPPcode21, skontroluje správnosť a interpretuje\n jednotlivé inštrukcie v jazyku python 3.8.5")
        exit(0)
    elif(arr[0] == "--source"):
        source_found = True
        sourcef = arr[1]
    elif(arr[0] == "--input"):
        input_found = True
        inputf = arr[1]
    else:
        exit(10)
elif(len(sys.argv) == 3):
    arr1 = sys.argv[1].split('=')
    arr2 = sys.argv[2].split('=')
    if(arr1[0] == "--source"):
        source_found = True
        sourcef = arr1[1]
    elif(arr1[0] == "--input"):
        input_found = True
        inputf = arr1[1]
    else:
        exit(10)
    if(arr2[0] == "--source"):
        if(source_found):
            exit(10)
        source_found = True
        sourcef = arr2[1]
    elif(arr2[0] == "--input"):
        if(input_found):
            exit(10)
        input_found = True
        inputf = arr2[1]
    else:
        exit(10)
else:
    exit(10)

if inputf != "":
    try:
        input_descriptor = open(inputf)
    except:
        exit(32)

if sourcef != "":
    sourcefile = open(sourcef, 'rb')
    try:
        tree = et.parse(sourcefile)
    except:
        exit(31)
else:
    try:
        tree = et.parse(sys.stdin)
    except Exception as ex:
        exit(31)

root = tree.getroot()
sys.stdin = input_descriptor

if(root.tag != 'program'):
    exit(32)
if 'language' in root.attrib:
    attribute = root.get('language')
    if attribute != "IPPcode21":
        exit(32)

ar_tp = []
type_counter = 0
first = True
instructions = []
pc = []
args = {}
labels = []
index_order = 0
for instruction in root:
    for child in instruction:
        if(not re.match(Arg_re, child.tag)):
            exit(32)
    if(instruction.tag != "instruction"):
        exit(32)
    try:
        order = int(instruction.get('order'))
    except:
        exit(32)
    if(order <= 0):
        exit(32)
    opcode = instruction.get('opcode')
    if not opcode:
        exit(32)
    opcode = opcode.upper()
    if(first):
        first = False
        pc.append(order)
        instructions.append(opcode)
    else:
        for i in range(0, len(pc)):
            if order > pc[i] and i<len(pc)-1:
                if order < pc[i+1]:
                    pc.insert(i+1, order)
                    instructions.insert(i+1, opcode)
                    break
                elif order > pc[i+1]:
                    continue
                else:
                    exit(32)
            elif order > pc[i] and i == len(pc)-1:
                pc.append(order)
                instructions.append(opcode)
                break
            elif order < pc[i] and i > 0:
                pc.insert(i-1, order)
                instructions.insert(i-1, opcode)
                break
            elif order < pc[i] and i == 0:
                pc.insert(0, order)
                instructions.insert(0, opcode)
                break
            else:
                exit(32)


    temporary = []
    ar_tp.append(temporary)
    iterations = 0
    if(opcode == "MOVE" or opcode == "INT2CHAR" or opcode == "STRLEN" or opcode == "TYPE" or opcode == "NOT"):
        args[order] = {}
        ar_tp[index_order].append(None)
        ar_tp[index_order].append(None)  
        for arg in instruction:
            argtype = arg.get('type')
            if(arg.tag == "arg1"):
                if(argtype != "var"):
                    exit(32)
                if(not re.match(var, instruction[iterations].text)):
                    exit(32)
                args[order][0] = instruction[iterations].text
                ar_tp[index_order][0] = argtype
            elif(arg.tag == "arg2"):
                if(argtype != "var" and argtype != "string" and argtype != "int" and argtype != "nil" and argtype != "bool"):
                    exit(32)
                if(argtype == "string" and instruction[iterations].text is None):
                    args[order][1] = None
                    iterations = iterations + 1
                    ar_tp[index_order][1] = argtype
                    continue
                if(not re.match(symb, instruction[iterations].text)):
                    exit(32)
                args[order][1] = instruction[iterations].text
                ar_tp[index_order][1] = argtype
            else:
                exit(32)
            iterations = iterations + 1
        if(iterations != 2):
            exit(32)
    
    elif(opcode == "CREATEFRAME" or opcode == "PUSHFRAME" or opcode == "POPFRAME" or opcode == "RETURN" or opcode == "BREAK"):
        args[order] = {}
        for arg in instruction:
            iterations = iterations + 1
        if(iterations != 0):
            exit(32)
    
    elif(opcode == "DEFVAR" or opcode == "POPS"):
        args[order] = {}
        ar_tp[index_order].append(None)
        for arg in instruction:
            argtype = arg.get('type')
            if(arg.tag == "arg1"):
                if(argtype != "var"):
                    exit(32)
                if(not re.match(var, instruction[iterations].text)):
                    exit(32)
                args[order][0] = instruction[iterations].text
                ar_tp[index_order][0] = argtype
            else:
                exit(32) 
            iterations = iterations + 1
        if(iterations != 1):
            exit(32)

    elif(opcode == "CALL" or opcode == "LABEL" or opcode == "JUMP"):
        args[order] = {}
        ar_tp[index_order].append(None)
        for arg in instruction:
            argtype = arg.get('type')
            if(arg.tag == "arg1"):
                if(argtype != "label"):
                    exit(32)
                if(not re.match(label, instruction[iterations].text)):
                    exit(32)
                if(opcode == "LABEL"):
                    labels.append([index_order, instruction[iterations].text])
                args[order][0] = instruction[iterations].text
                ar_tp[index_order][0] = argtype
            else:
                exit(32)
            iterations = iterations + 1
        if(iterations != 1):
            exit(32)

    elif(opcode == "PUSHS" or opcode == "WRITE" or opcode == "EXIT" or opcode == "DPRINT"):
        args[order] = {}
        ar_tp[index_order].append(None)
        for arg in instruction:
            argtype = arg.get('type')
            if(arg.tag == "arg1"):
                if(argtype != "var" and argtype != "string" and argtype != "int" and argtype != "nil" and argtype != "bool"):
                    exit(32)
                if(argtype == "string" and instruction[iterations].text is None):
                    args[order][0] = ""
                    iterations = iterations + 1
                    ar_tp[index_order][0] = "string"
                    continue
                if(not re.match(symb, instruction[iterations].text)):
                    exit(32)
                args[order][0] = instruction[iterations].text
                ar_tp[index_order][0] = argtype
            else:
                exit(32) 
            iterations = iterations + 1
        if(iterations != 1):
            exit(32)

    elif(opcode == "ADD" or opcode == "SUB" or opcode == "MUL" or opcode == "IDIV" or opcode == "LT" or opcode == "GT" or opcode == "EQ" or opcode == "AND" or opcode == "OR" or opcode == "STRI2INT" or opcode == "CONCAT" or opcode == "SETCHAR" or opcode == "GETCHAR"):
        args[order] = {}
        ar_tp[index_order].append(None)
        ar_tp[index_order].append(None)
        ar_tp[index_order].append(None)
        for arg in instruction:
            argtype = arg.get('type')
            if(arg.tag == "arg1"):
                if(argtype != "var"):
                    exit(32)
                if(not re.match(var, instruction[iterations].text)):
                    exit(32)
                args[order][0] = instruction[iterations].text
                ar_tp[index_order][0] = argtype
            elif(arg.tag == "arg2"):
                if(argtype != "var" and argtype != "string" and argtype != "int" and argtype != "nil" and argtype != "bool"):
                    exit(32)
                if(argtype == "string" and instruction[iterations].text is None):
                    args[order][1] = ""
                    iterations = iterations + 1
                    ar_tp[index_order].insert(1, argtype)
                    continue
                if(not re.match(symb, instruction[iterations].text)):
                    exit(32)
                args[order][1] = instruction[iterations].text
                ar_tp[index_order][1] = argtype
            elif(arg.tag == "arg3"):
                if(argtype != "var" and argtype != "string" and argtype != "int" and argtype != "nil" and argtype != "bool"):
                    exit(32)
                if(argtype == "string" and instruction[iterations].text is None):
                    args[order][2] = ""
                    iterations = iterations + 1
                    ar_tp[index_order].insert(2, argtype)
                    continue
                if(not re.match(symb, instruction[iterations].text)):
                    exit(32)
                args[order][2] = instruction[iterations].text
                ar_tp[index_order][2] = argtype
            else:
                exit(32)
            iterations = iterations + 1
        if(iterations != 3):
            exit(32)

    elif(opcode == "READ"):
        args[order] = {}
        ar_tp[index_order].append(None)
        ar_tp[index_order].append(None)
        for arg in instruction:
            argtype = arg.get('type')
            if(arg.tag == "arg1"):
                if(argtype != "var"):
                    exit(32)
                if(not re.match(var, instruction[iterations].text)):
                    exit(32)
                args[order][0] = instruction[iterations].text
                ar_tp[index_order][0] = argtype
            elif(arg.tag == "arg2"):
                if(argtype != "type"):
                    exit(32)
                if(not re.match(type_re, instruction[iterations].text)):
                    exit(32)
                args[order][1] = instruction[iterations].text
                ar_tp[index_order][1] = argtype
            else:
                exit(32)
            iterations = iterations + 1
        if(iterations != 2):
            exit(32)


    elif(opcode == "JUMPIFEQ" or opcode == "JUMPIFNEQ"):
        args[order] = {}
        ar_tp[index_order].append(None)
        ar_tp[index_order].append(None)
        ar_tp[index_order].append(None)
        for arg in instruction:
            argtype = arg.get('type')
            if(arg.tag == "arg1"):
                if(argtype != "label"):
                    exit(32)
                if(not re.match(label, instruction[iterations].text)):
                    exit(32)
                args[order][0] = instruction[iterations].text
                ar_tp[index_order][0] = argtype
            elif(arg.tag == "arg2"):
                if(argtype != "var" and argtype != "string" and argtype != "int" and argtype != "nil" and argtype != "bool"):
                    exit(32)
                if(argtype == "string" and instruction[iterations].text is None):
                    args[order][1] = ""
                    iterations = iterations + 1
                    ar_tp[index_order][1] = argtype
                    continue
                if(not re.match(symb, instruction[iterations].text)):
                    exit(32)
                args[order][1] = instruction[iterations].text
                ar_tp[index_order][1] = argtype
            elif(arg.tag == "arg3"):
                if(argtype != "var" and argtype != "string" and argtype != "int" and argtype != "nil" and argtype != "bool"):
                    exit(32)
                if(argtype == "string" and instruction[iterations].text is None):
                    args[order][2] = ""
                    iterations = iterations + 1
                    ar_tp[index_order][2] = argtype
                    continue
                if(not re.match(symb, instruction[iterations].text)):
                    exit(32)
                args[order][2] = instruction[iterations].text
                ar_tp[index_order][2] = argtype
            else:
                exit(32)
            iterations = iterations + 1
        if(iterations != 3):
            exit(32)

    index_order = index_order + 1

sorted_args = {}
sorted_keys = sorted(args.keys())
ar_tp_sorted = []
iterable = 1
for i in sorted_keys:
    for key, value in args.items():
        if i == key:
            sorted_args[iterable] = value
            iterable = iterable + 1


another_counter = 0
for sorted_key in sorted_keys:
    yet_another_counter = 0
    for key in args.keys():
        if sorted_key == key:
            ar_tp_sorted.append(None)
            ar_tp_sorted[another_counter] = ar_tp[yet_another_counter]
            
        yet_another_counter = yet_another_counter + 1
    another_counter = another_counter + 1

ar_tp = ar_tp_sorted
sorted_keys = list(sorted_keys)
if(len(instructions) != len(sorted_args)):
    exit(32)

for i in labels:
    for j in range(0,len(labels)-1):
        if(labels[j] == i):
            continue
        if i[1] == labels[j][1]:
            exit(52)


TF = None
GF = []
LF = None
CALL_STACK = []
FRAME_STACK = []
DATA_STACK = []
var = [None, None, None, None]
symb = [None, None, None, None]
temp = [None, None, None, None]
symb1 = [None, None, None, None]
symb2 = [None, None, None, None]

#Funkcia vrati listovu reprezentaciu literalu alebo premennej. V pripade premennej je premenna najdena v prislusnom ramci a vratena.
def matchfind(symb):
    global GF
    global TF
    global LF

    if(symb is None):
        return [None, "string", "", None]
    elif(re.match(Nil, symb)):
        return [None, "nil", "nil", None]
    elif(re.match(Int, symb)):
        return [None, "int", int(symb), None]
    elif(re.match(Bool, symb)):
        if(symb == "true"):
            return [None, "bool", True, None]
        else:
            return [None, "bool", False, None]
    elif(re.match(Gvar, symb)):
        symblist = list(symb)
        if(symblist[0] != "G"):
            exit(32)
        symb = "".join(symblist[3:])
        for var in GF:
            if(var[0] == symb):
                return var
        return[None, None, None, None]
    elif(re.match(Tvar, symb)):
        if TF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "T"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in TF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    elif(re.match(Lvar, symb)):
        if LF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "L"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in LF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    elif(re.match(String, symb)):
        symb = string_escape(symb)
        return [None, "string", symb, None]
    else:
        return[None, None, None, None]

#Funkcia vrati listovu reprezentaciu literalu alebo premennej. Varianta pre ocakavany typ string (vyssia priorita).
def matchfind_string(symb):
    global GF
    global TF
    global LF

    if(symb is None):
        return [None, "string", "", None]
    elif(re.match(String, symb)):
        symb = string_escape(symb)
        return [None, "string", symb, None]
    elif(re.match(Gvar, symb)):
        symblist = list(symb)
        if(symblist[0] != "G"):
            exit(32)
        symb = "".join(symblist[3:])
        for var in GF:
            if(var[0] == symb):
                return var
        return[None, None, None, None]
    elif(re.match(Tvar, symb)):
        if TF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "T"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in TF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    elif(re.match(Lvar, symb)):
        if LF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "L"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in LF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    else:
        return[None, None, None, None]

#Funkcia vrati listovu reprezentaciu literalu alebo premennej. Varianta pre ocakavany typ bool (vyssia priorita).
def matchfind_bool(symb):
    global GF
    global TF
    global LF

    if(symb is None):
        return [None, "string", "", None]
    elif(re.match(Bool, symb)):
        if(symb == "true"):
            return [None, "bool", True, None]
        else:
            return [None, "bool", False, None]
    elif(re.match(Gvar, symb)):
        symblist = list(symb)
        if(symblist[0] != "G"):
            exit(32)
        symb = "".join(symblist[3:])
        for var in GF:
            if(var[0] == symb):
                return var
        return[None, None, None, None]
    elif(re.match(Tvar, symb)):
        if TF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "T"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in TF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    elif(re.match(Lvar, symb)):
        if LF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "L"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in LF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    else:
        return[None, None, None, None]

#Funkcia vrati listovu reprezentaciu literalu alebo premennej. Varianta pre ocakavany typ nil (vyssia priorita).
def matchfind_nil(symb):
    global GF
    global TF
    global LF

    if(symb is None):
        return [None, "string", "", None]
    elif(re.match(Nil, symb)):
        return [None, "nil", "nil", None]
    elif(re.match(Gvar, symb)):
        symblist = list(symb)
        if(symblist[0] != "G"):
            exit(32)
        symb = "".join(symblist[3:])
        for var in GF:
            if(var[0] == symb):
                return var
        return[None, None, None, None]
    elif(re.match(Tvar, symb)):
        if TF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "T"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in TF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    elif(re.match(Lvar, symb)):
        if LF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "L"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in LF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    else:
        return[None, None, None, None]

#Funkcia vrati listovu reprezentaciu literalu alebo premennej. Varianta pre ocakavany typ int (vyssia priorita).
def matchfind_int(symb):
    global GF
    global TF
    global LF

    if(symb is None):
        return [None, "string", "", None]
    elif(re.match(Int, symb)):
        return [None, "int", int(symb), None]
    elif(re.match(Gvar, symb)):
        symblist = list(symb)
        if(symblist[0] != "G"):
            exit(32)
        symb = "".join(symblist[3:])
        for var in GF:
            if(var[0] == symb):
                return var
        return[None, None, None, None]
    elif(re.match(Tvar, symb)):
        if TF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "T"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in TF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    elif(re.match(Lvar, symb)):
        if LF is None:
            exit(55)
        else:
            symblist = list(symb)
            if(symblist[0] != "L"):
                exit(32)
            symb = "".join(symblist[3:])
            for var in LF:
                if(var[0] == symb):
                    return var
        return[None, None, None, None]
    else:
        return[None, None, None, None]

#Parametrom funkcie su dve listove reprezentacie premennych alebo literalov. Funkcia vracia hodnotu typu bool.
#Funkcia vrati True v pripade ze je typ prvej hodnoty nil alebo sa typy oboch hodnot zhoduju. Inak funkcia vrati False.
def typecmp(symb1, symb2):
    if(symb1[1] == None):
        return True
    elif(symb1[1] == symb2[1]):
        return True
    else:
        return False

# INTERPRETACIA

i = 1
while i<=len(sorted_keys):
    if(instructions[i-1] == "MOVE"):
        var = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb = matchfind_nil(sorted_args[i][1])
        else:
            symb = matchfind(sorted_args[i][1])
        if(var[0] is None or symb == [None, None, None, None]):
            exit(54)
        if(symb[0] is not None and symb[2] is None):
            exit(56)
        if(symb[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var"):
            exit(32)
        var[1] = symb[1]
        var[2] = symb[2]
        i = i + 1

    elif(instructions[i-1] == "CREATEFRAME"):
        TF = []
        i = i + 1

    elif(instructions[i-1] == "PUSHFRAME"):
        if TF is None:
            exit(55)
        FRAME_STACK.append(LF)
        LF = TF
        for var in LF:
            var[3] = "L"
        TF = None
        i = i +1

    elif(instructions[i-1] == "POPFRAME"): #Musi tf uz existovat ?
        if LF is None:
            exit(55)
        TF = LF
        for var in TF:
            var[3] = "T"
        if(len(FRAME_STACK) == 0):
            LF = None
        else:
            LF = FRAME_STACK.pop()
        i = i + 1

    elif(instructions[i-1] == "DEFVAR"):
        temp = matchfind(sorted_args[i][0])
        if(temp != [None, None, None, None]):
            exit(52)
        if(re.match(Gvar, sorted_args[i][0])):
            strlist = list(sorted_args[i][0])[3:]
            toappend = "".join(strlist)
            GF.append([toappend, None, None, "G"])
        elif(re.match(Tvar, sorted_args[i][0])):
            if TF is None:
                exit(55)
            else:
                strlist = list(sorted_args[i][0])[3:]
                toappend = "".join(strlist)
                TF.append([toappend, None, None, "T"])
        elif(re.match(Lvar, sorted_args[i][0])):
            if LF is None:
                exit(55)
            else:
                strlist = list(sorted_args[i][0])[3:]
                toappend = "".join(strlist)
                LF.append([toappend, None, None, "L"])
        i = i + 1

    elif(instructions[i-1] == "CALL"):
        call_found = False
        CALL_STACK.append(i)
        for lab in labels:
            if(sorted_args[i][0] == lab[1]):
                i = lab[0]
                call_found = True
                break
        if(not call_found):
            exit(52)
        i = i + 1
            
    elif(instructions[i-1] == "RETURN"):
        if(len(CALL_STACK) == 0):
            exit(56)
        i = CALL_STACK.pop()
        i = i + 1

    elif(instructions[i-1] == "PUSHS"):         
        if(ar_tp[i-1][0] == "string"):
            symb = matchfind_string(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "int"):
            symb = matchfind_int(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "bool"):
            symb = matchfind_bool(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "nil"):
            symb = matchfind_nil(sorted_args[i][0])
        else:
            symb = matchfind(sorted_args[i][0])
        if(symb[0] is not None and symb[2] is None):
            exit(56)
        if(symb == [None, None, None, None]):
            exit(54)
        DATA_STACK.append(symb)
        i = i + 1

    elif(instructions[i-1] == "POPS"):
        if(len(DATA_STACK) == 0):
            exit(56)
        temp = matchfind(sorted_args[i][0])
        if(temp[0] == None):
            exit(54)
        popped = DATA_STACK.pop()
        if(popped[1] is not None):
            temp[1] = popped[1]
            temp[2] = popped[2]
        else:
            temp[2] = popped[2]

        i = i + 1

    elif(instructions[i-1] == "ADD"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[1] != "int" or symb2[1] != "int"):
            exit(53)
        temp[1] = symb1[1]
        temp[2] = int(symb1[2]) + int(symb2[2])
        i = i + 1
     
    elif(instructions[i-1] == "SUB"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[1] != "int" or symb2[1] != "int"):
            exit(53)
        temp[1] = symb1[1]
        temp[2] = int(symb1[2]) - int(symb2[2])
        i = i + 1

    elif(instructions[i-1] == "MUL"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[1] != "int" or symb2[1] != "int"):
            exit(53)
        temp[1] = symb1[1]
        temp[2] = int(symb1[2]) * int(symb2[2])
        i = i + 1

    elif(instructions[i-1] == "IDIV"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[1] != "int" or symb2[1] != "int"):
            exit(53)
        if(symb2[2] == 0):
            exit(57)
        temp[1] = symb1[1]
        temp[2] = int(symb1[2] / symb2[2])
        i = i + 1

    elif(instructions[i-1] == "LT"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(not typecmp(symb1, symb2) or symb1[1] == "nil"):
            exit(53)
        if(symb1[1] == "string"):
            if(symb1[2] < symb2[2]):
                temp[2] = True
            else:
                temp[2] = False
        elif(symb1[1] == "int"):
            if(symb1[2] < symb2[2]):
                temp[2] = True
            else:
                temp[2] = False
        elif(symb1[1] == "bool"):
            if(not symb1[2] and symb2[2]):
                temp[2] = True
            else:
                temp[2] = False
        temp[1] = "bool"
        i = i + 1

    elif(instructions[i-1] == "GT"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(not typecmp(symb1, symb2) or symb1[1] == "nil"):
            exit(53)
        if(symb1[1] == "string"):
            if(symb1[2] > symb2[2]):
                temp[2] = True
            else:
                temp[2] = False
        elif(symb1[1] == "int"):
            if(symb1[2] > symb2[2]):
                temp[2] = True
            else:
                temp[2] = False
        elif(symb1[1] == "bool"):
            if(symb1[2] and not symb2[2]):
                temp[2] = True
            else:
                temp[2] = False
        temp[1] = "bool"
        i = i + 1

    elif(instructions[i-1] == "EQ"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[1] != symb2[1] and (symb1[1] != "nil" and symb2[1] != "nil")):
            exit(53)
        if(symb1[1] == "string"):
            if(symb1[2] == symb2[2]):
                temp[2] = True
            else:
                temp[2] = False
        elif(symb1[1] == "int"):
            if(symb1[2] == symb2[2]):
                temp[2] = True
            else:
                temp[2] = False
        elif(symb1[1] == "bool" and symb2[1] == "bool"):
            if((not symb1[2] and not symb2[2]) or (symb1[2] and symb2[2])):
                temp[2] = True
            else:
                temp[2] = False
        elif(symb1[1] == "nil" and symb2[1] == "nil"):
            temp[2] = True
        elif((symb1[1] == "nil" and symb2[1] != "nil") or (symb1[1] != "nil" and symb2[1] == "nil")):
            temp[2] = False
        temp[1] = "bool"
        i = i + 1

    elif(instructions[i-1] == "AND"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(not typecmp(symb1, symb2) or symb1[1] != "bool"):
            exit(53)
        temp[1] = "bool"
        temp[2] = symb1[2] and symb2[2]
        i = i + 1

    elif(instructions[i-1] == "OR"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(not typecmp(symb1, symb2) or symb1[1] != "bool"):
            exit(53)
        temp[1] = "bool"
        temp[2] = symb1[2] or symb2[2]
        i = i + 1

    elif(instructions[i-1] == "NOT"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb = matchfind_nil(sorted_args[i][1])
        else:
            symb = matchfind(sorted_args[i][1])
        if(symb[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var"):
            exit(32)
        if(temp == [None, None, None, None] or symb == [None, None, None, None]):
            exit(54)
        if(symb[0] is not None and symb[2] is None):
            exit(56)
        if(symb[1] != "bool"):
            exit(53)
        temp[1] = "bool"
        temp[2] = not symb[2]
        i = i + 1

    elif(instructions[i-1] == "INT2CHAR"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb = matchfind_nil(sorted_args[i][1])
        else:
            symb = matchfind(sorted_args[i][1])
        if(symb[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var"):
            exit(32)
        if(temp == [None, None, None, None] or symb == [None, None, None, None]):
            exit(54)
        if(symb[0] is not None and symb[2] is None):
            exit(56)
        if(symb[1] != "int"):
            exit(53)
        temp[1] = "string"
        try:
            temp[2] = chr(symb[2])
        except:
            exit(58)
        i = i + 1

    elif(instructions[i-1] == "STRI2INT"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(symb1[1] != "string" and symb1[1] is not None):
            exit(53)
        if(symb2[1] != "int"):
            exit(53)
        if(symb1[2] is None):
            exit(58)
        if((symb2[2] >= len(symb1[2])) or symb2[2] < 0):
            exit(58)
        temp[1] = "int"
        temp[2] = ord(symb1[2][symb2[2]])
        i = i + 1
        
    elif(instructions[i-1] == "READ"):
        var = matchfind(sorted_args[i][0])
        if(var == [None, None, None, None]):
            exit(54)
        try:
            temp = input()
        except:
            var[1] = "nil"
            var[2] = "nil"
            i = i + 1
            continue
        if(sorted_args[i][1] == "string"):
            var[1] = "string"
            var[2] = temp
            i = i + 1
            continue
        elif(sorted_args[i][1] == "int"):
            var[1] = "int"
            try:
                var[2] = int(temp)
            except:
                var[1] = "nil"
                var[2] = "nil"
        elif(sorted_args[i][1] == "bool"):
            var[1] = "bool"
            if(temp.lower() == "true"):
                var[2] = True
            else:
                var[2] = False
        i = i + 1

    elif(instructions[i-1] == "WRITE"):
        if(ar_tp[i-1][0] == "string"):
            symb = matchfind_string(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "int"):
            symb = matchfind_int(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "bool"):
            symb = matchfind_bool(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "nil"):
            symb = matchfind_nil(sorted_args[i][0])
        else:
            symb = matchfind(sorted_args[i][0])
        if(symb[1] != ar_tp[i-1][0] and ar_tp[i-1][0] != "var"):
            exit(32)
        if(symb == [None, None, None, None]):
            exit(54)
        if(symb[0] is not None and symb[2] is None):
            exit(56)
        if(symb[1] == "nil"):
            print("",end='')
        elif(symb[1] == "bool"):
            if(symb[2]):
                print("true",end='')
            else:
                print("false",end='')
        else:
            print(symb[2],end='')
        i = i + 1

    elif(instructions[i-1] == "CONCAT"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(symb1[1] != "string" or symb2[1] != "string"):
            exit(53)
        temp[1] = "string"
        if(symb1[2] is None and symb2[2] is not None):
            temp[2] = symb2[2]
        elif(symb2[2] is None and symb1[2] is not None):
            temp[2] = symb1[2]
        elif(symb1[2] is None and symb2[2] is None):
            temp[2] = None
        else:
            temp[2] = symb1[2] + symb2[2]
        i = i + 1
        
    elif(instructions[i-1] == "STRLEN"):
        var = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb = matchfind_nil(sorted_args[i][1])
        else:
            symb = matchfind(sorted_args[i][1])
        if(symb[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var"):
            exit(32)
        if(var == [None, None, None, None] or symb == [None, None, None, None]):
            exit(54)
        if(symb[0] is not None and symb[2] is None):
            exit(56)
        if(symb[1] != "string"):
            exit(53)
        if(symb[2] is None):
            var[2] = 0
        else:
            var[2] = len(symb[2])
        var[1] = "int"
        i = i + 1

    elif(instructions[i-1] == "GETCHAR"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None):
            exit(56)
        if(symb1[1] != "string"):
            exit(53)
        if(symb2[1] != "int"):
            exit(53)
        if(symb1[2] is None):
            exit(58)
        if(symb2[2] >= len(symb1[2])):
            exit(58)
        if(symb2[2] < 0):
            exit(58)
        temp[1] = "string"
        temp[2] = symb1[2][symb2[2]]
        i = i + 1    
        
    elif(instructions[i-1] == "SETCHAR"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(temp == [None, None, None, None] or symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[0] is not None and symb1[2] is None or symb2[0] is not None and symb2[2] is None or temp[2] is None):
            exit(56)
        if(symb1[1] != "int"):
            exit(53)
        if(symb2[1] != "string"):
            exit(53)
        if(symb2[2] is None or symb2[2] == ""):
            exit(58)
        if(temp[1] == "string"):
            if(len(temp[2]) <= symb1[2] or symb1[2] < 0):
                exit(58)
            strtolist = list(temp[2])
            strtolist[symb1[2]] = symb2[2][0]
            temp[2] = "".join(strtolist)
            i = i + 1
        else:
            exit(53)
        
    elif(instructions[i-1] == "TYPE"):
        temp = matchfind(sorted_args[i][0])
        if(ar_tp[i-1][1] == "string"):
            symb = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb = matchfind_nil(sorted_args[i][1])
        else:
            symb = matchfind(sorted_args[i][1])
        if(symb[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var"):
            exit(32)
        if(temp == [None, None, None, None] or symb == [None, None, None, None]):
            exit(54)
        if(symb[0] is not None and symb[1] is None):
            temp[2] = ""
            temp[1] = "string"
        elif(symb[0] is not None and symb[1] is not None):
            temp[2] = symb[1]
        elif(symb[1] == "string"):
            temp[2] = "string"
        elif(symb[1] == "int"):
            temp[2] = "int"
        elif(symb[1] == "bool"):
            temp[2] = "bool"
        elif(symb[1] == "nil"):
            temp[2] = "nil"
        temp[1] = "string"
        i = i + 1

    elif(instructions[i-1] == "LABEL"):
        i = i + 1

    elif(instructions[i-1] == "JUMP"):
        found = False
        for lab in labels:
            if lab[1] == sorted_args[i][0]:
                i = lab[0] + 2
                found = True
                break
        if(not found):
            exit(52)

    elif(instructions[i-1] == "JUMPIFEQ"):
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        found = False
        for lab in labels:
            if lab[1] == sorted_args[i][0]:
                found = True
        if(found == False):
            exit(52)
        if(symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[2] is None or symb2[2] is None):
            exit(56)
        if((symb1[1] != symb2[1]) and (symb1[1] != "nil" and symb2[1] != "nil")):
            exit(53)
        if((symb1[1] != ar_tp[i-1][1] and ar_tp[i-1][1] != "var") or (symb2[1] != ar_tp[i-1][2] and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[1] == "nil" and symb2[1] != "nil"):
            i = i + 1
            continue
        elif(symb2[1] == "nil" and symb1[1] != "nil"):
            i = i + 1
            continue
        elif(symb1[2] == symb2[2]):
            found = False
            for lab in labels:
                if lab[1] == sorted_args[i][0]:
                    i = lab[0] + 1
                    found = True
                    break
            if(not found):
                exit(52)
        i = i + 1

    elif(instructions[i-1] == "JUMPIFNEQ"):
        if(ar_tp[i-1][1] == "string"):
            symb1 = matchfind_string(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "int"):
            symb1 = matchfind_int(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "bool"):
            symb1 = matchfind_bool(sorted_args[i][1])
        elif(ar_tp[i-1][1] == "nil"):
            symb1 = matchfind_nil(sorted_args[i][1])
        else:
            symb1 = matchfind(sorted_args[i][1])
        if(ar_tp[i-1][2] == "string"):
            symb2 = matchfind_string(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "int"):
            symb2 = matchfind_int(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "bool"):
            symb2 = matchfind_bool(sorted_args[i][2])
        elif(ar_tp[i-1][2] == "nil"):
            symb2 = matchfind_nil(sorted_args[i][2])
        else:
            symb2 = matchfind(sorted_args[i][2])
        found = False
        for lab in labels:
            if lab[1] == sorted_args[i][0]:
                found = True
        if(found == False):
            exit(52)
        if(symb1 == [None, None, None, None] or symb2 == [None, None, None, None]):
            exit(54)
        if(symb1[2] is None or symb2[2] is None):
            exit(56)
        if((symb1[1] != symb2[1]) and (symb1[1] != "nil" and symb2[1] != "nil")):
            exit(53)
        if(((symb1[1] != ar_tp[i-1][1]) and ar_tp[i-1][1] != "var") or ((symb2[1] != ar_tp[i-1][2]) and ar_tp[i-1][2] != "var")):
            exit(32)
        if(symb1[1] == "nil" and symb2[1] == "nil"):
            i = i + 1
            continue
        elif(symb1[2] != symb2[2]):
            found = False
            for lab in labels:
                if lab[1] == sorted_args[i][0]:
                    i = lab[0] + 1
                    found = True
                    break
            if(not found):
                exit(52)
        i = i + 1

    elif(instructions[i-1] == "EXIT"):
        if(ar_tp[i-1][0] == "string"):
            symb = matchfind_string(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "int"):
            symb = matchfind_int(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "bool"):
            symb = matchfind_bool(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "nil"):
            symb = matchfind_nil(sorted_args[i][0])
        else:
            symb = matchfind(sorted_args[i][0])
        if(symb[1] != ar_tp[i-1][0] and ar_tp[i-1][0] != "var"):
            exit(32)
        if(symb == [None, None, None, None]):
            exit(54)
        if(symb[0] is not None and symb[2] is None):
            exit(56)
        if(symb[1] != "int"):
            exit(53)
        if(symb[2] > 49 or symb[2] < 0):
            exit(57)
        else:
            exit(symb[2])
            
    elif(instructions[i-1] == "DPRINT"):
        if(ar_tp[i-1][0] == "string"):
            symb = matchfind_string(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "int"):
            symb = matchfind_int(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "bool"):
            symb = matchfind_bool(sorted_args[i][0])
        elif(ar_tp[i-1][0] == "nil"):
            symb = matchfind_nil(sorted_args[i][0])
        else:
            symb = matchfind(sorted_args[i][0])
        if(symb[1] != ar_tp[i-1][0] and ar_tp[i-1][0] != "var"):
            exit(32)
        if(symb == [None, None, None, None]):
            exit(54)
        if(symb[1] == "nil"):
            sys.stderr.write("")
        elif(symb[1] == "bool"):
            if(symb[2]):
                sys.stderr.write("true")
            else:
                sys.stderr.write("false")
        else:
            sys.stderr.write(symb[2])
        i = i + 1

    elif(instruction[i-1] == "BREAK"):
        i = i + 1

    else:
        exit(32)

exit(0)