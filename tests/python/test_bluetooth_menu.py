import pytest

MAC = "AA:BB:CC:DD:EE:FF"


@pytest.fixture
def bt(load_menu):
    return load_menu("bluetooth_menu")


def _btctl(bt, monkeypatch, fake_run, salidas, **kwargs):
    registro = fake_run({("bluetoothctl", *k): v for k, v in salidas.items()}, **kwargs)
    monkeypatch.setattr(bt.subprocess, "run", registro)
    return registro


def test_btctl_agrega_timeout_solo_cuando_se_pide(bt, monkeypatch, fake_run):
    registro = _btctl(bt, monkeypatch, fake_run, {})
    bt.btctl("show")
    bt.btctl("scan", "on", timeout=5)
    assert registro.calls[0][0] == ["bluetoothctl", "show"]
    assert registro.calls[1][0] == ["bluetoothctl", "--timeout", "5", "scan", "on"]


@pytest.mark.parametrize(
    "salida, esperado",
    [("Powered: yes\n", True), ("Powered: no\n", False), ("", False)],
)
def test_power_enabled(bt, monkeypatch, fake_run, salida, esperado):
    _btctl(bt, monkeypatch, fake_run, {("show",): salida})
    assert bt.power_enabled() is esperado


def test_list_devices_solo_acepta_lineas_con_mac_valida(bt, monkeypatch, fake_run):
    salida = (
        f"Device {MAC} Auriculares\n"
        "Device 11:22:33:44:55:66 Teclado K380\n"
        "Device ZZ:BB:CC:DD:EE:FF Invalida\n"
        "Device AA:BB:CC Corta\n"
        "linea cualquiera\n"
    )
    _btctl(bt, monkeypatch, fake_run, {("devices",): salida})
    assert bt.list_devices() == {MAC: "Auriculares", "11:22:33:44:55:66": "Teclado K380"}


def test_list_devices_con_filtro_lo_pasa_a_bluetoothctl(bt, monkeypatch, fake_run):
    registro = _btctl(bt, monkeypatch, fake_run, {("devices", "Paired"): f"Device {MAC} Altavoz\n"})
    assert bt.list_devices("Paired") == {MAC: "Altavoz"}
    assert registro.calls[0][0] == ["bluetoothctl", "devices", "Paired"]


def test_list_devices_sin_bluetoothctl_falla_de_forma_explicita(bt, monkeypatch, fake_run):
    monkeypatch.setattr(bt.subprocess, "run", fake_run(missing=["bluetoothctl"]))
    with pytest.raises(FileNotFoundError):
        bt.list_devices()


@pytest.fixture
def avisos(bt, monkeypatch):
    lista = []
    monkeypatch.setattr(bt, "notify", lista.append)
    return lista


def test_connect_exitoso_avisa_con_el_nombre_del_dispositivo(bt, monkeypatch, fake_run, avisos):
    salidas = {("connect", MAC): "Connection successful", ("devices",): f"Device {MAC} Altavoz\n"}
    _btctl(bt, monkeypatch, fake_run, salidas)
    bt.connect(MAC)
    assert avisos == ["Conectado a Altavoz"]


def test_connect_fallido_avisa_con_la_mac(bt, monkeypatch, fake_run, avisos):
    _btctl(bt, monkeypatch, fake_run, {("connect", MAC): "Failed to connect"})
    bt.connect(MAC)
    assert avisos == [f"No pude conectar: {MAC}"]


def test_disconnect(bt, monkeypatch, fake_run, avisos):
    _btctl(bt, monkeypatch, fake_run, {("disconnect", MAC): "Successful disconnected"})
    bt.disconnect(MAC)
    _btctl(bt, monkeypatch, fake_run, {("disconnect", MAC): "Failed"})
    bt.disconnect(MAC)
    assert avisos == ["Desconectado", f"No pude desconectar: {MAC}"]


def test_pair_and_connect_ejecuta_pair_trust_y_connect_en_orden(bt, monkeypatch, fake_run, avisos):
    registro = _btctl(bt, monkeypatch, fake_run, {("connect", MAC): "Connection successful"})
    bt.pair_and_connect(MAC, "Altavoz")
    assert [c[0][1] for c in registro.calls] == ["pair", "trust", "connect"]
    assert avisos[-1] == "Conectado a Altavoz"


def test_notify_escapa_el_marcado_de_los_nombres_de_terceros(bt, monkeypatch):
    lanzados = []
    monkeypatch.setattr(bt.subprocess, "Popen", lambda cmd, **kw: lanzados.append(cmd))
    bt.notify("Conectado a <a href='https://malo.example'>Pulsa aquí</a> & co")
    assert lanzados == [["notify-send", "Bluetooth",
                         "Conectado a &lt;a href='https://malo.example'&gt;Pulsa aquí&lt;/a&gt; &amp; co"]]
