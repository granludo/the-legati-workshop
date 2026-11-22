# Perfiles de máquina: una sección por máquina

Todo legatus lee **solo la sección de esta máquina** al arrancar: `bash tools/legati/host-section.sh` imprime la sección `## <hostname>` que coincide con `hostname -s` (sin distinguir mayúsculas de minúsculas), hasta el siguiente encabezado `## `. Una máquina sin sección → el legatus te lo dice y no supone ninguna cadena de herramientas.

> [!todo] Tú
> Añade una sección por cada máquina desde la que trabajes (`/start-here`, paso 6, escribe contigo la primera). Mantén cada sección corta: se lee al inicio de cada sesión. Borra el ejemplo de abajo cuando tengas el tuyo.

## example-laptop

- **Qué es:** portátil, macOS, Apple Silicon, 16 GB. Máquina de uso diario; viaja conmigo.
- **Harness:** Claude Code (con sesión iniciada); Codex (`codex login` hecho, `install-hooks.sh codex` ejecutado el 2026-11-22, hooks aprobados).
- **Ruta del repositorio:** `~/Code/my-workshop`.
- **Herramientas:** `pandoc`, `typst`, `python3` 3.12, `uv`, `node`, `llm` (con el plugin `llm-ollama`).
- **Modelos:** aquí no hay modelos locales; `llm -m gpt-…` con una clave en `llm keys`; un servidor Ollama local en el ordenador de sobremesa cuando estoy en la red de casa.
- **Repositorios externos:** ninguno.
- **Notas:** va con batería casi todo el día: aquí nada de lotes largos con modelos locales.
