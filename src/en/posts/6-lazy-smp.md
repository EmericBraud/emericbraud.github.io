---
translationKey: 6-lazy-smp
layout: post.njk
title: Multithreading with Lazy SMP
date: 2026-09-10
section: How a chess engine works
chapter: Exploring faster
chapterOrder: 6
---
# A tree that is hard to split

Every optimization covered so far aimed at exploring **fewer nodes**. There is one orthogonal lever left: exploring nodes **faster**, by using all the cores of the machine.

The problem is that alpha-beta parallelizes very poorly. Its strength comes precisely from its **sequential** nature: the result of the first move searched provides the $\alpha$ bound that lets us cut the following ones. If we spread the moves of a node across several threads in parallel, each one starts with a $[\alpha, \beta]$ window wider than necessary, therefore cuts less, and explores a much larger subtree than a sequential search would have visited.

> So we are not trying to split a fixed amount of work among $N$ threads. The total work **grows** with the number of threads: the whole point is to keep that overhead smaller than the gain brought by parallelism.
>
> This loss of efficiency has a name: **search overhead**. With $N$ threads you never get a factor of $N$; a good engine typically reaches a factor of `2.5` to `3` on 4 threads.

# Historical approaches

The first attempts tried to split the tree explicitly.

The **Young Brothers Wait Concept** (YBWC) algorithm formalizes the intuition above: at a given node, we first search the first move (the "eldest brother") **sequentially**, which establishes a reliable $\alpha$ bound, and only then distribute the remaining moves (the "young brothers") over the available threads. The threads then work with an already narrowed window, and cut almost as much as in a sequential search.

It is satisfying in theory, but expensive in practice: threads have to be synchronized at every shared node, work has to be distributed dynamically, and bound updates have to be propagated. The search code becomes considerably more complex, and the synchronization points limit scalability.

<figure>
<svg viewBox="0 0 760 268" width="100%" style="max-width:760px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="YBWC: the first move is searched alone, then the remaining moves are distributed over the threads">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ph { font-size: 11px; font-weight: 600; letter-spacing: .06em; fill: #8a8372; text-anchor: middle; text-transform: uppercase }
  .lane { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11.5px; text-anchor: end }
  .rail { stroke: #ebe7dc }
  .bar { font-size: 12px; font-weight: 600; text-anchor: middle }
  .bar.s { text-anchor: start }
  .wait { font-size: 11px; fill: #b3ab9b; text-anchor: middle; font-style: italic }
  .sync { stroke: #9c5b4a; stroke-width: 1.4; stroke-dasharray: 5 4 }
  .synct { font-size: 11px; fill: #9c5b4a; text-anchor: middle; font-weight: 600 }
  .axis { fill: none; stroke: #ded9cd }
</style>
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#ded9cd"/></marker></defs>
<text x="245.0" y="34" class="ph">1. sequential</text>
<text x="563.0" y="34" class="ph">2. parallel</text>
<text x="92" y="86.0" class="lane" fill="#3f6b9c">thread 1</text>
<line x1="104" y1="82.0" x2="740" y2="82.0" class="rail"/>
<text x="92" y="132.0" class="lane" fill="#4a7f6b">thread 2</text>
<line x1="104" y1="128.0" x2="740" y2="128.0" class="rail"/>
<text x="92" y="178.0" class="lane" fill="#a9762f">thread 3</text>
<line x1="104" y1="174.0" x2="740" y2="174.0" class="rail"/>
<rect x="104" y="68" width="274" height="28" fill="#eaf0f7" stroke="#3f6b9c"/>
<text x="241.0" y="86.0" class="bar" fill="#3f6b9c">move 1, searched alone</text>
<text x="241.0" y="132.0" class="wait">waiting</text>
<text x="241.0" y="178.0" class="wait">waiting</text>
<line x1="386" y1="52" x2="386" y2="198" class="sync"/>
<text x="386" y="216" class="synct">α bound known</text>
<rect x="394" y="68" width="222" height="28" fill="#eaf0f7" stroke="#3f6b9c"/>
<text x="406" y="86.0" class="bar s" fill="#3f6b9c">move 2</text>
<rect x="394" y="114" width="292" height="28" fill="#e9f2ee" stroke="#4a7f6b"/>
<text x="406" y="132.0" class="bar s" fill="#4a7f6b">move 3</text>
<rect x="394" y="160" width="172" height="28" fill="#f9f1e3" stroke="#a9762f"/>
<text x="406" y="178.0" class="bar s" fill="#a9762f">move 4</text>
<path d="M104 242 H740" class="axis" marker-end="url(#a)"/>
<text x="740" y="236" class="wait" text-anchor="end">time</text>
</svg>
<figcaption>YBWC first searches the first move alone, long enough to get a reliable bound; the other threads sit idle in the meantime, then share the following moves with an already narrowed window.</figcaption>
</figure>

# Lazy SMP: share nothing, or almost

**Lazy SMP** *(<strong>L</strong>azy <strong>S</strong>ymmetric <strong>M</strong>ulti<strong>P</strong>rocessing)* turns the problem on its head. Instead of splitting the tree, we simply run **the same search** on every thread, from the root position, each doing its own iterative deepening.

No synchronization, no splitting, no work distribution. The only thing the threads share is the **transposition table**, which becomes global and concurrent.

That is the whole paradox of the method: if the threads did exactly the same work, the gain would be zero. But the shared transposition table is enough to make them diverge in useful ways:

- as soon as one thread writes a result to the table, the others read it and avoid recomputing that subtree;
- the best move stored in the table changes the **move ordering** of the other threads, which then explore their nodes in a different order;
- these differences in ordering change the bounds encountered, hence the cutoffs, hence the subtrees visited, and the gap widens as the search progresses.

The threads therefore naturally explore different parts of the tree, without us ever having to ask them to. A thread that happens to stumble on a good move early fills the table with tight bounds that all the others benefit from immediately.

<pre class="mermaid">
sequenceDiagram
  participant T1 as Thread 1
  participant TT as Transposition table
  participant T2 as Thread 2
  T1->>TT: is position P known?
  TT-->>T1: no, nothing in the table
  T1->>T1: explores the subtree of P
  T1->>TT: writes the score and best move of P
  T2->>TT: is position P known?
  TT-->>T2: yes, score + best move
  Note over T2: does not explore P
</pre>

> To deliberately amplify the divergence, most implementations slightly desynchronize the threads: some start at an offset depth, or skip depths, so that they never search exactly the same iteration at the same time.

# Concurrent access to the table

Sharing the transposition table between threads raises one difficulty. An entry contains several fields (Zobrist key, score, depth, bound type, best move) that exceed the size of an atomic write. Two threads writing to the same slot at the same time can produce a **torn** entry: the key from one with the score from the other.

The usual answer is... to do nothing. We accept these rare corruptions, relying on the fact that the stored Zobrist key already acts as a check: a torn entry is overwhelmingly likely to fail the key comparison, and is therefore simply ignored. The rare cases that slip through introduce an error in one branch, which a deeper search will usually correct.

> Locking the table would be disastrous: it is the most heavily used structure in the engine, and a global lock would wipe out the entire benefit of parallelism.
>
> Some engines still reduce the risk by storing a small *checksum* in the entry, or by packing the fields so that the whole thing fits in a single 128-bit atomic write.

# Retrieving the result

Since each thread runs its own search, we need to decide which one is authoritative. The convention is to keep the result of the thread that completed the **highest depth**, using the score as a tiebreaker. When the allotted time runs out, we never take the result of an incomplete iteration: just like with sequential iterative deepening, only the last fully explored depth is reliable.

One consequence worth knowing: an engine using Lazy SMP is no longer **deterministic**. Two searches on the same position, with the same time, can return different moves depending on the exact order in which the threads filled the table. This is a real drawback for debugging and regression testing, and the reason engines are almost always tested single-threaded.

# Why it is the dominant method

The simplicity of the code is the most visible reason, and it is not a minor one: the search function stays the sequential version, unchanged; we just run it $N$ times and make the transposition table concurrent. There is no tree splitting, no task distribution, and no synchronization to write.

But stopping there would misrepresent the situation, as if Lazy SMP were a compromise we accept out of laziness. Several deeper reasons explain why it is not only cheaper to write, but also **competitive in playing strength**.

## The modern tree is too irregular to split

YBWC relies on a strong assumption: the first move searched establishes a reliable $\alpha$ bound, and the following moves are comparable subtrees that can be distributed.

That assumption has eroded as lossy pruning and reductions have become widespread. Today, at a single node, one move can be searched at reduced depth, cut immediately, or trigger a full **re-search** at full depth if its score exceeds $\alpha$. The cost of a branch is no longer predictable **before** exploring it, and it varies by several orders of magnitude from one move to the next. Statically distributing work whose size you do not know leads to unevenly loaded threads, hence work stealing, hence even more synchronization.

## The transposition table already does the coordination

The role played by the transposition table has also grown a lot. It no longer just stores scores to avoid recomputation: it holds the **best move** for each position, and therefore most of the move ordering.

And that is exactly the information a parallel algorithm needs to share. By making the table concurrent, we get a communication channel between threads for free: each one publishes its best moves and reads those of the others, at every node, with no explicit protocol. The fine-grained coordination that YBWC implements by hand already exists, in an implicit and asynchronous form.

## The hardware has changed shape

Finally, YBWC was designed at a time when people talked about a handful of processors. On today's machines (many cores, several levels of cache, possibly several NUMA nodes), the cost of a shared synchronization point grows with the number of participants, while a search with no synchronization scales almost freely. The ranking of the two approaches therefore flips beyond a few threads, not because Lazy SMP gets better, but because the price of synchronization goes up.
