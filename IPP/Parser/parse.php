<?php
ini_set('display_errors', 'stderr');
#pocitadla a polia pre rozsirenie STATP
$labelArray;
$labelFind;
$labelCount = 0;
$jumpCount = 0;
$fwjumpCount = 0;
$backjumpCount = 0;
$commentCount = 0;
$badjumpCount = 0;
$unknownlabels = 0;

#funkcia rozdeli retazec na pole retazcov podla bielych znakov
function splitstr($str)
{
    $arr = [];
    $c = $str[0];
    $i = 0;
    $count = 0;
    $index = 0;
    $comment = false;
    $arr[0] = "";
    global $commentCount;
    while($c != "\n")
    {  
        while($c == ' ' || $c == "\t")
        {
            $count++;
            $c = $str[$count];
        }
        if($c == '#')
        {
            $commentCount++;
            break;
        }
        $i = 0;
        $tmp = "";
        while($c != ' ' && $c != "\t" && $c != "\n")
        {
            if($c == '#')
            {
                $commentCount++;
                $comment = true;
                break;
            }
            $tmp[$i] = $c;
            $count++;
            $c = $str[$count];
            $i++;
        }
        if($comment)
        {
            while(($c = $str[$count]) != "\n")
            {
                $count++;
            }
            $arr[$index] = $tmp;
            break;
        }
        $arr[$index] = $tmp;
        $index++;
    }
    return $arr;
}

#funkcia na preskocenie znaku '@' v retazci
function skipat($str)
{
    $i = 0;
    $c = $str[$i];
    while($c != '@')
    {
        $c = $str[$i];
        $i++;
    }
    $counter = 0;
    $name = "";
    for(;$i<strlen($str); $i++)
    {
        $name[$counter] = $str[$i];
        $counter++;
    }
    return $name;
}

$statistics = array();
$files;
$m = 0;
$statistics[$m] = array();
if (($argc >= 2) && !strcmp(($filearr = explode("=", $argv[1]))[0], '--stats'))
{
    if(!($file[0] = fopen($filearr[1], "w+")))
    {
        exit(11);
    }
    $files[0] = $filearr[1];
    $s = 0;
    for($k = 2; $k < $argc; $k++)
    {
        switch($argv[$k])
        {
            case "--loc":
                $statistics[$m][$s] = "instructions";
                break;
            case "--comments":
                $statistics[$m][$s] = "comments";
                break;
            case "--labels":
                $statistics[$m][$s] = "labels";
                break;
            case "--jumps":
                $statistics[$m][$s] = "jumps";
                break;
            case "--fwjumps":
                $statistics[$m][$s] = "fwjumps";
                break;
            case "--backjumps":
                $statistics[$m][$s] = "backjumps";
                break;
            case "--badjumps":
                $statistics[$m][$s] = "badjumps";
                break;
            default:
                if(strpos($argv[$k], "--stats=") === 0) #ak najdeme dalsi parameter --stats=file otvarame novy subor
                {
                    $s = -1;
                    $m++;
                    $files[$m] = explode("=", $argv[$k])[1];
                    $statistics[$m] = array();
                    for($p = 0; $p<$m; $p++)
                    {
                        if(!strcmp($files[$m], $files[$p]))
                        {
                            echo "12";
                            exit(12);
                        }
                    }
                    if(!($file[$m] = fopen($files[$m], "w+")))
                    {
                        exit(11);
                    }
                    break;
                }
                else
                {
                    exit(10);
                }
        }
        $s++;
    }
}
else if(($argc == 2) && (!strcmp($argv[1], '--help'))) #--help
{
    echo "Skript typu filter (parse.php v jazyku PHP 7.4) načíta zo štandardného vstupu zdrojový kód v IPPcode21, skontroluje lexikálnu a syntaktickú správnosť kódu a vypíše na štandardný výstup XML reprezentáciu programu.\nSkript pracuje s nasledujúcimi parametrami:\n\n --help  výpis nápovedy ku programu.\n --stats='file'  výpis štatistík zdrojového kódu IPPcode21 do súboru 'file'.\n\nPre výpis jednotlivých štatistík je nutné uviesť za tento parameter niektoré z nasledujúcich parametrov:\n\n  --loc  výpis počtu inštrukcií\n  --comments výpis počtu komentárov\n  --jumps  výpis počtu inštrukcií skokov\n  --fwjumps  výpis počtu inštrukcií skoku dopredu\n  --backjumps výpis počtu inštrukcií skoku dozadu\n  --badjumps výpis počtu inštrukcií skoku na neplatné náveštie\n";
    exit();
}
else if($argc != 1)
{
    exit(10);
}

#kontrola hlavicky .IPPcode21
$header = "";
while($line = fgets(STDIN))
{
    $line = $line."\n";
    $i=0;
    while(($line[$i] == ' ') || (($line[$i]) == "\t"))
    {
        $i++;
    }
    if($line[$i] == '#')
    {
        $commentCount++;
        while($line[$i] != "\n")
        {
            $i++;
        }
        continue;
    }
    else if ($line[$i] == "\n")
    {
        continue;
    }
    for($j=0; $j<10; $j++)
    {
        if($j >= strlen($line))
        {
            exit(21);
        }
        $header[$j] = $line[$i];
        $i++;
    }
    if(strcmp(strtolower($header), ".ippcode21"))
    {
        exit(21);
    }
    while($line[$i] != "\n")
    {
        if($line[$i] == "#")
        {
            $commentCount++;
            break;
        }
        else if(($line[$i] == ' ') || ($line[$i] == "\t"))
            $i++;
        else if($line[$i] != "\n")
        {
            exit(21);
        }
    }
    break;
}

if(strlen($header) != 10)
{
    exit(21);
}

#Zaciatok generovania vystupneho xml
$xw = xmlwriter_open_memory();
xmlwriter_set_indent($xw, 1);
$res = xmlwriter_set_indent_string($xw, ' ');
xmlwriter_start_document($xw, '1.0', 'UTF-8');
xmlwriter_start_element($xw, 'program');
xmlwriter_start_attribute($xw, 'language');
xmlwriter_text($xw, 'IPPcode21');
xmlwriter_end_attribute($xw);

#regularne vyrazy
$var = "/^[LGT]F{1}@{1}[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/";
$label = "/^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/";
$symb = "/^([LGT]F{1}@{1}[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$)|(^(\bstring\b@{1}(([^#\\\\\s])|([\\\\][0-9]{3}))*$)|^(\bint\b@[+-]?[0-9]+$)|^(\bbool\b@{1}(\bfalse\b|\btrue\b)$)|^(\bnil\b@{1}\bnil\b)$)/";
$type = "/^(\bint\b)$|^(\bstring\b)$|^(\bbool\b)$|^(\bnil\b)$/";
$counter = 0;
#nacitanie kodu
while($line = fgets(STDIN))
{
    $line = $line."\n";
    $arr = splitstr($line);

    if(strlen($arr[0]) == 0)
    {
        $arr[0] = "\n";
    }

    if(strlen($arr[0]) > 12)
    {
        exit(22);
    }
    $counter++;
    if($arr[0] != "\n")
    {
        xmlwriter_start_element($xw, 'instruction');
        xmlwriter_start_attribute($xw, 'order');
        xmlwriter_text($xw, $counter);
        xmlwriter_end_attribute($xw);
        xmlwriter_start_attribute($xw, 'opcode');
        xmlwriter_text($xw, strtoupper($arr[0]));
        xmlwriter_end_attribute($xw);

        for($i = 1; $i<count($arr); $i++)
        {  
            xmlwriter_start_element($xw, 'arg'.$i);
            xmlwriter_start_attribute($xw, 'type');
            if(preg_match($var, $arr[$i]))
            {
                xmlwriter_text($xw, 'var');
                xmlwriter_end_attribute($xw);
                xmlwriter_text($xw, $arr[$i]);
            }
            else if(preg_match($type, $arr[$i]))
            {
                xmlwriter_text($xw, 'type');
                xmlwriter_end_attribute($xw);
                xmlwriter_text($xw, $arr[$i]);
            }
            else if (preg_match($symb, $arr[$i]))
            {
                $literal  = skipat($arr[$i]);
                switch($arr[$i][0])
                {
                    case 'b':
                        xmlwriter_text($xw, 'bool');
                        xmlwriter_end_attribute($xw);
                        xmlwriter_text($xw, $literal);
                        break;
                    case 'i':
                        xmlwriter_text($xw, 'int');
                        xmlwriter_end_attribute($xw);
                        xmlwriter_text($xw, $literal);
                        break;
                    case 's':
                        xmlwriter_text($xw, 'string');
                        xmlwriter_end_attribute($xw);
                        xmlwriter_text($xw, $literal);
                        break;
                    case 'n':
                        xmlwriter_text($xw, 'nil');
                        xmlwriter_end_attribute($xw);
                        xmlwriter_text($xw, $literal);
                        break;
                    default:
                        exit(23);
                }
            }
            else if (preg_match($label, $arr[$i]))
            {
                xmlwriter_text($xw, 'label');
                xmlwriter_end_attribute($xw);
                xmlwriter_text($xw, $arr[$i]);
            }
            xmlwriter_end_element($xw);
        }
        xmlwriter_end_element($xw);
    }
    switch (strtolower($arr[0]))
    {
        case "move":
            if(count($arr) != 3)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2])))
            {
                exit(23);
            }
            break;
        case "createframe":
            if(count($arr) != 1)
            {
                exit(23);
            }
            break;
        case "pushframe":
            if(count($arr) != 1)
            {
                exit(23);
            }
            break;
        case "popframe":
            if(count($arr) != 1)
            {
                exit(23);
            }
            break;
        case "defvar":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($var, $arr[1]))
            {
                exit(23);
            }
            break;
        case "call":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($label, $arr[1]))
            {
                exit(23);
            }
            $jumpCount++;
            $foundLabel = false;
            for($l = 0; $l<$labelCount; $l++)
            {
                if(!strcmp($arr[1], $labelArray[$l]))
                {
                    $backjumpCount++;
                    $foundLabel = true;
                }
            }
            if(!$foundLabel)
            {
                $labelFind[$unknownlabels] = $arr[1];
                $unknownlabels++;
                $badjumpCount++;
            }
            break;
        case "return":
            if(count($arr) != 1)
            {
                exit(23);
            }
            $jumpCount++;
            break;
        case "pushs":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($symb, $arr[1]))
            {
                exit(23);
            }
            break;
        case "pops":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($var, $arr[1]))
            {
                exit(23);
            }
            break;
        case "add":
            if(count($arr) != 4)
            {
                echo "count\n";
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                echo "regex\n";
                exit(23);
            }
            break;
        case "sub":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "mul":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "idiv":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "lt":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "gt":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "eq":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "and":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "or":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "not":
            if(count($arr) != 3)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2])))
            {
                exit(23);
            }
            break;
        case "int2char":
            if(count($arr) != 3)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2])))
            {
                exit(23);
            }
            break;
        case "stri2int":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "read":
            if(count($arr) != 3)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($type, $arr[2])))
            {
                exit(23);
            }
            break;
        case "write":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($symb, $arr[1]))
            {
                exit(23);
            }
            break;
        case "concat":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "strlen":
            if(count($arr) != 3)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2])))
            {
                exit(23);
            }
            break;
        case "getchar":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "setchar":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            break;
        case "type":
            if(count($arr) != 3)
            {
                exit(23);
            }
            if(!(preg_match($var, $arr[1]) && preg_match($symb, $arr[2])))
            {
                exit(23);
            }
            break;
        case "label":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($label, $arr[1]))
            {
                exit(23);
            }
            $labelArray[$labelCount] = $arr[1];
            $labelCount++;
            for($t = 0; $t<$unknownlabels; $t++)
            {
                if(!strcmp($arr[1], $labelFind[$t]))
                {
                    $badjumpCount--;
                    $fwjumpCount++;
                }
            }
            break;
        case "jump":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($label, $arr[1]))
            {
                exit(23);
            }
            $jumpCount++;
            $foundLabel = false;
            for($l = 0; $l<$labelCount; $l++)
            {
                if(!strcmp($arr[1], $labelArray[$l]))
                {
                    $backjumpCount++;
                    $foundLabel = true;
                    break;
                }
            }
            if(!$foundLabel)
            {
                $labelFind[$unknownlabels] = $arr[1];
                $unknownlabels++;
                $badjumpCount++;
            }
            break;
        case "jumpifeq":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($label, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            $jumpCount++;
            $foundLabel = false;
            for($l = 0; $l<$labelCount; $l++)
            {
                if(!strcmp($arr[1], $labelArray[$l]))
                {
                    $backjumpCount++;
                    $foundLabel = true;
                    break;
                }
            }
            if(!$foundLabel)
            {
                $labelFind[$unknownlabels] = $arr[1];
                $unknownlabels++;
                $badjumpCount++;
            }
            break;
        case "jumpifneq":
            if(count($arr) != 4)
            {
                exit(23);
            }
            if(!(preg_match($label, $arr[1]) && preg_match($symb, $arr[2]) && preg_match($symb, $arr[3])))
            {
                exit(23);
            }
            $jumpCount++;
            $foundLabel = false;
            for($l = 0; $l<$labelCount; $l++)
            {
                if(!strcmp($arr[1], $labelArray[$l]))
                {
                    $backjumpCount++;
                    $foundLabel = true;
                    break;
                }
            }
            if(!$foundLabel)
            {
                $labelFind[$unknownlabels] = $arr[1];
                $unknownlabels++;
                $badjumpCount++;
            }
            break;
        case "exit":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($symb, $arr[1]))
            {
                exit(23);
            }
            break;
        case "dprint":
            if(count($arr) != 2)
            {
                exit(23);
            }
            if(!preg_match($symb, $arr[1]))
            {
                exit(23);
            }
            break;
        case "break":
            if(count($arr) != 1)
            {
                exit(23);
            }
            break;
        case "\n":
            $counter--;
            break;
        default:
            $counter--;
            exit(22);
    }
}
xmlwriter_end_element($xw);
xmlwriter_end_document($xw);
echo xmlwriter_output_memory($xw);

#Vypis udajov rozsirenia STATP do suborov
for($i = 0; $i<=$m; $i++)
{
    for($j = 0; $j<count($statistics[$i]); $j++) #count($statistics[$i])
    {       
        switch($statistics[$i][$j])
        {
            case "instructions":
                fwrite($file[$i], $counter."\n");
                break;
            case "comments":
                fwrite($file[$i], $commentCount."\n");
                break;
            case "labels":
                fwrite($file[$i], $labelCount."\n");
                break;
            case "jumps":
                fwrite($file[$i], $jumpCount."\n");
                break;
            case "fwjumps":
                fwrite($file[$i], $fwjumpCount."\n");
                break;
            case "backjumps":
                fwrite($file[$i], $backjumpCount."\n");
                break;
            case "badjumps":
                fwrite($file[$i], $badjumpCount."\n");
                break;
            default:
                exit(23);
        }
    }
}
?>