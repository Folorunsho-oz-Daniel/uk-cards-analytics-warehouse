"""
generate_accounts.py

Generates a synthetic 'accounts' dataset — one credit card account
per customer, linked back to customers.csv via customer_id.
"""

import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

PRODUCT_TYPES = ["Standard", "Rewards", "Low-Rate", "Balance Transfer", "Student"]
PRODUCT_WEIGHTS = [0.40, 0.25, 0.15, 0.15, 0.05]

ACCOUNT_STATUSES = ["Active", "Closed", "Defaulted"]
STATUS_WEIGHTS = [0.85, 0.10, 0.05]


def credit_limit_for(credit_score, annual_income):
    """
    Better credit score and higher income -> higher credit limit.
    This is a simplified rule, not real underwriting logic.
    """
    base = (credit_score - 300) * 20        # score 300-850 -> 0-11,000
    income_boost = annual_income * 0.15      # a slice of income
    limit = base + income_boost
    limit = max(500, min(limit, 25000))      # keep between £500 and £25,000
    return round(limit / 100) * 100          # round to nearest £100


def apr_for(credit_score):
    """
    Better credit score -> lower APR (interest rate).
    Roughly mirrors how real card pricing works.
    """
    if credit_score >= 750:
        return round(random.uniform(9.9, 14.9), 1)
    elif credit_score >= 650:
        return round(random.uniform(15.0, 22.9), 1)
    elif credit_score >= 550:
        return round(random.uniform(23.0, 29.9), 1)
    else:
        return round(random.uniform(30.0, 39.9), 1)


def opening_date_after(customer_since_date):
    """Account opens sometime between customer_since_date and today."""
    start = datetime.strptime(str(customer_since_date), "%Y-%m-%d")
    days_range = max((datetime.today() - start).days, 1)
    random_offset = random.randint(0, days_range)
    return (start + timedelta(days=random_offset)).date()


def generate_accounts(customers_df):
    rows = []
    for i, customer in customers_df.iterrows():
        account_status = random.choices(
            ACCOUNT_STATUSES, weights=STATUS_WEIGHTS, k=1
        )[0]

        rows.append({
            "account_id": f"ACC{i+1:06d}",
            "customer_id": customer["customer_id"],
            "product_type": random.choices(
                PRODUCT_TYPES, weights=PRODUCT_WEIGHTS, k=1
            )[0],
            "credit_limit_gbp": credit_limit_for(
                customer["credit_score"], customer["annual_income_gbp"]
            ),
            "apr_percent": apr_for(customer["credit_score"]),
            "opening_date": opening_date_after(customer["customer_since_date"]),
            "account_status": account_status,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    customers_df = pd.read_csv("data_generation/output/customers.csv")

    accounts_df = generate_accounts(customers_df)

    output_path = "data_generation/output/accounts.csv"
    accounts_df.to_csv(output_path, index=False)

    print(f"Generated {len(accounts_df)} accounts.")
    print(f"Saved to {output_path}")
    print("\nPreview:")
    print(accounts_df.head())