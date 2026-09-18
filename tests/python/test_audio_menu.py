import pytest

WPCTL_SINK = ("wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@")
WPCTL_SOURCE = ("wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@")


@pytest.fixture
def audio(load_menu):
    return load_menu("audio_menu")


@pytest.mark.parametrize(
    "salida, esperado",
    [
        ("Volume: 0.45\n", (45, False)),
        ("Volume: 0.30 [MUTED]\n", (30, True)),
        ("Volume: 1.00\n", (100, False)),
        ("Volume: 0.005\n", (0, False)),
        ("", (0, False)),
        ("Volume:", (0, False)),
        ("Volume: abc", (0, False)),
    ],
)
def test_get_volume_interpreta_la_salida_de_wpctl(audio, monkeypatch, fake_run, salida, esperado):
    monkeypatch.setattr(audio.subprocess, "run", fake_run({WPCTL_SINK: salida}))
    assert audio.get_volume() == esperado


def test_get_volume_sin_wpctl_no_rompe_el_menu(audio, monkeypatch, fake_run):
    monkeypatch.setattr(audio.subprocess, "run", fake_run(missing=["wpctl"]))
    assert audio.get_volume() == (0, False)


@pytest.mark.parametrize(
    "salida, esperado",
    [("Volume: 0.5 [MUTED]", True), ("Volume: 0.5", False), ("", False)],
)
def test_get_mic_muted(audio, monkeypatch, fake_run, salida, esperado):
    monkeypatch.setattr(audio.subprocess, "run", fake_run({WPCTL_SOURCE: salida}))
    assert audio.get_mic_muted() is esperado


def test_get_mic_muted_sin_wpctl_asume_no_silenciado(audio, monkeypatch, fake_run):
    monkeypatch.setattr(audio.subprocess, "run", fake_run(missing=["wpctl"]))
    assert audio.get_mic_muted() is False


LISTADO = """Sink #47
\tState: RUNNING
\tName: alsa_output.speakers
\tDescription: Altavoces internos
Sink #52
\tState: IDLE
\tName: alsa_output.hdmi
\tDescription: HDMI / DisplayPort
"""


@pytest.mark.parametrize(
    "predeterminado, esperado",
    [
        ("alsa_output.speakers", "Altavoces internos"),
        ("alsa_output.hdmi", "HDMI / DisplayPort"),
        ("no_existe", "Salida"),
        ("", "Salida"),
    ],
)
def test_default_sink_desc_elige_la_descripcion_del_sink_activo(
    audio, monkeypatch, fake_run, predeterminado, esperado
):
    salidas = {("pactl", "get-default-sink"): predeterminado + "\n", ("pactl", "list", "sinks"): LISTADO}
    monkeypatch.setattr(audio.subprocess, "run", fake_run(salidas))
    assert audio.default_sink_desc() == esperado


def test_default_sink_desc_sin_pactl_devuelve_valor_por_defecto(audio, monkeypatch, fake_run):
    monkeypatch.setattr(audio.subprocess, "run", fake_run(missing=["pactl"]))
    assert audio.default_sink_desc() == "Salida"


def test_set_volume_envia_fraccion_con_dos_decimales(audio, monkeypatch):
    lanzados = []
    monkeypatch.setattr(audio.subprocess, "Popen", lambda cmd, **kw: lanzados.append(cmd))
    audio.set_volume(45)
    assert lanzados == [["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "0.45"]]
