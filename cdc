#!/bin/sh
set -e

if [ $# -lt 2 ] || [ x"$1" = x"" ]; then
 echo "Usage: $(basename -- "$0") <directory> <command> [<argument> [...]]" >&2
 exit 2
fi

dir=$1; shift
if ! [ -e "$dir" ]; then
 printf '%s\n' "$(basename -- "$0"): cannot cd to '$dir': No such file or directory" >&2
 exit 1
elif ! [ -d "$dir" ]; then
 printf '%s\n' "$(basename -- "$0"): cannot cd to '$dir': Not a directory" >&2
 exit 1
elif ! [ -x "$dir" ]; then
 printf '%s\n' "$(basename -- "$0"): cannot cd to '$dir': Permission denied" >&2
 exit 1
fi

cd "$dir"
exec "$@"
