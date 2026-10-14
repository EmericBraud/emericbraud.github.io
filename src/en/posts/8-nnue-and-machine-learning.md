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
<svg viewBox="0 0 1910 920" width="100%" style="max-width:1910px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagram of a NNUE read from left to right: a chess position encoded as binary features, the accumulator neurons, then a small non-linear head and the score"> <style>   text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }   .nnue-ttl { font-size: 17px; font-weight: 600; letter-spacing: .1em; fill: #8a8372; text-anchor: middle }   .nnue-zt { font-size: 15px; font-weight: 600; letter-spacing: .14em; fill: #8a8372; text-anchor: middle }   .nnue-zt-b { font-size: 15px; font-weight: 600; letter-spacing: .14em; fill: #3f6b9c; text-anchor: middle }   .nnue-zt-g { font-size: 12.5px; font-weight: 600; letter-spacing: .16em; fill: #4a7f6b; text-anchor: middle }   .nnue-lbl { font-size: 15px; fill: #8a8372 }   .nnue-sub { font-size: 13px; fill: #8a8372; text-anchor: middle }   .nnue-off { stroke: #ded9cd; stroke-width: .7; opacity: .4 }   .nnue-on { stroke: #3f6b9c; stroke-width: 1.3; opacity: .55 }   .nnue-li { stroke: #b0aa9b; stroke-width: 1; stroke-opacity: .45 }   .nnue-masque { fill: #fdfcfa }   @media (prefers-color-scheme: dark) { .nnue-masque { fill: #f7f6f2 } } </style>  <text x="955.0" y="46" class="nnue-ttl">THE MESH OF A NNUE</text> <text x="955.0" y="80" class="nnue-sub">Each accumulator neuron sums the weight columns of the active features.</text> <g> <rect x="78.0" y="250.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="104.0" y="250.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="130.0" y="250.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="156.0" y="250.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="182.0" y="250.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="208.0" y="250.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="234.0" y="250.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="260.0" y="250.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="78.0" y="276.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="104.0" y="276.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="130.0" y="276.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="156.0" y="276.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="182.0" y="276.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="208.0" y="276.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="234.0" y="276.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="260.0" y="276.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="78.0" y="302.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="104.0" y="302.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="130.0" y="302.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="156.0" y="302.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="182.0" y="302.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="208.0" y="302.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="234.0" y="302.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="260.0" y="302.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="78.0" y="328.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="104.0" y="328.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="130.0" y="328.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="156.0" y="328.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="182.0" y="328.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="208.0" y="328.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="234.0" y="328.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="260.0" y="328.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="78.0" y="354.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="104.0" y="354.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="130.0" y="354.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="156.0" y="354.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="182.0" y="354.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="208.0" y="354.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="234.0" y="354.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="260.0" y="354.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="78.0" y="380.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="104.0" y="380.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="130.0" y="380.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="156.0" y="380.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="182.0" y="380.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="208.0" y="380.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="234.0" y="380.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="260.0" y="380.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="78.0" y="406.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="104.0" y="406.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="130.0" y="406.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="156.0" y="406.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="182.0" y="406.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="208.0" y="406.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="234.0" y="406.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="260.0" y="406.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="78.0" y="432.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="104.0" y="432.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="130.0" y="432.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="156.0" y="432.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="182.0" y="432.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="208.0" y="432.0" width="26.0" height="26.0" fill="#f2efe6"/> <rect x="234.0" y="432.0" width="26.0" height="26.0" fill="#c8c1ae"/> <rect x="260.0" y="432.0" width="26.0" height="26.0" fill="#f2efe6"/> </g> <rect x="78.0" y="250.0" width="208" height="208" fill="none" stroke="#8a8372" stroke-width="1.4"/> <g> <text x="91.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♜</text> <text x="117.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♞</text> <text x="143.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♝</text> <text x="169.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♛</text> <text x="195.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♚</text> <text x="221.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♝</text> <text x="247.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♞</text> <text x="273.0" y="270.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♜</text> <text x="91.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="117.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="143.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="169.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="195.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="221.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="247.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="273.0" y="296.3" text-anchor="middle" font-size="22.4" fill="#2b2b2b">♟</text> <text x="195.0" y="374.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="91.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="117.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="143.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="169.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="221.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="247.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="273.0" y="426.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♙</text> <text x="91.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♖</text> <text x="117.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♘</text> <text x="143.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♗</text> <text x="169.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♕</text> <text x="195.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♔</text> <text x="221.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♗</text> <text x="247.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♘</text> <text x="273.0" y="452.3" text-anchor="middle" font-size="22.4" fill="#ffffff" stroke="#5f594e" stroke-width="1.2" stroke-linejoin="round">♖</text> </g> <line x1="78.0" y1="238" x2="286" y2="238" stroke="#b9b2a2" stroke-width="1.4"/> <text x="182" y="224" class="nnue-zt">POSITION</text> <g> <rect x="310.0" y="165.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="189.0" width="20.0" height="20.0" rx="3" fill="#2f3a44" stroke="#1e262e" stroke-width="1.1"/> <rect x="310.0" y="213.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="237.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="261.0" width="20.0" height="20.0" rx="3" fill="#2f3a44" stroke="#1e262e" stroke-width="1.1"/> <rect x="310.0" y="285.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="309.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="333.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="357.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="381.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="405.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="429.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="453.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="477.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="501.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="525.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="549.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="573.0" width="20.0" height="20.0" rx="3" fill="#2f3a44" stroke="#1e262e" stroke-width="1.1"/> <rect x="310.0" y="597.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="621.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="645.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="669.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="693.0" width="20.0" height="20.0" rx="3" fill="#2f3a44" stroke="#1e262e" stroke-width="1.1"/> <rect x="310.0" y="717.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="741.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> <rect x="310.0" y="765.0" width="20.0" height="20.0" rx="3" fill="#ffffff" stroke="#cfc9bb" stroke-width="1.1"/> </g> <g> <line x1="330.0" y1="175.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="200.0" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="200.0" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="200.0" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="200.0" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="200.0" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="261.1" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="261.1" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="261.1" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="261.1" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="261.1" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="322.2" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="322.2" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="322.2" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="322.2" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="322.2" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="383.3" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="383.3" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="383.3" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="383.3" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="383.3" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="444.4" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="444.4" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="444.4" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="444.4" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="444.4" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="505.6" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="505.6" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="505.6" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="505.6" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="505.6" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="566.7" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="566.7" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="566.7" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="566.7" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="566.7" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="627.8" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="627.8" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="627.8" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="627.8" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="627.8" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="688.9" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="688.9" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="688.9" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="688.9" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="688.9" class="nnue-off"/> <line x1="330.0" y1="175.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="199.0" x2="847.0" y2="750.0" class="nnue-on"/> <line x1="330.0" y1="223.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="247.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="271.0" x2="847.0" y2="750.0" class="nnue-on"/> <line x1="330.0" y1="295.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="319.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="343.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="367.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="391.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="415.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="439.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="463.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="487.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="511.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="535.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="559.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="583.0" x2="847.0" y2="750.0" class="nnue-on"/> <line x1="330.0" y1="607.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="631.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="655.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="679.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="703.0" x2="847.0" y2="750.0" class="nnue-on"/> <line x1="330.0" y1="727.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="751.0" x2="847.0" y2="750.0" class="nnue-off"/> <line x1="330.0" y1="775.0" x2="847.0" y2="750.0" class="nnue-off"/> </g> <g> <circle cx="870.0" cy="200.0" r="23.0" fill="#6f7480" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="261.1" r="23.0" fill="#8e939c" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="322.2" r="23.0" fill="#a8adb5" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="383.3" r="23.0" fill="#5c626d" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="444.4" r="23.0" fill="#b8bcc2" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="505.6" r="23.0" fill="#7e838c" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="566.7" r="23.0" fill="#999ea6" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="627.8" r="23.0" fill="#636a75" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="688.9" r="23.0" fill="#b0b4ba" stroke="#4c525c" stroke-width="1.2"/> <circle cx="870.0" cy="750.0" r="23.0" fill="#888d96" stroke="#4c525c" stroke-width="1.2"/> </g> <g> <line x1="893.0" y1="200.0" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="200.0" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="261.1" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="322.2" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="383.3" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="444.4" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="505.6" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="566.7" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="627.8" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="688.9" x2="1191.0" y2="600.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="400.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="440.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="480.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="520.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="560.0" class="nnue-li"/> <line x1="893.0" y1="750.0" x2="1191.0" y2="600.0" class="nnue-li"/> </g> <g> <circle cx="1205.0" cy="400.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="440.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="480.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="520.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="560.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1205.0" cy="600.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> </g> <g> <line x1="1219.0" y1="400.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="400.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="400.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="400.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="440.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="440.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="440.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="440.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="480.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="480.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="480.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="480.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="520.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="520.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="520.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="520.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="560.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="560.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="560.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="560.0" x2="1446.0" y2="600.0" class="nnue-li"/> <line x1="1219.0" y1="600.0" x2="1446.0" y2="400.0" class="nnue-li"/> <line x1="1219.0" y1="600.0" x2="1446.0" y2="466.7" class="nnue-li"/> <line x1="1219.0" y1="600.0" x2="1446.0" y2="533.3" class="nnue-li"/> <line x1="1219.0" y1="600.0" x2="1446.0" y2="600.0" class="nnue-li"/> </g> <g> <circle cx="1460.0" cy="400.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1460.0" cy="466.7" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1460.0" cy="533.3" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> <circle cx="1460.0" cy="600.0" r="14.0" fill="#dde4d2" stroke="#7d8a61" stroke-width="1.3"/> </g> <g> <line x1="1474.0" y1="400.0" x2="1689.0" y2="500.0" class="nnue-li"/> <line x1="1474.0" y1="466.7" x2="1689.0" y2="500.0" class="nnue-li"/> <line x1="1474.0" y1="533.3" x2="1689.0" y2="500.0" class="nnue-li"/> <line x1="1474.0" y1="600.0" x2="1689.0" y2="500.0" class="nnue-li"/> </g> <circle cx="1708.0" cy="500.0" r="19.0" fill="#c9d3be" stroke="#6d7a53" stroke-width="1.4"/> <rect x="1731" y="474" width="150" height="60" class="nnue-masque"/> <text x="1779" y="496" text-anchor="middle" style="font-size:40px;font-weight:700;fill:#3d3b35">+1.35</text> <text x="1779" y="530" class="nnue-sub">SCORE</text> <text x="320" y="836" class="nnue-zt">ENCODING</text> <text x="320" y="860" class="nnue-sub">a binary vector of 41,024 bits</text> <text x="320" y="880" class="nnue-sub">about thirty active</text> <text x="870" y="836" class="nnue-zt-b">512 LINEAR NEURONS</text> <text x="870" y="860" class="nnue-sub">maintained by differences</text> <text x="870" y="880" class="nnue-sub">most of the cost</text> <text x="1456" y="836" class="nnue-zt-g" style="font-size:15px">SMALL NON-LINEAR HEAD</text> <text x="1456" y="880" class="nnue-sub">recomputed at every evaluation</text> <text x="1205" y="866" class="nnue-sub">layer 1: 32 neurons</text> <text x="1460" y="866" class="nnue-sub">layer 2: 32 neurons</text> <text x="1708" y="866" class="nnue-sub">output: 1 neuron</text> </svg>
<figcaption>From position to score: the board encoded as binary features, the linear accumulator maintained by differences, and the small non-linear head recomputed at every evaluation. Diagram not to scale.</figcaption>
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
