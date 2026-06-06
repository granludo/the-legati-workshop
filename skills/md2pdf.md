Convert one or more markdown files to print-ready academic-style PDFs using pandoc and the first available PDF engine on the current machine.

## Why this skill branches

This repo runs on more than one Mac, and the machines do not have the same PDF toolchain. One machine has **typst** at `/opt/homebrew/bin/typst`; another has **xelatex** from MacTeX at `/Library/TeX/texbin/xelatex` with no typst. A third machine might have different paths again. Pandoc does not fall back automatically — if you ask it for a missing engine it errors out. So this skill detects what is actually available before running pandoc, and uses the matching command template.

## Instructions

1. **Identify the markdown file(s) to convert** from the user's arguments. If no file is specified, ask.

1a. **Identify the profile** from the user's arguments. Two profiles exist (see "Profiles" below). If no profile is specified, use **`default`**. If the user says "remarkable" / "tablet" / "for my reMarkable", use the **`remarkable`** profile.

2. **Detect the PDF engine** in this priority order — stop at the first one found:

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

   If no engine is found, stop and tell the user — installing typst or MacTeX is a one-time setup step, not something this skill should work around. Do not silently degrade.

3. **Use the command template for the detected engine.** The templates differ between engines (flag-name dialects); they also differ between profiles (visual target values). Pick (engine, profile) → command.

### Template A — Typst (`--pdf-engine=typst`)

**Profile `default`** — Palatino 11pt, 2.5/3cm margins, US letter, coloured URLs, TOC:

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

**Profile `remarkable`** — Palatino 13pt body / 10pt tables + figure captions, **1.5cm uniform margins**, A5, no link colour, line stretch 1.3, TOC. *(Earlier on 2026-05-25 we briefly ran an asymmetric 1.5/0.75cm configuration after Marc noted excessive side whitespace; after reading the rendered PDF on the device with the now-correctly-applied measurements, Marc settled back on 1.5cm uniform as the comfortable reading width. Margin discipline lives in `md2pdf-remarkable-meta.yaml`; update there if Marc revises again.)*

**Important quirk discovered 2026-05-25.** Pandoc's typst writer renders the `margin` variable as a *typst map* (`#set page(margin: (...))`), not as separate scalar variables. The CLI `-V margin-top=…` / `-V margin-left=…` flags are silently ignored — every render falls back to typst's 2.5cm default. The supported workaround is to pass margins via `--metadata-file` pointing at a YAML that constructs the map. The sibling file `skills/md2pdf-remarkable-meta.yaml` is that YAML and is loaded below; do not duplicate margin values in the pandoc command line.

```bash
pandoc INPUT.md \
  -o OUTPUT.pdf \
  --pdf-engine=typst \
  --metadata-file=/Users/granludo/Documents/ludo-claude/ludo-writting-workshop/skills/md2pdf-remarkable-meta.yaml \
  --include-in-header=/Users/granludo/Documents/ludo-claude/ludo-writting-workshop/skills/md2pdf-remarkable-header.typ \
  -V mainfont="Palatino" \
  -V sansfont="Palatino" \
  -V monofont="Menlo" \
  -V fontsize=13pt \
  -V papersize=a5 \
  -V linestretch=1.3 \
  --toc
```

The two sidecar files split the responsibilities cleanly: `md2pdf-remarkable-meta.yaml` carries the page geometry (the map-shaped variable pandoc's typst writer needs), and `md2pdf-remarkable-header.typ` carries the element-size overrides (tables 10pt, figure captions 10pt, breakable-table fix). Margins live in the yaml; font sizes live in the typ; don't cross them.

The `md2pdf-remarkable-header.typ` file sits next to this skill and holds Typst `show` rules for element-specific font sizes (tables 10pt, figure captions 10pt — body stays at 13pt). Edit that file to tune element sizes without touching the skill body. The path in the command above is **absolute** so the include resolves regardless of the user's cwd when the skill runs; update the path if the workshop repo moves.

**Profile `bsc-course`** — `default` geometry plus the per-page license footer. Add `--include-in-header` pointing at the footer sidecar; drop `--toc` for short exercises:

```bash
pandoc INPUT.md \
  -o OUTPUT.pdf \
  --pdf-engine=typst \
  --include-in-header=/Users/granludo/Documents/ludo-claude/ludo-writting-workshop/skills/md2pdf-bsc-course-footer.typ \
  -V mainfont="Palatino" \
  -V sansfont="Palatino" \
  -V monofont="Menlo" \
  -V fontsize=11pt \
  -V papersize=us-letter \
  -V margin-top=2.5cm \
  -V margin-bottom=2.5cm \
  -V margin-left=3cm \
  -V margin-right=3cm
```

Verified 2026-06-06 on `tom-nook-studio.local` (typst): the footer renders on every page (license block full width, `N / total` page number below it). The footer text/author line is edited in `md2pdf-bsc-course-footer.typ`, not here.

### Template B — xelatex or lualatex (`--pdf-engine=xelatex` or `=lualatex`)

**Profile `default`** — Palatino 11pt, 2.5cm margins, US letter, coloured URLs, TOC:

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

**Profile `remarkable`** — Palatino 13pt, 1.5cm top/bottom + **0.75cm left/right** margins (asymmetric), A5, links black (E-Ink), line stretch 1.3, TOC. The asymmetric geometry under xelatex needs split flags (the single `geometry:margin=X` form sets all four sides uniformly and cannot express the asymmetry):

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
  -V geometry:left=0.75cm \
  -V geometry:right=0.75cm \
  -V linestretch=1.3 \
  -V colorlinks=true \
  -V linkcolor=black \
  -V urlcolor=black \
  --toc
```

Differences from Template A to be aware of:
- Typst wants `papersize=us-letter`; xelatex wants `papersize=letter`.
- Typst takes four separate `margin-top/bottom/left/right` variables; xelatex uses a single `geometry:margin=X`. To get the 3cm left/right + 2.5cm top/bottom of the Typst template under xelatex, use `-V geometry:"margin=2.5cm 3cm"` or split: `-V geometry:top=2.5cm -V geometry:bottom=2.5cm -V geometry:left=3cm -V geometry:right=3cm`. A single 2.5cm uniform margin is close enough for most academic prints — use it unless the user asks for the asymmetric margins.
- xelatex needs `PATH` prepended with `/Library/TeX/texbin` when MacTeX is installed there and not on the default shell PATH. This is the most common macOS MacTeX setup.
- Both templates support `--toc` (table of contents) and `colorlinks`. Include them by default; the user can tell you to drop them for a short document.

### Template C — pdflatex (last-resort fallback)

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

**Pdflatex does not use system fonts** — it uses its own font catalogue and cannot load Palatino from the OS. The output will default to Computer Modern. Tell the user explicitly when you fall back to this template so they know why the visual result differs from the other two. For the **`remarkable`** profile under pdflatex, swap `papersize=letter` → `papersize=a5paper`, `fontsize=11pt` → `fontsize=12pt` (pdflatex caps body text at 12pt for standard `article` class; 13pt requires `extarticle` or other class), the single `geometry:margin=2.5cm` → split asymmetric flags `geometry:top=1.5cm geometry:bottom=1.5cm geometry:left=0.75cm geometry:right=0.75cm`, and add `-V linestretch=1.3`.

## Profiles

A **profile** is a named bundle of visual-target settings (paper size, font size, margins, link colour, line stretch). The profile is engine-agnostic; the engine-specific templates above implement each profile's values in the appropriate flag dialect.

### Profile `default` — academic print
- **Target:** A printed academic deliverable (chapter, paper, talk handout) viewed on letter or A4 paper.
- **Values:** US letter, Palatino 11pt, 2.5–3cm margins, coloured URLs (blue), TOC.
- **When to use:** the default. Marc's chapter v4s, papers, lecture references for print, anything destined for a paper printer or for on-screen reading at 100% zoom.

### Profile `remarkable` — reMarkable tablet (or any E-Ink ≤ 12")
- **Target:** Readable on Marc's reMarkable without zooming. Effective on-screen text size matches a normal book at arm's length.
- **Values:** A5 (148×210mm), Palatino 13pt, Menlo 11pt for code, **1.5cm uniform margins**, line stretch 1.3, black links (no colour — E-Ink turns blue links into illegible grey), TOC.
- **Why these numbers:** the reMarkable scales pages width-fit to its ~12.6cm visible area. US letter scales to ~58% → 11pt source ≈ 6.4pt on screen (why zoom is needed). A5 scales to ~85% → 13pt source ≈ 11pt on screen — same effective letterform as a printed book. 1.5cm uniform margins translate to ~1.27cm on screen after width-fit scaling, which Marc verified as comfortable reading width on the device. Line stretch is bumped because E-Ink refresh artifacts make tight leading harder to read.
- **When to use:** Marc explicitly asks for the reMarkable / tablet / "for reading" profile. The default profile is wrong for tablet reading — text comes out tiny.
- **Trade-offs:** more pages than the default profile (smaller page, similar content density). Acceptable on a tablet where flipping is free; not acceptable for paper print (use `default`).
- **History (2026-05-25):** the rule went through three positions in one day — (1) original 1.5cm uniform per the skill template, but the `-V margin-*` flags silently ignored and renders defaulted to typst's 2.5cm; (2) Marc asked to halve side margins after the v2 RIED PDF visibly had too much whitespace; we shipped 0.75cm side margins via the now-corrected metadata-file pipeline and rendered at 67 pages; (3) reading on the device with accurate measurements, Marc reverted to 1.5cm uniform as the comfortable reading width. The technical fix (metadata-file path) is what stuck; the parametric value cycled back to 1.5cm.

### Profile `bsc-course` — BSC Agents Course materials (license-footered)
- **Target:** any student-facing PDF for the **BSC Agents Course** (exercises, lecture notes, the pre-course package). Same print geometry as `default`, **plus a per-page copyright + CC BY-NC-SA 4.0 footer** on every page.
- **Why:** the course materials are Marc's intellectual property and have been republished as someone else's work before. Every page must carry authorship + the non-commercial / share-alike / attribution license, so the material cannot be cropped, re-badged, and passed off. The license is the legal protection; the footer makes it travel with the document.
- **Values:** identical to `default` (US letter, Palatino 11pt, 2.5–3cm margins) plus a Typst footer injected from `skills/md2pdf-bsc-course-footer.typ`. The author line / year lives in that one file — edit it there and every course PDF inherits the change.
- **When to use:** **every** PDF rendered from anything under `writting-projects/BSC-AGENTS-COURSE/`. This is the default profile for that folder, not an option.
- **TOC:** drop `--toc` for short documents (most exercises are 1–3 pages); keep it for lecture notes.
- **Engine note:** the footer is verified on the **Typst** engine (the command below). On **xelatex** hosts, use the sibling `skills/md2pdf-bsc-course-footer.tex` via `--include-in-header` instead (fancyhdr-based; verify the long footer line wraps before shipping — not yet checked on a MacTeX host).

### Adding a new profile

If Marc asks for another profile (e.g. `slides`, `mobile`, `large-print`), add it as a sibling here with the same shape: target, values, why-these-numbers, when-to-use, trade-offs. Then add the value overrides under each engine template. Do not duplicate the entire pandoc command — add only the deltas. Update the "Requirements" section if a new profile needs a new dependency.

4. **The output PDF goes in the same directory as the input file**, with the same name but `.pdf` extension. Quote file paths containing spaces (e.g. `cap03-el-miratge-de-la-deteccio.en -v2.md`) in both the input and output arguments. **If a non-default profile is used, suffix the output filename with the profile name** to avoid clobbering: e.g. `lecture-2026-05-20-notes.md` → `lecture-2026-05-20-notes.remarkable.pdf`. The default profile renders to plain `<name>.pdf`.

5. **After generating, run `pdfinfo`** on the output to confirm page count and file size, and report to the user:
   - Which engine was used (and the full path where it was found)
   - Which profile was used (`default` or `remarkable`)
   - Page count
   - File size
   - Page size (confirm A5 vs letter as expected for the profile)
   - Any visual-result differences from the target (relevant only if Template C was used)

6. **Move the PDF to `TO-READ/` (`remarkable` profile only).** After step 5, move the rendered `<name>.remarkable.pdf` from its build directory to the repo root's `TO-READ/` folder:

   ```bash
   mv "<build-dir>/<name>.remarkable.pdf" \
      "/Users/granludo/Documents/ludo-claude/ludo-writting-workshop/TO-READ/<name>.remarkable.pdf"
   ```

   `TO-READ/` is the staging area for tablet reading. The folder is tracked (via its own `.gitignore`); its contents are gitignored, so PDFs accumulate per host without entering git history. Marc drags from `TO-READ/` into the reMarkable Desktop app (or whatever future sync target replaces the drag-drop step) to deliver to the tablet.

   **Why move rather than copy:** the `.remarkable.pdf` is a tablet-bound artifact, not an archival deliverable. The source `.md` is the canonical version; the default-profile `.pdf` (when it exists) is the archival print version. The remarkable variant has only one purpose — read it on the tablet — so it belongs in the staging folder, not next to the source.

   **Re-rendering** overwrites the file in `TO-READ/`. `mv` on macOS overwrites silently by default; this is the desired behaviour (the most recent render is the one that should be on the tablet).

   **Profile-conditional:** the `default` profile produces print-targeted PDFs that stay next to the source. Only `remarkable` moves to `TO-READ/`. If the host changes or the workshop repo path changes, update the absolute path in the `mv` command above.

   **Reporting:** after the move, the report to the user should state the final location is `TO-READ/<name>.remarkable.pdf`, not the build directory.

   *Historical note: an earlier version of this step used `open -a reMarkable <pdf>` to trigger an auto-upload via the desktop app. Verified 2026-05-22 that this opens the PDF in the app's local reader but does NOT push it to the user's cloud library, so the tablet never receives the file. The `TO-READ/` drop-folder convention replaces it. The `rmapi` (`ddvk/rmapi`) community CLI is the path to real automation if Marc later wants the drag-drop step itself automated; that requires a third-party install + a one-time OAuth-style ceremony against `my.remarkable.com`.*

## Known machine configurations

Living data — update this section when the skill runs on a new machine or when a machine's toolchain changes.

| Hostname | pandoc | typst | xelatex / MacTeX | Template to use | Last verified |
|---|---|---|---|---|---|
| `Ludos-MBP-M3-3.local` (MBP M3, macOS 26.3.1) | `/opt/homebrew/bin/pandoc` | **absent** | `/Library/TeX/texbin/xelatex` (MacTeX installed) | **B — xelatex** | 2026-04-14 |
| `tom-nook-studio.local` (Mac Studio, tom-nook) | `/opt/homebrew/bin/pandoc` | `/opt/homebrew/bin/typst` | **absent** | **A — typst** | 2026-05-20 |

Record the hostname (`hostname` at the shell) alongside the verification date so future sessions can identify which machine they are on without guessing. If the engine inventory changes on a machine, update the table rather than the skill body — the templates do not change, only the routing does.

## Requirements

- **pandoc** (required on every machine)
- **At least one of:** typst, xelatex, lualatex, or pdflatex

If pandoc is missing, stop and tell the user — that is a prerequisite, not a fallback case. If no PDF engine is present, tell the user and stop; suggest installing either typst (lighter, faster, cleaner defaults) or MacTeX (heavier but handles more edge cases).

$ARGUMENTS
