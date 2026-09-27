---
translationKey: 2-iterative-deepening
layout: post.njk
title: Iterative deepening
date: 2026-09-08
section: How a chess engine works
chapter: Reusing computation
chapterOrder: 2
---
# Iterative Deepening
Alpha-beta pruning is only efficient if the best moves are explored first. Later on, we will look at a few heuristics that let us explore promising-looking moves first.

If we simply launch an alpha-beta search straight at the target depth `P`, we have no information at all to sort the moves before the search has even started.

This is where **iterative deepening** comes in: rather than searching directly at depth `P`, we run a series of complete searches at increasing depths:

<pre class="mermaid">
graph LR
  D1["Depth 1"] --> D2["Depth 2"] --> D3["Depth 3"] --> D4["..."] --> DP["Depth P"]
</pre>

At first glance this seems absurd: each iteration recomputes all the work already done at the previous depths. Yet this approach brings two major benefits.

# Move ordering that speeds up the search

Each search at depth `P-1` tells us which move looked best at that depth. Nothing guarantees that this move will still be the best at depth `P`, but it is an excellent estimate, so we can explore it **first** in the next search.

And as we saw, the efficiency of alpha-beta pruning depends directly on the quality of the move ordering: the earlier the best move is explored, the earlier the cutoffs trigger, and the faster the algorithm runs.

The result is counter-intuitive: even though we redo all the work of the previous depths, the gain from better move ordering **far outweighs the cost of the previous iterations**. In practice, the total time spent on all depths `1` to `P` is often shorter than a direct, poorly ordered search at depth `P`.

# A usable result at any time

The second benefit is just as important, especially in a timed game. In chess, each player has a limited amount of thinking time, so we need to be able to stop the search at any moment and immediately have a move to play.

With a direct search at a fixed depth `P`, if the allotted time runs out before the search finishes, we have **no usable result**: the tree has only been partially explored, and nothing guarantees that the best move found so far is reliable.

With iterative deepening, the situation is very different: as soon as the depth `1` search is done, we already have a move to play. Then at depth `2`, then `3`, and so on. So all we have to do is stop the search as soon as the allotted time is up, and play the best move found by the **last fully completed depth**.

> We say that iterative deepening makes the search **anytime**: it can be interrupted at any moment and still return a usable result.

Later on, we will see how to store, at least partially, the search tree from one iteration to the next, so that the information computed at one depth can speed up the search at the next depth even further.
