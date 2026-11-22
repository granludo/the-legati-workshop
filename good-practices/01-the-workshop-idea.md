# 1. La idea del taller

La majoria de la gent fa servir la IA com fa servir Google: una pregunta, una resposta, la pregunta següent. La sessió s'acaba i tot torna a zero. La IA no ha après res de tu, i tu no has après res de la IA. És una màquina expenedora: útil, però no és cap col·laborador.

Un taller és just el contrari. La sessió s'acaba i alguna cosa perdura: la memòria d'allò en què treballes, la memòria de com penses i escrius, la memòria de les decisions que has pres i per què. La sessió següent comença amb un context que ha costat temps de veritat construir. Al llarg dels mesos, la diferència es va acumulant.

El que noto (i és el que intento explicar als col·legues que m'ho pregunten) no és que sigui més productiu. No ho soc. Publico més o menys el mateix nombre d'articles. El que canvia és la profunditat de la feina. Problemes que es passaven anys en un calaix perquè no els trobava mai per on agafar-los es tornen abordables. La IA no els resol. Però manté el context mentre penso, em fa millors preguntes de les que em faria jo mateix i m'obliga a articular posicions que arrossegava a mig formular. Això no és productivitat. És palanca intel·lectual.

## Què fa el repositori

El repositori del taller és la capa duradora. Sobreviu a qualsevol conversa, a qualsevol versió del model, a qualsevol actualització d'eines. La IA que el llegeix avui pot ser un model diferent del que el llegirà l'any que ve, però el repositori recorda el que han après totes dues sessions. Aquesta és la idea estructural: **no estàs construint un xatbot. Estàs construint un col·laborador de llarga durada que acumula context.**

El repositori conté:
- El sistema de memòria: el que els agents saben de tu, de la teva feina i de les teves preferències
- Les definicions de les skills: quines operacions poden fer els agents
- Les eines: scripts que funcionen de veritat per generar PDF, transcriure, processar fonts i verificar bibliografia
- Les identitats dels agents: els personatges que has donat a cada rol especialitzat

Res d'això no és als pesos de la IA. Tot és aquí, en text pla, sota control de versions. Quan la IA ho llegeix en començar la sessió, es converteix en l'agent que has dissenyat, no en un assistent genèric.

## La diferència que fa

El perfil d'escriptura n'és l'exemple més concret. Després d'un any fent anar aquest taller, tinc un document que descriu com escric: el meu ritme, les frases que evito, com estructuro els arguments, les metàfores a què recorro, els canvis de registre entre els articles acadèmics i els assajos per al gran públic. Quan començo una sessió amb «carrega el perfil d'escriptura», el resultat deixa de sonar a IA i comença a sonar a mi. No del tot: el calibratge no s'acaba mai. Però ara el primer esborrany es pot fer servir, en lloc de ser una obra d'enderroc.

Quan vaig començar, aquest document no existia. El vaig construir fixant-me en quan fallava un esborrany, explicant per què i escrivint la regla. El mateix amb el document de visió del món: les posicions intel·lectuals acumulades que eviten que els agents escriguin coses que jo no diria mai. El mateix amb els fitxers de memòria que recullen què va passar en sessions anteriors. El sistema millora perquè hi inverteixes.

## La inversió mínima viable

No cal que res d'això sigui perfecte el primer dia. La bastida ve amb plantilles i esquelets. El que has de fer el primer mes:

1. Escriu un primer esborrany del teu perfil d'escriptura. Quedarà curt. No passa res: ja creixerà.
2. Posa nom als teus agents i dona'ls com a mínim una missió d'una frase. N'hi ha prou per començar.
3. Fes unes quantes sessions i fixa't en què va malament. Escriu aquestes correccions a `memory/` com a fitxers de feedback.

El sistema es torna útil abans del que et penses. El primer cop que un agent aplica una correcció de fa tres setmanes sense que l'hagis de repetir, entens per què val la pena tota aquesta preparació.

## Què no fa

Un taller no et fa més ràpid. No t'automatitza el pensament. Els agents no prenen decisions: les prens tu. Mantenen el context, generen esborranys, verifiquen referències, fan aflorar patrons. El criteri sempre és teu.

Això és una virtut, no una limitació. L'objectiu és la feina profunda, no la feina delegada. Un agent que prengués decisions per tu estaria substituint la teva producció intel·lectual per la seva. El que vols és un agent que prepari el terreny perquè la teva producció intel·lectual pugui anar més a fons.
