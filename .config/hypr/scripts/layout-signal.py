#!/usr/bin/env python3
# Escucha el socket de eventos de Hyprland y refresca el módulo custom/language
# de waybar (señal RTMIN+9) cada vez que cambia el layout con SUPER+Space.
import os
import socket
import subprocess
import sys

# Sin un salto de línea en este margen el flujo no es un evento válido de Hyprland;
# se descarta para que un emisor defectuoso no haga crecer la memoria sin límite.
MAX_PENDIENTE = 65536


def socket_path(env=os.environ):
    return f"{env['XDG_RUNTIME_DIR']}/hypr/{env['HYPRLAND_INSTANCE_SIGNATURE']}/.socket2.sock"


def refresh_waybar():
    subprocess.run(["pkill", "-RTMIN+9", "waybar"], check=False)


def listen(sock, on_layout_change=refresh_waybar):
    pendiente = ""
    while True:
        data = sock.recv(4096).decode(errors="ignore")
        if not data:
            break
        pendiente += data
        while "\n" in pendiente:
            line, pendiente = pendiente.split("\n", 1)
            if line.startswith("activelayout>>"):
                on_layout_change()
        if len(pendiente) > MAX_PENDIENTE:
            pendiente = ""


def main():
    try:
        path = socket_path()
    except KeyError as missing:
        print(f"layout-signal: falta la variable de entorno {missing.args[0]}", file=sys.stderr)
        return 1
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(path)
        listen(sock)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
