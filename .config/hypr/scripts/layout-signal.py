#!/usr/bin/env python3
# Escucha el socket de eventos de Hyprland y refresca el módulo custom/language
# de waybar (señal RTMIN+9) cada vez que cambia el layout con SUPER+Space.
import os
import socket
import subprocess

sock_path = f"{os.environ['XDG_RUNTIME_DIR']}/hypr/{os.environ['HYPRLAND_INSTANCE_SIGNATURE']}/.socket2.sock"

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(sock_path)

buf = ""
while True:
    data = s.recv(4096).decode(errors="ignore")
    if not data:
        break
    buf += data
    while "\n" in buf:
        line, buf = buf.split("\n", 1)
        if line.startswith("activelayout>>"):
            subprocess.run(["pkill", "-RTMIN+9", "waybar"])
