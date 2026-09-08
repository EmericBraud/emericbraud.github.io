---
layout: post.njk
title: Le pruning alpha-beta
date: 2026-07-30
---
# L'EBF : la base de l'exponentielle
Notre arbre de recherche grossit de manière exponentielle en augmentant la profondeur. On estime aux échecs qu'une position "moyenne" proposerait environ **40 à 45 coups légaux**. Cela signifie que la complexité temporelle de notre algorithme grossit en

$$
O(45^P)
$$

où $P$ est la profondeur de recherche.
C'est évidemment un gros problème.

<pre class="mermaid">
graph LR
  P0["Profondeur 0<br/>1 nœud"]
  P1["Profondeur 1<br/>~45 nœuds"]
  P2["Profondeur 2<br/>~45² nœuds"]
  P3["Profondeur 3<br/>~45³ nœuds"]
  P0 -->|"×45"| P1 -->|"×45"| P2 -->|"×45"| P3
</pre>
<p style="text-align:center"><em>Le nombre de nœuds à explorer est multiplié par ~45 à chaque demi-coup de profondeur supplémentaire.</em></p>

On appelle **EBF** (*<strong>E</strong>ffective <strong>B</strong>ranching <strong>F</strong>actor*) le facteur multiplicatif moyen de nœuds qu'il est nécessaire de parcourir afin de passer d'une profondeur `P` à la profondeur `P+1`.

$$
EBF = \text{AVG}\left(\frac{N(P+1)}{N(P)}\right)
$$

où $N(P)$ est le nombre de nœuds explorés à la profondeur $P$.

On a donc une complexité temporelle en 
$$
N = O(EBF^P)
$$
L'EBF est **le facteur le plus déterminant** sur la rapidité de notre algorithme. Les optimisations sur la vitesse de traitement des nœuds passent généralement au second plan.

> Avec un EBF de 10, il faudrait traiter **10 fois plus de nœuds par seconde** pour gagner un seul demi-coup de profondeur *(un coup étant un coup des blancs suivi de la réponse des noirs)*.

# L'algorithme alpha-bêta

Le MinMax explore l'intégralité de l'arbre : chaque feuille est évaluée, sans exception. Or, en observant attentivement le déroulement de l'algorithme, on remarque qu'une grande partie de ce travail est **inutile** : dès qu'on a trouvé, dans une branche, un coup suffisamment mauvais pour qu'un joueur n'ait jamais intérêt à l'autoriser, il est inutile de continuer à explorer cette branche plus en détail. On peut **couper** (élaguer, ou *prune*) la recherche à cet endroit.

C'est exactement ce que fait l'algorithme **alpha-bêta** : il produit rigoureusement le même résultat que le MinMax, mais en visitant beaucoup moins de nœuds.

### Alpha et bêta : deux bornes que l'on affine

L'idée est de faire descendre, tout au long de la recherche, deux valeurs :

- **alpha ($\alpha$)** : le meilleur score que les blancs (le joueur qui maximise) sont **certains de pouvoir obtenir** ailleurs dans l'arbre.
- **bêta ($\beta$)** : le meilleur score que les noirs (le joueur qui minimise) sont **certains de pouvoir obtenir** ailleurs dans l'arbre.

Au départ, $\alpha = -\infty$ et $\beta = +\infty$ : on ne sait encore rien. Au fur et à mesure de l'exploration, ces deux valeurs se resserrent, et l'intervalle $[\alpha, \beta]$ représente la **fenêtre** des scores encore "intéressants" à explorer.

La coupure se produit dès que $\alpha \geq \beta$ : cela signifie qu'un des deux joueurs a déjà, ailleurs dans l'arbre, une alternative au moins aussi bonne que ce que la branche en cours pourrait lui offrir. Continuer à explorer cette branche ne changera donc jamais le coup finalement choisi à la racine : on peut s'arrêter net.

### Un exemple concret

Reprenons un arbre à deux niveaux, où les blancs (MAX) choisissent parmi deux coups, chacun suivi de deux réponses noires (MIN) :

<pre class="mermaid">
graph TD
  P0["Racine (MAX)"]
  P0 --> B1["Coup blanc 1 (MIN)"]
  P0 --> B2["Coup blanc 2 (MIN)"]
  B1 --> N1["Eval = 3"]
  B1 --> N2["Eval = 5"]
  B2 --> N3["Eval = 2"]
  B2 --> N4["Eval = ?"]
</pre>

- On explore d'abord la branche **Coup blanc 1**. Le nœud MIN y trouve d'abord `3`, puis `5` : comme il minimise, il garde `3`. La branche remonte donc `3` à la racine, qui met à jour $\alpha = 3$ *(les blancs sont désormais certains de pouvoir obtenir au moins 3)*.
- On explore ensuite **Coup blanc 2**. Le nœud MIN y trouve d'abord `2`. Comme ce nœud minimise et a déjà trouvé une valeur (`2`) **inférieure ou égale à $\alpha$ (3)**, il sait que les blancs ne choisiront jamais ce coup à la racine : peu importe ce que vaut le nœud restant (`Eval = ?`), le score de cette branche ne pourra pas dépasser `2`, donc il ne pourra jamais battre le `3` déjà garanti par **Coup blanc 1**.
- Le dernier nœud (`Eval = ?`) est donc **élagué** : il n'est jamais évalué.

C'est là toute la force de l'algorithme : le résultat final (les blancs jouent **Coup blanc 1**, score `3`) est strictement identique à celui du MinMax, mais on a économisé l'exploration d'un sous-arbre entier, qui, en profondeur, peut représenter des milliers, voire des millions de nœuds.

### L'importance de l'ordre d'exploration

L'efficacité de l'élagage dépend énormément de **l'ordre dans lequel les coups sont explorés**. Si, par malchance, on explorait toujours en premier le pire coup pour l'adversaire (ce qui l'oblige à explorer davantage avant de trouver de quoi couper), l'alpha-bêta ne coupe presque rien et se comporte comme un MinMax classique.

À l'inverse, avec un **ordre de coups optimal** (on essaie d'abord les coups qui ont le plus de chances d'être les meilleurs : captures, échecs, coups suggérés par une recherche précédente...), l'alpha-bêta atteint sa performance théorique maximale : dans le meilleur des cas, la complexité chute de

$$
O(EBF^P) \quad \text{à} \quad O(\sqrt{EBF^P})
$$

Ce qui revient, en pratique, à pouvoir chercher **deux fois plus profond** pour le même budget de calcul, un gain absolument considérable, puisqu'on a vu que l'EBF est le facteur le plus déterminant de la vitesse de l'algorithme.

> C'est précisément pour cette raison que le tri des coups (*move ordering*) est un sujet à part entière dans la conception d'un moteur d'échecs : plus l'ordre d'exploration se rapproche de l'ordre idéal, plus l'alpha-bêta coupe efficacement.