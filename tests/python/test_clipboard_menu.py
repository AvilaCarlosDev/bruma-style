import subprocess

import pytest


@pytest.fixture
def clipboard(load_menu):
    return load_menu("clipboard_menu")


def test_load_entries_descarta_lineas_vacias(clipboard, monkeypatch, fake_run):
    salida = "1\thola\n\n   \n2\tmundo\n"
    monkeypatch.setattr(clipboard.subprocess, "run", fake_run({("cliphist", "list"): salida}))
    assert clipboard.load_entries() == ["1\thola", "2\tmundo"]


def test_load_entries_con_historial_vacio(clipboard, monkeypatch, fake_run):
    monkeypatch.setattr(clipboard.subprocess, "run", fake_run({("cliphist", "list"): ""}))
    assert clipboard.load_entries() == []


def test_copy_entry_decodifica_y_copia_al_portapapeles(clipboard, monkeypatch):
    llamadas = []

    def run(cmd, **kwargs):
        llamadas.append((cmd, kwargs.get("input")))
        return type("R", (), {"stdout": b"contenido real"})()

    monkeypatch.setattr(clipboard.subprocess, "run", run)
    clipboard.copy_entry("1\thola")
    assert llamadas[0] == (["cliphist", "decode"], b"1\thola")
    assert llamadas[1] == (["wl-copy"], b"contenido real")


def test_copy_entry_propaga_el_error_si_cliphist_falla(clipboard, monkeypatch):
    def run(cmd, **kwargs):
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(clipboard.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError):
        clipboard.copy_entry("1\thola")
