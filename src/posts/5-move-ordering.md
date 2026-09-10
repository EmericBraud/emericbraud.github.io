---
layout: post.njk
title: Le move ordering
date: 2026-09-08
chapter: Heuristiques d'élagage
chapterOrder: 1
---
# Pourquoi l'ordre des coups est si important

Nous l'avons évoqué à plusieurs reprises dans les articles précédents : l'efficacité de l'alpha-bêta dépend directement de l'ordre dans lequel les coups sont explorés à chaque nœud. Avec un tri parfait, l'EBF chute de `45` à environ `6.7` ; avec un mauvais tri, l'alpha-bêta ne coupe presque rien et se comporte comme un MinMax classique.

Le **move ordering** regroupe l'ensemble des heuristiques qui permettent, à un instant `T`, d'estimer quels coups ont le plus de chances d'être bons, **avant même de les avoir explorés**. Aucune de ces heuristiques n'est parfaite : elles s'appuient toutes sur des indices indirects, glanés soit lors de recherches précédentes, soit à partir de propriétés statiques du coup lui-même.

# Le coup de la table de transposition

La source d'information la plus fiable est celle que l'on possède déjà : si la position courante a déjà été rencontrée (via l'iterative deepening ou une transposition), la table de transposition contient le **meilleur coup** trouvé lors de la recherche précédente. Ce coup est alors systématiquement exploré en tout premier.

C'est de loin l'heuristique la plus puissante : elle ne repose sur aucune supposition, mais sur un résultat de calcul réel, obtenu à une profondeur légèrement inférieure.

# MVV-LVA : trier les captures

Pour les coups qui n'ont pas de meilleur coup connu en table de transposition, on trie d'abord par **catégorie** de coup, et la première catégorie à explorer est celle des captures.

Toutes les captures ne se valent cependant pas. L'heuristique **MVV-LVA** *(<strong>M</strong>ost <strong>V</strong>aluable <strong>V</strong>ictim, <strong>L</strong>east <strong>V</strong>aluable <strong>A</strong>ttacker)* propose de les trier en donnant la priorité :

- à la pièce **capturée** la plus précieuse (`V`ictim),
- puis, à valeur égale, à la pièce **capturante** la moins précieuse (`A`ttacker).

Prendre une dame avec un pion est ainsi exploré avant de prendre un pion avec une dame : intuitivement, capturer une pièce de grande valeur avec une pièce de faible valeur est presque toujours une bonne affaire, tandis que l'inverse mérite d'être vérifié plus tard, une fois qu'on a une meilleure borne pour couper rapidement si ça se révèle mauvais.

<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Coup</th>
      <th>Victime</th>
      <th>Attaquant</th>
      <th>Priorité</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Pion prend Dame</td>
      <td>Dame (9)</td>
      <td>Pion (1)</td>
      <td>Très haute</td>
    </tr>
    <tr>
      <td>Cavalier prend Tour</td>
      <td>Tour (5)</td>
      <td>Cavalier (3)</td>
      <td>Moyenne</td>
    </tr>
    <tr>
      <td>Dame prend Pion</td>
      <td>Pion (1)</td>
      <td>Dame (9)</td>
      <td>Basse</td>
    </tr>
  </tbody>
</table>

Pour affiner encore ce tri, certains moteurs utilisent une évaluation plus poussée, la **SEE** *(<strong>S</strong>tatic <strong>E</strong>xchange <strong>E</strong>valuation)*, qui simule statiquement toute la séquence d'échanges sur une case donnée (reprises comprises) afin de déterminer si une capture est réellement gagnante une fois toutes les reprises effectuées, plutôt que de ne regarder que le premier échange.

# Les killer moves

Une fois les captures épuisées, on s'intéresse aux coups "calmes" (qui ne capturent rien). Ici, on ne dispose plus d'un critère aussi direct que MVV-LVA. On s'appuie alors sur l'historique de la recherche en cours : les **killer moves**.

L'idée est la suivante : si un coup calme a provoqué une coupure alpha-bêta (un **fail-high**, c'est-à-dire un coup dont le score dépasse $\beta$) à un nœud donné, il y a de bonnes chances qu'un coup similaire soit également bon dans une **position sœur**, c'est-à-dire un autre nœud situé à la **même profondeur** de l'arbre. On mémorise donc, pour chaque profondeur, les coups ayant récemment causé une coupure, et on les essaie en priorité dans les positions frères.

*(À ne pas confondre avec le **fail-low** : lorsqu'aucun coup exploré à un nœud ne dépasse $\alpha$, le nœud renvoie simplement une borne supérieure, sans qu'aucun coup particulier ne se distingue. Seul le fail-high désigne un coup précis à retenir comme killer move.)*

<pre class="mermaid">
graph TD
  R["Racine"]
  R --> A["Position A"]
  R --> B["Position B (sœur de A)"]
  A --> K["Coup 'killer'<br/>a causé une coupure ici"]
  B --> K2["On essaie le même coup en priorité"]
</pre>

# La history heuristic

Dans la même veine, la **history heuristic** généralise l'idée des killer moves à l'échelle de toute la recherche, indépendamment de la profondeur. On maintient une table qui associe à chaque coup (typiquement une paire *case de départ / case d'arrivée*) un score, incrémenté à chaque fois que ce coup a provoqué une coupure alpha-bêta n'importe où dans l'arbre. Plus un coup a "fait ses preuves" au global, plus il est essayé tôt dans les positions suivantes.

# Un tri, jamais une certitude

Ces heuristiques peuvent se combiner naturellement, dans un ordre décroissant de fiabilité :

1. le coup issu de la table de transposition,
2. les captures, triées par MVV-LVA / SEE,
3. les killer moves,
4. les coups restants, triés par history heuristic.

Aucune de ces techniques ne garantit de trouver le meilleur coup en premier : ce ne sont que des paris informés, construits sur des statistiques et des résultats de recherches passées. Mais comme on l'a vu, même un tri imparfait suffit à rapprocher très fortement l'alpha-bêta de sa performance théorique optimale, ce qui en fait l'un des leviers d'optimisation les plus rentables d'un moteur d'échecs.
