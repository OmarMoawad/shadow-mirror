# Corrected Formal Appendix

**Drop-in replacement for the formal content of Part 3 (pp. 55–79) and Appendix B.**
Every equation below is written out in full LaTeX. Every symbol has one meaning. Every operator has
a named implementation in `shadow_mirror` v1.0 or is explicitly marked as unimplemented.

---

## A.1 Notation

Time is discrete and indexes the order in which information becomes available, not physical
duration:

$$t \in \{0, 1, 2, \ldots\}$$

| Symbol | Object | Type |
|---|---|---|
| $O_t$ | observations available at $t$ | finite set |
| $E_t$ | evidence state | finite set of evidence objects |
| $C_t$ | contextual state | structured record |
| $H_t$ | hypothesis set | finite set, $\lvert H_t \rvert \ge 0$ |
| $B_t$ | belief state | see A.4 |
| $K_t$ | knowledge state | $K_t \subseteq H_t$, revisable |
| $U_t$ | uncertainty state | see A.5 |
| $R_t$ | reflective state | the 6-tuple below |

$$R_t = (E_t,\; C_t,\; H_t,\; B_t,\; K_t,\; U_t)$$

**Operators use script capitals throughout, and no script capital is ever also a state component.**
The monograph as it stands names the operators $O, C, H, R, Q, X$, which collides with $O_t$, $C_t$,
$H_t$ and $R_t$ — four collisions out of six, including $R$ meaning both *the reflective state* and
*the belief-revision operator* on facing pages. That must not survive to submission.

| Operator | Role | Signature |
|---|---|---|
| $\mathcal{I}$ | evidence construction (**I**ngest) | $\mathcal{I}: O_{t+1} \times C_t \to E_{t+1}$ |
| $\mathcal{K}$ | context construction | $\mathcal{K}: C_t \times E_{t+1} \to C_{t+1}$ |
| $\mathcal{G}$ | hypothesis generation | $\mathcal{G}: E_{t+1} \times C_{t+1} \times H_t \to H_{t+1}$ |
| $\mathcal{B}$ | belief revision | $\mathcal{B}: B_t \times E_{t+1} \to B_{t+1}$ |
| $\mathcal{Q}$ | inquiry planning | $\mathcal{Q}: B_{t+1} \times \mathcal{A} \to \mathcal{A}^{\*}$ |
| $\mathcal{X}$ | explanation synthesis | $\mathcal{X}: R_{t+1} \to \Xi$ |

$\mathcal{A}$ is the set of candidate observations, $\mathcal{A}^{\*}$ an ordered subset, and $\Xi$
the space of explanations.

---

## A.2 Evidence objects

$$e_i = \langle v_i,\; s_i,\; r_i,\; u_i,\; c_i,\; \tau_i,\; p_i \rangle$$

with observed value $v_i \in [0,1]$, source $s_i$, reliability $r_i \in [0,1]$, uncertainty
$u_i \in [0,1]$, context reference $c_i$, timestamp $\tau_i$, and provenance $p_i \subseteq E_{<t}
\cup O_{\le t}$.

$p_i$ is a **set**, not a single parent. This is the formal statement of Invariant II, and writing
it as a scalar is what licensed the prototype defect in which derived evidence reported one parent
and silently discarded the rest.

$$E_t = \{e_1, e_2, \ldots, e_n\}$$

---

## A.3 Reflective evolution

$$R_{t+1} \;=\; \mathcal{F}(R_t,\, O_{t+1})$$

where $\mathcal{F}$ is the composition

$$\mathcal{F} \;=\; \mathcal{X} \circ \mathcal{Q} \circ \mathcal{B} \circ \mathcal{G} \circ \mathcal{K} \circ \mathcal{I}$$

The monograph currently gives $\mathcal{F}$ two incompatible signatures — $\mathcal{F}(R_t, O_{t+1})$
on p. 58 and $\mathcal{F}(R_t, E_{t+1}, C_{t+1})$ on p. 62 — without reconciling them. Defining
$\mathcal{F}$ as the composition dissolves the problem: the second form is the same map with
$\mathcal{I}$ and $\mathcal{K}$ already applied, and can be written

$$\mathcal{F} \;=\; \mathcal{F}' \circ (\mathcal{K} \circ \mathcal{I}), \qquad
\mathcal{F}'(R_t,\, E_{t+1},\, C_{t+1}) = (\mathcal{X} \circ \mathcal{Q} \circ \mathcal{B} \circ \mathcal{G})(\cdot)$$

---

## A.4 The belief state, instantiated

The monograph leaves $B_t$ deliberately unspecified — "probability distributions, weighted graphs,
logical structures, or hybrid models". Later chapters then assert properties *of* $B_t$ (revision
history, sequential recursion, hypothesis plurality). Properties cannot be asserted of an object
whose type is open. The fix is not to close the abstraction but to state the **axioms** any
instantiation must satisfy, and then give one reference instantiation.

**Axioms on $B_t$.** For hypotheses $h \in H_t$ and evidence $e$:

* **B1 (plurality)** $B_t$ assigns a value to every $h \in H_t$ simultaneously; it does not
  distinguish a unique maximiser.
* **B2 (commutativity)** For conditionally independent $e, e'$:
  $\mathcal{B}(\mathcal{B}(B_t, e), e') = \mathcal{B}(\mathcal{B}(B_t, e'), e)$.
* **B3 (invertibility)** There exists $\mathcal{B}^{-1}$ with
  $\mathcal{B}^{-1}(\mathcal{B}(B_t, e), e) = B_t$.
* **B4 (audit)** Every application of $\mathcal{B}$ records $(h, e, B_t(h), B_{t+1}(h), \text{method}, \tau)$.

B2 and B3 are not decoration. The prototype satisfied neither, and the measured consequence was a
final belief of $0.0396$ or $0.9900$ for the same five observations depending only on arrival order.

**Reference instantiation.** Per-hypothesis log-odds ledger:

$$\ell_t(h) \;=\; \operatorname{logit} \pi(h) \;+\; \sum_{e \in \mathcal{E}_t} w_e \, \lambda_e(h),
\qquad
\lambda_e(h) = \log \frac{P(e \mid h)}{P(e \mid \lnot h)},
\qquad
B_t(h) = \sigma\big(\ell_t(h)\big)$$

with prior $\pi(h)$, reliability weight $w_e \in [0,1]$, and $\sigma$ the logistic function.
$\mathcal{E}_t$ is a **set keyed by evidence identity**, which gives B2 (addition commutes), B3
(subtract the term), and idempotence under re-application of the same evidence.

Clamping to a display range is applied to $B_t(h)$ **on output only**. Clamping the state is not
invertible and destroys B3.

---

## A.5 Uncertainty

$$U_t = \langle u^{\text{obs}}_t,\; u^{\text{mod}}_t,\; u^{\text{exp}}_t,\; u^{\text{tmp}}_t,\; u^{\text{eth}}_t \rangle$$

each in $[0,1]$. Reporting a scalar requires an explicit aggregation rule; the reference
implementation uses

$$u_t \;=\; \min\Big(1,\; \alpha_1 \tilde{H}(B_t) + \alpha_2 \operatorname{sd}_w(E_t) + \alpha_3 \theta(n) + \alpha_4 \, m_t\Big)$$

with $\tilde{H}$ the entropy of $B_t$ normalised to $[0,1]$, $\operatorname{sd}_w$ the weighted
dispersion of the evidence, $\theta(n) = \max(0, (4-n)/4)$ a thinness penalty, and $m_t$ the
posterior mass on the *unmodelled* hypothesis. Coefficients
$(\alpha_1,\ldots,\alpha_4) = (0.40, 0.15, 0.10, 0.35)$ are design choices, not fitted parameters,
and are stated as such.

---

## A.6 Sequential updating, and the assumption it requires

$$P(h) \;\to\; P(h \mid e_1) \;\to\; P(h \mid e_1, e_2) \;\to\; \cdots$$

$$P(h \mid e_{1:n}) \;=\; \frac{P(h) \prod_{i=1}^{n} P(e_i \mid h)}{\sum_{h' \in H} P(h') \prod_{i=1}^{n} P(e_i \mid h')}
\qquad \textbf{only if} \quad e_i \perp e_j \mid h \;\; \forall i \neq j$$

The monograph states "after each observation, the posterior becomes the new prior" without stating
the conditional-independence condition. In this domain the condition is **frequently violated**: two
self-reports on consecutive days about the same topic are correlated through mood, framing and
recall, not only through the latent state.

This is a limitation to declare, not to hide. Two mitigations are implemented:

1. Evidence contributions are keyed by identity, so re-submitting the same observation does not
   compound it.
2. Temporal decay down-weights clustered observations, which partially offsets the
   over-counting that correlated evidence produces.

Neither is a substitute for a correlated-likelihood model. That remains open.

---

## A.7 Bayes' theorem

$$P(h \mid e) \;=\; \frac{P(e \mid h)\, P(h)}{P(e)}, \qquad P(e) = \sum_{h' \in H} P(e \mid h')\, P(h') > 0$$

*(As printed on p. 67 of the monograph this equation has no equals sign. See §B.)*

Hypothesis plurality: reflection does **not** require collapsing to

$$\hat{h} = \operatorname*{arg\,max}_{h \in H} P(h \mid e)$$

Instead the reported object is the smallest credible set

$$\mathcal{S}_\gamma(B_t) \;=\; \operatorname*{arg\,min}_{S \subseteq H} \Big\{ \lvert S \rvert \;\Big|\; \sum_{h \in S} B_t(h) \ge \gamma \Big\}$$

with correctness measured as coverage, $\Pr[h^{\*} \in \mathcal{S}_\gamma] \ge \gamma$, rather than
as top-1 accuracy.

---

## A.8 Inquiry

For candidate observation $a \in \mathcal{A}$ with binary outcome $Y_a$:

$$\mathrm{EIG}(a) \;=\; \mathbb{H}(B) \;-\; \mathbb{E}_{Y_a}\big[\mathbb{H}(B \mid Y_a)\big]
\;=\; \mathbb{H}(B) - \sum_{y \in \{0,1\}} P(y)\, \mathbb{H}(B \mid Y_a = y)$$

$$\mathcal{Q}(B, \mathcal{A}) = \operatorname*{arg\,max}_{a \in \mathcal{A}} \; \frac{\mathrm{EIG}(a)}{\mathrm{cost}(a)}$$

Note that $\mathrm{EIG}(a)$ depends on $a$. The heuristic it replaces —
$\text{benefit} = 1 - \lvert B(h_i) - B(h_j) \rvert$ — does not, which is why it performed no better
than random selection.

---

## A.9 Traceability

$$T(x) \;=\; \{e_1, e_2, \ldots, e_k\} \subseteq E_t, \qquad T(x) \neq \varnothing \;\; \forall x \in \Xi$$

*(As printed in the monograph the equals sign and the set braces are both absent.)*

Provenance closure, which is what Invariant II actually requires:

$$\operatorname{anc}(e) \;=\; \bigcup_{p \in p_e} \big(\{p\} \cup \operatorname{anc}(p)\big)$$

— the transitive closure over *all* parents, not the first.

---

## A.10 Complexity — measured, not asserted

| Operation | Bound | Measured scaling per doubling |
|---|---|---|
| $\mathcal{B}$ — one belief update (log-odds ledger) | $O(1)$ | **2.0×** ✓ |
| $\operatorname{anc}(e)$ — provenance closure | $O(V + E)$ | **2.0×** ✓ |
| $\mathcal{Q}$ — inquiry planning | $O(\lvert H \rvert \cdot \lvert \mathcal{A} \rvert)$ | 3.9× at $\lvert H \rvert = \lvert \mathcal{A} \rvert$ ✓ (product of two linear factors) |
| Engine `add()` — full recompute per observation | $O(n)$ per call, $O(n^2)$ cumulative | **3.8×** — quadratic, as the monograph predicts |

The monograph's warning that unrestricted recomputation "could approach $O(n^2)$" is not
hypothetical: the shipped engine has exactly that growth, 27 ms at 100 evidence pairs and 1121 ms at
800. It is a real optimisation target (incremental recompute), not a strawman.

The complexity chapter should state these four bounds. It currently states $O(n^2)$ for pairwise
evidence comparison — which nothing in the architecture requires — and $O(T)$ for naive history
storage, and gives no bound for any operator it defines.
