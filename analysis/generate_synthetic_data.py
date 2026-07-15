"""
Fabricated REDCap-style export for testing the pipeline without real
patient data. Column structure matches what analyze_redcap.py /
config.py expect.

    python3 generate_synthetic_data.py --output synthetic_redcap_export.csv --n 500
"""

import argparse

import numpy as np
import pandas as pd


def generate(n=500, seed=7):
    rng = np.random.default_rng(seed)

    df = pd.DataFrame({
        "subject_id": [f"Sub-{i:04d}" for i in range(n)],
        "age": rng.integers(12, 22, n),
        "biological_sex": rng.choice([0, 1], n),
        "gender": rng.choice(["male", "female", "other"], n),
        "race_ethnicity": rng.choice(["A", "B", "C", "D"], n),
        "insurance_type": rng.choice(["private", "medicaid", "uninsured"], n),
        "zip_code": rng.choice(["92868", "92870", "90001"], n),
        "med_risk_flag": rng.binomial(1, 0.2, n),
        "comorbid_dx": rng.choice(["anxiety", "depression", "none"], n),
        "icd10": rng.choice(["F32.9", "F41.1", "T14.91"], n),
        "phqa_total": rng.normal(10, 6, n).clip(0, 27),
        "gad7_total": rng.normal(8, 5, n).clip(0, 21),
        "cssrs_triage_result": rng.binomial(1, 0.4, n),
        "bssa_tier": rng.choice(["low", "moderate", "high"], n),
        "presenting_complaint": rng.choice(["psychiatric", "medical", "trauma"], n),
        "track": rng.choice(["behavioral", "physical"], n),
        "esi_level": rng.choice([1, 2, 3, 4, 5], n),
    })

    # ~10% of age-eligible patients never get the ASQ
    bypass_mask = rng.choice([True, False], n, p=[0.10, 0.90])
    df["asq_result"] = rng.choice(["positive", "negative"], n, p=[0.6, 0.4])
    df.loc[bypass_mask, "asq_result"] = np.nan
    df["bypass_reason"] = pd.array([pd.NA] * n, dtype="object")
    reasons = ["altered mental status", "acuity 1", "trauma", "cognitive disability"]
    df.loc[bypass_mask, "bypass_reason"] = rng.choice(reasons, bypass_mask.sum())

    for i in range(1, 11):
        df[f"inq10_item_{i}"] = rng.integers(1, 8, n)

    # give the model something real to detect: correlate the outcome
    # with PHQ-A, C-SSRS triage, and a few INQ-10 items
    raw_score = (
        0.15 * df["phqa_total"]
        + 0.5 * df["cssrs_triage_result"]
        + 0.3 * df[[f"inq10_item_{i}" for i in range(1, 6)]].mean(axis=1)
        + rng.normal(0, 1.5, n)
    )
    df["cssrs_ideation_severity"] = pd.qcut(raw_score, 5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Primary Analytic Sample requires a positive ASQ; everyone else
    # gets no INQ-10 / no C-SSRS score, matching the protocol's actual
    # eligibility logic
    incomplete = df["asq_result"].isna() | (df["asq_result"] != "positive")
    df.loc[incomplete, [f"inq10_item_{i}" for i in range(1, 11)]] = np.nan
    df.loc[incomplete, "cssrs_ideation_severity"] = np.nan

    # 10% dual-abstraction subsample for inter-rater reliability, with
    # a bit of induced disagreement so kappa isn't a trivial 1.0
    df["presenting_complaint_2nd"] = pd.array([pd.NA] * n, dtype="object")
    df["comorbid_dx_2nd"] = pd.array([pd.NA] * n, dtype="object")
    dual_idx = rng.choice(df.index, size=int(0.1 * n), replace=False)
    df.loc[dual_idx, "presenting_complaint_2nd"] = df.loc[dual_idx, "presenting_complaint"]
    df.loc[dual_idx, "comorbid_dx_2nd"] = df.loc[dual_idx, "comorbid_dx"]
    flip_idx = rng.choice(dual_idx, size=max(1, int(0.1 * len(dual_idx))), replace=False)
    df.loc[flip_idx, "presenting_complaint_2nd"] = rng.choice(
        ["psychiatric", "medical", "trauma"], len(flip_idx)
    )

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic REDCap-style test data")
    parser.add_argument("--output", default="synthetic_redcap_export.csv")
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    df = generate(n=args.n, seed=args.seed)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df)} synthetic rows to {args.output}")
    print(f"ASQ-positive (Primary Analytic Sample eligible): {(df['asq_result'] == 'positive').sum()}")
    print(f"ASQ bypassed (Screening-Cascade Descriptive Sample only): {df['asq_result'].isna().sum()}")


if __name__ == "__main__":
    main()
