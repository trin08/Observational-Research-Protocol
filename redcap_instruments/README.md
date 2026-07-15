# REDCap Instruments — RCHOC INQ-10 Study

Two scripts build the two CSVs that together make up the full REDCap
project. Upload both, in either order — REDCap doesn't care, but the
combined project isn't complete until both are in.

- `generate_data_dictionary.py` — every study field except INQ-10.
- `generate_inq10_instrument.py` — the INQ-10 itself: pre-disclosure
  text as a descriptive field, then the 10-item matrix.

They're split because INQ-10 needs its own pre-disclosure text and
matrix layout, and folding it into the general dictionary would mean
carrying that layout logic alongside demographics and screening
fields for no reason.

## Usage

```bash
python3 generate_data_dictionary.py --output rchoc_data_dictionary.csv
python3 generate_inq10_instrument.py --output inq10_instrument.csv
```

No dependencies beyond the standard library for either script.

## What's in the data dictionary

- **demographics** — subject_id, age, biological sex, gender,
  race/ethnicity, insurance type, ZIP code
- **screening_triage** — ASQ result, bypass reason, presenting
  complaint, track, ESI level, C-SSRS triage result
- **clinical_assessments** — PHQ-A total, GAD-7 total, C-SSRS
  Ideation Severity Score, BSSA tier, medication/substance-risk flag,
  comorbid diagnosis, ICD-10
- **chart_abstraction_qc** — second-abstractor fields for the 10%
  dual-abstraction inter-rater reliability check

## What's in the INQ-10 instrument

`inq10_item_1` through `inq10_item_10`, preceded by a `descriptive`
field (`inq10_disclosure`) that carries the pre-disclosure text.
Item wording and order come straight from the protocol's own
appendix (Table 1, reproducing Hill et al., 2015) — not paraphrased,
not pulled from a screenshot somewhere. The order matches the
original-item numbering `config.py` assumes by default (1, 3, 9, 12,
14, 17, 19, 20, 21, 24), so `INQ10_FIELD_TO_ORIGINAL_ITEM` doesn't
need touching as long as the live REDCap build keeps this order. The
source table only says which items belong in the INQ-10 and which
are reverse-scored — it doesn't dictate field order — so if items
get reordered in the Online Designer after upload, that mapping has
to be updated to match.

Items 17, 19, and 24 (positions 6, 7, 10 in the survey) are
positively worded and get reverse-scored in `analyze_redcap.py`, not
in the instrument itself — the survey shows every item in its
natural wording, since flipping wording on the page would just
confuse someone moving through a matrix.

## Why the field names and choice codes matter

Every field name matches `config.COLUMNS` in the analysis pipeline
exactly — `biological_sex`, `med_risk_flag`, `phqa_total`,
`asq_result`, and so on — and the INQ-10 fields match
`config.INQ10_ITEM_COLUMNS` exactly. Build the REDCap project from
these two files and `analyze_redcap.py` reads the resulting export
with zero edits to `config.py`. Rename anything in REDCap later and
`config.COLUMNS` needs the same update, or the two drift apart.

Choice codes are picked to match what the pipeline expects, not just
what's convenient in REDCap. `asq_result` is coded
`positive`/`negative`, not `1`/`0`, because `analyze_redcap.py` checks
for the literal string `"positive"`. Recode that in REDCap later
without touching the pipeline and the check silently stops matching
anything — every row ends up looking ASQ-negative.

## Two deliberate deviations from a literal reading of the protocol

- **No date-of-birth field.** The protocol's Medical Record Review
  list includes DOB, but DOB is a direct identifier, and the protocol
  is equally explicit that no direct identifiers enter the REDCap
  analysis database. This dictionary collects `age` directly instead.
  If the abstraction workflow needs DOB to compute age, do that
  computation outside REDCap — alongside the Master Linking Log step
  — and only enter the derived age here.
- **`comorbid_dx` is single-select**, not checkbox, even though real
  patients can carry more than one documented diagnosis. This matches
  what the pipeline (and `generate_synthetic_data.py`) actually
  consume — a single categorical column. Add a checkbox field for
  chart documentation if multiple comorbidities need capturing, but
  keep this single-select field as the one the pipeline reads,
  populated with the clinically primary diagnosis.

## Pre-disclosure text and the consent model

Delivered as a `descriptive` field immediately before the item
matrix, per the protocol's notice-and-continuation model — the
participant is told the following questions are for research,
separate from clinical care, and continuing past that screen is their
decision to proceed. It's not a required field and takes no input.

All 10 items are marked required, which forces an answer before
REDCap lets someone move to the next page — but that does **not**
stop someone from closing the survey mid-way, which is what the
protocol actually promises ("may decline or stop... at any point
without any effect on their clinical care"). Partial responses from a
stopped survey are excluded per protocol, and `analyze_redcap.py`
already requires at least one non-null INQ-10 item to include a row
in the Primary Analytic Sample, so a fully-blank partial response
won't get picked up regardless.

## After generating both

1. REDCap → Project Setup → Data Dictionary → Upload — both CSVs, in
   either order.
2. In the Online Designer, confirm the INQ-10 matrix renders as
   expected and the disclosure text sits above it, not inline within
   the grid.
3. Spot-check branching logic (`bypass_reason`, `track`,
   `cssrs_triage_result`, and the PHQ-A/GAD-7/C-SSRS gate on
   `[asq_result] = 'positive'`) against the actual clinical workflow
   before going live. It's written to match the protocol's Figure 1
   diagram, but REDCap's branching syntax is picky about exact value
   matches.
4. If Spanish/Mandarin translations are needed per the protocol's
   Language Limitation section, add them through REDCap's
   Multi-Language Management module rather than duplicating fields —
   `generate_inq10_instrument.py` only builds the English base
   instrument.

## Reference

Hill, R., Rey, Y., Marin, C. E., Sharp, C., Green, K. L., & Pettit, J.
(2015). Evaluating the Interpersonal Needs Questionnaire: Comparison
of the reliability, factor structure, and predictive validity across
five versions. *Suicide & Life-Threatening Behavior, 45*(3), 302-314.
