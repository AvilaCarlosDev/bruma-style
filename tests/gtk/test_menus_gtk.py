"""`main()` de cada menú con GTK real: qué filas construye y qué ocurre al activarlas."""
from ayudas import Gtk, activar, fila, filas, recorrer, textos
from gi.repository import GdkPixbuf

MAC_AURICULARES, MAC_TECLADO, MAC_NUEVO = "AA:AA:AA:AA:AA:01", "AA:AA:AA:AA:AA:02", "AA:AA:AA:AA:AA:03"


class HiloSincrono:
    """Ejecuta el hilo de escaneo al instante y en el mismo hilo, sin bucle de GLib."""

    def __init__(self, target, daemon=True):
        self.target = target

    def start(self):
        self.target()


def sin_hilos(monkeypatch, modulo):
    monkeypatch.setattr(modulo.threading, "Thread", HiloSincrono)
    monkeypatch.setattr(modulo.GLib, "idle_add", lambda funcion, *args: funcion(*args))


def abrir(sesion, main):
    main()
    assert len(sesion.ventanas) == 1
    return sesion.ventanas[0]


# ---------------------------------------------------------------- energía
def test_energia_lista_las_cinco_acciones(load_menu, sesion):
    popup = abrir(sesion, load_menu("power_menu").main)
    assert [t for f in filas(popup) for t in textos(f)[1:]] == [
        "Bloquear pantalla", "Suspender", "Reiniciar", "Apagar", "Cerrar sesión",
    ]


def test_energia_cada_fila_ejecuta_su_comando_y_cierra(load_menu, sesion, monkeypatch):
    modulo = load_menu("power_menu")
    ejecutados = []
    monkeypatch.setattr(modulo, "run", lambda *cmd: ejecutados.append(cmd))
    popup = abrir(sesion, modulo.main)
    for texto in ("Bloquear pantalla", "Suspender", "Reiniciar", "Apagar", "Cerrar sesión"):
        activar(popup, texto)
    assert ejecutados == [
        ("hyprlock",), ("systemctl", "suspend"), ("systemctl", "reboot"),
        ("systemctl", "poweroff"), ("pkill", "-SIGTERM", "-x", "Hyprland"),
    ]
    assert sesion.cierres == 5


def test_energia_marca_como_peligrosas_apagar_y_cerrar_sesion(load_menu, sesion):
    popup = abrir(sesion, load_menu("power_menu").main)
    peligrosas = {textos(f)[1] for f in filas(popup) if f.get_style_context().has_class("danger")}
    assert peligrosas == {"Apagar", "Cerrar sesión"}


# ---------------------------------------------------------------- audio
def preparar_audio(modulo, monkeypatch, pct=40, silenciado=False, mic_silenciado=True):
    llamadas = []
    monkeypatch.setattr(modulo, "get_volume", lambda: (pct, silenciado))
    monkeypatch.setattr(modulo, "default_sink_desc", lambda: "Altavoces internos")
    monkeypatch.setattr(modulo, "get_mic_muted", lambda: mic_silenciado)
    monkeypatch.setattr(modulo, "set_volume", lambda v: llamadas.append(("volumen", v)))
    monkeypatch.setattr(modulo, "toggle_mute", lambda: llamadas.append("mute"))
    monkeypatch.setattr(modulo, "toggle_mic_mute", lambda: llamadas.append("mic"))
    monkeypatch.setattr(modulo.subprocess, "Popen", lambda cmd, **kw: llamadas.append(tuple(cmd)))
    return llamadas


def test_audio_muestra_volumen_salida_y_entrada(load_menu, sesion, monkeypatch):
    modulo = load_menu("audio_menu")
    preparar_audio(modulo, monkeypatch)
    etiquetas = textos(abrir(sesion, modulo.main))
    esperadas = ("Volumen de salida", "40%", "SALIDA", "Altavoces internos", "ENTRADA", "Silenciar micrófono")
    for esperado in esperadas:
        assert esperado in etiquetas


def test_audio_indica_cuando_el_volumen_esta_silenciado(load_menu, sesion, monkeypatch):
    modulo = load_menu("audio_menu")
    preparar_audio(modulo, monkeypatch, pct=25, silenciado=True)
    popup = abrir(sesion, modulo.main)
    assert "25% · silenciado" in textos(popup)
    assert "Silenciado" in textos(fila(popup, "Silenciar parlantes"))
    assert fila(popup, "Silenciar parlantes").get_style_context().has_class("danger")


def test_audio_el_deslizador_arranca_en_el_volumen_actual_y_envia_cambios(load_menu, sesion, monkeypatch):
    modulo = load_menu("audio_menu")
    llamadas = preparar_audio(modulo, monkeypatch, pct=40)
    popup = abrir(sesion, modulo.main)
    escala = next(w for w in recorrer(popup) if isinstance(w, Gtk.Scale))
    assert escala.get_value() == 40
    escala.set_value(60)
    assert ("volumen", 60) in llamadas and "60%" in textos(popup)


def test_audio_las_filas_ejecutan_sus_acciones(load_menu, sesion, monkeypatch):
    modulo = load_menu("audio_menu")
    llamadas = preparar_audio(modulo, monkeypatch)
    popup = abrir(sesion, modulo.main)
    activar(popup, "Silenciar parlantes")
    activar(popup, "Silenciar micrófono")
    activar(popup, "Mezclador completo (pavucontrol)")
    assert llamadas == ["mute", "mic", ("pavucontrol",)]


# ---------------------------------------------------------------- batería
def preparar_bateria(modulo, monkeypatch, tmp_path, inicio="40", fin="80", nivel="87", estado="Charging"):
    for nombre, valor in (("capacity", nivel), ("status", estado),
                          ("charge_control_start_threshold", inicio), ("charge_control_end_threshold", fin)):
        (tmp_path / nombre).write_text(valor)
    monkeypatch.setattr(modulo, "BAT", str(tmp_path))
    aplicados = []
    monkeypatch.setattr(modulo, "apply", aplicados.append)
    return aplicados


def test_bateria_muestra_nivel_estado_y_marca_el_modo_activo(load_menu, sesion, monkeypatch, tmp_path):
    modulo = load_menu("battery_menu")
    preparar_bateria(modulo, monkeypatch, tmp_path)
    popup = abrir(sesion, modulo.main)
    etiquetas = textos(popup)
    assert "87%" in etiquetas and "Charging" in etiquetas and "MODO DE CARGA" in etiquetas
    activas = [textos(f)[1] for f in filas(popup) if f.get_style_context().has_class("active")]
    assert activas == ["Preservación"]


def test_bateria_cada_modo_llama_a_apply_con_su_nombre(load_menu, sesion, monkeypatch, tmp_path):
    modulo = load_menu("battery_menu")
    aplicados = preparar_bateria(modulo, monkeypatch, tmp_path)
    popup = abrir(sesion, modulo.main)
    for texto in ("Carga completa", "Preservación", "Equilibrado", "Default TLP"):
        activar(popup, texto)
    assert aplicados == ["full", "preserve", "balanced", "reset"]


def test_bateria_sin_dispositivo_no_marca_ningun_modo_ni_falla(load_menu, sesion, monkeypatch):
    modulo = load_menu("battery_menu")
    monkeypatch.setattr(modulo, "BAT", "")
    popup = abrir(sesion, modulo.main)
    assert "?%" in textos(popup)
    assert not [f for f in filas(popup) if f.get_style_context().has_class("active")]


# ---------------------------------------------------------------- red
def preparar_red(modulo, monkeypatch, activo=True, actual="MiRed"):
    conexiones = []
    redes = {"Casa": ("WPA2", "70"), "Cafe": ("--", "50"), "MiRed": ("WPA2", "90")}
    monkeypatch.setattr(modulo, "wifi_enabled", lambda: activo)
    monkeypatch.setattr(modulo, "active_ssid", lambda: actual)
    monkeypatch.setattr(modulo, "saved_connections", lambda: {"MiRed", "Casa"})
    monkeypatch.setattr(modulo, "scan", lambda: redes)
    monkeypatch.setattr(modulo, "connect", lambda *args: conexiones.append(args))
    sin_hilos(monkeypatch, modulo)
    return conexiones


def test_red_muestra_la_conectada_y_las_disponibles_por_senal(load_menu, sesion, monkeypatch):
    modulo = load_menu("network_menu")
    preparar_red(modulo, monkeypatch)
    popup = abrir(sesion, modulo.main)
    lineas = [textos(f) for f in filas(popup) if len(textos(f)) >= 2]
    assert ["✓", "MiRed", "Conectado"] in lineas
    disponibles = [t[1] for t in lineas if t[0] in ("🔒", "📶")]
    assert disponibles == ["Casa", "Cafe"]
    assert ["📶", "Cafe", "50%"] in lineas and ["🔒", "Casa", "70%"] in lineas


def test_red_activar_una_red_conecta_con_su_seguridad_y_perfiles_guardados(load_menu, sesion, monkeypatch):
    modulo = load_menu("network_menu")
    conexiones = preparar_red(modulo, monkeypatch)
    popup = abrir(sesion, modulo.main)
    activar(popup, "Casa")
    activar(popup, "Cafe")
    assert conexiones == [("Casa", "WPA2", {"MiRed", "Casa"}), ("Cafe", "--", {"MiRed", "Casa"})]


def test_red_con_wifi_apagado_solo_muestra_el_interruptor(load_menu, sesion, monkeypatch):
    modulo = load_menu("network_menu")
    preparar_red(modulo, monkeypatch, activo=False)
    popup = abrir(sesion, modulo.main)
    assert textos(popup) == ["Wi-Fi"]
    assert any(isinstance(w, Gtk.Switch) for w in recorrer(popup))


def test_red_el_interruptor_enciende_y_apaga_la_radio(load_menu, sesion, monkeypatch):
    modulo = load_menu("network_menu")
    preparar_red(modulo, monkeypatch, activo=False)
    ejecutados = []
    monkeypatch.setattr(modulo.subprocess, "run", lambda cmd, **kw: ejecutados.append(cmd))
    popup = abrir(sesion, modulo.main)
    interruptor = next(w for w in recorrer(popup) if isinstance(w, Gtk.Switch))
    interruptor.set_active(True)
    interruptor.set_active(False)
    assert ejecutados == [["nmcli", "radio", "wifi", "on"], ["nmcli", "radio", "wifi", "off"]]


def test_red_sin_conexion_activa_no_muestra_fila_de_conectado(load_menu, sesion, monkeypatch):
    modulo = load_menu("network_menu")
    preparar_red(modulo, monkeypatch, actual=None)
    popup = abrir(sesion, modulo.main)
    assert "Conectado" not in [t for f in filas(popup) for t in textos(f)]
    assert "MiRed" in [t for f in filas(popup) for t in textos(f)]


# ---------------------------------------------------------------- bluetooth
def preparar_bluetooth(modulo, monkeypatch, activo=True, emparejados=None, cercanos=None):
    if emparejados is None:
        emparejados = {MAC_AURICULARES: "Auriculares", MAC_TECLADO: "Teclado"}
    cercanos = {**emparejados, MAC_NUEVO: "Nuevo"} if cercanos is None else cercanos
    acciones = []
    monkeypatch.setattr(modulo, "power_enabled", lambda: activo)

    def dispositivos(filtro=None):
        if filtro == "Paired":
            return emparejados
        if filtro == "Connected":
            return {MAC_AURICULARES: "Auriculares"} if MAC_AURICULARES in emparejados else {}
        return cercanos

    monkeypatch.setattr(modulo, "list_devices", dispositivos)
    monkeypatch.setattr(modulo, "btctl", lambda *args, **kw: acciones.append(("btctl", args)))
    monkeypatch.setattr(modulo, "connect", lambda mac: acciones.append(("connect", mac)))
    monkeypatch.setattr(modulo, "disconnect", lambda mac: acciones.append(("disconnect", mac)))
    monkeypatch.setattr(modulo, "pair_and_connect", lambda *datos: acciones.append(("pair", *datos)))
    sin_hilos(monkeypatch, modulo)
    return acciones


def test_bluetooth_separa_conectados_emparejados_y_cercanos(load_menu, sesion, monkeypatch):
    modulo = load_menu("bluetooth_menu")
    preparar_bluetooth(modulo, monkeypatch)
    popup = abrir(sesion, modulo.main)
    lineas = [textos(f) for f in filas(popup)]
    assert ["✓", "Auriculares", "Conectado"] in lineas
    assert ["🔵", "Teclado", "Emparejado"] in lineas
    assert ["📡", "Nuevo"] in lineas
    assert ["📡", "Teclado"] not in lineas and ["📡", "Auriculares"] not in lineas


def test_bluetooth_las_filas_llaman_a_la_accion_correcta(load_menu, sesion, monkeypatch):
    modulo = load_menu("bluetooth_menu")
    acciones = preparar_bluetooth(modulo, monkeypatch)
    acciones.clear()
    popup = abrir(sesion, modulo.main)
    activar(popup, "Auriculares")
    activar(popup, "Teclado")
    activar(popup, "Nuevo")
    assert [a for a in acciones if a[0] != "btctl"] == [
        ("disconnect", MAC_AURICULARES), ("connect", MAC_TECLADO), ("pair", MAC_NUEVO, "Nuevo"),
    ]


def test_bluetooth_escanea_cinco_segundos_al_abrir(load_menu, sesion, monkeypatch):
    modulo = load_menu("bluetooth_menu")
    acciones = preparar_bluetooth(modulo, monkeypatch)
    abrir(sesion, modulo.main)
    assert ("btctl", ("scan", "on")) in acciones


def test_bluetooth_sin_emparejados_ni_cercanos_muestra_mensajes_vacios(load_menu, sesion, monkeypatch):
    modulo = load_menu("bluetooth_menu")
    preparar_bluetooth(modulo, monkeypatch, emparejados={}, cercanos={})
    etiquetas = [t for f in filas(abrir(sesion, modulo.main)) for t in textos(f)]
    assert "Sin dispositivos emparejados" in etiquetas and "Nada nuevo cerca" in etiquetas


def test_bluetooth_apagado_solo_muestra_el_interruptor(load_menu, sesion, monkeypatch):
    modulo = load_menu("bluetooth_menu")
    acciones = preparar_bluetooth(modulo, monkeypatch, activo=False)
    popup = abrir(sesion, modulo.main)
    assert textos(popup) == ["Bluetooth"] and acciones == []
    interruptor = next(w for w in recorrer(popup) if isinstance(w, Gtk.Switch))
    interruptor.set_active(True)
    assert acciones == [("btctl", ("power", "on"))]


# ---------------------------------------------------------------- portapapeles
def test_portapapeles_lista_filtra_y_copia(load_menu, sesion, monkeypatch):
    modulo = load_menu("clipboard_menu")
    copiados = []
    monkeypatch.setattr(modulo, "load_entries", lambda: ["1\thola mundo", "2\tadiós", "3\t" + "x" * 200])
    monkeypatch.setattr(modulo, "copy_entry", copiados.append)
    menu = modulo.ClipboardMenu()
    assert [textos(f)[0] for f in filas(menu.list)] == ["hola mundo", "adiós", "x" * 90]
    menu.search.set_text("ADI")
    assert [textos(f)[0] for f in filas(menu.list)] == ["adiós"]
    activar(menu.list, "adiós")
    assert copiados == ["2\tadiós"] and sesion.cierres == 1


def test_portapapeles_vacio_no_muestra_filas(load_menu, sesion, monkeypatch):
    modulo = load_menu("clipboard_menu")
    monkeypatch.setattr(modulo, "load_entries", lambda: [])
    menu = modulo.ClipboardMenu()
    assert filas(menu.list) == []
    menu.run()
    assert sesion.ventanas == [menu.popup]


# ---------------------------------------------------------------- fondos de pantalla
def imagen_pequena(ruta):
    GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 4, 4).savev(str(ruta), "png", [], [])
    return str(ruta)


def test_fondos_muestra_conteo_marca_el_actual_filtra_y_aplica(load_menu, sesion, monkeypatch, tmp_path):
    modulo = load_menu("wallpaper_menu")
    for nombre in ("mar.png", "montana.png"):
        imagen_pequena(tmp_path / nombre)
    aplicados = []
    monkeypatch.setattr(modulo, "WALLPAPER_DIR", str(tmp_path))
    monkeypatch.setattr(modulo, "list_wallpapers", lambda: ["mar.png", "montana.png"])
    monkeypatch.setattr(modulo, "current_wallpaper", lambda: str(tmp_path / "mar.png"))
    monkeypatch.setattr(modulo, "thumb_for", lambda ruta: ruta)
    monkeypatch.setattr(modulo, "apply_wallpaper", aplicados.append)

    selector = modulo.WallpaperPicker()
    assert "2 fondos en ~/wallpaper" in textos(selector.popup)
    marcados = [textos(h) for h in selector.grid.get_children() if "✓" in textos(h)]
    assert marcados == [["✓", "mar"]]

    selector.search.set_text("MONT")
    assert [textos(h)[-1] for h in selector.grid.get_children()] == ["montana"]

    selector.grid.emit("child-activated", selector.grid.get_children()[0])
    assert aplicados == [str(tmp_path / "montana.png")] and sesion.cierres == 1
    selector.run()
    assert sesion.ventanas == [selector.popup]


def test_fondos_sin_imagenes_muestra_cero(load_menu, sesion, monkeypatch):
    modulo = load_menu("wallpaper_menu")
    monkeypatch.setattr(modulo, "list_wallpapers", lambda: [])
    monkeypatch.setattr(modulo, "current_wallpaper", lambda: None)
    selector = modulo.WallpaperPicker()
    assert "0 fondos en ~/wallpaper" in textos(selector.popup)
    assert selector.grid.get_children() == []
