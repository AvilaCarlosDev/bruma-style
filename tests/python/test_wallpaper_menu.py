import os
import time

import pytest


@pytest.fixture
def wall(load_menu, monkeypatch, tmp_path):
    modulo = load_menu("wallpaper_menu")
    monkeypatch.setattr(modulo, "WALLPAPER_DIR", str(tmp_path / "wallpaper"))
    monkeypatch.setattr(modulo, "THUMB_DIR", str(tmp_path / "thumbs"))
    monkeypatch.setattr(modulo, "CURRENT_FILE", str(tmp_path / "current_wallpaper"))
    return modulo


def test_list_wallpapers_filtra_por_extension_sin_distinguir_mayusculas_y_ordena(wall, tmp_path):
    carpeta = tmp_path / "wallpaper"
    carpeta.mkdir()
    for nombre in ("b.PNG", "a.jpg", "c.webp", "d.jpeg", "notas.txt", "video.mp4"):
        (carpeta / nombre).write_bytes(b"x")
    assert wall.list_wallpapers() == ["a.jpg", "b.PNG", "c.webp", "d.jpeg"]


def test_list_wallpapers_con_carpeta_inexistente(wall):
    assert wall.list_wallpapers() == []


def test_current_wallpaper_sin_archivo_es_none(wall):
    assert wall.current_wallpaper() is None


def test_current_wallpaper_lee_la_ruta_guardada(wall, tmp_path):
    (tmp_path / "current_wallpaper").write_text("/x/y.png\n")
    assert wall.current_wallpaper() == "/x/y.png"


def _origen(tmp_path):
    imagen = tmp_path / "foto.png"
    imagen.write_bytes(b"img")
    return str(imagen)


def test_thumb_for_genera_la_miniatura_y_la_reutiliza_mientras_este_vigente(wall, tmp_path, monkeypatch):
    llamadas = []

    def magick(cmd, **kwargs):
        llamadas.append(cmd)
        with open(cmd[-1], "wb") as salida:
            salida.write(b"thumb")

    monkeypatch.setattr(wall.subprocess, "run", magick)
    origen = _origen(tmp_path)
    miniatura = wall.thumb_for(origen)
    assert os.path.exists(miniatura) and len(llamadas) == 1
    assert wall.thumb_for(origen) == miniatura and len(llamadas) == 1


def test_thumb_for_regenera_si_el_original_es_mas_nuevo(wall, tmp_path, monkeypatch):
    llamadas = []

    def magick(cmd, **kwargs):
        llamadas.append(cmd)
        with open(cmd[-1], "wb") as salida:
            salida.write(b"t")

    monkeypatch.setattr(wall.subprocess, "run", magick)
    origen = _origen(tmp_path)
    miniatura = wall.thumb_for(origen)
    viejo = time.time() - 100
    os.utime(miniatura, (viejo, viejo))
    wall.thumb_for(origen)
    assert len(llamadas) == 2


def test_thumb_for_si_magick_no_produce_miniatura_devuelve_el_original(wall, tmp_path, monkeypatch):
    monkeypatch.setattr(wall.subprocess, "run", lambda cmd, **kw: None)
    origen = _origen(tmp_path)
    assert wall.thumb_for(origen) == origen


def test_apply_wallpaper_persiste_la_ruta_y_lanza_swaybg(wall, tmp_path, monkeypatch):
    lanzados = []
    monkeypatch.setattr(wall.subprocess, "run", lambda cmd, **kw: None)
    monkeypatch.setattr(wall.subprocess, "Popen", lambda cmd, **kw: lanzados.append(cmd))
    wall.apply_wallpaper("/fondos/mar.png")
    assert (tmp_path / "current_wallpaper").read_text() == "/fondos/mar.png"
    assert lanzados[0] == ["swaybg", "-i", "/fondos/mar.png", "-m", "fill"]
