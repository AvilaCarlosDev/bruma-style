# Registro de cambios / Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) ·
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Sin publicar / Unreleased]

### Añadido / Added
- Pruebas unitarias en `tests/python/` para los menús de audio, batería, red,
  portapapeles y fondos de pantalla (GTK y comandos del sistema simulados). /
  Unit tests for the audio, battery, network, clipboard and wallpaper menus.
- Configuración de `ruff` y `pytest` en `pyproject.toml`; dependencias de
  desarrollo fijadas en `requirements-dev.txt`. / `ruff` and `pytest`
  configuration; pinned development dependencies.
- CI: trabajos de Python, escaneo de secretos (gitleaks) y verificación de
  marcas de agua. / CI jobs for Python, secret scanning and watermark checks.
- Documentación bilingüe (`README`, `PACKAGES`, `CONTRIBUTING`, `SECURITY`),
  `CODE_OF_CONDUCT` y plantillas de issues y PR. / Bilingual documentation,
  code of conduct, and issue/PR templates.

### Corregido / Fixed
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
