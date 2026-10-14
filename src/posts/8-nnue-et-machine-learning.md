---
layout: post.njk
title: Le NNUE, une architecture de machine learning révolutionnaire
date: 2026-10-14
section: Techniques de programmation
chapter: Apprendre à évaluer
chapterOrder: 7
---

5 décembre 2017 : DeepMind annonce AlphaZero, capable de battre [Stockfish 8](https://stockfishchess.org/), le plus fort moteur d'échecs de l'époque, après quelques heures d'auto-jeu. La nouvelle fait le tour du monde, mais elle est à nuancer : AlphaZero tourne sur des TPU, Stockfish sur un simple CPU.

Le match n'oppose donc pas seulement deux moteurs, mais **deux façons d'évaluer une position**.

# L'arrivée de l'IA dans les échecs

Pendant soixante ans, pour développer un moteur d'échecs, on écrivait [une fonction d'évaluation](/posts/0-concepts-généraux/) qu'on affinait ensuite, par exemple par [Texel tuning](https://www.chessprogramming.org/Texel%27s_Tuning_Method). C'était léger en calculs, mais imprécis et borné par le **biais humain** : toute la connaissance venait de l'intuition des plus grands joueurs.

AlphaZero a renversé la table. Aucune règle écrite à la main ni connaissance humaine préétablie. Au lieu de ça, un [ResNet](https://en.wikipedia.org/wiki/Residual_neural_network) qui apprend seul, par auto-jeu et apprentissage par renforcement _(reinforcement learning)_. L'approche est révolutionnaire pour l'époque : l'évaluation des positions devient bien plus précise. Mais elle a un coût : il lui faut un [TPU](https://en.wikipedia.org/wiki/Tensor_processing_unit) ou un GPU, et l'inférence d'un aussi gros réseau de neurones est lente.

Pour Stockfish, la question ne se pose même pas : le moteur doit rester portable, donc tourner sur un CPU seul. Et deux obstacles s'y opposeraient de toute façon. Le premier est matériel : un moteur alpha-bêta comme [celui que nous avons décrit](/posts/1-pruning-alpha-beta/) évalue des dizaines de millions de positions par seconde, avec une évaluation qui coûte quelques centaines d'opérations et des structures de données qui tiennent dans le cache ; une évaluation AlphaZero, elle, exige un aller-retour CPU → GPU → CPU, dont la latence interdit un tel rythme.

<figure>
<svg viewBox="0 0 840 285" width="100%" style="max-width:840px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Trajet d une position dans la hierarchie memoire : caches L1 L2 L3 du CPU, RAM, bus PCIe, VRAM et caches du GPU, puis retour">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .zt { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .nm { font-size: 13px; font-weight: 600; text-anchor: middle }
  .lt { font-size: 10.5px; fill: #8a8372; text-anchor: middle }
  .bus { font-size: 10.5px; font-weight: 600; letter-spacing: .06em; fill: #9c5b4a; text-anchor: middle }
  .bus.s { font-size: 10px; font-weight: 400; letter-spacing: 0 }
  .ret { font-size: 11px; fill: #9c5b4a; text-anchor: middle }
  .zone { fill: #fcfbf8; stroke: #ded9cd; stroke-dasharray: 4 3 }
  .cpu { fill: #eaf0f7; stroke: #3f6b9c }
  .gpu { fill: #e9f2ee; stroke: #4a7f6b }
  .ram { fill: #f4f2ec; stroke: #8a8372 }
  .fx { fill: none; stroke: #b9b2a2; stroke-width: 1.3 }
  .rt { fill: none; stroke: #c98b7b; stroke-width: 1.3; stroke-dasharray: 5 4 }
</style>
<defs>
<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#b9b2a2"/></marker>
<marker id="rr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#c98b7b"/></marker>
</defs>
<text x="420" y="18" class="ttl">LE TRAJET D'UNE POSITION JUSQU'AU RÉSEAU</text>
<rect x="12" y="70" width="314" height="104" rx="3" class="zone"/>
<text x="169" y="60" class="zt">CPU</text>
<rect x="516" y="70" width="312" height="104" rx="3" class="zone"/>
<text x="672" y="60" class="zt">CARTE GRAPHIQUE</text>
<rect x="20" y="88" width="86" height="68" class="cpu"/>
<text x="63" y="118" class="nm" fill="#3f6b9c">L1</text>
<text x="63" y="138" class="lt">~1 ns</text>
<rect x="126" y="88" width="86" height="68" class="cpu"/>
<text x="169" y="118" class="nm" fill="#3f6b9c">L2</text>
<text x="169" y="138" class="lt">~5 ns</text>
<rect x="232" y="88" width="86" height="68" class="cpu"/>
<text x="275" y="118" class="nm" fill="#3f6b9c">L3</text>
<text x="275" y="138" class="lt">~15 ns</text>
<rect x="338" y="88" width="86" height="68" class="ram"/>
<text x="381" y="118" class="nm" fill="#6b6459">RAM</text>
<text x="381" y="138" class="lt">~100 ns</text>
<rect x="522" y="88" width="86" height="68" class="gpu"/>
<text x="565" y="118" class="nm" fill="#4a7f6b">VRAM</text>
<text x="565" y="138" class="lt">~300 ns</text>
<rect x="628" y="88" width="86" height="68" class="gpu"/>
<text x="671" y="118" class="nm" fill="#4a7f6b">L2 GPU</text>
<text x="671" y="138" class="lt">cache</text>
<rect x="734" y="88" width="86" height="68" class="gpu"/>
<text x="777" y="118" class="nm" fill="#4a7f6b">L1 GPU</text>
<text x="777" y="138" class="lt">le réseau</text>
<path d="M106 122 H124" class="fx" marker-end="url(#ar)"/>
<path d="M212 122 H230" class="fx" marker-end="url(#ar)"/>
<path d="M318 122 H336" class="fx" marker-end="url(#ar)"/>
<path d="M424 122 H520" class="fx" marker-end="url(#ar)"/>
<path d="M608 122 H626" class="fx" marker-end="url(#ar)"/>
<path d="M714 122 H732" class="fx" marker-end="url(#ar)"/>
<text x="473" y="108" class="bus">PCIe</text>
<text x="473" y="142" class="bus s">~1 µs</text>
<path d="M777 156 V250 H63 V160" class="rt" marker-end="url(#rr)"/>
<text x="420" y="242" class="ret">le score retraverse la même hiérarchie en sens inverse</text>
</svg>
<figcaption>Dans le CPU, une évaluation coûte quelques nanosecondes ; dès qu'il faut changer de puce, elle se compte en microsecondes.</figcaption>
</figure>

Le second obstacle est structurel. L'alpha-bêta explore un arbre **séquentiel**, où chaque nœud attend le résultat du précédent. Si on voulait appliquer un ResNet à un algorithme alpha-bêta, la latence serait payée à chaque nœud. AlphaZero y substitue une recherche arborescente de Monte-Carlo _([Monte-Carlo Tree Search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search), ou MCTS)_ : les positions partent vers le GPU par lots, et la latence n'est payée qu'une fois pour des milliers de nœuds, au prix d'un arbre non plus déterministe, mais **statistique**.

# Le retour du roi : Stockfish et le NNUE
Mais Stockfish n'avait pas dit son dernier mot. En 2018, [Yu Nasu](https://chessprogramming.org/Yu_Nasu) publie pour le shogi une architecture que les développeurs reprennent : un **[Efficiently Updatable Neural Network](https://www.chessprogramming.org/NNUE)** _(NNUE : l'acronyme prend les initiales à l'envers, ne me demandez pas pourquoi 🤷)_.

## Un arbre incrémental, une évaluation qui ne l'est pas

L'idée part d'une observation simple : l'arbre de recherche est **incrémental** par nature. Chaque nœud représente une position, et deux nœuds voisins ne diffèrent dans l'arbre que d'un demi-coup.

<figure>
<div class="boardrow">
  <div>
    <chess-board class="hl-e2" position="5rk1/5ppp/2np4/8/2BP4/5N2/4PPPP/5RK1 w - - 0 1" orientation="white" style="width: 250px; max-width: 100%;"></chess-board>
    <p class="boardcap">avant le coup, le pion est en e2</p>
  </div>
  <div>
    <chess-board class="hl-e4" position="5rk1/5ppp/2np4/8/2BPP3/5N2/5PPP/5RK1 b - - 0 1" orientation="white" style="width: 250px; max-width: 100%;"></chess-board>
    <p class="boardcap">après le coup, le pion est en e4</p>
  </div>
</div>
<figcaption>Deux nœuds voisins : un demi-coup les sépare, deux entrées sur trente changent.</figcaption>
</figure>

On comprend alors que faire tourner un réseau de neurones énorme à chaque position de l'arbre est un gaspillage : l'entrée ne change qu'à 1 % d'un nœud au suivant. On serait alors tenté de mettre à jour l'état du réseau de manière incrémentale.

C'est impossible : dans un réseau non linéaire, chaque couche transforme l'information au lieu de la transporter, si bien qu'une variation minuscule en entrée se propage partout. Une mise à jour incrémentale exige en effet la **linéarité** : pour écrire $f(x + \delta) = f(x) + f(\delta)$, il faut que $f$ soit linéaire. Or un réseau purement linéaire ne servirait à rien, car composer des couches linéaires revient à n'en avoir qu'une. Sans non-linéarité, pas d'intelligence ; avec elle, pas d'incrémental.

## Encoder l'échiquier autrement

L'astuce est de déplacer le problème : rendre **linéaire tout le calcul coûteux**, et repousser la non-linéarité dans une partie minuscule du réseau. Première étape : changer la représentation de l'échiquier, pour un vecteur **binaire** et très **creux** _(sparse)_ dont chaque entrée décrit une combinaison précise, comme le triplet (case du roi, case de la pièce, type de pièce) de l'encodage `HalfKP`.

<figure>
<div class="boardrow">
  <div>
    <chess-board position="5rk1/5ppp/2np4/8/2BP4/5N2/4PPPP/5RK1 w - - 0 1" orientation="white" style="width: 220px; max-width: 100%;"></chess-board>
    <p class="boardcap">la position</p>
  </div>
  <p class="boardarrow">&rarr;</p>
  <div style="width: 320px; max-width: 100%;">
<svg viewBox="0 0 320 190" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Vecteur binaire creux de 41 024 entrees, dont une trentaine seulement sont actives">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .note { font-size: 11px; fill: #8a8372; text-anchor: middle }
  .cell { fill: #f7f6f2; stroke: #e3dfd5 }
  .cell.a { fill: #3f6b9c; stroke: #2f5580 }
</style>
<text x="160" y="16" class="ttl">41 024 ENTRÉES BINAIRES</text>
<rect x="32" y="40" width="16" height="12" class="cell"/>
<rect x="48" y="40" width="16" height="12" class="cell a"/>
<rect x="64" y="40" width="16" height="12" class="cell"/>
<rect x="80" y="40" width="16" height="12" class="cell"/>
<rect x="96" y="40" width="16" height="12" class="cell"/>
<rect x="112" y="40" width="16" height="12" class="cell"/>
<rect x="128" y="40" width="16" height="12" class="cell"/>
<rect x="144" y="40" width="16" height="12" class="cell"/>
<rect x="160" y="40" width="16" height="12" class="cell"/>
<rect x="176" y="40" width="16" height="12" class="cell a"/>
<rect x="192" y="40" width="16" height="12" class="cell"/>
<rect x="208" y="40" width="16" height="12" class="cell"/>
<rect x="224" y="40" width="16" height="12" class="cell"/>
<rect x="240" y="40" width="16" height="12" class="cell"/>
<rect x="256" y="40" width="16" height="12" class="cell"/>
<rect x="272" y="40" width="16" height="12" class="cell"/>
<rect x="32" y="52" width="16" height="12" class="cell"/>
<rect x="48" y="52" width="16" height="12" class="cell"/>
<rect x="64" y="52" width="16" height="12" class="cell"/>
<rect x="80" y="52" width="16" height="12" class="cell"/>
<rect x="96" y="52" width="16" height="12" class="cell"/>
<rect x="112" y="52" width="16" height="12" class="cell"/>
<rect x="128" y="52" width="16" height="12" class="cell a"/>
<rect x="144" y="52" width="16" height="12" class="cell"/>
<rect x="160" y="52" width="16" height="12" class="cell"/>
<rect x="176" y="52" width="16" height="12" class="cell"/>
<rect x="192" y="52" width="16" height="12" class="cell"/>
<rect x="208" y="52" width="16" height="12" class="cell"/>
<rect x="224" y="52" width="16" height="12" class="cell"/>
<rect x="240" y="52" width="16" height="12" class="cell"/>
<rect x="256" y="52" width="16" height="12" class="cell a"/>
<rect x="272" y="52" width="16" height="12" class="cell"/>
<rect x="32" y="64" width="16" height="12" class="cell"/>
<rect x="48" y="64" width="16" height="12" class="cell"/>
<rect x="64" y="64" width="16" height="12" class="cell"/>
<rect x="80" y="64" width="16" height="12" class="cell"/>
<rect x="96" y="64" width="16" height="12" class="cell"/>
<rect x="112" y="64" width="16" height="12" class="cell"/>
<rect x="128" y="64" width="16" height="12" class="cell"/>
<rect x="144" y="64" width="16" height="12" class="cell"/>
<rect x="160" y="64" width="16" height="12" class="cell"/>
<rect x="176" y="64" width="16" height="12" class="cell a"/>
<rect x="192" y="64" width="16" height="12" class="cell"/>
<rect x="208" y="64" width="16" height="12" class="cell"/>
<rect x="224" y="64" width="16" height="12" class="cell"/>
<rect x="240" y="64" width="16" height="12" class="cell"/>
<rect x="256" y="64" width="16" height="12" class="cell"/>
<rect x="272" y="64" width="16" height="12" class="cell"/>
<rect x="32" y="76" width="16" height="12" class="cell"/>
<rect x="48" y="76" width="16" height="12" class="cell"/>
<rect x="64" y="76" width="16" height="12" class="cell"/>
<rect x="80" y="76" width="16" height="12" class="cell"/>
<rect x="96" y="76" width="16" height="12" class="cell a"/>
<rect x="112" y="76" width="16" height="12" class="cell"/>
<rect x="128" y="76" width="16" height="12" class="cell"/>
<rect x="144" y="76" width="16" height="12" class="cell"/>
<rect x="160" y="76" width="16" height="12" class="cell"/>
<rect x="176" y="76" width="16" height="12" class="cell"/>
<rect x="192" y="76" width="16" height="12" class="cell"/>
<rect x="208" y="76" width="16" height="12" class="cell"/>
<rect x="224" y="76" width="16" height="12" class="cell a"/>
<rect x="240" y="76" width="16" height="12" class="cell"/>
<rect x="256" y="76" width="16" height="12" class="cell"/>
<rect x="272" y="76" width="16" height="12" class="cell"/>
<rect x="32" y="88" width="16" height="12" class="cell"/>
<rect x="48" y="88" width="16" height="12" class="cell"/>
<rect x="64" y="88" width="16" height="12" class="cell"/>
<rect x="80" y="88" width="16" height="12" class="cell"/>
<rect x="96" y="88" width="16" height="12" class="cell a"/>
<rect x="112" y="88" width="16" height="12" class="cell"/>
<rect x="128" y="88" width="16" height="12" class="cell"/>
<rect x="144" y="88" width="16" height="12" class="cell"/>
<rect x="160" y="88" width="16" height="12" class="cell"/>
<rect x="176" y="88" width="16" height="12" class="cell"/>
<rect x="192" y="88" width="16" height="12" class="cell a"/>
<rect x="208" y="88" width="16" height="12" class="cell"/>
<rect x="224" y="88" width="16" height="12" class="cell"/>
<rect x="240" y="88" width="16" height="12" class="cell"/>
<rect x="256" y="88" width="16" height="12" class="cell"/>
<rect x="272" y="88" width="16" height="12" class="cell"/>
<text x="160" y="126" class="note">une trentaine sont actives</text>
<text x="160" y="144" class="note">toutes les autres valent 0</text>
<text x="160" y="178" class="note">une entrée = (case du roi, case de la pièce, type de pièce)</text>
</svg>
  </div>
</div>
<figcaption>41 024 entrées binaires, dont une trentaine actives. Schéma non à l'échelle.</figcaption>
</figure>

L'intelligence est ainsi **pré-encodée dans les features** plutôt que laissée à des couches profondes : un fou sur une diagonale devient une entrée active parmi des milliers, dont le réseau apprend le poids.

## L'accumulateur

Deuxième étape : ajouter une première couche **linéaire** à l'entrée du réseau, l'**accumulateur**. Sa sortie n'étant qu'une somme des colonnes de poids des features actives, passer d'un nœud au suivant revient à retirer les colonnes de celles qui s'éteignent et à ajouter celles qui s'allument.

<figure>
<svg viewBox="0 0 720 326" width="100%" style="max-width:720px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mise a jour incrementale de l accumulateur : soustraction et addition de colonnes de poids">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .nm { font-size: 13px; font-weight: 600; text-anchor: middle }
  .lt { font-size: 10.5px; fill: #8a8372; text-anchor: middle }
  .note { font-size: 11px; fill: #8a8372; text-anchor: middle }
  .note.s { text-anchor: start }
  .op { font-size: 21px; font-weight: 600; fill: #6b6459; text-anchor: middle }
  .sym { font-size: 12.5px; font-weight: 600; text-anchor: middle }
  .bx-in { fill: #f4f2ec; stroke: #8a8372 }
  .bx-acc { fill: #eaf0f7; stroke: #3f6b9c }
  .bx-sm { fill: #e9f2ee; stroke: #4a7f6b }
  .col-acc { fill: #eaf0f7; stroke: #3f6b9c }
  .col-off { fill: #f9ece7; stroke: #c98b7b }
  .col-on { fill: #e9f2ee; stroke: #4a7f6b }
  .cell { fill: #f7f6f2; stroke: #e3dfd5 }
  .cell.a { fill: #3f6b9c; stroke: #2f5580 }
  .fx { fill: none; stroke: #b9b2a2; stroke-width: 1.3 }
  .br { fill: none; stroke: #ded9cd }
</style>
<text x="360" y="16" class="ttl">LA MISE À JOUR DE L'ACCUMULATEUR</text>
<rect x="202" y="76" width="52" height="120" class="col-acc"/>
<line x1="202" y1="93.1" x2="254" y2="93.1" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="202" y1="110.3" x2="254" y2="110.3" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="202" y1="127.4" x2="254" y2="127.4" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="202" y1="144.6" x2="254" y2="144.6" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="202" y1="161.7" x2="254" y2="161.7" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="202" y1="178.9" x2="254" y2="178.9" stroke="#ffffff" stroke-opacity=".55"/>
<rect x="290" y="76" width="52" height="120" class="col-off"/>
<line x1="290" y1="93.1" x2="342" y2="93.1" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="290" y1="110.3" x2="342" y2="110.3" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="290" y1="127.4" x2="342" y2="127.4" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="290" y1="144.6" x2="342" y2="144.6" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="290" y1="161.7" x2="342" y2="161.7" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="290" y1="178.9" x2="342" y2="178.9" stroke="#ffffff" stroke-opacity=".55"/>
<rect x="378" y="76" width="52" height="120" class="col-on"/>
<line x1="378" y1="93.1" x2="430" y2="93.1" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="378" y1="110.3" x2="430" y2="110.3" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="378" y1="127.4" x2="430" y2="127.4" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="378" y1="144.6" x2="430" y2="144.6" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="378" y1="161.7" x2="430" y2="161.7" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="378" y1="178.9" x2="430" y2="178.9" stroke="#ffffff" stroke-opacity=".55"/>
<rect x="466" y="76" width="52" height="120" class="col-acc"/>
<line x1="466" y1="93.1" x2="518" y2="93.1" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="466" y1="110.3" x2="518" y2="110.3" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="466" y1="127.4" x2="518" y2="127.4" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="466" y1="144.6" x2="518" y2="144.6" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="466" y1="161.7" x2="518" y2="161.7" stroke="#ffffff" stroke-opacity=".55"/>
<line x1="466" y1="178.9" x2="518" y2="178.9" stroke="#ffffff" stroke-opacity=".55"/>
<text x="272" y="144" class="op">−</text>
<text x="360" y="144" class="op">+</text>
<text x="448" y="144" class="op">=</text>
<text x="228.0" y="222" class="sym" fill="#3f6b9c">A</text>
<text x="316.0" y="222" class="sym" fill="#9c5b4a">w(e2)</text>
<text x="404.0" y="222" class="sym" fill="#4a7f6b">w(e4)</text>
<text x="492.0" y="222" class="sym" fill="#3f6b9c">A′</text>
<text x="360" y="266" class="note">A : l'accumulateur avant le coup, A′ : le même, à jour</text>
<text x="360" y="288" class="note">on retire la colonne de l'entrée qui s'éteint, on ajoute celle de l'entrée qui s'allume</text>
<text x="360" y="310" class="note">chaque colonne est un vecteur de 256 valeurs : aucune réévaluation complète n'est nécessaire</text>
</svg>
<figcaption>Mise à jour par soustraction et addition de colonnes, sans reprojeter l'échiquier.</figcaption>
</figure>

L'accumulateur est donc une projection : 41 024 entrées binaires, quelques centaines de valeurs continues en sortie, dont un exemplaire par camp. Les réseaux actuels en emploient 1024, parfois 3072, contre 256 pour le premier NNUE de Stockfish.

{% plus "Le cas du roi" %}

L'accumulateur n'est pas magique pour autant. Dans l'encodage `HalfKP`, chaque entrée est indexée par la case du roi : tant que le roi ne bouge pas, la mise à jour incrémentale fonctionne. Dès qu'il se déplace, en revanche, toutes les entrées actives changent d'indice, et l'accumulateur doit être **entièrement reconstruit**. Stockfish parle de _refresh trigger_ : l'événement qui impose ce recalcul complet.

Les moteurs modernes amortissent ce coût en gardant en réserve des accumulateurs déjà calculés pour d'autres positions du roi, quitte à ne mettre à jour que la différence par rapport à eux. Le principe reste : l'incrémentalité a ses exceptions, et le roi en est la principale.

{% endplus %}

## Le piège de l'accumulation

Mettre à jour une somme flottante au fil de l'eau a un défaut connu : **les erreurs s'accumulent**. Chaque addition arrondie écarte un peu l'accumulateur de la valeur qu'il aurait eue s'il était recalculé depuis zéro, et après des millions de mises à jour, la dérive compte. La réponse des NNUE : **quantifier le réseau en entiers**, dont l'addition est exacte, au prix d'une perte de précision.

{% plus "Le SIMD" %}

La quantification a de gros avantages, dont la vitesse d'inférence. Sommer ou multiplier des entiers 8 bits sur des registres de 128, 256 ou 512 bits permet de faire du SIMD : en une unique instruction CPU, on peut réaliser jusqu'à 64 opérations simultanées !

{% endplus %}

## Un petit réseau non linéaire par-dessus

Reste la partie réellement intelligente, justement celle que l'on ne peut pas incrémenter. Elle est réduite au minimum : branché à l'accumulateur, un tout petit réseau non linéaire est recalculé à chaque évaluation. Dans le premier NNUE de Stockfish, les 512 valeurs traversent deux couches de 32 neurones, puis un neurone de sortie qui donne le score.

<figure>
<svg viewBox="0 0 1910 920" width="100%" style="max-width:1910px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Schema d un NNUE lu de gauche a droite : position aux echecs encodee en features binaires, neurones de l accumulateur, puis petite tete non lineaire et score"> <style>   text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }   .nnue-ttl { font-size: 17px; font-weight: 600; letter-spacing: .1em; fill: #8a8372; text-anchor: middle }   .nnue-zt { font-size: 15px; font-weight: 600; letter-spacing: .14em; fill: #8a8372; text-anchor: middle }   .nnue-zt-b { font-size: 15px; font-weight: 600; letter-spacing: .14em; fill: #3f6b9c; text-anchor: middle }   .nnue-zt-g { font-size: 12.5px; font-weight: 600; letter-spacing: .16em; fill: #4a7f6b; text-anchor: middle }   .nnue-lbl { font-size: 15px; fill: #8a8372 }   .nnue-sub { font-size: 13px; fill: #8a8372; text-anchor: middle }   .nnue-off { stroke: #ded9cd; stroke-width: .7; opacity: .4 }   .nnue-on { stroke: #3f6b9c; stroke-width: 1.3; opacity: .55 }   .nnue-li { stroke: #b0aa9b; stroke-width: 1; stroke-opacity: .45 }   .nnue-masque { fill: #fdfcfa }   @media (prefers-color-scheme: dark) { .nnue-masque { fill: #f7f6f2 } } </style>  <text x="955.0" y="46" class="nnue-ttl">LE MAILLAGE D'UN NNUE</text> <text x="955.0" y="80" class="nnue-sub">Chaque neurone de l'accumulateur somme les colonnes de poids des features allumées.</text> <g> <rect x="78.0" y="250.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="104.0" y="250.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="130.0" y="250.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="156.0" y="250.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="182.0" y="250.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="208.0" y="250.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="234.0" y="250.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="260.0" y="250.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="78.0" y="276.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="104.0" y="276.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="130.0" y="276.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="156.0" y="276.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="182.0" y="276.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="208.0" y="276.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="234.0" y="276.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="260.0" y="276.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="78.0" y="302.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="104.0" y="302.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="130.0" y="302.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="156.0" y="302.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="182.0" y="302.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="208.0" y="302.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="234.0" y="302.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="260.0" y="302.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="78.0" y="328.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="104.0" y="328.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="130.0" y="328.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="156.0" y="328.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="182.0" y="328.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="208.0" y="328.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="234.0" y="328.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="260.0" y="328.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="78.0" y="354.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="104.0" y="354.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="130.0" y="354.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="156.0" y="354.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="182.0" y="354.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="208.0" y="354.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="234.0" y="354.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="260.0" y="354.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="78.0" y="380.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="104.0" y="380.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="130.0" y="380.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="156.0" y="380.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="182.0" y="380.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="208.0" y="380.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="234.0" y="380.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="260.0" y="380.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="78.0" y="406.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="104.0" y="406.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="130.0" y="406.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="156.0" y="406.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="182.0" y="406.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="208.0" y="406.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="234.0" y="406.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="260.0" y="406.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="78.0" y="432.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="104.0" y="432.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="130.0" y="432.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="156.0" y="432.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="182.0" y="432.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="208.0" y="432.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="234.0" y="432.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="260.0" y="432.0" width="26.0" height="26.0" fill="#f2efe6"/> </g> <rect x="78.0" y="250.0" width="208" height="208" fill="none" stroke="#8a8372" stroke-width="1.4"/> <g> <text x="91.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♜</text> <text x="117.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♞</text> <text x="143.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♝</text> <text x="169.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♛</text> <text x="195.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♚</text> <text x="221.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♝</text> <text x="247.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♞</text> <text x="273.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♜</text> <text x="91.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="117.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="143.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="169.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="195.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="221.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="247.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="273.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="195.0" y="374.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="91.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="117.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="143.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="169.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="221.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="247.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="273.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="91.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♖</text> <text x="117.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♘</text> <text x="143.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♗</text> <text x="169.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♕</text> <text x="195.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♔</text> <text x="221.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♗</text> <text x="247.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♘</text> <text x="273.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♖</text> </g> <line x1="78.0" y1="238" x2="286" y2="238" stroke="#b9b2a2" stroke-width="1.4"/> <text x="182" y="224" class="nnue-zt">POSITION</text> <g> <rect x="310.0" y="165.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="189.0" width="20.0" height="20.0" rx="3" fill="#2f3a44" stroke="#1e262e" stroke-width="1.1"/> <rect x="310.0" y="213.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="237.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="261.0" width="20.0" height="20.0" rx="3" fill="#2f3a44" stroke="#1e262e" stroke-width="1.1"/> <rect x="310.0" y="285.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="309.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="333.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="357.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="381.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="405.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="429.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="453.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="477.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="501.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="525.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="549.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="573.0" width="20.0" height="20.0" rx="3" fill="#2f3a44" stroke="#1e262e" stroke-width="1.1"/> <rect x="310.0" y="597.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="621.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="645.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="669.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="693.0" width="20.0" height="20.0" rx="3" fill="#2f3a44" stroke="#1e262e" stroke-width="1.1"/> <rect x="310.0" y="717.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="741.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="765.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> </g> <g> <line x1="330.0" y1="175.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="200.0" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="200.0" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="200.0" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="200.0" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="261.1" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="261.1" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="261.1" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="261.1" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="322.2" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="322.2" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="322.2" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="322.2" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="383.3" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="383.3" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="383.3" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="383.3" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="444.4" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="444.4" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="444.4" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="444.4" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="505.6" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="505.6" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="505.6" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="505.6" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="566.7" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="566.7" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="566.7" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="566.7" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="627.8" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="627.8" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="627.8" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="627.8" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="688.9" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="688.9" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="688.9" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="688.9" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="750.0" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="750.0" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="750.0" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="750.0" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="750.0" class="nnue-off"/> </g> <g> <circle cx="870.0" cy="200.0" r="23.0" fill="#6f7480" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="261.1" r="23.0" fill="#8e939c" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="322.2" r="23.0" fill="#a8adb5" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="383.3" r="23.0" fill="#5c626d" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="444.4" r="23.0" fill="#b8bcc2" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="505.6" r="23.0" fill="#7e838c" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="566.7" r="23.0" fill="#999ea6" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="627.8" r="23.0" fill="#636a75" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="688.9" r="23.0" fill="#b0b4ba" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="750.0" r="23.0" fill="#888d96" stroke="#4c525c" stroke-width="1.2"/> </g> <g> <line x1="893.0" y1="200.0" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="600.0" class="nnue-li"/> </g> <g> <circle cx="1205.0" cy="400.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="440.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="480.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="520.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="560.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="600.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> </g> <g> <line x1="1219.0" y1="400.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="400.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="400.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="400.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="440.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="440.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="440.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="440.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="480.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="480.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="480.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="480.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="520.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="520.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="520.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="520.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="560.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="560.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="560.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="560.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="600.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="600.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="600.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="600.0" x2="1446.0" y2="600.0" class="nnue-li"/> </g> <g> <circle cx="1460.0" cy="400.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1460.0" cy="466.7" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1460.0" cy="533.3" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1460.0" cy="600.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> </g> <g> <line x1="1474.0" y1="400.0" x2="1689.0" y2="500.0" class="nnue-li"/> <line x1="1474.0" y1="466.7" x2="1689.0" y2="500.0" class="nnue-li"/> <line x1="1474.0" y1="533.3" x2="1689.0" y2="500.0" class="nnue-li"/> <line x1="1474.0" y1="600.0" x2="1689.0" y2="500.0" class="nnue-li"/> </g> <circle cx="1708.0" cy="500.0" r="19.0" fill="#c9d3be" stroke="#6d7a53" stroke-width="1.4"/> <rect x="1731" y="474" width="150" height="60" class="nnue-masque"/> <text x="1779" y="496" text-anchor="middle" style="font-size:40px;font-weight:700;fill:#3d3b35">+1.35</text> <text x="1779" y="530" class="nnue-sub">SCORE</text> <text x="320" y="836" class="nnue-zt">ENCODAGE</text> <text x="320" y="860" class="nnue-sub">un vecteur binaire de 41 024 bits</text> <text x="320" y="880" class="nnue-sub">une trentaine actives</text> <text x="870" y="836" class="nnue-zt-b">512 NEURONES LINÉAIRES</text> <text x="870" y="860" class="nnue-sub">entretenus par différences</text> <text x="870" y="880" class="nnue-sub">le gros du coût</text> <text x="1456" y="836" class="nnue-zt-g" style="font-size:15px">PETITE TÊTE NON LINÉAIRE</text> <text x="1456" y="880" class="nnue-sub">recalculée à chaque évaluation</text> <text x="1205" y="866" class="nnue-sub">couche 1 : 32 neurones</text> <text x="1460" y="866" class="nnue-sub">couche 2 : 32 neurones</text> <text x="1708" y="866" class="nnue-sub">sortie : 1 neurone</text> </svg>
<figcaption>De la position au score : l'échiquier encodé en features binaires, l'accumulateur linéaire entretenu par différences, et la petite tête non linéaire recalculée à chaque évaluation. Schéma non à l'échelle.</figcaption>
</figure>

Pour aller plus loin, on peut dupliquer tout ce qui suit l'accumulateur en plusieurs **experts**, et choisir lequel exécuter selon le matériel restant sur l'échiquier. C'est un [mélange d'experts](https://en.wikipedia.org/wiki/Mixture_of_experts) _(Mixture of Experts, ou MoE)_ : un seul tourne à la fois, donc l'inférence ne ralentit pas, mais chaque expert se spécialise.

Le contraste avec AlphaZero est vertigineux : quelques dizaines de milliers d'opérations par évaluation, contre des milliards pour un ResNet. Et l'essentiel du coût, l'accumulateur, n'est même pas recalculé, il est mis à jour.

<table>
  <thead>
    <tr><th></th><th>AlphaZero</th><th>NNUE</th></tr>
  </thead>
  <tbody>
    <tr><td>Évaluation</td><td>un ResNet, recalculé entièrement</td><td>une projection linéaire entretenue par différences, plus une petite tête non linéaire</td></tr>
    <tr><td>Matériel</td><td>TPU ou GPU</td><td>CPU seul</td></tr>
    <tr><td>Recherche</td><td>MCTS, statistique</td><td>alpha-bêta, séquentiel</td></tr>
    <tr><td>Coût d'une évaluation</td><td>des milliards d'opérations</td><td>quelques dizaines de milliers d'opérations</td></tr>
  </tbody>
</table>

{% plus "Compacité dans le cache" %}

Un petit réseau a un autre avantage : son empreinte mémoire. Là où un gros réseau provoquerait des défauts de cache à répétition, ce petit réseau tient dans le cache L2 du CPU, ce qui rend l'inférence infiniment plus rapide.

La matrice de poids de l'accumulateur, en revanche, ne tient dans aucun cache : une vingtaine de mégaoctets, où chaque mise à jour va chercher quelques lignes éparpillées. C'est une source importante de défauts de cache.

{% endplus %}

# Peut-on appliquer la même architecture à d'autres problèmes ?

Rien, dans ce qui précède, n'est propre aux échecs. Le NNUE résout un problème très général : **comment réévaluer un modèle à moindre coût quand l'entrée ne change qu'à la marge ?** Trois conditions suffisent :

- **l'état évolue par petits pas** : entre deux évaluations, seule une poignée de features change ;
- **un espace de features vaste et creux** : l'accumulateur projette cet espace vers quelques centaines de valeurs. Il faut des dizaines de milliers d'entrées possibles, dont quelques dizaines actives ; un espace déjà petit n'aurait rien à projeter.
- **la non-linéarité tient dans une petite tête**, recalculée à chaque évaluation.

Ces modèles sont donc taillés pour l'embarqué, où l'on ne dispose que d'un petit CPU, ou pour l'inférence à haute fréquence, en finance par exemple. Une entrée dense, en revanche, ne s'y prête pas.

## Ce qu'il faut retenir

Un NNUE, c'est une grande couche linéaire que l'on **entretient** par différences, surmontée d'une petite tête non linéaire que l'on recalcule. L'idée dépasse les échecs : quand une entrée ne bouge qu'à la marge et que son encodage reste creux, entretenir un résultat coûte moins cher que le recalculer.
