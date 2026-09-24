"""
generate_transactions.py

Generates synthetic card transactions for each account, covering
roughly the trailing 12 months. This is the largest dataset in the
project, so it will take longer to run than the previous scripts.
"""

import pandas as pd
import random
from datetime import date, timedelta

random.seed(42)

TRANSACTION_TYPES = ["Purchase", "Cash Withdrawal", "Refund"]
TYPE_WEIGHTS = [0.85, 0.10, 0.05]

MERCHANT_CATEGORIES = [
    "Groceries", "Fuel", "Retail", "Dining", "Travel",
    "Utilities", "Online Shopping", "Entertainment",
]

TODAY = date.today()
WINDOW_START = TODAY - timedelta(days=365)


def amount_for(transaction_type):
    """Purchases and withdrawals are positive spend; refunds are negative."""
    if transaction_type == "Purchase":
        amount = round(random.uniform(5, 400), 2)
    elif transaction_type == "Cash Withdrawal":
        amount = round(random.uniform(20, 300), 2)
    else:  # Refund
        amount = -round(random.uniform(5, 200), 2)
    return amount


def transactions_for_account(account):
    """Generates a list of transaction rows for a single account."""
    rows = []

    # Work out the window this account was actually active for
    opening_date = pd.to_datetime(account["opening_date"]).date()
    start_date = max(opening_date, WINDOW_START)

    if account["account_status"] == "Active":
        end_date = TODAY
    else:
        # Closed / Defaulted accounts stop transacting at some
        # random point between opening and today.
        days_span = max((TODAY - start_date).days, 1)
        end_date = start_date + timedelta(days=random.randint(0, days_span))

    if end_date <= start_date:
        return rows  # account never actually transacted in our window

    months_active = max((end_date.year - start_date.year) * 12
                         + (end_date.month - start_date.month), 1)

    for month_offset in range(months_active):
        # How many transactions this account makes in this month
        num_transactions = random.randint(1, 15)

        for _ in range(num_transactions):
            random_days = random.randint(0, 27)
            txn_date = start_date + timedelta(days=month_offset * 30 + random_days)
            if txn_date > end_date:
                continue

            txn_type = random.choices(TRANSACTION_TYPES, weights=TYPE_WEIGHTS, k=1)[0]

            rows.append({
                "account_id": account["account_id"],
                "transaction_date": txn_date,
                "transaction_type": txn_type,
                "merchant_category": (
                    "Cash Withdrawal" if txn_type == "Cash Withdrawal"
                    else random.choice(MERCHANT_CATEGORIES)
                ),
                "amount_gbp": amount_for(txn_type),
            })

    return rows


def generate_transactions(accounts_df):
    all_rows = []
    for _, account in accounts_df.iterrows():
        all_rows.extend(transactions_for_account(account))

    df = pd.DataFrame(all_rows)
    # Give every transaction a unique, readable ID now that we know the total count
    df.insert(0, "transaction_id", [f"TXN{i+1:08d}" for i in range(len(df))])
    return df


if __name__ == "__main__":
    accounts_df = pd.read_csv("data_generation/output/accounts.csv")

    print("Generating transactions... this may take a minute.")
    transactions_df = generate_transactions(accounts_df)

    output_path = "data_generation/output/transactions.csv"
    transactions_df.to_csv(output_path, index=False)

    print(f"Generated {len(transactions_df)} transactions.")
    print(f"Saved to {output_path}")
    print("\nPreview:")
    print(transactions_df.head())