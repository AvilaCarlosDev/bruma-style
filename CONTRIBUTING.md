# Contribuir / Contributing

[Español](#español) · [English](#english)

## Español

Bruma-style es un subconjunto público y curado de un escritorio real, no un marco
universal para Hyprland. Las contribuciones deben mejorar la portabilidad, la
corrección, la privacidad o la documentación sin añadir datos propios de un
equipo.

Antes de abrir un pull request:

1. ejecuta `./tests/run.sh`;
2. instala las dependencias de desarrollo (`pip install -r requirements-dev.txt`)
   y ejecuta `ruff check .` y `pytest`;
3. ejecuta `shellcheck install.sh scripts/*.sh tests/*.sh .config/hypr/scripts/*.sh .config/waybar/scripts/*.sh`;
4. confirma que capturas, registros y datos de prueba no contienen usuarios,
   nombres de equipo, nombres de red, tokens ni rutas personales absolutas;
5. documenta las dependencias nuevas, obligatorias u opcionales, en
   `PACKAGES.md` y `PACKAGES.en.md`;
6. indica qué hardware y qué versión de Hyprland usaste en las pruebas manuales;
7. todo cambio de lógica en los menús de Python debe llevar su prueba en
   `tests/python/`, incluidos los casos límite (comando ausente, salida vacía,
   datos corruptos); los cambios de interfaz, en `tests/gtk/`
   (`xvfb-run -a python3 -m pytest tests/gtk`).

La documentación pública se mantiene en español e inglés; si cambias una,
actualiza la otra. El CI rechaza marcas de agua de IA en archivos y mensajes de
commit (por ejemplo, trailers `Co-Authored-By` de asistentes). Si usaste un
asistente, menciónalo en la descripción del PR.

No envíes credenciales, perfiles de red ni copias completas de un directorio
personal. Mantén los cambios enfocados y describe las limitaciones con honestidad.

## English

Bruma-style is a curated public subset of a real desktop, not a universal
Hyprland framework. Contributions should improve portability, correctness,
privacy or documentation without adding machine-specific data.

Before opening a pull request:

1. run `./tests/run.sh`;
2. install the development dependencies (`pip install -r requirements-dev.txt`)
   and run `ruff check .` and `pytest`;
3. run `shellcheck install.sh scripts/*.sh tests/*.sh .config/hypr/scripts/*.sh .config/waybar/scripts/*.sh`;
4. confirm screenshots, logs and fixtures contain no usernames, hostnames,
   network names, tokens or absolute personal paths;
5. document new required and optional dependencies in `PACKAGES.md` and
   `PACKAGES.en.md`;
6. state which hardware and Hyprland version were used for manual testing;
7. any logic change in the Python menus must come with a test in
   `tests/python/`, including edge cases (missing command, empty output,
   corrupt data); UI changes go in `tests/gtk/`
   (`xvfb-run -a python3 -m pytest tests/gtk`).

Public documentation is kept in Spanish and English; if you change one, update
the other. CI rejects AI watermarks in files and commit messages (for example
assistant `Co-Authored-By` trailers). If you used an assistant, say so in the PR
description instead.

Do not submit credentials, network profiles or full copies of a home directory.
Keep changes focused and describe limitations honestly.
