"""Los nombres de redes, dispositivos y archivos los controlan terceros: nunca deben llegar
al demonio de notificaciones como marcado (enlaces o formato falsos)."""

MALICIOSO = "<a href='https://malo.example'>Cobro pendiente</a> & <b>urgente</b>"
ESCAPADO = "&lt;a href='https://malo.example'&gt;Cobro pendiente&lt;/a&gt; &amp; &lt;b&gt;urgente&lt;/b&gt;"


def test_network_notify_escapa_el_marcado(load_menu, monkeypatch):
    red = load_menu("network_menu")
    lanzados = []
    monkeypatch.setattr(red.subprocess, "Popen", lambda cmd, **kw: lanzados.append(cmd))
    red.notify(f"Conectado a {MALICIOSO}")
    assert lanzados == [["notify-send", "Wi-Fi", f"Conectado a {ESCAPADO}"]]


def test_wallpaper_notifica_el_nombre_de_archivo_escapado(load_menu, monkeypatch, tmp_path):
    wall = load_menu("wallpaper_menu")
    monkeypatch.setattr(wall, "CURRENT_FILE", str(tmp_path / "actual"))
    lanzados = []
    monkeypatch.setattr(wall.subprocess, "run", lambda cmd, **kw: None)
    monkeypatch.setattr(wall.subprocess, "Popen", lambda cmd, **kw: lanzados.append(cmd))
    wall.apply_wallpaper("/fondos/<b>x.png")
    aviso = next(c for c in lanzados if c[0] == "notify-send")
    assert "&lt;b&gt;x.png" in aviso[2] and "<b>" not in aviso[2]


def test_power_menu_escapa_el_error_del_comando(load_menu, monkeypatch):
    energia = load_menu("power_menu")
    lanzados = []

    class Proceso:
        returncode = 1

        def communicate(self):
            return None, b"fallo <b>grave</b>"

    def popen(cmd, **kwargs):
        lanzados.append(cmd)
        return Proceso()

    hilos = []

    class HiloSincrono:
        def __init__(self, target, daemon=True):
            hilos.append(target)

        def start(self):
            hilos[-1]()

    monkeypatch.setattr(energia.subprocess, "Popen", popen)
    monkeypatch.setattr(energia.threading, "Thread", HiloSincrono)
    energia.run("hyprlock")
    aviso = next(c for c in lanzados if c[0] == "notify-send")
    assert "&lt;b&gt;grave&lt;/b&gt;" in aviso[2] and "<b>" not in aviso[2]
