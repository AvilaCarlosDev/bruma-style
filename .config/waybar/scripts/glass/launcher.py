#!/usr/bin/env python3
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup
from gi.repository import Gtk, Gio, GLib

CATEGORIES = [
    ("Aplicaciones", None),
    ("Red", "Network"),
    ("Dev", "Development"),
    ("Multimedia", "AudioVideo|Audio|Video"),
    ("Oficina", "Office"),
    ("Sistema", "System"),
    ("Juegos", "Game"),
    ("Gráficos", "Graphics"),
]


def load_apps():
    apps = []
    for info in Gio.AppInfo.get_all():
        if not info.should_show():
            continue
        apps.append(info)
    apps.sort(key=lambda a: (a.get_display_name() or "").lower())
    return apps


def matches_category(info, pattern):
    if pattern is None:
        return True
    cats = info.get_categories() or ""
    return re.search(pattern, cats) is not None


class Launcher:
    def __init__(self):
        self.popup = GlassPopup(width=760, height=520, center=True)
        self.apps = load_apps()
        self.active_pattern = None
        self.query = ""

        self.search = Gtk.Entry(placeholder_text="Buscar aplicaciones")
        self.search.get_style_context().add_class("glass-search")
        self.search.set_margin_bottom(12)
        self.search.connect("changed", self.on_search_changed)
        self.search.connect("activate", self.on_search_activate)
        self.popup.body.pack_start(self.search, False, False, 0)

        pills = Gtk.Box(spacing=6)
        pills.set_margin_bottom(14)
        self.pill_buttons = []
        for label, pattern in CATEGORIES:
            btn = Gtk.ToggleButton(label=label)
            btn.get_style_context().add_class("glass-pill")
            btn.set_active(pattern is None)
            btn.connect("toggled", self.on_category_toggled, pattern, btn)
            pills.pack_start(btn, False, False, 0)
            self.pill_buttons.append(btn)
        self.popup.body.pack_start(pills, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.grid = Gtk.FlowBox()
        self.grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self.grid.set_max_children_per_line(6)
        self.grid.set_min_children_per_line(6)
        self.grid.set_row_spacing(10)
        self.grid.set_column_spacing(4)
        self.grid.set_homogeneous(True)
        self.grid.get_style_context().add_class("glass-appgrid")
        self.grid.connect("child-activated", self.on_activated)
        scroller.add(self.grid)
        self.popup.body.pack_start(scroller, True, True, 0)

        self.populate()
        self.search.grab_focus()

    def on_category_toggled(self, btn, pattern, self_btn):
        if not btn.get_active():
            return
        for b in self.pill_buttons:
            if b is not btn:
                b.set_active(False)
        self.active_pattern = pattern
        self.populate()

    def on_search_changed(self, entry):
        self.query = entry.get_text().lower()
        self.populate()

    def on_search_activate(self, entry):
        for child in self.grid.get_children():
            self.launch(child.info)
            return

    def populate(self):
        for child in self.grid.get_children():
            self.grid.remove(child)
        for info in self.apps:
            if self.query and self.query not in (info.get_display_name() or "").lower():
                continue
            if not matches_category(info, self.active_pattern):
                continue
            self.grid.add(self.make_tile(info))
        self.grid.show_all()

    def make_tile(self, info):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(4)
        box.set_margin_bottom(4)

        img = Gtk.Image()
        icon = info.get_icon()
        if icon:
            img.set_from_gicon(icon, Gtk.IconSize.DIALOG)
        img.set_pixel_size(48)
        box.pack_start(img, False, False, 0)

        name = Gtk.Label(label=info.get_display_name() or info.get_name())
        name.set_line_wrap(True)
        name.set_justify(Gtk.Justification.CENTER)
        name.set_max_width_chars(12)
        name.set_lines(2)
        name.get_style_context().add_class("glass-app-name")
        box.pack_start(name, False, False, 0)

        child = Gtk.FlowBoxChild()
        child.add(box)
        child.info = info
        return child

    def on_activated(self, _flow, child):
        self.launch(child.info)

    def launch(self, info):
        try:
            info.launch([], None)
        except GLib.Error:
            pass
        self.popup._quit()

    def run(self):
        self.popup.run()


if __name__ == "__main__":
    Launcher().run()
