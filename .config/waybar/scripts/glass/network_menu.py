#!/usr/bin/env python3
import subprocess
import sys
import threading

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import GlassPopup, make_list, add_row, bind_activate, sep, section_label
from gi.repository import Gtk, GLib


def nmcli(*args):
    return subprocess.run(["nmcli", *args], capture_output=True, text=True).stdout.strip()


def notify(msg):
    subprocess.Popen(["notify-send", "Wi-Fi", msg])


def wifi_enabled():
    return nmcli("-g", "WIFI", "general") == "enabled"


def active_ssid():
    for line in nmcli("-t", "-f", "ACTIVE,SSID", "dev", "wifi").splitlines():
        parts = line.split(":", 1)
        if len(parts) == 2 and parts[0] == "yes":
            return parts[1]
    return None


def saved_connections():
    names = set()
    for line in nmcli("-t", "-f", "NAME,TYPE", "connection", "show").splitlines():
        parts = line.rsplit(":", 1)
        if len(parts) == 2 and parts[1] == "802-11-wireless":
            names.add(parts[0])
    return names


def scan():
    seen = {}
    for line in nmcli("-t", "-f", "SSID,SECURITY,SIGNAL", "dev", "wifi", "list").splitlines():
        parts = line.split(":")
        if len(parts) < 3 or not parts[0] or parts[0] in seen:
            continue
        seen[parts[0]] = (parts[1], parts[2])
    return seen


def ask_password(ssid):
    dlg = Gtk.Dialog(title=f"Clave para {ssid}")
    dlg.get_style_context().add_class("glass-panel")
    dlg.set_decorated(False)
    entry = Gtk.Entry(visibility=False)
    entry.get_style_context().add_class("glass-search")
    entry.set_activates_default(True)
    box = dlg.get_content_area()
    box.set_spacing(8)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)
    box.add(entry)
    dlg.add_button("Conectar", Gtk.ResponseType.OK)
    dlg.set_default_response(Gtk.ResponseType.OK)
    dlg.show_all()
    resp = dlg.run()
    pw = entry.get_text() if resp == Gtk.ResponseType.OK else None
    dlg.destroy()
    return pw


def connect(ssid, security, saved):
    if ssid in saved:
        ok = subprocess.run(["nmcli", "connection", "up", "id", ssid]).returncode == 0
        notify(f"Conectado a {ssid}" if ok else f"No pude conectar con el perfil guardado: {ssid}")
        return
    if security and security != "--":
        pw = ask_password(ssid)
        if not pw:
            return
        ok = subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", pw]).returncode == 0
        notify(f"Conectado a {ssid}" if ok else f"No pude conectar a {ssid}. Revisa la clave o la señal.")
    else:
        ok = subprocess.run(["nmcli", "device", "wifi", "connect", ssid]).returncode == 0
        notify(f"Conectado a {ssid}" if ok else f"No pude conectar a {ssid}")


def refresh():
    notify("Buscando redes…")
    subprocess.Popen([__file__])


def open_editor():
    notify("Abriendo editor avanzado…")
    subprocess.Popen(["nm-connection-editor"])


def main():
    enabled = wifi_enabled()
    popup = GlassPopup(width=300, margin_right=330)

    head = Gtk.Box(spacing=8)
    head.set_margin_top(4)
    head.set_margin_bottom(6)
    head.set_margin_start(8)
    head.set_margin_end(8)
    lbl = Gtk.Label(label="Wi-Fi", xalign=0)
    lbl.get_style_context().add_class("glass-batt-pct")
    head.pack_start(lbl, True, True, 0)
    switch = Gtk.Switch()
    switch.get_style_context().add_class("glass-switch")
    switch.set_active(enabled)

    def on_switch(_sw, state):
        subprocess.run(["nmcli", "radio", "wifi", "on" if state else "off"])
        return False

    switch.connect("state-set", on_switch)
    head.pack_start(switch, False, False, 0)
    popup.body.pack_start(head, False, False, 0)

    if not enabled:
        popup.run()
        return

    current = active_ssid()
    saved = saved_connections()

    lst = make_list()
    if current:
        add_row(lst, "✓", current, meta="Conectado", active=True)
    sep_row = Gtk.ListBoxRow()
    sep_row.set_activatable(False)
    sep_row.set_selectable(False)
    sep_row.add(sep())
    lst.add(sep_row)
    popup.body.pack_start(lst, False, False, 0)
    popup.body.pack_start(section_label("REDES DISPONIBLES"), False, False, 0)

    loading_row = Gtk.ListBoxRow()
    loading_row.set_activatable(False)
    loading_row.set_selectable(False)
    loading_lbl = Gtk.Label(label="Buscando redes…", xalign=0)
    loading_lbl.set_margin_top(6)
    loading_lbl.set_margin_bottom(6)
    loading_lbl.set_margin_start(10)
    loading_lbl.get_style_context().add_class("row-meta")
    loading_row.add(loading_lbl)

    net_list = make_list()
    net_list.add(loading_row)
    popup.body.pack_start(net_list, False, False, 0)

    actions = make_list()
    add_row(actions, "↻", "Refrescar redes", on_click=refresh)
    add_row(actions, "⚙", "Editor avanzado…", on_click=open_editor)
    bind_activate(actions, popup)
    popup.body.pack_start(actions, False, False, 0)

    def on_scan_done(networks):
        net_list.remove(loading_row)
        for ssid, (security, signal) in sorted(networks.items(), key=lambda kv: -int(kv[1][1] or 0)):
            if ssid == current:
                continue
            glyph = "🔒" if security and security != "--" else "📶"
            add_row(net_list, glyph, ssid, meta=f"{signal}%",
                    on_click=lambda s=ssid, sec=security: connect(s, sec, saved))
        bind_activate(net_list, popup)
        net_list.show_all()
        return False

    def scan_worker():
        networks = scan()
        GLib.idle_add(on_scan_done, networks)

    threading.Thread(target=scan_worker, daemon=True).start()

    popup.run()


if __name__ == "__main__":
    main()
