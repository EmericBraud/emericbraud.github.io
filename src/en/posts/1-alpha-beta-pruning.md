---
translationKey: 1-pruning-alpha-beta
layout: post.njk
title: Alpha-beta pruning
date: 2026-07-30
section: How a chess engine works
chapter: Search fundamentals
chapterOrder: 1
---
# The EBF: the base of the exponential
Our search tree grows exponentially as depth increases. In chess, an "average" position is estimated to offer around **40 to 45 legal moves**. This means the time complexity of our algorithm grows as

$$
O(45^P)
$$

where $P$ is the search depth.

For example, at a depth of $P = 10$ (only 5 moves for each player), we would need to explore roughly

$$
45^{10} \approx 34\,050\,628\,916\,015\,625 \text{ positions}
$$

that is, more than **34 quadrillion** positions. Obviously, that is a big problem.

<pre class="mermaid">
graph LR
  P0["Depth 0<br/>1 node"]
  P1["Depth 1<br/>~45 nodes"]
  P2["Depth 2<br/>~45² nodes"]
  P3["Depth 3<br/>~45³ nodes"]
  P0 -->|"×45"| P1 -->|"×45"| P2 -->|"×45"| P3
</pre>
<p style="text-align:center"><em>The number of nodes to explore is multiplied by ~45 with each additional ply of depth.</em></p>

The **EBF** (*<strong>E</strong>ffective <strong>B</strong>ranching <strong>F</strong>actor*) is the average multiplier on the number of nodes you need to visit to go from depth `P` to depth `P+1`.

$$
EBF = \text{AVG}\left(\frac{N(P+1)}{N(P)}\right)
$$

where $N(P)$ is the number of nodes explored at depth $P$.

So the time complexity is
$$
N = O(EBF^P)
$$
The EBF is **the single most important factor** in how fast our algorithm is. Optimizations on raw node processing speed usually come second.

> With an EBF of 10, you would need to process **10 times more nodes per second** to gain a single ply of depth *(a move being a White move followed by Black's reply)*.

# The alpha-beta algorithm

MinMax explores the whole tree: every single leaf is evaluated, without exception. Yet if you look closely at how the algorithm unfolds, you notice that a large part of this work is **useless**: as soon as we find, in a branch, a move bad enough that a player would never let it happen, there is no point exploring that branch any further. We can **cut** (or *prune*) the search right there.

That is exactly what the **alpha-beta** algorithm does: it produces exactly the same result as MinMax, but visits far fewer nodes.

### Alpha and beta: two bounds we keep tightening

The idea is to pass two values down throughout the search:

- **alpha ($\alpha$)**: the best score White (the maximizing player) is **guaranteed to get** elsewhere in the tree.
- **beta ($\beta$)**: the best score Black (the minimizing player) is **guaranteed to get** elsewhere in the tree.

At the start, $\alpha = -\infty$ and $\beta = +\infty$: we know nothing yet. As the exploration goes on, these two values close in on each other, and the interval $[\alpha, \beta]$ represents the **window** of scores still "worth" exploring.

The cutoff happens as soon as $\alpha \geq \beta$: it means one of the two players already has, elsewhere in the tree, an alternative at least as good as anything the current branch could offer. Exploring this branch further will never change the move finally chosen at the root, so we can stop right away.

### A concrete example

Let's take a two-level tree again, where White (MAX) chooses between two moves, each followed by two Black replies (MIN):

<pre class="mermaid">
graph TD
  P0["Root (MAX)"]
  P0 --> B1["White move 1 (MIN)"]
  P0 --> B2["White move 2 (MIN)"]
  B1 --> N1["Eval = 3"]
  B1 --> N2["Eval = 5"]
  B2 --> N3["Eval = 2"]
  B2 --> N4["Eval = ?"]
</pre>

- We first explore the **White move 1** branch. The MIN node finds `3`, then `5`: since it minimizes, it keeps `3`. The branch therefore returns `3` to the root, which updates $\alpha = 3$ *(White is now guaranteed to get at least 3)*.
- We then explore **White move 2**. The MIN node first finds `2`. Since this node minimizes and has already found a value (`2`) **less than or equal to $\alpha$ (3)**, it knows White will never choose this move at the root: whatever the remaining node is worth (`Eval = ?`), the score of this branch cannot exceed `2`, so it can never beat the `3` already guaranteed by **White move 1**.
- The last node (`Eval = ?`) is therefore **pruned**: it is never evaluated.

That is the whole strength of the algorithm: the final result (White plays **White move 1**, score `3`) is strictly identical to MinMax's, but we saved the exploration of an entire subtree, which, at greater depths, can mean thousands or even millions of nodes.

### Why exploration order matters

How well pruning works depends heavily on **the order in which moves are explored**. If, by bad luck, we always explored the move that is worst for the opponent first (forcing it to explore more before finding something to cut on), alpha-beta would prune almost nothing and behave like plain MinMax.

Conversely, with **optimal move ordering** (trying first the moves most likely to be best: captures, checks, moves suggested by a previous search...), alpha-beta reaches its maximum theoretical performance: in the best case, complexity drops from

$$
O(EBF^P) \quad \text{to} \quad O(\sqrt{EBF^P})
$$

In practice, this means being able to search **twice as deep** for the same compute budget, an absolutely huge gain, since we saw that the EBF is the most important factor in the algorithm's speed.

> This is precisely why move ordering is a topic in its own right when designing a chess engine: the closer the exploration order gets to the ideal order, the more efficiently alpha-beta prunes.