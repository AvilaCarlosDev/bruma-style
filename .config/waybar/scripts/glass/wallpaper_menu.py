#!/usr/bin/env python3
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup
from gi.repository import Gtk, Pango

HOME = os.path.expanduser("~")
WALLPAPER_DIR = os.path.join(HOME, "wallpaper")
THUMB_DIR = os.path.join(HOME, ".cache", "wallpaper-selector", "thumbs")
CURRENT_FILE = os.path.join(HOME, ".config", "hypr", "current_wallpaper")
EXTS = (".jpg", ".jpeg", ".png", ".webp")


def list_wallpapers():
    if not os.path.isdir(WALLPAPER_DIR):
        return []
    files = [f for f in os.listdir(WALLPAPER_DIR) if f.lower().endswith(EXTS)]
    files.sort()
    return files


def thumb_for(path):
    os.makedirs(THUMB_DIR, exist_ok=True)
    h = hashlib.sha256(path.encode()).hexdigest()
    thumb = os.path.join(THUMB_DIR, f"{h}.png")
    if not os.path.exists(thumb) or os.path.getmtime(path) > os.path.getmtime(thumb):
        subprocess.run([
            "magick", path, "-auto-orient", "-thumbnail", "256x144^",
            "-gravity", "center", "-extent", "256x144", thumb,
        ], capture_output=True)
    return thumb if os.path.exists(thumb) else path


def current_wallpaper():
    try:
        with open(CURRENT_FILE) as f:
            return f.read().strip()
    except OSError:
        return None


def apply_wallpaper(path):
    subprocess.run(["pkill", "swaybg"])
    subprocess.Popen(["swaybg", "-i", path, "-m", "fill"])
    with open(CURRENT_FILE, "w") as f:
        f.write(path)
    subprocess.Popen(["notify-send", "Wallpaper", f"Fondo cambiado a: {os.path.basename(path)}",
                       "-i", path])


class WallpaperPicker:
    def __init__(self):
        self.popup = GlassPopup(width=820, height=580, center=True)
        self.files = list_wallpapers()
        self.current = current_wallpaper()

        head = Gtk.Box(spacing=8)
        head.set_margin_bottom(10)
        count_lbl = Gtk.Label(xalign=0)
        count_lbl.get_style_context().add_class("row-meta")
        count_lbl.set_text(f"{len(self.files)} fondos en ~/wallpaper")
        head.pack_start(count_lbl, True, True, 0)
        self.popup.body.pack_start(head, False, False, 0)

        self.search = Gtk.Entry(placeholder_text="Buscar wallpaper")
        self.search.get_style_context().add_class("glass-search")
        self.search.set_margin_bottom(10)
        self.search.connect("changed", self.on_search)
        self.popup.body.pack_start(self.search, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.grid = Gtk.FlowBox()
        self.grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self.grid.set_max_children_per_line(4)
        self.grid.set_min_children_per_line(4)
        self.grid.set_row_spacing(12)
        self.grid.set_column_spacing(12)
        self.grid.set_homogeneous(True)
        self.grid.connect("child-activated", self.on_activated)
        scroller.add(self.grid)
        self.popup.body.pack_start(scroller, True, True, 0)

        self.populate()
        self.search.grab_focus()

    def populate(self, query=""):
        for child in self.grid.get_children():
            self.grid.remove(child)
        for fname in self.files:
            if query and query.lower() not in fname.lower():
                continue
            self.grid.add(self.make_tile(fname))
        self.grid.show_all()

    def make_tile(self, fname):
        full = os.path.join(WALLPAPER_DIR, fname)
        thumb = thumb_for(full)

        overlay = Gtk.Overlay()
        img = Gtk.Image.new_from_file(thumb)
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        frame.get_style_context().add_class("wall-tile")
        frame.add(img)
        overlay.add(frame)

        is_active = self.current and os.path.abspath(full) == os.path.abspath(self.current)
        if is_active:
            check = Gtk.Label(label="✓")
            check.set_halign(Gtk.Align.END)
            check.set_valign(Gtk.Align.START)
            check.get_style_context().add_class("wall-check")
            overlay.add_overlay(check)

        label = Gtk.Label(label=os.path.splitext(fname)[0])
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.get_style_context().add_class("glass-app-name")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.pack_start(overlay, False, False, 0)
        box.pack_start(label, False, False, 0)

        child = Gtk.FlowBoxChild()
        child.add(box)
        child.wallpaper_path = full
        return child

    def on_search(self, entry):
        self.populate(entry.get_text())

    def on_activated(self, _flow, child):
        apply_wallpaper(child.wallpaper_path)
        self.popup._quit()

    def run(self):
        self.popup.run()


if __name__ == "__main__":
    WallpaperPicker().run()
