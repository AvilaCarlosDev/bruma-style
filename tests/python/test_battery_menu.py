import pytest


@pytest.fixture
def battery(load_menu, monkeypatch):
    monkeypatch.delenv("VAHO_BATTERY_PATH", raising=False)
    return load_menu("battery_menu")


def _fuente(raiz, nombre, tipo, **archivos):
    carpeta = raiz / nombre
    carpeta.mkdir()
    (carpeta / "type").write_text(tipo + "\n")
    for archivo, contenido in archivos.items():
        (carpeta / archivo).write_text(contenido)
    return carpeta


def test_battery_path_respeta_la_variable_de_entorno(battery, monkeypatch, tmp_path):
    monkeypatch.setenv("VAHO_BATTERY_PATH", str(tmp_path))
    assert battery.battery_path() == str(tmp_path)


def test_battery_path_omite_el_cargador_y_elige_la_bateria(battery, monkeypatch, tmp_path):
    _fuente(tmp_path, "AC", "Mains")
    bateria = _fuente(tmp_path, "BAT1", "Battery")
    monkeypatch.setattr(battery, "POWER_SUPPLY_ROOT", str(tmp_path))
    assert battery.battery_path() == str(bateria)


def test_battery_path_ignora_fuentes_sin_archivo_type(battery, monkeypatch, tmp_path):
    (tmp_path / "sin_type").mkdir()
    bateria = _fuente(tmp_path, "BAT0", "Battery")
    monkeypatch.setattr(battery, "POWER_SUPPLY_ROOT", str(tmp_path))
    assert battery.battery_path() == str(bateria)


def test_battery_path_sin_bateria_devuelve_cadena_vacia(battery, monkeypatch, tmp_path):
    _fuente(tmp_path, "AC", "Mains")
    monkeypatch.setattr(battery, "POWER_SUPPLY_ROOT", str(tmp_path))
    assert battery.battery_path() == ""


def test_battery_path_con_raiz_inexistente_devuelve_cadena_vacia(battery, monkeypatch, tmp_path):
    monkeypatch.setattr(battery, "POWER_SUPPLY_ROOT", str(tmp_path / "no_existe"))
    assert battery.battery_path() == ""


def test_read_devuelve_el_contenido_sin_espacios(battery, monkeypatch, tmp_path):
    (tmp_path / "capacity").write_text(" 87\n")
    monkeypatch.setattr(battery, "BAT", str(tmp_path))
    assert battery.read("capacity") == "87"


def test_read_sin_bateria_o_sin_archivo_devuelve_el_valor_por_defecto(battery, monkeypatch, tmp_path):
    monkeypatch.setattr(battery, "BAT", "")
    assert battery.read("capacity") == "?"
    monkeypatch.setattr(battery, "BAT", str(tmp_path))
    assert battery.read("no_existe", default="n/d") == "n/d"


@pytest.mark.parametrize(
    "inicio, fin, modo",
    [("0", "100", "full"), ("40", "80", "preserve"), ("50", "90", "balanced"), ("96", "100", "reset")],
)
def test_active_mode_reconoce_los_umbrales_conocidos(battery, monkeypatch, tmp_path, inicio, fin, modo):
    (tmp_path / "charge_control_start_threshold").write_text(inicio)
    (tmp_path / "charge_control_end_threshold").write_text(fin)
    monkeypatch.setattr(battery, "BAT", str(tmp_path))
    assert battery.active_mode() == modo


def test_active_mode_con_umbrales_desconocidos_o_ausentes_es_none(battery, monkeypatch, tmp_path):
    monkeypatch.setattr(battery, "BAT", str(tmp_path))
    assert battery.active_mode() is None
    (tmp_path / "charge_control_start_threshold").write_text("12")
    (tmp_path / "charge_control_end_threshold").write_text("34")
    assert battery.active_mode() is None
