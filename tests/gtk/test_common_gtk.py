from types import SimpleNamespace

from ayudas import Gtk, activar, recorrer, textos
from gi.repository import Gdk


def test_make_list_sin_seleccion_y_con_clase_de_estilo(common):
    lista = common.make_list()
    assert lista.get_selection_mode() == Gtk.SelectionMode.NONE
    assert lista.get_style_context().has_class("glass-list")


def test_add_row_construye_glifo_etiqueta_y_meta(common):
    lista = common.make_list()
    common.add_row(lista, "🔈", "Altavoces", meta="Activo")
    fila = lista.get_children()[0]
    assert textos(fila) == ["🔈", "Altavoces", "Activo"]


def test_add_row_sin_meta_no_crea_la_tercera_etiqueta(common):
    lista = common.make_list()
    common.add_row(lista, "🔈", "Altavoces")
    assert textos(lista.get_children()[0]) == ["🔈", "Altavoces"]


def test_add_row_marca_peligro_y_activo(common):
    lista = common.make_list()
    peligro = common.add_row(lista, "⏻", "Apagar", danger=True)
    activa = common.add_row(lista, "✓", "Conectado", active=True)
    normal = common.add_row(lista, "·", "Otra")
    assert peligro.get_style_context().has_class("danger")
    assert activa.get_style_context().has_class("active")
    assert not normal.get_style_context().has_class("danger")
    assert not normal.get_style_context().has_class("active")


def test_bind_activate_ejecuta_el_callback_y_cierra_el_popup(common, sesion):
    llamadas = []
    popup = common.GlassPopup()
    lista = common.make_list()
    common.add_row(lista, "·", "Accion", on_click=lambda: llamadas.append("hecho"))
    common.bind_activate(lista, popup)
    activar(lista, "Accion")
    assert llamadas == ["hecho"]
    assert sesion.cierres == 1


def test_bind_activate_en_fila_sin_callback_no_cierra(common, sesion):
    popup = common.GlassPopup()
    lista = common.make_list()
    common.add_row(lista, "—", "Informativa")
    common.bind_activate(lista, popup)
    activar(lista, "Informativa")
    assert sesion.cierres == 0


def test_sep_y_section_label(common):
    assert common.sep().get_style_context().has_class("glass-sep")
    etiqueta = common.section_label("SALIDA")
    assert etiqueta.get_text() == "SALIDA"
    assert etiqueta.get_style_context().has_class("glass-section-label")


def test_popup_se_configura_como_ventana_de_vidrio(common):
    popup = common.GlassPopup(width=300)
    assert popup.get_decorated() is False
    assert popup.get_resizable() is False
    assert popup.get_style_context().has_class("glass-panel")
    assert isinstance(popup.body, Gtk.Box)
    assert popup.body in list(recorrer(popup))


def test_popup_con_titulo_lo_muestra_con_marcado(common):
    popup = common.GlassPopup(title="<b>Ajustes</b>")
    assert "Ajustes" in textos(popup)


def test_popup_sin_titulo_solo_tiene_el_cuerpo(common):
    popup = common.GlassPopup()
    assert textos(popup) == []


def test_escape_cierra_el_popup_y_otras_teclas_no(common, sesion):
    popup = common.GlassPopup()
    popup._on_key(None, SimpleNamespace(keyval=Gdk.KEY_a))
    assert sesion.cierres == 0
    popup._on_key(None, SimpleNamespace(keyval=Gdk.KEY_Escape))
    assert sesion.cierres == 1


def test_run_muestra_la_ventana_y_entra_al_bucle(common, monkeypatch):
    eventos = []
    popup = common.GlassPopup()
    popup.show_all = lambda: eventos.append("show_all")
    popup.present = lambda: eventos.append("present")
    monkeypatch.setattr(common.Gtk, "main", lambda: eventos.append("main"))
    popup.run()
    assert eventos == ["show_all", "present", "main"]


def test_el_css_se_carga_una_sola_vez(common, monkeypatch):
    cargas = []
    monkeypatch.setattr(common, "_css_loaded", False)
    original = common.Gtk.CssProvider

    class Proveedor(original):
        def load_from_path(self, ruta):
            cargas.append(ruta)
            return super().load_from_path(ruta)

    monkeypatch.setattr(common.Gtk, "CssProvider", Proveedor)
    common.GlassPopup()
    common.GlassPopup()
    assert len(cargas) == 1 and cargas[0].endswith("theme.css")
