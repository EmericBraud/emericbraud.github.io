---
translationKey: 3-table-de-transposition
layout: post.njk
title: The transposition table
date: 2026-09-08
section: How a chess engine works
chapter: Reusing computation
chapterOrder: 3
---
# One position, many paths

In chess, it is very common to reach **the exact same position** by playing the moves in a different order. For example, `1. e4 c5 2. Nf3` and `1. Nf3 c5 2. e4` lead to exactly the same position on the board, even though they are two completely separate branches of our search tree.

<pre class="mermaid">
graph TD
  R["Starting position"]
  R --> A1["1. e4"]
  R --> A2["1. Nf3"]
  A1 --> B1["1. e4 c5"]
  A2 --> B2["1. Nf3 c5"]
  B1 --> C1["2. Nf3"]
  B2 --> C2["2. e4"]
  C1 --> T["Same position"]
  C2 --> T
</pre>

This is called a **transposition**. Without special care, our MinMax / alpha-beta algorithm will explore this position twice, starting from scratch, even though it has already done all that work once. The deeper the tree, the more transpositions there are, and the more expensive this redundant work becomes.

# Remembering what we have already computed

The idea is simple: every time we evaluate a position, we **store the result** in a data structure, the **transposition table**. Before exploring a position, we first check whether it is already there: if so, we can reuse the result directly, without re-exploring the whole corresponding subtree.

Concretely, for each position already encountered, the transposition table stores:

- the **score** obtained for this position,
- the **depth** at which this score was computed,
- the **best move** found for this position,
- a flag telling whether this score is an exact value or only a bound (more on that later).

You can picture the transposition table as a simple array, indexed by the position's hash, where each slot holds this information:

<figure>
<table class="compact">
  <thead>
    <tr>
      <th>Hash (key)</th>
      <th class="num">Score</th>
      <th class="num">Depth</th>
      <th>Best move</th>
      <th>Type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>0x3F2A…C1</code></td>
      <td class="num">+35</td>
      <td class="num">8</td>
      <td>Nf3</td>
      <td>Exact</td>
    </tr>
    <tr>
      <td><code>0x9B10…44</code></td>
      <td class="num">−120</td>
      <td class="num">5</td>
      <td>Qxd5</td>
      <td>Upper bound</td>
    </tr>
    <tr>
      <td><code>0x7E88…0D</code></td>
      <td class="num">+500</td>
      <td class="num">12</td>
      <td>Rxe8</td>
      <td>Lower bound</td>
    </tr>
    <tr class="ellipsis">
      <td colspan="5">⋮</td>
    </tr>
  </tbody>
</table>
<figcaption>A few entries of a transposition table. The hash serves as the index; the other fields are the result of the search that encountered this position.</figcaption>
</figure>

When we encounter a new position, we compute its hash, check whether an entry already exists at that slot in the array, and decide whether to reuse it, complete it or overwrite it, based on the criteria above.

# Identifying a position: Zobrist hashing

To find a position quickly in the table, we first need a way to identify it uniquely and efficiently. Using the whole board as the key, then comparing positions square by square, would be far too slow.

This is where **Zobrist hashing** comes in. The principle is as follows: once and for all, at program startup, we generate a random number for every possible *(piece, square)* combination, plus a few extra numbers to represent the side to move, castling rights and the en passant square.

The hash of a position is then obtained by combining, with a simple `XOR`, the random numbers corresponding to each piece on the board:

$$
H(position) = \bigoplus_{i}^{\text{pieces on board}} Z_i
$$

The beauty of `XOR` is that it lets us **update the hash incrementally** with each move, without recomputing it from scratch: we just `XOR` in the few numbers affected by the move (the origin square, the destination square, a possible captured piece...) instead of scanning the whole board again.

> For the math-minded, this works because `XOR` is an involution: $a \oplus a = 0$ and $a \oplus 0 = a$. In practice, applying the same `XOR` twice cancels its effect, so we can "remove" a piece from the hash by `XOR`-ing it a second time, exactly the way we added it.

This hash then becomes the **key** we use to store and look up a position in the transposition table.

This involution property has another important consequence, which we will come back to in detail later: during the search, it is almost always faster to work **incrementally**, going down and back up the tree one move at a time (`move` / `unmove`), rather than rebuilding the full state of the position at every node. And that is exactly what the involution allows: since `XOR`-ing the same number twice cancels its effect, we can just as easily **play** a move (`XOR` the hash) as **undo** it (`XOR` the same hash again), without ever recomputing the position from the start.

# Storage is necessarily partial

The number of reachable positions in chess is astronomical, far too large to keep them all in memory. The transposition table therefore has a **fixed size**, chosen not only based on available memory, but also on **cache miss** concerns that we will discuss later. Several distinct positions may thus end up sharing the same slot in the table (a **collision**). When that happens, one entry has to be sacrificed to make room for the new one.

A common strategy is to always keep the deepest entry (it represents more computation, and therefore more time saved if we find it again), or to favor positions from the current search over those from a previous one.

This is also what ties the transposition table to the **iterative deepening** discussed in the previous article: the results computed at depth `P-1` are still available in the table when we start the search at depth `P`. Not only is the best move found used to decide which moves to explore first, but if a sub-position has already been fully evaluated at a sufficient depth, we can skip re-exploring it altogether.

> So the transposition table does more than avoid redundant work within a single search: it also lets us reuse, iteration after iteration, part of the work done at previous depths.
