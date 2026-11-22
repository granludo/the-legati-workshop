# /playwright: dale a un agente un navegador de verdad

El patrón fijo para cualquier tarea de navegador que vaya más allá de una sola lectura. Léelo cuando tú (cualquier agente) necesites cargar una página renderizada con JS, sortear un bloqueo antibots, recorrer un flujo de varios pasos o capturar una pantalla o un PDF, y `WebFetch` no baste.

Esta skill es la capa de **cómo conseguir un navegador**. La regla que la gobierna es code-as-action (el código como acción): escribe un script y consérvalo; el navegador es desechable, el script es el activo duradero.

## Primera decisión: ¿de verdad necesitas Playwright?

| Tipo de tarea | Recurre a | Por qué |
|---|---|---|
| Leer una página pública y estática; extraer una cosa | **`WebFetch`** | Lo más barato, dentro del contexto. La opción por defecto. |
| GitHub (issues, PR, releases) | **la CLI `gh`** | Nunca uses `WebFetch` con github.com. |
| Gmail / Calendar / Drive | **una CLI de Workspace** (carril del agente comms) | Con alcance OAuth, no un navegador. |
| Moodle / LMS | **la API de servicios web del LMS** | Usa el endpoint WS, no un navegador. |
| **Renderizado con JS / varios pasos / con estado / bloqueado por antibots / captura como entregable** | **Playwright** (esta skill) | Cuando lo anterior no llega. |

Si `WebFetch` devuelve una página vacía, un muro de login o un `403`, esa es la señal para pasar a Playwright.

## Dos maneras de usar Playwright aquí: elige según si se va a repetir

**Modo A: script con la librería (code-as-action). Es la opción por defecto para todo lo que vaya a repetirse.**
Escribe un script pequeño `.mjs` (o en Python) con la librería `playwright`, haz commit en `tools/<task-slug>/` y, la próxima vez, vuelve a ejecutarlo o parte de él. El navegador es desechable; **el script es el activo duradero**.

- Crea un directorio `tools/<task-slug>/` con el script, un `package.json` y un README breve; pon en el gitignore `node_modules/` y cualquier `outputs/`.
- Parte de un ejemplo que funciona, [`tools/refs-check/verify-urls.mjs`](../tools/refs-check/verify-urls.mjs) (Node/`.mjs`): carga una lista de URL, registra el estado HTTP + el título de la página y modifica un fichero markdown. Una buena plantilla para «cargar N URL, extraer un campo de cada una, escribir los resultados de vuelta».

**Modo B: `@playwright/cli` para exploración interactiva puntual.**
Cuando solo necesitas tantear una página una vez (sacarle un snapshot, leer un valor, hacer una captura) y no hay nada que merezca conservarse, la CLI es más rápida que escribir un script: `npx --yes @playwright/cli@latest <command>`. Regla de tokens: mejor `snapshot` que volcar el DOM con `eval`.

**No** manejes el navegador turno a turno desde el chat («ahora haz clic ahí, ahora desplázate»). Si la tarea tiene más de ~2 pasos, es el modo A: escribe el script.

## Configuración única por máquina

Para un directorio de herramienta nuevo:
```bash
cd tools/<task-slug>/
npm install playwright                  # local dep; add node_modules/ to .gitignore
npx playwright install chromium         # ~150 MB, one-time per host, reused after
```
Para el modo B: `npx --yes @playwright/cli@latest <command>`, sin instalación; se cachea en la primera llamada.

**Avisa al usuario de la descarga por adelantado.** La primera instalación de navegadores en una máquina nueva descarga de ~150 MB (solo Chromium) a ~500 MB (todos los motores). Díselo al usuario antes de lanzarla, como con cualquier instalación larga.

## Trampas aprendidas en la práctica

- **Un navegador de verdad también sufre bloqueos antibots a veces.** Los servidores detrás de Cloudflare devuelven una página intermedia `403` (`"Just a moment…"` / `"Access Denied"`) incluso a un Chromium headless con un User-Agent correcto. Cuando pasa eso, la URL está detrás de un desafío duro: no lo tomes como prueba de que el recurso es falso; pásaselo a un humano para que haga clic.
- **Pon un User-Agent realista + `Accept-Language`.** El UA por defecto de Playwright se rechaza más a menudo. Usa un bloque `newContext({ userAgent, extraHTTPHeaders })`.
- **`waitUntil: 'domcontentloaded'`** suele bastar y es mucho más rápido que `networkidle` para comprobaciones del tipo «¿ha cargado esta página y cuál es su título?».
- **Los scripts de verificación solo deben mejorar la evidencia, nunca machacar un positivo anterior.** Una comprobación de navegador que falla (bloqueo/timeout) es **indeterminada**, no negativa: conserva el veredicto que ya tuvieras. Solo una evidencia nueva positiva (la página carga, el contenido coincide) debe cambiar un veredicto.
- **La autenticación se queda fuera de git.** Inicia sesión solo con credenciales que el usuario facilite para ese script (env / `.env`). Nunca guardes cookies ni sesiones en el repositorio. Los flujos con 2FA se devuelven al usuario.

## Nota sobre portabilidad

Esta skill es markdown sin más y se invoca en lenguaje natural («usa Playwright para cargar…»), sin ningún mecanismo propio de un scaffolding concreto. La capa duradera es: esta skill + los scripts versionados + `package.json`. `node_modules/` y los binarios de los navegadores son locales de cada máquina y `npm install` los vuelve a instalar. Cualquier scaffolding de agentes que pueda lanzar `node`/`npx` desde el shell los ejecuta sin cambios.

## Relacionado

- [`tools/refs-check/verify-urls.mjs`](../tools/refs-check/verify-urls.mjs): el ejemplo resuelto del modo A.

---

*La invocación canónica es en lenguaje natural; `/playwright` es el atajo corto.*
