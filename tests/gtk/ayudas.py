"""Ayudantes para recorrer y accionar el árbol de widgets."""
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


def hijos(widget):
    return widget.get_children() if isinstance(widget, Gtk.Container) else []


def recorrer(widget):
    yield widget
    for hijo in hijos(widget):
        yield from recorrer(hijo)


def textos(widget):
    return [w.get_text() for w in recorrer(widget) if isinstance(w, Gtk.Label)]


def filas(widget):
    return [w for w in recorrer(widget) if isinstance(w, Gtk.ListBoxRow)]


def fila(widget, texto):
    coincidencias = [f for f in filas(widget) if texto in textos(f)]
    assert coincidencias, f"no hay fila con el texto {texto!r}; hay: {[textos(f) for f in filas(widget)]}"
    return coincidencias[0]


def activar(widget, texto):
    """Simula el clic en la fila con ese texto, tal como lo dispara GTK."""
    objetivo = fila(widget, texto)
    objetivo.get_parent().emit("row-activated", objetivo)
