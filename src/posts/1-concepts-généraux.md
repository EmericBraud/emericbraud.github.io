---
layout: post.njk
title: Introduction rapide
date: 2026-07-27
---

*Cet article présente l'algorithme le plus classiquement utilisé pour permettre à l'ordinateur de jouer aux échecs. D'autres algorithmes, bien que plus marginaux, existent, s'appuyant sur des méthodes de Monte Carlo.*

*Bien que la cible de ce blog soit les échecs, les mêmes concepts s'appliquent au Othello, jeu de go, ou tout jeu impliquant deux joueurs qui joueraient au tour par tour...*

# Formuler le problème

Essayons de réfléchir ensemble à la manière la plus pragmatique de résoudre ce problème : on a accès à un ordinateur, et on aimerait le faire jouer aux échecs. Bien que cela  puisse paraître complexe, à première vue, c'est en réalité déconcertant de simplicité.

En effet, il suffit d'à partir d'une position donnée, prédire le coup suivant, puis répéter le processus jusque la fin de la partie pour atteindre notre objectif.

La question se résume alors à : **comment prédire le prochain meilleur coup ?** Intuitivement, afin de déterminer qu'un coup est meilleur qu'un autre, il est nécessaire de définir ce qu'est une bonne et une mauvaise position.

# Estimer la force d'une position : la fonction d'évaluation

Demandons-nous : comment un joueur d'échec arrive, en d'un coup de regard sur l'échiquier, à déterminer qui est gagnant et qui est perdant ?

On apprend dans un premier temps aux débutants à "compter les points" :
- Une pion : 1 point
- Une cavalier ou un fou : 3 points
- Une tour : 5 points
- Une dame : 9 points

Imaginons dans un premier temps que nous stockions dans un tableau de dimension 8x8 la position de chaque pièce. Il suffirait donc de boucler sur ce tableau, et de sommer la valeur des pièces de chaque joueur puis de faire la différence pour en déduire la force d'une position :

$$
S = Eval(position) = \sum_{i}^{P_{\text{blanches}}} v_i - \sum_{j}^{P_{\text{noires}}} v_j
$$

Ainsi, si le score $S$ est positif, les blancs ont l'avantage. Si le score $S$ est négatif, ce sont les noirs qui semblent gagner.

Evidemment, simplement sommer les pièces montrera vite ses limites : parfois, deux positions égales en matériel ne sont pas égales, et parfois même, une position gagnante en matériel peut être perdante.

Pendant des années, les programmeurs ont donc imaginé des règles de plus en plus sophistiquées pour évaluer le plus finement possible une position : bonus de paire de fous, structure de pions, sécurité du roi... On peut rajouter autant de règles que l'on souhaite.

Ecrire des règles à la main pour évaluer une position, cela s'appelle une **HCE** *(Hand Crafted Evaluation)*. Des techniques plus récentes utilisent des réseaux neuronaux afin d'améliorer la finesse de l'évaluation. Mais l'idée est la même : concevoir une fonction `Eval(position)` qui nous renvoie un score.

# Déterminer le meilleur coup : l'arbre de recherche

Bien, maintenant que l'on sait déterminer **statiquement** quelle position est la plus favorable, comment déterminer le meilleur coup ?

### Profondeur 1

L'idée coule de source : on joue tous les coups possibles à partir de notre position, on évalue la position pour chaque coup joué, et on choisit le coup qui nous donne le meilleur score.

```
                    Position initiale
                    Eval = S₀
                   /   |   |   \
                  /    |   |    \
           Coup 1   Coup 2  Coup 3  Coup 4
           Eval=S1  Eval=S2 Eval=S3 Eval=S4
```

On choisit alors le coup dont l'`Eval` est la plus favorable (la plus grande pour les blancs, la plus petite pour les noirs).

Mais on arrive vite face à un problème : si on s'arrête là, notre programme sera totalement aveugle tactiquement. Ainsi, il sera capable de sacrifier sa dame contre un pion parce qu'au coup suivant en comptant les pièces, la position semble gagnante (la dame n'ayant toujours pas été re-capturée par l'adversaire).

{% fen "4k3/3p4/4p3/8/8/8/4Q3/4K3 w - - 0 1", "white", "Score matériel : 9 pour les blancs, 2 pour les noirs. Score absolu : +7" %}

{% fen "4k3/3p4/4Q3/8/8/8/8/4K3 b - - 0 1", "white", "Score matériel : 9 pour les blancs, 1 pour les noirs. Score absolu : +8. <strong>La position semble meilleure.</strong>" %}

{% fen "4k3/8/4p3/8/8/8/8/4K3 w - - 0 1", "white", "Score matériel : 0 pour les blancs, 1 pour les noirs. Score absolu : -1. <strong>Effondrement de l'évaluation lié à un aveuglement tactique.</strong>" %}

Il faudrait donc également simuler la réponse de l'adversaire.

### Profondeur 2

Essayons de répéter le processus mais du point de vue de l'adversaire :

```
                              Position initiale
                          (trait aux blancs)
                       /                        \
                Coup blanc 1                Coup blanc 2
                /          \                /          \
        Coup noir 1   Coup noir 2   Coup noir 1   Coup noir 2
        Eval=S1       Eval=S2       Eval=S3       Eval=S4
```

Les blancs choisissent alors le coup qui, en supposant que les noirs répondent au mieux pour eux, laisse le score le plus favorable possible. On a réglé notre problème, dans cette position, les blancs verront la réponse possible des noirs et ne sacrifieront plus leur dame !

{% fen "4k3/3p4/4p3/8/8/8/4Q3/4K3 w - - 0 1" %}

Mais le même problème se pose alors plus loin : on fait jouer à l'adversaire le coup le plus favorable pour lui, mais on a également besoin de déterminer notre réponse suivante pour ne pas faire jouer à l'adversaire un coup irrationnel qui le ferait lui aussi sacrifier sa position.

### Profondeur N

Il nous faudrait donc un arbre à 3 niveaux ! Mais là encore le problème se pose, à chaque fois les feuilles de l'arbre sont dans un état instable, on va donc juste se contenter pour le moment de développer l'arbre le plus profond que notre CPU nous permette. 