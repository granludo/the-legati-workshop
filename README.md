# The Legati Workshop

Un andamiaje para construir tu propio espacio de trabajo intelectual aumentado con IA.

**Qué es:** un punto de partida con opiniones propias para llevar trabajo intelectual de largo aliento (escribir, investigar, dirigir trabajos, enseñar, pensar) con Claude Code o el Codex CLI de OpenAI como colaborador. Incluye herramientas que funcionan, un sistema de memoria, un marco de skills y un conjunto de personajes de IA con nombre. Tú pones nombre a los personajes, les das misiones y rellenas tu propia voz y tu visión del mundo.

**Qué no es:** una plantilla en blanco. La infraestructura funciona desde el primer día. Tu trabajo es personalizarla, no construirla desde cero.

**Empieza aquí:** lee `skills/start-here.md` y luego invócala: dile a Claude Code o a Codex `"start here"` o `"/start-here"`.

**Lee la guía:** `good-practices/` es una guía escrita por alguien que lleva más de un año con un taller como este. Cuenta qué funciona, qué no y por qué.

---

## Inicio rápido

1. Clona el repositorio: `git clone https://github.com/granludo/the-legati-workshop.git` y `cd the-legati-workshop`.
2. Inicia una sesión como el orquestador:
   - **Claude Code:** `./claude_orchestrator.sh`. Claude Code te pide que confíes en la carpeta la primera vez.
   - **Codex:** una vez por máquina, `codex login` y luego `bash tools/legati/install-hooks.sh codex`. A partir de ahí, `./codex_orchestrator.sh`. La primera vez, aprueba los hooks dentro de Codex con `/hooks`.
3. Di `start here`. La skill de bienvenida pone nombre a tus legati y escribe contigo tu primer perfil.
4. Dale al taller una casa propia: crea un repositorio **privado** y apunta `origin` hacia él (`git remote set-url origin <your-url>`). Tu taller guardará borradores, notas y memorias, así que nunca debería vivir en un repositorio público. Mientras no lo hagas, funciona en local y `tools/git/sync.sh` deja los commits en tu máquina. La skill de bienvenida te acompaña en esto (paso 6).

---

## Idiomas

La rama `main` está en inglés. La rama `castellano` tiene todos los ficheros markdown en castellano (español de España), y la rama `català`, en catalán: `git switch castellano` o `git switch català`, o clona directamente una de ellas: `git clone -b castellano https://github.com/granludo/the-legati-workshop.git`. El código, los comandos y los nombres de fichero siguen en inglés en todas las ramas, así que un comando que leas en un idioma funciona en los tres.

---

## Sobre los legati

La palabra que se usa en todo este repositorio es **legati** (en singular, *legatus*). En la República romana, un *legatus* era un delegado: alguien que llevaba la autoridad y los valores de un principal a un ámbito concreto, con un mandato claro y unos límites claros. Te representaba; no te sustituía.

Ese es el marco que usa este taller para los personajes de IA. No agentes: delegados. La distinción importa.

La palabra «agente» ha colonizado el discurso sobre la IA para designar algo que actúa de forma autónoma, persigue objetivos y usa herramientas por iniciativa propia. Ese marco coloca sutilmente al humano en el papel de espectador: fijas un objetivo y luego miras. El marco de los legati lo invierte: **tú eres el principal**. Cada legatus tiene un mandato que viene de ti, un dominio, un antimandato (lo que no debe hacer) y la obligación permanente de devolverte las decisiones cuando hace falta criterio. El repositorio es el registro duradero de todo esto; no lo es el modelo, ni la conversación, ni el servicio en la nube.

A mí «legati» me parece más honesto con lo que pasa de verdad. El modelo no tiene objetivos. Tiene un contexto, un fichero de personaje y tus instrucciones. Llamarlo delegado mantiene eso a la vista.

Dicho esto: «agente» está por todas partes, todo el mundo lo usa, y esa batalla la he perdido. Este repositorio usa «legati» porque es lo que son. Encontrarás «agente» en la documentación de las herramientas, en el propio vocabulario de Claude y en todos los tutoriales de internet. Aquí aparecerán las dos palabras. Lo que importa es el concepto.

---

## La idea en un párrafo

Un taller de escritura e investigación es una colaboración de largo recorrido entre tú y un conjunto de personajes de IA. Los personajes tienen memoria persistente, papeles especializados y herramientas que funcionan. Tú eres el principal: la fuente de los valores, el gusto y el criterio. Los legati hacen el trabajo mecánico y de síntesis, recuerdan lo que les dijiste y te devuelven las decisiones que requieren tu criterio. El repositorio es la capa duradera: sobrevive a cualquier conversación, a cualquier versión del modelo, a cualquier actualización de las herramientas. Todo lo importante vive aquí.

---

## Quién ha construido esto

Este andamiaje se destiló del taller en uso de Marc Alier (Ludo) (https://wasabi.essi.upc.edu/ludo), profesor de la UPC en Barcelona que lo usa para trabajar en libros, artículos académicos, materiales docentes, dirección de estudiantes y trabajo institucional. La guía de buenas prácticas está escrita con su voz. Las herramientas y las convenciones son suyas. Las opiniones son suyas. Los agentes están en blanco, porque tus agentes deberían ser tuyos.

Se recomienda usar Obsidian para navegar por los documentos con los que trabajáis tú y tus agentes.

---

## Licencia

Copyright (c) 2026 Marc Alier Forment (Ludo)

Con licencia **Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)**.

Puedes compartir y adaptar libremente este material, siempre que atribuyas la autoría a Marc Alier, no lo uses con fines comerciales y distribuyas las obras derivadas con la misma licencia.

Licencia completa: consulta `LICENSE`, o https://creativecommons.org/licenses/by-nc-sa/4.0/
