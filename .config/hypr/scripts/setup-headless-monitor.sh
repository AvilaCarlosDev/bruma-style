#!/usr/bin/env bash
# Crea el monitor virtual HEADLESS-1 (tablet como segundo monitor via wayvnc)
# y lo asigna al workspace 10.
hyprctl output create headless
sleep 0.5
hyprctl eval 'hl.monitor({ output = "HEADLESS-1", mode = "1280x800@60", position = "1920x0", scale = 1 })'
hyprctl eval 'hl.workspace_rule({ workspace = "10", monitor = "HEADLESS-1", default = true })'
