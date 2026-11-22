Converteix un o més fitxers markdown en PDF a punt per imprimir amb pandoc i el primer motor de PDF disponible a la màquina actual.

## Per què aquesta skill es ramifica

Aquest repositori pot funcionar en més d'una màquina, i les màquines no sempre tenen les mateixes eines de PDF. Una màquina pot tenir **typst**; una altra, **xelatex** de MacTeX; una tercera, camins diferents. Pandoc no recorre a cap alternativa automàticament: si li demanes un motor que no hi és, falla. Per això aquesta skill detecta què hi ha disponible abans d'executar pandoc i fa servir la plantilla d'ordre corresponent.

## Instruccions

1. **Identifica els fitxers markdown que cal convertir** a partir dels arguments de l'usuari. Si no se n'especifica cap, pregunta.

1a. **Identifica el perfil** a partir dels arguments de l'usuari. Hi ha dos perfils (vegeu «Perfils» més avall). Si no se n'especifica cap, fes servir **`default`**. Si l'usuari diu «remarkable» / «tauleta» / «per al meu reMarkable» / «per a E-Ink», fes servir el perfil **`remarkable`**.

2. **Detecta el motor de PDF** en aquest ordre de prioritat, i atura't al primer que trobis:

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

   Si no es troba cap motor, atura't i digues-ho a l'usuari: instal·lar typst o MacTeX és un pas de configuració que només cal fer una vegada. No degradis el resultat en silenci.

3. **Detecta l'arrel del repositori** abans de construir els camins dels fitxers auxiliars:

   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel)
   ```

   Els fitxers auxiliars del perfil `remarkable` són a `$REPO_ROOT/skills/md2pdf-remarkable-meta.yaml` i `$REPO_ROOT/skills/md2pdf-remarkable-header.typ`. Fes servir camins absoluts a totes les ordres de pandoc perquè la skill funcioni sigui quin sigui el directori de treball de l'usuari.

4. **Fes servir la plantilla d'ordre del motor detectat.** Les plantilles canvien segons el motor (dialectes d'opcions) i el perfil (valors visuals de destinació). Tria (motor, perfil) → ordre.

### Plantilla A: Typst (`--pdf-engine=typst`)

**Perfil `default`**: Palatino 11pt, marges de 2,5/3 cm, carta US, URL en color, índex:

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

**Perfil `remarkable`**: Palatino 13pt, marges uniformes d'1,5 cm, A5, enllaços negres, interlineat 1,3, índex.

**Particularitat important.** L'escriptor typst de pandoc genera la variable `margin` com un mapa de typst (`#set page(margin: (...))`), no com a variables escalars separades. Les opcions de línia d'ordres `-V margin-top=…` / `-V margin-left=…` s'ignoren en silenci: tots els resultats tornen al valor per defecte de typst, 2,5 cm. La solució és passar els marges amb `--metadata-file` apuntant a `skills/md2pdf-remarkable-meta.yaml`, que construeix el mapa correcte. No dupliquis els valors de marge a la línia d'ordres de pandoc: el yaml és l'única font de veritat per a la geometria.

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

Els dos fitxers auxiliars es reparteixen la feina: `md2pdf-remarkable-meta.yaml` porta la geometria de la pàgina (el mapa que necessita l'escriptor typst de pandoc); `md2pdf-remarkable-header.typ` porta les mides dels elements (taules a 10pt, peus de figura a 10pt, correcció de les taules divisibles). Edita aquests fitxers directament per ajustar el perfil; no toquis la plantilla d'ordre.

### Plantilla B: xelatex o lualatex

**Perfil `default`**: Palatino 11pt, marges de 2,5 cm, carta US, URL en color, índex:

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

**Perfil `remarkable`**: Palatino 13pt, marges uniformes d'1,5 cm, A5, enllaços negres, interlineat 1,3:

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

Notes sobre les diferències entre la plantilla A i la plantilla B:
- Typst vol `papersize=us-letter`; xelatex vol `papersize=letter` / `papersize=a5paper`.
- L'error dels marges de typst (opcions `-V margin-*` ignorades en silenci) no afecta xelatex: pots passar directament les quatre opcions de geometria separades.
- xelatex necessita `PATH` amb `/Library/TeX/texbin` al davant quan MacTeX està instal·lat allà i no és al PATH per defecte del shell. És la configuració de MacTeX més habitual a macOS.

### Plantilla C: pdflatex (últim recurs)

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

**Pdflatex no fa servir les fonts del sistema**: té el seu propi catàleg de fonts i no pot carregar Palatino del sistema operatiu. El resultat surt per defecte en Computer Modern. Digues-ho explícitament a l'usuari quan recorris a aquesta plantilla. Per al perfil `remarkable` amb pdflatex, fes servir `papersize=a5paper`, `fontsize=12pt` (pdflatex arriba com a màxim a 12pt amb la classe estàndard `article`), opcions `geometry:` separades per als marges uniformes d'1,5 cm, i `-V linestretch=1.3`.

## Perfils

### Perfil `default`: impressió estàndard
- **Objectiu:** un lliurable imprès (capítol, article, material de classe) vist en paper carta/A4 o en pantalla al 100% de zoom.
- **Valors:** carta US, Palatino 11pt, marges de 2,5 a 3 cm, URL en color (blau), índex.
- **Quan fer-lo servir:** el perfil per defecte per a gairebé tot.

### Perfil `remarkable`: tauleta E-Ink (reMarkable o similar ≤ 12")
- **Objectiu:** que es pugui llegir en una tauleta E-Ink sense fer zoom.
- **Valors:** A5, Palatino 13pt, Menlo 11pt per al codi, marges uniformes d'1,5 cm, interlineat 1,3, enllaços negres (sense color: la tinta electrònica mostra els enllaços blaus com un gris il·legible), índex.
- **Per què A5 + 13pt:** el reMarkable escala les pàgines a l'amplada de l'àrea visible. La carta US s'escala al ~58%, i un text de 11pt es llegeix com si fos de ~6,4pt: per això cal fer zoom. L'A5 s'escala al ~85%, i un text de 13pt es llegeix com si fos de ~11pt, la mateixa mida efectiva que un llibre imprès.
- **Quan fer-lo servir:** quan l'usuari demana explícitament el perfil reMarkable / tauleta / E-Ink.
- **Contrapartides:** més pàgines que el perfil per defecte (pàgina més petita, densitat de contingut semblant). Acceptable en una tauleta; no per imprimir en paper.

### Afegir un perfil nou

Afegeix-lo aquí amb: objectiu, valors, per què aquests números, quan fer-lo servir, contrapartides. Afegeix els valors específics a cada plantilla de motor. Actualitza la secció «Requisits» si un perfil nou necessita una dependència nova.

5. **El PDF de sortida va al mateix directori que el fitxer d'entrada**, amb el mateix nom però extensió `.pdf`. Posa entre cometes els camins que continguin espais. **Si es fa servir un perfil que no és el per defecte, afegeix el nom del perfil com a sufix al nom del fitxer de sortida** per no sobreescriure res: per exemple, `my-chapter.md` → `my-chapter.remarkable.pdf`. El perfil per defecte genera simplement `<name>.pdf`.

6. **Després de generar-lo, executa `pdfinfo`** sobre la sortida per confirmar el nombre de pàgines i la mida del fitxer, i informa l'usuari de:
   - Quin motor s'ha fet servir (i el camí complet on s'ha trobat)
   - Quin perfil s'ha fet servir
   - Nombre de pàgines i mida del fitxer
   - Mida de pàgina (confirma A5 o carta, segons el previst)
   - Qualsevol diferència visual respecte de l'objectiu (només rellevant si s'ha fet servir la plantilla C)

7. **Mou els PDF remarkable a `TO-READ/`.** Després del pas 6, mou el `.remarkable.pdf` a la carpeta `TO-READ/` de l'arrel del repositori:

   ```bash
   mkdir -p "$REPO_ROOT/TO-READ"
   mv "PATH/TO/<name>.remarkable.pdf" "$REPO_ROOT/TO-READ/<name>.remarkable.pdf"
   ```

   `TO-READ/` és una zona d'espera per a la lectura a la tauleta: arrossega els fitxers des d'allà a l'aplicació d'escriptori que sincronitza la teva tauleta. La carpeta està versionada, però git n'ignora el contingut (afegeix `TO-READ/*.pdf` a `.gitignore` si encara no hi és). El perfil per defecte es queda al costat de la font; només la variant remarkable es mou a `TO-READ/`.

## Configuracions de màquina conegudes

Omple aquesta taula a mesura que facis servir la skill a cada màquina. Actualitza les files en lloc d'afegir-ne.

| Nom de màquina | pandoc | typst | xelatex / MacTeX | Plantilla que cal fer servir | Última verificació |
|---|---|---|---|---|---|
| *(afegeix aquí el nom de la teva màquina)* | | | | | |

Executa `hostname` al shell per obtenir el nom de la teva màquina.

## Requisits

- **pandoc** (obligatori a totes les màquines)
- **Com a mínim un d'aquests:** typst, xelatex, lualatex o pdflatex

Si falta pandoc, atura't i digues-ho a l'usuari. Si no hi ha cap motor de PDF, suggereix instal·lar typst (més lleuger, més ràpid, valors per defecte més nets) o MacTeX (més pesat, però resol més casos límit).

$ARGUMENTS
