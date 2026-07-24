"""The reflection layer: turn a posterior into questions, never verdicts.

The single most important product rule in your concept documents: the output is
never a static profile -- it is an open-ended question you may choose to sit with.
So this module never returns "you are X". It returns things you might ask yourself,
each tied to a *dated hypothesis* with its uncertainty attached.

If the safety layer says suppress, we say so plainly and ask a gentle,
non-interpretive question instead.
"""

from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import ShadowMirror

# Each hypothesis maps to a *question*, phrased so it opens reflection rather
# than closing it into a label.
_KNOWLEDGE_PROMPTS = {
    "explicit_knowledge": (
        "Your stated confidence and what you can actually do seem to line up here. "
        "Where has that confidence been tested recently, and where hasn't it?"
    ),
    "explicit_uncertainty": (
        "You seem to know that you don't know this yet. What is the smallest next "
        "thing that would move you from 'unsure' to 'sure'?"
    ),
    "latent_knowledge": (
        "You perform better here than you give yourself credit for. What are you "
        "relying on that you can't quite put into words?"
    ),
    "blind_spot": (
        "Your confidence ran ahead of what your performance supports on this. What "
        "evidence were you leaning on -- and what would change your mind?"
    ),
}

_DESIRE_PROMPTS = {
    "explicit_attraction": (
        "What you say you want and what you move toward agree here. What would it "
        "look like to act on that a little more deliberately?"
    ),
    "explicit_aversion": (
        "You say you don't want this, and you act accordingly. Is that a settled no, "
        "or a no worth revisiting sometime?"
    ),
    "latent_approach": (
        "Your actions leaned toward something you didn't fully endorse out loud. "
        "What made it pull at you? (It might be curiosity, habit, or pressure -- "
        "not necessarily a hidden 'true' want.)"
    ),
    "latent_avoidance": (
        "You endorse this, but you keep moving away from it. What tends to happen in "
        "the moments just before you step back?"
    ),
    "ambivalence": (
        "Your signals genuinely pull both ways here -- toward and away, across time. "
        "It may be that you want and don't want this at once, and that doubleness is "
        "the honest answer rather than a puzzle with one hidden solution. What would "
        "it be like to let both be true for now?"
    ),
    "threat_response": (
        "These signals fit feeling unsafe more than they fit wanting or not wanting. "
        "What, if anything, felt threatening here? There's no need to call it a "
        "preference at all."
    ),
}


def reflective_prompts(mirror: "ShadowMirror", topic=None) -> List[str]:
    """Return questions to sit with -- ordered, dated, and honestly hedged."""
    belief = mirror.current(topic)
    safety = mirror.safety(topic)

    # The threat caution is protective, not interpretive -- it must surface
    # *especially* when we are otherwise too unsure to say anything. So it is
    # checked before, and survives, any suppression.
    threat_first: List[str] = []
    if belief is not None and (
        "threat_response" in safety.flags or belief.top_desire() == "threat_response"
    ):
        threat_first.append(f"[{belief.timestamp[:10]}] {_DESIRE_PROMPTS['threat_response']}")

    if belief is None or safety.suppress_interpretation:
        prompts = list(threat_first)
        prompts.append(
            "There isn't enough certainty here to say anything useful about "
            "wanting or knowing -- which is fine. What did you notice today about "
            "the gap between what you meant to do and what you actually did?"
        )
        prompts.extend(f"(note) {m}" for m in safety.messages)
        return prompts

    date = belief.timestamp[:10]
    hedge = "leans" if belief.uncertainty < 0.5 else "very tentatively leans"
    k_n, d_n = mirror.evidence_pairs(topic)

    # Threat (if any) always comes first -- never buried under a "want" reading.
    prompts: List[str] = list(threat_first)

    # Only speak to an axis that actually has evidence.
    if k_n >= 2:
        top_k = belief.top_knowledge()
        prompts.append(
            f"[{date}] On what you know, the evidence {hedge} toward "
            f"'{top_k.replace('_', ' ')}'. {_KNOWLEDGE_PROMPTS[top_k]}"
        )

    if d_n >= 2:
        top_d = belief.top_desire()
        if top_d != "threat_response":
            prompts.append(
                f"[{date}] On what you want, the evidence {hedge} toward "
                f"'{top_d.replace('_', ' ')}'. {_DESIRE_PROMPTS[top_d]}"
            )

    # Surface every safety note as an explicit caution the person can see.
    prompts.extend(f"(caution) {m}" for m in safety.messages)

    prompts.append(
        "None of the above is a conclusion about you. It is one dated guess about "
        "signal tension. What would you say back to it?"
    )
    return prompts
