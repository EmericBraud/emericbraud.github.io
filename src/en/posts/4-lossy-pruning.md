---
translationKey: 4-pruning-avec-perte
layout: post.njk
title: Lossy pruning
date: 2026-09-08
section: How a chess engine works
chapter: Exploring fewer branches
chapterOrder: 4
---
# Pruning that guarantees correctness... but not speed

Alpha-beta, as we have described it so far, is an **exact** algorithm: it produces strictly the same result as MinMax, and no information is lost along the way. That is a reassuring property, but it comes at a cost: even with excellent move ordering, in the worst case we still have to explore almost every legal move at each node before we can conclude anything.

Yet, statistically, we already know a lot before we even start searching. A move that shoves a piece into a corner for no apparent reason, or the tenth candidate move in a position where the first nine all turned out to be disastrous, is very likely to be bad. So why spend as much search effort on it as on a promising move?

That is the idea behind **lossy pruning** *(forward pruning)*: we accept cutting branches of the tree no longer because we are **certain** they are irrelevant (as alpha-beta does), but because we estimate, based on statistics or heuristics, that they have a **low enough probability** of changing the final result.

> Unlike alpha-beta, these techniques are no longer guaranteed to find the same result as MinMax. We knowingly accept a risk of error, in exchange for an often considerable speedup.

# Putting the EBF back into perspective

We can measure the impact of these techniques very concretely through the **EBF** defined in a previous article. We had estimated:

- $EBF \approx 45$ for a raw MinMax that prunes nothing,
- $EBF \approx \sqrt{45} \approx 6.7$ for a **perfectly** ordered alpha-beta, in the best case.

In practice, a good modern chess engine, combining alpha-beta, move ordering, a transposition table and lossy pruning, reaches an **EBF of around 2 to 3**. That is still well below the theoretical 6.7 of perfect alpha-beta: the techniques presented in this article are therefore not just marginal optimizations, they account for a large share of the final gain in search depth observed in a real engine.

# Null move pruning

One of the most widely used techniques is **null move pruning**. The starting idea is almost provocative: what if, just for a moment, we let a player **pass their turn**?

In chess, passing is not a legal move, but nothing stops us from simulating it in our search tree. The reasoning goes like this: in almost every position, making a move is always at least as good as doing nothing *(the notable exception being zugzwang, a position where absolutely every move makes things worse)*. If, even after handing the opponent a free move, the position still stays favorable for us beyond a certain threshold ($\beta$), chances are the position is winning anyway, and there is no point exploring the real moves at this node in more detail.

<pre class="mermaid">
graph TD
  P0["Position to explore, depth d"]
  P0 --> NM["We pass our turn:<br/>the opponent moves first"]
  NM --> N["Reduced-depth search<br/>d − 1 − R"]
  N --> Q{"score ≥ β ?"}
  Q -->|yes| C["Cutoff: return β<br/>without exploring real moves"]
  Q -->|no| E["The test proved nothing:<br/>normal search of all moves"]
</pre>

This saves us from exploring a whole subtree, at the price of a risk: in a zugzwang position, this reasoning is wrong, and we may cut a branch that would have revealed a problem. That is precisely what the word "lossy" means in "lossy pruning".

# Late Move Reductions (LMR)

A second family of techniques starts from an empirical observation: if our move ordering is good (see the article on iterative deepening), then the very first moves explored at a node are statistically far more likely to be the best move than the moves explored in tenth or twentieth place.

**Late Move Reductions** exploit this observation directly: rather than cutting late moves outright, we still explore them, but at a **reduced depth**.

<pre class="mermaid">
graph LR
  M1["Move 1"] -->|"depth P"| S1["Full search"]
  M2["Move 2"] -->|"depth P"| S2["Full search"]
  M3["Move 3, 4, 5..."] -->|"depth P - R"| S3["Reduced search"]
</pre>

If this reduced search still reveals a move better than anything found so far (a **fail-high**), we then rerun a full search at depth `P` for that move, this time without reduction: the heuristic was wrong, and we correct the mistake. Otherwise, we trust the reduced estimate and move on to the next move.

# Futility pruning

A third technique, **futility pruning**, relies this time on the material score rather than on move order. Near the leaves of the tree, if the static score of the position (`Eval(position)`) is already so far below $\alpha$ that no reasonable move seems able to close the gap *(adding a safety margin equal to, for example, the value of a minor piece)*, we can cut the search at this node immediately instead of exploring each move one by one.

Here again, the risk is real: an unexpected tactical move (a sacrifice leading to mate, for example) could defeat this estimate. But statistically, this case is rare enough that the speedup is worth it.

# A bet that is never final

The word "lossy" deserves some nuance: these techniques do not **discard** a move once and for all, they merely **postpone** its in-depth exploration. A move deemed unpromising at depth `P` of iterative deepening is not removed from the tree: it will be a candidate again, and re-evaluated with up-to-date information (new transposition table, new move ordering...), from depth `P+1` onward.

This is quite close to the idea behind the **A\*** pathfinding algorithm: we do not visit the search space uniformly, we **steer** it by devoting most of the computational effort to the most promising areas, without permanently ruling out exploring the others if they later turn out to be relevant.

# A deliberate trade-off between speed and correctness

What these techniques have in common is that they replace an expensive certainty with a cheap statistical bet, and one that is rarely final. Each one introduces a risk, different every time: missing a zugzwang, misjudging a late move, or overlooking a buried tactic. A modern chess engine usually combines all these techniques (and many others), tuning them carefully so that the gain in search depth far outweighs, on average, the occasional errors they introduce.

> That is the whole difference in philosophy with alpha-beta: we no longer aim to **never be wrong**, but to **be wrong rarely enough**, and harmlessly enough, that overall the algorithm plays better, faster.
