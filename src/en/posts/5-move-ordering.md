---
translationKey: 5-move-ordering
layout: post.njk
title: Move ordering
date: 2026-09-08
section: How a chess engine works
chapter: Exploring fewer branches
chapterOrder: 5
---
# Why move order matters so much

We've brought it up several times in the previous articles: how well alpha-beta performs depends directly on the order in which moves are explored at each node. With perfect ordering, the EBF drops from `45` to about `6.7`; with bad ordering, alpha-beta prunes almost nothing and behaves like plain MinMax.

**Move ordering** covers all the heuristics that let us estimate, at a given moment `T`, which moves are most likely to be good, **before we've even explored them**. None of these heuristics is perfect: they all rely on indirect clues, gathered either from previous searches or from static properties of the move itself.

# The transposition table move

The most reliable source of information is the one we already have: if the current position has been seen before (through iterative deepening or a transposition), the transposition table holds the **best move** found during the previous search. That move is always explored first.

This is by far the most powerful heuristic: it doesn't rest on any assumption, but on an actual search result, obtained at a slightly shallower depth.

# MVV-LVA: ordering captures

For moves with no known best move in the transposition table, we first sort by move **category**, and the first category to explore is captures.

Not all captures are equal, though. The **MVV-LVA** heuristic *(<strong>M</strong>ost <strong>V</strong>aluable <strong>V</strong>ictim, <strong>L</strong>east <strong>V</strong>aluable <strong>A</strong>ttacker)* sorts them by giving priority:

- to the most valuable **captured** piece (`V`ictim),
- then, for equal value, to the least valuable **capturing** piece (`A`ttacker).

So taking a queen with a pawn is explored before taking a pawn with a queen: intuitively, capturing a high-value piece with a low-value one is almost always a good deal, while the reverse is worth checking later, once we have a better bound to cut off quickly if it turns out to be bad.

<table>
  <thead>
    <tr>
      <th>Move</th>
      <th>Victim</th>
      <th>Attacker</th>
      <th>Priority</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Pawn takes Queen</td>
      <td>Queen (9)</td>
      <td>Pawn (1)</td>
      <td>Very high</td>
    </tr>
    <tr>
      <td>Knight takes Rook</td>
      <td>Rook (5)</td>
      <td>Knight (3)</td>
      <td>Medium</td>
    </tr>
    <tr>
      <td>Queen takes Pawn</td>
      <td>Pawn (1)</td>
      <td>Queen (9)</td>
      <td>Low</td>
    </tr>
  </tbody>
</table>

> To refine this ordering further, some engines use a more thorough evaluation, **SEE** *(<strong>S</strong>tatic <strong>E</strong>xchange <strong>E</strong>valuation)*, which statically simulates the whole sequence of exchanges on a given square (recaptures included) to determine whether a capture actually wins material once all recaptures are played out, rather than only looking at the first exchange.

# Killer moves

Once captures are exhausted, we turn to "quiet" moves (those that capture nothing). Here we no longer have a criterion as direct as MVV-LVA. Instead, we rely on the history of the current search: **killer moves**.

The idea is this: if a quiet move caused an alpha-beta cutoff (a **fail-high**, meaning a move whose score exceeds $\beta$) at a given node, there's a good chance a similar move is also good in a **sibling position**, that is, another node at the **same depth** in the tree. So for each depth, we remember the moves that recently caused a cutoff, and try them first in sibling positions.

> Not to be confused with a **fail-low**: when no move explored at a node exceeds $\alpha$, the node simply returns an upper bound, and no particular move stands out. Only a fail-high points to a specific move worth keeping as a killer move.

<pre class="mermaid">
graph TD
  R["Root"]
  R --> A["Position A"]
  R --> B["Position B (sibling of A)"]
  A --> K["'Killer' move<br/>caused a cutoff here"]
  B --> K2["We try the same move first"]
</pre>

# The history heuristic

Along the same lines, the **history heuristic** extends the killer move idea to the whole search, regardless of depth. We maintain a table that maps each move (typically a *from square / to square* pair) to a score, incremented every time that move causes an alpha-beta cutoff anywhere in the tree. The more a move has "proven itself" overall, the earlier it gets tried in later positions.

<figure>
<svg viewBox="0 0 630 342" width="100%" style="max-width:630px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Two chessboard heatmaps: from-squares and to-squares of moves that caused a cutoff">
<style>
  .bt { font: 600 13px "Noto Sans", sans-serif; fill: #333; text-anchor: middle }
  .ax { font: 10px "Noto Sans", sans-serif; fill: #999; text-anchor: middle }
  .sq { font: 10px "Noto Sans", sans-serif; fill: #33404f; text-anchor: middle }
  .sq.lt { fill: #fff }
  .lg { font: 10px "Noto Sans", sans-serif; fill: #777 }
</style>
<defs><linearGradient id="hg"><stop offset="0" stop-color="#f7f6f2"/><stop offset="1" stop-color="#1f4e79"/></linearGradient></defs>
<text x="156" y="22" class="bt">From squares</text>
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
<text x="484" y="22" class="bt">To squares</text>
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
<text x="391.0" y="333" class="lg">frequent</text>
</svg>
<figcaption>Illustrative example of a history heuristic table at the end of a search: the darker a square, the more cutoffs were caused by moves leaving it (left) or landing on it (right). Moves toward the center and knight development clearly stand out, so they will be tried first in later positions.</figcaption>
</figure>

# An ordering, never a certainty

These heuristics combine naturally, in decreasing order of reliability:

1. the move from the transposition table,
2. captures, sorted by MVV-LVA / SEE,
3. killer moves,
4. the remaining moves, sorted by the history heuristic.

None of these techniques guarantees finding the best move first: they're only informed bets, built on statistics and the results of past searches. But as we've seen, even imperfect ordering is enough to bring alpha-beta very close to its theoretical optimum, which makes it one of the most cost-effective optimizations in a chess engine.
