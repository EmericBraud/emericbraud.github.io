---
layout: post.njk
title: La pile, le tas, et le coût d'une allocation
date: 2026-09-10
section: Techniques de programmation
chapter: Gestion de la mémoire
chapterOrder: 7
---
Durant le développement de [Chess26](https://github.com/EmericBraud/chess26), j'ai été amené à approfondir ma compréhension du fonctionnement de la mémoire dans un programme. Ces concepts sont de peu d'utilité quand on développe en Python ou que l'on travaille avec un framework JavaScript, mais deviennent incontournables dès que l'on descend d'un niveau et que l'on cherche de la performance.

Un programme dispose de deux endroits pour stocker ses données : la **pile** *(stack)* et le **tas** *(heap)*. Ces deux zones mémoire vivent dans la RAM et ont des propriétés structurelles très différentes et complémentaires.

<figure id="carte-memoire">
<svg viewBox="0 0 620 410" width="100%" style="max-width:620px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Carte memoire d un programme : code, donnees globales, tas, espace libre, pile">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .sn { font-size: 13px; font-weight: 600 }
  .sd { font-size: 11px; fill: #8a8372 }
  .ax { font-size: 10.5px; fill: #8a8372; text-anchor: middle }
  .ax.s { text-anchor: start }
  .ax.e { text-anchor: end }
  .gl { fill: #3f6b9c; font-weight: 600 }
  .gl.t { fill: #4a7f6b }
  .gap { fill: #fdfcfa; stroke: #ded9cd; stroke-dasharray: 4 4 }
  .gr { fill: none; stroke: #3f6b9c; stroke-width: 1.3 }
  .gr.t { stroke: #4a7f6b }
</style>
<defs>
<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#3f6b9c"/></marker>
<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#4a7f6b"/></marker>
</defs>
<text x="300.0" y="18" class="ttl">MÉMOIRE D'UN PROGRAMME</text>
<text x="462" y="38" class="ax s">adresses hautes</text>
<rect x="150" y="34" width="300" height="78" fill="#eaf0f7" stroke="#3f6b9c"/>
<rect x="150" y="34" width="4" height="78" fill="#3f6b9c"/>
<text x="166" y="60" class="sn" fill="#3f6b9c">Pile</text>
<text x="166" y="80" class="sd">variables locales, cadres d'appel</text>
<rect x="150" y="112" width="300" height="92" class="gap"/>
<text x="300.0" y="162.0" class="ax">espace libre</text>
<rect x="150" y="204" width="300" height="78" fill="#e9f2ee" stroke="#4a7f6b"/>
<rect x="150" y="204" width="4" height="78" fill="#4a7f6b"/>
<text x="166" y="230" class="sn" fill="#4a7f6b">Tas</text>
<text x="166" y="250" class="sd">allocations dynamiques</text>
<rect x="150" y="282" width="300" height="52" fill="#f4f2ec" stroke="#8a8372"/>
<rect x="150" y="282" width="4" height="52" fill="#8a8372"/>
<text x="166" y="308" class="sn" fill="#8a8372">Données globales</text>
<text x="166" y="328" class="sd">variables statiques, constantes</text>
<rect x="150" y="334" width="300" height="52" fill="#f4f2ec" stroke="#8a8372"/>
<rect x="150" y="334" width="4" height="52" fill="#8a8372"/>
<text x="166" y="360" class="sn" fill="#8a8372">Code</text>
<text x="166" y="380" class="sd">les instructions du programme</text>
<text x="462" y="386" class="ax s">adresses basses</text>
<path d="M394 54 V140" class="gr" marker-end="url(#a)"/>
<text x="386" y="77.0" class="ax e gl">croît</text>
<path d="M394 262 V176" class="gr t" marker-end="url(#b)"/>
<text x="386" y="247.0" class="ax e gl t">croît</text>
</svg>
<figcaption>Les deux zones se font face et grandissent l'une vers l'autre, en se partageant le même espace libre.</figcaption>
</figure>

{% partie "Première partie", "Comment la mémoire fonctionne" %}

# La pile

La pile est celle que l'on utilise **par défaut**, souvent sans le savoir : toute variable locale à une fonction, tout paramètre, toute valeur de retour y atterrit sans qu'on ait rien demandé. Écrire `int score = 0;` dans une fonction, c'est allouer sur la pile.

> **Le cas des langages interprétés.** En Python, le programme qui s'exécute réellement sur la machine n'est pas celui que l'on écrit : c'est l'interpréteur, qui lit ce code et l'exécute au fur et à mesure. La pile de la machine est donc celle de l'interpréteur, pas celle du programme.
>
> Les variables déclarées dans le code, elles, désignent des objets alloués sur le tas, et ne sont que des références vers eux. C'est le sens de la formule « en Python, tout est un objet », aux quelques exceptions près que l'implémentation se réserve.

<figure class="side">
<svg viewBox="0 0 382 403" width="100%" style="max-width:382px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="La pile : un cadre colore par fonction appelee, une case par variable locale">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .fn { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px; font-weight: 600 }
  .cur { font-size: 9.5px; letter-spacing: .06em; text-anchor: end; text-transform: uppercase }
  .var { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11px; fill: #3d3b35 }
  .sz { font-size: 10px; fill: #9a9488; text-anchor: end }
  .ax { font-size: 10.5px; fill: #8a8372; text-anchor: middle }
  .ax.s { text-anchor: start }
  .ax.lim { fill: #9c5b4a }
  .spt { fill: #3f6b9c; font-weight: 600 }
  .it { font-style: italic }
  .free { fill: #fdfcfa; stroke: #ded9cd; stroke-dasharray: 4 4 }
  .limit { stroke: #c98b7b; stroke-width: 1.5; stroke-dasharray: 6 4 }
  .sp { fill: none; stroke: #3f6b9c; stroke-width: 1.4 }
</style>
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0 0 L10 5 L0 10 z" fill="#3f6b9c"/></marker></defs>
<text x="168.0" y="16" class="ttl">PILE DU THREAD</text>
<text x="326" y="41" class="ax s">adresses<tspan x="326" dy="11">hautes</tspan></text>
<rect x="18" y="32" width="300" height="85" fill="#eaf0f7" stroke="#3f6b9c" stroke-width="1"/>
<rect x="18" y="32" width="4" height="85" fill="#3f6b9c"/>
<text x="32" y="50" class="fn" fill="#3f6b9c">main()</text>
<rect x="32" y="58" width="258" height="20" fill="#fff" stroke="#3f6b9c" stroke-opacity=".45"/>
<text x="40" y="72" class="var">argc</text>
<text x="282" y="72" class="sz">4 o</text>
<rect x="32" y="83" width="258" height="20" fill="#fff" stroke="#3f6b9c" stroke-opacity=".45"/>
<text x="40" y="97" class="var">argv</text>
<text x="282" y="97" class="sz">8 o</text>
<rect x="18" y="117" width="300" height="110" fill="#e9f2ee" stroke="#4a7f6b" stroke-width="1"/>
<rect x="18" y="117" width="4" height="110" fill="#4a7f6b"/>
<text x="32" y="135" class="fn" fill="#4a7f6b">search(profondeur)</text>
<rect x="32" y="143" width="258" height="20" fill="#fff" stroke="#4a7f6b" stroke-opacity=".45"/>
<text x="40" y="157" class="var">alpha</text>
<text x="282" y="157" class="sz">4 o</text>
<rect x="32" y="168" width="258" height="20" fill="#fff" stroke="#4a7f6b" stroke-opacity=".45"/>
<text x="40" y="182" class="var">beta</text>
<text x="282" y="182" class="sz">4 o</text>
<rect x="32" y="193" width="258" height="20" fill="#fff" stroke="#4a7f6b" stroke-opacity=".45"/>
<text x="40" y="207" class="var">coups[218]</text>
<text x="282" y="207" class="sz">872 o</text>
<rect x="18" y="227" width="300" height="60" fill="#f9f1e3" stroke="#a9762f" stroke-width="1.6"/>
<rect x="18" y="227" width="4" height="60" fill="#a9762f"/>
<text x="32" y="245" class="fn" fill="#a9762f">evaluate()</text>
<rect x="32" y="253" width="258" height="20" fill="#fff" stroke="#a9762f" stroke-opacity=".45"/>
<text x="40" y="267" class="var">score</text>
<text x="282" y="267" class="sz">4 o</text>
<text x="304" y="245" class="cur" fill="#a9762f">en cours</text>
<rect x="18" y="287" width="300" height="86" class="free"/>
<path d="M168.0 327 V293" class="sp" marker-end="url(#a)"/>
<text x="168.0" y="343" class="ax spt">sommet de la pile</text>
<text x="168.0" y="363" class="ax">espace libre</text>
<line x1="10" y1="373" x2="326" y2="373" class="limit"/>
<text x="168.0" y="391" class="ax lim">limite : <tspan class="it">stack overflow</tspan></text>
<text x="326" y="357" class="ax s">adresses<tspan x="326" dy="11">basses</tspan></text>
</svg>
<figcaption>Chaque appel empile un cadre, une case par variable locale ; le retour dépile le tout d'un coup.</figcaption>
</figure>

C'est une zone contiguë de mémoire, propre à chaque thread, gérée par un simple pointeur. Entrer dans une fonction réserve la place des variables locales en déplaçant ce pointeur, en sortir le remet où il était. Une allocation sur la pile coûte donc une instruction arithmétique, et sa libération n'a littéralement aucun coût. Comme les appels successifs réutilisent sans cesse les mêmes adresses, le sommet de la pile est presque toujours déjà dans le cache L1.

> Par convention sur les architectures courantes, la pile croît vers les adresses **décroissantes** : le prologue d'une fonction décrémente le pointeur de pile, et son épilogue le réincrémente d'autant. Le mot « pile » décrit donc l'empilement des appels, pas le sens de progression en mémoire.

On peut voir la pile comme un livre dans lequel on suivrait la page actuelle via un marque-page : à chaque nouvel appel de fonction, on avance le marque-page d'un nombre de pages équivalent au poids des variables locales à cette fonction, et une fois qu'on quitte la fonction, on recule le marque-page du même nombre de pages.



Cette simplicité est précisément ce qui la rend rapide, et c'est aussi ce qui lui impose deux limites dont on ne peut pas sortir.

**La taille de chaque variable doit être connue d'avance.** Puisque entrer dans une fonction se résume à déplacer le marque-page d'un nombre de pages fixé, le compilateur doit savoir, à la compilation, de combien le déplacer. On ne peut donc pas réserver sur la pile un tableau dont la taille ne sera connue qu'à l'exécution, ni faire grandir une structure au fil du programme. De la même façon, tout ce qui est alloué dans une fonction disparaît à sa sortie : une donnée qui doit **survivre** à la fonction qui l'a créée n'a rien à faire sur la pile, y renvoyer un pointeur est une des erreurs classiques en C++.

**La pile est petite.** Là où le tas peut occuper toute la mémoire disponible, la pile est plafonnée à sa réservation initiale, souvent 1 à 8 Mo par thread. C'est confortable pour des variables locales, mais très vite insuffisant dès qu'on manipule de vrais volumes de données : la [table de transposition](/posts/3-table-de-transposition/) d'un moteur d'échecs, plusieurs centaines de mégaoctets, n'y tiendrait évidemment pas.

> Le dépassement de cette limite, le fameux *stack overflow*, ne se signale pas par un code d'erreur que l'on pourrait traiter : le programme s'arrête net. Les deux causes habituelles sont une récursion trop profonde et un gros tableau déclaré en variable locale.

C'est pour ces deux raisons, et pour elles seules, que l'autre zone existe.

# Le tas

<figure class="side">
<svg viewBox="0 0 384 380" width="100%" style="max-width:384px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fragmentation du tas : trois blocs libres mais non contigus, une demande de trois blocs echoue">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .cap { font-size: 10.5px; fill: #8a8372; text-anchor: middle }
  .bn { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11.5px; font-weight: 600; text-anchor: middle }
  .hole { fill: #fdfcfa; stroke: #ded9cd; stroke-dasharray: 4 4 }
  .lib { font-size: 10.5px; fill: #b3ab9b; text-anchor: middle }
  .ask { fill: none; stroke: #c98b7b; stroke-width: 1.4; stroke-dasharray: 5 4 }
  .askt { font-size: 11px; fill: #9c5b4a; text-anchor: middle; font-weight: 600 }
  .no { font-size: 10.5px; fill: #9c5b4a; text-anchor: middle }
</style>
<text x="192.0" y="16" class="ttl">LE TAS</text>
<text x="86.0" y="40" class="cap">Après quelques allocations</text>
<rect x="20" y="52" width="132" height="78" fill="#eaf0f7" stroke="#3f6b9c"/>
<rect x="20" y="52" width="4" height="78" fill="#3f6b9c"/>
<text x="86.0" y="95.0" class="bn" fill="#3f6b9c">bloc A</text>
<rect x="20" y="130" width="132" height="52" fill="#e9f2ee" stroke="#4a7f6b"/>
<rect x="20" y="130" width="4" height="52" fill="#4a7f6b"/>
<text x="86.0" y="160.0" class="bn" fill="#4a7f6b">bloc B</text>
<rect x="20" y="182" width="132" height="52" fill="#f9f1e3" stroke="#a9762f"/>
<rect x="20" y="182" width="4" height="52" fill="#a9762f"/>
<text x="86.0" y="212.0" class="bn" fill="#a9762f">bloc C</text>
<rect x="20" y="234" width="132" height="26" class="hole"/>
<text x="86.0" y="251.0" class="lib">libre</text>
<text x="298.0" y="40" class="cap">Après libération de B</text>
<rect x="232" y="52" width="132" height="78" fill="#eaf0f7" stroke="#3f6b9c"/>
<rect x="232" y="52" width="4" height="78" fill="#3f6b9c"/>
<text x="298.0" y="95.0" class="bn" fill="#3f6b9c">bloc A</text>
<rect x="232" y="130" width="132" height="52" class="hole"/>
<text x="298.0" y="160.0" class="lib">libre</text>
<rect x="232" y="182" width="132" height="52" fill="#f9f1e3" stroke="#a9762f"/>
<rect x="232" y="182" width="4" height="52" fill="#a9762f"/>
<text x="298.0" y="212.0" class="bn" fill="#a9762f">bloc C</text>
<rect x="232" y="234" width="132" height="26" class="hole"/>
<text x="298.0" y="251.0" class="lib">libre</text>
<rect x="226" y="276" width="144" height="78" class="ask"/>
<text x="298.0" y="311.0" class="askt">demande de 3 blocs</text>
<text x="298.0" y="329.0" class="no">refusée</text>
</svg>
<figcaption>Les libérations laissent des trous : la place totale suffit, mais aucun bloc contigu n'est assez grand.</figcaption>
</figure>

Le **tas** est une ressource globale, partagée par tout le processus. Demander de la mémoire, c'est appeler un allocateur, c'est-à-dire du vrai code : il doit trouver un bloc libre de taille suffisante, mettre à jour ses structures internes, éventuellement demander de nouvelles pages au système d'exploitation. La libération est explicite, l'ordre est arbitraire, et rien ne garantit que deux allocations consécutives soient voisines en mémoire.

On peut voir le tas comme une bibliothèque : on a beaucoup plus de place, mais il faut parfois demander à l'OS (le bibliothécaire) une étagère libre et suffisamment grande pour y stocker ses livres. Il se peut qu'on range une partie de ses livres dans une étagère, puis une autre partie dans une autre : le tas n'est pas une unique zone contiguë en mémoire. Il se peut aussi rarement que le bibliothécaire n'ait plus aucune étagère de libre. Cela est rare sur ordinateurs modernes possédant plusieurs gigaoctets de RAM, mais beaucoup plus courant sur de petits systèmes embarqués.

<table>
  <thead>
    <tr><th></th><th>Pile</th><th>Tas</th></tr>
  </thead>
  <tbody>
    <tr><td>Coût d'une allocation</td><td>une instruction</td><td>appel de fonction, chemin variable</td></tr>
    <tr><td>Libération</td><td>automatique, gratuite</td><td>explicite, à la charge du programme</td></tr>
    <tr><td>Durée de vie</td><td>liée à la portée</td><td>arbitraire</td></tr>
    <tr><td>Localité</td><td>excellente, cache chaud</td><td>dépend de l'historique des allocations</td></tr>
    <tr><td>Taille disponible</td><td>limitée (souvent 1 à 8 Mo)</td><td>presque illimitée pour notre usage (limitée par la RAM)</td></tr>
    <tr><td>Concurrence</td><td>une pile par thread</td><td>structure partagée entre threads</td></tr>
  </tbody>
</table>

La dernière ligne est celle que l'on oublie le plus souvent, et c'est justement celle qui fait le plus mal dans un programme multithreadé.

{% plus "D'où vient réellement la mémoire du tas : <code>brk</code> et <code>mmap</code>" %}

Le tas n'est pas une réserve que le programme posséderait dès son lancement : il la demande au système d'exploitation, au fur et à mesure, par l'un de deux mécanismes.

Le premier est historique. Le noyau maintient pour chaque processus une frontière, le *program break*, qui marque la fin de la zone de données. L'appel système [`brk`](https://man7.org/linux/man-pages/man2/brk.2.html) déplace cette frontière et agrandit d'autant la zone utilisable. C'est le tas du [premier schéma](#carte-memoire) de cet article, celui qui « croît vers les adresses hautes ».

Le second est celui qui domine aujourd'hui. Avec [`mmap`](https://man7.org/linux/man-pages/man2/mmap.2.html), le programme ne repousse plus une frontière : il demande au noyau une **zone entièrement nouvelle**, que celui-ci place où il veut dans l'espace d'adressage. La glibc bascule automatiquement sur ce mécanisme au-delà d'un certain seuil, 128 Ko par défaut, et c'est ainsi que sont servies toutes les grosses allocations, à commencer par la [table de transposition](/posts/3-table-de-transposition/) d'un moteur d'échecs.

> C'est la vraie raison pour laquelle le tas n'est pas une zone contiguë. L'image d'une région unique qui grandit vers le haut ne vaut que pour les petites allocations ; les grosses vivent dans des zones séparées, disséminées dans l'espace d'adressage.

Cette distinction a une conséquence visible. Un bloc obtenu par `mmap` est rendu au système lors de sa libération, et la mémoire du processus diminue réellement. Un bloc issu du tas historique, lui, reste presque toujours acquis au processus : l'allocateur le récupère dans ses listes internes pour le réutiliser, mais ne redescend pratiquement jamais le *program break*. C'est pourquoi la consommation mémoire affichée par le système ne baisse pas nécessairement après avoir libéré beaucoup d'objets.

{% endplus %}

{% plus "Ce qui se passe quand la place vient à manquer" %}

Contrairement à ce que laisse penser [ce premier schéma](#carte-memoire), la pile et le tas ne se percutent jamais. Quand la place manque, c'est le noyau qui refuse d'étendre la zone : `brk` ou `mmap` échoue, l'allocateur renvoie un pointeur nul, et `new` lève une exception [`std::bad_alloc`](https://en.cppreference.com/w/cpp/memory/new/bad_alloc). Trois situations bien distinctes se cachent derrière cet échec.

**L'espace d'adressage est plein.** Hors de portée sur une machine 64 bits, où l'espace utilisateur atteint 128 Tio. C'était en revanche une limite réelle en 32 bits : l'espace total y est de 4 Gio, dont le noyau se réserve une part, si bien qu'il ne restait que 2 à 3 Gio au processus, quelle que soit la RAM installée.

**La mémoire physique est épuisée.** Sous Linux, ce cas ne produit généralement pas d'échec d'allocation, à cause du **surengagement** : le noyau accorde la mémoire demandée sans vérifier qu'il pourra la fournir, en pariant que le programme n'utilisera pas tout. Le manque ne se révèle donc qu'au premier accès réel aux pages, et il ne se manifeste plus par une erreur que l'on pourrait traiter, mais par l'OOM killer, qui choisit un processus et le tue, parfois un autre que le coupable.

**La mémoire est fragmentée.** C'est le cas le plus insidieux, et c'est celui qui compte réellement en embarqué : la mémoire libre totale est largement suffisante, mais elle est découpée en morceaux dont aucun n'est assez grand. L'allocation échoue alors sans que rien n'ait changé dans le programme, simplement parce qu'il tourne depuis longtemps.

{% endplus %}

# Ce qu'est réellement un std::vector

Un [`std::vector`](https://en.cppreference.com/w/cpp/container/vector) est le tableau de taille dynamique de la bibliothèque standard : contrairement à un tableau C ou à un [`std::array`](https://en.cppreference.com/w/cpp/container/array), dont le nombre d'éléments est fixé à la compilation (donc qui vit sur la pile), un vecteur peut grandir et rétrécir pendant l'exécution, au fur et à mesure des [`push_back`](https://en.cppreference.com/w/cpp/container/vector/push_back). C'est ce qui en fait le conteneur par défaut en C++ : un simple tableau dont on n'a pas à connaître à l'avance le nombre d'éléments.

Cette souplesse n'est pas gratuite, et il vaut la peine de regarder ce qu'elle implique. Le vecteur est en réalité découpé entre les deux mémoires (la pile et le tas). L'objet lui-même ne contient que trois pointeurs (début des données, fin des données, fin de la capacité), soit 24 octets sur une machine 64 bits, et il vit là où on l'a déclaré, typiquement sur la pile. Les éléments, eux, sont toujours sur le tas.

<figure>
<svg viewBox="0 0 820 300" width="100%" style="max-width:820px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Un std::vector : trois pointeurs sur la pile designant le debut, la fin des elements et la fin du buffer alloue sur le tas">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .zone { fill: #fcfbf8; stroke: #ded9cd; stroke-dasharray: 4 3 }
  .zt { font-size: 11px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .obj { fill: #fff; stroke: #b9b2a2 }
  .sep { stroke: #e6e1d4 }
  .lbl { font-size: 13px; font-weight: 600; fill: #3d3b35; text-anchor: middle }
  .mono { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12.5px; fill: #3d3b35 }
  .mono.c { text-anchor: middle; fill: #1f4e79; font-weight: 600 }
  .mk { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11.5px; font-weight: 600 }
  .note { font-size: 11px; fill: #8a8372; text-anchor: middle }
  .cell { fill: #e8eef5; stroke: #9db4cd }
  .cell.free { fill: #fbfaf7; stroke: #ded9cd; stroke-dasharray: 3 3 }
  .link { fill: none; stroke: #c3bcab; stroke-width: 1.2; stroke-dasharray: 5 3 }
  .brace { fill: none; stroke: #ded9cd }
</style>
<defs><marker id="begin" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#3f6b9c"/></marker><marker id="end" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#4a7f6b"/></marker><marker id="capacity" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#a9762f"/></marker><marker id="g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#c3bcab"/></marker></defs>
<rect x="14" y="60" width="312" height="180" rx="3" class="zone"/>
<text x="170" y="48" class="zt">PILE</text>
<rect x="412" y="60" width="384" height="180" rx="3" class="zone"/>
<text x="604.0" y="48" class="zt">TAS</text>
<rect x="46" y="112" width="214" height="90" class="obj"/>
<text x="153.0" y="98" class="lbl">std::vector&lt;int&gt; v</text>
<text x="153.0" y="224" class="note">24 octets</text>
<rect x="58" y="122.0" width="10" height="10" fill="#3f6b9c"/>
<text x="78" y="131.0" class="mono">begin</text>
<line x1="46" y1="142" x2="260" y2="142" class="sep"/>
<rect x="58" y="152.0" width="10" height="10" fill="#4a7f6b"/>
<text x="78" y="161.0" class="mono">end</text>
<line x1="46" y1="172" x2="260" y2="172" class="sep"/>
<rect x="58" y="182.0" width="10" height="10" fill="#a9762f"/>
<text x="78" y="191.0" class="mono">capacity</text>
<path d="M260 157.0 H438" class="link" marker-end="url(#g)"/>
<text x="356.0" y="149.0" class="note">pointent dans ce buffer</text>
<rect x="452" y="150" width="38" height="38" class="cell"/>
<text x="471.0" y="175" class="mono c">3</text>
<rect x="490" y="150" width="38" height="38" class="cell"/>
<text x="509.0" y="175" class="mono c">7</text>
<rect x="528" y="150" width="38" height="38" class="cell"/>
<text x="547.0" y="175" class="mono c">1</text>
<rect x="566" y="150" width="38" height="38" class="cell"/>
<text x="585.0" y="175" class="mono c">9</text>
<rect x="604" y="150" width="38" height="38" class="cell free"/>
<rect x="642" y="150" width="38" height="38" class="cell free"/>
<rect x="680" y="150" width="38" height="38" class="cell free"/>
<rect x="718" y="150" width="38" height="38" class="cell free"/>
<path d="M452 120 V146" stroke="#3f6b9c" stroke-width="1.6" fill="none" marker-end="url(#begin)"/>
<text x="456" y="112" class="mk" fill="#3f6b9c" text-anchor="start">begin</text>
<path d="M604 120 V146" stroke="#4a7f6b" stroke-width="1.6" fill="none" marker-end="url(#end)"/>
<text x="604" y="112" class="mk" fill="#4a7f6b" text-anchor="middle">end</text>
<path d="M756 120 V146" stroke="#a9762f" stroke-width="1.6" fill="none" marker-end="url(#capacity)"/>
<text x="752" y="112" class="mk" fill="#a9762f" text-anchor="end">capacity</text>
<path d="M455 198 V204 H601 V198" class="brace"/>
<text x="528.0" y="220" class="note">4 éléments</text>
<path d="M607 198 V204 H753 V198" class="brace"/>
<text x="680.0" y="220" class="note">capacité libre</text>
</svg>
<figcaption>Les trois pointeurs du vecteur tiennent sur la pile ; les éléments vivent dans un buffer sur le tas. C'est la marge entre <code>end</code> et <code>capacity</code> qui évite une réallocation à chaque ajout.</figcaption>
</figure>

Deux conséquences en découlent. La première est une **indirection** : lire `v[i]` demande de charger un pointeur, puis de suivre ce pointeur vers une zone du tas qui n'a aucune raison d'être dans le cache. La seconde est que toute modification de la taille peut déclencher une **réallocation** : quand `push_back` dépasse la capacité, le vecteur alloue un nouveau buffer (généralement deux fois plus grand), y déplace les éléments existants, détruit les anciens, puis libère l'ancien buffer.

Un `std::vector<int> v; for (...) v.push_back(x);` sur 1000 éléments ne fait donc pas une allocation, mais potentiellement des dizaines, avec les copies correspondantes. Le coût est amorti en $O(1)$ par élément, ce qui est une excellente propriété en moyenne, et une propriété inutilisable quand ce qui compte est le pire cas.

[`reserve`](https://en.cppreference.com/w/cpp/container/vector/reserve) résout ce point précis en allouant la capacité voulue d'un coup, mais ne supprime pas l'allocation elle-même, ni l'indirection.

> **Un concept presque universel :** Cette séparation entre une enveloppe sur la pile et un contenu sur le tas n'a rien de propre au C++, et elle est même la règle dans certains langages. En Java, hors types primitifs, toute donnée vit sur le tas : une variable d'objet ne contient qu'une référence vers l'objet.
>
> C'est ce qui explique que la `NullPointerException` y soit l'erreur la plus courante. La référence peut ne désigner aucun objet, et l'on ne s'en aperçoit qu'en tentant de l'utiliser à l'exécution. La différence avec le C++ est que là où ce découpage est imposé et invisible en Java, il reste un choix explicite en C++ : un objet C++ peut vivre entièrement sur la pile.

# Le coût réel d'une allocation dynamique

Une allocation n'a pas un coût, elle a une **distribution** de coûts.

Dans le cas favorable, l'allocateur trouve un bloc de la bonne taille dans un cache par thread et rend la main en quelques dizaines de nanosecondes. Dans le cas défavorable, il doit fusionner des blocs libres, prendre un verrou partagé, ou demander de nouvelles pages au noyau via `mmap`. Ces pages arrivent alors non mappées : le premier accès déclenche un défaut de page, donc une entrée dans le noyau, à quelques microsecondes. Le rapport entre le meilleur et le pire cas dépasse facilement un facteur cent.

> Le problème d'une allocation dynamique n'est pas sa moyenne, c'est sa variance. Un coût moyen faible mais imprévisible est bien plus difficile à absorber qu'un coût élevé mais constant.

À cela s'ajoute la contention. Les allocateurs modernes maintiennent des caches par thread, mais ces caches se remplissent et se vident depuis des structures communes. Sur un moteur d'échecs en Lazy SMP, où tous les threads exécutent la même boucle de recherche, une allocation dans cette boucle signifie que tous les threads frappent l'allocateur en même temps, sur le même point de synchronisation.

{% partie "Seconde partie", "Ce que cela change pour Chess26" %}

# La règle : zéro allocation sur le chemin critique

La fonction de recherche d'un moteur d'échecs est appelée plusieurs millions de fois par seconde. À ce rythme, une seule allocation par nœud suffit à faire de l'allocateur le composant le plus sollicité du programme, devant l'évaluation et la génération de coups.

La règle est donc absolue : **aucune allocation dynamique sur le chemin critique**. En pratique, cela veut dire :

- les listes de coups sont des tableaux de taille fixe sur la pile, dimensionnés au pire cas : le maximum théorique est de 218 coups légaux dans une position. Chess26 réserve [256 entrées](https://github.com/EmericBraud/chess26/blob/main/src/common/constants.hpp#L7), que la [`MoveList`](https://github.com/EmericBraud/chess26/blob/main/src/core/move/move_list.hpp#L7-L11) déclare en tableaux bruts ;
- les structures indexées par profondeur, comme les killer moves ou l'historique de la partie, sont des tableaux préalloués une fois pour toutes ;
- les objets par thread sont alloués à la création du thread, jamais pendant la recherche.

> Le point délicat est que beaucoup d'allocations sont **invisibles** dans le code. Un `std::string` construit pour un message de log, un `std::function` qui capture plus que ne le permet son stockage interne, un `std::map` qui alloue un nœud par insertion, un `std::vector` local dans une fonction utilitaire : rien de tout cela ne s'annonce comme une allocation, et tout cela en fait une. Le seul moyen fiable de s'en assurer est de mesurer, en instrumentant `operator new` pour compter les appels pendant une recherche : le nombre attendu est zéro.

# Les gros objets : alloués une fois, au démarrage

L'autre versant de la règle concerne les structures volumineuses, au premier rang desquelles la **table de transposition**. Elle occupe couramment plusieurs centaines de mégaoctets, et elle est allouée exactement une fois, au démarrage du moteur, ou lors d'un changement explicite de taille demandé par l'interface UCI.

Elle est allouée en un seul bloc contigu, dimensionné à une puissance de deux pour que l'indexation se fasse par masque binaire plutôt que par modulo. Rien n'est alloué ensuite : entre deux recherches, la table n'est ni libérée ni vidée, on se contente d'incrémenter un compteur d'âge qui permet de reconnaître les entrées devenues obsolètes. Le coût de cette mémoire est ainsi payé une seule fois, hors du temps de jeu, là où quelques centaines de millisecondes n'ont aucune importance.

Le même raisonnement s'applique aux poids du réseau de neurones, chargés au démarrage, et aux tables précalculées de la génération de coups.

# Le principe général

Rien de tout cela ne condamne l'allocation dynamique : sans elle, impossible d'écrire un programme dont les besoins ne sont connus qu'à l'exécution. Mais allouer, c'est faire appel à un **service partagé** dont on ne maîtrise ni le temps de réponse, ni la disponibilité. La bonne réaction n'est donc pas d'allouer moins, mais d'allouer **ailleurs** : à un moment que l'on choisit, plutôt qu'au milieu de la boucle la plus chaude du programme.

Le motif qui en découle se retrouve dans tous les domaines où la latence compte plus que la commodité, du traitement audio temps réel à la finance à haute fréquence : on alloue aux frontières du programme, à l'initialisation ou lors d'événements rares, et on garde le chemin chaud entièrement libre d'allocations, sur des tampons dont on possède déjà la mémoire.

L'embarqué et les systèmes critiques appliquent la même règle, mais pour une raison encore plus forte : une allocation dynamique peut **échouer**. Sur un moteur d'échecs, une allocation lente coûte de la profondeur de recherche ; sur un calculateur de vol ou un dispositif médical, une allocation qui échoue au mauvais moment est une panne. À cela s'ajoute la fragmentation : après des heures de fonctionnement, un tas peut disposer de la mémoire totale demandée sans plus contenir un seul bloc contigu assez grand, et l'échec survient alors sans que rien n'ait changé dans le programme.

Ainsi, sur des systèmes critiques, toute la mémoire est réservée au démarrage, dans des tampons de taille fixe dimensionnés au pire cas, et le programme n'appelle plus jamais l'allocateur ensuite. Un système qui a démarré a donc, par construction, déjà toute la mémoire dont il aura besoin, et la question « que faire si l'allocation échoue » disparaît au lieu d'être traitée. C'est par exemple le cas des normes dans la NASA ou le MISRA C dans l'automobile.
