#!/usr/bin/env python3
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup, make_list, add_row, bind_activate, section_label
from gi.repository import Gtk

BAT = "/sys/class/power_supply/BAT0"
MODE_SCRIPT = "/home/carlosdev/scripts/battery-mode.sh"


def read(path, default="?"):
    try:
        with open(f"{BAT}/{path}") as f:
            return f.read().strip()
    except OSError:
        return default


def active_mode():
    start, stop = read("charge_control_start_threshold"), read("charge_control_end_threshold")
    return {
        ("0", "100"): "full",
        ("40", "80"): "preserve",
        ("50", "90"): "balanced",
        ("96", "100"): "reset",
    }.get((start, stop))


def apply(mode):
    subprocess.Popen([MODE_SCRIPT, mode])


def main():
    level = read("capacity")
    status = read("status")
    mode = active_mode()

    popup = GlassPopup(width=270, margin_right=110)

    head = Gtk.Box(spacing=10)
    head.set_margin_top(4)
    head.set_margin_bottom(6)
    head.set_margin_start(8)
    head.set_margin_end(8)
    pct_lbl = Gtk.Label(xalign=0)
    color = "#42ffa1" if status == "Charging" else "#f5f5f7"
    pct_lbl.set_markup(f"<span font_desc='16' weight='bold'>{level}%</span>")
    state_lbl = Gtk.Label(xalign=0)
    state_lbl.set_markup(f"<span foreground='{color}' size='small'>{status}</span>")
    col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    col.pack_start(pct_lbl, False, False, 0)
    col.pack_start(state_lbl, False, False, 0)
    head.pack_start(col, False, False, 0)
    popup.body.pack_start(head, False, False, 0)

    popup.body.pack_start(section_label("MODO DE CARGA"), False, False, 0)

    lst = make_list()
    add_row(lst, "🔌", "Carga completa", meta="0–100%",
            active=(mode == "full"), on_click=lambda: apply("full"))
    add_row(lst, "🛡", "Preservación", meta="40–80%",
            active=(mode == "preserve"), on_click=lambda: apply("preserve"))
    add_row(lst, "⚖", "Equilibrado", meta="50–90%",
            active=(mode == "balanced"), on_click=lambda: apply("balanced"))
    add_row(lst, "↺", "Default TLP", meta="96–100%",
            active=(mode == "reset"), on_click=lambda: apply("reset"))

    bind_activate(lst, popup)
    popup.body.pack_start(lst, False, False, 0)
    popup.run()


if __name__ == "__main__":
    main()
