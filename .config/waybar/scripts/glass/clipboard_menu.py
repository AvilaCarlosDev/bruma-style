#!/usr/bin/env python3
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup
from gi.repository import Gtk, Pango


def load_entries():
    out = subprocess.run(["cliphist", "list"], capture_output=True, text=True).stdout
    return [line for line in out.splitlines() if line.strip()]


def copy_entry(line):
    decode = subprocess.run(["cliphist", "decode"], input=line, capture_output=True, text=True)
    subprocess.run(["wl-copy"], input=decode.stdout.encode())


class ClipboardMenu:
    def __init__(self):
        self.popup = GlassPopup(width=460, height=440, center=True)
        self.entries = load_entries()

        self.search = Gtk.Entry(placeholder_text="Buscar en el portapapeles")
        self.search.get_style_context().add_class("glass-search")
        self.search.set_margin_bottom(10)
        self.search.connect("changed", self.on_search)
        self.popup.body.pack_start(self.search, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list.get_style_context().add_class("glass-list")
        self.list.connect("row-activated", self.on_activated)
        scroller.add(self.list)
        self.popup.body.pack_start(scroller, True, True, 0)

        self.populate()
        self.search.grab_focus()

    def populate(self, query=""):
        for child in self.list.get_children():
            self.list.remove(child)
        for line in self.entries:
            text = line.split("\t", 1)[-1]
            if query and query.lower() not in text.lower():
                continue
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label=text[:90], xalign=0)
            lbl.get_style_context().add_class("row-label")
            lbl.set_margin_top(6)
            lbl.set_margin_bottom(6)
            lbl.set_margin_start(8)
            lbl.set_margin_end(8)
            lbl.set_ellipsize(Pango.EllipsizeMode.END)
            lbl.set_max_width_chars(1)
            lbl.set_hexpand(True)
            row.add(lbl)
            row._raw = line
            self.list.add(row)
        self.list.show_all()

    def on_search(self, entry):
        self.populate(entry.get_text())

    def on_activated(self, _lb, row):
        copy_entry(row._raw)
        self.popup._quit()

    def run(self):
        self.popup.run()


if __name__ == "__main__":
    ClipboardMenu().run()
