---
layout: post.njk
title: Le move ordering
date: 2026-09-08
section: Fonctionnement d'un moteur d'échecs
chapter: Explorer moins de branches
chapterOrder: 5
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

<table>
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

> Pour affiner encore ce tri, certains moteurs utilisent une évaluation plus poussée, la **SEE** *(<strong>S</strong>tatic <strong>E</strong>xchange <strong>E</strong>valuation)*, qui simule statiquement toute la séquence d'échanges sur une case donnée (reprises comprises) afin de déterminer si une capture est réellement gagnante une fois toutes les reprises effectuées, plutôt que de ne regarder que le premier échange.

# Les killer moves

Une fois les captures épuisées, on s'intéresse aux coups "calmes" (qui ne capturent rien). Ici, on ne dispose plus d'un critère aussi direct que MVV-LVA. On s'appuie alors sur l'historique de la recherche en cours : les **killer moves**.

L'idée est la suivante : si un coup calme a provoqué une coupure alpha-bêta (un **fail-high**, c'est-à-dire un coup dont le score dépasse $\beta$) à un nœud donné, il y a de bonnes chances qu'un coup similaire soit également bon dans une **position sœur**, c'est-à-dire un autre nœud situé à la **même profondeur** de l'arbre. On mémorise donc, pour chaque profondeur, les coups ayant récemment causé une coupure, et on les essaie en priorité dans les positions frères.

> À ne pas confondre avec le **fail-low** : lorsqu'aucun coup exploré à un nœud ne dépasse $\alpha$, le nœud renvoie simplement une borne supérieure, sans qu'aucun coup particulier ne se distingue. Seul le fail-high désigne un coup précis à retenir comme killer move.

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

<figure>
<svg viewBox="0 0 630 342" width="100%" style="max-width:630px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Deux heatmaps d'echiquier : cases de depart et cases d'arrivee des coups ayant provoque une coupure">
<style>
  .bt { font: 600 13px "Noto Sans", sans-serif; fill: #333; text-anchor: middle }
  .ax { font: 10px "Noto Sans", sans-serif; fill: #999; text-anchor: middle }
  .sq { font: 10px "Noto Sans", sans-serif; fill: #33404f; text-anchor: middle }
  .sq.lt { fill: #fff }
  .lg { font: 10px "Noto Sans", sans-serif; fill: #777 }
</style>
<defs><linearGradient id="hg"><stop offset="0" stop-color="#f7f6f2"/><stop offset="1" stop-color="#1f4e79"/></linearGradient></defs>
<text x="156" y="22" class="bt">Cases de départ</text>
<rect x="20" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="54" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="88" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="122" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="156" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="190" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="224" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="258" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="13" y="55.0" class="ax">8</text>
<rect x="20" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="54" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="88" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="122" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="156" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="190" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="224" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="258" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="13" y="89.0" class="ax">7</text>
<rect x="20" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="54" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="88" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="122" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="156" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="190" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="224" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="258" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="13" y="123.0" class="ax">6</text>
<rect x="20" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="54" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="88" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="122" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="156" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="190" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="224" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="258" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="13" y="157.0" class="ax">5</text>
<rect x="20" y="170" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="54" y="170" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="88" y="170" width="34" height="34" fill="#ccd4da" stroke="#e2dfd6" stroke-width="1"/>
<rect x="122" y="170" width="34" height="34" fill="#b6c4ce" stroke="#e2dfd6" stroke-width="1"/>
<rect x="156" y="170" width="34" height="34" fill="#bbc7d0" stroke="#e2dfd6" stroke-width="1"/>
<rect x="190" y="170" width="34" height="34" fill="#d0d8dc" stroke="#e2dfd6" stroke-width="1"/>
<rect x="224" y="170" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="258" y="170" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="13" y="191.0" class="ax">4</text>
<rect x="20" y="204" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="54" y="204" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="88" y="204" width="34" height="34" fill="#96aabc" stroke="#e2dfd6" stroke-width="1"/>
<text x="105.0" y="225.0" class="sq ">c3</text>
<rect x="122" y="204" width="34" height="34" fill="#c7d1d7" stroke="#e2dfd6" stroke-width="1"/>
<rect x="156" y="204" width="34" height="34" fill="#ccd4da" stroke="#e2dfd6" stroke-width="1"/>
<rect x="190" y="204" width="34" height="34" fill="#7591a9" stroke="#e2dfd6" stroke-width="1"/>
<text x="207.0" y="225.0" class="sq lt">f3</text>
<rect x="224" y="204" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="258" y="204" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="13" y="225.0" class="ax">3</text>
<rect x="20" y="238" width="34" height="34" fill="#dde2e3" stroke="#e2dfd6" stroke-width="1"/>
<rect x="54" y="238" width="34" height="34" fill="#d0d8dc" stroke="#e2dfd6" stroke-width="1"/>
<rect x="88" y="238" width="34" height="34" fill="#c1ccd4" stroke="#e2dfd6" stroke-width="1"/>
<rect x="122" y="238" width="34" height="34" fill="#8ba2b6" stroke="#e2dfd6" stroke-width="1"/>
<text x="139.0" y="259.0" class="sq ">d2</text>
<rect x="156" y="238" width="34" height="34" fill="#809aaf" stroke="#e2dfd6" stroke-width="1"/>
<text x="173.0" y="259.0" class="sq ">e2</text>
<rect x="190" y="238" width="34" height="34" fill="#b6c4ce" stroke="#e2dfd6" stroke-width="1"/>
<rect x="224" y="238" width="34" height="34" fill="#ccd4da" stroke="#e2dfd6" stroke-width="1"/>
<rect x="258" y="238" width="34" height="34" fill="#d7dde0" stroke="#e2dfd6" stroke-width="1"/>
<text x="13" y="259.0" class="ax">2</text>
<rect x="20" y="272" width="34" height="34" fill="#e1e5e6" stroke="#e2dfd6" stroke-width="1"/>
<rect x="54" y="272" width="34" height="34" fill="#60809d" stroke="#e2dfd6" stroke-width="1"/>
<text x="71.0" y="293.0" class="sq lt">b1</text>
<rect x="88" y="272" width="34" height="34" fill="#a1b3c2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="122" y="272" width="34" height="34" fill="#abbbc8" stroke="#e2dfd6" stroke-width="1"/>
<rect x="156" y="272" width="34" height="34" fill="#b6c4ce" stroke="#e2dfd6" stroke-width="1"/>
<rect x="190" y="272" width="34" height="34" fill="#96aabc" stroke="#e2dfd6" stroke-width="1"/>
<text x="207.0" y="293.0" class="sq ">f1</text>
<rect x="224" y="272" width="34" height="34" fill="#3f678b" stroke="#e2dfd6" stroke-width="1"/>
<text x="241.0" y="293.0" class="sq lt">g1</text>
<rect x="258" y="272" width="34" height="34" fill="#dde2e3" stroke="#e2dfd6" stroke-width="1"/>
<text x="13" y="293.0" class="ax">1</text>
<text x="37.0" y="321" class="ax">a</text>
<text x="71.0" y="321" class="ax">b</text>
<text x="105.0" y="321" class="ax">c</text>
<text x="139.0" y="321" class="ax">d</text>
<text x="173.0" y="321" class="ax">e</text>
<text x="207.0" y="321" class="ax">f</text>
<text x="241.0" y="321" class="ax">g</text>
<text x="275.0" y="321" class="ax">h</text>
<text x="484" y="22" class="bt">Cases d'arrivée</text>
<rect x="348" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="382" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="416" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="450" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="484" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="518" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="552" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="586" y="34" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="341" y="55.0" class="ax">8</text>
<rect x="348" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="382" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="416" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="450" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="484" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="518" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="552" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="586" y="68" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="341" y="89.0" class="ax">7</text>
<rect x="348" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="382" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="416" y="102" width="34" height="34" fill="#ccd4da" stroke="#e2dfd6" stroke-width="1"/>
<rect x="450" y="102" width="34" height="34" fill="#d7dde0" stroke="#e2dfd6" stroke-width="1"/>
<rect x="484" y="102" width="34" height="34" fill="#d4dbdf" stroke="#e2dfd6" stroke-width="1"/>
<rect x="518" y="102" width="34" height="34" fill="#c7d1d7" stroke="#e2dfd6" stroke-width="1"/>
<rect x="552" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="586" y="102" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="341" y="123.0" class="ax">6</text>
<rect x="348" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="382" y="136" width="34" height="34" fill="#abbbc8" stroke="#e2dfd6" stroke-width="1"/>
<rect x="416" y="136" width="34" height="34" fill="#b6c4ce" stroke="#e2dfd6" stroke-width="1"/>
<rect x="450" y="136" width="34" height="34" fill="#8fa5b8" stroke="#e2dfd6" stroke-width="1"/>
<text x="467.0" y="157.0" class="sq ">d5</text>
<rect x="484" y="136" width="34" height="34" fill="#8ba2b6" stroke="#e2dfd6" stroke-width="1"/>
<text x="501.0" y="157.0" class="sq ">e5</text>
<rect x="518" y="136" width="34" height="34" fill="#c1ccd4" stroke="#e2dfd6" stroke-width="1"/>
<rect x="552" y="136" width="34" height="34" fill="#b6c4ce" stroke="#e2dfd6" stroke-width="1"/>
<rect x="586" y="136" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="341" y="157.0" class="ax">5</text>
<rect x="348" y="170" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="382" y="170" width="34" height="34" fill="#c7d1d7" stroke="#e2dfd6" stroke-width="1"/>
<rect x="416" y="170" width="34" height="34" fill="#809aaf" stroke="#e2dfd6" stroke-width="1"/>
<text x="433.0" y="191.0" class="sq ">c4</text>
<rect x="450" y="170" width="34" height="34" fill="#3f678b" stroke="#e2dfd6" stroke-width="1"/>
<text x="467.0" y="191.0" class="sq lt">d4</text>
<rect x="484" y="170" width="34" height="34" fill="#355f85" stroke="#e2dfd6" stroke-width="1"/>
<text x="501.0" y="191.0" class="sq lt">e4</text>
<rect x="518" y="170" width="34" height="34" fill="#a1b3c2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="552" y="170" width="34" height="34" fill="#ccd4da" stroke="#e2dfd6" stroke-width="1"/>
<rect x="586" y="170" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="341" y="191.0" class="ax">4</text>
<rect x="348" y="204" width="34" height="34" fill="#d7dde0" stroke="#e2dfd6" stroke-width="1"/>
<rect x="382" y="204" width="34" height="34" fill="#c1ccd4" stroke="#e2dfd6" stroke-width="1"/>
<rect x="416" y="204" width="34" height="34" fill="#60809d" stroke="#e2dfd6" stroke-width="1"/>
<text x="433.0" y="225.0" class="sq lt">c3</text>
<rect x="450" y="204" width="34" height="34" fill="#abbbc8" stroke="#e2dfd6" stroke-width="1"/>
<rect x="484" y="204" width="34" height="34" fill="#b2c0cb" stroke="#e2dfd6" stroke-width="1"/>
<rect x="518" y="204" width="34" height="34" fill="#4a7091" stroke="#e2dfd6" stroke-width="1"/>
<text x="535.0" y="225.0" class="sq lt">f3</text>
<rect x="552" y="204" width="34" height="34" fill="#b6c4ce" stroke="#e2dfd6" stroke-width="1"/>
<rect x="586" y="204" width="34" height="34" fill="#ccd4da" stroke="#e2dfd6" stroke-width="1"/>
<text x="341" y="225.0" class="ax">3</text>
<rect x="348" y="238" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="382" y="238" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="416" y="238" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="450" y="238" width="34" height="34" fill="#d0d8dc" stroke="#e2dfd6" stroke-width="1"/>
<rect x="484" y="238" width="34" height="34" fill="#ccd4da" stroke="#e2dfd6" stroke-width="1"/>
<rect x="518" y="238" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="552" y="238" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="586" y="238" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="341" y="259.0" class="ax">2</text>
<rect x="348" y="272" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="382" y="272" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="416" y="272" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="450" y="272" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="484" y="272" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="518" y="272" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="552" y="272" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<rect x="586" y="272" width="34" height="34" fill="#f7f6f2" stroke="#e2dfd6" stroke-width="1"/>
<text x="341" y="293.0" class="ax">1</text>
<text x="365.0" y="321" class="ax">a</text>
<text x="399.0" y="321" class="ax">b</text>
<text x="433.0" y="321" class="ax">c</text>
<text x="467.0" y="321" class="ax">d</text>
<text x="501.0" y="321" class="ax">e</text>
<text x="535.0" y="321" class="ax">f</text>
<text x="569.0" y="321" class="ax">g</text>
<text x="603.0" y="321" class="ax">h</text>
<rect x="245.0" y="326" width="140" height="8" fill="url(#hg)" stroke="#e2dfd6"/>
<text x="239.0" y="333" class="lg" text-anchor="end">rare</text>
<text x="391.0" y="333" class="lg">fréquent</text>
</svg>
<figcaption>Exemple illustratif d'une table d'history heuristic en fin de recherche : plus une case est foncée, plus les coups partant de cette case (à gauche) ou y arrivant (à droite) ont provoqué de coupures. Les coups vers le centre et les sorties de cavalier ressortent nettement, et seront donc essayés en priorité dans les positions suivantes.</figcaption>
</figure>

# Un tri, jamais une certitude

Ces heuristiques peuvent se combiner naturellement, dans un ordre décroissant de fiabilité :

1. le coup issu de la table de transposition,
2. les captures, triées par MVV-LVA / SEE,
3. les killer moves,
4. les coups restants, triés par history heuristic.

Aucune de ces techniques ne garantit de trouver le meilleur coup en premier : ce ne sont que des paris informés, construits sur des statistiques et des résultats de recherches passées. Mais comme on l'a vu, même un tri imparfait suffit à rapprocher très fortement l'alpha-bêta de sa performance théorique optimale, ce qui en fait l'un des leviers d'optimisation les plus rentables d'un moteur d'échecs.
