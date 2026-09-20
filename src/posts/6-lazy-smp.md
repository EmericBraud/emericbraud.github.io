---
layout: post.njk
title: Le multithreading avec Lazy SMP
date: 2026-09-10
section: Fonctionnement d'un moteur d'échecs
chapter: Explorer plus vite
chapterOrder: 6
---
# Un arbre difficile à découper

Toutes les optimisations vues jusqu'ici cherchaient à explorer **moins de nœuds**. Il reste un levier orthogonal : explorer les nœuds **plus vite**, en utilisant les différents cœurs de la machine.

Le problème est que l'alpha-bêta se parallélise très mal. Sa force vient précisément de sa nature **séquentielle** : le résultat du premier coup exploré fournit la borne $\alpha$ qui permet de couper les suivants. Si on distribue les coups d'un nœud sur plusieurs threads en parallèle, chacun démarre avec une fenêtre $[\alpha, \beta]$ plus large que nécessaire, coupe donc moins, et explore un sous-arbre bien plus gros que celui qu'un parcours séquentiel aurait visité.

> On ne cherche donc pas à répartir un travail fixe entre $N$ threads. Le travail total **augmente** avec le nombre de threads : tout l'enjeu est que cette surcharge reste inférieure au gain apporté par le parallélisme.
>
> Cette perte d'efficacité porte un nom : le **search overhead**. Avec $N$ threads, on n'obtient jamais un facteur $N$ ; un bon moteur atteint typiquement un facteur `2.5` à `3` sur 4 threads.

# Les approches historiques

Les premières tentatives cherchaient à découper l'arbre explicitement.

L'algorithme **Young Brothers Wait Concept** (YBWC) formalise l'intuition ci-dessus : à un nœud donné, on explore d'abord **séquentiellement** le premier coup (l'« aîné »), qui établit une borne $\alpha$ fiable, et seulement ensuite on distribue les coups restants (les « jeunes frères ») sur les threads disponibles. Les threads travaillent alors avec une fenêtre déjà resserrée, et coupent presque autant que dans une recherche séquentielle.

C'est théoriquement satisfaisant, mais coûteux en pratique : il faut synchroniser les threads à chaque nœud partagé, gérer la répartition dynamique du travail, et propager les mises à jour de bornes. Le code de recherche devient considérablement plus complexe, et les points de synchronisation limitent le passage à l'échelle.

<figure>
<svg viewBox="0 0 760 268" width="100%" style="max-width:760px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="YBWC : le premier coup est explore seul, puis les coups restants sont distribues sur les threads">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ph { font-size: 11px; font-weight: 600; letter-spacing: .06em; fill: #8a8372; text-anchor: middle; text-transform: uppercase }
  .lane { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11.5px; text-anchor: end }
  .rail { stroke: #ebe7dc }
  .bar { font-size: 12px; font-weight: 600; text-anchor: middle }
  .bar.s { text-anchor: start }
  .wait { font-size: 11px; fill: #b3ab9b; text-anchor: middle; font-style: italic }
  .sync { stroke: #9c5b4a; stroke-width: 1.4; stroke-dasharray: 5 4 }
  .synct { font-size: 11px; fill: #9c5b4a; text-anchor: middle; font-weight: 600 }
  .axis { fill: none; stroke: #ded9cd }
</style>
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#ded9cd"/></marker></defs>
<text x="245.0" y="34" class="ph">1. séquentiel</text>
<text x="563.0" y="34" class="ph">2. parallèle</text>
<text x="92" y="86.0" class="lane" fill="#3f6b9c">thread 1</text>
<line x1="104" y1="82.0" x2="740" y2="82.0" class="rail"/>
<text x="92" y="132.0" class="lane" fill="#4a7f6b">thread 2</text>
<line x1="104" y1="128.0" x2="740" y2="128.0" class="rail"/>
<text x="92" y="178.0" class="lane" fill="#a9762f">thread 3</text>
<line x1="104" y1="174.0" x2="740" y2="174.0" class="rail"/>
<rect x="104" y="68" width="274" height="28" fill="#eaf0f7" stroke="#3f6b9c"/>
<text x="241.0" y="86.0" class="bar" fill="#3f6b9c">coup 1, exploré seul</text>
<text x="241.0" y="132.0" class="wait">en attente</text>
<text x="241.0" y="178.0" class="wait">en attente</text>
<line x1="386" y1="52" x2="386" y2="198" class="sync"/>
<text x="386" y="216" class="synct">borne α connue</text>
<rect x="394" y="68" width="222" height="28" fill="#eaf0f7" stroke="#3f6b9c"/>
<text x="406" y="86.0" class="bar s" fill="#3f6b9c">coup 2</text>
<rect x="394" y="114" width="292" height="28" fill="#e9f2ee" stroke="#4a7f6b"/>
<text x="406" y="132.0" class="bar s" fill="#4a7f6b">coup 3</text>
<rect x="394" y="160" width="172" height="28" fill="#f9f1e3" stroke="#a9762f"/>
<text x="406" y="178.0" class="bar s" fill="#a9762f">coup 4</text>
<path d="M104 242 H740" class="axis" marker-end="url(#a)"/>
<text x="740" y="236" class="wait" text-anchor="end">temps</text>
</svg>
<figcaption>YBWC explore d'abord le premier coup seul, le temps d'obtenir une borne fiable ; les threads restent inactifs pendant ce temps, puis se partagent les coups suivants avec une fenêtre déjà resserrée.</figcaption>
</figure>

# Lazy SMP : ne rien partager, ou presque

**Lazy SMP** *(<strong>L</strong>azy <strong>S</strong>ymmetric <strong>M</strong>ulti<strong>P</strong>rocessing)* prend le problème à l'envers. Plutôt que de découper l'arbre, on lance simplement **la même recherche** sur tous les threads, à partir de la position racine, chacun faisant son propre iterative deepening.

Aucune synchronisation, aucun découpage, aucune répartition de travail. La seule chose que les threads partagent est la **table de transposition**, qui devient globale et concurrente.

C'est tout le paradoxe de la méthode : si les threads faisaient rigoureusement le même travail, le gain serait nul. Mais la table de transposition partagée suffit à les faire diverger utilement :

- dès qu'un thread écrit un résultat en table, les autres le lisent et évitent de recalculer ce sous-arbre ;
- le meilleur coup stocké en table modifie le **move ordering** des autres threads, qui explorent alors leurs nœuds dans un ordre différent ;
- ces divergences d'ordre modifient les bornes rencontrées, donc les coupures, donc les sous-arbres visités, et l'écart se creuse à mesure que la recherche progresse.

Les threads explorent donc naturellement des parties différentes de l'arbre, sans qu'on ait jamais eu à le leur demander. Un thread qui tombe par chance sur un bon coup tôt remplit la table avec des bornes serrées dont tous les autres profitent immédiatement.

<pre class="mermaid">
sequenceDiagram
  participant T1 as Thread 1
  participant TT as Table de transposition
  participant T2 as Thread 2
  T1->>TT: la position P est-elle connue ?
  TT-->>T1: non, rien en table
  T1->>T1: explore le sous-arbre de P
  T1->>TT: ecrit le score et le meilleur coup de P
  T2->>TT: la position P est-elle connue ?
  TT-->>T2: oui, score + meilleur coup
  Note over T2: n'explore pas P
</pre>

> Pour accentuer volontairement la divergence, la plupart des implémentations désynchronisent légèrement les threads : certains démarrent à une profondeur décalée, ou sautent des profondeurs, de sorte qu'ils ne cherchent jamais exactement la même itération au même moment.

# Les accès concurrents à la table

Partager la table de transposition entre threads soulève une difficulté. Une entrée contient plusieurs champs (clé de Zobrist, score, profondeur, type de borne, meilleur coup) qui dépassent la taille d'une écriture atomique. Deux threads écrivant simultanément dans le même emplacement peuvent produire une entrée **mélangée** : la clé de l'un avec le score de l'autre.

La réponse habituelle est... de ne rien faire. On accepte ces corruptions rares, en s'appuyant sur le fait que la clé de Zobrist stockée sert déjà de vérification : une entrée mélangée a une probabilité écrasante d'échouer à la comparaison de clé, et est donc simplement ignorée. Les rares cas qui passent au travers introduisent une erreur dans une branche, qu'une recherche à profondeur supérieure corrigera le plus souvent.

> Verrouiller la table serait catastrophique : c'est la structure la plus sollicitée du moteur, et un verrou global annulerait tout le bénéfice du parallélisme.
>
> Certains moteurs réduisent tout de même le risque en stockant un petit *checksum* dans l'entrée, ou en regroupant les champs de manière à ce que l'ensemble tienne dans une écriture atomique de 128 bits.

# Récupérer le résultat

Puisque chaque thread mène sa propre recherche, il faut décider lequel fait foi. La convention est de retenir le résultat du thread ayant terminé la **profondeur la plus élevée**, en départageant par le score. À l'arrêt du temps imparti, on ne prend jamais le résultat d'une itération incomplète : comme pour l'iterative deepening séquentiel, seule la dernière profondeur entièrement explorée est fiable.

Une conséquence à connaître : un moteur en Lazy SMP n'est plus **déterministe**. Deux recherches sur la même position, avec le même temps, peuvent renvoyer des coups différents selon l'ordre exact dans lequel les threads ont rempli la table. C'est un vrai inconvénient pour le débogage et les tests de régression, et la raison pour laquelle on teste presque toujours un moteur en mono-thread.

# Pourquoi c'est la méthode dominante

La simplicité du code est la raison la plus visible, et elle n'est pas anecdotique : la fonction de recherche reste la version séquentielle, inchangée ; on se contente de la lancer $N$ fois et de rendre la table de transposition concurrente. Il n'y a ni découpage d'arbre, ni répartition de tâches, ni synchronisation à écrire.

Mais ce serait mal résumer la situation que de s'arrêter là, comme si Lazy SMP était un compromis que l'on accepterait par paresse. Plusieurs raisons de fond expliquent qu'elle ne soit pas seulement moins coûteuse à écrire, mais aussi **compétitive en force de jeu**.

## L'arbre moderne est trop irrégulier pour être découpé

YBWC repose sur une hypothèse forte : le premier coup exploré établit une borne $\alpha$ fiable, et les coups suivants sont des sous-arbres comparables que l'on peut distribuer.

Cette hypothèse s'est érodée à mesure que le pruning avec perte et les réductions se sont généralisés. Aujourd'hui, à un même nœud, un coup peut être exploré à profondeur réduite, coupé immédiatement, ou déclencher une **re-recherche** complète à pleine profondeur si son score dépasse $\alpha$. Le coût d'une branche n'est plus prévisible **avant** de l'avoir explorée, et il varie de plusieurs ordres de grandeur d'un coup à l'autre. Répartir statiquement un travail dont on ignore la taille conduit à des threads inégalement chargés, donc à du vol de travail, donc à encore plus de synchronisation.

## La table de transposition fait déjà le travail de coordination

Le rôle joué par la table de transposition a lui aussi beaucoup grandi. Elle ne stocke plus seulement des scores pour éviter des recalculs : elle porte le **meilleur coup** de chaque position, donc l'essentiel du move ordering.

Or c'est exactement l'information qu'un algorithme parallèle a besoin de partager. En rendant la table concurrente, on obtient gratuitement un canal de communication entre threads : chacun publie ses meilleurs coups et lit ceux des autres, à chaque nœud, sans protocole explicite. La coordination fine que YBWC implémente à la main existe déjà, sous une forme implicite et asynchrone.

## Le matériel a changé de forme

Enfin, YBWC a été conçu à une époque où l'on parlait de quelques processeurs. Sur les machines actuelles (beaucoup de cœurs, plusieurs niveaux de cache, éventuellement plusieurs nœuds NUMA), le coût d'un point de synchronisation partagé croît avec le nombre de participants, tandis qu'une recherche sans synchronisation passe à l'échelle presque librement. Le classement des deux approches s'inverse donc au-delà de quelques threads, non pas parce que Lazy SMP s'améliore, mais parce que le prix de la synchronisation augmente.
