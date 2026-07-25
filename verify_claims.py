"""Re-derive every quantitative claim used in the unified draft.

Ground rule 4 of this programme: no number enters a manuscript unless a file in
the repository produces it and the person writing the sentence has run that file.
This is that file for `papers/UNIFIED_DRAFT.md`.

Run:  python verify_claims.py
"""
import itertools
import json
import time

from shadow_mirror import (
    INSTITUTIONAL, ConsentLedger, DeploymentContext, DeploymentRefusal,
    FormationModel, FormationRefusal, ShadowMirror,
)
import shadow_mirror.invariants as INV

OUT = {}


def head(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


# ---------------------------------------------------------------- intake cost
head("1. Write-then-consult scaling  (D-28: was 3.8x per doubling before Session 12)")


def timed(n_pairs):
    rows = []
    for i in range(n_pairs):
        rows.append(("knowledge", "self_report", 0.8, "t%d" % (i % 7), "s"))
        rows.append(("knowledge", "task_performance", 0.3, "t%d" % (i % 7), "p"))
    t0 = time.perf_counter()
    m = ShadowMirror()
    m.add_batch(rows)
    m.report()
    return (time.perf_counter() - t0) * 1000.0


times = {}
for n in (100, 200, 400, 800):
    times[n] = min(timed(n) for _ in range(3))          # best of three
    print("  %4d evidence pairs: %8.2f ms" % (n, times[n]))

ratio = times[800] / times[400]
print("  scaling per doubling (400->800): %.2fx   (linear ~2.0, quadratic ~4.0)" % ratio)
OUT["intake"] = {"ms_by_pairs": {str(k): round(v, 2) for k, v in times.items()},
                 "ratio_per_doubling": round(ratio, 2)}


# ------------------------------------------------------- belief order-invariance
head("2. Belief revision: order invariance over all 120 permutations")

obs = [("knowledge", "self_report", 0.90, "recursion", "a"),
       ("knowledge", "task_performance", 0.30, "recursion", "b"),
       ("knowledge", "self_report", 0.85, "recursion", "c"),
       ("knowledge", "task_performance", 0.25, "recursion", "d"),
       ("knowledge", "self_report", 0.70, "recursion", "e")]

finals = []
for perm in itertools.permutations(obs):
    m = ShadowMirror()
    m.add_batch(list(perm))
    post = m.report()["knowledge"]["posterior"]
    finals.append(tuple(round(post[k], 12) for k in sorted(post)))

spread = max(max(col) - min(col) for col in zip(*finals))
print("  permutations examined  : %d" % len(finals))
print("  distinct outcomes      : %d" % len(set(finals)))
print("  max spread across perms: %.3e" % spread)
OUT["order_invariance"] = {"permutations": len(finals),
                           "distinct_outcomes": len(set(finals)),
                           "max_spread": spread}


# -------------------------------------------------------------- invariants
head("3. Invariant catalogue: every check is callable")

checks = sorted(n for n in dir(INV) if n.startswith("check_"))
print("  callable invariant checks: %d" % len(checks))
for c in checks:
    print("    - %s" % c)
OUT["invariants"] = {"count": len(checks), "names": checks}


# -------------------------------------------------------------- deployment gate
head("4. Deployment gate  (AI Act Art. 5(1)(f) mechanism, D-32)")

results = {}
for name, ctx in (("institutional", DeploymentContext(INSTITUTIONAL)),
                  ("undeclared", DeploymentContext()),
                  ("self", DeploymentContext("self"))):
    try:
        ctx.require("physiological")
        results[name] = "allowed"
    except DeploymentRefusal as e:
        results[name] = "refused"
        if name == "institutional":
            first = " ".join(str(e).split())[:150]
    print("  %-14s -> %s" % (name, results[name]))
print("\n  refusal text (institutional):\n    %s..." % first)

# the safety exception needs written text, not a boolean
excepted = DeploymentContext(INSTITUTIONAL, safety_exception_basis="")
blank_refused = not excepted.permits("physiological")
withbasis = DeploymentContext(
    INSTITUTIONAL, safety_exception_basis="Guard exists solely to prevent the "
                                          "measured false hidden-desire harm.")
print("\n  empty safety_exception_basis still refuses : %s" % blank_refused)
print("  written basis permits the stream           : %s" % withbasis.permits("physiological"))
OUT["deployment"] = {"by_context": results,
                     "empty_basis_refuses": blank_refused,
                     "written_basis_permits": withbasis.permits("physiological")}


# -------------------------------------------------------------- consent ledger
head("5. Consent ledger  (GDPR Art. 7(1) demonstrability / 7(3) parity, D-31)")

led = ConsentLedger()
e1 = led.record("granted", "s1", streams=["self_report"], purpose="study")
e2 = led.record("stream_added", "s1", streams=["behavior_log"], purpose="study")
e3 = led.record("revoked", "s1", purpose="study")
print("  chain length        : %d" % len(led.events()))
print("  verify()            : %s" % led.verify())
print("  streams at t(e2)    : %s" % led.streams_granted_at("s1", e2.timestamp))
print("  streams at t(e3)    : %s" % led.streams_granted_at("s1", e3.timestamp))

tampered = ConsentLedger()
tampered.record("granted", "s1", streams=["self_report"], purpose="study")
tampered.record("stream_added", "s1", streams=["behavior_log"], purpose="study")
tampered.events()[0].detail["purpose"] = "a different purpose"
print("  verify() after edit : %s   <- history edit is detectable" % tampered.verify())

receipt = led.withdrawal_receipt("s1")
print("  withdrawal receipt keys: %s" % sorted(receipt))
OUT["ledger"] = {"entries": len(led.events()), "verifies": led.verify(),
                 "detects_tampering": not tampered.verify(),
                 "receipt_keys": sorted(receipt)}


# -------------------------------------------------------------- formation refusals
head("6. Formation model: refusals refuse *when called* (Invariant XI, cond. b)")

fm = FormationModel(subject="s1")
refused, returned = [], []
for name in ("maturity_level", "overall_maturity", "developmental_stage",
             "eventual_purpose", "life_purpose", "what_they_still_need",
             "deficits", "infer_origin", "infer_background",
             "instrument_trajectory", "trajectory"):
    fn = getattr(fm, name, None)
    if fn is None:
        continue
    try:
        fn()
        returned.append(name)
        print("  %-22s -> RETURNED A VALUE" % name)
    except FormationRefusal as e:
        refused.append(name)
        print("  %-22s -> refused: %s" % (name, " ".join(str(e).split())[:58]))
    except TypeError:
        pass                                    # needs arguments; not a refusal site
print("\n  refusing methods exercised: %d   methods that returned: %d"
      % (len(refused), len(returned)))

# absence is not refusal: deleting the method must also fail the invariant
class Deleted(FormationModel):
    eventual_purpose = None

print("  deleting a refusing method leaves no explanation for a caller: "
      "%s" % (Deleted(subject="s2").eventual_purpose is None))
OUT["formation"] = {"refusing_methods": refused, "returned": returned}


# -------------------------------------------------------------- open questions
head("7. open_questions(): what replaces the refused asks")

for q in FormationModel(subject="s1").open_questions()[:4]:
    print("  - %s" % q)
OUT["open_questions_sample"] = FormationModel(subject="s1").open_questions()[:4]


# -------------------------------------------------------------- summary
head("SUMMARY")
print(json.dumps(OUT, indent=2, default=str))
with open("verify_claims_output.json", "w", encoding="utf8") as f:
    json.dump(OUT, f, indent=2, default=str)
print("\nwritten: verify_claims_output.json")
