import socket

import pytest


@pytest.fixture
def layout(load_hypr_script):
    return load_hypr_script("layout-signal.py")


class SocketFalso:
    """Entrega los fragmentos indicados y luego un cierre (b"")."""

    def __init__(self, *fragmentos):
        self.fragmentos = list(fragmentos)

    def recv(self, _tamano):
        return self.fragmentos.pop(0) if self.fragmentos else b""


def test_socket_path_se_arma_con_el_entorno_de_hyprland(layout):
    entorno = {"XDG_RUNTIME_DIR": "/run/user/1000", "HYPRLAND_INSTANCE_SIGNATURE": "abc123"}
    assert layout.socket_path(entorno) == "/run/user/1000/hypr/abc123/.socket2.sock"


def test_socket_path_sin_variables_falla_con_keyerror(layout):
    with pytest.raises(KeyError):
        layout.socket_path({})


def test_listen_avisa_solo_en_eventos_activelayout(layout):
    llamadas = []
    sock = SocketFalso(b"workspace>>2\nactivelayout>>kb,us\nfocus>>x\nactivelayout>>kb,es\n")
    layout.listen(sock, lambda: llamadas.append(1))
    assert len(llamadas) == 2


def test_listen_reensambla_eventos_partidos_entre_lecturas(layout):
    llamadas = []
    sock = SocketFalso(b"activelay", b"out>>kb,es", b"\nworkspace>>1\n")
    layout.listen(sock, lambda: llamadas.append(1))
    assert len(llamadas) == 1


def test_listen_ignora_bytes_invalidos_sin_romperse(layout):
    llamadas = []
    sock = SocketFalso(b"\xff\xfe\nactivelayout>>kb,us\n")
    layout.listen(sock, lambda: llamadas.append(1))
    assert len(llamadas) == 1


def test_listen_descarta_el_flujo_sin_saltos_de_linea_que_supera_el_limite(layout, monkeypatch):
    monkeypatch.setattr(layout, "MAX_PENDIENTE", 10)
    llamadas = []
    sock = SocketFalso(b"x" * 20, b"activelayout>>kb,us\n")
    layout.listen(sock, lambda: llamadas.append(1))
    assert len(llamadas) == 1


def test_listen_con_socket_real_termina_al_cerrarse_el_otro_extremo(layout):
    a, b = socket.socketpair()
    b.sendall(b"activelayout>>kb,es\n")
    b.close()
    llamadas = []
    layout.listen(a, lambda: llamadas.append(1))
    a.close()
    assert llamadas == [1]


def test_refresh_waybar_envia_la_senal_rtmin_9(layout, monkeypatch):
    llamadas = []
    monkeypatch.setattr(layout.subprocess, "run", lambda cmd, **kw: llamadas.append(cmd))
    layout.refresh_waybar()
    assert llamadas == [["pkill", "-RTMIN+9", "waybar"]]


def test_main_sin_variables_de_hyprland_termina_con_error_claro(layout, monkeypatch, capsys):
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
    assert layout.main() == 1
    assert "XDG_RUNTIME_DIR" in capsys.readouterr().err
