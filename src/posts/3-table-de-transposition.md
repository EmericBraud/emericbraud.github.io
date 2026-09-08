---
layout: post.njk
title: La table de transposition
date: 2026-09-08
---
# Une même position, plusieurs chemins

Aux échecs, il est très fréquent d'arriver à une **position strictement identique** en ayant joué les coups dans un ordre différent. Par exemple, `1. e4 c5 2. Nf3` et `1. Nf3 c5 2. e4` mènent exactement à la même position sur l'échiquier, alors qu'il s'agit de deux branches totalement distinctes de notre arbre de recherche.

<pre class="mermaid">
graph TD
  R["Position de départ"]
  R --> A1["1. e4"]
  R --> A2["1. Nf3"]
  A1 --> B1["1. e4 c5"]
  A2 --> B2["1. Nf3 c5"]
  B1 --> C1["2. Nf3"]
  B2 --> C2["2. e4"]
  C1 --> T["Même position"]
  C2 --> T
</pre>

On appelle ce phénomène une **transposition**. Sans précaution particulière, notre algorithme MinMax / alpha-bêta va explorer cette position deux fois, en repartant de zéro, alors qu'il a déjà fait tout ce travail une première fois. Plus l'arbre est profond, plus les transpositions sont nombreuses, et plus ce travail redondant devient coûteux.

# Mémoriser ce que l'on a déjà calculé

L'idée est donc simple : à chaque fois que l'on évalue une position, on **mémorise le résultat** dans une structure de données, la **table de transposition** *(transposition table)*. Avant d'explorer une position, on vérifie d'abord si elle ne s'y trouve pas déjà : si c'est le cas, on peut directement réutiliser le résultat déjà calculé, sans avoir à ré-explorer tout le sous-arbre correspondant.

Concrètement, la table de transposition stocke, pour chaque position déjà rencontrée :

- le **score** obtenu pour cette position,
- la **profondeur** à laquelle ce score a été calculé,
- le **meilleur coup** trouvé pour cette position,
- un indicateur précisant si ce score est une valeur exacte, ou seulement une borne (on y reviendra).

On peut se représenter la table de transposition comme un simple tableau, indexé par le hachage de la position, où chaque case regroupe ces informations :

<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Hachage (clé)</th>
      <th>Score</th>
      <th>Profondeur</th>
      <th>Meilleur coup</th>
      <th>Type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>0x3F2A...C1</code></td>
      <td>+35</td>
      <td>8</td>
      <td>Nf3</td>
      <td>Exact</td>
    </tr>
    <tr>
      <td><code>0x9B10...44</code></td>
      <td>-120</td>
      <td>5</td>
      <td>Qxd5</td>
      <td>Borne sup.</td>
    </tr>
    <tr>
      <td><code>0x7E88...0D</code></td>
      <td>+500</td>
      <td>12</td>
      <td>Rxe8</td>
      <td>Borne inf.</td>
    </tr>
    <tr>
      <td colspan="5">...</td>
    </tr>
  </tbody>
</table>

Lorsqu'on rencontre une nouvelle position, on calcule son hachage, on regarde si une entrée existe déjà à cet emplacement dans le tableau, et on décide de la réutiliser, de la compléter ou de l'écraser selon les critères vus plus haut.

# Identifier une position : le hachage de Zobrist

Pour retrouver rapidement une position dans la table, encore faut-il pouvoir l'identifier de manière unique et efficace. Stocker l'échiquier complet comme clé, puis comparer les positions case par case, serait bien trop lent.

C'est ici qu'intervient le **hachage de Zobrist** *(Zobrist hashing)*. Le principe est le suivant : on génère, une bonne fois pour toutes au démarrage du programme, un nombre aléatoire pour chaque combinaison possible de *(pièce, case)*, ainsi que quelques nombres supplémentaires pour représenter le trait, les droits au roque et la case en passant.

Le hachage d'une position s'obtient alors en combinant, par un simple `XOR`, les nombres aléatoires correspondant à chaque pièce présente sur l'échiquier :

$$
H(position) = \bigoplus_{i}^{\text{pièces en jeu}} Z_i
$$

L'intérêt du `XOR` est qu'il permet de **mettre à jour le hachage incrémentalement** à chaque coup joué, sans avoir à le recalculer entièrement : il suffit de `XOR`-er les quelques nombres concernés par le coup joué (la case de départ, la case d'arrivée, une éventuelle pièce capturée...) plutôt que de reparcourir tout l'échiquier.

*(Pour les matheux : cela fonctionne car le `XOR` est une involution, c'est-à-dire que $a \oplus a = 0$ et $a \oplus 0 = a$. Concrètement, cela signifie qu'appliquer deux fois le même `XOR` annule son effet : on peut donc "retirer" une pièce du hachage en la `XOR`-ant une seconde fois, exactement comme on l'a ajoutée.)*

Ce hachage devient alors la **clé** que l'on utilise pour stocker et retrouver une position dans la table de transposition.

Cette propriété d'involution a une autre conséquence importante, sur laquelle nous reviendrons en détail par la suite : lors de la recherche, il est presque toujours plus rapide de fonctionner **par incréments**, en descendant puis en remontant l'arbre coup par coup (`move` / `unmove`), plutôt que de reconstruire l'état complet de la position à chaque nœud. Or c'est précisément ce que permet l'involution : puisque `XOR`-er deux fois le même nombre annule son effet, on peut aussi bien **jouer** un coup (`XOR` du hachage) que le **défaire** (à nouveau `XOR` du même hachage) sans jamais recalculer la position depuis le début.

# Un stockage nécessairement partiel

Le nombre de positions atteignables aux échecs est astronomique, bien trop important pour toutes les conserver en mémoire. La table de transposition a donc une **taille fixe**, choisie non seulement en fonction de la mémoire disponible, mais aussi de problématiques de **cache misses** que nous évoquerons plus tard. Plusieurs positions distinctes peuvent donc être amenées à se partager la même case de la table (une **collision**). Quand cela se produit, une entrée doit être sacrifiée pour laisser la place à la nouvelle.

Une stratégie courante consiste à toujours garder l'entrée la plus profonde (elle représente davantage de travail de calcul, donc davantage de temps économisé si on la retrouve), ou à privilégier les positions issues de la recherche en cours plutôt que d'une recherche précédente.

C'est également ce qui permet de relier la table de transposition à l'**iterative deepening** évoqué dans l'article précédent : les résultats calculés à la profondeur `P-1` restent disponibles dans la table lorsqu'on entame la recherche à la profondeur `P`. Non seulement le meilleur coup trouvé sert à trier les coups à explorer en premier, mais si une sous-position a déjà été entièrement évaluée à une profondeur suffisante, on peut carrément s'épargner de la ré-explorer.

> La table de transposition ne se contente donc pas d'éviter le travail redondant au sein d'une seule recherche : elle permet également de réutiliser, itération après itération, une partie du travail effectué aux profondeurs précédentes.
