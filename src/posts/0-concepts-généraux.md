---
layout: post.njk
title: Introduction rapide
date: 2026-07-27
chapter: Fondamentaux
chapterOrder: 0
---

*Cet article présente l'algorithme le plus classiquement utilisé pour permettre à l'ordinateur de jouer aux échecs. D'autres algorithmes, bien que plus marginaux, existent, s'appuyant sur des méthodes de Monte Carlo.*

*Bien que la cible de ce blog soit les échecs, les mêmes concepts s'appliquent au Othello, jeu de go, ou tout jeu impliquant deux joueurs qui joueraient au tour par tour...*

# Formuler le problème

Essayons de réfléchir ensemble à la manière la plus pragmatique de résoudre ce problème : on a accès à un ordinateur, et on aimerait le faire jouer aux échecs. Bien que cela  puisse paraître complexe à première vue, c'est en réalité déconcertant de simplicité.

En effet, il suffit d'à partir d'une position donnée, prédire le coup suivant, puis de répéter le processus jusque la fin de la partie pour atteindre notre objectif.

La question se résume alors à : **comment prédire le prochain meilleur coup ?** Intuitivement, afin de déterminer qu'un coup est meilleur qu'un autre, il est nécessaire de définir ce qu'est une bonne et une mauvaise position.

# Estimer la force d'une position : la fonction d'évaluation

Demandons-nous : comment un joueur d'échec arrive, d'un unique coup d'œil sur l'échiquier, à déterminer qui est gagnant et qui est perdant ?

On apprend dans un premier temps aux débutants à "compter les points" :
- Une pion : 1 point
- Une cavalier ou un fou : 3 points
- Une tour : 5 points
- Une dame : 9 points

Imaginons dans un premier temps que pour représenter l'échiquier, nous stockions dans un tableau de dimension 8x8 la position de chaque pièce. Pour déduire la force d'une position, il suffirait donc de boucler sur ce tableau, et de sommer la valeur des pièces de chaque joueur puis de faire la différence :

$$
S = Eval(position) = \sum_{i}^{P_{\text{blanches}}} v_i - \sum_{j}^{P_{\text{noires}}} v_j
$$

Ainsi, si le score $S$ est positif, les blancs ont l'avantage. Si le score $S$ est négatif, ce sont les noirs qui semblent gagner.

Evidemment, simplement sommer le score des pièces montrera vite ses limites : parfois, deux positions égales en matériel ne sont pas égales, et parfois même, une position pourtant gagnante en matériel peut être une très mauvaise position.

Pendant des années, les programmeurs ont donc imaginé des règles de plus en plus sophistiquées afin d'évaluer le plus finement possible une position : bonus de paire de fous, structure de pions, sécurité du roi... On peut rajouter autant de règles que l'on souhaite.

Ecrire des règles à la main pour évaluer une position, cela s'appelle une **HCE** *(Hand Crafted Evaluation)*. Des techniques plus récentes utilisent des réseaux neuronaux afin d'améliorer la finesse de l'évaluation. Mais l'idée est la même : concevoir une fonction `Eval(position)` qui, à partir d'une position, nous renvoie un score.

# Déterminer le meilleur coup : l'arbre de recherche

Bien, maintenant que l'on sait déterminer **statiquement** quelle position est la plus favorable, comment choisir le meilleur coup parmi tous les coups légaux possibles ?

### Profondeur 1

L'idée coule de source : on joue tous les coups possibles à partir de notre position, on évalue la position pour chaque coup joué grâce à notre fonction d'évaluation, et on choisit le coup qui nous donne le meilleur score.

<pre class="mermaid">
graph TD
  P0["Position initiale<br/>Eval = S₀"]
  P0 --> C1["Coup 1<br/>Eval = S1"]
  P0 --> C2["Coup 2<br/>Eval = S2"]
  P0 --> C3["Coup 3<br/>Eval = S3"]
  P0 --> C4["Coup 4<br/>Eval = S4"]
</pre>

Pour choisir le coup dont l'`Eval` est la plus favorable, on prend le score le plus grand pour les blancs, le plus petit pour les noirs.

Mais on arrive vite face à un problème : si on s'arrête là, notre programme sera totalement aveugle tactiquement. Ainsi, il sera capable de sacrifier sa dame contre un pion parce qu'au coup suivant, en comptant la valeur des pièces par exemple, la position semble gagnante (la dame n'ayant toujours pas été re-capturée par l'adversaire).

{% fen "4k3/3p4/4p3/8/8/8/4Q3/4K3 w - - 0 1", "white", "Score matériel : 9 pour les blancs, 2 pour les noirs. Score absolu : +7" %}

{% fen "4k3/3p4/4Q3/8/8/8/8/4K3 b - - 0 1", "white", "Score matériel : 9 pour les blancs, 1 pour les noirs. Score absolu : +8. <strong>La position semble meilleure.</strong>" %}

{% fen "4k3/8/4p3/8/8/8/8/4K3 w - - 0 1", "white", "Score matériel : 0 pour les blancs, 1 pour les noirs. Score absolu : -1. <strong>Effondrement de l'évaluation lié à un aveuglement tactique.</strong>" %}

Il faudrait donc également simuler la réponse de l'adversaire.

### Profondeur 2

Essayons de répéter le processus mais du point de vue de l'adversaire :

<pre class="mermaid">
graph TD
  P0["Position initiale<br/>(trait aux blancs)"]
  P0 --> B1["Coup blanc 1"]
  P0 --> B2["Coup blanc 2"]
  B1 --> N1["Coup noir 1<br/>Eval = S1"]
  B1 --> N2["Coup noir 2<br/>Eval = S2"]
  B2 --> N3["Coup noir 1<br/>Eval = S3"]
  B2 --> N4["Coup noir 2<br/>Eval = S4"]
</pre>

Les blancs choisissent alors le coup qui, en supposant que les noirs répondent au mieux pour eux, laisse le score le plus favorable possible. On a réglé notre problème, dans cette position, les blancs verront la réponse possible des noirs et ne sacrifieront plus leur dame !

{% fen "4k3/3p4/4p3/8/8/8/4Q3/4K3 w - - 0 1" %}

Mais le même problème se pose alors plus loin : on fait jouer à l'adversaire le coup le plus favorable pour lui, mais on a également besoin de déterminer notre réponse suivante pour ne pas faire jouer à l'adversaire un coup irrationnel qui le ferait lui aussi sacrifier sa position.

### L'algorithme MinMax

Ce que l'on vient de décrire porte un nom : l'algorithme **MinMax**. L'idée est de faire alterner, à chaque niveau de l'arbre, un joueur qui cherche à **maximiser** le score (les blancs) et un joueur qui cherche à le **minimiser** (les noirs).

On calcule d'abord l'`Eval` de toutes les feuilles de l'arbre, puis on remonte niveau par niveau : à chaque nœud "MIN", on garde la plus petite valeur parmi ses enfants ; à chaque nœud "MAX", on garde la plus grande. Le score qui remonte jusqu'à la racine correspond donc au score obtenu si les deux joueurs jouent le mieux possible.

<pre class="mermaid">
graph TD
  R["MAX<br/>retient 3"]:::maxNode
  A["MIN<br/>retient 3"]:::minNode
  B["MIN<br/>retient 2"]:::minNode
  L1["Eval = 3"]:::leaf
  L2["Eval = 5"]:::leaf
  L3["Eval = 2"]:::leaf
  L4["Eval = 9"]:::leaf
  R --> A
  R --> B
  A --> L1
  A --> L2
  B --> L3
  B --> L4

  classDef maxNode fill:#fdebd0,stroke:#e67e22,stroke-width:2px;
  classDef minNode fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
  classDef leaf fill:#f4f6f7,stroke:#7f8c8d;

  linkStyle 0 stroke:#e67e22,stroke-width:3px;
  linkStyle 2 stroke:#e67e22,stroke-width:3px;
</pre>
<p style="text-align:center"><em>En orange, le niveau MAX (les blancs) ; en bleu, le niveau MIN (les noirs). Le chemin en gras est celui réellement joué.</em></p>

Ici, les noirs, à gauche, choisiraient le coup menant à `Eval = 3` plutôt que `Eval = 5` (ils minimisent), et à droite, celui menant à `Eval = 2` plutôt que `Eval = 9`. Les blancs, eux, comparent alors `3` et `2`, et choisissent la branche de gauche puisque `3 > 2` (ils maximisent). Le score final remonté à la racine est donc `3`, et ce sont ces choix qui déterminent, de proche en proche, le premier coup à jouer.

### Profondeur N

Il nous faudrait donc un arbre infini ! C'est évidemment impossible. On va donc juste se contenter pour le moment de développer l'arbre le plus profond que notre CPU nous permette.

<pre class="mermaid">
graph TD
  P0["Position initiale<br/>(trait aux blancs)"]
  P0 --> B1["Coup blanc 1"]
  P0 --> B2["Coup blanc 2"]
  P0 --> B3["Coup blanc 3"]
  B1 --> N1["Coup noir"]
  B1 --> N2["Coup noir"]
  B2 --> N3["..."]
  B3 --> N4["Coup noir"]
  B3 --> N5["Coup noir"]
  N1 --> D1["⋮"]
  N2 --> D2["⋮"]
  N4 --> D3["⋮"]
  N5 --> D4["⋮"]
  D1 --> F1["Eval = S1"]
  D2 --> F2["Eval = S2"]
  D3 --> F3["..."]
  D4 --> F4["Eval = Sn"]
</pre>
<p style="text-align:center"><em>Arbre de recherche déplié jusqu'à la profondeur N</em></p>

Plus la profondeur `N` est grande, plus notre programme "voit loin" et évite les pièges tactiques en évaluant les feuilles de l'arbre qui se retrouvent de plus en plus loin de notre position. Mais le nombre de positions à évaluer explose exponentiellement avec `N`. Il faudrait donc nous débarrasser des branches de l'arbre peu prometteuses pour nous concentrer sur les coups les plus prometteurs : c'est là tout l'enjeu des algorithmes que nous allons voir par la suite.

