# Registro de cambios / Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) ·
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Sin publicar / Unreleased]

### Añadido / Added
- Pruebas unitarias en `tests/python/` para los menús de audio, batería, red,
  Bluetooth, energía, portapapeles y fondos de pantalla, y para `layout-signal`
  (GTK y comandos del sistema simulados). / Unit tests for the menus and
  `layout-signal`.
- Pruebas de interfaz con GTK real en `tests/gtk/` (54): `GlassPopup`, `Launcher`
  y el `main()` de los siete menús, con un trabajo de CI bajo Xvfb. / UI tests
  with real GTK covering `GlassPopup`, `Launcher` and every menu's `main()`.
- Pruebas de shell para `weather.sh` y los scripts de la tableta en
  `tests/run.sh`. / Shell tests for `weather.sh` and the tablet scripts.
- Configuración de `ruff` y `pytest` en `pyproject.toml`; dependencias de
  desarrollo fijadas en `requirements-dev.txt`. / `ruff` and `pytest`
  configuration; pinned development dependencies.
- CI: trabajos de Python, escaneo de secretos (gitleaks) y verificación de
  marcas de agua. / CI jobs for Python, secret scanning and watermark checks.
- Documentación bilingüe (`README`, `PACKAGES`, `CONTRIBUTING`, `SECURITY`),
  `CODE_OF_CONDUCT` y plantillas de issues y PR. / Bilingual documentation,
  code of conduct, and issue/PR templates.

### Seguridad / Security
- Las notificaciones escapan el marcado de nombres que controlan terceros (SSID,
  dispositivos Bluetooth, archivos): antes un SSID como `<a href=...>` llegaba a
  `swaync` como enlace. / Notifications now escape markup in third-party names.
- `weather.sh`: la ubicación se codifica en la URL (`/`, `?` o `#` ya no la
  alteran) y la caché deja de caer en `/tmp` compartido. / The location is
  percent-encoded and the cache no longer falls back to a shared `/tmp`.
- Scripts de la tableta: exigen `XDG_RUNTIME_DIR` para el PID y el registro de
  WayVNC en lugar de usar `/tmp`. / Tablet scripts require `XDG_RUNTIME_DIR`.

### Corregido / Fixed
- `bluetooth_menu`: los dispositivos conectados no respondían al clic, así que no
  se podían desconectar desde el menú; faltaba `bind_activate` en su lista. /
  Connected devices did not react to clicks, so they could not be disconnected.
- `layout-signal.py` se reestructura en funciones (`socket_path`, `listen`,
  `main`): ya no se conecta al importarse, informa si faltan variables de
  entorno y descarta flujos sin salto de línea que crecerían sin límite. /
  Restructured into functions; no side effects on import.
- `network_menu`: los SSID y nombres de perfil con `:` o `\` se interpretaban
  mal porque `nmcli -t` los escapa; ahora se separan respetando el escape. /
  SSIDs and profile names containing `:` or `\` were parsed incorrectly.
- `audio_menu`: si `wpctl` o `pactl` no están instalados, el menú ya no falla
  y muestra valores neutros. / The menu no longer crashes when `wpctl` or
  `pactl` are missing.
- `common`: se elimina un import sin uso (`GLib`). / Removed an unused import.

## [0.1.0] - 2026-09-18

### Añadido / Added
- Publicación inicial de la configuración portable de Hyprland, Waybar y menús
  GTK, con instalador que respalda antes de escribir. / Initial release of the
  portable Hyprland, Waybar and GTK menu configuration, with a backup-first
  installer.
