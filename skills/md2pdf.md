Convert one or more markdown files to print-ready PDFs using pandoc and the first available PDF engine on the current machine.

## Why this skill branches

This repo can run on more than one machine, and machines do not always have the same PDF toolchain. One machine may have **typst**; another may have **xelatex** from MacTeX; a third may have different paths. Pandoc does not fall back automatically — if you ask it for a missing engine it errors out. So this skill detects what is available before running pandoc, and uses the matching command template.

## Instructions

1. **Identify the markdown file(s) to convert** from the user's arguments. If no file is specified, ask.

1a. **Identify the profile** from the user's arguments. Two profiles exist (see "Profiles" below). If no profile is specified, use **`default`**. If the user says "remarkable" / "tablet" / "for my reMarkable" / "for E-Ink", use the **`remarkable`** profile.

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

   If no engine is found, stop and tell the user — installing typst or MacTeX is a one-time setup step. Do not silently degrade.

3. **Detect the repo root** before building sidecar paths:

   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel)
   ```

   Sidecar files for the `remarkable` profile live at `$REPO_ROOT/skills/md2pdf-remarkable-meta.yaml` and `$REPO_ROOT/skills/md2pdf-remarkable-header.typ`. Use absolute paths in every pandoc command so the skill works regardless of the user's current working directory.

4. **Use the command template for the detected engine.** Templates differ between engines (flag dialects) and profiles (visual target values). Pick (engine, profile) → command.

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

**Profile `remarkable`** — Palatino 13pt, 1.5cm uniform margins, A5, black links, line stretch 1.3, TOC.

**Important quirk.** Pandoc's typst writer renders the `margin` variable as a typst map (`#set page(margin: (...))`), not as separate scalar variables. The CLI `-V margin-top=…` / `-V margin-left=…` flags are silently ignored — every render falls back to typst's 2.5cm default. The fix is to pass margins via `--metadata-file` pointing at `skills/md2pdf-remarkable-meta.yaml`, which constructs the correct map. Do not duplicate margin values on the pandoc command line — the yaml is the single source of truth for geometry.

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

The two sidecar files split responsibilities: `md2pdf-remarkable-meta.yaml` carries page geometry (the map pandoc's typst writer needs); `md2pdf-remarkable-header.typ` carries element-size overrides (tables 10pt, figure captions 10pt, breakable-table fix). Edit those files directly to tune the profile — don't change the command template.

### Template B — xelatex or lualatex

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

**Profile `remarkable`** — Palatino 13pt, 1.5cm uniform margins, A5, black links, line stretch 1.3:

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

Notes on Template A vs Template B differences:
- Typst wants `papersize=us-letter`; xelatex wants `papersize=letter` / `papersize=a5paper`.
- Typst's margin bug (silently ignored `-V margin-*` flags) does not affect xelatex — you can pass the four split geometry flags directly.
- xelatex needs `PATH` prepended with `/Library/TeX/texbin` when MacTeX is installed there and not on the default shell PATH. This is the most common macOS MacTeX setup.

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

**Pdflatex does not use system fonts** — it uses its own font catalogue and cannot load Palatino from the OS. Output defaults to Computer Modern. Tell the user explicitly when you fall back to this template. For the `remarkable` profile under pdflatex, use `papersize=a5paper`, `fontsize=12pt` (pdflatex caps at 12pt for the standard `article` class), split `geometry:` flags for 1.5cm uniform margins, and `-V linestretch=1.3`.

## Profiles

### Profile `default` — standard print
- **Target:** A printed deliverable (chapter, paper, handout) viewed on letter/A4 paper or on screen at 100% zoom.
- **Values:** US letter, Palatino 11pt, 2.5–3cm margins, coloured URLs (blue), TOC.
- **When to use:** the default for almost everything.

### Profile `remarkable` — E-Ink tablet (reMarkable or similar ≤ 12")
- **Target:** Readable on an E-Ink tablet without zooming.
- **Values:** A5, Palatino 13pt, Menlo 11pt for code, 1.5cm uniform margins, line stretch 1.3, black links (no colour — E-Ink renders blue links as illegible grey), TOC.
- **Why A5 + 13pt:** the reMarkable scales pages width-fit to its visible area. US letter scales to ~58%, making 11pt source text read at ~6.4pt — why you need to zoom. A5 scales to ~85%, making 13pt source text read at ~11pt — same effective size as a printed book.
- **When to use:** user explicitly requests the reMarkable / tablet / E-Ink profile.
- **Trade-offs:** more pages than default (smaller page, similar content density). Acceptable on a tablet; not for paper print.

### Adding a new profile

Add it here with: target, values, why-these-numbers, when-to-use, trade-offs. Add the value overrides under each engine template. Update the "Requirements" section if a new profile needs a new dependency.

5. **The output PDF goes in the same directory as the input file**, with the same name but `.pdf` extension. Quote file paths containing spaces. **If a non-default profile is used, suffix the output filename with the profile name** to avoid clobbering: e.g. `my-chapter.md` → `my-chapter.remarkable.pdf`. The default profile renders to plain `<name>.pdf`.

6. **After generating, run `pdfinfo`** on the output to confirm page count and file size, and report to the user:
   - Which engine was used (and the full path where it was found)
   - Which profile was used
   - Page count and file size
   - Page size (confirm A5 vs letter as expected)
   - Any visual-result differences from the target (relevant only if Template C was used)

7. **Move remarkable PDFs to `TO-READ/`.** After step 6, move the `.remarkable.pdf` to the repo root's `TO-READ/` folder:

   ```bash
   mkdir -p "$REPO_ROOT/TO-READ"
   mv "PATH/TO/<name>.remarkable.pdf" "$REPO_ROOT/TO-READ/<name>.remarkable.pdf"
   ```

   `TO-READ/` is a staging area for tablet reading — drag files from there into your tablet's desktop sync app. The folder is tracked but its contents are gitignored (add `TO-READ/*.pdf` to `.gitignore` if not already). The default profile stays next to the source; only the remarkable variant moves to `TO-READ/`.

## Known machine configurations

Fill this in as you run the skill on each machine. Update rather than append.

| Hostname | pandoc | typst | xelatex / MacTeX | Template to use | Last verified |
|---|---|---|---|---|---|
| *(add your hostname here)* | | | | | |

Run `hostname` at the shell to get your machine name.

## Requirements

- **pandoc** (required on every machine)
- **At least one of:** typst, xelatex, lualatex, or pdflatex

If pandoc is missing, stop and tell the user. If no PDF engine is present, suggest installing typst (lighter, faster, cleaner defaults) or MacTeX (heavier but handles more edge cases).

$ARGUMENTS
