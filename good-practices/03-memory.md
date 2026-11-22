# 3. El sistema de memòria

El sistema de memòria és el que converteix una sèrie de sessions en una col·laboració contínua. Sense ell, cada sessió comença de zero: l'agent no sap qui ets, en què treballes, quines correccions ja li has fet ni quines decisions ja has pres. Amb ell, els cinc primers minuts de cada sessió es poden dedicar a fer feina de veritat en lloc de tornar a establir el context.

La idea clau és la distinció entre un fitxer de memòria i una nota. Una nota és una cosa que has escrit tu. Un fitxer de memòria és una cosa que l'agent llegeix en començar la sessió. La disciplina d'escriure fitxers de memòria és la disciplina de preguntar-se: «què necessitaria saber un agent nou, que només llegeix aquest repositori, per servir-me bé?»

## Els quatre tipus de memòria

**Les memòries d'usuari** parlen de tu: el teu rol, la teva experiència, com prefereixes treballar, què et treu de polleguera. Una bona memòria d'usuari no és una biografia: és una posada en antecedents. «Tinc vint anys d'experiència en enginyeria del programari, però és la primera vegada que em poso seriosament amb l'escriptura acadèmica» és útil. «M'agrada treballar al matí i prefereixo respostes curtes» és només una mica útil. «Soc una persona reflexiva que valora la feina ben feta» és soroll.

**Les memòries de feedback** recullen correccions i confirmacions. Quan dius «no facis això» a un agent, això és una memòria de feedback. Quan dius «sí, exacte, continua fent-ho així», també ho és (la gent s'oblida d'apuntar aquestes, però són igual d'importants: si només guardes les correccions, els agents es tornaran massa prudents). La norma: primer la regla, després el motiu. Una correcció sense motiu s'aplicarà malament.

**Les memòries de projecte** segueixen l'estat de la feina activa: què està en marxa, què s'ha decidit, què està encallat. Envelleixen de pressa: una memòria de projecte de fa tres mesos pot estar desfasada. Posa-hi sempre la data i una nota que digui quan deixarà de ser rellevant.

**Les memòries de referència** apunten a recursos externs: on es fa el seguiment dels errors, quin calendari mana, on trobar la normativa d'un procediment concret. Són punters, no contingut.

## Què no cal guardar

Aquí és on la gent s'equivoca. La temptació és guardar-ho tot: cada conversa, cada decisió, cada bocí de context. No ho facis.

No guardis allò que es pot deduir del codi o de l'historial de git. Si l'arquitectura es veu als fitxers, no et cal cap fitxer de memòria que en parli. No guardis solucions de depuració ni receptes d'arranjaments: l'arranjament és al codi, i el missatge del commit té el context. No guardis detalls efímers de tasques: el que estàs fent ara mateix va a un gestor de tasques, no a la memòria.

La memòria és per a les coses que no són evidents a partir de l'estat actual del repositori i que un agent nou que el llegís necessitaria per servir-te bé. Si un agent futur ho pot deduir llegint els fitxers, no és una memòria.

## L'índex MEMORY.md

`memory/MEMORY.md` és un índex, no un magatzem de contingut. Es carrega al context de cada sessió. Mantén-lo per sota de 200 línies: no és un tauler, és un fitxer de punters. Cada entrada és una línia: un enllaç al fitxer de memòria i una descripció d'una línia prou concreta perquè un agent futur pugui decidir si l'obre.

«Perfil d'usuari» és una mala entrada d'índex. «L'usuari és enginyer de camins amb deu anys d'experiència en disseny de ponts, nou en l'escriptura acadèmica» és una bona entrada: l'agent pot decidir sense obrir el fitxer si és rellevant per a la tasca que té entre mans.

## La regla d'arxivar, no esborrar

Els fitxers de memòria antics que ja no són exactes no s'esborren. Van a `archive/`. Els motius són pràctics: primer, de vegades una memòria descartada torna a ser rellevant. Segon, la història del que creies en cada moment ja és informativa per si mateixa. Tercer, l'arxiu no costa res: l'agent no llegirà els fitxers arxivats tret que l'hi demanis.

Aquesta regla s'estén a tot el taller. No esborris res. Arxiva-ho.
