#!/usr/bin/env python3
import subprocess
import sys
import threading

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup, make_list, add_row, bind_activate, sep


def run(*cmd):
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)

    def watch():
        _, err = p.communicate()
        if p.returncode not in (0, None) and err:
            subprocess.Popen(["notify-send", "Energía",
                               f"{cmd[0]} falló: {err.decode(errors='replace')[:200]}"])

    threading.Thread(target=watch, daemon=True).start()


def lock():
    run("hyprlock")


def main():
    popup = GlassPopup(width=230, margin_right=10)
    lst = make_list()

    add_row(lst, "🔒", "Bloquear pantalla", on_click=lock)
    add_row(lst, "󰤄", "Suspender",
            on_click=lambda: run("systemctl", "suspend"))
    add_row(lst, "󰜉", "Reiniciar",
            on_click=lambda: run("systemctl", "reboot"))
    lst.add(sep_row())
    add_row(lst, "⏻", "Apagar", danger=True,
            on_click=lambda: run("systemctl", "poweroff"))
    add_row(lst, "󰍃", "Cerrar sesión", danger=True,
            on_click=lambda: run("pkill", "-SIGTERM", "-x", "Hyprland"))

    bind_activate(lst, popup)
    popup.body.pack_start(lst, False, False, 0)
    popup.run()


def sep_row():
    from gi.repository import Gtk
    row = Gtk.ListBoxRow()
    row.set_activatable(False)
    row.set_selectable(False)
    row.add(sep())
    return row


if __name__ == "__main__":
    main()
