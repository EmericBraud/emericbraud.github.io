---
translationKey: 7-pile-et-tas
layout: post.njk
title: The stack, the heap, and the cost of an allocation
date: 2026-09-10
section: Programming techniques
chapter: Memory management
chapterOrder: 7
---
While developing [Alcyon](https://github.com/EmericBraud/alcyon), I had to deepen my understanding of how memory works in a program. These concepts feel very abstract when you write Python or work with a JavaScript framework, but they become unavoidable as soon as you go down a level and start chasing performance.

A program has two main areas for storing the data it creates at runtime: the **stack** and the **heap**. Both live in RAM, and they have very different, complementary structural properties.

<figure id="carte-memoire">
<svg viewBox="0 0 620 410" width="100%" style="max-width:620px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Memory map of a program: code, global data, heap, free space, stack">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .sn { font-size: 13px; font-weight: 600 }
  .sd { font-size: 11px; fill: #8a8372 }
  .ax { font-size: 10.5px; fill: #8a8372; text-anchor: middle }
  .ax.s { text-anchor: start }
  .ax.e { text-anchor: end }
  .gl { fill: #3f6b9c; font-weight: 600 }
  .gl.t { fill: #4a7f6b }
  .gap { fill: #fdfcfa; stroke: #ded9cd; stroke-dasharray: 4 4 }
  .gr { fill: none; stroke: #3f6b9c; stroke-width: 1.3 }
  .gr.t { stroke: #4a7f6b }
</style>
<defs>
<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#3f6b9c"/></marker>
<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#4a7f6b"/></marker>
</defs>
<text x="300.0" y="18" class="ttl">MEMORY OF A PROGRAM</text>
<text x="462" y="38" class="ax s">high addresses</text>
<rect x="150" y="34" width="300" height="78" fill="#eaf0f7" stroke="#3f6b9c"/>
<rect x="150" y="34" width="4" height="78" fill="#3f6b9c"/>
<text x="166" y="60" class="sn" fill="#3f6b9c">Stack</text>
<text x="166" y="80" class="sd">local variables, call frames</text>
<rect x="150" y="112" width="300" height="92" class="gap"/>
<text x="300.0" y="162.0" class="ax">free space</text>
<rect x="150" y="204" width="300" height="78" fill="#e9f2ee" stroke="#4a7f6b"/>
<rect x="150" y="204" width="4" height="78" fill="#4a7f6b"/>
<text x="166" y="230" class="sn" fill="#4a7f6b">Heap</text>
<text x="166" y="250" class="sd">dynamic allocations</text>
<rect x="150" y="282" width="300" height="52" fill="#f4f2ec" stroke="#8a8372"/>
<rect x="150" y="282" width="4" height="52" fill="#8a8372"/>
<text x="166" y="308" class="sn" fill="#8a8372">Global data</text>
<text x="166" y="328" class="sd">static variables, constants</text>
<rect x="150" y="334" width="300" height="52" fill="#f4f2ec" stroke="#8a8372"/>
<rect x="150" y="334" width="4" height="52" fill="#8a8372"/>
<text x="166" y="360" class="sn" fill="#8a8372">Code</text>
<text x="166" y="380" class="sd">the program's instructions</text>
<text x="462" y="386" class="ax s">low addresses</text>
<path d="M394 54 V140" class="gr" marker-end="url(#a)"/>
<text x="386" y="77.0" class="ax e gl">grows</text>
<path d="M394 262 V176" class="gr t" marker-end="url(#b)"/>
<text x="386" y="247.0" class="ax e gl t">grows</text>
</svg>
<figcaption>The two areas face each other and grow toward one another, sharing the same free space.</figcaption>
</figure>

It is the diagram every developer has seen at least once, often without knowing what it actually implies.

{% partie "Part one", "How memory works" %}

# The stack

The stack is the memory area a program uses **by default**: every local variable in a function, every parameter, every return value lands there without you asking for anything. Writing `int score = 0;` inside a function is a stack allocation.

<figure class="side">
<svg viewBox="0 0 382 403" width="100%" style="max-width:382px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The stack: one colored frame per called function, one slot per local variable">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .fn { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px; font-weight: 600 }
  .cur { font-size: 9.5px; letter-spacing: .06em; text-anchor: end; text-transform: uppercase }
  .var { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11px; fill: #3d3b35 }
  .sz { font-size: 10px; fill: #9a9488; text-anchor: end }
  .ax { font-size: 10.5px; fill: #8a8372; text-anchor: middle }
  .ax.s { text-anchor: start }
  .ax.lim { fill: #9c5b4a }
  .spt { fill: #3f6b9c; font-weight: 600 }
  .it { font-style: italic }
  .free { fill: #fdfcfa; stroke: #ded9cd; stroke-dasharray: 4 4 }
  .limit { stroke: #c98b7b; stroke-width: 1.5; stroke-dasharray: 6 4 }
  .sp { fill: none; stroke: #3f6b9c; stroke-width: 1.4 }
</style>
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0 0 L10 5 L0 10 z" fill="#3f6b9c"/></marker></defs>
<text x="168.0" y="16" class="ttl">THREAD STACK</text>
<text x="326" y="41" class="ax s">high<tspan x="326" dy="11">addresses</tspan></text>
<rect x="18" y="32" width="300" height="85" fill="#eaf0f7" stroke="#3f6b9c" stroke-width="1"/>
<rect x="18" y="32" width="4" height="85" fill="#3f6b9c"/>
<text x="32" y="50" class="fn" fill="#3f6b9c">main()</text>
<rect x="32" y="58" width="258" height="20" fill="#fff" stroke="#3f6b9c" stroke-opacity=".45"/>
<text x="40" y="72" class="var">argc</text>
<text x="282" y="72" class="sz">4 B</text>
<rect x="32" y="83" width="258" height="20" fill="#fff" stroke="#3f6b9c" stroke-opacity=".45"/>
<text x="40" y="97" class="var">argv</text>
<text x="282" y="97" class="sz">8 B</text>
<rect x="18" y="117" width="300" height="110" fill="#e9f2ee" stroke="#4a7f6b" stroke-width="1"/>
<rect x="18" y="117" width="4" height="110" fill="#4a7f6b"/>
<text x="32" y="135" class="fn" fill="#4a7f6b">search(depth)</text>
<rect x="32" y="143" width="258" height="20" fill="#fff" stroke="#4a7f6b" stroke-opacity=".45"/>
<text x="40" y="157" class="var">alpha</text>
<text x="282" y="157" class="sz">4 B</text>
<rect x="32" y="168" width="258" height="20" fill="#fff" stroke="#4a7f6b" stroke-opacity=".45"/>
<text x="40" y="182" class="var">beta</text>
<text x="282" y="182" class="sz">4 B</text>
<rect x="32" y="193" width="258" height="20" fill="#fff" stroke="#4a7f6b" stroke-opacity=".45"/>
<text x="40" y="207" class="var">moves[218]</text>
<text x="282" y="207" class="sz">872 B</text>
<rect x="18" y="227" width="300" height="60" fill="#f9f1e3" stroke="#a9762f" stroke-width="1.6"/>
<rect x="18" y="227" width="4" height="60" fill="#a9762f"/>
<text x="32" y="245" class="fn" fill="#a9762f">evaluate()</text>
<rect x="32" y="253" width="258" height="20" fill="#fff" stroke="#a9762f" stroke-opacity=".45"/>
<text x="40" y="267" class="var">score</text>
<text x="282" y="267" class="sz">4 B</text>
<text x="304" y="245" class="cur" fill="#a9762f">running</text>
<rect x="18" y="287" width="300" height="86" class="free"/>
<path d="M168.0 327 V293" class="sp" marker-end="url(#a)"/>
<text x="168.0" y="343" class="ax spt">top of the stack</text>
<text x="168.0" y="363" class="ax">free space</text>
<line x1="10" y1="373" x2="326" y2="373" class="limit"/>
<text x="168.0" y="391" class="ax lim">limit: <tspan class="it">stack overflow</tspan></text>
<text x="326" y="357" class="ax s">low<tspan x="326" dy="11">addresses</tspan></text>
</svg>
<figcaption>Each call pushes a frame, one slot per local variable; returning pops it all at once.</figcaption>
</figure>

It is a contiguous region of memory _(a single block)_, private to each thread, managed by a simple pointer. Entering a function reserves room for its local variables by moving that pointer, and leaving it puts the pointer back where it was. A stack allocation therefore costs one arithmetic instruction, and freeing it costs literally nothing.

You can think of the stack as a bookmark in a book: each function call moves it forward by as many pages as its local variables take up, and returning moves it back exactly where it was.

That simplicity is exactly what makes it fast, and it is also what imposes two limits you cannot get around.

**The size of every variable must be known in advance.** The memory each function needs is fixed at compile time.

**The stack is small.** Where the heap can take up all available memory, the stack is capped at its initial reservation, often 1 to 8 MB per thread. That is plenty for local variables, but it quickly falls short once you handle real volumes of data: a chess engine's [transposition table](/en/posts/3-transposition-table/), several hundred megabytes, obviously wouldn't fit.

Going past that limit, the famous *stack overflow*, isn't reported through an error code you could handle: the program just dies. The two usual culprits are recursion that goes too deep and a large array declared as a local variable.

These two limits are the reason the other area exists.

{% plus "A few more details about the stack" %}

Since successive calls keep reusing the same addresses, the top of the stack is almost always already in the L1 cache. That is another reason it is so fast.

By convention on common architectures, the stack grows toward **lower** addresses: pushing a frame therefore *decreases* the stack pointer.

Finally, the known-size rule has a notable exception in C: [_Variable-length Arrays_](https://en.wikipedia.org/wiki/Variable-length_array), which allow a dynamically sized allocation on the stack.

{% endplus %}

{% plus "What about an interpreted language like Python?" %}

In Python, the program actually running on the machine is not the one you write: it is the interpreter, which reads your code and executes it as it goes. The machine's stack is therefore the interpreter's stack, and the interpreter then simulates its own stack to run your code.

The variables you declare in your code are only references pointing to objects allocated on the heap. That is what the saying "in Python, everything is an object" really means.

{% endplus %}

# The heap

The **heap** is a global resource, shared by the whole process. Asking for memory means calling an allocator, which is real code: it has to find a free block that is large enough, update its internal structures, and possibly request memory from the operating system. Freeing is explicit and can happen in any order, unlike the stack, where the last block reserved is always the first one released. Nothing guarantees either that two consecutive allocations will be adjacent in memory.

You can think of the heap as a library: there is much more room, but you have to ask the librarian for a free shelf big enough. Your books often end up spread across shelves far apart from each other, and sometimes, especially on small embedded systems, there is no shelf left at all.

Here is a quick summary of the differences between the stack and the heap:

<table>
  <thead>
    <tr><th></th><th>Stack</th><th>Heap</th></tr>
  </thead>
  <tbody>
    <tr><td>Allocation cost</td><td>one instruction</td><td>function call, variable path</td></tr>
    <tr><td>Freeing</td><td>automatic, free</td><td>explicit, the program's responsibility</td></tr>
    <tr><td>Lifetime</td><td>tied to scope</td><td>arbitrary</td></tr>
    <tr><td>Locality</td><td>excellent, hot cache</td><td>depends on allocation history</td></tr>
    <tr><td>Available size</td><td>limited (often 1 to 8 MB)</td><td>practically unlimited for our purposes (bounded by RAM)</td></tr>
    <tr><td>Concurrency</td><td>one stack per thread</td><td>structure shared between threads</td></tr>
  </tbody>
</table>

The last row is the one people forget most often, and it is precisely the one that hurts the most in a multithreaded program.

{% plus "Where heap memory really comes from: <code>brk</code> and <code>mmap</code>" %}

Contrary to a common belief, the allocator does **not** live at the operating system level: it is a library bundled into the program, which manages its memory in user space. It only calls on the kernel when it needs more room.

So the heap is not a reserve the program owns from the moment it starts: it requests it from the operating system, bit by bit, through one of two mechanisms.

The first is the historical one. For each process, the kernel keeps a boundary, the *program break*, which marks the end of the data segment. The [`brk`](https://man7.org/linux/man-pages/man2/brk.2.html) system call moves that boundary and enlarges the usable area by the same amount. This is the heap from the [first diagram](#carte-memoire) in this article, the one that "grows toward higher addresses".

The second is the one that dominates today. With [`mmap`](https://man7.org/linux/man-pages/man2/mmap.2.html), the program no longer pushes a boundary: it asks the kernel for an **entirely new region**, which the kernel places wherever it likes in the address space. glibc automatically switches to this mechanism above a certain threshold, 128 KB by default.

> This is the real reason the heap is not a contiguous region. The picture of a single area growing upward only holds for small allocations; large ones live in separate regions, scattered across the address space.

This distinction has a visible consequence. A block obtained through `mmap` is returned to the system when it is freed, and the process's memory really does shrink. A block from the historical heap, on the other hand, almost always stays with the process: the allocator takes it back into its internal lists for reuse, but practically never lowers the *program break*. That is why the memory usage reported by the system doesn't necessarily go down after freeing a lot of objects.

{% endplus %}

{% plus "What happens when you run out of room" %}

Contrary to what [that first diagram](#carte-memoire) suggests, the stack and the heap never collide. When room runs out, it is the kernel that refuses to extend the region: `brk` or `mmap` fails, the allocator (bundled into our program) returns a null pointer, and `new` throws a [`std::bad_alloc`](https://en.cppreference.com/w/cpp/memory/new/bad_alloc) exception. Three quite different situations hide behind that failure.

**The address space is full.** Out of reach on a 64-bit machine, this was a real limit on 32-bit systems: the total space there is 4 GiB, part of which the kernel reserves for itself, leaving the process only 2 to 3 GiB regardless of how much RAM was installed.

**Physical memory is exhausted.** On Linux, this usually doesn't make the allocation fail, because of **overcommit**. When a program asks for memory, the kernel only reserves addresses for it, and only supplies actual RAM when the program writes to it. Since programs rarely use everything they ask for, the kernel promises more memory than it has, the way an airline sells more seats than the plane holds. If the bet is lost, it is too late to make the allocation fail, since it succeeded long ago: the kernel then frees memory by force with the OOM killer, which picks a process and kills it, sometimes not the culprit.

<figure class="side">
<svg viewBox="0 0 384 380" width="100%" style="max-width:384px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Heap fragmentation: three free but non-contiguous blocks, a request for three blocks fails">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .ttl { font-size: 10.5px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .cap { font-size: 10.5px; fill: #8a8372; text-anchor: middle }
  .bn { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11.5px; font-weight: 600; text-anchor: middle }
  .hole { fill: #fdfcfa; stroke: #ded9cd; stroke-dasharray: 4 4 }
  .lib { font-size: 10.5px; fill: #b3ab9b; text-anchor: middle }
  .ask { fill: none; stroke: #c98b7b; stroke-width: 1.4; stroke-dasharray: 5 4 }
  .askt { font-size: 11px; fill: #9c5b4a; text-anchor: middle; font-weight: 600 }
  .no { font-size: 10.5px; fill: #9c5b4a; text-anchor: middle }
</style>
<text x="192.0" y="16" class="ttl">THE HEAP</text>
<text x="86.0" y="40" class="cap">After a few allocations</text>
<rect x="20" y="52" width="132" height="78" fill="#eaf0f7" stroke="#3f6b9c"/>
<rect x="20" y="52" width="4" height="78" fill="#3f6b9c"/>
<text x="86.0" y="95.0" class="bn" fill="#3f6b9c">block A</text>
<rect x="20" y="130" width="132" height="52" fill="#e9f2ee" stroke="#4a7f6b"/>
<rect x="20" y="130" width="4" height="52" fill="#4a7f6b"/>
<text x="86.0" y="160.0" class="bn" fill="#4a7f6b">block B</text>
<rect x="20" y="182" width="132" height="52" fill="#f9f1e3" stroke="#a9762f"/>
<rect x="20" y="182" width="4" height="52" fill="#a9762f"/>
<text x="86.0" y="212.0" class="bn" fill="#a9762f">block C</text>
<rect x="20" y="234" width="132" height="26" class="hole"/>
<text x="86.0" y="251.0" class="lib">free</text>
<text x="298.0" y="40" class="cap">After freeing B</text>
<rect x="232" y="52" width="132" height="78" fill="#eaf0f7" stroke="#3f6b9c"/>
<rect x="232" y="52" width="4" height="78" fill="#3f6b9c"/>
<text x="298.0" y="95.0" class="bn" fill="#3f6b9c">block A</text>
<rect x="232" y="130" width="132" height="52" class="hole"/>
<text x="298.0" y="160.0" class="lib">free</text>
<rect x="232" y="182" width="132" height="52" fill="#f9f1e3" stroke="#a9762f"/>
<rect x="232" y="182" width="4" height="52" fill="#a9762f"/>
<text x="298.0" y="212.0" class="bn" fill="#a9762f">block C</text>
<rect x="232" y="234" width="132" height="26" class="hole"/>
<text x="298.0" y="251.0" class="lib">free</text>
<rect x="226" y="276" width="144" height="78" class="ask"/>
<text x="298.0" y="311.0" class="askt">request for 3 blocks</text>
<text x="298.0" y="329.0" class="no">denied</text>
</svg>
<figcaption>Freeing leaves holes: there is enough room in total, but no contiguous block is large enough.</figcaption>
</figure>

**Memory is fragmented.** This is the most insidious case, and the one that really matters in embedded systems: the total free memory is more than enough, but it is split into pieces, none of which is large enough. The allocation then fails even though nothing has changed in the program, simply because it has been running for a long time.

{% endplus %}

# A practical case: std::vector in C++

A [`std::vector`](https://en.cppreference.com/w/cpp/container/vector) is the standard library's dynamically sized array: unlike a C array or a [`std::array`](https://en.cppreference.com/w/cpp/container/array), whose number of elements is fixed at compile time (and which therefore lives on the stack), a vector can grow and shrink at runtime, one [`push_back`](https://en.cppreference.com/w/cpp/container/vector/push_back) after another. It is the default container in C++.

That flexibility isn't free. A vector is actually split between the stack and the heap. The object itself only holds three pointers (start of the data, end of the data, end of the capacity), which is 24 bytes on a 64-bit machine, and it lives on the stack. The elements, however, are always on the heap.

<figure>
<svg viewBox="0 0 820 300" width="100%" style="max-width:820px" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A std::vector: three pointers on the stack marking the start, the end of the elements and the end of the buffer allocated on the heap">
<style>
  text { font-family: "Noto Sans", -apple-system, Helvetica, sans-serif }
  .zone { fill: #fcfbf8; stroke: #ded9cd; stroke-dasharray: 4 3 }
  .zt { font-size: 11px; font-weight: 600; letter-spacing: .09em; fill: #8a8372; text-anchor: middle }
  .obj { fill: #fff; stroke: #b9b2a2 }
  .sep { stroke: #e6e1d4 }
  .lbl { font-size: 13px; font-weight: 600; fill: #3d3b35; text-anchor: middle }
  .mono { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12.5px; fill: #3d3b35 }
  .mono.c { text-anchor: middle; fill: #1f4e79; font-weight: 600 }
  .mk { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11.5px; font-weight: 600 }
  .note { font-size: 11px; fill: #8a8372; text-anchor: middle }
  .cell { fill: #e8eef5; stroke: #9db4cd }
  .cell.free { fill: #fbfaf7; stroke: #ded9cd; stroke-dasharray: 3 3 }
  .link { fill: none; stroke: #c3bcab; stroke-width: 1.2; stroke-dasharray: 5 3 }
  .brace { fill: none; stroke: #ded9cd }
</style>
<defs><marker id="begin" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#3f6b9c"/></marker><marker id="end" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#4a7f6b"/></marker><marker id="capacity" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#a9762f"/></marker><marker id="g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#c3bcab"/></marker></defs>
<rect x="14" y="60" width="312" height="180" rx="3" class="zone"/>
<text x="170" y="48" class="zt">STACK</text>
<rect x="412" y="60" width="384" height="180" rx="3" class="zone"/>
<text x="604.0" y="48" class="zt">HEAP</text>
<rect x="46" y="112" width="214" height="90" class="obj"/>
<text x="153.0" y="98" class="lbl">std::vector&lt;int&gt; v</text>
<text x="153.0" y="224" class="note">24 bytes</text>
<rect x="58" y="122.0" width="10" height="10" fill="#3f6b9c"/>
<text x="78" y="131.0" class="mono">begin</text>
<line x1="46" y1="142" x2="260" y2="142" class="sep"/>
<rect x="58" y="152.0" width="10" height="10" fill="#4a7f6b"/>
<text x="78" y="161.0" class="mono">end</text>
<line x1="46" y1="172" x2="260" y2="172" class="sep"/>
<rect x="58" y="182.0" width="10" height="10" fill="#a9762f"/>
<text x="78" y="191.0" class="mono">capacity</text>
<path d="M260 157.0 H438" class="link" marker-end="url(#g)"/>
<text x="356.0" y="149.0" class="note">point into this buffer</text>
<rect x="452" y="150" width="38" height="38" class="cell"/>
<text x="471.0" y="175" class="mono c">3</text>
<rect x="490" y="150" width="38" height="38" class="cell"/>
<text x="509.0" y="175" class="mono c">7</text>
<rect x="528" y="150" width="38" height="38" class="cell"/>
<text x="547.0" y="175" class="mono c">1</text>
<rect x="566" y="150" width="38" height="38" class="cell"/>
<text x="585.0" y="175" class="mono c">9</text>
<rect x="604" y="150" width="38" height="38" class="cell free"/>
<rect x="642" y="150" width="38" height="38" class="cell free"/>
<rect x="680" y="150" width="38" height="38" class="cell free"/>
<rect x="718" y="150" width="38" height="38" class="cell free"/>
<path d="M452 120 V146" stroke="#3f6b9c" stroke-width="1.6" fill="none" marker-end="url(#begin)"/>
<text x="456" y="112" class="mk" fill="#3f6b9c" text-anchor="start">begin</text>
<path d="M604 120 V146" stroke="#4a7f6b" stroke-width="1.6" fill="none" marker-end="url(#end)"/>
<text x="604" y="112" class="mk" fill="#4a7f6b" text-anchor="middle">end</text>
<path d="M756 120 V146" stroke="#a9762f" stroke-width="1.6" fill="none" marker-end="url(#capacity)"/>
<text x="752" y="112" class="mk" fill="#a9762f" text-anchor="end">capacity</text>
<path d="M455 198 V204 H601 V198" class="brace"/>
<text x="528.0" y="220" class="note">4 elements</text>
<path d="M607 198 V204 H753 V198" class="brace"/>
<text x="680.0" y="220" class="note">free capacity</text>
</svg>
<figcaption>The vector's three pointers fit on the stack; the elements live in a buffer on the heap. The slack between <code>end</code> and <code>capacity</code> is what avoids a reallocation on every insertion.</figcaption>
</figure>

Two consequences follow. The first is an **indirection**: reading `v[i]` means following a pointer to the heap, into a region that has no reason to be in the cache. The second is **reallocation**: when `push_back` exceeds the capacity, the vector allocates a bigger buffer (usually twice as large), moves the elements into it, then frees the old one.

Filling a vector with 1000 elements this way therefore triggers about ten allocations, along with the corresponding copies. The cost is amortized $O(1)$ per element: excellent on average, unusable when what matters is the worst case. [`reserve`](https://en.cppreference.com/w/cpp/container/vector/reserve) fixes this by allocating the desired capacity in one go, but it removes neither the allocation itself nor the indirection.

{% plus "An almost universal split: the case of Java" %}

This split between a wrapper on the stack and contents on the heap is in no way specific to C++, and in some languages it is even the rule. In Java, apart from primitive types, all data lives on the heap: an object variable only holds a reference to the object.

That is why `NullPointerException` is the most common error there. The reference may point to no object at all, and you only find out when you try to use it at runtime. The difference with C++ is that where this split is enforced and invisible in Java, it remains an explicit choice in C++: a C++ object can live entirely on the stack.

{% endplus %}

# The real cost of a dynamic allocation

In the best case, the allocator finds a free block in a thread-local cache and returns within a few tens of nanoseconds. In the worst case, it has to reorganize its free blocks, wait for other threads, or ask the kernel for memory: you are then looking at several microseconds, a factor of a hundred.

> The problem with a dynamic allocation isn't its average, it's its variance. A low but unpredictable cost is much harder to absorb than a high but constant one.

{% partie "Part two", "What this changes for Alcyon" %}

# The rule: zero allocations on the hot path

A chess engine's search function is called several million times per second. At that rate, a single allocation per node is enough to make the allocator the busiest component of the program, ahead of evaluation and move generation. [Lazy SMP](/en/posts/6-lazy-smp/) makes the problem even worse: every thread runs the same search loop, so an allocation in that loop means they all hammer the allocator at the same time.

The rule is therefore absolute: **no dynamic allocation on the hot path**. In practice, this means:

- move lists are fixed-size arrays on the stack, sized for the worst case: the theoretical maximum is 218 legal moves in a position. Alcyon reserves [256 entries](https://github.com/EmericBraud/alcyon/blob/main/src/common/constants.hpp#L7), which [`MoveList`](https://github.com/EmericBraud/alcyon/blob/main/src/core/move/move_list.hpp#L7-L11) declares as raw arrays;
- depth-indexed structures, such as [killer moves](/en/posts/5-move-ordering/) or the game history, are arrays preallocated once and for all;
- per-thread objects are allocated when the thread is created, never during the search;
- large objects (transposition table, neural network weights, precomputed move generation tables) are allocated only once, at startup. Between two searches, the table isn't even cleared: an age counter is enough to recognize stale entries.

{% plus "The trap of invisible allocations" %}

The tricky part is that many allocations are **invisible** in the code. A `std::string` built for a log message, a `std::function` capturing more than its internal storage allows, a `std::map` allocating a node per insertion, a local `std::vector` in a utility function: none of these announces itself as an allocation, and every one of them is. The only reliable way to be sure is to measure, by instrumenting `operator new` to count calls during a search: the expected number is zero.

{% endplus %}

# The general principle

None of this condemns dynamic allocation: without it, you couldn't write a program whose needs are only known at runtime. But allocating means calling on a **shared service** whose response time and availability are out of your control. The right reaction, then, is not to allocate less, but to allocate **at the right time**: a moment you choose, rather than in the middle of the program's hottest loop. In safety-critical systems or those chasing absolute performance, all memory is therefore reserved at startup, in fixed-size buffers sized for the worst case, and the program never calls the allocator again afterward: the question "what do we do if the allocation fails?" disappears instead of having to be handled. This is what NASA's coding rules or the MISRA C standard in the automotive industry require, for example.
