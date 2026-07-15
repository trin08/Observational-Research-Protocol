<img width="1690" height="1489" alt="image" src="https://github.com/user-attachments/assets/84432df5-fede-4083-968e-d2aed4e23007" /># Observational-Research-Protocol
# RCHOC INQ-10 Study

Screening and analysis code for an observational protocol at the
Rady Children's Hospital / CHOC-affiliated ED (RCHOC) testing whether
INQ-10 Perceived Burdensomeness (PB) and Thwarted Belongingness (TB)
subscale scores explain unique variance in C-SSRS Ideation Severity
Score among 12-21 year olds screened in the ED, beyond age, sex,
medication/substance-use status, PHQ-A, and C-SSRS triage result.

The study is a Waiver of Consent design layered on top of the ED's
existing ASQ-based suicide screening workflow — patients aren't
recruited separately; positive-ASQ patients already routed into
standard psychiatric follow-up get the INQ-10 added as a research
instrument alongside the assessments they're already receiving.

## Repo layout

```
rchoc-inq10-study/
├── figures/
│   ├── generate_workflow_diagram.py   # builds the diagram below
│   └── RCHOC_ED_Study_Workflow_v7.png
├── redcap_instruments/
│   ├── generate_data_dictionary.py    # every field except INQ-10
│   ├── generate_inq10_instrument.py   # INQ-10 disclosure + matrix
│   └── README.md
└── analysis/
    ├── config.py                      # column names + scoring key
    ├── power_analysis.py              # run this first
    ├── generate_synthetic_data.py     # fabricated test CSV
    ├── analyze_redcap.py              # the pipeline
    ├── ordinal_logit.py               # proportional-odds from scratch
    ├── supplementary_stats.py         # hierarchical OLS + PO diagnostic
    └── README.md
```

## Study workflow

<img width="1690" height="1489" alt="image" src="https://github.com/user-attachments/assets/4a5e1a1a-e433-44ff-b420-a6df162e85b6" />


Patients 12-21 admitted to the RCHOC ED get the ASQ at universal
triage unless a documented bypass reason applies (altered mental
status, ESI acuity 1, acute trauma, or a cognitive disability that
makes the ASQ unadministerable). A negative ASQ exits the patient
from the study. A positive ASQ routes the patient into whichever
clinical track matches their presenting complaint:

- **Behavioral Health Track** — PHQ-A/GAD-7 as standard clinical
  care, then INQ-10 as the research add-on.
- **Physical Health Track** — PHQ-A/GAD-7 are *not* standard of care
  here, so the research protocol bundles them in alongside INQ-10.

Both tracks converge on a clinician follow-up: BSSA interview to a
C-SSRS result, and a debrief on the study's purpose where clinically
appropriate. INQ-10 carries a real-time safety trigger in both tracks
regardless of which track a patient came in through.

## Quick start

```bash
pip install numpy pandas scipy scikit-learn

cd redcap_instruments
python3 generate_data_dictionary.py --output rchoc_data_dictionary.csv
python3 generate_inq10_instrument.py --output inq10_instrument.csv
# upload both CSVs to REDCap: Project Setup -> Data Dictionary -> Upload

cd ../analysis
python3 generate_synthetic_data.py --output synth.csv --n 500
python3 analyze_redcap.py --input synth.csv --output results/
```

Once real data collection starts, edit `analysis/config.py` to match
the live REDCap export's column names (it ships with `COLUMNS`
pointed at the field names the dictionary above generates, so if the
dictionary is used as-is, no edits are needed) and point `--input` at
the real export instead of `synth.csv`.

## What the pipeline runs

1. Primary Analytic Sample (positive ASQ, PHQ-A + C-SSRS complete,
   INQ-10 administered) vs. Screening-Cascade Descriptive Sample (all
   age-eligible patients).
2. INQ-10 scoring into PB/TB means.
3. Baseline descriptives.
4. Four-step hierarchical ordinal logistic regression — age/sex/med
   status, then PHQ-A/triage result, then PB+TB, then the PB×TB
   interaction — with a likelihood-ratio test at each step.
5. Approximate proportional-odds diagnostic.
6. Supplementary hierarchical OLS with F-tests for R² change.
7. Secondary, descriptive-only aims: screening-cascade proportions by
   age band, sex, race/ethnicity, and insurance (Aim 2), and screened
   vs. unscreened by bypass reason, ESI, presenting complaint, and age
   (Aim 3).
8. Cohen's kappa on any configured dual-abstraction fields.

GAD-7 is descriptive only and never enters the confirmatory model,
even though it's collected on both tracks.

## Statistical caveats

- The proportional-odds diagnostic in the pipeline is a heuristic
  (cutpoint-wise coefficient spread against average SE), not a formal
  Brant test. A flag here means checking `brant::brant()` on a
  `MASS::polr` fit (or `ordinal::clm`) before treating the assumption
  as actually violated — the pipeline flags, it doesn't auto-switch to
  a partial-PO or multinomial model, and that switch needs a human
  look at which predictors got flagged.
- Predictors are z-scored internally before the ordinal fit and
  converted back after, which fixes a real conditioning issue —
  unscaled columns were leaving some standard errors stuck near their
  BFGS starting value. Those SEs are still an inverse-Hessian
  approximation, not analytic observed information, so cross-check
  anything headed for publication or continuing review against
  `MASS::polr` in R.
- Sparse ordinal categories (fewer than 20 observations on either
  side of a cutpoint) are excluded from the PO diagnostic outright,
  rather than reporting a falsely reassuring "no violation" on an
  unstable estimate.
- Secondary Aim 2/3 chi-square and t-tests are descriptive /
  hypothesis-generating per the protocol's own framing, not causal
  claims.
- ZIP code isn't auto-binned for the SES-proxy stratification in Aim
  2 — map it to a real grouping (income tercile, etc.) before using
  it that way.

## Known gap worth resolving before real data collection

`presenting_complaint` (psychiatric / medical / trauma) and `track`
(behavioral / physical) are separate REDCap fields, and nothing in
the pipeline or the synthetic data generator derives one from the
other — `generate_synthetic_data.py` randomizes them independently.
The workflow diagram's triage box describes presenting complaint as
determining the track, but there's no branching logic or scoring
rule anywhere that actually enforces that, and it's not obvious which
track a `trauma` presenting complaint is supposed to fall into. This
needs a clinical decision (probably: trauma routes to whichever track
the underlying injury/complaint implies, decided at triage, not
derived automatically) written into either the REDCap branching logic
or the abstraction instructions — right now it's just a note in a
diagram, not an enforced rule.

## Data handling

No real subject data belongs in this repository at any point. Real
REDCap exports, the Master Linking Log, and any file containing DOB,
MRN, or other direct identifiers should never enter version control —
they exist only in the REDCap project and CHOC's secured research
drive, per the protocol's data management plan.

## References

Hill, R., Rey, Y., Marin, C. E., Sharp, C., Green, K. L., & Pettit, J.
(2015). Evaluating the Interpersonal Needs Questionnaire: Comparison
of the reliability, factor structure, and predictive validity across
five versions. *Suicide & Life-Threatening Behavior, 45*(3), 302-314.

Cohen, J. (1988). *Statistical Power Analysis for the Behavioral
Sciences* (2nd ed.). Lawrence Erlbaum Associates.
