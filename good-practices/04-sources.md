# 4. Gestión de fuentes

Una fuente es material en bruto: un artículo científico, una grabación, un vídeo, un capítulo de libro, un artículo web. Las fuentes no son resultados. Alimentan tu pensamiento; no son tu pensamiento. La distinción parece obvia, pero sus consecuencias en el flujo de trabajo son considerables.

La carpeta `sources/` no es una biblioteca. Es una cola de procesamiento con almacenamiento a largo plazo. Algo entra como fuente, se procesa hasta tener una forma utilizable y luego se queda ahí como recurso citable y buscable para futuras sesiones. Si no se procesa, es solo un fichero cogiendo polvo.

## La cadena de procesamiento

Toda fuente que entra en el taller pasa por la skill `/add-source`. Esa skill se encarga de la mecánica: extraer la transcripción del vídeo y el audio, extraer el texto de los PDF, recuperar limpios los artículos web. Lo que produce no es solo una copia de la fuente, sino la fuente con sus metadatos: de dónde viene, cuándo la conseguiste, para qué la quieres, las afirmaciones o los pasajes clave que marcaste.

El motivo de esta disciplina: una fuente que es solo un PDF o una transcripción cuesta de usar en una sesión. Una fuente procesada (con un resumen, con los pasajes clave extraídos, con un README que explica por qué te interesó) es útil al momento. Los tres minutos de procesamiento ahorran diez minutos de búsqueda en veinte sesiones.

## Las transcripciones de Whisper hay que revisarlas

Si procesas audio o vídeo con transcripción automática, no te fíes nunca de la transcripción tal cual. El reconocimiento automático del habla comete errores característicos: nombres propios, términos técnicos, la jerga de cada grupo, los cambios de idioma. A menudo entiende mal justo las palabras que más importan. Haz una pasada de revisión antes de citar nada de una transcripción. En tu propia lengua basta con un vistazo rápido; en contenido técnico, una pasada más cuidadosa.

## Lo compartido y lo de cada proyecto

Las fuentes que necesita un solo proyecto van en `sources/[project-slug]/`. Las que pueden usar varios proyectos van en `sources/shared/`. Cuando una fuente pasa de un proyecto a compartida, actualiza los dos ficheros `INDEX.md`.

No te pases de listo con la división. En caso de duda, ponla en la carpeta del proyecto. Compartir antes de tiempo crea confusión sobre de quién es la fuente y sobre si los cambios afectan a otros proyectos.

## Tu propio trabajo anterior

Tus artículos publicados van en `sources/shared/papers-own/`. Parece redundante (ya sabes lo que escribiste), pero tiene un propósito concreto: darle al agente escritor ejemplos concretos de tu voz y de tu forma de argumentar en su versión final, publicada. El perfil de escritura describe tu voz en abstracto; tus artículos la encarnan. Cuando al agente le cuesta dar con tu registro, leer tres de tus artículos funciona mejor que volver a leer el perfil de escritura.

## La disciplina de las citas

Las fuentes alimentan las citas. Las citas exigen verificación. Antes de que un artículo salga del taller, cada referencia debería tener un DOI o una URL verificados y una coincidencia confirmada entre el título y los autores que citas y el documento real. Las herramientas de `/refs-check` se encargan automáticamente de casi todo esto. La regla es: no te inventes nunca una URL o un DOI para rellenar metadatos que faltan; deja el campo vacío y escálalo a ti mismo. Una cita rota es mejor que una inventada.
