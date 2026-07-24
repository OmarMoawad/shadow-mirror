"""Command-line interface for the Shadow Mirror.

Commands:
  shadow consent                         acknowledge the self-use terms (once)
  shadow log AXIS SIGNAL VALUE [-c CTX]  record one observation
  shadow reflect                         print questions to sit with
  shadow report                          print the full posterior + safety JSON
  shadow history                         list recorded observations
  shadow export PATH                     write a full copy of your data
  shadow forget                          irreversibly delete everything

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
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    store = Store(args.path)
    return args.func(args, store)


if __name__ == "__main__":
    raise SystemExit(main())
