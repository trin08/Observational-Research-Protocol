"""
Column mapping + INQ-10 scoring key for the RCHOC study pipeline.
Edit COLUMNS and the two mappings below to match your actual REDCap
export before running analyze_redcap.py on real data.

Scoring key source: Hill et al. (2015), Table 1 ("Items Included in
Each Version of the INQ"). Checked directly against the protocol's own
appendix reproduction of that table:

  PB (Perceived Burdensomeness): original items 1, 3, 9, 12, 14
  TB (Thwarted Belongingness):   original items 17, 19, 20, 21, 24

TB items 17, 19, 24 are positively worded ("I feel like I belong",
"I am fortunate to have many caring and supportive friends", "I am
close to other people") and get reverse-scored so higher always means
more thwarted belonging, matching the negatively-worded TB items (20,
21). All 5 PB items are already negatively worded, no reversal needed.

The one thing this file can't verify for you: INQ10_FIELD_TO_ORIGINAL_ITEM
assumes your REDCap instrument presents the 10 retained items in their
original relative order, renumbered 1-10 -- the usual convention for a
derived short form, but an assumption about your specific build, not
something the source table states. If your instrument's field order
differs, edit that mapping only; leave the two dicts above it alone.
"""

# REDCap column names -- edit to match your export
COLUMNS = {
    "subject_id": "subject_id",
    "age": "age",
    "sex": "biological_sex",            # "M"/"F" or 0/1
    "gender": "gender",
    "race_ethnicity": "race_ethnicity",
    "insurance_type": "insurance_type",
    "zip_code": "zip_code",
    "medication_status": "med_risk_flag",   # 1 = documented elevated-risk med/substance use
    "comorbid_dx": "comorbid_dx",
    "icd10": "icd10",
    "phqa_total": "phqa_total",
    "gad7_total": "gad7_total",              # descriptive only, never enters the confirmatory model
    "cssrs_triage_result": "cssrs_triage_result",
    "cssrs_ideation_severity": "cssrs_ideation_severity",  # primary outcome, ordinal 1-5
    "bssa_tier": "bssa_tier",
    "asq_result": "asq_result",              # "positive" / "negative"
    "presenting_complaint": "presenting_complaint",
    "track": "track",                        # "behavioral" / "physical"
    "bypass_reason": "bypass_reason",
    "esi_level": "esi_level",
}

INQ10_ITEM_COLUMNS = [f"inq10_item_{i}" for i in range(1, 11)]

# Sourced -- don't edit these two.
INQ_SUBSCALE_BY_ORIGINAL_ITEM = {
    1: "PB", 3: "PB", 9: "PB", 12: "PB", 14: "PB",
    17: "TB", 19: "TB", 20: "TB", 21: "TB", 24: "TB",
}
REVERSE_SCORED_ORIGINAL_ITEMS = [17, 19, 24]

# Verify against your actual REDCap instrument -- see docstring above.
INQ10_FIELD_TO_ORIGINAL_ITEM = {
    "inq10_item_1": 1,
    "inq10_item_2": 3,
    "inq10_item_3": 9,
    "inq10_item_4": 12,
    "inq10_item_5": 14,
    "inq10_item_6": 17,
    "inq10_item_7": 19,
    "inq10_item_8": 20,
    "inq10_item_9": 21,
    "inq10_item_10": 24,
}

# Derived -- don't edit directly.
INQ_SUBSCALE_MAP = {
    field: INQ_SUBSCALE_BY_ORIGINAL_ITEM[orig_item]
    for field, orig_item in INQ10_FIELD_TO_ORIGINAL_ITEM.items()
}
REVERSE_SCORED_ITEMS = [
    field for field, orig_item in INQ10_FIELD_TO_ORIGINAL_ITEM.items()
    if orig_item in REVERSE_SCORED_ORIGINAL_ITEMS
]

INQ_ITEM_SCALE_MIN = 1
INQ_ITEM_SCALE_MAX = 7

# Paired columns for the 10% dual-abstraction inter-rater check.
DUAL_ABSTRACTION_FIELD_PAIRS = {
    "presenting_complaint": ("presenting_complaint", "presenting_complaint_2nd"),
    "comorbid_dx": ("comorbid_dx", "comorbid_dx_2nd"),
}
