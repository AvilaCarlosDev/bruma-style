"""Pruebas de interfaz con GTK real. Se ejecutan aparte de tests/python (que simula `gi`):

    xvfb-run -a python3 -m pytest tests/gtk

Ninguna ventana se muestra: solo se construyen y se recorre su árbol de widgets.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

GLASS_DIR = Path(__file__).resolve().parents[2] / ".config" / "waybar" / "scripts" / "glass"

try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import Gtk
except (ImportError, ValueError):
    Gtk = None

if Gtk is None:
    # Sin PyGObject no hay nada que importar; en CI las dependencias siempre están.
    collect_ignore_glob = ["test_*.py"]


def pytest_collection_modifyitems(config, items):
    motivo = None
    if getattr(sys.modules.get("gi"), "__file__", None) is None:
        motivo = "`gi` está simulado por tests/python; ejecuta tests/gtk por separado"
    elif not Gtk.init_check()[0]:
        motivo = "no hay display (usa xvfb-run)"
    if motivo:
        for item in items:
            item.add_marker(pytest.mark.skip(reason=motivo))


@pytest.fixture
def load_menu():
    def _load(name):
        sys.path.insert(0, str(GLASS_DIR))
        spec = importlib.util.spec_from_file_location(f"glass_{name}", GLASS_DIR / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return _load


@pytest.fixture
def common(load_menu):
    load_menu("common")
    import common as modulo

    return modulo


class Sesion:
    """Lo que ocurrió con el bucle de GTK: ventanas que pidieron `run` y salidas."""

    def __init__(self):
        self.ventanas = []
        self.cierres = 0


@pytest.fixture
def sesion(monkeypatch, common):
    """Evita el bucle de GTK: `run` solo registra la ventana y `main_quit` cuenta las salidas."""
    estado = Sesion()

    def run(self):
        estado.ventanas.append(self)

    def main_quit():
        estado.cierres += 1

    monkeypatch.setattr(common.GlassPopup, "run", run)
    monkeypatch.setattr(common.Gtk, "main_quit", main_quit)
    return estado
