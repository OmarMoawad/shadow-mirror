"""A self-contained walkthrough. Run:  python demo.py

Shows the three things the concept documents care about most:
  1. A confidence/performance gap surfacing as a *question*, not a label.
  2. A stated-vs-behaviour desire tension.
  3. The trauma guard: arousal + avoidance refusing to become "hidden want".
"""

import json

from shadow_mirror import ShadowMirror, reflective_prompts


def show(title, mirror):
    print("=" * 70)
    print(title)
    print("=" * 70)
    print(json.dumps(mirror.report(), indent=2))
    print("\nQuestions to sit with:")
    for p in reflective_prompts(mirror):
        print("  - " + p)
    print()


# 1. Overconfidence on a topic: says 0.9 sure, performs ~0.25.
k = ShadowMirror()
k.add_batch([
    ("knowledge", "self_report", 0.9, "recursion", "I know recursion cold"),
    ("knowledge", "task_performance", 0.3, "recursion", "recursion exercise"),
    ("knowledge", "self_report", 0.88, "recursion", "still feel solid"),
    ("knowledge", "task_performance", 0.25, "recursion", "second exercise"),
])
show("1) Knowledge: a confidence/performance gap", k)

# 2. Desire tension: says doesn't want it, keeps doing it.
d = ShadowMirror()
d.add_batch([
    ("desire", "self_report", 0.2, "leaderboard", "I don't care about the leaderboard"),
    ("desire", "behavior", 0.85, "leaderboard", "checked ranking 6x today"),
    ("desire", "self_report", 0.25, "leaderboard", "really, I don't"),
    ("desire", "behavior", 0.8, "leaderboard", "checked again"),
])
show("2) Desire: stated vs. behavioural tension", d)

# 3. Trauma guard: same avoidance pattern, but with high arousal + avoidance.
#    (topic given as 4th positional; context as 5th.)
t = ShadowMirror()
t.add_batch([
    ("desire", "self_report", 0.2, "calls", "I avoid calling them"),
    ("desire", "behavior", 0.15, "calls", "didn't call"),
    ("desire", "physiological", 0.9, "calls", "heart racing when the phone rang"),
    ("desire", "avoidance", 0.9, "calls", "left the room"),
    ("desire", "self_report", 0.2, "calls", "still avoid it"),
    ("desire", "behavior", 0.2, "calls", "still didn't"),
    ("desire", "physiological", 0.88, "calls", "tight chest"),
    ("desire", "avoidance", 0.9, "calls", "put the phone away"),
])
show("3) Trauma guard: threat-response, NOT a hidden want", t)

# 4. Ambivalence: stated want and behaviour both swing hard over time.
#    The doubleness is held up, un-collapsed -- not resolved into a "true" want.
a = ShadowMirror()
a.add_batch([
    ("desire", "self_report", 0.9, "moving_abroad", "some days I ache to go"),
    ("desire", "behavior", 0.85, "moving_abroad", "researched visas"),
    ("desire", "self_report", 0.1, "moving_abroad", "other days I dread it"),
    ("desire", "behavior", 0.15, "moving_abroad", "cancelled the call"),
    ("desire", "self_report", 0.85, "moving_abroad", "back to yearning"),
    ("desire", "behavior", 0.8, "moving_abroad", "booked a viewing"),
    ("desire", "self_report", 0.15, "moving_abroad", "and back to no"),
    ("desire", "behavior", 0.2, "moving_abroad", "let it lapse"),
])
show("4) Ambivalence: wanting and not-wanting, held un-collapsed", a)
