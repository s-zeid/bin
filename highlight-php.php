<?php

// Modified from <http://www.php.net/manual/en/function.highlight-file.php#93268>

// According to <http://php.net/manual/add-note.php>, this is released under the
// same license as the PHP Documentation, which is Creative Commons BY 3.0, which,
// while it is a free license, is unfortunately not compatible with the GPL and
// GFDL.

function highlight_string_ansi($str, $return = false) {
 $c_string  = ini_get("highlight.string"); // get ini values
 $c_comment = ini_get("highlight.comment");
 $c_keyword = ini_get("highlight.keyword");
 $c_default = ini_get("highlight.default");
 $c_html    = ini_get("highlight.html");

 $source = highlight_string($str, true); // load highlighted source

 $source = str_replace("</span>", "\x1b[0m", $source); // replace html tags
 $source = str_replace("<span style=\"color: $c_string\">", "\x1b[31m", $source);
 $source = str_replace("<span style=\"color: $c_comment\">", "\x1b[33m", $source);
 $source = str_replace("<span style=\"color: $c_keyword\">", "\x1b[32m", $source);
 $source = str_replace("<span style=\"color: $c_default\">", "\x1b[34m", $source);
 $source = str_replace("<span style=\"color: $c_html\">", "\x1b[30m", $source);

 $source = str_replace("\n", "", $source); // remove newlines
 $source = str_replace("<code>", "", $source); // strip <code> and <br>
 $source = str_replace("</code>", "", $source);
 $source = str_replace("<br />", "\n", $source);
 $source = str_replace("&nbsp;", " ", $source); // remove &nbsp and entities
 $source = html_entity_decode($source);

 if (!$return)
  echo $source;
 else
  return $source;
}

function highlight_file_ansi($file, $return = false) {
 return highlight_string_ansi(file_get_contents($file), $return);
}

function main($argv) {
 $file = $argv[(count($argv) > 1) ? 1 : 0];
 highlight_file_ansi($file);
 return 0;
}

if (realpath($argv[0]) === realpath(__FILE__))
 exit(main($argv));

?>
