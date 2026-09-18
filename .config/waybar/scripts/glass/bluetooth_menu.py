#!/usr/bin/env python3
import re
import subprocess
import sys
import threading

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup, make_list, add_row, bind_activate, sep, section_label
from gi.repository import Gtk, GLib


def btctl(*args, timeout=None):
    cmd = ["bluetoothctl"]
    if timeout:
        cmd += ["--timeout", str(timeout)]
    cmd += list(args)
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def notify(message):
    subprocess.Popen(["notify-send", "Bluetooth", message])


def power_enabled():
    return "Powered: yes" in btctl("show")


def list_devices(filter_name=None):
    args = ["devices"]
    if filter_name:
        args.append(filter_name)
    devices = {}
    for line in btctl(*args).splitlines():
        match = re.match(r"Device ([0-9A-F:]{17}) (.+)", line)
        if match:
            devices[match.group(1)] = match.group(2)
    return devices


def connect(mac):
    output = btctl("connect", mac)
    ok = "Connection successful" in output
    notify(f"Conectado a {list_devices().get(mac, mac)}" if ok else f"No pude conectar: {mac}")


def disconnect(mac):
    output = btctl("disconnect", mac)
    ok = "Successful disconnected" in output or "Successful" in output
    notify("Desconectado" if ok else f"No pude desconectar: {mac}")


def pair_and_connect(mac, name):
    notify(f"Emparejando con {name}…")
    btctl("pair", mac)
    btctl("trust", mac)
    output = btctl("connect", mac)
    notify(f"Conectado a {name}" if "Connection successful" in output else f"No pude emparejar con {name}")


def refresh():
    notify("Buscando dispositivos…")
    subprocess.Popen([__file__])


def main():
    enabled = power_enabled()
    popup = GlassPopup(width=300, margin_right=200)

    head = Gtk.Box(spacing=8)
    head.set_margin_top(4)
    head.set_margin_bottom(6)
    head.set_margin_start(8)
    head.set_margin_end(8)
    label = Gtk.Label(label="Bluetooth", xalign=0)
    label.get_style_context().add_class("glass-batt-pct")
    head.pack_start(label, True, True, 0)
    switch = Gtk.Switch()
    switch.get_style_context().add_class("glass-switch")
    switch.set_active(enabled)

    def on_switch(_switch, state):
        btctl("power", "on" if state else "off")
        return False

    switch.connect("state-set", on_switch)
    head.pack_start(switch, False, False, 0)
    popup.body.pack_start(head, False, False, 0)

    if not enabled:
        popup.run()
        return

    paired = list_devices("Paired")
    connected = set(list_devices("Connected").keys())
    connected_list = make_list()
    any_connected = False
    for mac, name in sorted(paired.items(), key=lambda item: item[1]):
        if mac in connected:
            add_row(connected_list, "✓", name, meta="Conectado", active=True,
                    on_click=lambda device=mac: disconnect(device))
            any_connected = True
    if any_connected:
        sep_row = Gtk.ListBoxRow()
        sep_row.set_activatable(False)
        sep_row.set_selectable(False)
        sep_row.add(sep())
        connected_list.add(sep_row)
    popup.body.pack_start(connected_list, False, False, 0)

    popup.body.pack_start(section_label("DISPOSITIVOS EMPAREJADOS"), False, False, 0)
    paired_list = make_list()
    for mac, name in sorted(paired.items(), key=lambda item: item[1]):
        if mac not in connected:
            add_row(paired_list, "🔵", name, meta="Emparejado",
                    on_click=lambda device=mac: connect(device))
    if not paired_list.get_children():
        add_row(paired_list, "—", "Sin dispositivos emparejados")
    bind_activate(paired_list, popup)
    popup.body.pack_start(paired_list, False, False, 0)

    popup.body.pack_start(section_label("DISPOSITIVOS CERCANOS"), False, False, 0)
    nearby_list = make_list()
    loading_row = Gtk.ListBoxRow()
    loading_row.set_activatable(False)
    loading_row.set_selectable(False)
    loading_label = Gtk.Label(label="Buscando…", xalign=0)
    loading_label.set_margin_start(10)
    loading_label.get_style_context().add_class("row-meta")
    loading_row.add(loading_label)
    nearby_list.add(loading_row)
    popup.body.pack_start(nearby_list, False, False, 0)

    def on_scan_done(nearby):
        nearby_list.remove(loading_row)
        found = False
        for mac, name in sorted(nearby.items(), key=lambda item: item[1]):
            if mac in paired:
                continue
            found = True
            add_row(nearby_list, "📡", name,
                    on_click=lambda device=mac, label=name: pair_and_connect(device, label))
        if not found:
            add_row(nearby_list, "—", "Nada nuevo cerca")
        bind_activate(nearby_list, popup)
        nearby_list.show_all()
        return False

    def scan_worker():
        btctl("scan", "on", timeout=5)
        GLib.idle_add(on_scan_done, list_devices())

    threading.Thread(target=scan_worker, daemon=True).start()

    actions = make_list()
    add_row(actions, "↻", "Refrescar", on_click=refresh)
    add_row(actions, "⚙", "Editor avanzado…", on_click=lambda: subprocess.Popen(["blueman-manager"]))
    bind_activate(actions, popup)
    popup.body.pack_start(actions, False, False, 0)
    popup.run()


if __name__ == "__main__":
    main()
