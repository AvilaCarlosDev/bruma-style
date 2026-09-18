"""Fixtures compartidos: simulan GTK y cargan los scripts de menú como módulos."""
import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GLASS_DIR = ROOT / ".config" / "waybar" / "scripts" / "glass"
HYPR_SCRIPTS_DIR = ROOT / ".config" / "hypr" / "scripts"


def _install_gi_stub():
    """Los menús importan `gi` a nivel de módulo; en CI no hay GTK ni pantalla."""
    from unittest.mock import MagicMock

    gtk = MagicMock(name="Gtk")
    gtk.Window = type("Window", (), {"__init__": lambda self, *a, **k: None})
    repository = types.ModuleType("gi.repository")
    for name in ("Gtk", "Gdk", "GLib", "Gio", "Pango", "GtkLayerShell"):
        setattr(repository, name, gtk if name == "Gtk" else MagicMock(name=name))
    gi = types.ModuleType("gi")
    gi.require_version = lambda *args, **kwargs: None
    gi.repository = repository
    sys.modules.setdefault("gi", gi)
    sys.modules.setdefault("gi.repository", repository)


_install_gi_stub()
sys.path.insert(0, str(GLASS_DIR))


@pytest.fixture
def load_menu():
    """Carga un script de `glass/` desde cero, con `HYPRGLASS_*` ya aplicado."""

    def _load(name):
        spec = importlib.util.spec_from_file_location(f"glass_{name}", GLASS_DIR / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return _load


@pytest.fixture
def load_hypr_script():
    """Carga un script de `.config/hypr/scripts/` (el nombre puede llevar guion)."""

    def _load(filename):
        name = filename.removesuffix(".py").replace("-", "_")
        spec = importlib.util.spec_from_file_location(name, HYPR_SCRIPTS_DIR / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return _load


class FakeRun:
    """Sustituto de subprocess.run: responde por comando y registra las llamadas."""

    def __init__(self, outputs=None, returncode=0, missing=()):
        self.outputs = outputs or {}
        self.returncode = returncode
        self.missing = set(missing)
        self.calls = []

    def __call__(self, cmd, **kwargs):
        self.calls.append((list(cmd), kwargs))
        if cmd[0] in self.missing:
            raise FileNotFoundError(cmd[0])
        stdout = self.outputs.get(tuple(cmd), "")
        return types.SimpleNamespace(stdout=stdout, returncode=self.returncode)


@pytest.fixture
def fake_run():
    return FakeRun
