# Shadow Mirror — Session 18: The Route A Pipeline and the AUC IRB Packet

**Author of record:** Omar Moawad · **The American University in Cairo** · **Session date:** 25 July 2026
**Deliverables:** `shadow_mirror/route_a.py`, `tests/test_route_a.py` (28 tests), `AUC_IRB_PACKET.md`,
package v1.3.0.

The final session of the programme. Route A was chosen: a secondary analysis of three existing corpora,
no new participants, alongside a written IRB protocol for the primary study that would be needed to
test the claim no public data can reach.

---

## 1. The loaders, and why they are written the way they are

Schemas were read from the **actual archives**, not from the papers describing them. That distinction
earned its keep immediately, because **all three corpora contradict their own documentation**:

- **FOODEEG's** `task-pairedchoice_beh.json` documents 87 trials per block. That is true for `sub-006`
  and false for the other 116 participants, who have 60.
- **Urban Appraisal's** `dataset_description.json` says CC0 and its README says CC BY 4.0. Its sidecar
  spells a scale key differently from the data file.
- **BIRAFFE2's** *Scientific Data* paper prints `GAME-EXP-PAST-YEAR`; the file spells it
  `GAME-EXO-PAST-YEAR`.

So the files are the authority, and a schema mismatch raises `SchemaError` rather than warning. The
error message prints expected columns, found columns, and the difference, because the realistic time to
discover this is six months after someone re-downloaded a newer version.

### 1.1 Three design rules, each of which cost functionality

**A loader that cannot verify its schema refuses.** Not a warning. The failure mode being prevented is
a silent misread, which produces numbers rather than errors.

**Undocumented coding is a refusal, not a default.** This is the important one, and it concerns Urban
Appraisal. The archive gives anchor wording — *"valence: happy – unhappy"* — but **nowhere states which
end of the numeric scale is which**. No `Levels` in the sidecar, nothing in the README, nothing in
`participants.json`. A wrong polarity **does not fail**. It inverts every result that depends on sign
and looks entirely normal. So `load_urban_appraisal` raises `PolarityUnknown` until a direction is
passed explicitly, and records what was assumed in the returned report:

```python
load_urban_appraisal(root, polarity={"valence": +1, "arousal": +1})
```

**No data means no numbers.** Every analysis entry point returns a structured `no_data` record rather
than a plausible one, and a test asserts it. Nothing in the module can produce a figure without the
archives present.

### 1.2 Nine file traps, each with a test

| Trap | Consequence if unhandled |
|---|---|
| BIRAFFE2 is semicolon-delimited | A default comma read yields one column and no error |
| BIRAFFE2 abstention tokens are `''`, `NaN` **and** `None` | Abstentions silently become missing data |
| FOODEEG Session 1 uses Windows path separators, Session 2 POSIX, for the same images | `os.path.basename` will not strip a backslash on POSIX; the cross-session join fails |
| Every FOODEEG `.tsv` has a byte-identical `.csv` twin | A glob on `sub-*/beh/*` doubles every row |
| FOODEEG encodes the choice twice — `respKey` and `stimChosen_path` | Disagreement between them means the file is not what we think; the loader raises |
| FOODEEG applied **no RT timeout** — real values reach 66.7 s | Untrimmed outliers dominate any latency analysis |
| Urban Appraisal ratings live inside a semicolon-delimited string in `events.tsv` | There is no ratings file; a loader expecting one finds nothing |
| Urban Appraisal's beauty scale contains a raw `0x1A` byte, and the sidecar drops the character entirely | An exact-literal match finds neither spelling |
| Urban Appraisal's `sub-51` uses English scale labels where 62 others use German | German-only matching silently drops 336 of that participant's ratings |

### 1.3 What the analyses can and cannot establish

**Can:** preference contradiction (FOODEEG records a rating and a later choice on the same items, so a
choice can disagree with the person's own stated preference); abstention behaviour (BIRAFFE2 records
when a participant left the rating widget at its default rather than moving it — a person declining to
answer, recorded as such, which is the closest thing to a real abstention signal in any public
affective corpus); order-invariance against real observations rather than generated ones.

**Cannot:** the threat confound. The contradiction result carries its own disclaimer in the returned
object:

> *A contradiction here is a choice that disagrees with the person's own earlier rating of the same
> item. It is NOT evidence of a hidden preference and NOT evidence of compliance under pressure — this
> corpus contains no manipulation that could separate those.*

A test asserts that disclaimer is present, and another asserts that no corpus in the registry claims to
support the threat-confound claim.

---

## 2. The IRB packet

A complete draft protocol for the primary study: a two-session, within-subjects design where Session 1
collects private ratings and Session 2 collects forced choices under three social contexts — private,
observed, and a displayed majority — with EDA, ECG and response latency throughout. The discriminating
comparison is between contradictions arising without social pressure (candidate hidden preference) and
contradictions arising only under a manufactured majority with elevated arousal and longer latency
(candidate compliance).

Everything requiring a fact only the author holds is marked `[YOU]` and left blank. I will not invent a
supervisor, a sample size, a start date, or a committee that has not met.

### Three findings that change the sequence

**Expect full board review, not expedited.** AUC's expedited category covers "behaviour/cognition
studies without subject manipulation or stress". §3 of the protocol is a social-pressure manipulation
with incomplete disclosure. Submitting as expedited would cost a review cycle.

**The PDPL licence and the CAPMAS permit must start before the IRB, not after.** The study processes
psychological *and* biometric data, which under Law 151/2020 Art. 12 requires a licence from the
Personal Data Protection Centre in addition to written explicit consent — with no research exemption.
Separately, AUC's own IRB page warns that its approval does not imply CAPMAS approval and that the IRB
"is not equipped to handle matters related to CAPMAS".

**Only key destruction takes the dataset out of PDPL scope.** Pseudonymised data remains personal data.
Until the code-to-identity key is destroyed, every obligation continues to apply. That makes the
key-destruction milestone the most consequential line in the data management plan.

### Two things written deliberately

**The deception is stated plainly rather than buried in a methods paragraph**, with the argument for why
no alternative design preserves the construct, what participants are told in advance, and why the risk
is low. Consent obtained at the start is treated as insufficient: at debriefing, after the true design
is explained, participants are asked **again** whether their data may be retained, and one who declines
has it destroyed and keeps full compensation.

**A pre-committed null-result statement.** The study tests an assumption the analysing software already
makes, which is a real confirmation-bias risk. The protocol commits in advance that if the
physiological and latency channels do *not* separate the two mechanisms, that finding is reported as
prominently as a positive one — and notes that such a result would be more valuable than the one we
hope for, because the architecture's headline safety result depends on those channels carrying signal.

---

## 3. State

| | |
|---|---|
| Package | **v1.3.0** — 709 collected, **707 passed**, 2 xfailed |
| New module | `route_a.py` — 3 loaders, 3 analyses, 12 documented corpus quirks |
| New tests | 28, against fixtures reproducing the real file structure |
| Sessions | **18 of 18 complete** |

**What sits with the author:** three dataset downloads (two are small — BIRAFFE2 needs only its 35 MB
procedure archive, Urban Appraisal only its 16 MB git metadata); the Urban Appraisal rating polarity,
from the BeMoBIL analysis code; CITI certification and a supervisor if submitting as a graduate
student; and two remaining instrument permissions.

The pipeline runs the moment the archives arrive. It will not run before then, and it will not pretend
to.
