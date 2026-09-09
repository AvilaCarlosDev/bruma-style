#!/usr/bin/env python3
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup, make_list, add_row, bind_activate, sep, section_label
from gi.repository import Gtk


def get_volume():
    out = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                          capture_output=True, text=True).stdout.strip()
    muted = "MUTED" in out
    try:
        pct = round(float(out.split()[1]) * 100)
    except (IndexError, ValueError):
        pct = 0
    return pct, muted


def set_volume(pct):
    subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{pct/100:.2f}"])


def toggle_mute():
    subprocess.Popen(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])


def get_mic_muted():
    out = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"],
                          capture_output=True, text=True).stdout.strip()
    return "MUTED" in out


def toggle_mic_mute():
    subprocess.Popen(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"])


def default_sink_desc():
    name = subprocess.run(["pactl", "get-default-sink"],
                           capture_output=True, text=True).stdout.strip()
    listing = subprocess.run(["pactl", "list", "sinks"],
                              capture_output=True, text=True).stdout
    in_sink = False
    for line in listing.splitlines():
        if line.startswith("Sink #"):
            in_sink = False
        if line.strip() == f"Name: {name}":
            in_sink = True
        if in_sink and "Description:" in line:
            return line.split("Description:", 1)[1].strip()
    return "Salida"


def main():
    pct, muted = get_volume()
    sink_desc = default_sink_desc()
    mic_muted = get_mic_muted()

    popup = GlassPopup(width=280, margin_right=230)

    vol_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    vol_row.get_style_context().add_class("glass-volume-row")

    top = Gtk.Box()
    lbl_left = Gtk.Label(label="Volumen de salida", xalign=0)
    lbl_left.get_style_context().add_class("row-meta")
    top.pack_start(lbl_left, True, True, 0)
    val_lbl = Gtk.Label()
    val_lbl.get_style_context().add_class("glass-volume-val")
    val_lbl.set_text(f"{pct}%" if not muted else f"{pct}% · silenciado")
    top.pack_start(val_lbl, False, False, 0)
    vol_row.pack_start(top, False, False, 0)

    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(pct)
    scale.set_draw_value(False)
    scale.get_style_context().add_class("glass-scale")

    def on_change(sc):
        set_volume(int(sc.get_value()))
        val_lbl.set_text(f"{int(sc.get_value())}%")

    scale.connect("value-changed", on_change)
    vol_row.pack_start(scale, False, False, 0)
    popup.body.pack_start(vol_row, False, False, 0)

    popup.body.pack_start(section_label("SALIDA"), False, False, 0)
    lst = make_list()
    add_row(lst, "🔈", sink_desc, active=True)
    add_row(lst, "🔇", "Silenciar parlantes",
            meta="Silenciado" if muted else "Activo",
            danger=muted, on_click=toggle_mute)
    bind_activate(lst, popup)
    popup.body.pack_start(lst, False, False, 0)
    popup.body.pack_start(section_label("ENTRADA"), False, False, 0)
    lst2 = make_list()
    add_row(lst2, "🎙", "Silenciar micrófono",
            meta="Silenciado" if mic_muted else "Activo",
            danger=mic_muted, on_click=toggle_mic_mute)

    sep_box2 = Gtk.ListBoxRow()
    sep_box2.set_activatable(False)
    sep_box2.set_selectable(False)
    sep_box2.add(sep())
    lst2.add(sep_box2)
    add_row(lst2, "🎛", "Mezclador completo (pavucontrol)",
            on_click=lambda: subprocess.Popen(["pavucontrol"]))
    bind_activate(lst2, popup)
    popup.body.pack_start(lst2, False, False, 0)
    popup.run()


if __name__ == "__main__":
    main()
