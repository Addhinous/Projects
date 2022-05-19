<?php
#Parametrom funkcie je priecinok a pole do ktoreho budu ulozene nazvi suborov s celou cestou (rekurzivna varianta)
function get_sort_files_rec($directory, &$out = array())
{
    $files = scandir($directory);
    sort($files);
    foreach ($files as $key => $val)
    {
        $path = realpath($directory . DIRECTORY_SEPARATOR . $val);
        if(!is_dir($path))
        {
            $out[] = $path;
        }
        else if (($val != ".") && ($val != ".."))
        {
            get_sort_files_rec($path, $out);
        }
    }
    return $out;
}

#Parametrom funkcie je priecinok a pole do ktoreho budu ulozene nazvi suborov s celou cestou
function get_sort_files($directory, &$out = array())
{
    $files = scandir($directory);
    sort($files);
    foreach ($files as $key => $val)
    {
        $path = realpath($directory . DIRECTORY_SEPARATOR . $val);
        if(!is_dir($path))
        {
            $out[] = $path;
        }
        continue;
    }
    return $out;
}

$directory = getcwd();
$recursive = false;
$parse_only = false;
$int_only = false;
$curr_dir = true;
$parse = "parse.php";
$interpret = "interpret.py";
$xml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
$cfg = "/pub/courses/ipp/jexamxml/options";
$ionly = true;
$ponly = true;
for($i = 1; $i<$argc; $i++)
{
    $match = true;
    switch($argv[$i])
    {
        case "--help":
            if(($argc != 2) || (strcmp($argv[1], "--help")))
            {
                exit(10);
            }
            echo "Help\n";
            exit(0);
            break;
        case "--recursive":
            if($recursive)
            {
                exit(10);
            }
            $recursive = true;
            break;
        case "--parse-only":
            if($parse_only || !$ionly)
            {
                exit(10);
            }
            $parse_only = true;
            break;
        case "--int-only":
            if($int_only || !$ponly)
            {
                exit(10);
            }
            $int_only = true;
            break;
        default:
            $match = false;
            break;
    }
    if($match)
        continue;
    $boom = explode("=", $argv[$i], 2);
    switch($boom[0])
    {
        case "--directory":
            if(!$curr_dir)
            {
                exit(10);
            }
            if(!is_dir($boom[1]))
            {
                exit(41);
            }
            $curr_dir = false;
            $directory = $boom[1];
            break;
        case "--parse-script":
            if(!file_exists($boom[1]))
            {
                exit(41);
            }
            if(strcmp($parse, "parse.php"))
            {
                exit(41);
            }
            $parse = $boom[1];
            $ionly = false;
            break;
        case "--int-script":
            if(!file_exists($boom[1]))
            {
                exit(41);
            }
            if(strcmp($interpret, "interpret.py"))
            {
                exit(10);
            }
            $interpret = $boom[1];
            $ponly = false;
            break;
        case "--jexamxml":
            if(!file_exists($boom[1]))
            {
                exit(41);
            }
            if(strcmp($xml, "/pub/courses/ipp/jexamxml/jexamxml.jar"))
            {
                exit(10);
            }
            $xml = $boom[1];
            break;
        case "--jexamcfg":
            if(!file_exists($boom[1]))
            {
                exit(41);
            }
            if(strcmp($cfg, "/pub/courses/ipp/jexamxml/options"))
            {
                exit(10);
            }
            $cfg = $boom[1];
            break;
        default:
            exit(41);
    }
}

$files = array();
$outputs = array();
$act_outputs = array();
$inputs = array();
$rcs = array();
$act_rcs = array();
$test_names = array();
$results = array();

if($recursive)
{
    $files = get_sort_files_rec($directory, $files);
}
else
{
    $files = get_sort_files($directory, $files);
}

$passed = 0;
$failed = 0;


$i = 0;
foreach($files as $key => $val)
{
    $ext = substr($val, -3, 3);
    $name = substr($val, 0, -4);
    if(!strcmp($ext, "src"))
    {
        $test_names[] = $val;
        if(!is_file($name.".rc"))
        {
            try
            {
                $rcfile = fopen($name.".rc", "w+");
                fwrite($rcfile, "0");
            }
            catch(Exception $e)
            {
                exit(41);
            }
            $rcs[] = 0;
            $ex_rc = 0;
        }
        else
        {
            try
            {
                $rcfile = fopen($name.".rc", "r");
                $rcs[] = intval(fread($rcfile, filesize($name.".rc")), 10);
                $ex_rc = intval(fread($rcfile, filesize($name.".rc")), 10);
            }
            catch(Exception $e)
            {
                exit(41);
            }
        }
        if(!is_file($name.".in"))
        {
            try
            {
                $infile = fopen($name.".in", "w+");
            }
            catch(Exception $e)
            {
                exit(41);
            }
        }
        else
        {
            try
            {
                $infile = fopen($name.".in", "r");
            }
            catch(Exception $e)
            {
                exit(41);
            }
        }
        $input = $name.".in";
        if(!is_file($name.".out"))
        {
            try
            {
                $outfile = fopen($name.".out", "w+");
                $outputs[] = "";
            }
            catch(Exception $e)
            {
                exit(41);
            }
        }
        else
        {
            try
            {
                $outfile = fopen($name.".out", "r");
                if(filesize($name.".out"))
                {
                    $outputs[] = fread($outfile, filesize($name.".out"));
                }
                else
                {
                    $outputs[] = "";
                }
            }
            catch(Exception $e)
            {
                exit(41);
            }
        }
        $src = $val;

        if($parse_only)
        {
            exec("php7.4 ".$parse." <".$src." >output", $arr, $rc);
            $act_rcs[] = $rc;
            $tmp_out = fopen("output", "r");
            if(filesize("output"))
            {
                $act_outputs[] = fread($tmp_out,filesize("output"));
            }
            else
            {
                $act_outputs[] = "";
            }
            if($rc)
            {
                if(!strcmp($rcs[count($rcs)-1], $rc))
                {
                    $passed++;
                    $results[] = True;
                }
                else
                {
                    $failed++;
                    $results[] = False;
                }
            }
            else
            {
                exec("java -jar jexamxml.jar ".$name.".out output delta.xml options", $out_arr);
                if(!strcmp("JExamXML 1.01 - Java XML comparison tool", $out_arr[0]) && !strcmp("Comparing \"".$name.".out\" and \"output\"", $out_arr[1]) && !strcmp("Two files are identical", $out_arr[2]))
                {
                    $passed++;
                    $results[] = True;
                    unset($out_arr);
                }
                else
                {
                    $failed++;
                    $results[] = False;
                    unset($out_arr);
                }
            }
        }
        else if($int_only)
        {
            exec("python3 ".$interpret." --input=".$input." <".$src." >output", $arr, $rc);
            $act_rcs[] = $rc;
            $tmp_out = fopen("output", "r");
            if(filesize("output"))
            {
                $act_outputs[] = fread($tmp_out,filesize("output"));
            }
            else
            {
                $act_outputs[] = "";
            }
            if($rc)
            {
                if($rcs[count($rcs)-1] == $rc)
                {
                    $passed++;
                    $results[] = True;
                }
                else
                {
                    $failed++;
                    $results[] = False;
                }
            }
            else
            {
                exec("diff ".$name.".out output", $arr, $diff);
                if($diff)
                {
                    $failed++;
                    $results[] = False;
                }
                else
                {
                    $passed++;
                    $results[] = True;
                }
            }
        }
        else
        {
            exec("php7.4 ".$parse." <".$src." >output", $arr, $rc);
            if($rc)
            {
                $act_rcs[] = $rc;
                if($ex_rc == $rc)
                {
                    $passed++;
                    $results[] = True;
                }
                else
                {
                    $failed++;
                    $results[] = False;
                }
            }
            else
            {
                exec("python3 ".$interpret." --input=".$input." <output >output2", $arr, $rc);
                $tmp_out = fopen("output2", "r");
                if(filesize("output2"))
                {
                    $act_outputs[] = fread($tmp_out,filesize("output2"));
                }
                else
                {
                    $act_outputs[] = "";
                }
                $act_rcs[] = $rc;
                if($rc)
                {
                    if($rcs[count($rcs)-1] == $rc)
                    {
                        $passed++;
                        $results[] = True;
                    }
                    else
                    {
                        $failed++;
                        $results[] = False;
                    }
                }
                else
                {
                    exec("diff ".$name.".out output2", $arr, $diff);
                    if($diff)
                    {
                        $failed++;
                        $results[] = False;
                    }
                    else
                    {
                        $passed++;
                        $results[] = True;
                    }
                }
            }
        }
    }
}
$html = "<!DOCTYPE html>\n<html lang=\"sk\">\n<head>\n<meta charset=\"UTF-8\">\n<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\n<title>Výsledky testovacieho skriptu test.php</title><meta charset=utf-8>\n</head><body><h2 style=\"color:green\">Počet prechádzajúcich testov: ".$passed."</h2><br><h2 style=\"color:red\">Počet neprechádzajúcich testov: ".$failed."</h2><br>";

for($i = 0; $i<count($rcs); $i++)
{
    $html = $html."<section>";
    if($results[$i])
    {
        $html = $html."<h3 style=\"color:green\">".$test_names[$i]." PASSED</h3><p>Očakávaný návratový kód: ".$rcs[$i]."</p><p>Výsledný návratový kód: ".$act_rcs[$i]."</p><p>Očakávaný výstup:</p><br><p>".$outputs[$i]."</p><br><p>Výsledný výstup:</p><br><p>".$act_outputs[$i]."</p>";
    }
    else
    {
        $html = $html."<h3 style=\"color:red\">".$test_names[$i]." FAILED</h3><p>Očakávaný návratový kód: ".$rcs[$i]."</p><p>Výsledný návratový kód: ".$act_rcs[$i]."</p><p>Očakávaný výstup:</p><br><p>".$outputs[$i]."</p><br><p>Výsledný výstup:</p><br><p>".$act_outputs[$i]."</p>";
    }
    $html = $html."</section><br>";
}

$html = $html."</body></html>";
print($html);

?>