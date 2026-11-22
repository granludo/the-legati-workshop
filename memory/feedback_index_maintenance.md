---
name: index-maintenance
description: Qualsevol canvi al sistema de fitxers o a l'estat d'un projecte actualitza els INDEX.md i BACKLOG.md corresponents en el mateix commit. Memòria inicial del taller original; conserva-la, edita-la o esborra-la.
metadata:
  type: feedback
---

Quan s'afegeixen, es mouen, es reanomenen o s'arxiven fitxers o carpetes, actualitza els mapes que es mantenen **en el mateix commit**: `INDEX.md` (estructura del repositori i projectes), `sources/INDEX.md` (material de fonts), el `BACKLOG.md` del projecte (el que s'ha treballat realment, s'ha acabat o s'ha ajornat) i `memory/MEMORY.md` quan s'afegeix una memòria.

**Per què:** diverses sessions treballen al repositori, sovint en paral·lel i des de harness diferents. Qualsevol que torni després d'una pausa, humà o legatus, s'orienta a partir d'aquests fitxers. Quan deixen de coincidir amb el sistema de fitxers, tots els resums que s'hi basen són erronis, i ningú no se n'adona fins que una sessió actua sobre un mapa desfasat.

**Com aplicar-ho:**
- Tracta l'actualització de l'índex i del backlog com a part de «fet», mai com un commit posterior.
- Llegeix el fitxer abans d'afegir-hi una entrada, perquè el format es mantingui coherent.
- Els elements acabats del backlog passen a una secció de fets, amb la data; no s'esborren (són la història del projecte).
- Per afegir una font: fes servir `/add-source`, que actualitza l'índex com a part del procés.
- No te'n desentenguis mai amb un missatge de commit del tipus «ja ho arreglaré».
