---
translationKey: 0-concepts-généraux
layout: post.njk
title: A quick introduction
date: 2026-07-27
section: How a chess engine works
chapter: Search fundamentals
chapterOrder: 0
---

*This article presents the algorithm most commonly used to make a computer play chess. Other algorithms exist, though they are more niche, relying on Monte Carlo methods.*

*Although this blog focuses on chess, the same concepts apply to Othello, Go, or any turn-based game between two players...*

# Framing the problem

Let's think together about the most pragmatic way to solve this problem: we have a computer, and we would like it to play chess. It may look complicated at first glance, but it is actually disarmingly simple.

All we need is to predict the next move from a given position, then repeat the process until the end of the game.

So the question boils down to: **how do we predict the best next move?** Intuitively, to decide that one move is better than another, we first need to define what makes a position good or bad.

# Estimating the strength of a position: the evaluation function

Let's ask ourselves: how does a chess player, with a single glance at the board, tell who is winning and who is losing?

Beginners are first taught to "count points":
- A pawn: 1 point
- A knight or a bishop: 3 points
- A rook: 5 points
- A queen: 9 points

Let's imagine for now that we represent the board as an 8x8 array storing the position of each piece. To deduce the strength of a position, we would simply loop over this array, sum up the value of each player's pieces, and take the difference:

$$
S = Eval(position) = \sum_{i}^{P_{\text{white}}} v_i - \sum_{j}^{P_{\text{black}}} v_j
$$

So if the score $S$ is positive, White has the advantage. If $S$ is negative, Black seems to be winning.

> Obviously, just summing up piece values quickly shows its limits: sometimes two positions with equal material are not equal at all, and sometimes a position that is winning on material can actually be a very bad one.
>
> For years, programmers therefore came up with more and more sophisticated rules to evaluate a position as accurately as possible: bishop pair bonus, pawn structure, king safety... You can add as many rules as you like.
>
> Writing rules by hand to evaluate a position is called an **HCE** *(Hand Crafted Evaluation)*. More recent techniques use neural networks to refine the evaluation. But the idea is the same: design an `Eval(position)` function that takes a position and returns a score.

# Finding the best move: the search tree

Good, now that we know how to tell **statically** which position is more favorable, how do we pick the best move among all the legal moves?

### Depth 1

The idea is straightforward: we play every possible move from our position, evaluate the resulting position for each move with our evaluation function, and pick the move that gives us the best score.

<pre class="mermaid">
graph TD
  P0["Initial position<br/>Eval = S₀"]
  P0 --> C1["Move 1<br/>Eval = S1"]
  P0 --> C2["Move 2<br/>Eval = S2"]
  P0 --> C3["Move 3<br/>Eval = S3"]
  P0 --> C4["Move 4<br/>Eval = S4"]
</pre>

To pick the move with the most favorable `Eval`, we take the highest score for White and the lowest for Black.

But we quickly run into a problem: if we stop there, our program will be completely blind tactically. It will happily sacrifice its queen for a pawn because, on the next move, counting piece values for instance, the position looks winning (the queen has not been recaptured by the opponent yet).

{% fen "4k3/3p4/4p3/8/8/8/4Q3/4K3 w - - 0 1", "white", "Material: 9 for White, 2 for Black. Absolute score: +7" %}

{% fen "4k3/3p4/4Q3/8/8/8/8/4K3 b - - 0 1", "white", "Material: 9 for White, 1 for Black. Absolute score: +8. <strong>The position looks better.</strong>" %}

{% fen "4k3/8/4p3/8/8/8/8/4K3 w - - 0 1", "white", "Material: 0 for White, 1 for Black. Absolute score: -1. <strong>The evaluation collapses because of tactical blindness.</strong>" %}

So we also need to simulate the opponent's reply.

### Depth 2

Let's repeat the process, this time from the opponent's point of view:

<pre class="mermaid">
graph TD
  P0["Initial position<br/>(White to move)"]
  P0 --> B1["White move 1"]
  P0 --> B2["White move 2"]
  B1 --> N1["Black move 1<br/>Eval = S1"]
  B1 --> N2["Black move 2<br/>Eval = S2"]
  B2 --> N3["Black move 1<br/>Eval = S3"]
  B2 --> N4["Black move 2<br/>Eval = S4"]
</pre>

White then picks the move that, assuming Black replies as well as possible, leaves the most favorable score. Problem solved: in this position, White will see Black's possible reply and will no longer sacrifice its queen!

{% fen "4k3/3p4/4p3/8/8/8/4Q3/4K3 w - - 0 1" %}

But the same problem then shows up further down: we make the opponent play its best move, but we also need to work out our own next reply, otherwise the opponent might play an irrational move that sacrifices its own position.

### The MinMax algorithm

What we just described has a name: the **MinMax** algorithm. The idea is to alternate, at each level of the tree, between a player who tries to **maximize** the score (White) and a player who tries to **minimize** it (Black).

We first compute the `Eval` of every leaf in the tree, then work our way back up level by level: at each "MIN" node, we keep the smallest value among its children; at each "MAX" node, we keep the largest. The score that makes it up to the root is therefore the score reached if both players play as well as possible.

<pre class="mermaid">
graph TD
  R["MAX<br/>keeps 3"]:::maxNode
  A["MIN<br/>keeps 3"]:::minNode
  B["MIN<br/>keeps 2"]:::minNode
  L1["Eval = 3"]:::leaf
  L2["Eval = 5"]:::leaf
  L3["Eval = 2"]:::leaf
  L4["Eval = 9"]:::leaf
  R --> A
  R --> B
  A --> L1
  A --> L2
  B --> L3
  B --> L4

  classDef maxNode fill:#fdebd0,stroke:#e67e22,stroke-width:2px;
  classDef minNode fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
  classDef leaf fill:#f4f6f7,stroke:#7f8c8d;

  linkStyle 0 stroke:#e67e22,stroke-width:3px;
  linkStyle 2 stroke:#e67e22,stroke-width:3px;
</pre>
<p style="text-align:center"><em>In orange, the MAX level (White); in blue, the MIN level (Black). The bold path is the one actually played.</em></p>

Here, on the left, Black would pick the move leading to `Eval = 3` rather than `Eval = 5` (Black minimizes), and on the right, the one leading to `Eval = 2` rather than `Eval = 9`. White then compares `3` and `2`, and picks the left branch since `3 > 2` (White maximizes). The final score propagated to the root is therefore `3`, and these choices determine, step by step, the first move to play.

### Depth N

So we would need an infinite tree! That is obviously impossible. For now, we will simply settle for building the deepest tree our CPU allows.

<pre class="mermaid">
graph TD
  P0["Initial position<br/>(White to move)"]
  P0 --> B1["White move 1"]
  P0 --> B2["White move 2"]
  P0 --> B3["White move 3"]
  B1 --> N1["Black move"]
  B1 --> N2["Black move"]
  B2 --> N3["..."]
  B3 --> N4["Black move"]
  B3 --> N5["Black move"]
  N1 --> D1["⋮"]
  N2 --> D2["⋮"]
  N4 --> D3["⋮"]
  N5 --> D4["⋮"]
  D1 --> F1["Eval = S1"]
  D2 --> F2["Eval = S2"]
  D3 --> F3["..."]
  D4 --> F4["Eval = Sn"]
</pre>
<p style="text-align:center"><em>Search tree expanded down to depth N</em></p>

The larger the depth `N`, the further our program "sees" and the better it avoids tactical traps, since the leaves it evaluates are further and further away from our position. But the number of positions to evaluate grows exponentially with `N`. We therefore need to get rid of the unpromising branches of the tree and focus on the most promising moves: that is what the algorithms we will see next are all about.
