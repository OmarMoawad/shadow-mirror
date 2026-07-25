# Shadow Mirror — Session 07: The Mathematical Chapters

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverables:** `FORMAL_APPENDIX_corrected.md` (drop-in replacement for the formal content of
Part 3), `shadow_mirror_v1.0.zip` (**308 passing, 2 xfailed**), this report.

---

## 0. Summary

Seven findings. One is a presentation catastrophe with a trivial fix, three are genuine
well-definedness defects, and one was found by measuring rather than reading — a quadratic-time
defect in code I wrote in Session 4.

| # | Finding | Severity |
|---|---|---|
| **F-1** | **Every equals sign is missing from every display equation**, including Bayes' theorem | Critical (presentation) |
| **F-2** | Operator symbols collide with state symbols — four of six, including $R$ meaning both the reflective state and belief revision | High |
| **F-3** | Set braces absent throughout: $t \in 0,1,2,\ldots$, $E_t = e_1,\ldots,e_n$, $T(x)\,\{e_1,\ldots,e_k\}$ | High |
| **F-4** | $\mathcal{F}$ carries two incompatible signatures, unreconciled | Medium |
| **F-5** | $B_t$ is left untyped, yet later chapters assert properties of it | Medium |
| **F-6** | Sequential updating stated without its conditional-independence condition | Medium |
| **F-7 / D-27** | Complexity chapter gives no bound for any operator it defines — and measurement found the belief update running in **quadratic** time | High |

---

## 1. F-1 — every equals sign is gone

Seven display equations survive in the PDF as literal LaTeX, and **all seven are missing the `=`**.
The worst is on p. 67:

```
\[ P(H \mid E) \frac{P(E \mid H),P(H)} {P(E)}. \]
```

That is Bayes' theorem, in the chapter named for Bayes' theorem, with no equals sign. Also affected:
`R_{t+1} \mathcal{F}(R_t, O_{t+1})` (three separate occurrences), `B_{t+1} \mathcal{R}(B_t, E_{t+1})`,
`\mathcal{F}(R_t,, E_{t+1},, C_{t+1})`, and Invariant I's `T(x) {e_1,\ldots,e_k}`.

The corruption is systematic, not random. Three character classes were stripped by whatever
converted the source: `=` signs, backslash-escaped thin spaces (`\,` became a bare comma — visible as
the `,,` in the third equation), and escaped set braces (`\{` `\}` vanished entirely). Inline maths
lost its delimiters too, so `\(\mathcal{F}\)` renders as `(\mathcal{F})` — bare parentheses that
read as function application.

The fix is mechanical and it is the single highest-value edit available to the manuscript: **§A of
the corrected appendix restates every equation in full.** No reviewer will read past a Bayes'
theorem without an equals sign, and no reviewer should.

---

## 2. F-2 — the operators collide with the state

p. 58 defines the reflective state:

$$R_t = (E_t, C_t, H_t, B_t, K_t, U_t)$$

and then, on the same page, names the operators $O$, $C$, $H$, $R$, $Q$, $X$.

$R$ is now both the reflective state and the belief-revision operator. $O$ is both the observation
set and observation incorporation. $C$ is both context and context construction. $H$ is both the
hypothesis set and hypothesis generation. **Four collisions out of six operators**, and p. 67 then
writes "the operator $R$" nine pages after $R_{t+1}$ was defined as a state.

This is not pedantry. A reader cannot parse $\mathcal{F}(R_t, O_{t+1})$ without deciding whether
those are states or operators, and the text gives no way to decide.

The corrected appendix uses $\mathcal{I}, \mathcal{K}, \mathcal{G}, \mathcal{B}, \mathcal{Q},
\mathcal{X}$ — script capitals, none of which is a state component — with an explicit signature for
each.

---

## 3. F-3, F-4 — braces and arity

**Braces.** $t \in 0,1,2,\ldots$ is not a set membership statement. $E_t = e_1, e_2, \ldots, e_n$
reads as a tuple. $H = h_1, h_2, h_3$ likewise. $T(x)\ \{e_1, \ldots, e_k\}$ has neither an equals
sign nor delimiters. Same root cause as F-1; must be fixed explicitly rather than assumed.

**Arity.** p. 58 gives $\mathcal{F}(R_t, O_{t+1})$; p. 62 gives $\mathcal{F}(R_t, E_{t+1}, C_{t+1})$.
Two arities for one symbol, never reconciled. Defining $\mathcal{F} = \mathcal{X} \circ \mathcal{Q}
\circ \mathcal{B} \circ \mathcal{G} \circ \mathcal{K} \circ \mathcal{I}$ dissolves it: the second
form is the same map with the first two operators already applied.

---

## 4. F-5 — you cannot assert properties of an untyped object

The chapter says $B_t$ "may be probability distributions, weighted graphs, logical structures, or
hybrid models. The framework intentionally leaves this choice open."

Then later chapters assert properties of $B_t$: that it has a revision history (Invariant III), that
posteriors chain (sequential reflection), that plurality is preserved. Those are claims about an
object whose type has been left open. A reviewer will ask which of them survive under the "weighted
graph" reading, and there is no answer in the text.

The abstraction is worth keeping. The fix is to move it up a level: state **axioms** every
instantiation must satisfy, then give one reference instantiation.

- **B1 plurality** — assigns a value to every hypothesis simultaneously
- **B2 commutativity** — order of conditionally independent evidence does not matter
- **B3 invertibility** — evidence can be retracted exactly
- **B4 audit** — every application records prior, posterior, trigger, method, time

B2 and B3 are not decoration: the prototype satisfied neither, and the measured consequence was a
final belief of 0.0396 or 0.9900 for the same five observations depending only on arrival order.
Stating them as axioms turns that from an embarrassment into a specification the architecture
enforces — and `test_operator_correspondence.py` now asserts all four.

---

## 5. F-6 — the missing independence assumption

> "After each observation, the posterior becomes the new prior."

True only if $e_i \perp e_j \mid h$. In this domain that is frequently false: two self-reports on
consecutive days about the same topic are correlated through mood, framing and recall, not only
through the latent state. Left unstated it is an error; stated, it is an honest limitation — and it
is what makes the implementation's per-evidence keying defensible rather than arbitrary, since
re-submitting the same observation cannot compound it.

Neither that nor temporal decay substitutes for a correlated-likelihood model. §A.6 says so.

---

## 6. F-7 / D-27 — the complexity chapter, and what measurement found

The chapter warns that unrestricted pairwise comparison "could approach $O(n^2)$" and that naive
history storage is $O(T)$. Neither bound applies to any operator the monograph actually defines. No
bound is given for belief revision, provenance traversal, or inquiry planning.

So I measured all four. Scaling ratios per doubling:

| Operation | Bound | Measured |
|---|---|---|
| Provenance closure `ancestors()` | $O(V+E)$ | **2.0×** ✓ |
| Inquiry planning | $O(\lvert H\rvert \cdot \lvert \mathcal{A}\rvert)$ | 3.9× at $\lvert H\rvert = \lvert \mathcal{A}\rvert$ ✓ |
| Engine `add()` — full recompute | $O(n^2)$ cumulative | **3.8×** — quadratic |
| Belief update — log-odds ledger | expected $O(1)$ | **4.2× — quadratic** ❌ |

The last row is a defect in code I wrote in Session 4. `BeliefLedger.log_odds()` summed every
contribution on every call, so each update was $O(n)$ and a session of $n$ updates was $O(n^2)$:
11.8 ms at 1,000 updates, 624 ms at 8,000. **Fixed** by maintaining a running total; re-measured at
**2.0× per doubling**, 78 ms at 16,000 updates. A regression test now fails if the ratio exceeds 3×.

The engine's own `add()` remains quadratic — it recomputes the full belief state on every
observation. 27 ms at 100 evidence pairs, 1121 ms at 800. That is a real optimisation target
(incremental recompute), and it is worth noting that **the monograph predicted exactly this growth
before the code existed.** The complexity chapter was right; it just needs to say it about the
operators it defines rather than about a strawman.

---

## 7. Operator-to-implementation map

`tests/test_operator_correspondence.py` binds each formal operator to a callable and asserts its
specified behaviour. Two operators have **no** implementation, and are recorded as strict `xfail`
with the reason rather than quietly omitted:

| Operator | Implementation | Status |
|---|---|---|
| $\mathcal{I}$ ingest | `ShadowMirror.add`, `URG` provenance edges | ✅ |
| $\mathcal{K}$ context | `URG.revise_context`, `contextualise` | ✅ |
| $\mathcal{G}$ generation | `engine._infer_*` posterior over hypotheses | ✅ |
| $\mathcal{B}$ revision | `BeliefRevisionEngine` — axioms B1–B4 all asserted | ✅ |
| $\mathcal{Q}$ inquiry | `InquiryPlanner`, `expected_information_gain` | ✅ |
| $\mathcal{X}$ explanation | `reflective_prompts`, `EWKProfile`, `credible_set` | ✅ |
| **Causal reasoning** (pp. 64–66) | — | ❌ **prose only.** No do-operator, no intervention, no counterfactual query. |
| **Knowledge consolidation** $K_t \leftarrow B_t$ (p. 145) | — | ❌ **prose only.** No promotion criterion from belief to revisable knowledge. |

Those two gaps are now enumerable rather than implied, which is the point: a reference architecture
earns the word "reference" when the distance between its formalism and its implementation can be
listed.

The causal gap is the more significant. Chapter "Reflection and Causal Reasoning" occupies pp. 64–66
and Pearl (2009) is in the bibliography, but nothing in the codebase performs an intervention. The
architecture paper should present causal reflection as **research agenda**, not as a component.

---

## 8. What changed in the claim inventory

**Now claimable:** every operator in the formalism either has a named implementation with asserted
behaviour, or is listed as unimplemented. Four belief-revision axioms are enforced by test.
Complexity bounds for three of four core operations are measured, not asserted.

**Now explicitly disclaimed:** causal reflective reasoning and knowledge consolidation are
specified but not built. The engine's observation intake is quadratic.

---

## 9. Corrections table

| # | Location | Action |
|---|---|---|
| M-1 | All seven display equations | **Replace with §A of the corrected appendix.** Highest-value single edit in the manuscript. |
| M-2 | p. 58 operator names | Rename to $\mathcal{I}, \mathcal{K}, \mathcal{G}, \mathcal{B}, \mathcal{Q}, \mathcal{X}$ |
| M-3 | pp. 55–58 set notation | Restore braces throughout |
| M-4 | pp. 58, 62 | Define $\mathcal{F}$ as the composition; drop the second signature |
| M-5 | p. 57 belief state | Add axioms B1–B4 and the reference instantiation |
| M-6 | p. 68 sequential reflection | State the conditional-independence condition and that it is often violated here |
| M-7 | pp. 71–74 complexity | Replace with the four measured bounds |
| M-8 | pp. 64–66 causal | Reframe as research agenda; no implementation exists |

---

*Session 08 — rebuilding the claim-to-validation matrix against the code that now exists —
continues automatically.*
