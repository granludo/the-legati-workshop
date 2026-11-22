Convierte uno o varios ficheros markdown en PDF listos para imprimir con pandoc y el primer motor PDF disponible en la máquina actual.

## Por qué esta skill se ramifica

Este repositorio puede funcionar en más de una máquina, y no todas tienen la misma cadena de herramientas para PDF. Una máquina puede tener **typst**; otra, **xelatex** de MacTeX; una tercera, rutas distintas. Pandoc no recurre a una alternativa por su cuenta: si le pides un motor que no está, da error. Por eso esta skill detecta qué hay disponible antes de ejecutar pandoc y usa la plantilla de comando correspondiente.

## Instrucciones

1. **Identifica el fichero o los ficheros markdown que hay que convertir** a partir de los argumentos del usuario. Si no se indica ninguno, pregunta.

1a. **Identifica el perfil** a partir de los argumentos del usuario. Hay dos perfiles (véase «Perfiles» más abajo). Si no se indica ninguno, usa **`default`**. Si el usuario dice «remarkable» / «tablet» / «para mi reMarkable» / «para E-Ink», usa el perfil **`remarkable`**.

2. **Detecta el motor PDF** en este orden de prioridad y detente en el primero que encuentres:

   ```bash
   # Typst — check homebrew, usr/local, cargo, then PATH
   [ -x /opt/homebrew/bin/typst ] && echo "typst:/opt/homebrew/bin/typst" && exit 0
   [ -x /usr/local/bin/typst ] && echo "typst:/usr/local/bin/typst" && exit 0
   [ -x "$HOME/.cargo/bin/typst" ] && echo "typst:$HOME/.cargo/bin/typst" && exit 0
   which typst >/dev/null 2>&1 && echo "typst:$(which typst)" && exit 0

   # xelatex — check MacTeX, then PATH
   [ -x /Library/TeX/texbin/xelatex ] && echo "xelatex:/Library/TeX/texbin/xelatex" && exit 0
   which xelatex >/dev/null 2>&1 && echo "xelatex:$(which xelatex)" && exit 0

   # lualatex — same paths
   [ -x /Library/TeX/texbin/lualatex ] && echo "lualatex:/Library/TeX/texbin/lualatex" && exit 0
   which lualatex >/dev/null 2>&1 && echo "lualatex:$(which lualatex)" && exit 0

   # pdflatex — last resort, cannot use system fonts
   [ -x /Library/TeX/texbin/pdflatex ] && echo "pdflatex:/Library/TeX/texbin/pdflatex" && exit 0
   which pdflatex >/dev/null 2>&1 && echo "pdflatex:$(which pdflatex)" && exit 0

   echo "none" && exit 1
   ```

   Si no encuentras ningún motor, detente y díselo al usuario: instalar typst o MacTeX es un paso de configuración que se hace una sola vez. No degrades el resultado en silencio.

3. **Detecta la raíz del repositorio** antes de construir las rutas de los ficheros auxiliares:

   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel)
   ```

   Los ficheros auxiliares del perfil `remarkable` están en `$REPO_ROOT/skills/md2pdf-remarkable-meta.yaml` y `$REPO_ROOT/skills/md2pdf-remarkable-header.typ`. Usa rutas absolutas en todos los comandos de pandoc para que la skill funcione sea cual sea el directorio de trabajo del usuario.

4. **Usa la plantilla de comando del motor detectado.** Las plantillas cambian según el motor (dialectos de flags) y el perfil (valores visuales objetivo). Elige (motor, perfil) → comando.

### Plantilla A: Typst (`--pdf-engine=typst`)

**Perfil `default`**: Palatino 11pt, márgenes de 2.5/3cm, US letter, URL en color, índice (TOC):

```bash
pandoc INPUT.md \
  -o OUTPUT.pdf \
  --pdf-engine=typst \
  -V mainfont="Palatino" \
  -V sansfont="Palatino" \
  -V monofont="Menlo" \
  -V fontsize=11pt \
  -V papersize=us-letter \
  -V margin-top=2.5cm \
  -V margin-bottom=2.5cm \
  -V margin-left=3cm \
  -V margin-right=3cm \
  --toc
```

**Perfil `remarkable`**: Palatino 13pt, márgenes uniformes de 1.5cm, A5, enlaces en negro, interlineado 1.3, índice (TOC).

**Una rareza importante.** El writer de typst de pandoc genera la variable `margin` como un mapa de typst (`#set page(margin: (...))`), no como variables escalares separadas. Los flags de línea de comandos `-V margin-top=…` / `-V margin-left=…` se ignoran en silencio: todos los renderizados vuelven al valor por defecto de typst, 2.5cm. La solución es pasar los márgenes con `--metadata-file` apuntando a `skills/md2pdf-remarkable-meta.yaml`, que construye el mapa correcto. No dupliques los valores de margen en la línea de comandos de pandoc: el yaml es la única fuente de verdad de la geometría.

```bash
pandoc INPUT.md \
  -o OUTPUT.pdf \
  --pdf-engine=typst \
  --metadata-file="$REPO_ROOT/skills/md2pdf-remarkable-meta.yaml" \
  --include-in-header="$REPO_ROOT/skills/md2pdf-remarkable-header.typ" \
  -V mainfont="Palatino" \
  -V sansfont="Palatino" \
  -V monofont="Menlo" \
  -V fontsize=13pt \
  -V papersize=a5 \
  -V linestretch=1.3 \
  --toc
```

Los dos ficheros auxiliares se reparten el trabajo: `md2pdf-remarkable-meta.yaml` lleva la geometría de página (el mapa que necesita el writer de typst de pandoc); `md2pdf-remarkable-header.typ` lleva los ajustes de tamaño de los elementos (tablas a 10pt, pies de figura a 10pt, el arreglo para que las tablas puedan partirse entre páginas). Edita esos ficheros directamente para afinar el perfil; no cambies la plantilla de comando.

### Plantilla B: xelatex o lualatex

**Perfil `default`**: Palatino 11pt, márgenes de 2.5cm, US letter, URL en color, índice (TOC):

```bash
PATH="/Library/TeX/texbin:$PATH" pandoc INPUT.md \
  -o OUTPUT.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Palatino" \
  -V sansfont="Palatino" \
  -V monofont="Menlo" \
  -V fontsize=11pt \
  -V papersize=letter \
  -V geometry:margin=2.5cm \
  -V colorlinks=true \
  -V linkcolor=black \
  -V urlcolor=blue \
  --toc
```

**Perfil `remarkable`**: Palatino 13pt, márgenes uniformes de 1.5cm, A5, enlaces en negro, interlineado 1.3:

```bash
PATH="/Library/TeX/texbin:$PATH" pandoc INPUT.md \
  -o OUTPUT.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Palatino" \
  -V sansfont="Palatino" \
  -V monofont="Menlo" \
  -V fontsize=13pt \
  -V papersize=a5paper \
  -V geometry:top=1.5cm \
  -V geometry:bottom=1.5cm \
  -V geometry:left=1.5cm \
  -V geometry:right=1.5cm \
  -V linestretch=1.3 \
  -V colorlinks=true \
  -V linkcolor=black \
  -V urlcolor=black \
  --toc
```

Diferencias entre la plantilla A y la plantilla B:
- Typst quiere `papersize=us-letter`; xelatex quiere `papersize=letter` / `papersize=a5paper`.
- El fallo de márgenes de typst (los flags `-V margin-*` ignorados en silencio) no afecta a xelatex: puedes pasar directamente los cuatro flags de geometría por separado.
- xelatex necesita anteponer `/Library/TeX/texbin` al `PATH` cuando MacTeX está instalado ahí y no en el PATH por defecto del shell. Es la configuración más habitual de MacTeX en macOS.

### Plantilla C: pdflatex (último recurso)

```bash
PATH="/Library/TeX/texbin:$PATH" pandoc INPUT.md \
  -o OUTPUT.pdf \
  --pdf-engine=pdflatex \
  -V fontsize=11pt \
  -V papersize=letter \
  -V geometry:margin=2.5cm \
  -V colorlinks=true \
  -V linkcolor=black \
  -V urlcolor=blue \
  --toc
```

**Pdflatex no usa las fuentes del sistema**: usa su propio catálogo de fuentes y no puede cargar la Palatino del sistema operativo. La salida usa por defecto Computer Modern. Díselo explícitamente al usuario cuando recurras a esta plantilla. Para el perfil `remarkable` con pdflatex, usa `papersize=a5paper`, `fontsize=12pt` (con la clase estándar `article`, pdflatex llega como máximo a 12pt), flags `geometry:` separados para márgenes uniformes de 1.5cm y `-V linestretch=1.3`.

## Perfiles

### Perfil `default`: impresión estándar
- **Objetivo:** un entregable impreso (capítulo, artículo, material de clase) que se lee en papel carta/A4 o en pantalla al 100% de zoom.
- **Valores:** US letter, Palatino 11pt, márgenes de 2.5–3cm, URL en color (azul), índice (TOC).
- **Cuándo usarlo:** el perfil por defecto para casi todo.

### Perfil `remarkable`: tableta E-Ink (reMarkable o similar ≤ 12")
- **Objetivo:** que se lea en una tableta E-Ink sin hacer zoom.
- **Valores:** A5, Palatino 13pt, Menlo 11pt para el código, márgenes uniformes de 1.5cm, interlineado 1.3, enlaces en negro (sin color: la tinta electrónica muestra los enlaces azules como un gris ilegible), índice (TOC).
- **Por qué A5 + 13pt:** la reMarkable escala las páginas ajustándolas al ancho de su área visible. US letter queda al ~58%, así que un texto de 11pt se lee a ~6.4pt: por eso hay que hacer zoom. A5 queda al ~85%, así que un texto de 13pt se lee a ~11pt, el mismo tamaño efectivo que un libro impreso.
- **Cuándo usarlo:** cuando el usuario pide explícitamente el perfil reMarkable / tableta / E-Ink.
- **Contrapartidas:** más páginas que con el perfil por defecto (página más pequeña, densidad de contenido parecida). Aceptable en una tableta; no para imprimir en papel.

### Añadir un perfil nuevo

Añádelo aquí con: objetivo, valores, por qué esos números, cuándo usarlo, contrapartidas. Añade los valores que cambian en cada plantilla de motor. Actualiza la sección «Requisitos» si el perfil nuevo necesita una dependencia nueva.

5. **El PDF de salida va en el mismo directorio que el fichero de entrada**, con el mismo nombre y la extensión `.pdf`. Pon entre comillas las rutas que contengan espacios. **Si se usa un perfil distinto del de por defecto, añade su nombre como sufijo al nombre del fichero de salida** para no sobrescribir nada: p. ej., `my-chapter.md` → `my-chapter.remarkable.pdf`. El perfil por defecto genera simplemente `<name>.pdf`.

6. **Después de generarlo, ejecuta `pdfinfo`** sobre la salida para confirmar el número de páginas y el tamaño del fichero, e informa al usuario de:
   - Qué motor se ha usado (y la ruta completa donde se ha encontrado)
   - Qué perfil se ha usado
   - El número de páginas y el tamaño del fichero
   - El tamaño de página (confirma A5 o carta, según lo esperado)
   - Cualquier diferencia visual respecto al objetivo (solo relevante si se ha usado la plantilla C)

7. **Mueve los PDF remarkable a `TO-READ/`.** Tras el paso 6, mueve el `.remarkable.pdf` a la carpeta `TO-READ/` de la raíz del repositorio:

   ```bash
   mkdir -p "$REPO_ROOT/TO-READ"
   mv "PATH/TO/<name>.remarkable.pdf" "$REPO_ROOT/TO-READ/<name>.remarkable.pdf"
   ```

   `TO-READ/` es una zona de espera para la lectura en tableta: arrastra los ficheros desde ahí a la aplicación de sincronización de escritorio de tu tableta. La carpeta está versionada, pero su contenido está en el gitignore (añade `TO-READ/*.pdf` a `.gitignore` si aún no está). El PDF del perfil por defecto se queda junto a la fuente; solo la variante remarkable se mueve a `TO-READ/`.

## Configuraciones de máquina conocidas

Rellena esta tabla a medida que ejecutes la skill en cada máquina. Actualiza en lugar de añadir.

| Hostname | pandoc | typst | xelatex / MacTeX | Plantilla que usar | Última verificación |
|---|---|---|---|---|---|
| *(añade aquí tu hostname)* | | | | | |

Ejecuta `hostname` en el shell para obtener el nombre de tu máquina.

## Requisitos

- **pandoc** (obligatorio en todas las máquinas)
- **Al menos uno de:** typst, xelatex, lualatex o pdflatex

Si falta pandoc, detente y díselo al usuario. Si no hay ningún motor PDF, sugiere instalar typst (más ligero, más rápido, valores por defecto más limpios) o MacTeX (más pesado, pero resuelve más casos límite).

$ARGUMENTS
