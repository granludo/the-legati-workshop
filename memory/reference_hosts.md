# Perfils de màquina: una secció per màquina

Cada legatus llegeix **només la secció d'aquesta màquina** en arrencar: `bash tools/legati/host-section.sh` imprimeix la secció `## <hostname>` que coincideix amb `hostname -s` (sense distingir majúscules i minúscules), fins al següent encapçalament `## `. Una màquina sense secció → el legatus t'ho diu i no dona per fet cap conjunt d'eines.

> [!todo] Tu
> Afegeix-hi una secció per cada màquina des de la qual treballes (`/start-here`, pas 6, escriu la primera amb tu). Mantén cada secció curta: es llegeix a cada inici de sessió. Esborra l'exemple de sota quan tinguis el teu.

## example-laptop

- **Què és:** portàtil, macOS, Apple Silicon, 16 GB. Màquina de cada dia; viatja.
- **Harness:** Claude Code (amb sessió iniciada); Codex (`codex login` fet, `install-hooks.sh codex` executat el 2026-11-22, hooks aprovats).
- **Camí del repositori:** `~/Code/my-workshop`.
- **Eines:** `pandoc`, `typst`, `python3` 3.12, `uv`, `node`, `llm` (amb el plugin `llm-ollama`).
- **Models:** cap model local aquí; `llm -m gpt-…` amb una clau a `llm keys`; un servidor Ollama local a la màquina de taula quan és a la xarxa de casa.
- **Repositoris externs:** cap.
- **Notes:** amb bateria la major part del dia: res de lots llargs amb models locals aquí.
