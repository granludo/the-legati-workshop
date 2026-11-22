# 4. La gestió de fonts

Una font és material en brut: un article acadèmic, un enregistrament, un vídeo, un capítol de llibre, un article web. Les fonts no són resultats. Alimenten el teu pensament; no són el teu pensament. La distinció sembla òbvia, però té conseqüències importants en la manera de treballar.

La carpeta `sources/` no és una biblioteca. És una cua de processament amb emmagatzematge a llarg termini. Una cosa hi entra com a font, es processa fins que és utilitzable i després s'hi queda com a recurs citable i cercable per a sessions futures. Si no es processa, només és un fitxer que acumula pols.

## El circuit de processament

Cada font que entra al taller passa per la skill `/add-source`. Aquesta skill s'encarrega de la mecànica: extreure la transcripció dels vídeos i els àudios, extreure el text dels PDF, recuperar net el contingut dels articles web. El que produeix no és només una còpia de la font, sinó la font més unes metadades: d'on ve, quan la vas aconseguir, per a què serveix, les afirmacions o els passatges clau que vas marcar.

El motiu d'aquesta disciplina: una font que només és un PDF o una transcripció costa de fer servir en una sessió. Una font processada (amb un resum, amb els passatges clau extrets, amb un README que explica per què t'interessava) és útil a l'acte. Els tres minuts de processament t'estalvien deu minuts de cerca en vint sessions.

## Les transcripcions de Whisper s'han de revisar

Si passes àudio o vídeo per una transcripció automàtica, no et fiïs mai directament del resultat. El reconeixement automàtic de la parla fa errors característics: noms propis, termes tècnics, vocabulari de grup, canvis de llengua. Sovint entén malament justament les paraules que més importen. Fes una passada de revisió abans de citar res d'una transcripció. En la teva pròpia llengua, n'hi ha prou amb una lectura ràpida; per a contingut tècnic, cal una passada més acurada.

## La divisió entre compartit i per projecte

Les fonts que només necessita un projecte van a `sources/[project-slug]/`. Les fonts que poden fer servir diversos projectes van a `sources/shared/`. Quan una font passa d'un projecte a la carpeta compartida, actualitza tots dos fitxers `INDEX.md`.

No et passis de llest amb la divisió. En cas de dubte, posa-la a la carpeta del projecte. Compartir abans d'hora crea confusió sobre de qui és la font i sobre si els canvis afecten altres projectes.

## La teva pròpia obra

Els teus articles publicats van a `sources/shared/papers-own/`. Sembla redundant (ja saps què has escrit), però té un propòsit concret: donar a l'agent d'escriptura exemples reals de la teva veu i de la teva manera d'argumentar en la seva forma final, publicada. El perfil d'escriptura descriu la teva veu en abstracte; els teus articles la fan concreta. Quan a l'agent li costa encertar el teu registre, llegir tres articles teus és més eficaç que rellegir el perfil d'escriptura.

## La disciplina de les citacions

Les fonts alimenten les citacions. Les citacions s'han de verificar. Abans que cap article surti del taller, cada referència ha de tenir un DOI o un URL verificat i una coincidència confirmada entre el títol i els autors que cites i el document real. Les eines de `/refs-check` en fan la major part de manera automàtica. La regla és: no t'inventis mai un URL ni un DOI per omplir metadades que falten; deixa el camp buit i eleva-ho a tu mateix. Més val una citació trencada que una d'inventada.
