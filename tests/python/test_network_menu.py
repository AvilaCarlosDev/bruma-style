import pytest


@pytest.fixture
def network(load_menu):
    return load_menu("network_menu")


def _con_nmcli(network, monkeypatch, fake_run, salidas):
    monkeypatch.setattr(network.subprocess, "run", fake_run({("nmcli", *k): v for k, v in salidas.items()}))


def test_wifi_enabled(network, monkeypatch, fake_run):
    _con_nmcli(network, monkeypatch, fake_run, {("-g", "WIFI", "general"): "enabled\n"})
    assert network.wifi_enabled() is True
    _con_nmcli(network, monkeypatch, fake_run, {("-g", "WIFI", "general"): "disabled\n"})
    assert network.wifi_enabled() is False


ACTIVE = ("-t", "-f", "ACTIVE,SSID", "dev", "wifi")


@pytest.mark.parametrize(
    "salida, esperado",
    [
        ("no:Vecino\nyes:MiRed\n", "MiRed"),
        ("no:Vecino\n", None),
        ("", None),
        ("linea_corrupta\n", None),
        ("yes:Casa\\:5G\n", "Casa:5G"),
        ("yes:Ruta\\\\Dos\n", "Ruta\\Dos"),
    ],
)
def test_active_ssid(network, monkeypatch, fake_run, salida, esperado):
    _con_nmcli(network, monkeypatch, fake_run, {ACTIVE: salida})
    assert network.active_ssid() == esperado


SAVED = ("-t", "-f", "NAME,TYPE", "connection", "show")


def test_saved_connections_solo_incluye_perfiles_wifi(network, monkeypatch, fake_run):
    salida = "Casa:802-11-wireless\nCable:802-3-ethernet\nVPN:wireguard\nOficina:802-11-wireless\n"
    _con_nmcli(network, monkeypatch, fake_run, {SAVED: salida})
    assert network.saved_connections() == {"Casa", "Oficina"}


def test_saved_connections_con_dos_puntos_escapados_en_el_nombre(network, monkeypatch, fake_run):
    _con_nmcli(network, monkeypatch, fake_run, {SAVED: "Casa\\:5G:802-11-wireless\n"})
    assert network.saved_connections() == {"Casa:5G"}


SCAN = ("-t", "-f", "SSID,SECURITY,SIGNAL", "dev", "wifi", "list")


def test_scan_deduplica_por_ssid_y_omite_redes_ocultas_o_corruptas(network, monkeypatch, fake_run):
    salida = "MiRed:WPA2:80\nMiRed:WPA2:40\n:WPA2:70\nAbierta:--:55\ncorrupta\n"
    _con_nmcli(network, monkeypatch, fake_run, {SCAN: salida})
    assert network.scan() == {"MiRed": ("WPA2", "80"), "Abierta": ("--", "55")}


def test_scan_con_dos_puntos_escapados_en_el_ssid(network, monkeypatch, fake_run):
    _con_nmcli(network, monkeypatch, fake_run, {SCAN: "Casa\\:5G:WPA2:66\n"})
    assert network.scan() == {"Casa:5G": ("WPA2", "66")}


def test_scan_sin_nmcli_instalado_falla_de_forma_explicita(network, monkeypatch, fake_run):
    monkeypatch.setattr(network.subprocess, "run", fake_run(missing=["nmcli"]))
    with pytest.raises(FileNotFoundError):
        network.scan()


class _Registro:
    def __init__(self, network, monkeypatch, returncode=0):
        self.notificaciones, self.comandos, self.editores = [], [], []
        monkeypatch.setattr(network, "notify", self.notificaciones.append)

        def run(cmd, **kwargs):
            self.comandos.append(list(cmd))
            return type("R", (), {"returncode": returncode})()

        monkeypatch.setattr(network.subprocess, "run", run)
        monkeypatch.setattr(network.subprocess, "Popen", lambda cmd, **kw: self.editores.append(list(cmd)))


def test_connect_perfil_guardado_usa_connection_up(network, monkeypatch):
    r = _Registro(network, monkeypatch)
    network.connect("MiRed", "WPA2", {"MiRed"})
    assert r.comandos == [["nmcli", "connection", "up", "id", "MiRed"]]
    assert r.notificaciones == ["Conectado a MiRed"]


def test_connect_perfil_guardado_con_fallo_avisa_del_error(network, monkeypatch):
    r = _Registro(network, monkeypatch, returncode=1)
    network.connect("MiRed", "WPA2", {"MiRed"})
    assert "No pude conectar" in r.notificaciones[0]


def test_connect_red_protegida_nueva_nunca_pasa_la_clave_por_argv(network, monkeypatch):
    r = _Registro(network, monkeypatch)
    network.connect("Nueva", "WPA2", set())
    assert r.comandos == []
    assert r.editores == [["nm-connection-editor"]]


def test_connect_red_abierta_nueva_conecta_directo(network, monkeypatch):
    r = _Registro(network, monkeypatch)
    network.connect("Cafe", "--", set())
    assert r.comandos == [["nmcli", "device", "wifi", "connect", "Cafe"]]
