---
layout: post.njk
title: Le pruning avec perte
date: 2026-09-08
chapter: Heuristiques d'élagage
chapterOrder: 0
---
# Un élagage qui garantit l'exactitude... mais pas la vitesse

L'alpha-bêta, tel que nous l'avons décrit jusqu'à présent, est un algorithme **exact** : il produit rigoureusement le même résultat que le MinMax, aucune information n'est perdue en cours de route. C'est une propriété rassurante, mais elle a un coût : même avec un excellent tri des coups, il faut toujours, dans le pire des cas, explorer la quasi-totalité des coups légaux à chaque nœud avant de pouvoir conclure quoi que ce soit.

Or, statistiquement, on sait déjà beaucoup de choses avant même d'avoir commencé à chercher. Un coup qui déplace une pièce dans un coin sans aucune raison apparente, ou le dixième coup candidat d'une position alors que les neuf premiers se sont tous révélés catastrophiques, a de très fortes chances d'être mauvais. Pourquoi alors lui consacrer le même effort de recherche qu'à un coup prometteur ?

C'est l'idée derrière le **pruning avec perte** *(forward pruning)* : on accepte de couper des branches de l'arbre non plus parce qu'on est **certain** qu'elles sont sans intérêt (comme le fait l'alpha-bêta), mais parce qu'on estime, sur la base de statistiques ou d'heuristiques, qu'elles ont une **probabilité suffisamment faible** de changer le résultat final.

> Contrairement à l'alpha-bêta, ces techniques ne sont plus garanties de trouver le même résultat que le MinMax. On accepte sciemment un risque d'erreur, en échange d'un gain de vitesse souvent considérable.

# Remettre l'EBF en perspective

On peut mesurer très concrètement l'apport de ces techniques à travers l'**EBF** défini dans un précédent article. On avait estimé :

- $EBF \approx 45$ pour un MinMax brut, qui n'élague rien,
- $EBF \approx \sqrt{45} \approx 6.7$ pour un alpha-bêta **parfaitement** ordonné, dans le meilleur des cas.

En pratique, un bon moteur d'échecs moderne, combinant alpha-bêta, tri des coups, table de transposition et pruning avec perte, atteint un **EBF de l'ordre de 2 à 3**. C'est encore très largement en dessous du 6.7 théorique de l'alpha-bêta parfait : les techniques présentées dans cet article ne sont donc pas de simples optimisations marginales, elles sont responsables d'une bonne partie du gain final de profondeur de recherche que l'on observe dans un moteur réel.

# Le null move pruning

Une des techniques les plus utilisées est le **null move pruning**. L'idée de départ est presque provocante : et si on laissait, l'espace d'un instant, un joueur **passer son tour** ?

Aux échecs, passer son tour n'est pas un coup légal, mais rien n'empêche de le simuler dans notre arbre de recherche. Le raisonnement est le suivant : dans la quasi-totalité des positions, jouer un coup est toujours au moins aussi bon que ne rien jouer *(l'exception notable étant le zugzwang, une position où absolument tout coup empire la situation)*. Si, même en offrant à l'adversaire un tour gratuit, la position reste malgré tout favorable pour nous au-delà d'un certain seuil ($\beta$), il y a de fortes chances que la position soit de toute façon gagnante, et il devient inutile d'explorer plus en détail les coups réels à cet endroit.

<pre class="mermaid">
graph TD
  P0["Position (trait aux blancs)"]
  P0 -->|"coup nul"| N["Recherche à profondeur réduite"]
  N -->|"score ≥ β"| C["Coupure : on suppose la position gagnante"]
  P0 -->|"sinon"| E["Recherche normale des coups"]
</pre>

On économise ainsi l'exploration de tout un sous-arbre, au prix d'un risque : dans une position de zugzwang, ce raisonnement est faux, et on peut couper une branche qui aurait révélé un problème. C'est précisément le sens du mot "perte" dans "pruning avec perte".

# Les Late Move Reductions (LMR)

Une deuxième famille de techniques part d'une observation empirique : si notre tri des coups est de bonne qualité (voir l'article sur l'iterative deepening), alors les tout premiers coups explorés à un nœud ont statistiquement bien plus de chances d'être le meilleur coup que les coups explorés en dixième ou vingtième position.

Les **Late Move Reductions** *(réductions des coups tardifs)* exploitent directement cette observation : plutôt que de couper purement et simplement les coups tardifs, on les explore quand même, mais à une **profondeur réduite**.

<pre class="mermaid">
graph LR
  M1["Coup 1"] -->|"profondeur P"| S1["Recherche complète"]
  M2["Coup 2"] -->|"profondeur P"| S2["Recherche complète"]
  M3["Coup 3, 4, 5..."] -->|"profondeur P - R"| S3["Recherche réduite"]
</pre>

Si cette recherche réduite révèle malgré tout un coup meilleur que ce qui a été trouvé jusque là (on parle de **fail-high**), on relance alors une recherche complète à la profondeur `P` pour ce coup, cette fois sans réduction : l'heuristique s'est trompée, et on rattrape l'erreur. Sinon, on fait confiance à l'estimation réduite et on passe au coup suivant.

# Le futility pruning

Une troisième technique, le **futility pruning**, s'appuie cette fois sur le score matériel plutôt que sur l'ordre des coups. Proche des feuilles de l'arbre, si le score statique de la position (`Eval(position)`) est déjà tellement inférieur à $\alpha$ qu'aucun coup raisonnable ne semble pouvoir combler l'écart *(en ajoutant une marge de sécurité correspondant, par exemple, à la valeur d'une pièce mineure)*, on peut couper immédiatement la recherche à ce nœud plutôt que d'explorer chaque coup un par un.

Là encore, le risque est réel : un coup tactique inattendu (un sacrifice menant à un mat, par exemple) pourrait déjouer cette estimation. Mais statistiquement, ce cas de figure reste suffisamment rare pour que le gain de vitesse en vaille la peine.

# Un pari qui n'est jamais définitif

Il est important de nuancer le mot "perte" : ces techniques n'**écartent** pas un coup une bonne fois pour toutes, elles se contentent de **reporter** son exploration approfondie. Un coup jugé peu prometteur à la profondeur `P` de l'iterative deepening n'est pas supprimé de l'arbre : il sera à nouveau candidat, et réévalué avec les informations à jour (nouvelle table de transposition, nouveau tri des coups...), dès la profondeur `P+1`.

On retrouve ici une idée assez proche de celle de l'algorithme **A\*** en recherche de chemin : on ne visite pas l'espace de recherche uniformément, on l'**oriente** en consacrant l'essentiel de l'effort de calcul aux zones les plus prometteuses, sans pour autant s'interdire définitivement d'explorer les autres si elles se révèlent, plus tard, pertinentes.

# Un compromis assumé entre vitesse et exactitude

Ce que ces techniques ont en commun, c'est qu'elles remplacent une certitude coûteuse par un pari statistique bon marché, et rarement définitif. Chacune introduit un risque, différent à chaque fois : ignorer un zugzwang, mal évaluer un coup tardif, ou passer à côté d'une tactique enfouie. Un moteur d'échecs moderne combine généralement toutes ces techniques (et bien d'autres), en les réglant soigneusement pour que le gain en profondeur de recherche l'emporte, en moyenne, largement sur les erreurs ponctuelles qu'elles introduisent.

> C'est là toute la différence de philosophie avec l'alpha-bêta : on ne cherche plus à ne **jamais se tromper**, mais à **se tromper suffisamment rarement**, et de manière suffisamment bénigne, pour qu'au global l'algorithme joue mieux, plus vite.
