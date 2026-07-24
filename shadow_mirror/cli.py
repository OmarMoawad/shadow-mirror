"""Command-line interface for the Shadow Mirror.

Commands:
  shadow consent                         acknowledge the self-use terms (once)
  shadow log AXIS SIGNAL VALUE [-c CTX]  record one observation
  shadow reflect                         print questions to sit with
  shadow report                          print the full posterior + safety JSON
  shadow history                         list recorded observations
  shadow export PATH                     write a full copy of your data
  shadow forget                          irreversibly delete everything

  shadow subject consent SUBJECT         informed, per-stream consent flow (run it WITH them)
  shadow subject encounter SUBJECT COND  record one consent-gated encounter
  shadow subject patterns SUBJECT        first-reaction / counter-pattern questions
  shadow subject records|revoke|forget|list   inspect / withdraw / erase / list subjects

AXIS   : knowledge | desire
SIGNAL : self_report | task_performance | implicit_task | behavior |
         physiological | avoidance
VALUE  : a number in [0, 1]

Run `python -m shadow_mirror ...` or, if installed, `shadow ...`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .models import Axis, SignalType
from .reflect import reflective_prompts
from .store import CONSENT_TEXT, DEFAULT_PATH, Store
from .consent import (
    ConsentError, ConsentGrant, DATA_STREAMS, INFERENCE_DOMAINS,
    NON_OBVIOUS_STREAMS, disclosure_text,
)
from .study import Study

_AXES = ("knowledge", "desire")
_SIGNALS = ("self_report", "task_performance", "implicit_task", "behavior",
            "physiological", "avoidance")


def _require_consent(store: Store) -> bool:
    if store.has_consent():
        return True
    print("You have not acknowledged the self-use terms yet.\n")
    print(CONSENT_TEXT + "\n")
    print("Run:  shadow consent    to acknowledge (self-owned use only).")
    return False


def cmd_consent(args: argparse.Namespace, store: Store) -> int:
    print(CONSENT_TEXT + "\n")
    reply = input("Type 'I agree' to acknowledge: ").strip().lower()
    if reply == "i agree":
        store.record_consent()
        print("Acknowledged. This mirror is yours; you can `forget` it anytime.")
        return 0
    print("Not acknowledged. Nothing was stored.")
    return 1


def cmd_log(args: argparse.Namespace, store: Store) -> int:
    if not _require_consent(store):
        return 1
    if not (0.0 <= args.value <= 1.0):
        print("VALUE must be in [0, 1].", file=sys.stderr)
        return 2
    if not (0.0 <= args.reliability <= 1.0):
        print("--reliability must be in [0, 1].", file=sys.stderr)
        return 2
    mirror = store.load()
    mirror.add(args.axis, args.signal, args.value, topic=args.topic,
               context=args.context or "", reliability=args.reliability)
    store.save(mirror)
    print(f"Logged: [{args.topic}] {args.axis}/{args.signal} = {args.value:.2f}"
          + (f"  ({args.context})" if args.context else "")
          + (f"  reliability={args.reliability:.2f}" if args.reliability != 1.0 else ""))
    n = len(mirror.observations)
    if mirror.current() is None:
        print(f"({n} observation(s) so far -- not enough to reflect yet. "
              "That restraint is deliberate.)")
    return 0


def cmd_reflect(args: argparse.Namespace, store: Store) -> int:
    if not _require_consent(store):
        return 1
    mirror = store.load()
    topic = args.topic
    header = f" [topic: {topic}]" if topic else ""
    print(f"\nQuestions to sit with (not conclusions){header}:\n")
    for line in reflective_prompts(mirror, topic=topic):
        print("  - " + line)
    print()
    return 0


def cmd_report(args: argparse.Namespace, store: Store) -> int:
    if not _require_consent(store):
        return 1
    mirror = store.load()
    print(json.dumps(mirror.report(topic=args.topic), indent=2))
    return 0


def cmd_topics(args: argparse.Namespace, store: Store) -> int:
    if not _require_consent(store):
        return 1
    mirror = store.load()
    topics = mirror.topics()
    if not topics:
        print("No topics yet.")
        return 0
    for t in topics:
        k_n, d_n = mirror.evidence_pairs(t)
        print(f"{t:24s}  knowledge_pairs={k_n}  desire_pairs={d_n}")
    return 0


def cmd_history(args: argparse.Namespace, store: Store) -> int:
    if not _require_consent(store):
        return 1
    mirror = store.load()
    if not mirror.observations:
        print("No observations yet.")
        return 0
    for o in mirror.observations:
        ts = o.timestamp[:19].replace("T", " ")
        ctx = f"  ({o.context})" if o.context else ""
        rel = "" if o.reliability == 1.0 else f"  r={o.reliability:.2f}"
        print(f"{ts}  {o.topic:16s} {o.axis:9s} {o.signal_type:16s} "
              f"{o.value:.2f}{rel}{ctx}")
    return 0


def cmd_export(args: argparse.Namespace, store: Store) -> int:
    dest = store.export(Path(args.path))
    print(f"Exported all data to: {dest}")
    return 0


def cmd_forget(args: argparse.Namespace, store: Store) -> int:
    if not store.exists():
        print("Nothing to forget.")
        return 0
    reply = input("This permanently deletes ALL your data. Type 'forget' to confirm: ")
    if reply.strip().lower() == "forget":
        store.forget()
        print("Deleted. Nothing remains.")
        return 0
    print("Cancelled. Your data is untouched.")
    return 1


# ---------------------------------------------------------------------------
# Consented-subject study: getting to know another person, but only with their
# informed, granular, revocable consent. Every stream is granted on its own; the
# ones a person cannot notice about themselves must be acknowledged individually.
# ---------------------------------------------------------------------------
def cmd_subject_consent(args: argparse.Namespace, store: Store) -> int:
    subject = args.subject
    print(f"\nConsent flow for subject: {subject}\n" + "-" * 40)
    print("This records another person's informed, revocable agreement to be")
    print("studied. Run it WITH them, reading it TO them. Never fill it in for")
    print("someone who is not present and agreeing.\n")

    purpose = input("State the purpose you are both agreeing to: ").strip()
    if not purpose:
        print("No purpose given. A purpose-less grant is not informed. Aborted.")
        return 1

    grant = ConsentGrant(subject_id=subject, purpose=purpose)
    grant.domains = set(INFERENCE_DOMAINS)

    print("\nNow, each data stream. Say yes only to what they agree to.\n")
    for key, stream in DATA_STREAMS.items():
        print(f"* {stream.label}")
        print(f"    captures:   {stream.captures}")
        print(f"    may reveal: {stream.may_reveal}")
        if not stream.self_noticeable:
            print("    NOTE: this is something they may NOT notice about themselves.")
            print("          It needs its own explicit, separate agreement.")
            reply = input(f"    Do they explicitly agree to '{key}'? "
                          "Type 'I agree' verbatim: ").strip().lower()
            ok = reply == "i agree"
            if ok:
                grant.add_stream(key, acknowledged_non_obvious=True)
                grant.disclosures.append(f"{key}: {stream.captures}")
        else:
            reply = input(f"    Agree to '{key}'? [y/N]: ").strip().lower()
            ok = reply in ("y", "yes")
            if ok:
                grant.add_stream(key)
                grant.disclosures.append(f"{key}: {stream.captures}")
        print(f"    -> {'GRANTED' if ok else 'declined'}\n")

    if not grant.streams:
        print("No streams granted. Nothing to study, nothing stored.")
        return 1

    # Final confirmation: show them exactly what they agreed to.
    print(disclosure_text(grant.streams, grant.domains, grant.purpose))
    final = input("\nDoes the subject confirm ALL of the above? Type 'I agree': ").strip().lower()
    if final != "i agree":
        print("Not confirmed. Nothing stored.")
        return 1

    store.save_study(Study(grant))
    print(f"\nConsent recorded for {subject}: {len(grant.streams)} stream(s), "
          f"review in {grant.review_days} days. They can revoke anytime.")
    return 0


def cmd_subject_encounter(args: argparse.Namespace, store: Store) -> int:
    study = store.load_study(args.subject)
    if study is None:
        print(f"No consent on file for {args.subject!r}. Run: "
              f"shadow subject consent {args.subject}", file=sys.stderr)
        return 1
    for name, val in (("valence", args.valence), ("arousal", args.arousal),
                      ("action", args.action), ("reliability", args.reliability)):
        if not (0.0 <= val <= 1.0):
            print(f"--{name} must be in [0, 1].", file=sys.stderr)
            return 2
    try:
        study.observe(
            condition=args.condition, valence=args.valence, action=args.action,
            arousal=args.arousal, stream=args.stream, context=args.context or "",
            reliability=args.reliability,
        )
    except ConsentError as exc:
        print(f"Refused: {exc}", file=sys.stderr)
        return 3
    store.save_study(study)
    n = len(study.records(args.condition))
    print(f"Recorded encounter for {args.subject} / '{args.condition}' "
          f"(stream={args.stream}). {n} for this condition so far.")
    return 0


def cmd_subject_patterns(args: argparse.Namespace, store: Store) -> int:
    study = store.load_study(args.subject)
    if study is None:
        print(f"No consent on file for {args.subject!r}.", file=sys.stderr)
        return 1
    if not study.grant.active:
        print(f"Consent for {args.subject!r} is not active (revoked or lapsed). "
              "No analysis.", file=sys.stderr)
        return 1
    conditions = [args.condition] if args.condition else study.conditions()
    if not conditions:
        print("No encounters recorded yet.")
        return 0
    if args.json:
        out = {c: study.patterns(c).to_dict() for c in conditions}
        print(json.dumps(out, indent=2))
        return 0
    for c in conditions:
        reading = study.patterns(c)
        print(f"\n'{c}'  (n={reading.n_encounters}, uncertainty={reading.uncertainty}, "
              f"counter_pattern={reading.counter_pattern}"
              + (f", driver={reading.driver}" if reading.counter_pattern else "")
              + "):\n")
        for q in reading.questions:
            print("  - " + q)
    print()
    return 0


def cmd_subject_records(args: argparse.Namespace, store: Store) -> int:
    study = store.load_study(args.subject)
    if study is None:
        print(f"No consent on file for {args.subject!r}.", file=sys.stderr)
        return 1
    recs = study.records(args.condition)
    if not recs:
        print("No encounters recorded.")
        return 0
    for e in recs:
        ts = e.timestamp[:19].replace("T", " ")
        ctx = f"  ({e.context})" if e.context else ""
        print(f"{ts}  {e.condition:20s} v={e.valence:.2f} a={e.arousal:.2f} "
              f"act={e.action:.2f}  [{e.stream}]{ctx}")
    return 0


def cmd_subject_revoke(args: argparse.Namespace, store: Store) -> int:
    study = store.load_study(args.subject)
    if study is None:
        print(f"No consent on file for {args.subject!r}.", file=sys.stderr)
        return 1
    study.revoke(wipe=True)
    store.save_study(study)
    print(f"Consent for {args.subject} revoked and their encounter data wiped.")
    return 0


def cmd_subject_forget(args: argparse.Namespace, store: Store) -> int:
    if store.forget_subject(args.subject):
        print(f"Subject {args.subject} erased entirely.")
        return 0
    print(f"No such subject: {args.subject}")
    return 1


def cmd_subject_list(args: argparse.Namespace, store: Store) -> int:
    subs = store.list_subjects()
    if not subs:
        print("No consented subjects on file.")
        return 0
    for s in subs:
        study = store.load_study(s)
        g = study.grant
        state = "active" if g.active else ("revoked" if g.revoked else "lapsed")
        print(f"{s:20s}  {state:8s}  streams={len(g.streams)}  "
              f"encounters={len(study.encounters)}  purpose={g.purpose!r}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="shadow", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--path", type=Path, default=DEFAULT_PATH,
                   help=f"journal location (default: {DEFAULT_PATH})")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("consent", help="acknowledge self-use terms").set_defaults(func=cmd_consent)

    lp = sub.add_parser("log", help="record one observation")
    lp.add_argument("axis", choices=_AXES)
    lp.add_argument("signal", choices=_SIGNALS)
    lp.add_argument("value", type=float)
    lp.add_argument("-t", "--topic", default="general",
                    help="what this is about, e.g. 'recursion' (default: general)")
    lp.add_argument("-c", "--context", default="", help="free-text context")
    lp.add_argument("-r", "--reliability", type=float, default=1.0,
                    help="how much to trust this datum, 0..1 (default: 1.0)")
    lp.set_defaults(func=cmd_log)

    rp = sub.add_parser("reflect", help="print questions to sit with")
    rp.add_argument("-t", "--topic", default=None, help="scope to one topic")
    rp.set_defaults(func=cmd_reflect)

    rep = sub.add_parser("report", help="print full posterior + safety JSON")
    rep.add_argument("-t", "--topic", default=None, help="scope to one topic")
    rep.set_defaults(func=cmd_report)

    sub.add_parser("topics", help="list topics and their evidence counts").set_defaults(func=cmd_topics)
    sub.add_parser("history", help="list observations").set_defaults(func=cmd_history)

    ep = sub.add_parser("export", help="export all data to a file")
    ep.add_argument("path")
    ep.set_defaults(func=cmd_export)

    sub.add_parser("forget", help="irreversibly delete everything").set_defaults(func=cmd_forget)

    # -- consented-subject study ------------------------------------------
    sp = sub.add_parser("subject", help="study a consenting other person")
    ssub = sp.add_subparsers(dest="subject_command", required=True)

    scp = ssub.add_parser("consent", help="run the informed-consent flow with a subject")
    scp.add_argument("subject", help="an identifier for the consenting person")
    scp.set_defaults(func=cmd_subject_consent)

    sep = ssub.add_parser("encounter", help="record one dated encounter (consent-gated)")
    sep.add_argument("subject")
    sep.add_argument("condition", help="the recurring condition, e.g. 'public disagreement'")
    sep.add_argument("--valence", type=float, required=True,
                     help="emotion valence 0..1 (0=very negative, 1=very positive)")
    sep.add_argument("--action", type=float, required=True,
                     help="behaviour 0..1 (0=full withdrawal, 1=full approach)")
    sep.add_argument("--arousal", type=float, default=0.5, help="arousal 0..1")
    sep.add_argument("--stream", choices=tuple(DATA_STREAMS), default="self_report",
                     help="which consented data stream this came from")
    sep.add_argument("-c", "--context", default="", help="free-text context")
    sep.add_argument("-r", "--reliability", type=float, default=1.0)
    sep.set_defaults(func=cmd_subject_encounter)

    spp = ssub.add_parser("patterns", help="first-reaction / counter-pattern reading")
    spp.add_argument("subject")
    spp.add_argument("-c", "--condition", default=None, help="scope to one condition")
    spp.add_argument("--json", action="store_true", help="emit raw JSON instead of questions")
    spp.set_defaults(func=cmd_subject_patterns)

    srp = ssub.add_parser("records", help="show encounters held about a subject")
    srp.add_argument("subject")
    srp.add_argument("-c", "--condition", default=None)
    srp.set_defaults(func=cmd_subject_records)

    svp = ssub.add_parser("revoke", help="revoke consent and wipe the subject's data")
    svp.add_argument("subject")
    svp.set_defaults(func=cmd_subject_revoke)

    sfp = ssub.add_parser("forget", help="erase a subject entirely")
    sfp.add_argument("subject")
    sfp.set_defaults(func=cmd_subject_forget)

    ssub.add_parser("list", help="list consented subjects").set_defaults(func=cmd_subject_list)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    store = Store(args.path)
    return args.func(args, store)


if __name__ == "__main__":
    raise SystemExit(main())
