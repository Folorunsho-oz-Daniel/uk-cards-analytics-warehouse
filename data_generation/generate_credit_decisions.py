"""
generate_credit_decisions.py

Generates a synthetic credit decisions dataset covering BOTH:
  1. Approved applicants (our existing customers, linked to their accounts)
  2. Declined applicants (new, synthetic people who never became customers)

This is what makes approval-rate and lending-decision analysis possible.
"""

import pandas as pd
from faker import Faker
import random
from datetime import timedelta

fake = Faker("en_GB")
Faker.seed(99)
random.seed(99)

NUM_DECLINED_APPLICANTS = 2200  # roughly a 70% approval rate overall

DECLINE_REASONS = [
    "Low Credit Score",
    "Insufficient Income",
    "Too Many Existing Debts",
    "Missing Documentation",
    "Fraud Risk Flagged",
]
DECLINE_REASON_WEIGHTS = [0.40, 0.25, 0.20, 0.10, 0.05]


def build_approved_decisions(customers_df, accounts_df):
    """One 'Approved' decision per existing customer/account pair."""
    merged = customers_df.merge(accounts_df, on="customer_id")

    rows = []
    for _, row in merged.iterrows():
        approved_limit = row["credit_limit_gbp"]
        # People often request slightly more than they're approved for
        requested_limit = round(approved_limit * random.uniform(1.0, 1.3), 2)

        # Decision happens a few days before the account was opened
        opening_date = pd.to_datetime(row["opening_date"]).date()
        decision_date = opening_date - timedelta(days=random.randint(1, 10))

        rows.append({
            "decision_id": None,  # filled in later
            "applicant_id": row["customer_id"],
            "decision_date": decision_date,
            "credit_score_at_application": row["credit_score"],
            "annual_income_gbp": row["annual_income_gbp"],
            "requested_credit_limit_gbp": requested_limit,
            "decision_outcome": "Approved",
            "decline_reason": None,
            "approved_credit_limit_gbp": approved_limit,
        })
    return rows


def build_declined_decisions(n):
    """Generates n brand-new applicants who were declined."""
    rows = []
    for i in range(n):
        # Declined applicants skew towards lower scores/income —
        # that's WHY they were declined.
        credit_score = random.randint(300, 620)
        annual_income = round(random.uniform(0, 30000), 2)
        requested_limit = round(random.uniform(500, 8000), 2)

        rows.append({
            "decision_id": None,
            "applicant_id": f"APPL{i+1:06d}",  # note: different prefix — never a customer_id
            "decision_date": fake.date_between(start_date="-1y", end_date="today"),
            "credit_score_at_application": credit_score,
            "annual_income_gbp": annual_income,
            "requested_credit_limit_gbp": requested_limit,
            "decision_outcome": "Declined",
            "decline_reason": random.choices(
                DECLINE_REASONS, weights=DECLINE_REASON_WEIGHTS, k=1
            )[0],
            "approved_credit_limit_gbp": None,
        })
    return rows


if __name__ == "__main__":
    customers_df = pd.read_csv("data_generation/output/customers.csv")
    accounts_df = pd.read_csv("data_generation/output/accounts.csv")

    print("Generating credit decisions...")
    approved_rows = build_approved_decisions(customers_df, accounts_df)
    declined_rows = build_declined_decisions(NUM_DECLINED_APPLICANTS)

    all_rows = approved_rows + declined_rows
    df = pd.DataFrame(all_rows)

    # Shuffle so approved/declined rows are mixed, not grouped in blocks
    df = df.sample(frac=1, random_state=99).reset_index(drop=True)

    df["decision_id"] = [f"DEC{i+1:07d}" for i in range(len(df))]

    output_path = "data_generation/output/credit_decisions.csv"
    df.to_csv(output_path, index=False)

    approval_rate = (df["decision_outcome"] == "Approved").mean() * 100

    print(f"Generated {len(df)} credit decisions.")
    print(f"  Approved: {(df['decision_outcome'] == 'Approved').sum()}")
    print(f"  Declined: {(df['decision_outcome'] == 'Declined').sum()}")
    print(f"  Approval rate: {approval_rate:.1f}%")
    print(f"Saved to {output_path}")
    print("\nPreview:")
    print(df.head(10))