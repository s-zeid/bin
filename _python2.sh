#!/bin/sh

re='^.*python2\?$'
color=$( (grep --help 2>&1 | grep -q -e --color) && echo "--color" || echo "")

grep $color "$re" "$(dirname -- "$0")"/* 2>/dev/null
echo
grep "$re" "$(dirname -- "$0")"/* 2>/dev/null | wc -l
