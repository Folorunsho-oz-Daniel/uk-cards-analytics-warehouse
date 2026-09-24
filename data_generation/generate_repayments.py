"""
generate_repayments.py

Generates a synthetic monthly repayment history for each account.
Defaulted accounts show a rising chance of missed payments over
time, simulating a customer sliding towards default.
"""

import pandas as pd
import random
from datetime import date, timedelta

random.seed(42)

REPAYMENT_TYPES = ["Full Payment", "Minimum Payment", "Partial Payment", "Missed Payment"]

TODAY = date.today()
WINDOW_START = TODAY - timedelta(days=365)


def repayment_weights_for(account_status, month_index, total_months):
    """
    Returns weights for [Full, Minimum, Partial, Missed] depending on
    account status and how far through its timeline we are.
    """
    if account_status == "Defaulted" and total_months > 1:
        # Progress from 0.0 (first month) to 1.0 (last month)
        progress = month_index / (total_months - 1)
        missed_chance = 0.05 + (progress * 0.55)  # rises up to ~60%
        remaining = 1 - missed_chance
        return [remaining * 0.25, remaining * 0.35, remaining * 0.40, missed_chance]
    elif account_status == "Closed":
        return [0.35, 0.40, 0.20, 0.05]
    else:  # Active
        return [0.30, 0.45, 0.20, 0.05]


def amount_paid(repayment_type, credit_limit):
    """Payment amount as a rough proportion of the account's credit limit."""
    if repayment_type == "Missed Payment":
        return 0.0
    elif repayment_type == "Full Payment":
        return round(credit_limit * random.uniform(0.15, 0.35), 2)
    elif repayment_type == "Minimum Payment":
        return round(credit_limit * random.uniform(0.02, 0.05), 2)
    else:  # Partial Payment
        return round(credit_limit * random.uniform(0.06, 0.14), 2)


def repayments_for_account(account):
    rows = []

    opening_date = pd.to_datetime(account["opening_date"]).date()
    start_date = max(opening_date, WINDOW_START)

    if account["account_status"] == "Active":
        end_date = TODAY
    else:
        days_span = max((TODAY - start_date).days, 1)
        end_date = start_date + timedelta(days=random.randint(0, days_span))

    if end_date <= start_date:
        return rows

    total_months = max((end_date.year - start_date.year) * 12
                        + (end_date.month - start_date.month), 1)

    for month_index in range(total_months):
        due_date = start_date + timedelta(days=month_index * 30)
        if due_date > end_date:
            break

        weights = repayment_weights_for(
            account["account_status"], month_index, total_months
        )
        repayment_type = random.choices(REPAYMENT_TYPES, weights=weights, k=1)[0]

        # Missed payments have no actual payment date; on-time ones
        # land a few days after the due date (simulating processing time)
        actual_date = None if repayment_type == "Missed Payment" else (
            due_date + timedelta(days=random.randint(0, 5))
        )

        rows.append({
            "account_id": account["account_id"],
            "due_date": due_date,
            "repayment_date": actual_date,
            "repayment_type": repayment_type,
            "amount_paid_gbp": amount_paid(repayment_type, account["credit_limit_gbp"]),
        })

    return rows


def generate_repayments(accounts_df):
    all_rows = []
    for _, account in accounts_df.iterrows():
        all_rows.extend(repayments_for_account(account))

    df = pd.DataFrame(all_rows)
    df.insert(0, "repayment_id", [f"REP{i+1:07d}" for i in range(len(df))])
    return df


if __name__ == "__main__":
    accounts_df = pd.read_csv("data_generation/output/accounts.csv")

    print("Generating repayments...")
    repayments_df = generate_repayments(accounts_df)

    output_path = "data_generation/output/repayments.csv"
    repayments_df.to_csv(output_path, index=False)

    print(f"Generated {len(repayments_df)} repayments.")
    print(f"Saved to {output_path}")
    print("\nPreview:")
    print(repayments_df.head(10))