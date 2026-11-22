# /observatory: mira quién está trabajando y no le pises el trabajo

**Cuándo invocarla:** siempre que pueda haber más de una sesión de agente trabajando a la vez sobre este repositorio: antes de regenerar un fichero compartido (un dashboard, un índice, un backlog), cuando quieras saber quién más está activo o cuando cambies de persona y quieras que tu actividad se atribuya bien. También es la skill que hay que leer cuando quieras renderizar el dashboard.

**Quién la ejecuta:** cualquier agente (cualquier legatus). La captura es automática mediante hooks; esta skill es la capa de **autoinforme + coordinación**, la que solo puede llevar el propio agente.

El diseño completo está en [`../engineering-projects/legati-observatory/README.md`](../engineering-projects/legati-observatory/README.md) y [`DESIGN.md`](../engineering-projects/legati-observatory/DESIGN.md). Esta skill es la guía operativa.

---

## La única variable de entorno

```bash
OBS=engineering-projects/legati-observatory/obs.py
```

## En cada cambio de persona: atribuye tus eventos

Los hooks capturan automáticamente cada llamada a una herramienta, pero necesitan saber **qué** legatus está actuando. En cuanto cambies de persona, ejecuta:

```bash
python3 $OBS agent <your-legatus-name>     # e.g. orchestrator, writer, reviewer
```

Esto escribe un marcador por sesión que prevalece sobre el valor por defecto de la sesión, de modo que todos los eventos capturados a partir de ahí se atribuyen al legatus activo hasta el siguiente cambio. Es idempotente y barato: ejecútalo en cada cambio.

## Indica qué estás haciendo (opcional pero útil)

```bash
python3 $OBS task "drafting the methodology paper §5"
```

`current_task` es el «qué estoy haciendo» legible por humanos que solo sabes tú; aparece en la tabla de presencia.

## Antes de una escritura compartida arriesgada: comprueba y luego bloquea

Esta es la razón de ser de todo el sistema. Si vas a regenerar un fichero que otra sesión también podría estar escribiendo (un dashboard, un `INDEX.md`, un `BACKLOG.md`):

```bash
python3 $OBS who                                          # 1. who else is live, doing what?
python3 $OBS lock acquire <slug> --task "..." --ttl 15    # 2. claim it (atomic; fails if already held)
#   ... do the write ...
python3 $OBS lock release <slug>                          # 3. release when done
```

`lock acquire` usa creación exclusiva atómica, así que **dos agentes que cooperan no pueden ganar los dos el mismo bloqueo**. Si la adquisición **falla**, devuelve el propietario actual: **díselo al usuario y retírate**, no compitas. Un bloqueo se libera solo al vencer su TTL si el propietario se ha caído (sin interbloqueo).

El bloqueo es **consultivo**: funciona porque los agentes que cooperan lo respetan. Escribe la disciplina en tu guía de agentes: «antes de regenerar cualquier fichero compartido, adquiere su bloqueo; si te lo deniegan, retírate».

## Renderiza el dashboard

```bash
python3 $OBS render            # markdown -> render/dashboard-<host>.md  (read it in your editor)
python3 $OBS render --html     # interactive single-file HTML -> render/dashboard-<host>.html (open in a browser)
```

Las dos superficies son estáticas, están en el gitignore y son propias de cada máquina. El markdown es la vista rápida; el HTML es interactivo (filtro por agente/proyecto/tiempo, detalle de una sesión, barras de coste).

## Lo que NO tienes que hacer

- **No arrancas ningún servidor ni demonio.** Todo son ficheros estáticos que se renderizan a demanda.
- **No haces commit de nada de esto.** `.observatory/` y `render/` están en el gitignore: dependen de la máquina.
- **No configuras la captura en cada sesión.** Los hooks de `.claude/settings.json` ya la conectan; un clon recién hecho captura desde la siguiente sesión.
