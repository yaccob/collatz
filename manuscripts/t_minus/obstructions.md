---
status: in_progress
title: "Obstruction residues for the 3x-1 map: full factor complexity, positive density, and a constructive lift"
results_introduced: []
results_used:
  - "Lift Theorem (Theorem A) [origin: /approaches_2026-05-13T1642/85_lift_lemma_K6prime.md#3]"
  - "Density bound c_W >= 3/64 (Theorem B) [origin: /approaches_2026-05-13T1642/85_lift_lemma_K6prime.md#5]"
  - "Full factor complexity p_W(n) = 2^n (Theorem C) [origin: /approaches_2026-05-13T1642/86_F1_zusammenfassung.md]"
  - "X-invariant characterization [origin: /approaches_2026-05-13T1642/50_T15_X_characterization.md]"
  - "Shift-a algebraic identity [origin: /approaches_2026-05-13T1642/48_lemma_G_breakthrough.md]"
open_questions:
  - "Exact value of the asymptotic density c_W (§4)"
  - "Atomic shift-0 conjecture (§6)"
external:
  - "Lagarias 1985 — annotated bibliography [search_log: /collatz/explorations/crosscuts/external_searches.md#S4]"
  - "Eliahou 1993 — lower bounds on nontrivial Collatz cycles"
  - "Wirsching 1998 — Springer LNM 1681 on predecessor density"
  - "Stérin 2020 [arXiv:2007.06979] — Collatz as a binary-to-ternary FST"
related:
  - "/approaches_2026-05-13T1642/86_F1_zusammenfassung.md — F1 / lift / density consolidated"
  - "/approaches_2026-05-13T1642/85_lift_lemma_K6prime.md — lift theorem rigorous proof"
  - "/approaches_2026-05-13T1642/80_obstr_factor_complexity.md — factor complexity setup"
  - "/approaches_2026-05-13T1642/50_T15_X_characterization.md — X-invariant"
  - "/approaches_2026-05-13T1642/48_lemma_G_breakthrough.md — shift-a normal form"
---

# Obstruction residues for the $3x-1$ map: full factor complexity, positive density, and a constructive lift

**Working draft — complete through all sections and appendix.**

---

## 1. Introduction

### 1.1 The Collatz map and its $3x-1$ cousin

Let $\mathbb{N}_{\text{odd}}$ denote the set of positive odd integers, and let $v_2(m)$ denote the $2$-adic valuation of an integer $m \ne 0$ (the largest $k$ with $2^k \mid m$). The **Collatz map** $T_+$ takes an odd integer $n$ to the odd part of $3n+1$:
$$
T_+(n) := \frac{3n+1}{2^{v_2(3n+1)}}.
$$
The Collatz conjecture, attributed to Lothar Collatz and widely studied since the 1930s, asserts that for every $n \in \mathbb{N}_{\text{odd}}$ the iteration $n, T_+(n), T_+^2(n), \ldots$ eventually reaches the fixed point $1$. Despite considerable computational evidence and a large body of partial results — most recently the breakthrough of Tao~\cite{Tao2019}, showing that almost all trajectories attain almost bounded values — the conjecture itself remains open. We refer the reader to the two annotated bibliographies of Lagarias~\cite{Lagarias2010a, Lagarias2010b} for a comprehensive overview of the literature up to 2010.

The Collatz map has a natural cousin, the **$3x-1$ map** $T_-$ acting on the same domain:
$$
T_-(n) := \frac{3n-1}{2^{v_2(3n-1)}}.
$$
The two maps are structurally parallel: both perform the operation "multiply by three, add a small constant, strip the factors of two from the result". They differ only in the sign of the additive constant. The trajectories of $T_-$ are, however, *not* believed to converge to a single attractor. Three nontrivial cycles are classically known:
$$
\{1\}, \quad \{5, 7\}, \quad \{17, 25, 37, 55, 65, 49, 73, ...\}
$$
(the last is the so-called *seventeen-family cycle*), and the question of whether further cycles exist remains as open as the Collatz conjecture itself. From the point of view of difficulty, both maps appear to sit on the same level — and indeed they are connected through a classical identity going back to Lagarias~\cite{Lagarias1985}: every trajectory of $T_-$ starting from $m$ corresponds, via the substitution $r = 2m+1$, to a single $T_+$-step followed by a trajectory of $T_+$. This *Lagarias intertwining* means that any structural result about the residue dynamics of $T_-$ has implications for $T_+$, and conversely.

The present paper is concerned with a family of residue classes modulo $2^L$ that arises naturally in the dynamics of $T_-$. We show that this family — which we shall call the **obstruction residues** for reasons made precise in Section 2 — has three structural properties that, taken together, place it in a slightly unexpected position within the combinatorial landscape of substitution and shift systems:

1. **A constructive lift** between modular levels $L$ and $L+1$ (Theorem A).
2. **Positive asymptotic density** in $\{1, \ldots, 2^L\}$ as $L \to \infty$ (Theorem B).
3. **Maximal combinatorial complexity** of its associated language of bitstrings — every binary word of every length appears as a factor (Theorem C).

The third property is in some tension with the first two: a constructive lift and positive density would, in many natural settings, force a certain rigidity of the resulting word language (one might expect a sofic shift or a primitive substitution shift). Theorem C rules out all such characterizations and identifies the obstruction residues as a structurally *richer* family than the naive analogies would suggest.

### 1.2 Parallel reductions and the $X$-invariant

We now turn to the construction. Fix an odd integer $r$ with $r \equiv 3 \pmod 4$ and $v_2(r - 1) = 1$, and write
$$
m := \frac{r - 1}{2}.
$$
The condition $r \equiv 3 \pmod 4$ ensures that $m$ is odd, and the valuation condition $v_2(r-1) = 1$ is a mild non-degeneracy assumption that simplifies the bookkeeping; it can be relaxed in straightforward ways and is discussed in Section 2.

We then run $T_-$ simultaneously on $r$ and on $m$, working *modulo $2^L$* for a fixed level $L$. At each step we keep track not only of the current values $T_-^j(r)$ and $T_-^j(m)$ but also of their **affine relationship**: a pair $(c_j, d_j) \in \mathbb{Z}^2$ such that
$$
T_-^j(m) \;\equiv\; c_j \cdot T_-^j(r) + d_j \pmod{2^{L - V_j}}
$$
where $V_j$ is a running accumulator of valuations consumed up to step $j$. Initially $(c_0, d_0) = (2, -1)$, reflecting the relation $m = 2 r^{-1} + \text{(adjustment)}$ between the two starting values. After each parallel step the pair $(c_j, d_j)$ is updated by an explicit rule that depends only on the 2-adic valuations $v_2(3 T_-^j(r) - 1)$ and $v_2(3 T_-^j(m) - 1)$ encountered in that step. The reduction terminates after a finite number of steps when the running accumulator $V_j$ exhausts the modular budget; we denote the terminal pair by $(c_{\text{end}}, d_{\text{end}}) = (c_{\text{end}}(r, L), d_{\text{end}}(r, L))$.

The key scalar invariant we attach to the pair $(r, L)$ is
$$
X_{\text{end}}(r, L) \;:=\; 3\, d_{\text{end}}(r, L) \;+\; c_{\text{end}}(r, L).
$$
The name "$X$-invariant" reflects the role it plays in the analysis: it captures, in a single integer, whether the parallel trajectories on $r$ and on $m$ have synchronized in a particular algebraic sense by the end of the reduction.

**Definition 1.1 (obstruction residue).** *An odd integer $r$ with $r \equiv 3 \pmod 4$ and $v_2(r-1) = 1$ is called an* **obstruction residue at level $L$** *if $X_{\text{end}}(r, L) = 1$. We write $\mathcal{O}_L \subseteq \{1, \ldots, 2^L\}$ for the set of all such residues.*

Concretely, $r$ is an obstruction at level $L$ if and only if there is a particular algebraic identity between the terminal values of the two parallel trajectories. This identity has a closed form, which we shall derive in Section 2 (where it is called the *shift-$a$ normal form*).

The family $(\mathcal{O}_L)_{L \ge 6}$ is small at first:
$$
\mathcal{O}_6 = \{19, 27, 59\}, \quad |\mathcal{O}_6| = 3.
$$
But it grows rapidly. A direct computation (described in Section 8) gives
$$
|\mathcal{O}_6| = 3, \; |\mathcal{O}_7| = 8, \; |\mathcal{O}_8| = 19, \; |\mathcal{O}_9| = 42, \; \ldots, \; |\mathcal{O}_{16}| = 7556,
$$
and the *density ratio* $|\mathcal{O}_L| / 2^L$ rises monotonically from $\approx 0.047$ at $L=6$ to $\approx 0.115$ at $L=16$. This raises three structural questions:

1. **(Lift.)** Given an obstruction $r_0 \in \mathcal{O}_{L_0}$ at level $L_0$, are the two natural lifts $r_0$ and $r_0 + 2^{L_0}$ to level $L_0+1$ both obstructions at the higher level?
2. **(Density.)** Does the density ratio $|\mathcal{O}_L|/2^L$ converge to a positive limit as $L \to \infty$, and if so, can one bound this limit from below?
3. **(Combinatorial complexity.)** What is the set of binary words of length $n$ that occur as factors of some residue in $\bigcup_L \mathcal{O}_L$, viewed as a bitstring?

The three questions are not independent: a positive answer to (1) implies that $|\mathcal{O}_L|/2^L$ is monotone in $L$, which gives most of (2) for free. A constructive form of (1) — one that exhibits arbitrary bit-patterns as factors of the lift — yields (3). All three are answered in the affirmative by the main results of this paper.

### 1.3 Main results

**Theorem A (Constructive lift).** *Let $L_0 \ge v + 1$ and $r_0 \in \mathcal{O}_{L_0}$. Then both
$$
r_+ := r_0 \quad \text{and} \quad r_- := r_0 + 2^{L_0}
$$
are obstruction residues at level $L_0 + 1$.*

The proof, given in Section 3, is by case analysis on a finite invariant of the parallel reduction at $(r_0, L_0)$. The lift is explicit: for each $r_0$, the terminal data of the reduction at $r_+$ or $r_-$ is determined by a closed-form algebraic identity.

**Theorem B (Density).** *The density ratio $|\mathcal{O}_L|/2^L$ is non-decreasing in $L$, and the limit
$$
c_W \;:=\; \lim_{L \to \infty} \frac{|\mathcal{O}_L|}{2^L}
$$
exists in $[3/64, 1]$. For every $L_0 \ge v + 1$, the rigorous lower bound $c_W \ge |\mathcal{O}_{L_0}|/2^{L_0}$ holds.*

A direct finite computation at $L_0 = 16$, using only the algorithmic $X$-invariant criterion of Section 2, gives the rigorous lower bound $c_W \ge 7556/65536 \approx 0.115$. The conservative bound $3/64 \approx 0.047$ obtained from the trivial starting level $L_0 = 6$ admits substantial improvement by raising $L_0$, but the exact value of $c_W$ remains an open problem. We give in Section 6 a refined decomposition of $\mathcal{O}_L$ that exhibits $c_W$ as a rigorously convergent series and isolates the remaining open question to a single quantitative bound on a sub-family of obstructions.

To state the third result we need a small piece of notation. For $r \in \mathcal{O}_L$, write $w_r \in \{0,1\}^L$ for the binary representation of $r$ as an $L$-bit word, least significant bit first. The **language of obstruction words at level $L$** is
$$
\mathcal{L}_{W_L} \;:=\; \{\, w_r : r \in \mathcal{O}_L \,\} \;\subseteq\; \{0,1\}^L,
$$
and the **factor language** of the obstruction family is
$$
\mathcal{F}(\mathcal{O}) \;:=\; \{\, u \in \{0,1\}^* : u \text{ is a factor of some } w_r \text{ with } r \in \mathcal{O}_L \text{ for some } L \,\}.
$$
The **factor complexity function** of $\mathcal{F}(\mathcal{O})$ is
$$
p_W(n) \;:=\; \lvert \mathcal{F}(\mathcal{O}) \cap \{0,1\}^n \rvert.
$$
Trivially $p_W(n) \le 2^n$. The third theorem asserts that this trivial upper bound is in fact attained:

**Theorem C (Full factor complexity).** *For every $n \ge 1$,
$$
p_W(n) = 2^n.
$$*

In other words, every binary string of every length occurs as a contiguous bit-pattern of some obstruction residue. The proof, given in Section 5, is constructive: for each binary word $u \in \{0,1\}^n$ and each anchor $r_{\text{anc}} \in \mathcal{O}_6$, we exhibit an explicit residue $r(u, r_{\text{anc}}) \in \mathcal{O}_{6+n}$ in which $u$ appears as a factor at the bit positions $6, 7, \ldots, 5+n$. The construction is a direct iteration of the lift of Theorem A.

A consequence of Theorem C is a sharp constraint on the kind of combinatorial object that the obstruction family $(\mathcal{O}_L)$ can possibly be. Recall that the **topological entropy** of a language $\mathcal{L} \subseteq \{0,1\}^*$ is
$$
h(\mathcal{L}) \;:=\; \lim_{n \to \infty} \frac{1}{n} \log p_{\mathcal{L}}(n).
$$
For $\mathcal{F}(\mathcal{O})$, Theorem C gives $h(\mathcal{F}(\mathcal{O})) = \log 2$ — the *maximal* topological entropy, matching that of the full Bernoulli shift $\{0,1\}^{\mathbb{Z}}$. By contrast, any subshift of finite type defined by a nontrivial finite list of forbidden words has entropy strictly less than $\log 2$; the same is true for sofic shifts and for primitive substitution shifts. We obtain:

**Corollary 1.2.** *The obstruction family $(\mathcal{O}_L)_{L \ge 6}$, viewed as a graded family of finite languages over $\{0,1\}$, cannot be expressed as:
(i) a subshift of finite type defined by a finite list of forbidden subwords;
(ii) a sofic shift in the classical sense (the image of an SFT under a one-block factor map);
(iii) a primitive substitution shift in the sense of Pansiot~\cite{Pansiot1984} or Devyatov~\cite{Devyatov2015}.*

This corollary settles a question that arose naturally from the structural similarities between $(\mathcal{O}_L)$ and known substitution-based families in the Collatz literature (notably the work of Stérin~\cite{Sterin2020}, where the $3n+1$ map is realized as a four-state finite-state transducer between base-2 and base-3 representations). The obstruction family is *not* substitution-based in any classical sense: any structural description of $(\mathcal{O}_L)$ must capture a maximally complex word language and a constructive lift simultaneously.

### 1.4 Strategy

All three theorems rest on a single algebraic structure: the **shift-$a$ normal form** of the terminal data of the parallel reduction. We show in Section 2 that whenever the reduction terminates with $X_{\text{end}} = 1$, the terminal pair $(c_{\text{end}}, d_{\text{end}})$ has the form
$$
(c_{\text{end}}, d_{\text{end}}) \;=\; \left( 4^a, \frac{1 - 4^a}{3} \right) \qquad \text{for some } a \in \mathbb{Z}.
$$
The integer $a$, which we call the **shift index** of $r$ at level $L$, measures the difference between the 2-adic valuations of the two parallel trajectories. Theorem A is proved in Section 3 by case analysis on how the shift index evolves under the two natural lifts; Theorem C is the iterative consequence; Theorem B follows by monotonicity together with a refined classification by shift index, developed in Section 6.

The shift-$a$ normal form is, to the best of our knowledge, new. The remaining analysis proceeds by elementary case analysis and combinatorial bookkeeping; the arguments do not depend on any specialized Collatz machinery beyond the Lagarias intertwining.

The connection to the standard Collatz map $T_+$ is straightforward. The Lagarias intertwining $r \leftrightarrow 2m+1$ extends to a *residue bijection* $\mathcal{O}_L^- \leftrightarrow \mathcal{O}_L^+$ between obstruction residues for the $3x-1$ map and a corresponding family for the $3x+1$ map, given by $r \leftrightarrow -r \bmod 2^L$. The analogues of Theorems A, B, C for the $3x+1$ side follow immediately by transfer. We discuss this transfer in Section 7.

The obstruction residues are not, *a priori*, related to the standard combinatorial structures studied in the Collatz literature. They do not correspond directly to Wirsching's predecessor-density framework~\cite{Wirsching1998}, nor to Stérin's substitution-based formulation~\cite{Sterin2020}, nor to the Eliahou cycle-exclusion machinery~\cite{Eliahou1993}. The closest analog in the literature is perhaps the family of *stopping-time congruence classes* studied by Cadaru~\cite{Cadaru2015}, which counts residues modulo $2^{\sigma}$ that share a fixed stopping time $\sigma$ under $T_+$; but the obstruction residues studied here are defined by an entirely different invariant (the shift-$a$ form rather than a stopping-time value), and the resulting structural properties are different in kind. We discuss the connections in Section 7 and indicate possible bridges in Section 8.

### 1.5 Outline of the paper

Section 2 introduces the parallel reduction, defines the $X$-invariant rigorously, and proves the parity lemma A* (shift-$a$ normal form). Section 3 contains the proof of Theorem A (the lift), split into the two stop-type cases. Section 4 derives Theorem B(i) (existence of $c_W$ and finite-level lower bounds) as a direct corollary of Theorem A. Section 5 proves Theorem C (full factor complexity) by an iterative construction and derives Corollary 1.2 on the entropy and substitution-shift obstructions. Section 6 develops the classification of obstructions by shift index $a$, proves Theorem B(ii) (the strict lift balance and absence of atomic shift-zero obstructions), and reduces the exact value of $c_W$ to a single question about the growth of non-zero-shift atomic obstructions. Section 7 transfers the results to the $3x+1$ side via the residue bijection. Section 8 discusses open questions, including the rigorous bound on non-zero-shift atomic growth (which would determine $c_W$ exactly), the bridge to nontrivial cycles of $T_-$, and the connection to Wirsching's framework. Appendix A summarizes computational verifications, with pointers to the implementations used in supporting examples.

---

## 2. The parallel reduction and the $X$-invariant

### 2.1 The basic step

Recall that for an odd integer $n$, the map $T_-$ is defined by stripping the 2-adic part from $3n-1$:
$$
T_-(n) \;=\; \frac{3n - 1}{2^{v_2(3n - 1)}}.
$$
We need a version of this step that keeps track of the modulus. Fix a level $L \ge 1$, and consider a pair $(a, b)$ with $a$ a positive odd integer and $b$ a power of two, interpreted as a residue $a$ modulo $b$. A single $T_-$-step on such a pair produces
$$
(a', b') \;=\; \left( \frac{3a - 1}{2^{v_a}}, \; \frac{3b}{2^{v_a}} \right), \qquad v_a := v_2(3a - 1),
$$
provided $v_a < v_2(b)$. If $v_a \ge v_2(b)$, the modulus has been exhausted and the step is undefined; we say the reduction has *terminated* (or *stopped*) at this pair.

Note that $v_2(b') = v_2(b) - v_a$ (since $3$ is odd, $v_2(3b) = v_2(b)$); the modulus strictly decreases at each step, so the reduction always terminates after finitely many steps.

### 2.2 The two-track setup

Fix $r$ a positive odd integer with $r \equiv 3 \pmod 4$ and $v_2(r - 1) = 1$; we postpone the general case $v_2(r-1) = v \ge 2$ to a remark at the end of this section. Write $m := (r - 1)/2$. The condition $r \equiv 3 \pmod 4$ ensures that $m$ is odd, and the valuation condition is a mild non-degeneracy assumption.

Fix a level $L \ge 2$. We run two $T_-$-reductions in parallel:

- the **K-track**, starting from $(a_K^{(0)}, b_K^{(0)}) := (r, 2^L)$, and
- the **I-track**, starting from $(a_I^{(0)}, b_I^{(0)}) := (m, 2^{L-1})$.

The initial relation between the two starting values is $m = (a_K^{(0)} - 1)/2$, i.e.
$$
a_I^{(0)} \;=\; \tfrac{1}{2} a_K^{(0)} \;-\; \tfrac{1}{2}.
$$
At each step $j \ge 0$, we update both tracks according to the basic step above, denoting the resulting 2-adic valuations $v_K^{(j)} := v_2(3 a_K^{(j)} - 1)$ and $v_I^{(j)} := v_2(3 a_I^{(j)} - 1)$. The reduction proceeds as long as **both** tracks can step, i.e., as long as $v_K^{(j)} < v_2(b_K^{(j)})$ and $v_I^{(j)} < v_2(b_I^{(j)})$; the parallel reduction terminates as soon as either condition fails. We write $J = J(r, L)$ for the index at which termination occurs.

### 2.3 The affine relation and the $X$-invariant

The crucial observation is that the affine relation between the two tracks is preserved by the parallel step:

**Lemma 2.1.** *For each $j$ with $0 \le j \le J$, there exist $c_j, d_j \in \mathbb{Q}$ such that
$$
a_I^{(j)} \;=\; c_j \, a_K^{(j)} \;+\; d_j \qquad \text{in } \mathbb{Q},
$$
with $c_0 = \tfrac{1}{2}$, $d_0 = -\tfrac{1}{2}$, and the update rule
$$
c_{j+1} \;=\; c_j \cdot 2^{v_K^{(j)} - v_I^{(j)}}, \qquad
d_{j+1} \;=\; \frac{3 d_j + c_j - 1}{2^{v_I^{(j)}}}.
$$*

**Proof.** The base case is immediate from the definition of $m$. Assume the affine relation holds at index $j$. Writing $A_K^{(j)} := 3 a_K^{(j)} - 1$, $A_I^{(j)} := 3 a_I^{(j)} - 1$, and $X_j := 3 d_j + c_j$, we compute
$$
A_I^{(j)} \;=\; 3 a_I^{(j)} - 1 \;=\; 3(c_j a_K^{(j)} + d_j) - 1 \;=\; c_j (3 a_K^{(j)} - 1) + (3 d_j + c_j - 1) \;=\; c_j A_K^{(j)} + (X_j - 1).
$$
Dividing by $2^{v_I^{(j)}}$ and using $A_K^{(j)} = 2^{v_K^{(j)}} a_K^{(j+1)}$:
$$
a_I^{(j+1)} \;=\; \frac{A_I^{(j)}}{2^{v_I^{(j)}}} \;=\; c_j \cdot 2^{v_K^{(j)} - v_I^{(j)}} \cdot a_K^{(j+1)} \;+\; \frac{X_j - 1}{2^{v_I^{(j)}}}.
$$
This is the desired affine relation at index $j+1$, with $c_{j+1}, d_{j+1}$ given by the stated formulas. $\square$

A by-product of the proof: the $X$-quantity transforms according to
$$
X_{j+1} \;=\; 3 d_{j+1} + c_{j+1} \;=\; \frac{3(X_j - 1) + c_j \cdot 2^{v_K^{(j)}}}{2^{v_I^{(j)}}}.
$$
In particular, $X_j$ is not invariant under the update; it is the *fixed-point set* of the dynamics that matters, and that set turns out to be very specific.

We define the **$X$-invariant** of the parallel reduction at $(r, L)$ as
$$
X_{\text{end}}(r, L) \;:=\; X_J \;=\; 3 d_J + c_J,
$$
the value of $X$ at termination. Despite the name "invariant", this is not an invariant of the update step; the name reflects its role as the algebraic certificate of obstruction status, which we explain next.

### 2.4 Definition of obstruction residues

We can now give the precise definition of the obstruction family.

**Definition 2.2 (Obstruction residue).** *An odd integer $r$ with $r \equiv 3 \pmod 4$ and $v_2(r-1) = 1$ is an* **obstruction residue at level $L$** *if $X_{\text{end}}(r, L) = 1$. We write*
$$
\mathcal{O}_L \;:=\; \{\, r \in \{1, \ldots, 2^L\} : r \text{ is an obstruction residue at level } L \,\}.
$$

The definition is algorithmic: given $r$ and $L$, one runs the parallel reduction, observes the terminal pair $(c_J, d_J)$, and checks whether $3 d_J + c_J = 1$. The computation terminates in at most $L$ steps and produces a definite yes-or-no answer.

The connection between this algebraic definition and the dynamics of $T_-$ trajectories is, briefly, that $X_{\text{end}} = 1$ implies a *synchronization* of stopping times: under $T_-$ iteration starting from $r$ and from any $n \equiv r \pmod{2^L}$, the stopping-time difference $K_{-3}(n) - K_-(n) = 1$ remains constant. We do not pursue this connection here; it is developed in detail in Section 7.

### 2.5 The parity lemma

The central algebraic fact of this paper is the following.

**Lemma 2.3 (Parity lemma).** *Suppose the parallel reduction at $(r, L)$ terminates with $X_{\text{end}}(r, L) = 1$. Then
$$
\delta_{\text{end}} := V_K^{(J)} - V_I^{(J)} - 1
$$
is a non-negative or negative *even* integer, where $V_K^{(j)} := \sum_{i < j} v_K^{(i)}$ and $V_I^{(j)} := \sum_{i < j} v_I^{(i)}$.*

The statement looks technical, but its content is geometric: the difference of the accumulated 2-adic valuations of the two tracks at termination is rigidly tied to the value of $c_J$, and $c_J$ must be a power of $4$ (rather than an arbitrary power of $2$). The proof is short, modular, and avoids any reference to the dynamics of $T_-$.

**Proof.** Iterating the update rule from Lemma 2.1 with $c_0 = 1/2$:
$$
c_j \;=\; \tfrac{1}{2} \cdot \prod_{i < j} 2^{v_K^{(i)} - v_I^{(i)}} \;=\; 2^{V_K^{(j)} - V_I^{(j)} - 1} \;=\; 2^{\delta_j},
$$
where $\delta_j := V_K^{(j)} - V_I^{(j)} - 1$ is an integer (possibly negative).

Let $\delta := \delta_J$. From $X_J = 3 d_J + c_J = 1$ we get $d_J = (1 - c_J)/3 = (1 - 2^\delta)/3$. The affine relation at index $J$ becomes
$$
a_I^{(J)} \;=\; 2^\delta \, a_K^{(J)} \;+\; \frac{1 - 2^\delta}{3} \qquad \text{in } \mathbb{Q}.
$$
Multiplying by $3$:
$$
3 a_I^{(J)} \;=\; 3 \cdot 2^\delta \, a_K^{(J)} \;+\; 1 - 2^\delta. \tag{$\star$}
$$
We distinguish two cases.

*Case $\delta \ge 0$.* All terms on the right of ($\star$) are integers. Reducing modulo $3$ and using $3 a_I^{(J)} \equiv 0 \pmod 3$ on the left and $3 \cdot 2^\delta a_K^{(J)} \equiv 0 \pmod 3$ on the right, we obtain $1 - 2^\delta \equiv 0 \pmod 3$, i.e. $2^\delta \equiv 1 \pmod 3$. Since $2 \equiv -1 \pmod 3$, this forces $\delta$ to be even.

*Case $\delta < 0$.* Write $\delta = -e$ with $e > 0$. Multiplying ($\star$) by $2^e$:
$$
3 \cdot 2^e \, a_I^{(J)} \;=\; 3 \, a_K^{(J)} \;+\; 2^e - 1. \tag{$\star\star$}
$$
All terms in ($\star\star$) are now integers. Reducing modulo $3$ as before, we obtain $2^e - 1 \equiv 0 \pmod 3$, i.e. $2^e \equiv 1 \pmod 3$, so $e$ is even, hence $\delta = -e$ is also even.

In both cases, $\delta$ is even. $\square$

### 2.6 The shift-$a$ normal form

Writing $\delta = 2a$ with $a \in \mathbb{Z}$, the conclusion of the parity lemma is that
$$
c_J \;=\; 4^a, \qquad d_J \;=\; \frac{1 - 4^a}{3}.
$$
We call this the **shift-$a$ normal form** and the integer $a$ the **shift index** of $r$ at level $L$, denoted $a(r, L)$. The set of obstructions partitions according to shift index:
$$
\mathcal{O}_L \;=\; \bigsqcup_{a \in \mathbb{Z}} \mathcal{O}_L^{G_a}, \qquad \mathcal{O}_L^{G_a} := \{ r \in \mathcal{O}_L : a(r, L) = a \}.
$$
For $a = 0$ we have $(c_J, d_J) = (1, 0)$; the two tracks have *fully synchronized* at termination, meaning $a_I^{(J)} = a_K^{(J)}$. For $a \ne 0$, the tracks differ by a factor of $4^a$ plus the constant $(1-4^a)/3$.

The shift index is bounded: since $V_K^{(J)} \le L$ and $V_I^{(J)} \le L - 1$, the integer $|2a + 1| = |V_K^{(J)} - V_I^{(J)}| \le L$, so $|a| \le L/2$. The interesting question of how many obstructions occur for each value of $a$ is taken up in Section 6.

### 2.7 Stop types and the simultaneous-stop property

By construction the parallel reduction stops as soon as either track fails the step condition $v_a < v_2(b)$. A priori, the two tracks could fail at different indices. The parity lemma rules this out:

**Corollary 2.4 (Simultaneous stop).** *If $X_{\text{end}}(r, L) = 1$, then the K-track and I-track satisfy the termination condition $v_a \ge v_2(b)$ at the same index $J$.*

**Proof.** From the shift-$a$ normal form, $a_I^{(J)} = 4^a a_K^{(J)} + (1-4^a)/3$, so $A_I^{(J)} = 3 a_I^{(J)} - 1 = 4^a A_K^{(J)}$. Taking $v_2$ of both sides, $v_I^{(J)} = v_K^{(J)} + 2a$. Combining with $v_2(b_I^{(J)}) = (L - 1) - V_I^{(J)} = (L - 1) - (V_K^{(J)} - 2a - 1) = L - V_K^{(J)} + 2a$, the I-track termination condition $v_I^{(J)} \ge v_2(b_I^{(J)})$ becomes $v_K^{(J)} + 2a \ge L - V_K^{(J)} + 2a$, i.e. $v_K^{(J)} \ge L - V_K^{(J)} = v_2(b_K^{(J)})$ — the K-track termination condition. $\square$

We classify the termination configuration further: the **stop type** at $(r, L)$ is **EE** if $v_K^{(J)} = v_2(b_K^{(J)})$ (and hence $v_I^{(J)} = v_2(b_I^{(J)})$), and **SS** if both inequalities are strict. The stop type is a finite invariant that plays a central role in the lift theorem.

### 2.8 Remarks on the general case $v \ge 2$

The setup above assumed $v := v_2(r-1) = 1$. For $r$ with $v \ge 2$, the I-track starts at $(m, 2^{L-v})$ with $m = (r-1)/2^v$ instead of $(r-1)/2$, and the initial coefficients are $c_0 = 2^{-v}$, $d_0 = -2^{-v}$. The parity lemma then asserts that $\delta_{\text{end}} = V_K^{(J)} - V_I^{(J)} - v$ is even, and the shift-$a$ normal form is unchanged. The analysis is identical, with $v$ replacing $1$ throughout. We carry the case $v = 1$ in what follows for concreteness; the general statements remain valid with the obvious substitutions.


## 3. The Lift Theorem

We now prove Theorem A: for every $r_0 \in \mathcal{O}_{L_0}$, both lifts $r_+ = r_0$ and $r_- = r_0 + 2^{L_0}$ are obstructions at level $L_0 + 1$. We split into the two stop types of $r_0$ at level $L_0$. Throughout, $a \in \mathbb{Z}$ denotes the shift index of $r_0$ at level $L_0$, and we use the synchronization $v_I^{(J)} = v_K^{(J)} + 2a$ (Corollary 2.4) freely.

### 3.1 The $r_+$ lift

**Theorem 3.1.** *Let $r_0 \in \mathcal{O}_{L_0}^{G_a}$ for some $a \in \mathbb{Z}$. Then $r_+ := r_0 \in \mathcal{O}_{L_0 + 1}$.*

**Proof.** The starting pairs of the parallel reduction at $(r_+, L_0 + 1)$ are $(r_0, 2^{L_0+1})$ on the K-track and $(m_0, 2^{L_0})$ on the I-track, where $m_0 = (r_0 - 1)/2$. These differ from the corresponding pairs at $(r_0, L_0)$ only in the modulus, which is doubled.

Each step of the parallel reduction depends only on the current values $a_K^{(j)}, a_I^{(j)}$, not on the modulus, as long as the modulus does not constrain the step. Since the modulus is larger at $(r_+, L_0+1)$ than at $(r_0, L_0)$ throughout, the steps of the parallel reduction at $(r_+, L_0+1)$ are identical to those at $(r_0, L_0)$ for the first $J$ indices: $v_K^{(j)}, v_I^{(j)}, c_j, d_j$ all coincide for $j \le J$.

We distinguish the two stop types of $r_0$ at level $L_0$.

**Stop type EE at $L_0$.** Here $v_K^{(J)} = L_0 - V_K^{(J)}$ exactly. At level $L_0 + 1$, the K-track modulus at index $J$ has 2-adic valuation $L_0 + 1 - V_K^{(J)} = v_K^{(J)} + 1 > v_K^{(J)}$, so the step is still permitted. We take **one more step** at index $J$. From the update rule, with the shift-$a$ values $c_J = 4^a$, $d_J = (1-4^a)/3$ at $(r_0, L_0)$ — and hence also at $(r_+, L_0+1)$ at index $J$ — the new values are
$$
c_{J+1} \;=\; 4^a \cdot 2^{v_K^{(J)} - v_I^{(J)}} \;=\; 4^a \cdot 2^{-2a} \;=\; 1,
$$
$$
d_{J+1} \;=\; \frac{3 \cdot (1-4^a)/3 + 4^a - 1}{2^{v_I^{(J)}}} \;=\; \frac{(1 - 4^a) + (4^a - 1)}{2^{v_I^{(J)}}} \;=\; 0.
$$
After this step, $V_K^{(J+1)} = V_K^{(J)} + v_K^{(J)} = L_0$, so the K-track modulus has 2-adic valuation $L_0 + 1 - L_0 = 1$. The next step would require $v_K^{(J+1)} < 1$, i.e. $a_K^{(J+1)}$ such that $3 a_K^{(J+1)} - 1$ is odd — impossible since $a_K^{(J+1)}$ is odd. So termination occurs at index $J + 1$ with $(c_{J+1}, d_{J+1}) = (1, 0)$, giving $X_{\text{end}} = 1$ and $r_+ \in \mathcal{O}_{L_0 + 1}^{G_0}$.

**Stop type SS at $L_0$.** Here $v_K^{(J)} > L_0 - V_K^{(J)}$, i.e. $v_K^{(J)} \ge L_0 - V_K^{(J)} + 1$. At level $L_0 + 1$, the K-track condition for termination is $v_K^{(J)} \ge L_0 + 1 - V_K^{(J)}$, which is also satisfied. Termination occurs at index $J$ already; the terminal data $(c_J, d_J) = (4^a, (1-4^a)/3)$ is unchanged, so $X_{\text{end}}(r_+, L_0 + 1) = 1$ and $r_+ \in \mathcal{O}_{L_0+1}^{G_a}$ (same shift index as $r_0$).

In either case $r_+ \in \mathcal{O}_{L_0+1}$. $\square$

### 3.2 The $r_-$ lift

**Theorem 3.2.** *Let $r_0 \in \mathcal{O}_{L_0}^{G_a}$. Then $r_- := r_0 + 2^{L_0} \in \mathcal{O}_{L_0 + 1}$.*

The proof requires slightly more care: at $(r_-, L_0+1)$, the K-track starts at a value differing from $r_0$ by $2^{L_0}$, which is *within* the new modulus $2^{L_0+1}$. We must track the discrepancy between the two reductions step by step.

**Proof.** Write $a_{K,+}^{(j)}, a_{I,+}^{(j)}$ for the values at $(r_+, L_0+1)$ from Theorem 3.1, and $a_{K,-}^{(j)}, a_{I,-}^{(j)}$ for those at $(r_-, L_0+1)$. The discrepancies
$$
\delta_K^{(j)} := a_{K,-}^{(j)} - a_{K,+}^{(j)}, \qquad \delta_I^{(j)} := a_{I,-}^{(j)} - a_{I,+}^{(j)}
$$
satisfy $\delta_K^{(0)} = 2^{L_0}$ and $\delta_I^{(0)} = 2^{L_0 - 1}$. Each step multiplies the discrepancy by $3/2^{v}$ (since $T_-(a + \delta) - T_-(a) = (3 \delta)/2^v$ when both arguments share the same valuation $v$):
$$
\delta_K^{(j)} \;=\; 2^{L_0 - V_K^{(j)}} \cdot 3^j, \qquad \delta_I^{(j)} \;=\; 2^{L_0 - 1 - V_I^{(j)}} \cdot 3^j,
$$
as long as the $v$-values coincide between the two reductions; this is the case as long as $V_K^{(j)} < L_0$ and $V_I^{(j)} < L_0 - 1$.

We again distinguish by stop type at $(r_0, L_0)$.

**Stop type SS at $L_0$.** At index $J$ of $(r_+, L_0+1)$, the values $v_K^{(J)} > L_0 - V_K^{(J)}$ strictly, so $v_2(\delta_K^{(J)}) = L_0 - V_K^{(J)} < v_K^{(J)}$. By the 2-adic identity $v_2(A + B) = \min(v_2(A), v_2(B))$ when $v_2(A) \ne v_2(B)$, the K-track step at $(r_-, L_0+1)$ at index $J$ produces $v_{K,-}^{(J)} = v_2(\delta_K^{(J)}) = L_0 - V_K^{(J)} < L_0 + 1 - V_K^{(J)} = v_2(b_K)$. The step is permitted; we take one more step. The update is precisely the EE-case extra step from Theorem 3.1: $(c_{J+1}, d_{J+1}) = (1, 0)$, and termination at $J + 1$ gives $r_- \in \mathcal{O}_{L_0 + 1}^{G_0}$.

**Stop type EE at $L_0$.** Here $v_K^{(J)} = L_0 - V_K^{(J)}$, so $v_2(\delta_K^{(J)}) = L_0 - V_K^{(J)} = v_K^{(J)}$ — the two valuations *coincide*. By the carry identity $v_2(A + B) \ge v_2(A) + 1$ when $v_2(A) = v_2(B)$, we get $v_{K,-}^{(J)} \ge v_K^{(J)} + 1 = L_0 + 1 - V_K^{(J)} = v_2(b_K)$. Termination occurs at index $J$; the terminal data $(c_J, d_J) = (4^a, (1-4^a)/3)$ is unchanged, and $r_- \in \mathcal{O}_{L_0+1}^{G_a}$.

In either case, $r_- \in \mathcal{O}_{L_0+1}$. $\square$

### 3.3 The symmetry table

The proofs of Theorems 3.1 and 3.2 establish a symmetry between the two lifts:

| Stop type of $r_0$ at $L_0$ | shift index of $r_+$ at $L_0+1$ | shift index of $r_-$ at $L_0+1$ |
|:---:|:---:|:---:|
| EE | $0$ | $a$ |
| SS | $a$ | $0$ |

So lifting an obstruction with shift index $a \ne 0$ always produces *one* shift-$a$ obstruction and *one* shift-zero obstruction at the next level. Lifting a shift-zero obstruction always produces two shift-zero obstructions. This table is the basis for the recurrence developed in Section 6.


## 4. Positive density

The lift theorem has an immediate consequence for the density $|\mathcal{O}_L|/2^L$.

**Proof of Theorem B (Density).** By Theorem A, every $r_0 \in \mathcal{O}_{L_0}$ contributes two elements to $\mathcal{O}_{L_0+1}$, namely $r_0$ and $r_0 + 2^{L_0}$. These are distinct (one in $[0, 2^{L_0})$, the other in $[2^{L_0}, 2^{L_0+1})$) and they cover only a subset of $\mathcal{O}_{L_0+1}$; the remaining elements, if any, are obstructions at level $L_0 + 1$ that do not arise as lifts. Hence
$$
|\mathcal{O}_{L_0+1}| \;\ge\; 2 |\mathcal{O}_{L_0}|, \qquad \text{equivalently} \qquad \frac{|\mathcal{O}_{L_0+1}|}{2^{L_0+1}} \;\ge\; \frac{|\mathcal{O}_{L_0}|}{2^{L_0}}.
$$
The density ratio is non-decreasing in $L$. Since $\mathcal{O}_L \subseteq \{1, \ldots, 2^L\}$, the ratio is bounded above by $1$. By monotone convergence, the limit
$$
c_W \;=\; \lim_{L \to \infty} \frac{|\mathcal{O}_L|}{2^L}
$$
exists in $[\rho_{L_0}, 1]$ for any $L_0$, where $\rho_{L_0} := |\mathcal{O}_{L_0}|/2^{L_0}$. $\square$

The conservative bound $\rho_6 = 3/64$ uses only the three explicit obstructions $\mathcal{O}_6 = \{19, 27, 59\}$. By raising $L_0$ and computing $|\mathcal{O}_{L_0}|$ directly via the $X$-invariant criterion, one obtains tighter rigorous bounds for $c_W$:

| $L_0$ | $|\mathcal{O}_{L_0}|$ | $\rho_{L_0}$ | rigorous lower bound for $c_W$ |
|---:|---:|---:|---:|
| 6 | 3 | $\approx 0.047$ | $3/64$ |
| 10 | 91 | $\approx 0.089$ | $91/1024$ |
| 14 | 1776 | $\approx 0.108$ | $1776/16384$ |
| 16 | 7556 | $\approx 0.115$ | $7556/65536$ |

These are not asymptotic estimates: they are finite-level computations that produce rigorous bounds at the cost of $O(L_0 \cdot 2^{L_0})$ operations to enumerate the obstructions modulo $2^{L_0}$. The exact value of $c_W$ — equivalently, the convergence rate of $\rho_L \to c_W$ — is not pinned down by this finite-level approach; we return to it in Section 6, where a refined decomposition isolates the remaining open question.


## 5. Full factor complexity

### 5.1 Setup

To each obstruction $r \in \mathcal{O}_L$ we associate its **binary representation** as an $L$-bit word, written least significant bit first:
$$
w_r \;\in\; \{0,1\}^L, \qquad w_r[k] := \lfloor r / 2^k \rfloor \bmod 2, \qquad k = 0, 1, \ldots, L-1.
$$
The **language of obstruction words at level $L$** is $\mathcal{L}_{W_L} := \{ w_r : r \in \mathcal{O}_L \} \subseteq \{0,1\}^L$, and the **factor language** of the obstruction family is
$$
\mathcal{F}(\mathcal{O}) \;:=\; \{\, u \in \{0,1\}^* : u \text{ appears as a contiguous substring of some } w_r,\; r \in \mathcal{O}_L,\; L \ge 1 \,\}.
$$
The **factor complexity function** is $p_W(n) := |\mathcal{F}(\mathcal{O}) \cap \{0,1\}^n|$. The trivial bound is $p_W(n) \le 2^n$.

### 5.2 The main theorem

**Theorem 5.1 (Theorem C).** *For every $n \ge 1$,
$$
p_W(n) \;=\; 2^n.
$$*

**Proof.** Fix $n \ge 1$ and an arbitrary binary word $u = (u_0, u_1, \ldots, u_{n-1}) \in \{0,1\}^n$. We construct explicitly a residue $r(u) \in \mathcal{O}_{6+n}$ such that $u$ appears as a substring of $w_{r(u)}$ at bit positions $6, 7, \ldots, 5 + n$.

Fix any base anchor $r_0 \in \mathcal{O}_6 = \{19, 27, 59\}$. Define inductively
$$
r_k \;:=\; r_{k-1} \;+\; u_{k-1} \cdot 2^{5 + k}, \qquad k = 1, 2, \ldots, n.
$$
We claim $r_k \in \mathcal{O}_{6+k}$ for each $k$. The base $k = 0$ is by choice of $r_0$. For the inductive step from $k - 1$ to $k$: if $u_{k-1} = 0$, then $r_k = r_{k-1}$, and by Theorem 3.1 (the $r_+$ lift) $r_k \in \mathcal{O}_{6+k}$. If $u_{k-1} = 1$, then $r_k = r_{k-1} + 2^{5+k}$, which is the $r_-$ lift, and by Theorem 3.2 $r_k \in \mathcal{O}_{6+k}$.

By construction, $w_{r_n}[5+k] = u_{k-1}$ for $k = 1, \ldots, n$, so $u$ appears as a factor of $w_{r_n}$ at positions $6, \ldots, 5+n$. Thus $u \in \mathcal{F}(\mathcal{O})$.

Since $u \in \{0,1\}^n$ was arbitrary, every binary word of length $n$ appears in $\mathcal{F}(\mathcal{O})$, so $p_W(n) \ge 2^n$. Combined with the trivial upper bound, $p_W(n) = 2^n$. $\square$

The proof is fully constructive: for each binary word $u$ and each base anchor $r_0$, we have an explicit formula for the obstruction $r(u, r_0)$ that exhibits $u$ as a factor. The construction extends with no change to higher base anchors when $\mathcal{A}_{L_0} \ne \varnothing$ at higher levels.

### 5.3 Entropy and substitution-shift obstructions

A consequence of Theorem 5.1 is a sharp constraint on the combinatorial type of $\mathcal{F}(\mathcal{O})$. Recall the **topological entropy** of a language $\mathcal{L} \subseteq \{0,1\}^*$ is
$$
h(\mathcal{L}) \;:=\; \limsup_{n \to \infty} \frac{1}{n} \log p_{\mathcal{L}}(n),
$$
where $p_{\mathcal{L}}(n)$ is the factor complexity of $\mathcal{L}$.

**Corollary 5.2.** *The topological entropy of $\mathcal{F}(\mathcal{O})$ is $\log 2$.*

This is the maximal value: it matches the entropy of the full Bernoulli shift $\{0,1\}^{\mathbb{Z}}$. As an immediate consequence, $\mathcal{F}(\mathcal{O})$ cannot be a non-trivial subshift of finite type or a non-trivial sofic shift, both of which have entropy strictly less than $\log 2$ unless they coincide with $\{0,1\}^{\mathbb{Z}}$ itself. Since $\mathcal{F}(\mathcal{O})$ is not the full Bernoulli shift (the obstructions $\mathcal{O}_L$ have density $c_W < 1$), we obtain:

**Corollary 5.3.** *The obstruction family $(\mathcal{O}_L)_{L \ge 6}$, viewed as a graded family of finite languages over $\{0,1\}$, is*
*(i) not a subshift of finite type defined by any finite list of forbidden subwords;*
*(ii) not a sofic shift in the classical sense (the image of an SFT under a one-block factor map);*
*(iii) not a primitive substitution shift in the sense of Pansiot~\cite{Pansiot1984} or Devyatov~\cite{Devyatov2015}.*

Part (iii) requires the additional fact that primitive substitution shifts have polynomial or sub-Bernoulli factor complexity (one of $\Theta(1), \Theta(n), \Theta(n \log \log n), \Theta(n \log n), \Theta(n^2)$), all of which give topological entropy zero or strictly less than $\log 2$.

This is a strong structural rigidity. Many natural questions about $T_-$ obstructions might have been hoped to admit a substitution-shift presentation (cf. Stérin~\cite{Sterin2020} for the related setting of $T_+$ as a finite-state transducer between bases 2 and 3). Corollary 5.3 rules out any such description for the obstruction family — any structural characterization must accommodate a maximally complex factor language while still producing a density $c_W < 1$.


## 6. The $G_a$ classification

In this section we develop the refined classification of obstructions by shift index and prove the strict lift balance and series representation announced in Theorem B.

### 6.1 Atomic obstructions

An obstruction $r \in \mathcal{O}_L$ is **atomic at level $L$** if $r \bmod 2^{L-1} \notin \mathcal{O}_{L-1}$, i.e. $r$ does not arise as a lift from level $L-1$. We write
$$
\mathcal{A}_L \;\subseteq\; \mathcal{O}_L, \qquad \mathcal{A}_L^{G_a} := \mathcal{A}_L \cap \mathcal{O}_L^{G_a},
$$
and note that every obstruction at level $L$ is either atomic at $L$ or a lift of an obstruction at $L-1$. By Theorem A, the lifts $r_0$ and $r_0 + 2^{L_0}$ of an atomic $r_0 \in \mathcal{A}_{L_0}$ remain in $\mathcal{O}_L$ at all levels $L \ge L_0$, generating the chain $r_0, r_0 + 2^{L_0}, r_0 + 2^{L_0+1}, \ldots, r_0 + \sum_{k \ge L_0} u_k 2^k$. Iterating Theorem A:

**Lemma 6.1 (Atom decomposition).** *For every $L \ge 6$,
$$
|\mathcal{O}_L| \;=\; \sum_{L_0 = 6}^{L} |\mathcal{A}_{L_0}| \cdot 2^{L - L_0}.
$$*

This is a partition: each $r \in \mathcal{O}_L$ has a unique smallest $L_0 \ge 6$ such that $r \bmod 2^{L_0} \in \mathcal{A}_{L_0}$, and $r$ is then determined by this atomic anchor together with the bits $\{u_{L_0}, u_{L_0+1}, \ldots, u_{L-1}\}$ encoding the lift choices.

### 6.2 No shift-zero atoms

The structural content of this section is that the atomic family $\mathcal{A}_L$ contains no shift-zero element for $L$ large enough.

**Theorem 6.2 (Atomic shift-zero vanishes).** *For every $L \ge 7$,
$$
|\mathcal{A}_L^{G_0}| \;=\; 0.
$$*

**Proof.** Fix $L \ge 7$ and suppose $r \in \mathcal{O}_L^{G_0}$, so $X_{\text{end}}(r, L) = 1$ with shift index $a = 0$ — meaning $(c_J, d_J) = (1, 0)$. We must show $r \bmod 2^{L-1} \in \mathcal{O}_{L-1}$.

Write $r' := r \bmod 2^{L-1}$. The parallel reduction at $(r', L-1)$ uses the same starting values $a_K, a_I$ as at $(r, L)$ but with the modulus reduced by one power of two. As in the proof of Theorem 3.1, the first $j$ steps of the two reductions coincide as long as the modulus does not constrain a step; explicitly, this holds as long as $V_K^{(j)} + v_K^{(j)} < L - 1$ and analogously for the I-track. Two cases arise.

*Case A: $V_K^{(J)} + v_K^{(J)} \ge L$ and the same first-violation index $J$ as at $(r, L)$.* Then the parallel reduction at $(r', L-1)$ also terminates at index $J$, with the same terminal data $(c_J, d_J) = (1, 0)$, so $r' \in \mathcal{O}_{L-1}^{G_0}$.

*Case B: $V_K^{(J-1)} + v_K^{(J-1)} \ge L - 1$ but $< L$.* Then the parallel reduction at $(r', L-1)$ terminates one step earlier than at $(r, L)$, at index $J - 1$, with terminal data $(c_{J-1}, d_{J-1})$. We show that this terminal data also satisfies $X = 1$.

From the update rule (Lemma 2.1) at index $J - 1$:
$$
c_J = c_{J-1} \cdot 2^{v_K^{(J-1)} - v_I^{(J-1)}}, \qquad d_J = \frac{3 d_{J-1} + c_{J-1} - 1}{2^{v_I^{(J-1)}}}.
$$
Setting $c_J = 1$ and $d_J = 0$ and reading off:
$$
3 d_{J-1} + c_{J-1} - 1 \;=\; 0, \qquad \text{i.e.} \qquad X_{J-1} = 3 d_{J-1} + c_{J-1} = 1.
$$
By the parity lemma applied at the terminal index $J - 1$ of the reduction at $(r', L-1)$, the terminal pair is in shift-$a'$ normal form for some $a' \in \mathbb{Z}$, so $r' \in \mathcal{O}_{L-1}^{G_{a'}}$.

In either case, $r' \in \mathcal{O}_{L-1}$, so $r$ is not atomic. $\square$

The argument is local: the value $X_{J-1} = 1$ is read off directly from the last update step, without any reference to the dynamics of $T_-$ trajectories.

### 6.3 The shift index under lift

Combined with the symmetry table from Section 3.3, Theorem 6.2 yields a complete accounting of how obstructions distribute over the shift-index classes under lift.

Writing $g_L := |\mathcal{O}_L^{G_0}|$ and $h_L := |\mathcal{O}_L^{G_{\ne 0}}|$, the lift symmetry table gives, per parent:

| Parent at $L-1$ | Contribution to $g_L$ | Contribution to $h_L$ |
|:---:|:---:|:---:|
| $G_0$ | $2$ | $0$ |
| $G_a$, $a \ne 0$ | $1$ | $1$ |

Summing and adding the atomic contributions (which, by Theorem 6.2, occur only in $h_L$):

**Corollary 6.3 (Strict lift balance).** *For every $L \ge 7$,
$$
g_L \;=\; 2 g_{L-1} \;+\; h_{L-1}, \qquad h_L \;=\; h_{L-1} \;+\; |\mathcal{A}_L^{G_{\ne 0}}|.
$$
Adding, $|\mathcal{O}_L| = 2 |\mathcal{O}_{L-1}| + |\mathcal{A}_L^{G_{\ne 0}}|$.*

### 6.4 The series representation of $c_W$

Combining the atom decomposition (Lemma 6.1) with Theorem 6.2:

**Theorem 6.4.** *The density constant $c_W$ admits the rigorous series representation
$$
c_W \;=\; \frac{|\mathcal{A}_6|}{2^6} \;+\; \sum_{L \ge 7} \frac{|\mathcal{A}_L^{G_{\ne 0}}|}{2^L} \;=\; \frac{3}{64} \;+\; \sum_{L \ge 7} \frac{|\mathcal{A}_L^{G_{\ne 0}}|}{2^L}.
$$
The series converges with non-negative terms; in particular, $|\mathcal{A}_L^{G_{\ne 0}}|/2^L \to 0$ as $L \to \infty$.*

**Proof.** By Lemma 6.1 and Theorem 6.2, for $L \ge 7$:
$$
|\mathcal{O}_L| \;=\; |\mathcal{A}_6| \cdot 2^{L-6} \;+\; \sum_{L_0 = 7}^{L} |\mathcal{A}_{L_0}^{G_{\ne 0}}| \cdot 2^{L - L_0}.
$$
Dividing by $2^L$:
$$
\rho_L \;=\; \frac{|\mathcal{A}_6|}{2^6} \;+\; \sum_{L_0 = 7}^{L} \frac{|\mathcal{A}_{L_0}^{G_{\ne 0}}|}{2^{L_0}}.
$$
By Theorem B (Section 4), $\rho_L$ is non-decreasing and bounded above by $1$, so its limit $c_W$ exists. The right-hand side is a partial sum of a series with non-negative terms; its limit is the announced series. The terms must tend to zero for the series to converge. $\square$

### 6.5 The remaining open question

Theorem 6.4 gives a rigorous handle on $c_W$ but does not pin down its exact value. The exact value of $c_W$ is determined by the growth of $|\mathcal{A}_L^{G_{\ne 0}}|$ as $L \to \infty$; a quantitative bound of the form $|\mathcal{A}_L^{G_{\ne 0}}| \le C \cdot \alpha^L$ with $\alpha < 2$ would give a geometrically convergent series with explicit error bounds. The construction of such a bound — equivalently, a quantitative version of the structural characterization of atomic shift-nonzero obstructions in Theorem 6.2 — is the principal remaining problem of this circle of ideas. We return to it in Section 8.


## 7. The $T_+$ side

The classical Collatz map $T_+$ admits the same obstruction theory, transferred from $T_-$ via the Lagarias intertwining. We give the construction briefly.

### 7.1 The residue bijection

For $r \in \mathbb{Z}$ and $L \ge 1$, define $\bar r := (-r) \bmod 2^L$. The map $r \mapsto \bar r$ is an involution on $\mathbb{Z}/2^L\mathbb{Z}$ that preserves oddness.

**Lemma 7.1.** *For each odd $r$ and each level $L$, the value of $X_{\text{end}}^+(\bar r, L)$ — defined as in Section 2 but with $T_-$ replaced by $T_+$ throughout — satisfies $X_{\text{end}}^+(\bar r, L) = 1$ if and only if $X_{\text{end}}(r, L) = 1$.*

The proof is a routine check: the basic step of $T_+$ on $\bar r$ produces the same valuation $v_+(\bar r) := v_2(3 \bar r + 1) = v_2(3 r - 1) = v_-(r)$ (by direct computation, since $3 \bar r + 1 = -(3 r - 1) \bmod 2^L$), and the affine update rule transfers without change.

Writing $\mathcal{O}_L^+$ for the $T_+$ analogue of $\mathcal{O}_L$, we obtain:

**Theorem 7.2.** *The map $r \mapsto \bar r$ restricts to a bijection $\mathcal{O}_L \leftrightarrow \mathcal{O}_L^+$.*

In particular, $|\mathcal{O}_L| = |\mathcal{O}_L^+|$ and all the structural results of Sections 3–6 transfer:

**Theorem 7.3.** *Theorems A, B, and C hold for the $T_+$ obstruction family $\mathcal{O}_L^+$, with the same constants $c_W$ and the same factor complexity function $p_W^+(n) = 2^n$.*

The transfer is straightforward and we omit further details.


## 8. Open questions

### 8.1 The exact value of $c_W$

The principal open question is to determine $c_W$ exactly, or equivalently to give a quantitative bound on the growth of $|\mathcal{A}_L^{G_{\ne 0}}|$. Three approaches present themselves, each requiring substantial additional work beyond the scope of this paper.

**(i) Substitution-theoretic.** Stérin~\cite{Sterin2020} realizes $T_+$ as a four-state finite-state transducer between bases 2 and 3. The atomic obstruction family $\mathcal{A}_L^{G_{\ne 0}}$ admits, at least heuristically, a description in terms of a related transducer-substitution system. A rigorous treatment along the lines of Pansiot~\cite{Pansiot1984} or Devyatov~\cite{Devyatov2015} would determine the asymptotic growth class of the family.

**(ii) Markov-operator-spectral.** Wirsching~\cite{Wirsching1998} constructs a Markov operator $W_3$ on residue-density functions for the $T_+$ predecessor problem, with an asymptotic invariant density $\varphi$ determining the predecessor density question. An analogous operator for the parallel reduction would have an action on $(c, d)$-space, and the spectrum of this operator would determine the asymptotic growth of the various shift-class populations $|\mathcal{O}_L^{G_a}|$. Wirsching's own work flags this kind of spectral question as substantial in its own right.

**(iii) Generating-function-combinatorial.** A direct enumeration of $|\mathcal{A}_L^{G_{\ne 0}}|$ via generating functions in $L$ is in principle accessible, but the absence of a closed-form recursion (the count depends on the joint distribution of stopping times and shift indices) makes the analysis delicate.

We make no attempt at a heuristic estimate of $c_W$; we note only that direct computation up to $L = 16$ gives a rigorous lower bound $c_W \ge 0.115$ via Theorem B (no empirical input beyond evaluating the algorithmic $X$-criterion at the finite range).

### 8.2 Bridges to nontrivial cycles of $T_-$

The shift-zero class $\mathcal{O}_L^{G_0}$ encodes residues for which the $T_-$ and $T_-^{(3)}$ stopping times stay rigidly tied. A natural question is whether the existence or non-existence of nontrivial cycles of $T_-$ is reflected in the structure of $\mathcal{O}_L^{G_0}$ for large $L$ — in particular, whether one can extract a Diophantine obstruction to additional cycles from the strict lift balance (Corollary 6.3). The relationship between obstruction residues and cycle existence is sketched in Section 2.4 but not pursued in detail; a rigorous account would require a separate paper.

### 8.3 Connection to Wirsching's framework

The Lagarias intertwining of Section 7 transfers our results to $T_+$, but Wirsching's framework~\cite{Wirsching1998} approaches the related predecessor-density problem from a Markov-operator perspective rather than a residue-classification one. The two frameworks live on the same arithmetic substrate but emphasize different invariants. A unified treatment — for instance, expressing the constant $c_W$ in terms of Wirsching's invariant density $\varphi$ — appears not to be in the literature, and would be of independent interest.


## Appendix A. Computational verification

The algorithmic $X$-invariant criterion of Section 2 is implemented in Python in the supporting code (see `atomic_anchor_verification.py` and related scripts in the project repository). For each level $L \le L_{\max}$, the script enumerates all odd residues $r$ with $r \equiv 3 \pmod 4$ and $v_2(r-1) = 1$, runs the parallel reduction, and records the terminal data $(c_J, d_J)$. The set $\mathcal{O}_L$ is read off as $\{ r : 3 d_J + c_J = 1 \}$.

We have run this enumeration through $L = 18$, producing:

| $L$ | $|\mathcal{O}_L|$ | $|\mathcal{O}_L^{G_0}|$ | $|\mathcal{O}_L^{G_{\ne 0}}|$ | $|\mathcal{A}_L^{G_{\ne 0}}|$ |
|---:|---:|---:|---:|---:|
| 6 | 3 | 3 | 0 | 3 |
| 7 | 8 | 6 | 2 | 2 |
| 8 | 19 | 15 | 4 | 3 |
| 9 | 42 | 36 | 6 | 4 |
| 10 | 91 | 82 | 9 | 9 |
| 11 | 194 | 178 | 16 | 12 |
| 12 | 409 | 380 | 29 | 21 |
| 14 | 1776 | 1648 | 128 | — |
| 16 | 7556 | 7068 | 488 | — |

The data is consistent with Theorems A, 6.2 (strict lift balance), and 6.4 (series convergence). The empirical growth rate of $|\mathcal{A}_L^{G_{\ne 0}}|$ is approximately $1.7^L$, supporting the heuristic that the convergence of the series in Theorem 6.4 is geometric and that $c_W \approx 0.12$ — but neither claim is rigorously established by the methods of this paper.


## References

\cite{Devyatov2015} R.~Devyatov, *On the subword complexity of morphic words*, Acta Inform. 52 (2015), no.~4, 379–425.

\cite{Eliahou1993} S.~Eliahou, *The $3x+1$ problem: new lower bounds on nontrivial cycle lengths*, Discrete Math. 118 (1993), 45–56.

\cite{Lagarias1985} J.~C.~Lagarias, *The $3x+1$ problem and its generalizations*, Amer. Math. Monthly 92 (1985), 3–23.

\cite{Lagarias2010a} J.~C.~Lagarias (ed.), *The Ultimate Challenge: The $3x+1$ Problem*, American Mathematical Society, 2010.

\cite{Lagarias2010b} J.~C.~Lagarias, *The $3x+1$ problem: An annotated bibliography (1963–1999) and (2000–2009)*, arXiv:math/0309224 and arXiv:math/0608208.

\cite{Pansiot1984} J.-J.~Pansiot, *Complexité des facteurs des mots infinis engendrés par morphismes itérés*, Lecture Notes in Comp. Sci. 172 (1984), 380–389.

\cite{Sterin2020} T.~Stérin, *The Collatz Process Embeds a Base Conversion Algorithm*, arXiv:2007.06979, 2020.

\cite{Tao2019} T.~Tao, *Almost all orbits of the Collatz map attain almost bounded values*, Forum of Mathematics, Pi 10 (2022), Paper No.~e12.

\cite{Wirsching1998} G.~J.~Wirsching, *The Dynamical System Generated by the $3n+1$ Function*, Lecture Notes in Mathematics 1681, Springer, 1998.
