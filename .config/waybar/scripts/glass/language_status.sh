#!/usr/bin/env bash
# Imprime el layout de teclado activo como US o ES para el módulo custom/language
layout=$(hyprctl devices -j | python3 -c "
import json, sys
d = json.load(sys.stdin)
for kb in d['keyboards']:
    if kb['name'] == 'at-translated-set-2-keyboard':
        print(kb['active_keymap'])
        break
")

case "$layout" in
    *Spanish*|*Español*|*Latin*) echo "ES" ;;
    *) echo "US" ;;
esac
