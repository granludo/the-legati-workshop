# /throat-clearing-review: encontrar la prosa que se anuncia en lugar de hablar

Revisión a dos legati de un documento que va a publicarse: **el escritor detecta y
propone reescrituras, el revisor gradúa la gravedad, el documento fuente no se altera
nunca.** El resultado es un informe que el principal lee con un veredicto asociado a
cada hallazgo, para poder aplicar, adaptar o rechazar cada uno con el bolígrafo en la mano.

**Invocación:** «Escritor, revisión de carraspeo de `<file>`» o
`/throat-clearing-review <file>`. Se dispara a petición del principal, no
de forma automática.

**Origen (2026-08-09).** En el taller original, el autor, leyendo las pruebas
de un artículo, se topó con este párrafo:

> "The mechanism behind that sensitivity is worth naming, because it applies to
> anyone computing this quantity. […] That is an argument for repetition, and
> for treating a configuration failure as a run that has not happened yet rather
> than as a result."

La reacción («If we need to say 'when a run failed due to an error in the
setup we fixed it and repeated the run', say that») es la skill entera. La
primera ejecución produjo un informe de formulación con 25 hallazgos, 2 de ellos
errores de hecho que el barrido de estilo sacó a la luz.

---

## La prueba

Para cada frase: **¿podría decir lo que pasó, con un verbo, de una sola vez?**
Si la frase retrasa un hecho, adorna un hecho o pone nota a su propia manera de
contar un hecho, es un hallazgo.

## La taxonomía de faltas

1. **Carraspeo**: anunciar que se va a decir algo en lugar de decirlo.
   Firmas: «X is worth naming, because…», «worth drawing
   out», «worth reading carefully», «worth being exact about which»,
   «worth separating because», «What makes this worth reporting is…»,
   «The striking feature of this table is…». El arreglo casi siempre es
   borrar el anuncio: lo que viene detrás ya estaba haciendo
   el trabajo.

2. **Evasión elíptica**: un hecho simple disfrazado de aforismo, de modo que el lector
   tiene que descifrar lo que se podría haber dicho sin más. Firmas de la primera ejecución:
   «a run that has not happened yet rather than as a result» (= arreglamos
   la configuración y lo volvimos a ejecutar), «not a failed measurement but an absent one»,
   «the ledger will empty on its own», «promote that from reading to
   finding», «sent us back to the machine». El arreglo es la regla del pan y el vino:
   al pan, pan, y al vino, vino; di el hecho.

3. **Metacomentario**: el documento narra su propia retórica o su propia
   elaboración en lugar de su tema. Firmas: «and we state it as such»,
   «we state it narrowly», «we note it rather than build on it», y el
   peor subtipo, la **filtración del historial de redacción**: texto dirigido a «a reader who
   later meets an earlier draft» en un medio donde solo existe el texto final.
   Parientes cercanos: los **verbos sin agente** («the findings publish regardless of
   direction»: los hallazgos no se publican solos; los publicamos nosotros) y las
   **construcciones que sermonean al lector** («A reader who takes X as Y will be
   misled, and so will one who…»).

## Lo que NO es una falta: protégelo

- **Aforismos ganados.** Un documento puede conservar sus dos o tres mejores frases aunque
  sean retóricas: «an instrument of this kind does not fail by
  crashing, it fails by returning a number one would have believed» sobrevivió a
  la primera ejecución porque enuncia el riesgo central del artículo, una vez, allí donde el
  incidente se lo había ganado. El grado Keep existe para que limpiar de más sea un error graduado,
  no una virtud.
- **Señalización que aporta información.** «Two conclusions follow, and they
  are separable» le dice al lector que puede aceptar una sin la otra. Se conserva.
- **Cautelas científicas que acotan una afirmación** («on these data», «we report it as
  observations on one model»). Acotar es contenido, no carraspeo.

## La cadena: cuatro pasos, de uno en uno

La revisión va **por etapas**. Cada paso produce un informe o una lista numerada, el
principal decide sobre ella, se aplica lo decidido, y solo entonces empieza el paso
siguiente. **Después de aplicar cada paso, sugiere el siguiente y di en una línea
en qué consiste.** No hagas nunca dos pasos en una misma pasada: cada paso lee
el documento tal como lo dejó el anterior.

Todos los pasos siguen el mismo contrato: **primero el informe, no se edita nada hasta que el
principal decide.** Lo decidido se aplica a una nueva versión menor (v10.2, v10.3, …) y al
fichero de publicación en la misma pasada, se verifica y se vuelve a renderizar.

### Paso 1: pasada de formulación (carraspeo, elipsis, metacomentario)

El escritor lee el documento de principio a fin, en orden (nada de una pasada solo con grep),
e informa de cada hallazgo: **ubicación, cita literal completa, falta identificada,
reescritura con la voz del principal**, en `<stem>-phrasing-report.md`, junto al documento
fuente. El revisor gradúa cada hallazgo en el mismo fichero: **Blocker / Major / Minor / Polish /
Keep**, con un recuento y un veredicto. El grado Keep es calibración obligatoria: un
documento conserva sus dos o tres aforismos ganados, y limpiar de más es un error
graduado. El principal edita el propio informe para decidir (cambiar un veredicto a Keep es una
decisión); «aplícalo todo» quiere decir aplicar todo lo que no esté marcado como Keep.

### Paso 2: pasada de párrafos redundantes

Relectura completa con una pregunta por párrafo: si esto desapareciera, ¿desaparecería
con él alguna afirmación, algún número o alguna salvedad? Propón unos 10 párrafos enteros cuya
eliminación no pierda nada o mejore el artículo, **como lista numerada en el chat con el
texto completo de cada párrafo** y una justificación de una línea (causas habituales: una historia
contada tres veces, una señal que apunta al párrafo siguiente, una salvedad que responde a
una pregunta que nadie ha hecho, una afirmación que se ha quedado obsoleta). El principal decide número
por número. Cuando un borrado deja huérfano un antecedente en una frase vecina, haz el
empalme mínimo e informa de él: un empalme forma parte del borrado, no es una reescritura.

### Paso 3: claridad de tablas y figuras (el revisor)

El revisor revisa **cada tabla y cada figura**: ¿está definida cada columna y cada dimensión
allí donde mira el lector? Comprobaciones fijas, aprendidas en la primera ejecución:
las columnas agregadas que mezclan modelos con precios por token distintos tienen que decirlo en
el pie; cada precio necesita una fuente y una fecha de captura declaradas **en el
artículo**, no solo en el repositorio; las referencias cruzadas de los pies tienen que apuntar a secciones
que de verdad contengan el material referido; los recuentos de los pies se pudren antes
que los recuentos de las tablas. Informa en el chat con las gravedades; nada de ediciones hasta que se decida.

### Paso 4: pasada de relleno dentro de las frases

El grano más fino: unas 20 expresiones dentro de los párrafos cuya **eliminación aporta claridad**:
intensificadores vacíos (*remarkably*, *simply*, *duly*), frases de anuncio que
las pasadas anteriores no vieron («X deserves a note», «The practical reading is
direct»), hipótesis escenificadas («A reviewer may reasonably ask…»), veredictos
repetidos, cautelas que diluyen lo que se está estableciendo («is understood to
be») y colas decorativas después de una idea ya completa. Lista numerada en el chat con cada
expresión dentro de su frase y lo que queda al quitarla. El principal decide; se aplica.

### Cada paso es también un barrido de bugs

Cada uno de los cuatro pasos encontró errores de hecho en la primera ejecución: un recuento
de andamiaje equivocado en la Discusión (paso 1), una afirmación que se volvió falsa al cambiar
los datos (paso 2), dos recuentos desfasados y una referencia de precio colgando en los pies
(paso 3), artículos gramaticales rotos y otro recuento desfasado (paso 4). **Las pasadas de estilo cazan
errores aritméticos porque obligan a releer frases que nadie ha mirado
en semanas.** Informa de los bugs junto a los hallazgos de estilo; tienen prioridad sobre todo lo demás.

## Relación con las pasadas que ya existen

Esta cadena es una capa distinta de `/unslop-text` (el barrido de tics de prosa).
El barrido de tics caza **vocabulario**: *delve*, *crucial*, *tapestry*. Esta
cadena caza **movimientos** (paso 1), **redundancia** (pasos 2 y 4) y
**dimensiones sin definir** (paso 3), que sobreviven a cualquier filtro de vocabulario porque
cada una de sus palabras, por separado, es inocente. Haz primero el barrido de tics (es
barato) y luego esta cadena, en todo lo que vaya a publicarse y donde la prosa importe.

## Ejemplo resuelto

La primera ejecución completa se hizo sobre el borrador para arXiv de un artículo de investigación (2026-08-09): el paso 1
produjo 25 hallazgos (2 Blockers), el paso 2 quitó nueve párrafos y corrigió una
afirmación falsa, el paso 3 restauró la procedencia de los precios en la que se apoyaban las columnas en dólares,
el paso 4 quitó veinte expresiones y cuatro bugs. Resultado: dos páginas menos, ningún número
cambiado, las 60 comprobaciones del verificador en verde de principio a fin.
