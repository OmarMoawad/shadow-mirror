"""Formation: what a person has told us about who they are, and what they have not.

This module exists because someone asked the architecture to determine "who people
probably are according to their will, desire and need — where they come from, how
mature they are, what they still need to be mature enough, what their eventual purpose
probably is".

Four of those are different requests, and the architecture answers them differently.

  will / desire / need      -> modelled, from instruments the person completed
  where they come from      -> REFUSED unless the person declared it
  how mature they are       -> REFUSED as a rank; offered as a dimensional profile
  what they still need      -> REFUSED; the system does not prescribe to a person
  their eventual purpose    -> REFUSED; there is no construct behind it

The refusals are not omissions. They are the feature. Each has a named ground, a
decision procedure, and a negative test, and each returns an explanation the person
can read rather than a silent absence.

Design commitments, in order of how much they constrain the code:

1.  **Nothing about a person enters this model unless the person put it there.**
    Either they declared it, or they completed an instrument. There is no third
    route. ``infer_*`` methods exist only to raise.

2.  **The person outranks the model.** A correction from the person wins for
    display, immediately and without argument. The evidence that disagreed is not
    deleted — it is marked contested and stays inspectable and retractable.

3.  **No instrument is administered whose licence we have not confirmed.** Most of
    the instruments in this area are author-held with no published permission
    statement. Administering one on an assumption is a real risk to a real
    researcher, so an unconfirmed licence is a refusal, not a warning.

4.  **No item text is bundled with this software.** The registry carries scoring
    rules and metadata only. The researcher supplies the licensed instrument. This
    keeps the package distributable and makes the licence status honest rather than
    decorative.

5.  **Stage instruments are refused outright.** Loevinger's WUSCT, Kegan's
    Subject-Object Interview and Cook-Greuter's MAP each produce a single ordered
    position for a person, and that is not an incidental summary — it is the
    construct. You cannot keep the construct and discard the rank without
    misrepresenting it. So the construct is dropped.

Zero runtime dependencies, consistent with the rest of the package.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .deployment import (
    DeploymentContext, DeploymentRefusal, SELF, CONSENTED_INDIVIDUAL,
)

__all__ = [
    "FormationRefusal", "REFUSAL_GROUNDS",
    "LICENCE_CONFIRMED_FREE", "LICENCE_AUTHOR_PERMISSION_REQUIRED",
    "LICENCE_UNVERIFIED", "LICENCE_EXTERNAL_SCORING", "LICENCE_PAID_CERTIFIED",
    "InstrumentSpec", "SubscaleScore", "Administration",
    "DeclaredAttribute", "Override", "FormationModel",
    "REGISTRY", "PSYCHOMETRIC_STREAM", "register_instrument",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------
# Refusals
# --------------------------------------------------------------------------

#: The consent stream this module reads. Distinct from ``physiological``
#: deliberately: psychometric responses are sensitive under GDPR Art. 9 and are
#: expressly named in Egypt's PDPL 151/2020 Art. 1 ("psychological ... health"),
#: which — unlike the GDPR — grants no scientific-research exemption.
PSYCHOMETRIC_STREAM = "psychometric"


REFUSAL_GROUNDS: Dict[str, str] = {
    "INFERRED_ORIGIN": (
        "Background may be declared by the person, never inferred about them. "
        "Inferring where someone comes from — nationality, class, religion, "
        "ethnicity, upbringing — from their behaviour is inference of a special "
        "category of data (GDPR Art. 9; Egypt PDPL 151/2020 Art. 1), and where it "
        "runs on biometric input it is prohibited outright by EU AI Act Art. "
        "5(1)(g). Ask the person. Record what they say. Let them change it."
    ),
    "GLOBAL_RANKING": (
        "This system does not produce a single number, level or stage for a person. "
        "The instruments that do — Loevinger's sentence completion test, Kegan's "
        "subject-object interview, Cook-Greuter's MAP — produce one because the rank "
        "IS the construct, not a summary of it. Keeping the construct while "
        "discarding the rank would misrepresent the instrument. So the construct is "
        "not offered. A dimensional profile is available instead: use profile()."
    ),
    "PRESCRIPTIVE_DEFICIT": (
        "This system does not tell a person what they lack or what they must acquire "
        "in order to be adequate. That is a directive about identity, and Invariant X "
        "forbids it. What is available instead is a question: see "
        "FormationModel.open_questions(), which returns things the person has not "
        "yet told us, ranked by how much an answer would resolve. A question invites; "
        "a verdict instructs."
    ),
    "PURPOSE_ATTRIBUTION": (
        "This system does not tell a person what their purpose is. No validated "
        "construct exists for a person's eventual purpose, so any output would be "
        "invented, and inventing it would violate the project's first ground rule. "
        "What can be measured is the person's OWN reported sense of meaning and "
        "purpose — the Meaning in Life Questionnaire measures presence of and search "
        "for meaning; the Claremont Purpose Scale measures three dimensions of it. "
        "Those report what the person said. They do not tell them what it is for."
    ),
    "UNLICENSED_INSTRUMENT": (
        "This instrument's permission terms are not confirmed. Most instruments in "
        "this area are author-held with no published licence statement; using one on "
        "an assumption exposes the researcher. Obtain written permission from the "
        "author, record it with confirm_licence(), and try again."
    ),
    "EXTERNAL_SCORING": (
        "This instrument cannot be scored locally. Its scoring algorithm is withheld "
        "and responses must be sent to a third party, which would take the person's "
        "answers out of this system and outside the consent recorded for them."
    ),
    "RATER_REQUIRED": (
        "This instrument requires a trained or certified human rater. It cannot be "
        "scored by software, and presenting an algorithmic approximation as though it "
        "were the instrument would be a fabrication."
    ),
    "UNCONSENTED_INSTRUMENT": (
        "No active consent grant covers the psychometric stream for this person. "
        "Psychometric responses are sensitive data. Consent must be granted before "
        "administration, not reconstructed afterwards."
    ),
    "NOT_SELF_COMPLETED": (
        "An instrument result may only be entered by the person it is about. A third "
        "party completing an instrument on someone's behalf produces a claim about "
        "them, not a report from them."
    ),
    "NORMS_ABSENT": (
        "This instrument publishes no population norms, so a score cannot be placed "
        "against a reference group. The raw subscale score is available; a percentile, "
        "a category or a comparison is not."
    ),
    "POPULATION_UNVALIDATED": (
        "This instrument has not been validated in the population being asked to "
        "complete it. The score can be recorded; it should not be interpreted as "
        "though the published psychometrics apply."
    ),
    "DEPLOYMENT_CONTEXT": (
        "The psychometric stream is refused in this deployment context. Reasoning "
        "about a person's needs, values, meaning or self-reported maturity on behalf "
        "of an institution is the workplace and education case that EU AI Act Art. "
        "5(1)(f) addresses, and it is the case this project has committed not to "
        "serve."
    ),
}


class FormationRefusal(PermissionError):
    """A refusal with a named ground, readable by the person it concerns."""

    def __init__(self, ground: str, detail: str = "") -> None:
        if ground not in REFUSAL_GROUNDS:
            raise ValueError(f"unknown refusal ground {ground!r}")
        self.ground = ground
        self.detail = detail
        message = REFUSAL_GROUNDS[ground]
        if detail:
            message = f"{message}\n\n{detail}"
        super().__init__(message)

    def to_dict(self) -> Dict[str, str]:
        return {"refused": True, "ground": self.ground,
                "explanation": REFUSAL_GROUNDS[self.ground], "detail": self.detail}


# --------------------------------------------------------------------------
# Instrument registry
# --------------------------------------------------------------------------

LICENCE_CONFIRMED_FREE = "confirmed_free_academic"
LICENCE_AUTHOR_PERMISSION_REQUIRED = "author_permission_required"
LICENCE_UNVERIFIED = "unverified"
LICENCE_EXTERNAL_SCORING = "external_scoring_mandatory"
LICENCE_PAID_CERTIFIED = "paid_certified_scorer"

_ADMINISTRABLE_LICENCES = {LICENCE_CONFIRMED_FREE}


@dataclass(frozen=True)
class InstrumentSpec:
    """Scoring rules and provenance for one instrument. No item text.

    ``subscales`` maps a subscale name to the 1-based item positions it draws on.
    ``reverse_items`` lists 1-based positions scored in reverse. ``n_items`` is the
    full instrument length, used to reject a response vector of the wrong shape.

    ``permits_total`` is false wherever the literature says a total score is
    unsound. The Claremont Purpose Scale is the clear case: Veazey et al. (2023)
    found the beyond-the-self items load poorly on the overall factor and
    recommended treating the three subscales separately.
    """

    id: str
    name: str
    construct: str
    citation: str
    n_items: int
    scale_min: int
    scale_max: int
    subscales: Dict[str, Tuple[int, ...]]
    reverse_items: Tuple[int, ...] = ()
    licence: str = LICENCE_UNVERIFIED
    licence_note: str = ""
    produces_single_rank: bool = False
    permits_total: bool = False
    requires_human_rater: bool = False
    has_population_norms: bool = False
    validated_populations: Tuple[str, ...] = ()
    caveats: Tuple[str, ...] = ()
    obtain_from: str = ""

    def score(self, responses: Sequence[float]) -> Dict[str, "SubscaleScore"]:
        if len(responses) != self.n_items:
            raise ValueError(
                f"{self.id} expects {self.n_items} responses, got {len(responses)}")
        for i, r in enumerate(responses, start=1):
            if not (self.scale_min <= r <= self.scale_max):
                raise ValueError(
                    f"{self.id} item {i}: response {r} outside "
                    f"[{self.scale_min}, {self.scale_max}]")
        out: Dict[str, SubscaleScore] = {}
        for name, positions in self.subscales.items():
            vals = []
            for p in positions:
                v = float(responses[p - 1])
                if p in self.reverse_items:
                    v = self.scale_min + self.scale_max - v
                vals.append(v)
            out[name] = SubscaleScore(
                subscale=name, mean=sum(vals) / len(vals), total=sum(vals),
                n_items=len(vals), scale_min=self.scale_min,
                scale_max=self.scale_max, instrument_id=self.id,
                norms_available=self.has_population_norms)
        return out


@dataclass(frozen=True)
class SubscaleScore:
    subscale: str
    mean: float
    total: float
    n_items: int
    scale_min: int
    scale_max: int
    instrument_id: str
    norms_available: bool

    def percentile(self) -> float:
        raise FormationRefusal(
            "NORMS_ABSENT",
            f"{self.instrument_id} / {self.subscale}: raw mean is "
            f"{self.mean:.2f} on a {self.scale_min}-{self.scale_max} scale.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


#: Registry. Populated below from Session 15's verification pass. Every entry's
#: metadata was confirmed against a live source; entries whose *permission terms*
#: could not be confirmed carry LICENCE_UNVERIFIED and are refused at
#: administration time rather than quietly used.
REGISTRY: Dict[str, InstrumentSpec] = {}


def register_instrument(spec: InstrumentSpec) -> InstrumentSpec:
    REGISTRY[spec.id] = spec
    return spec


# -- needs -----------------------------------------------------------------
register_instrument(InstrumentSpec(
    id="BPNSFS",
    name="Basic Psychological Need Satisfaction and Frustration Scale",
    construct="need",
    citation=("Chen, B., Vansteenkiste, M., Beyers, W., et al. (2015). Basic "
              "psychological need satisfaction, need frustration, and need strength "
              "across four cultures. Motivation and Emotion, 39(2), 216-236. "
              "doi:10.1007/s11031-014-9450-1"),
    n_items=24, scale_min=1, scale_max=5,
    subscales={
        "autonomy_satisfaction": (1, 7, 13, 19),
        "autonomy_frustration": (2, 8, 14, 20),
        "relatedness_satisfaction": (3, 9, 15, 21),
        "relatedness_frustration": (4, 10, 16, 22),
        "competence_satisfaction": (5, 11, 17, 23),
        "competence_frustration": (6, 12, 18, 24),
    },
    licence=LICENCE_CONFIRMED_FREE,
    licence_note=("Center for Self-Determination Theory: academic (non-commercial) "
                  "research use permitted; written permission required for commercial "
                  "use. No fee, no certified scorer."),
    has_population_norms=False,
    validated_populations=("Belgium", "China", "USA", "Peru",
                           "Oman", "Saudi Arabia", "Palestine", "Qatar", "Jordan"),
    caveats=(
        "Murphy et al. (2023, Psychological Assessment 35(2):127-139) argue the "
        "satisfaction/frustration distinction is probably a method artifact of item "
        "keying direction. Do not reason over frustration as a separate construct "
        "without acknowledging this.",
        "Arabic validation (Zayed et al. 2021, BMC Psychology 9:15, N=1082) covers "
        "five Arab countries but NOT Egypt. Some standardised loadings below 0.40.",
        "Subscale alphas as low as .63 are marginal for individual-level feedback.",
    ),
    obtain_from="https://selfdeterminationtheory.org/basic-psychological-need-satisfaction-and-frustration-scale/",
))

# -- meaning / purpose -----------------------------------------------------
register_instrument(InstrumentSpec(
    id="MLQ",
    name="Meaning in Life Questionnaire",
    construct="purpose",
    citation=("Steger, M. F., Frazier, P., Oishi, S., & Kaler, M. (2006). The Meaning "
              "in Life Questionnaire. Journal of Counseling Psychology, 53(1), 80-93. "
              "doi:10.1037/0022-0167.53.1.80"),
    n_items=10, scale_min=1, scale_max=7,
    subscales={"presence_of_meaning": (1, 4, 5, 6, 9),
               "search_for_meaning": (2, 3, 7, 8, 10)},
    reverse_items=(9,),
    licence=LICENCE_CONFIRMED_FREE,
    licence_note=("Free for educational, therapeutic and academic research use. "
                  "Commercial use requires written permission. (c) Michael F. Steger."),
    has_population_norms=False,
    validated_populations=("USA", "Lebanon (8-item variant)"),
    caveats=(
        "No norm tables. The packet's cut-off of 24 has no published statistical "
        "basis, and Steger states the resulting interpretations are 'really only "
        "guesses and should not in any way be considered diagnostic'.",
        "The Arabic version is NOT this instrument. Fekih-Romdhane et al. (2024, BMC "
        "Psychiatry 24) found the 10-item two-factor model fitted inadequately in "
        "Lebanon and dropped items 9 and 10, giving an 8-item version. That removes "
        "the only reverse-scored item and changes the Presence range. Register the "
        "8-item variant separately; do not mix them.",
        "Search is not a 'more is better' scale. High search with low presence is the "
        "interesting combination, not a deficit.",
    ),
    obtain_from="https://www.michaelfsteger.com/?page_id=13",
))

register_instrument(InstrumentSpec(
    id="CPS",
    name="Claremont Purpose Scale",
    construct="purpose",
    citation=("Bronk, K. C., Riches, B. R., & Mangan, S. A. (2018). Claremont Purpose "
              "Scale. Research in Human Development, 15(2), 101-117. "
              "doi:10.1080/15427609.2018.1441577"),
    n_items=12, scale_min=1, scale_max=5,
    subscales={"meaningfulness": (1, 2, 3, 4),
               "goal_orientation": (5, 6, 7, 8),
               "beyond_the_self": (9, 10, 11, 12)},
    licence=LICENCE_UNVERIFIED,
    licence_note=("No permission statement exists on any located source. Items are "
                  "printed in Table A2 of the openly downloadable 2018 paper, but "
                  "there is no affirmative grant of use. Email kcbronk@cgu.edu before "
                  "administering."),
    permits_total=False,
    has_population_norms=False,
    validated_populations=("USA", "Lebanon"),
    caveats=(
        "Do NOT compute a total. Veazey et al. (2023, J. Prevention & Health "
        "Promotion 4(2):200-222) found beyond-the-self items load poorly on the "
        "overall factor and recommended treating the three subscales separately.",
        "Response anchors differ per item ('Not at all clear'->'Extremely clear', "
        "'Almost never'->'Almost all the time', ...). Each item needs its own anchor "
        "set; a single shared Likert scale would be the wrong instrument.",
        "Arabic validation (Noureddine et al. 2025, Frontiers in Psychology 16:1583111) "
        "is Lebanese adolescents, snowball-sampled, no DIF analysis. Not Egypt.",
        "Developed on adolescents; extended to emerging adults (mean age 22-24).",
    ),
    obtain_from="https://edinstruments.org/instruments/youth-purpose-scaleclaremont-purpose-scale",
))

# -- values / will ---------------------------------------------------------
register_instrument(InstrumentSpec(
    id="PVQ-RR",
    name="Portrait Values Questionnaire - Revised",
    construct="will",
    citation=("Schwartz, S. H., & Cieciuch, J. (2022). Measuring the refined theory of "
              "individual values in 49 cultural groups. Assessment, 29(5), 1005-1019. "
              "doi:10.1177/1073191121998760"),
    n_items=57, scale_min=1, scale_max=6,
    subscales={},  # 19 values x 3 items; mapping must be loaded from the ORPC file
    licence=LICENCE_AUTHOR_PERMISSION_REQUIRED,
    licence_note=("ORPC repository, CC BY-NC-ND 3.0, free for educational use. The "
                  "NoDerivatives clause constrains abridging the instrument. The "
                  "item-to-value mapping table was NOT read during verification "
                  "(scholarworks.gvsu.edu returned HTTP 403) and must be obtained "
                  "before this spec is completed."),
    has_population_norms=False,
    validated_populations=("49 cultural groups incl. Oman, Israel Arab"),
    caveats=(
        "subscales is deliberately EMPTY. The 19-value item mapping was not verified, "
        "and guessing it would put an unverified number into a result. Load it from "
        "the ORPC coding instructions before use.",
        "Schwartz prescribes MRAT centering (subtract each respondent's mean across "
        "all 57 items) for structural and profile work.",
        "Coding differs between sources: the Assessment paper uses 1-6, the ORPC essay "
        "uses 0-6. Same labels, different offset. Pick one and stay with it.",
        "Gendered item versions require collecting gender first.",
    ),
    obtain_from="https://scholarworks.gvsu.edu/orpc/vol2/iss2/9/",
))

# -- maturity, as a profile and never as a rank ----------------------------
register_instrument(InstrumentSpec(
    id="3D-WS",
    name="Three-Dimensional Wisdom Scale",
    construct="maturity_profile",
    citation=("Ardelt, M. (2003). Empirical assessment of a three-dimensional wisdom "
              "scale. Research on Aging, 25(3), 275-324. "
              "doi:10.1177/0164027503025003004"),
    n_items=39, scale_min=1, scale_max=5,
    subscales={},  # 14 cognitive / 12 reflective / 13 affective; mapping from author
    licence=LICENCE_AUTHOR_PERMISSION_REQUIRED,
    licence_note=("No fee or restriction stated. Obtained by request: "
                  "'Please contact Dr. Monika Ardelt at ardelt@ufl.edu to obtain an MS "
                  "Word file of the 3D-WS...'. Absence of a stated fee is not a grant "
                  "of permission — get the reply in writing."),
    permits_total=False,
    has_population_norms=False,
    validated_populations=("USA",),
    caveats=(
        "Ardelt's overall score is the average of the three dimension averages, NOT "
        "the average of all 39 items — and this system does not compute it at all. "
        "The published 'strong criterion' for high wisdom is conjunctive (>=4.00 on "
        "EACH dimension), which is a profile test, not a rank.",
        "Measures SELF-PERCEIVED wisdom. Self-report wisdom correlates only modestly "
        "with performance measures; a person low in reflective capacity may be least "
        "able to report it.",
        "Not a stage theory. No developmental sequence is claimed. That is precisely "
        "why it is here and Loevinger is not.",
        "No Arabic validation located.",
    ),
    obtain_from="https://people.clas.ufl.edu/ardelt/home/the-three-dimensional-wisdom-scale-3d-ws",
))

register_instrument(InstrumentSpec(
    id="MEPSI",
    name="Modified Erikson Psychosocial Stage Inventory",
    construct="maturity_profile",
    citation=("Darling-Fisher, C. S., & Leidy, N. K. (1988). Measuring Eriksonian "
              "development in the adult. Psychological Reports, 62(3), 747-754. "
              "doi:10.2466/pr0.1988.62.3.747"),
    n_items=80, scale_min=1, scale_max=5,
    subscales={},  # 8 x 10 items; mapping and scale point-count need author contact
    licence=LICENCE_UNVERIFIED,
    licence_note=("No licensing page, distributor or permission statement located. "
                  "Author-held. Contact Darling-Fisher (University of Michigan School "
                  "of Nursing) for written permission. The response scale point-count "
                  "is also UNVERIFIED — do not assume 5-point."),
    permits_total=False,
    has_population_norms=False,
    validated_populations=("USA nursing samples",),
    caveats=(
        "Measures psychosocial attributes ASSOCIATED WITH Erikson's stages — how much "
        "trust or generativity a person reports — not stage attainment. That is why it "
        "is admissible here.",
        "Total-scale alpha of .97 is suspiciously high and suggests item redundancy or "
        "a strong general factor, which would undercut the eight-theme profile "
        "interpretation. Subscale reliability is 'more variable'.",
        "scale_max is a placeholder pending verification of the response format.",
    ),
    obtain_from="https://journals.sagepub.com/doi/10.2466/pr0.1988.62.3.747",
))


# -- free substitutes adopted in Session 17, after the licence hunt ---------
#
# PVQ-RR and 3D-WS are both permission-gated and both stayed blocked for two
# sessions. Rather than list that as an unfixable pending item, we went looking
# for instruments measuring the same constructs under a licence that already
# permits use. Two were found. Both are registered here as ADMINISTRABLE, and the
# blocked originals stay registered so the substitution is visible rather than
# silent.

register_instrument(InstrumentSpec(
    id="ESS-HVS",
    name="European Social Survey Human Values Scale (PVQ-21)",
    construct="will",
    citation=("S. H. Schwartz, B. Breyer, and D. Danner (2015). Human Values Scale (ESS). "
              "Zusammenstellung sozialwissenschaftlicher Items und Skalen (ZIS). "
              "doi:10.6102/zis234"),
    n_items=21, scale_min=1, scale_max=6,
    subscales={
        "self_direction": (1, 11), "power": (2, 17),
        "universalism": (3, 8, 19), "achievement": (4, 13),
        "security": (5, 14), "stimulation": (6, 15),
        "conformity": (7, 16), "tradition": (9, 20),
        "hedonism": (10, 21), "benevolence": (12, 18),
    },
    # ESS codes 1 = "very much like me" through 6 = "not like me at all", so a LOW
    # raw score means HIGH importance. Every item is reversed here so that a high
    # subscale score means the value matters more, which is what every downstream
    # consumer will assume.
    reverse_items=tuple(range(1, 22)),
    licence=LICENCE_CONFIRMED_FREE,
    licence_note=("Two independent grants. (1) ESS ERIC: 'European Social Survey "
                  "documentation is licensed under CC BY-SA 4.0' — no NonCommercial and no "
                  "NoDerivatives clause, so reproduction and translation are permitted. "
                  "(2) GESIS ZIS: 'The measurement instrument documented here can use free "
                  "of charge for non-commercial research purposes.' Schwartz is a named "
                  "author of the ZIS record, so (2) is the instrument author's own grant."),
    permits_total=False,
    has_population_norms=False,
    validated_populations=("ESS participating countries", "Israel (Arabic)"),
    caveats=(
        "Values are relative, not absolute. Schwartz requires ipsatising: subtract each "
        "respondent's mean across all 21 items (MRAT) from each value score before "
        "comparing profiles. Raw value means without centring are misleading.",
        "Replaces PVQ-RR at a cost: 10 basic values instead of 19 refined ones, from 2-3 "
        "items each. If a downstream distinction needs the refined 19 — societal versus "
        "natural universalism, face versus dominance — this instrument cannot supply it.",
        "An official Arabic version exists, fielded by ESS in Israel and hosted by the "
        "B. I. Cohen Institute, Tel Aviv University. It is Levantine Arabic prepared for "
        "Arab citizens of Israel, NOT Egyptian Arabic. Dialect review and cognitive "
        "pretesting are still required, but this is adaptation rather than translation.",
        "Item wording was verified in condensed form only during the licence hunt. Take "
        "the verbatim two-sentence portrait wording from ZIS Table 1 or the ESS source "
        "questionnaire, not from a secondary source.",
        "Separate male and female item versions exist, which means gender must be "
        "collected before administration.",
    ),
    obtain_from="https://access.gesis.org/zis/524",
))

register_instrument(InstrumentSpec(
    id="ASTI-R",
    name="Adult Self-Transcendence Inventory (revised)",
    construct="maturity_profile",
    citation=("I. Koller, M. R. Levenson, and J. Glueck (2017). What Do You Think You Are "
              "Measuring? A Mixed-Methods Procedure for Assessing the Content Validity of "
              "Test Items and Theory-Based Scaling. Frontiers in Psychology, 8:126. "
              "doi:10.3389/fpsyg.2017.00126"),
    n_items=25, scale_min=1, scale_max=4,
    subscales={
        "self_knowledge_and_integration": (10, 19, 20, 21),
        "peace_of_mind": (1, 5, 9, 22),
        "non_attachment": (3, 6, 8, 12),
        "self_transcendence": (2, 4, 7, 13, 16, 24, 25),
        "presence_and_growth": (11, 14, 15, 17, 18, 23),
    },
    reverse_items=(1, 8, 10, 11, 19, 20, 21, 22, 23, 24),
    licence=LICENCE_CONFIRMED_FREE,
    licence_note=("CC BY 4.0. 'Copyright (c) 2017 Koller, Levenson and Glueck ... The use, "
                  "distribution or reproduction in other forums is permitted, provided the "
                  "original author(s) or licensor are credited.' Michael Levenson, author of "
                  "the original ASTI, is a named co-author and therefore one of the "
                  "copyright holders granting the licence — which is what makes this usable "
                  "where the Brief Wisdom Screening Scale is not."),
    permits_total=False,
    has_population_norms=False,
    validated_populations=("Austria", "USA"),
    caveats=(
        "Construct drift, and it is not small. The ASTI measures SELF-TRANSCENDENCE, not "
        "wisdom. Non-attachment and peace-of-mind overlap Ardelt's reflective and affective "
        "dimensions reasonably, but there is NO analogue of her cognitive dimension — "
        "knowledge of the fundamental limits of knowing. Do not present this as a "
        "substitute for the 3D-WS construct, only for its dimensional form.",
        "The authors argue explicitly against a total score: 'if some items measure "
        "non-attachment while others measure self-knowledge, and these two constructs can "
        "occur independently, then summing up across all items is not informative'.",
        "Item count is contested. The MPsychoR dataset holds 25, the article reports 26 "
        "analysed, and 18- and 34-item versions circulate. This spec assumes 25 and the "
        "subscale assignments sum to 25. Reconcile against the Frontiers PDF before use.",
        "Response scale point-count taken as 4; verify against the article before "
        "administering. If it differs, the reverse-scoring arithmetic changes.",
        "No Arabic validation located.",
    ),
    obtain_from="https://doi.org/10.3389/fpsyg.2017.00126",
))

register_instrument(InstrumentSpec(
    id="LGS",
    name="Loyola Generativity Scale",
    construct="maturity_profile",
    citation=("D. P. McAdams and E. de St. Aubin (1992). A theory of generativity and its "
              "assessment through self-report, behavioral acts, and narration. Journal of "
              "Personality and Social Psychology, 62(6), 1003-1015. "
              "doi:10.1037/0022-3514.62.6.1003"),
    n_items=20, scale_min=0, scale_max=3,
    subscales={},  # single total; reverse-key not verified, so not scoreable here
    licence=LICENCE_CONFIRMED_FREE,
    licence_note=("Author grant, published by McAdams' own Study of Lives Research Group at "
                  "Northwestern: 'Researchers are free to use any and all of these "
                  "instruments - no explicit permission is needed.' This is a permission "
                  "grant rather than a formal licence: undated, unversioned, and silent on "
                  "translation. Email McAdams before translating."),
    permits_total=True,
    has_population_norms=False,
    validated_populations=("USA",),
    caveats=(
        "Covers ONE Eriksonian theme — generativity, stage 7 — against MEPSI's eight, and "
        "yields a single summed total rather than subscales. It is free and clear where "
        "MEPSI is not, and that is the whole of its advantage.",
        "subscales is empty deliberately: six items are reverse-scored but the specific "
        "item numbers were not verified against a primary source, so this instrument "
        "refuses to score rather than guessing the key.",
    ),
    obtain_from="https://sites.northwestern.edu/studyoflivesresearchgroup/instruments/",
))

# -- registered so they can be refused by name, not silently absent --------
for _spec in (
    InstrumentSpec(
        id="WUSCT", name="Washington University Sentence Completion Test",
        construct="ego_development_stage",
        citation=("Hy, L. X., & Loevinger, J. (1996). Measuring Ego Development, "
                  "2nd ed. Lawrence Erlbaum. ISBN 9781138876552"),
        n_items=36, scale_min=0, scale_max=0, subscales={},
        licence=LICENCE_UNVERIFIED, produces_single_rank=True,
        requires_human_rater=True,
        licence_note="Manual is a commercial trade book; reprint terms not located.",
        caveats=("Total Protocol Rating is one overall ego-development stage. The rank "
                 "is the construct.",
                 "Confounded with verbal fluency and verbal IQ; protocol length "
                 "correlates with rating."),
    ),
    InstrumentSpec(
        id="SOI", name="Subject-Object Interview",
        construct="order_of_mind_stage",
        citation=("Lahey, L., Souvaine, E., Kegan, R., Goodman, R., & Felix, S. (1988). "
                  "A Guide to the Subject-Object Interview. Harvard GSE."),
        n_items=0, scale_min=0, scale_max=0, subscales={},
        licence=LICENCE_PAID_CERTIFIED, produces_single_rank=True,
        requires_human_rater=True,
        licence_note=("Minds at Work certification: $4,345 (non-profit $3,025, students "
                      "$2,475), Reliable SOI Scorer +$550."),
        caveats=("60-90 minute interview, not self-report. ~8 hours to score one "
                 "transcript. One position on one ordered scale, delivered with a "
                 "written defence of that single score.",),
    ),
    InstrumentSpec(
        id="MAP", name="Maturity Assessment Profile (SCTi-MAP)",
        construct="ego_development_stage",
        citation="Cook-Greuter, S. MAP. No independent peer-reviewed validation located.",
        n_items=36, scale_min=0, scale_max=0, subscales={},
        licence=LICENCE_PAID_CERTIFIED, produces_single_rank=True,
        requires_human_rater=True,
        licence_note="$1,000 per assessment; two-year scorer certification.",
        caveats=("Reports a 'Center of Gravity (current stage)'. Proprietary manual, "
                 "closed scoring, no locatable independent validation of the full "
                 "current instrument.",),
    ),
    InstrumentSpec(
        id="DIT-2", name="Defining Issues Test 2",
        construct="moral_judgement_development",
        citation=("Rest, J. R., Narvaez, D., Thoma, S. J., & Bebeau, M. J. (1999). "
                  "DIT2. Journal of Educational Psychology, 91(4), 644-659. "
                  "doi:10.1037/0022-0663.91.4.644"),
        n_items=60, scale_min=1, scale_max=5, subscales={},
        licence=LICENCE_EXTERNAL_SCORING, produces_single_rank=False,
        licence_note=("$5.50 per participant. 'The DIT2 is provided only with the "
                      "Center's scoring service (the DIT2 cannot be scored by the "
                      "researcher).'"),
        caveats=("Mandatory external scoring sends participant responses to a third "
                 "party, outside the consent recorded here.",
                 "Its consolidated/transitional distinction — saying a person is "
                 "BETWEEN framings rather than forcing a point estimate — is worth "
                 "borrowing as an idea even though the instrument is refused.",),
    ),
):
    register_instrument(_spec)
del _spec


# --------------------------------------------------------------------------
# The person's own statements
# --------------------------------------------------------------------------

@dataclass
class DeclaredAttribute:
    """Something the person said about themselves. The only route in."""
    key: str
    value: Any
    declared_at: str = field(default_factory=_now)
    evidence_id: str = ""
    contested_by: List[str] = field(default_factory=list)
    retracted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Override:
    """A correction from the person. Wins for display; explains nothing away."""
    key: str
    value: Any
    reason: str = ""
    at: str = field(default_factory=_now)
    supersedes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Administration:
    instrument_id: str
    responses: Tuple[float, ...]
    scores: Dict[str, SubscaleScore]
    administered_at: str = field(default_factory=_now)
    self_completed: bool = True
    population: str = ""
    population_validated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "administered_at": self.administered_at,
            "self_completed": self.self_completed,
            "population": self.population,
            "population_validated": self.population_validated,
            "scores": {k: v.to_dict() for k, v in self.scores.items()},
        }


# --------------------------------------------------------------------------
# The model
# --------------------------------------------------------------------------

class FormationModel:
    """What a person has told us, what it does not add up to, and what we refuse.

    Every public method that could produce a claim the person did not make raises
    ``FormationRefusal`` with a named ground. Those methods exist rather than being
    absent so that the refusal is discoverable: calling ``eventual_purpose()`` and
    reading why it declines teaches more than finding no such method.
    """

    def __init__(self, subject: str,
                 deployment: Optional[DeploymentContext] = None,
                 ledger: Optional[Any] = None) -> None:
        self.subject = subject
        self.deployment = deployment
        self.ledger = ledger
        self._declared: Dict[str, List[DeclaredAttribute]] = {}
        self._overrides: Dict[str, Override] = {}
        self._administrations: List[Administration] = []
        self._licence_confirmations: Dict[str, str] = {}

    # -- the only two ways in ---------------------------------------------

    def declare(self, key: str, value: Any, evidence_id: str = "") -> DeclaredAttribute:
        """Record something the person said about themselves."""
        attr = DeclaredAttribute(key=key, value=value, evidence_id=evidence_id)
        self._declared.setdefault(key, []).append(attr)
        return attr

    def confirm_licence(self, instrument_id: str, evidence: str) -> None:
        """Record written permission obtained from an instrument's author.

        ``evidence`` must be a non-empty description of the permission — who granted
        it, when, and in what form. A boolean would let this be set by accident; a
        sentence has to be written on purpose. Same reasoning as
        ``DeploymentContext.safety_exception_basis``.
        """
        if instrument_id not in REGISTRY:
            raise KeyError(f"unknown instrument {instrument_id!r}")
        if not evidence.strip():
            raise ValueError(
                "confirm_licence() requires written evidence of permission, not a "
                "flag. Record who granted it, when, and in what form.")
        spec = REGISTRY[instrument_id]
        if spec.requires_human_rater or spec.licence in (
                LICENCE_PAID_CERTIFIED, LICENCE_EXTERNAL_SCORING):
            raise FormationRefusal(
                "RATER_REQUIRED" if spec.requires_human_rater else "EXTERNAL_SCORING",
                f"{instrument_id}: {spec.licence_note}")
        self._licence_confirmations[instrument_id] = evidence.strip()

    def administer(self, instrument_id: str, responses: Sequence[float],
                   self_completed: bool = True, population: str = "",
                   at: Optional[str] = None) -> Administration:
        """Enter an instrument the person completed themselves."""
        if instrument_id not in REGISTRY:
            raise KeyError(f"unknown instrument {instrument_id!r}")
        spec = REGISTRY[instrument_id]

        if not self_completed:
            raise FormationRefusal("NOT_SELF_COMPLETED", f"instrument={instrument_id}")

        if spec.requires_human_rater:
            raise FormationRefusal("RATER_REQUIRED",
                                   f"{spec.name}: {spec.licence_note}")
        if spec.licence == LICENCE_EXTERNAL_SCORING:
            raise FormationRefusal("EXTERNAL_SCORING",
                                   f"{spec.name}: {spec.licence_note}")
        if spec.produces_single_rank:
            raise FormationRefusal(
                "GLOBAL_RANKING",
                f"{spec.name} scores to a single position for a person. "
                f"{spec.caveats[0] if spec.caveats else ''}")

        if (spec.licence not in _ADMINISTRABLE_LICENCES
                and instrument_id not in self._licence_confirmations):
            raise FormationRefusal(
                "UNLICENSED_INSTRUMENT",
                f"{spec.name} — licence status {spec.licence!r}. "
                f"{spec.licence_note}\nObtain from: {spec.obtain_from}")

        self._require_psychometric_stream(at or _now())

        if not spec.subscales:
            raise FormationRefusal(
                "UNLICENSED_INSTRUMENT",
                f"{spec.name} has no verified item-to-subscale mapping in this "
                f"registry, so responses cannot be scored without inventing the "
                f"mapping. Load it from {spec.obtain_from} and register a completed "
                f"spec.")

        scores = spec.score(responses)
        validated = bool(population) and population in spec.validated_populations
        admin = Administration(
            instrument_id=instrument_id, responses=tuple(float(r) for r in responses),
            scores=scores, self_completed=True, population=population,
            population_validated=validated,
            administered_at=at or _now())
        self._administrations.append(admin)
        return admin

    def _require_psychometric_stream(self, when: str) -> None:
        if self.deployment is not None:
            if self.deployment.context not in (SELF, CONSENTED_INDIVIDUAL):
                raise FormationRefusal(
                    "DEPLOYMENT_CONTEXT",
                    f"declared context: {self.deployment.context!r}")
        if self.ledger is not None:
            granted = self.ledger.streams_granted_at(self.subject, when)
            if PSYCHOMETRIC_STREAM not in granted:
                raise FormationRefusal(
                    "UNCONSENTED_INSTRUMENT",
                    f"streams under grant at {when}: {sorted(granted) or 'none'}")

    # -- what the person outranks -----------------------------------------

    def override(self, key: str, value: Any, reason: str = "") -> Override:
        """The person corrects the model. They win, immediately.

        The contradicted statements are marked contested and stay inspectable. They
        are not deleted, because deleting them would remove the person's ability to
        see what the system had thought and why.
        """
        prior = self._declared.get(key, [])
        ov = Override(key=key, value=value, reason=reason,
                      supersedes=[a.declared_at for a in prior if not a.retracted])
        for a in prior:
            if not a.retracted:
                a.contested_by.append(ov.at)
        self._overrides[key] = ov
        return ov

    def current(self, key: str) -> Any:
        """What the model shows for a key. An override always wins."""
        if key in self._overrides:
            return self._overrides[key].value
        live = [a for a in self._declared.get(key, []) if not a.retracted]
        return live[-1].value if live else None

    def evidence_behind(self, key: str) -> Dict[str, Any]:
        """Everything the model holds for a key, including what the person overrode."""
        return {
            "key": key,
            "displayed": self.current(key),
            "overridden_by_person": key in self._overrides,
            "override": self._overrides[key].to_dict() if key in self._overrides else None,
            "declarations": [a.to_dict() for a in self._declared.get(key, [])],
        }

    # -- what can be shown -------------------------------------------------

    def profile(self) -> Dict[str, Any]:
        """Subscale scores across everything the person completed. Never a total."""
        out: Dict[str, Any] = {"subject": self.subject, "dimensions": {}, "caveats": []}
        for admin in self._administrations:
            spec = REGISTRY[admin.instrument_id]
            for name, sc in admin.scores.items():
                out["dimensions"][f"{admin.instrument_id}:{name}"] = {
                    "mean": round(sc.mean, 3), "n_items": sc.n_items,
                    "scale": [sc.scale_min, sc.scale_max],
                    "construct": spec.construct,
                    "norms_available": sc.norms_available,
                    "population_validated": admin.population_validated,
                }
            out["caveats"].extend(f"{spec.id}: {c}" for c in spec.caveats)
        out["no_total_score"] = (
            "No overall score is computed. Each dimension stands on its own; "
            "collapsing them would produce the single rank this system refuses.")
        return out

    def trajectory(self, key: str) -> Dict[str, Any]:
        """How a declared attribute has moved, with the evidence for each point."""
        points = [
            {"at": a.declared_at, "value": a.value, "evidence_id": a.evidence_id,
             "contested": bool(a.contested_by), "retracted": a.retracted}
            for a in self._declared.get(key, [])
        ]
        return {
            "key": key, "points": points, "n": len(points),
            "changed": len({p["value"] for p in points
                            if isinstance(p["value"], (str, int, float, bool))}) > 1,
            "interpretation": (
                "This is a record of what was said and when. It is not a claim about "
                "why it changed, and it is not a direction of travel."),
        }

    def instrument_trajectory(self, instrument_id: str, subscale: str) -> Dict[str, Any]:
        """Repeated administrations of one subscale, as points with dates."""
        pts = [{"at": a.administered_at, "mean": round(a.scores[subscale].mean, 3)}
               for a in self._administrations
               if a.instrument_id == instrument_id and subscale in a.scores]
        note = ("Two or more administrations are required before change can be shown."
                if len(pts) < 2 else
                "Change between administrations is not evidence of development; it "
                "may be measurement error, mood, or regression to the mean. No "
                "instrument here publishes a reliable change index.")
        return {"instrument_id": instrument_id, "subscale": subscale,
                "points": pts, "n": len(pts), "interpretation": note}

    def open_questions(self) -> List[Dict[str, str]]:
        """What the person has not told us — offered as questions, not deficits.

        This is the honest answer to "what do they still need". It returns things
        the model does not know, phrased as invitations, and never as a judgement
        about what is missing in the person.
        """
        qs: List[Dict[str, str]] = []
        constructs_held = {REGISTRY[a.instrument_id].construct
                           for a in self._administrations}
        for construct, prompt in (
            ("need", "What would you say you need most at the moment, and from whom?"),
            ("will", "Which of the things you care about would you not give up?"),
            ("purpose", "Is there something you are working toward, or are you looking?"),
            ("maturity_profile", "Where do you think you have changed most in the last few years?"),
        ):
            if construct not in constructs_held:
                qs.append({"construct": construct, "question": prompt,
                           "why": "Nothing in the model speaks to this yet."})
        for key in ("background", "upbringing", "origin"):
            if key not in self._declared:
                qs.append({"construct": "background",
                           "question": f"Would you like to tell me about your {key}?",
                           "why": ("Declared-only. The system cannot and will not "
                                   "infer this — if you would rather not say, it "
                                   "stays unknown.")})
        return qs

    # -- the refusals, callable so they can be read ------------------------

    def infer_background(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("INFERRED_ORIGIN")

    def infer_origin(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("INFERRED_ORIGIN")

    def maturity_level(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("GLOBAL_RANKING")

    def overall_maturity(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("GLOBAL_RANKING")

    def developmental_stage(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("GLOBAL_RANKING")

    def what_they_still_need(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("PRESCRIPTIVE_DEFICIT")

    def deficits(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("PRESCRIPTIVE_DEFICIT")

    def eventual_purpose(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("PURPOSE_ATTRIBUTION")

    def life_purpose(self, *_a: Any, **_k: Any) -> None:
        raise FormationRefusal("PURPOSE_ATTRIBUTION")

    # -- export ------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "declared": {k: [a.to_dict() for a in v] for k, v in self._declared.items()},
            "overrides": {k: v.to_dict() for k, v in self._overrides.items()},
            "administrations": [a.to_dict() for a in self._administrations],
            "profile": self.profile(),
            "open_questions": self.open_questions(),
            "refusals_available": sorted(REFUSAL_GROUNDS),
            "note": (
                "This model contains only what the subject declared or self-completed. "
                "It contains no inferred background, no maturity rank, no prescribed "
                "deficit and no attributed purpose. Those are refused by construction "
                "and the refusals are checkable — see invariants.check_xi_declared_only()."
            ),
        }
