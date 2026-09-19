import pytest
from ayudas import Gtk, textos
from gi.repository import GLib


class App:
    def __init__(self, nombre, categorias="", visible=True, falla=False):
        self.nombre, self.categorias, self.visible, self.falla = nombre, categorias, visible, falla
        self.lanzada = 0

    def should_show(self):
        return self.visible

    def get_display_name(self):
        return self.nombre

    def get_name(self):
        return self.nombre

    def get_categories(self):
        return self.categorias

    def get_icon(self):
        return None

    def launch(self, archivos, contexto):
        self.lanzada += 1
        if self.falla:
            raise GLib.Error("no se pudo lanzar")


@pytest.fixture
def apps():
    return [
        App("Firefox", "Network;WebBrowser;"),
        App("Kitty", "System;TerminalEmulator;"),
        App("Code", "Development;IDE;"),
        App("Oculta", "System;", visible=False),
        App("Steam", "Game;"),
    ]


@pytest.fixture
def lanzador(load_menu, sesion, monkeypatch, apps):
    modulo = load_menu("launcher")
    monkeypatch.setattr(modulo, "load_apps", lambda: [a for a in apps if a.should_show()])
    return modulo, modulo.Launcher()


def nombres_en_grilla(launcher):
    return [textos(hijo)[0] for hijo in launcher.grid.get_children()]


def test_load_apps_omite_las_ocultas_y_ordena_sin_distinguir_mayusculas(load_menu, monkeypatch):
    modulo = load_menu("launcher")
    sin_orden = [App("zeta"), App("Beta"), App("alfa"), App("oculta", visible=False)]
    monkeypatch.setattr(modulo.Gio.AppInfo, "get_all", staticmethod(lambda: sin_orden))
    assert [a.get_name() for a in modulo.load_apps()] == ["alfa", "Beta", "zeta"]


@pytest.mark.parametrize(
    "patron, categorias, esperado",
    [
        (None, "", True),
        ("Network", "Network;WebBrowser;", True),
        ("Network", "System;", False),
        ("AudioVideo|Audio|Video", "Video;Player;", True),
        ("Office", None, False),
    ],
)
def test_matches_category(load_menu, patron, categorias, esperado):
    modulo = load_menu("launcher")
    assert modulo.matches_category(App("x", categorias), patron) is esperado


def test_al_abrir_muestra_todas_las_aplicaciones_visibles(lanzador):
    _, launcher = lanzador
    assert nombres_en_grilla(launcher) == ["Firefox", "Kitty", "Code", "Steam"]


def test_la_busqueda_filtra_por_nombre_sin_distinguir_mayusculas(lanzador):
    _, launcher = lanzador
    launcher.search.set_text("FIRE")
    assert nombres_en_grilla(launcher) == ["Firefox"]
    launcher.search.set_text("no existe")
    assert nombres_en_grilla(launcher) == []


def test_el_filtro_de_categoria_reduce_la_lista(lanzador):
    modulo, launcher = lanzador
    boton_dev = next(b for b in launcher.pill_buttons if b.get_label() == "Dev")
    boton_dev.set_active(True)
    assert nombres_en_grilla(launcher) == ["Code"]


def test_las_categorias_son_excluyentes(lanzador):
    _, launcher = lanzador
    por_nombre = {b.get_label(): b for b in launcher.pill_buttons}
    por_nombre["Red"].set_active(True)
    por_nombre["Juegos"].set_active(True)
    assert por_nombre["Red"].get_active() is False
    assert nombres_en_grilla(launcher) == ["Steam"]


def test_busqueda_y_categoria_se_combinan(lanzador):
    _, launcher = lanzador
    por_nombre = {b.get_label(): b for b in launcher.pill_buttons}
    por_nombre["Sistema"].set_active(True)
    launcher.search.set_text("kit")
    assert nombres_en_grilla(launcher) == ["Kitty"]
    launcher.search.set_text("fire")
    assert nombres_en_grilla(launcher) == []


def test_enter_en_la_busqueda_lanza_la_primera_coincidencia_y_cierra(lanzador, apps, sesion):
    _, launcher = lanzador
    launcher.search.set_text("k")
    launcher.on_search_activate(launcher.search)
    assert apps[1].lanzada == 1 and sum(a.lanzada for a in apps) == 1
    assert sesion.cierres == 1


def test_enter_sin_resultados_no_lanza_nada(lanzador, apps, sesion):
    _, launcher = lanzador
    launcher.search.set_text("zzz")
    launcher.on_search_activate(launcher.search)
    assert sum(a.lanzada for a in apps) == 0 and sesion.cierres == 0


def test_activar_un_icono_lanza_esa_aplicacion(lanzador, apps, sesion):
    _, launcher = lanzador
    launcher.grid.emit("child-activated", launcher.grid.get_children()[2])
    assert apps[2].lanzada == 1 and sesion.cierres == 1


def test_un_error_al_lanzar_no_rompe_el_menu_y_lo_cierra(load_menu, sesion, monkeypatch):
    modulo = load_menu("launcher")
    rota = App("Rota", falla=True)
    monkeypatch.setattr(modulo, "load_apps", lambda: [rota])
    launcher = modulo.Launcher()
    launcher.launch(rota)
    assert rota.lanzada == 1 and sesion.cierres == 1


def test_la_tarjeta_usa_el_nombre_visible(lanzador):
    _, launcher = lanzador
    tile = launcher.make_tile(App("Mi App"))
    assert isinstance(tile, Gtk.FlowBoxChild) and textos(tile) == ["Mi App"]


def test_run_delega_en_el_popup(lanzador, sesion):
    _, launcher = lanzador
    launcher.run()
    assert sesion.ventanas == [launcher.popup]
