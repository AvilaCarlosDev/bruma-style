#!/usr/bin/env python3
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup, make_list, add_row, bind_activate, sep
from gi.repository import Gtk


def run(*cmd):
    subprocess.Popen(cmd)


def summon(name):
    subprocess.run(["shimejictl", "dismiss", "--all"])
    run("shimejictl", "summon", name)


def main():
    popup = GlassPopup(width=250, center=True)
    lst = make_list()

    add_row(lst, "🐾", "Luffy viejo",
            on_click=lambda: summon("Luffy_One_Piece"))
    add_row(lst, "🆕", "Luffy nuevo",
            on_click=lambda: summon("Luffy_ShimejiShop"))
    sep_row = Gtk.ListBoxRow()
    sep_row.set_activatable(False)
    sep_row.set_selectable(False)
    sep_row.add(sep())
    lst.add(sep_row)
    add_row(lst, "✕", "Quitar mascotas", danger=True,
            on_click=lambda: run("shimejictl", "dismiss", "--all"))

    bind_activate(lst, popup)
    popup.body.pack_start(lst, False, False, 0)
    popup.run()


if __name__ == "__main__":
    main()
