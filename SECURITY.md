# Política de seguridad / Security policy

[Español](#español) · [English](#english)

## Español

Vaho contiene configuración de escritorio y scripts auxiliares locales. No
opera ningún servicio alojado y nunca debe incluir credenciales activas ni
perfiles de red privados.

### Cómo reportar

Usa el flujo de avisos de seguridad privados de GitHub (pestaña *Security* →
*Report a vulnerability*) para vulnerabilidades que puedan ejecutar comandos no
previstos, exponer secretos locales o debilitar la garantía de copia de
seguridad del instalador. Para errores comunes, abre un issue público.

No incluyas contraseñas, tokens, claves privadas, SSID ni otros datos privados
en un reporte. Oculta rutas y capturas que identifiquen un equipo o a una
persona.

Solo se mantiene la rama `main` actual.

## English

Vaho contains desktop configuration and local helper scripts. It does not
operate a hosted service and it must never include live credentials or private
network profiles.

### Reporting

Use GitHub's private security-advisory flow (*Security* tab → *Report a
vulnerability*) for vulnerabilities that could execute unintended commands,
expose local secrets or weaken the installer's backup guarantees. For ordinary
bugs, open a public issue.

Do not include working passwords, tokens, private keys, SSIDs or other private
data in a report. Redact paths and screenshots when they identify a machine or
person.

Only the current `main` branch is maintained.
