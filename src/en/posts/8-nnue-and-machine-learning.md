---
translationKey: 8-nnue-et-machine-learning
layout: post.njk
title: NNUE, a revolutionary machine learning architecture
date: 2026-10-14
section: Programming techniques
chapter: Learning to evaluate
chapterOrder: 7
---

December 5, 2017: DeepMind announces AlphaZero, able to beat [Stockfish 8](https://stockfishchess.org/), the strongest chess engine of the time, after only a few hours of self-play. The news travels the world, but it deserves a caveat: AlphaZero runs on TPUs, Stockfish on a plain CPU.

The match is therefore not just between two engines, but between **two ways of evaluating a position**.

# The arrival of AI in chess

For sixty years, building a chess engine meant writing [an evaluation function](/en/posts/0-introduction/) and then refining it, for instance with [Texel tuning](https://www.chessprogramming.org/Texel%27s_Tuning_Method). It was cheap in computation, but imprecise, and bounded by **human bias**: all the knowledge came from the intuition of the best players.

AlphaZero turned the tables. No hand-written rule, no pre-existing human knowledge. Instead, a [ResNet](https://en.wikipedia.org/wiki/Residual_neural_network) that learns on its own, through self-play and reinforcement learning. The approach was revolutionary for its time: it made position evaluation far more precise. But it has a cost: it needs a [TPU](https://en.wikipedia.org/wiki/Tensor_processing_unit) or a GPU, and inference through such a large neural network is slow.

For Stockfish, the question does not even arise: the engine must stay portable, and therefore run on a CPU alone. And two obstacles would stand in the way in any case. The first is hardware: an alpha-beta engine like [the one we described](/en/posts/1-alpha-beta-pruning/) evaluates tens of millions of positions per second, with an evaluation that costs a few hundred operations and data structures that fit in cache; an AlphaZero evaluation, by contrast, requires a CPU → GPU → CPU round trip, whose latency rules out such a pace.

<figure>
<svg viewBox="0 0 840 285" width="100%" style="max-width:840px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Path of a position through the memory hierarchy: CPU L1 L2 L3 caches, RAM, PCIe bus, VRAM and GPU caches, then back">
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
<text x="420" y="18" class="ttl">THE PATH OF A POSITION TO THE NETWORK</text>
<rect x="12" y="70" width="314" height="104" rx="3" class="zone"/>
<text x="169" y="60" class="zt">CPU</text>
<rect x="516" y="70" width="312" height="104" rx="3" class="zone"/>
<text x="672" y="60" class="zt">GRAPHICS CARD</text>
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
<text x="777" y="138" class="lt">the network</text>
<path d="M106 122 H124" class="fx" marker-end="url(#ar)"/>
<path d="M212 122 H230" class="fx" marker-end="url(#ar)"/>
<path d="M318 122 H336" class="fx" marker-end="url(#ar)"/>
<path d="M424 122 H520" class="fx" marker-end="url(#ar)"/>
<path d="M608 122 H626" class="fx" marker-end="url(#ar)"/>
<path d="M714 122 H732" class="fx" marker-end="url(#ar)"/>
<text x="473" y="108" class="bus">PCIe</text>
<text x="473" y="142" class="bus s">~1 µs</text>
<path d="M777 156 V250 H63 V160" class="rt" marker-end="url(#rr)"/>
<text x="420" y="242" class="ret">the score crosses the same hierarchy in the opposite direction</text>
</svg>
<figcaption>Inside the CPU, one evaluation costs a few nanoseconds; as soon as you have to switch chips, it is counted in microseconds.</figcaption>
</figure>

The second obstacle is structural. Alpha-beta explores a **sequential** tree, where every node waits for the previous one to finish. Applying a ResNet to an alpha-beta algorithm would mean paying that latency at every node. AlphaZero replaces it with a Monte-Carlo tree search _([Monte-Carlo Tree Search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search), or MCTS)_: positions are sent to the GPU in batches, so the latency is paid once for thousands of nodes, at the price of a tree that is no longer deterministic, but **statistical**.

# The return of the king: Stockfish and NNUE
But Stockfish had not said its last word. In 2018, [Yu Nasu](https://chessprogramming.org/Yu_Nasu) published, for shogi, an architecture that the Stockfish developers adopted: an **[Efficiently Updatable Neural Network](https://www.chessprogramming.org/NNUE)** _(NNUE: the acronym takes the initials in reverse, don't ask me why 🤷)_.

## An incremental tree, an evaluation that is not

The idea starts from a simple observation: the search tree is **incremental** by nature. Each node is a position, and two neighboring nodes in the tree differ by a single ply.

<figure>
<div class="boardrow">
  <div>
    <chess-board class="hl-e2" position="5rk1/5ppp/2np4/8/2BP4/5N2/4PPPP/5RK1 w - - 0 1" orientation="white" style="width: 250px; max-width: 100%;"></chess-board>
    <p class="boardcap">before the move, the pawn is on e2</p>
  </div>
  <div>
    <chess-board class="hl-e4" position="5rk1/5ppp/2np4/8/2BPP3/5N2/5PPP/5RK1 b - - 0 1" orientation="white" style="width: 250px; max-width: 100%;"></chess-board>
    <p class="boardcap">after the move, the pawn is on e4</p>
  </div>
</div>
<figcaption>Two neighboring nodes: a single ply separates them, and two inputs out of thirty change.</figcaption>
</figure>

Running a huge neural network on every position of the tree is therefore wasteful: from one node to the next, the input changes by only 1 %. The temptation is to update the network's state incrementally.

That is impossible: in a non-linear network, each layer transforms the information instead of carrying it, so a tiny variation at the input propagates everywhere. An incremental update requires **linearity**: to write $f(x + \delta) = f(x) + f(\delta)$, $f$ must be linear. And a purely linear network would be useless, since composing linear layers amounts to having only one. Without non-linearity, no intelligence; with it, no incremental update.

## Encoding the board differently

The trick is to move the problem: make **all the expensive computation linear**, and push the non-linearity into a tiny part of the network. First step: change the representation of the board, for a **binary** and very **sparse** vector, in which every input describes a precise combination, such as the triplet (king square, piece square, piece type) of the `HalfKP` encoding.

<figure>
<div class="boardrow">
  <div>
    <chess-board position="5rk1/5ppp/2np4/8/2BP4/5N2/4PPPP/5RK1 w - - 0 1" orientation="white" style="width: 220px; max-width: 100%;"></chess-board>
    <p class="boardcap">the position</p>
  </div>
  <p class="boardarrow">&rarr;</p>
  <div style="width: 320px; max-width: 100%;">
<svg viewBox="0 0 320 190" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sparse binary vector of 41,024 inputs, of which only about thirty are active">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .note { font-size: 11px; fill: #8a8372; text-anchor: middle }
  .cell { fill: #f7f6f2; stroke: #e3dfd5 }
  .cell.a { fill: #3f6b9c; stroke: #2f5580 }
</style>
<text x="160" y="16" class="ttl">41,024 BINARY INPUTS</text>
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
<text x="160" y="126" class="note">about thirty are active</text>
<text x="160" y="144" class="note">all the others are 0</text>
<text x="160" y="178" class="note">one input = (king square, piece square, piece type)</text>
</svg>
  </div>
</div>
<figcaption>41,024 binary inputs, about thirty of them active. Diagram not to scale.</figcaption>
</figure>

Intelligence is thus **pre-encoded into the features** rather than left to deep layers: a bishop on a diagonal becomes one active input among thousands, whose weight the network learns.

## The accumulator

Second step: add a first **linear** layer at the input of the network, the **accumulator**. Since its output is nothing but a sum of the weight columns of the active features, moving from one node to the next amounts to removing the columns of those that turn off and adding those that turn on.

<figure>
<svg viewBox="0 0 720 326" width="100%" style="max-width:720px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Incremental update of the accumulator: subtracting and adding weight columns">
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
<text x="360" y="16" class="ttl">UPDATING THE ACCUMULATOR</text>
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
<text x="360" y="266" class="note">A: the accumulator before the move, A′: the same, up to date</text>
<text x="360" y="288" class="note">subtract the column of the input that turns off, add the column of the input that turns on</text>
<text x="360" y="310" class="note">each column is a vector of 256 values: no full re-evaluation is needed</text>
</svg>
<figcaption>Updated by subtracting and adding columns, without reprojecting the board.</figcaption>
</figure>

The accumulator is therefore a projection: 41,024 binary inputs, a few hundred continuous values as output, with one copy per side. Current networks use 1024 of them, sometimes 3072, against 256 for Stockfish's first NNUE.

{% plus "The case of the king" %}

The accumulator is not magic, though. In the `HalfKP` encoding, every input is indexed by the king square: as long as the king does not move, the incremental update works. As soon as it does move, all the active inputs change index, and the accumulator must be **entirely rebuilt**. Stockfish speaks of a _refresh trigger_: the event that forces this full recomputation.

Modern engines amortize that cost by keeping in reserve accumulators already computed for other king positions, even if that means updating only the difference with respect to them. The principle stands: incrementality has its exceptions, and the king is the main one.

{% endplus %}

## The trap of accumulation

Updating a floating-point sum on the fly has a well-known flaw: **errors accumulate**. Every rounded addition drifts the accumulator a little away from the value it would have had if recomputed from scratch, and after millions of updates the drift matters. The NNUE answer: **quantize the network into integers**, whose addition is exact, at the price of some precision.

{% plus "SIMD" %}

Quantization has big benefits, starting with inference speed. Adding or multiplying 8-bit integers across 128, 256 or 512-bit registers is SIMD: a single CPU instruction can perform up to 64 operations at once!

{% endplus %}

## A small non-linear network on top

What remains is the truly intelligent part, precisely the one we cannot increment. It is reduced to a minimum: connected to the accumulator, a very small non-linear network is recomputed at every evaluation. In Stockfish's first NNUE, the 512 values go through two layers of 32 neurons, then a single output neuron that gives the score.

<figure>
<svg viewBox="0 0 840 224" width="100%" style="max-width:840px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Architecture d un NNUE : encoding binaire, accumulator lineaire, petit reseau non lineaire">
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
<text x="420" y="16" class="ttl">THE COMPLETE ARCHITECTURE OF AN NNUE</text>
<rect x="20" y="74" width="170" height="78" class="bx-in"/>
<text x="105" y="101" font-size="11" font-weight="400" fill="#8a8372" text-anchor="middle">encoding</text>
<text x="105" y="118" font-size="13" font-weight="600" fill="#3d3b35" text-anchor="middle">41,024 bits</text>
<text x="105" y="133" font-size="11" font-weight="400" fill="#8a8372" text-anchor="middle">≈ 30 active</text>
<rect x="230" y="74" width="200" height="78" class="bx-acc"/>
<text x="330" y="102" font-size="13" font-weight="600" fill="#3f6b9c" text-anchor="middle">accumulator</text>
<text x="330" y="117" font-size="11" font-weight="400" fill="#3f6b9c" text-anchor="middle">256 × 2 = 512 values</text>
<text x="330" y="133" font-size="11" font-weight="400" fill="#8a8372" text-anchor="middle">linear, updated</text>
<rect x="470" y="74" width="90" height="78" class="bx-sm"/>
<text x="515" y="118" font-size="13" font-weight="600" fill="#4a7f6b" text-anchor="middle">32</text>
<rect x="600" y="74" width="90" height="78" class="bx-sm"/>
<text x="645" y="118" font-size="13" font-weight="600" fill="#4a7f6b" text-anchor="middle">32</text>
<rect x="730" y="74" width="90" height="78" class="bx-sm"/>
<text x="775" y="110" font-size="13" font-weight="600" fill="#4a7f6b" text-anchor="middle">1</text>
<text x="775" y="125" font-size="11" font-weight="400" fill="#8a8372" text-anchor="middle">score</text>
<defs><marker id="mkD" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#b9b2a2"/></marker></defs>
<path d="M190 113 H228" class="fx" marker-end="url(#mkD)"/>
<path d="M430 113 H468" class="fx" marker-end="url(#mkD)"/>
<path d="M560 113 H598" class="fx" marker-end="url(#mkD)"/>
<path d="M690 113 H728" class="fx" marker-end="url(#mkD)"/>
<text x="449" y="99" class="note">CReLU</text>
<text x="579" y="99" class="note">CReLU</text>
<path d="M230 164 V178 H430 V164" class="br"/>
<path d="M470 164 V178 H820 V164" class="br"/>
<text x="330" y="196" class="note" fill="#3f6b9c">saved and updated incrementally</text>
<text x="645" y="196" class="note" fill="#4a7f6b">recomputed at each evaluation</text>
</svg>
<figcaption>A linear accumulator updated incrementally, then a very small non-linear network, recomputed at every evaluation.</figcaption>
</figure>

To go further, everything after the accumulator can be duplicated into several **experts**, and the engine picks which one to run according to the material left on the board. That is a [mixture of experts](https://en.wikipedia.org/wiki/Mixture_of_experts) _(MoE)_: only one runs at a time, so inference does not slow down, but each expert specializes.

The contrast with AlphaZero is dizzying: a few tens of thousands of operations per evaluation, against billions for a ResNet. And the bulk of the cost, the accumulator, is not even recomputed: it is updated.

<table>
  <thead>
    <tr><th></th><th>AlphaZero</th><th>NNUE</th></tr>
  </thead>
  <tbody>
    <tr><td>Evaluation</td><td>a ResNet, recomputed entirely</td><td>a linear projection maintained by differences, plus a small non-linear head</td></tr>
    <tr><td>Hardware</td><td>TPU or GPU</td><td>CPU only</td></tr>
    <tr><td>Search</td><td>MCTS, statistical</td><td>alpha-beta, sequential</td></tr>
    <tr><td>Cost of one evaluation</td><td>billions of operations</td><td>a few tens of thousands of operations</td></tr>
  </tbody>
</table>

{% plus "Compact enough for the cache" %}

A small network has another advantage: its memory footprint. Where a large network would cause one cache miss after another, this small network fits in the CPU's L2 cache, which makes inference vastly faster.

The accumulator's weight matrix, on the other hand, fits in no cache at all: about twenty megabytes, in which every update fetches a few scattered lines. That is a significant source of cache misses.

{% endplus %}

# Can the same architecture be applied to other problems?

Nothing in the foregoing is specific to chess. NNUE solves a very general problem: **how do you re-evaluate a model cheaply when the input changes only marginally?** Three conditions are enough:

- **the state evolves in small steps**: between two evaluations, only a handful of features change;
- **a vast and sparse feature space**: the accumulator projects that space onto a few hundred values. You need tens of thousands of possible inputs, of which a few dozen are active; an already small space would have nothing to project.
- **the non-linearity fits in a small head**, recomputed at every evaluation.

Such models are therefore a good fit for embedded systems, where only a small CPU is available, or for high-frequency inference, in finance for instance. A dense input, on the other hand, does not lend itself to it.

## What to remember

An NNUE is a large linear layer that we **maintain** by differences, topped by a small non-linear head that we recompute. The idea goes beyond chess: when an input moves only marginally and its encoding stays sparse, maintaining a result costs less than recomputing it.
