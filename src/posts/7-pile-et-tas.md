---
layout: post.njk
title: La pile, le tas, et le coût d'une allocation
date: 2026-09-10
section: Techniques de programmation
chapter: Gestion de la mémoire
chapterOrder: 7
---
# Deux mémoires aux propriétés opposées

Un programme dispose de deux endroits pour stocker ses données : la **pile** *(stack)* et le **tas** *(heap)*. Ces deux zones mémoire vivent dans la RAM et ont des propriété structurelles très différentes et complémentaires.

La **pile** est une zone contiguë de mémoire associée à chaque thread, gérée par un simple pointeur. Entrer dans une fonction décrémente ce pointeur de la taille des variables locales, en sortir le remet où il était. Une allocation sur la pile coûte donc une instruction arithmétique, et sa libération n'a littéralement aucun coût. Comme les appels successifs réutilisent sans cesse les mêmes adresses, le sommet de la pile est presque toujours déjà dans le cache L1.

On peut voir la pile comme un livre dans lequel suivrait la page actuelle via un marque-page : à chaque nouvel appel de fonction, on avance le marque-page d'un nombre de pages équivalent au poids des variables locales à cette fonction, et une fois qu'on quitte la fonction, on recule le marque-page du même nombre de pages. 

Le **tas** est une ressource globale, partagée par tout le processus. Demander de la mémoire, c'est appeler un allocateur, c'est-à-dire du vrai code : il doit trouver un bloc libre de taille suffisante, mettre à jour ses structures internes, éventuellement demander de nouvelles pages au système d'exploitation. La libération est explicite, l'ordre est arbitraire, et rien ne garantit que deux allocations consécutives soient voisines en mémoire.

On peut voir le tas comme une bibliothèque : on a beaucoup plus de place, mais il faut parfois demander à l'OS (le bibliothécaire) une étagère libre et suffisamment grande pour y stocker ses livres. Il se peut qu'on range une partie de ses livres dans une étagère, puis une autre partie dans une autre : le tas n'est pas une unique zone contiguë en mémoire. Il se peut aussi rarement que le bibliothécaire n'ait plus aucune étagère de libre. Cela est rare sur ordinateurs modernes possédant plusieurs GO de RAM, mais beaucoup plus courant sur de petits systèmes embarqués.

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

# Ce qu'est réellement un std::vector

Un `std::vector` est le tableau de taille dynamique de la bibliothèque standard : contrairement à un tableau C ou à un `std::array`, dont le nombre d'éléments est fixé à la compilation, un vecteur peut grandir et rétrécir pendant l'exécution, au fur et à mesure des `push_back`. C'est ce qui en fait le conteneur par défaut en C++ : on n'a pas à connaître à l'avance le nombre d'éléments.

Cette souplesse n'est pas gratuite, et il vaut la peine de regarder ce qu'elle implique. Le vecteur est en réalité découpé entre les deux mémoires. L'objet lui-même ne contient que trois pointeurs (début des données, fin des données, fin de la capacité), soit 24 octets sur une machine 64 bits, et il vit là où on l'a déclaré, typiquement sur la pile. Les éléments, eux, sont toujours sur le tas.

<pre class="mermaid">
graph LR
  subgraph Pile
    V["std::vector&lt;int&gt; v<br/>begin | end | capacity<br/>24 octets"]
  end
  subgraph Tas
    B["buffer alloue<br/>[ 3 | 7 | 1 | ... | libre ]"]
  end
  V -->|pointe vers| B
</pre>

Deux conséquences en découlent. La première est une **indirection** : lire `v[i]` demande de charger un pointeur, puis de suivre ce pointeur vers une zone du tas qui n'a aucune raison d'être dans le cache. La seconde est que toute modification de la taille peut déclencher une **réallocation** : quand `push_back` dépasse la capacité, le vecteur alloue un nouveau buffer (généralement deux fois plus grand), y déplace les éléments existants, détruit les anciens, puis libère l'ancien buffer.

Un `std::vector<int> v; for (...) v.push_back(x);` sur 1000 éléments ne fait donc pas une allocation, mais une dizaine, avec les copies correspondantes. Le coût est amorti en $O(1)$ par élément, ce qui est une excellente propriété en moyenne, et une propriété inutilisable quand ce qui compte est le pire cas.

`reserve` résout ce point précis en allouant la capacité voulue d'un coup, mais ne supprime pas l'allocation elle-même, ni l'indirection.

# Le coût réel d'une allocation dynamique

Une allocation n'a pas un coût, elle a une **distribution** de coûts.

Dans le cas favorable, l'allocateur trouve un bloc de la bonne taille dans un cache par thread et rend la main en quelques dizaines de nanosecondes. Dans le cas défavorable, il doit fusionner des blocs libres, prendre un verrou partagé, ou demander de nouvelles pages au noyau via `mmap`. Ces pages arrivent alors non mappées : le premier accès déclenche un défaut de page, donc une entrée dans le noyau, à quelques microsecondes. Le rapport entre le meilleur et le pire cas dépasse facilement un facteur cent.

> Le problème d'une allocation dynamique n'est pas sa moyenne, c'est sa variance. Un coût moyen faible mais imprévisible est bien plus difficile à absorber qu'un coût élevé mais constant.

À cela s'ajoute la contention. Les allocateurs modernes maintiennent des caches par thread, mais ces caches se remplissent et se vident depuis des structures communes. Sur un moteur d'échecs en Lazy SMP, où tous les threads exécutent la même boucle de recherche, une allocation dans cette boucle signifie que tous les threads frappent l'allocateur en même temps, sur le même point de synchronisation.

# La règle : zéro allocation sur le chemin critique

La fonction de recherche d'un moteur d'échecs est appelée plusieurs millions de fois par seconde. À ce rythme, une seule allocation par nœud suffit à faire de l'allocateur le composant le plus sollicité du programme, devant l'évaluation et la génération de coups.

La règle est donc absolue : **aucune allocation dynamique sur le chemin critique**. En pratique, cela veut dire :

- les listes de coups sont des tableaux de taille fixe sur la pile, dimensionnés au pire cas théorique (218 coups légaux dans une position d'échecs) ;
- les structures indexées par profondeur, comme les killer moves ou l'historique de la partie, sont des tableaux préalloués une fois pour toutes ;
- les objets par thread sont alloués à la création du thread, jamais pendant la recherche.

Le point délicat est que beaucoup d'allocations sont **invisibles** dans le code. Un `std::string` construit pour un message de log, un `std::function` qui capture plus que ne le permet son stockage interne, un `std::map` qui alloue un nœud par insertion, un `std::vector` local dans une fonction utilitaire : rien de tout cela ne s'annonce comme une allocation, et tout cela en fait une. Le seul moyen fiable de s'en assurer est de mesurer, en instrumentant `operator new` pour compter les appels pendant une recherche : le nombre attendu est zéro.

# Les gros objets : alloués une fois, au démarrage

L'autre versant de la règle concerne les structures volumineuses, au premier rang desquelles la **table de transposition**. Elle occupe couramment plusieurs centaines de mégaoctets, et elle est allouée exactement une fois, au démarrage du moteur, ou lors d'un changement explicite de taille demandé par l'interface UCI.

Elle est allouée en un seul bloc contigu, dimensionné à une puissance de deux pour que l'indexation se fasse par masque binaire plutôt que par modulo. Rien n'est alloué ensuite : entre deux recherches, la table n'est ni libérée ni vidée, on se contente d'incrémenter un compteur d'âge qui permet de reconnaître les entrées devenues obsolètes. Le coût de cette mémoire est ainsi payé une seule fois, hors du temps de jeu, là où quelques centaines de millisecondes n'ont aucune importance.

Le même raisonnement s'applique aux poids du réseau de neurones, chargés au démarrage, et aux tables précalculées de la génération de coups.

# Le principe général

La leçon dépasse largement les échecs, et elle ne dit pas que l'allocation dynamique est mauvaise. Elle dit qu'une allocation est une **prise de ressource partagée**, avec une latence variable et un point de contention, et que la question utile n'est pas son coût mais l'endroit où ce coût tombe.

Le motif qui en découle se retrouve dans tous les domaines où la latence compte plus que la commodité, du traitement audio temps réel à la finance à haute fréquence : on alloue aux frontières du programme, à l'initialisation ou lors d'événements rares, et on garde le chemin chaud entièrement libre d'allocations, sur des tampons dont on possède déjà la mémoire.

L'embarqué et les systèmes critiques appliquent la même règle, mais pour une raison encore plus forte : une allocation dynamique peut **échouer**. Sur un moteur d'échecs, une allocation lente coûte de la profondeur de recherche ; sur un calculateur de vol ou un dispositif médical, une allocation qui échoue au mauvais moment est une panne, et il n'existe pas de conduite raisonnable à tenir en cours de vol lorsque `new` renvoie une erreur. À cela s'ajoute la fragmentation : après des heures de fonctionnement, un tas peut disposer de la mémoire totale demandée sans plus contenir un seul bloc contigu assez grand, et l'échec survient alors sans que rien n'ait changé dans le programme.

La réponse est la même, poussée à son terme : toute la mémoire est réservée au démarrage, dans des tampons de taille fixe dimensionnés au pire cas, et le programme n'appelle plus jamais l'allocateur ensuite. Un système qui a démarré a donc, par construction, déjà toute la mémoire dont il aura besoin, et la question « que faire si l'allocation échoue » disparaît au lieu d'être traitée. Certaines normes du domaine, comme les règles de codage de la NASA ou le MISRA C dans l'automobile, vont jusqu'à interdire purement et simplement l'allocation dynamique après l'initialisation.

Entre ces deux extrêmes, la démarche est identique, et c'est elle qu'il faut retenir : décider **quand** on paie, plutôt que subir un coût dont on ne maîtrise ni le moment, ni la durée, ni même la réussite.
