#!/usr/bin/env bash
# help.sh
# DESCRIPTION: List every *.sh script in this directory with its one‑line blurb

list_scripts() {
  for f in "$(dirname "$0")"/*.sh; do
    desc=$(grep -m1 '^# DESCRIPTION:' "$f" | sed 's/^# DESCRIPTION: //')
    printf "%-22s  %s\n" "$(basename "$f")" "${desc:-<no description>}"
  done
}

case "$1" in
  ""|-h|--help)  list_scripts ;;
  *)             grep -A99 -m1 '^# DESCRIPTION:' "scripts/$1" \
                    | sed 's/^# *//';;
esac
