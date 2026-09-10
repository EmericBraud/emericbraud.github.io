---
layout: post.njk
title: L'iterative deepening
date: 2026-09-08
chapter: Fondamentaux
chapterOrder: 2
---
# Iterative Deepening
L'algorithme alpha-bêta n'est efficace que si l'on explore les meilleurs coups en premiers. Nous explorerons par la suite certaines heuristiques permettant d'explorer en priorité certains coups paraissant prometteurs.

Si l'on se contente de lancer une recherche alpha-bêta directement à la profondeur `P` visée, on ne dispose d'aucune information pour trier les coups avant même d'avoir commencé à chercher.

C'est ici qu'intervient l'**iterative deepening** *(approfondissement itératif)* : plutôt que de chercher directement à la profondeur `P`, on effectue une succession de recherches complètes, à profondeur croissante :

<pre class="mermaid">
graph LR
  D1["Profondeur 1"] --> D2["Profondeur 2"] --> D3["Profondeur 3"] --> D4["..."] --> DP["Profondeur P"]
</pre>

À première vue, cela semble absurde : on recalcule à chaque itération tout le travail déjà fait aux profondeurs précédentes. Pourtant, cette approche apporte deux bénéfices majeurs.

# Un tri des coups qui accélère la recherche

Chaque recherche à la profondeur `P-1` nous indique quel coup a semblé être le meilleur à cette profondeur. Rien ne garantit que ce coup restera le meilleur à la profondeur `P`, mais il s'agit d'une excellente estimation : on peut donc l'explorer **en priorité** lors de la recherche suivante.

Or on a vu que l'efficacité de l'élagage alpha-bêta dépend directement de la qualité du tri des coups : plus le meilleur coup est exploré tôt, plus les coupures se déclenchent tôt et plus l'algorithme est rapide.

Le résultat est contre-intuitif : bien que l'on refasse tout le travail des profondeurs précédentes, le gain apporté par le meilleur tri des coups **dépasse largement le coût des itérations précédentes**. En pratique, la somme du temps passé sur toutes les profondeurs `1` à `P` est souvent plus rapide qu'une recherche directe et mal triée à la profondeur `P`.

# Un résultat exploitable à tout moment

Le second avantage est tout aussi important, en particulier dans une partie chronométrée. Aux échecs, chaque joueur dispose d'un temps de réflexion limité : il faut donc pouvoir arrêter la recherche à tout moment et disposer immédiatement d'un coup à jouer.

Avec une recherche directe à profondeur fixe `P`, si le temps imparti s'épuise avant la fin de la recherche, on ne dispose d'**aucun résultat exploitable** : l'arbre n'a été que partiellement exploré, et rien ne garantit que le meilleur coup trouvé jusque là soit fiable.

Avec l'iterative deepening, la situation est bien différente : dès que la recherche à la profondeur `1` est terminée, on dispose déjà d'un coup à jouer. Puis à la profondeur `2`, puis `3`, et ainsi de suite. Il suffit donc d'arrêter la recherche dès que le temps imparti est écoulé, et de jouer le meilleur coup trouvé par la **dernière profondeur entièrement terminée**.

> On dit que l'iterative deepening rend la recherche **anytime** : elle peut être interrompue à n'importe quel instant tout en renvoyant un résultat exploitable.

Nous verrons par la suite comment stocker, au moins partiellement, l'arbre de recherche d'une itération à l'autre, afin de réutiliser les informations calculées à une profondeur pour accélérer encore davantage la recherche à la profondeur suivante.
