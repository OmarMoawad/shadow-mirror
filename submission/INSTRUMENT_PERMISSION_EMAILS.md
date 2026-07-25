# Four permission emails

Send these before the formation model touches a real participant. Each is short on purpose —
instrument authors receive a lot of these, and the ones that get answered say what you want, what you
will do with it, and what you will not do with it, in that order.

**Before sending, fill in:** your corresponding email address, and your department or programme at AUC
if you have one. Both are marked `[…]`. Do not send with the placeholders in.

A note on the fourth: it is not a permission request. The PVQ-RR is already free under a Creative
Commons licence; what is missing is a file that would not download.

---

## 1 — Claremont Purpose Scale

**To:** kcbronk@cgu.edu
**Subject:** Permission to use the Claremont Purpose Scale in a non-commercial research study

Dear Dr Bronk,

I am a researcher at The American University in Cairo working on a software architecture for
reflective human–AI interaction. Part of the system lets a person voluntarily complete validated
self-report instruments and then reason over their own answers — it does not infer psychological
constructs from behaviour, and it is designed specifically to refuse doing so.

I would like to include the Claremont Purpose Scale, and I could not find a permission statement for
it, so I am asking directly rather than assuming.

What I would do: administer the 12 items as published, score the three subscales separately (following
Veazey et al.'s 2023 recommendation against a total score), and cite the 2018 *Research in Human
Development* paper. What I would not do: redistribute the items with the software, modify or abridge
the scale, or use it commercially. The software ships scoring rules and citations only; the items
would be supplied at deployment by whoever holds permission to use them.

If you would prefer the Arabic version, I would be glad to hear whether the items from Noureddine et
al. (2025) can be made available — our participants would be Egyptian, and I am aware that the
Lebanese validation does not straightforwardly transfer.

Would you be willing to grant permission for non-commercial academic use? I am happy to share results
if that would be useful.

With thanks,
Omar Moawad
The American University in Cairo
[corresponding email]

---

## 2 — Three-Dimensional Wisdom Scale

**To:** ardelt@ufl.edu
**Subject:** Request for the 3D-WS for a non-commercial research study

Dear Dr Ardelt,

I am writing to request a copy of the Three-Dimensional Wisdom Scale, following the instruction on
your webpage to contact you directly.

I am a researcher at The American University in Cairo building an architecture for reflective human–AI
interaction. It lets a person voluntarily complete self-report instruments and reason over their own
responses; it does not infer anything about them from behaviour.

The 3D-WS is in the design for a specific reason worth stating. I went looking for a way to represent
developmental maturity without collapsing a person into a single rank, and found that the stage
instruments will not permit it — the ordered position is the construct, not a summary of it. The 3D-WS
is the instrument I found that reports dimensions rather than a stage, and whose own criterion for
high wisdom is conjunctive across the three dimensions rather than an average. That distinction is
doing real work in the design, and I wanted you to know it is the reason for the request.

I would score the three dimensions separately and would not compute or report an overall wisdom score.
The items would not be redistributed with the software, which ships scoring rules and citations only.
Use is non-commercial and academic.

Could you send the instrument, and let me know of any conditions attached? I would also welcome your
view on whether an Arabic administration is advisable — I have not been able to locate an Arabic
validation, and I would rather say so in the write-up than imply coverage that does not exist.

With thanks,
Omar Moawad
The American University in Cairo
[corresponding email]

---

## 3 — Modified Erikson Psychosocial Stage Inventory

**To:** Cynthia S. Darling-Fisher, University of Michigan School of Nursing
*(find the current address via the School of Nursing directory — I did not want to guess at it)*
**Subject:** Permission to use the MEPSI in a non-commercial research study

Dear Dr Darling-Fisher,

I am a researcher at The American University in Cairo working on a system that lets people complete
validated self-report instruments and reflect on their own responses. I would like to include the
Modified Erikson Psychosocial Stage Inventory, and I could not locate a distributor or a permission
statement, so I am writing to you directly.

The MEPSI is in the design because it measures the psychosocial attributes associated with Erikson's
stages rather than claiming stage attainment. That distinction matters to us: the system is built to
refuse producing a single developmental level for a person, and an instrument that reports eight
themes rather than one position is compatible with that commitment where a stage instrument would not
be.

Two practical questions, if you have time for them:

1. Would you grant permission for non-commercial academic use? The items would not be redistributed
   with the software — it ships scoring rules and citations only.
2. Could you confirm the response format? I have seen the instrument described with different numbers
   of scale points and I do not want to hard-code the wrong one. I would rather ask than assume.

I would also value your view on the reported total-scale alpha of .97. It reads high enough to suggest
a strong general factor, which would bear on whether the eight subscales can carry an interpretation
independently — which is exactly how I would want to use them.

With thanks,
Omar Moawad
The American University in Cairo
[corresponding email]

---

## 4 — PVQ-RR coding instructions *(not a permission request)*

**To:** the corresponding author listed on the ORPC repository entry, or Prof. Shalom H. Schwartz
**Subject:** PVQ-RR coding and analysis instructions — repository files returning HTTP 403

Dear Professor Schwartz,

I am a researcher at The American University in Cairo, using the revised Portrait Values Questionnaire
under the ORPC repository's Creative Commons licence.

I am not writing to request permission — the licence covers what I need. The problem is access: the
supplementary files on `scholarworks.gvsu.edu`, including the PVQ-RR coding and analysis instructions
that carry the item-to-value mapping, return HTTP 403 to automated retrieval, and I have not been able
to obtain the mapping table.

I would rather ask you for it than reconstruct it. Our software refuses to score an instrument whose
item mapping has not been verified against a primary source, precisely so that no unverified number
ends up in a participant's result, and the PVQ-RR is currently registered in that refusing state.

Could you point me to a working copy of the coding instructions, or send the mapping directly? I would
also be grateful to know whether an Arabic version validated in an Egyptian sample exists — I can see
that Oman and Israel Arab groups are in the 49-group psychometrics, and I would like to describe the
coverage accurately rather than generously.

With thanks,
Omar Moawad
The American University in Cairo
[corresponding email]

---

## After a reply arrives

Record it in the model rather than in your memory. The licence gate takes written evidence, not a flag:

```python
m.confirm_licence(
    "CPS",
    "Email from K. C. Bronk, 14 Aug 2026, granting non-commercial academic use; "
    "no redistribution of items. Saved at docs/permissions/cps-bronk-2026-08-14.eml",
)
```

An empty string raises. That is deliberate — a boolean can be set by accident, and a sentence has to
be written on purpose.

If an author declines, or does not reply, the instrument stays refused and the study proceeds without
it. That is a worse study and an honest one, and it is the right trade.
