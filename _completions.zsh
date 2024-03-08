compdef mpa=mpv 2>/dev/null
compdef mpi=mpv 2>/dev/null
compdef mpv-realpath=mpv 2>/dev/null
compdef mvlc=vlc 2>/dev/null

compdef _cdc cdc
_cdc() {
  local cmd cpp; local -a _comp_priv_prefix
  cmd="$words[1]"; cpp='_comp_priv_prefix=( $cmd -n ${(kv)opt_args[(I)-u]} )'
  _arguments -s -S -A '-*' \
    '1: :_directories' \
    "2: :{$cpp;_command_names -e}" \
    "*: :{$cpp;_normal}"
}
