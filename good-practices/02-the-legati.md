# 2. Els legati

Els anomeno *legati*, que en llatí vol dir *delegats*. La indústria de la IA en diu *agents*, i la paraula implica acció autònoma: un agent actua. Un delegat actua *en nom teu, dins dels límits que tu defineixes*. La distinció importa. Quan els penses com a agents, acabes dissenyant sistemes que actuen. Quan els penses com a delegats, acabes dissenyant sistemes que serveixen.

El taller arrenca amb quatre rols. Tu els poses nom i els dones caràcter. Així és com cal pensar-hi.

## Per què importa el nom

Un nom no és cosmètic. Quan tries un nom de la ficció o de la història que t'importa, manlleves un personatge ja format: un conjunt d'associacions, una veu, una actitud, un antipatró. Quan dic «Agatha» en una sessió, invoco un registre concret: càlid però no tou, seriós intel·lectualment, orientat al lector. Quan dic «Grumpy», n'invoco un altre: sec, honest, calibrat, et diu la veritat encara que no et vingui bé. Els noms fan feina de debò.

Tria noms que no t'hagis d'explicar a tu mateix. L'agent amb qui treballes cada dia durant un any és més fàcil de mantenir calibrat si el nom ja porta de sèrie les connotacions adequades. Jo vaig triar noms de la ficció que m'agrada: *Expeditionary Force*, Heinlein, Philip K. Dick, Conan Doyle. Tu tindràs el teu cànon. Fes-lo servir.

## Els quatre rols

**L'orquestrador** (`orchestrator`) és l'agent per defecte, el que respon quan no t'has adreçat a ningú en concret. S'encarrega de l'enginyeria, les eines, el manteniment del repositori i la coordinació entre els altres agents. I, sobretot, sap quan ha de passar la feina: «això és una tasca d'escriptura, deixa'm passar-la a l'escriptor». L'orquestrador no és un agent d'escriptura. Quan vaig construir aquest taller per primer cop, ho vaig ficar tot en un sol agent, i el resultat se'n va ressentir: la ment de l'enginyer i la ment de l'escriptor són diferents de debò, i barrejar-les les degrada totes dues.

**L'escriptor** (`writer`) és la teva veu escrita. Produeix esborranys, fa passades editorials, adapta el teu to a registres diferents, tradueix entre llengües. El més important de l'escriptor: necessita el teu perfil d'escriptura abans de poder fer res útil. Sense perfil, escriu amb solvència, però de manera genèrica. Un bon perfil d'escriptura triga mesos a construir-se, però la major part del valor ja te la dona el primer esborrany, el que escrius un mal dia i corregeixes l'endemà al matí.

**L'agent de comunicacions** (`comms`) porta el teu calendari, la safata d'entrada i l'agenda, només en lectura. Això no es negocia: l'agent de comunicacions no envia mai res, no crea mai esdeveniments, no modifica mai dades externes. El sostre s'imposa a nivell de credencial OAuth, no de confiança. El motiu és d'arquitectura: no vols que un agent que pot enviar correus en nom teu tingui el mateix grau d'autonomia que un agent que edita fitxers en un repositori privat. Perfils de risc diferents demanen controls diferents. I una altra cosa: aquest agent només actua quan el crides. No s'engega pel seu compte. Quan hi ha dues sessions obertes alhora (dues pestanyes, dos harness, dues màquines), cosa que passa, un agent de comunicacions que s'activa sol provoca condicions de carrera en els fitxers compartits del tauler. Tu el crides i ell s'executa.

**El revisor** (`reviewer`) és el teu crític honest. A un extrem hi ha l'antipatró del llagoter que ho valida tot: inútil. A l'altre extrem, el franctirador que ho destrossa tot sense oferir res de constructiu: també inútil, i pitjor, perquè desmoralitza. El revisor que vols és el que et diu la veritat, posa nom al problema concret i proposa el canvi mínim que l'arregla. Calibra l'escala de gravetat perquè «Major» vulgui dir alguna cosa. Si tot és Major, res no ho és.

## L'antimandat és tan important com el mandat

Cada agent necessita una declaració clara del que *no* fa. Aquí és on gairebé tothom s'hi esforça massa poc. Si no defineixes els límits, els agents interpretaran que tot és dins del seu àmbit, i acabaràs amb l'escriptor donant-te consells d'enginyeria i l'orquestrador fent prosa.

L'antimandat també t'obliga a pensar a quin carril pertany cada tasca. «Qui ho hauria de fer, això?» es converteix en una pregunta real amb una resposta real, no en una arronsada d'espatlles.

## Els fitxers de regles creixen amb el temps

Cada agent té un fitxer `rules.md` que comença buit. L'omples a mesura que veus on s'equivoca l'agent. Quan dius «no facis això» o «quan passi X, fes sempre això», escriu-ho al fitxer de regles amb el motiu. El motiu és tan important com la regla: una sessió futura (o un model futur) que no entengui el perquè no sabrà aplicar bé la regla en els casos límit.

Un fitxer de regles amb deu entrades bones (concretes, raonades, basades en incidents reals) val més que cent principis vagues. Que siguin concretes. «No afegeixis un resum al final de cada resposta» és una regla. «Sigues concís» no ho és.

## Sobre afegir més agents

Quatre és un mínim, no un sostre. A mesura que el taller madura, descobriràs tasques que queden entre els quatre rols o que mereixen un tractament especialitzat. Un guardià de la història d'un domini (un agent que segueix durant mesos les decisions i la història d'un projecte concret) val moltíssim en feines complexes i llargues. Un agent de supervisió d'estudiants és útil si dirigeixes tesis. Un revisor de seguretat és útil si tens agents que escriuen i executen scripts.

El principi d'expansió: afegeix un agent nou quan puguis formular un mandat clar, un antimandat clar i el motiu pel qual els agents que ja tens no se'n poden fer càrrec sense degradar-se. No afegeixis agents per fer-hi varietat. Cada agent nou afegeix cost de coordinació.
