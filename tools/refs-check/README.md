# tools/refs-check/

Verificación de referencias para los documentos académicos que pasan por el revisor. Envuelve `bibsleuth` (triangulación en seis bases de datos: OpenAlex, Semantic Scholar, CrossRef, arXiv, DBLP, PubMed) y añade una pasada que descarga los resúmenes (abstracts) para que el revisor pueda comparar la **afirmación** que hace el artículo revisado sobre una referencia con **lo que la referencia dice de verdad**.

Produce un fichero markdown `<paper-stem>-refs-checks.md` que vive junto al documento revisado y se convierte en la **fuente de verdad** de la verificación de referencias de ese documento: en las revisiones siguientes el revisor lo lee en lugar de volver a consultar bibsleuth.

El encargo, en el taller original (2026-05-28):

> *«[reviewer], cuando revises un documento académico, crea en paralelo un `*-refs-checks.md` donde recopiles la lista de referencias del artículo y tu validación. Si es posible, consigue el abstract del artículo, para que puedas verificar la probabilidad de que el artículo sostenga de verdad lo que el artículo revisado afirma sobre la referencia. Después puedes tratar este fichero `*-refs-checks.md` como fuente de verdad, para no tener que volver a consultar la herramienta bibsleuth.»*

## Qué hay aquí

| Fichero | Qué hace |
|---|---|
| `check_refs.py` | El envoltorio. Ejecuta `bibsleuth check`, recupera los resúmenes (cadena de respaldo Semantic Scholar → OpenAlex → Crossref) y genera el markdown que hace de fuente de verdad. Idempotente: si lo vuelves a ejecutar con una referencia nueva en el .bib, solo añade la entrada nueva; las anotaciones manuales del revisor se conservan. |
| `setup.sh` | Arranque idempotente de la máquina. Instala `bibsleuth` con `uv tool install bibsleuth --python 3.12` y lanza una prueba rápida de conectividad de red contra una referencia que se sabe real. Se ejecuta una vez por máquina. |
| `README.md` | Este fichero. |

## Primera configuración en una máquina nueva

```bash
bash tools/refs-check/setup.sh
```

Define `REFS_CHECK_CONTACT=you@example.org` en el perfil de tu shell: OpenAlex y Crossref piden a los clientes educados una dirección de contacto, y el envoltorio la añade a su User-Agent solo si la variable está definida.

Idempotente: se puede volver a ejecutar sin riesgo. Requiere `uv` (si falta, el script te dice cómo instalarlo). Instala bibsleuth como herramienta de uv (`~/.local/bin/bibsleuth`), fijada a Python 3.12 porque bibsleuth requiere `>=3.12`. Tras la configuración, tanto `bibsleuth` como el script envoltorio del taller están preaprobados en `.claude/settings.json`: no hay peticiones de permiso durante las ejecuciones de los agentes.

El estado de instalación de cada máquina se registra en [`memory/reference_hosts.md`](../../memory/reference_hosts.md).

## Uso diario

```bash
# Produce / refresh the source-of-truth file:
python3 tools/refs-check/check_refs.py PATH/TO/refs.bib

# Custom output path:
python3 tools/refs-check/check_refs.py PATH/TO/refs.bib -o PATH/TO/my-refs.md
```

Por defecto, la salida es `<bib-stem>-refs-checks.md`, junto a la entrada. Así:
- `academic-reviews/schweitzer_rocuts_review/thesis.bib` →
- `academic-reviews/schweitzer_rocuts_review/thesis-refs-checks.md`

## Cómo es el fichero fuente de verdad

```markdown
# Reference verification — `thesis.bib`

**Source:** /path/to/thesis.bib
**Generated:** 2026-05-28T...
**bibsleuth version:** 0.1.3
**Providers consulted:** openalex, semantic_scholar, crossref, arxiv, dblp, pubmed
**Summary:** 47 likely, 3 unverified, 2 verified

> [!info]
> This file is the **source of truth** for reference validation on this document...

---

## [author2023key] — `likely`

**Citation:** Author Names (2023). *Paper Title*. https://doi.org/...

- **Bibsleuth verdict:** `likely` (score 0.78)
- **Entry type:** article
- **DOI:** [10.xxxx/xxxx](https://doi.org/10.xxxx/xxxx)
- **Providers with hits:** crossref, openalex, semantic_scholar (3/6)

**Abstract** (via openalex):

> [first ~300 words of abstract …]

**Cited in paper at:** _(The reviewer: fill in section / page)_
**Claim made:** _(The reviewer: what the reviewed paper says about this reference)_
**Assessment:** _(The reviewer: supported / partially supported / unsupported / claim is generic / no full-text access)_
**Flags:** _(auto-fill: chimeric / year-mismatch / author-mismatch)_

---
```

## Veredictos del revisor: qué significan

El envoltorio calcula un **veredicto del revisor** (Reviewer verdict) sobre la salida de bibsleuth, combinando la triangulación en bases de datos académicas con una comprobación de que la URL está viva (descargar la URL, seguir las redirecciones, comparar el título y el cuerpo de la página con el título citado).

| Veredicto | Significado | Acción |
|---|---|---|
| ✅ `confirmed` | Bibsleuth `verified`/`likely` **o** URL viva + el título o el cuerpo de la página coinciden con el título citado | Se puede entregar |
| ⚠️ `title-mismatch` | La URL existe y la página devuelve 200, pero el título de la página no coincide con el título citado | Revisar: puede ser que el editor haya cambiado el título (OK) o una referencia quimérica (Crítico) |
| 🚫 `unreachable` | La URL devuelve 4xx/5xx/timeout | Enlace roto o invención: encuentra la URL viva o elimina la cita |
| ❓ `escalate` | Sin URL, sin DOI, sin candidatos en las bases de datos académicas | **El principal debe verificarla a mano.** Ningún artículo sale hasta que esta lista esté vacía. |

## Veredictos de bibsleuth: la capa inferior

Bibsleuth, por su parte, devuelve `verified` / `likely` / `unverified`. Estos valores alimentan el veredicto del revisor, pero **no son la última palabra**: en concreto, `verified` para una entrada `@misc` con campo URL solo significa «aquí hay una cadena de URL», no «la URL apunta a una página real». El principal detectó este hueco el 2026-05-28; la capa de comprobación de URL es la solución.

| Veredicto de bibsleuth | Significado en la capa de bases de datos académicas |
|---|---|
| `verified` | Coincidencia de alta confianza en varios proveedores (referencias académicas); O BIEN marcador misc con URL (referencias de literatura gris: hace falta comprobar la URL para una verificación real) |
| `likely` | Coincidencia probable en las bases de datos académicas; algunas discrepancias en los metadatos, pero es el mismo artículo |
| `unverified` | Por debajo del umbral de coincidencia en todos los proveedores. Puede ser un artículo real con metadatos malos, O BIEN una invención. Lo comprueba el principal o el revisor. |

El caso **quimérico** es el sutil: el bib tiene un DOI falso; bibsleuth sigue el DOI y obtiene un artículo real pero distinto. La comparación de títulos del paso de comprobación de URL lo detecta: la URL está viva, pero el título de la página no coincide con el título citado → marca `title-mismatch`.

## La capa de comprobación de URL: qué hace

Para cada entrada del `.bib` con campo `url` (y para la URL resuelta de cada DOI):

1. **Descarga la URL** con un User-Agent de tipo Safari (los editores suelen bloquear los UA por defecto de Python).
2. **Sigue las redirecciones** hasta el límite estándar.
3. **Clasifica la respuesta:**
   - 200 → viva; extrae el título de la página (og:title → `<title>` → primer `<h1>`) y el cuerpo
   - 401/403/429 → bloqueada (muro de pago, antibots, límite de peticiones: la página puede existir; no se puede confirmar)
   - 404/410 → muerta: enlace roto o invención
   - 5xx / timeout / conexión rechazada → inalcanzable
4. **Compara el título citado con el título de la página** mediante una heurística de solapamiento de tokens. Si falla la coincidencia solo por título, busca en el cuerpo de la página (así se cubren los editores que cambian los títulos: p. ej., Khan Academy envuelve el título de la charla TED de Khan en su propia cabecera).
5. **Pasa el resultado al veredicto del revisor.**

El envoltorio espera ~0.3 s entre descargas de URL para ser educado con las API gratuitas y con los servidores de los editores.

## La capa de recomprobación de URL con Playwright: `verify-urls.mjs`

La pasada de URL de `check_refs.py` usa un cliente HTTP simple. Muchos servidores de editores y de blogs (Macmillan, BJET, RIED, theconversation, sitios detrás de Cloudflare) **bloquean como bots a los clientes que no son navegadores** y le devuelven `403`, lo que deja un muro de veredictos `escalate` que en realidad solo significan «a mi descargador lo han rechazado», no «esta referencia es sospechosa». `verify-urls.mjs` es la **capa de escalado**: vuelve a cargar esas URL en un Chromium headless de verdad (User-Agent y cabeceras correctos), que supera sin esfuerzo la mayoría de los bloqueos antibots suaves, y escribe el resultado de vuelta en el `*-refs-checks.md`.

```bash
# Re-check every not-yet-`alive` URL in a refs-checks file (default):
node tools/refs-check/verify-urls.mjs PATH/TO/foo-refs-checks.md

# Preview without writing:
node tools/refs-check/verify-urls.mjs PATH/TO/foo-refs-checks.md --dry

#   --only-blocked   re-check only `blocked` (403) entries, skip `unreachable`
#   --all            re-check every URL block, even ones already `alive`
#   --timeout MS     per-page nav timeout (default 25000)
```

Lee los títulos citados del `.bib` hermano (o de `--bib PATH`), carga cada URL de destino, registra el estado HTTP final + el `<title>` de la página, calcula la coincidencia de títulos por solapamiento de tokens y modifica **solo** el subbloque `**URL check**`, la viñeta `**The reviewer verdict:**`, el veredicto de la cabecera `## [key]` y el resumen agregado. Nunca toca las anotaciones manuales Claim/Assessment.

**El único invariante estricto: la recomprobación solo mejora el veredicto.** La comprobación de URL y la triangulación en bases de datos académicas son ejes de evidencia independientes. Una referencia que ya ha quedado `confirmed` gracias a las bases de datos de bibsleuth **nunca** debe rebajarse a `escalate` solo porque un editor bloquee el navegador como bot. Por eso, ante un `403` o un error de navegación, el script **conserva** el veredicto anterior (y solo actualiza las notas de la comprobación de URL); un `404` claro se muestra como `unreachable`, pero tampoco machaca un `confirmed` por bases de datos. Viva + título coincidente → `confirmed`; viva + título no coincidente → `title-mismatch` (huele a quimera), salvo que la referencia ya estuviera confirmada por las bases de datos. (Este invariante existe porque la primera versión lo hizo mal y rebajó cuatro referencias confirmadas por bases de datos el 2026-05-29; ese arreglo es el motivo de que la regla esté por escrito.)

Un `403` que persiste incluso con el navegador de verdad (normalmente una página intermedia de Cloudflare: `"Just a moment…"` / `"Access Denied"`) significa que la URL está de verdad detrás de un desafío duro: el veredicto se queda como estaba, y una referencia sin evidencia previa se queda en `escalate` para que el principal la confirme a mano.

La configuración la hace `setup.sh` (paso 6: instala en local el paquete npm `playwright` + descarga Chromium). `node_modules/` está en el gitignore; los activos duraderos versionados son `verify-urls.mjs`, `package.json` y `.gitignore`.

## La regla estricta contra las alucinaciones

**Nunca inventes una URL o un DOI para «rellenar» una entrada a la que le faltan metadatos.** Es justo el fallo que todo el sistema existe para evitar. Del mismo encargo:

> *«Lo que es CRÍTICO, y digo CRÍTICO, es que no podemos enviar un artículo con una referencia [no] verificada del todo... intentar publicar con referencias alucinadas es una pérdida de prestigio que no quiero arriesgar.»*

Si una entrada del `.bib` no tiene URL ni DOI en el material de origen, deja el campo vacío. La referencia aparecerá en la sección `❓ Refs to confirm manually` (referencias que hay que confirmar a mano). El principal encuentra la URL correcta; el revisor actualiza el .bib; se vuelve a ejecutar con `--force`.

En el taller original, el revisor (2026-05-28) se pilló a sí mismo inventando una URL de la Comisión Europea de aspecto verosímil mientras extraía el .bib de RIED. La autodetección + la reversión fueron correctas. La lección: **la tentación de «rellenar» una URL que falta es exactamente el fallo.** Resiste.

## La cadena de respaldo para recuperar resúmenes

Bibsleuth no devuelve resúmenes. `check_refs.py` añade:

1. **Semantic Scholar**: el campo de resumen más limpio, sin clave de API, nivel gratuito con límite de peticiones.
2. **OpenAlex**: formato de índice invertido, que el script vuelve a convertir en texto corrido.
3. **Crossref**: XML JATS en el campo `abstract`, sin etiquetas HTML.

Cada referencia dispara de uno a tres GET (gana el primer proveedor que responde). Hay una pausa de 0.4 segundos entre referencias para no pasar de los límites del nivel gratuito.

Si ninguno de los tres proveedores devuelve un resumen (algo habitual con libros, tesis, literatura gris o pósteres de congresos), la entrada muestra «Abstract: not retrievable» y el revisor lo anota de forma explícita en el campo Assessment.

## Reglas de idempotencia

`check_refs.py` analiza las secciones `## [refkey]` del markdown existente antes de escribir. Para cada referencia del .bib:

- **Clave ya presente en el fichero** → se salta. Los campos manuales del revisor (Cited-at, Claim, Assessment, Flags manuales) se conservan.
- **Clave nueva que no está en el fichero** → bibsleuth check + recuperación del resumen + se añade al final.

Es decir: a medida que crece la lista de referencias de un artículo mientras se escribe, vuelves a ejecutar el script y solo se procesan las referencias nuevas. El trabajo de revisión acumulado queda intacto.

## Qué hace el revisor con este fichero

La versión corta del flujo de trabajo del revisor:

1. Extrae el .bib del documento que se revisa (lo ideal es que lo aporte el autor; para los PDF sin fuente, extraído con GROBID).
2. Ejecuta este script → obtienes el `*-refs-checks.md`.
3. Para cada referencia: localiza en el artículo la afirmación que la cita, pégala en **Claim made**, compárala con el **Abstract** y escribe el **Assessment**.
4. Recoge los hallazgos en el documento principal de revisión del revisor (uno por encargo, en `academic-reviews/<engagement>/`). Los problemas de citas se corresponden con la matriz de severidad: **Crítico** para referencias inventadas o quiméricas, **Grave** para citas que no sostienen lo que se afirma, **Pulido** para DOI que faltan o metadatos que no cuadran.

## Limitaciones

- **Todavía no hay extractor de referencias de PDF.** La incorporación a nivel de documento supone una fuente `.bib`. Para los PDF sin fuente: pídesela al autor o ejecuta GROBID por separado (queda en cola como herramienta futura para cuando llegue el primer encargo solo en PDF).
- **Por defecto se usa el modo `--no-llm` de bibsleuth**, por determinismo y por coste. El modo asistido por LLM detecta más citas semánticamente erróneas, pero cuesta llamadas a la API y resta reproducibilidad. Si un encargo crítico justifica la comprobación más profunda, añade `--llm-on` a la invocación del subproceso de bibsleuth (ahora mismo no está expuesto como flag de `check_refs.py`; añadirlo es trivial).
- **Un resumen no es el texto completo.** A partir de un resumen el revisor puede verificar que una afirmación genérica cuadra, pero no una afirmación concreta («el artículo dice X sobre Y», donde X es un detalle enterrado en la página 14). Para esas hace falta el texto completo del artículo que cita o una comprobación manual.

## Relacionado

- [Las reglas del revisor, que hacen obligatoria la verificación de referencias](../../characters/reviewer/rules.md)
- [El modo de trabajo code-as-action](../../memory/feedback_browser_tasks_code_as_action.md): la misma postura aplicada a las tareas de navegador; la verificación de referencias sigue el mismo patrón (herramienta pequeña y dedicada, fichero de salida persistente, reejecuciones idempotentes).
- [El proyecto bibsleuth original](https://github.com/yy/bibsleuth): MIT, en desarrollo activo en marzo de 2026.

---

*Creado el 2026-05-28 en el taller original, para la verificación de referencias del revisor.*
