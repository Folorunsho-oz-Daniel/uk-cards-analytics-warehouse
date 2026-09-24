"""
generate_customers.py

Generates a synthetic (fake) UK customer dataset for the credit card
analytics warehouse. This simulates the 'raw' customer data a bank
would receive from its source systems.
"""

import pandas as pd
from faker import Faker
import random
from datetime import date

# Faker "en_GB" gives us UK-style names, addresses, and phone numbers
fake = Faker("en_GB")

# How many fake customers to generate. We start small so it's fast
# to test, and can increase this later once everything works.
NUM_CUSTOMERS = 5000

# Setting a "seed" makes the randomness repeatable — running this
# script twice will generate the exact same data both times, which
# is very useful for testing.
Faker.seed(42)
random.seed(42)

EMPLOYMENT_STATUSES = ["Employed", "Self-employed", "Unemployed", "Retired", "Student"]
# Weights control how common each status is (must add up to 1.0)
EMPLOYMENT_WEIGHTS = [0.60, 0.15, 0.08, 0.12, 0.05]


def random_date_of_birth():
    """Generates a birth date for someone aged 18 to 80."""
    return fake.date_of_birth(minimum_age=18, maximum_age=80)


def random_income(employment_status):
    """Generates a plausible annual income based on employment status."""
    if employment_status == "Employed":
        return round(random.uniform(18000, 75000), 2)
    elif employment_status == "Self-employed":
        return round(random.uniform(15000, 90000), 2)
    elif employment_status == "Retired":
        return round(random.uniform(9000, 30000), 2)
    elif employment_status == "Student":
        return round(random.uniform(0, 12000), 2)
    else:  # Unemployed
        return round(random.uniform(0, 8000), 2)


def random_credit_score():
    """Simplified credit score, 300 (poor) to 850 (excellent)."""
    return random.randint(300, 850)


def generate_customers(n):
    rows = []
    for i in range(1, n + 1):
        employment_status = random.choices(
            EMPLOYMENT_STATUSES, weights=EMPLOYMENT_WEIGHTS, k=1
        )[0]

        rows.append({
            "customer_id": f"CUST{i:06d}",       # e.g. CUST000001
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "date_of_birth": random_date_of_birth(),
            "email": fake.email(),
            "phone_number": fake.phone_number(),
            "address_line_1": fake.street_address(),
            "city": fake.city(),
            "postcode": fake.postcode(),
            "employment_status": employment_status,
            "annual_income_gbp": random_income(employment_status),
            "credit_score": random_credit_score(),
            "customer_since_date": fake.date_between(start_date="-10y", end_date="today"),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_customers(NUM_CUSTOMERS)

    output_path = "data_generation/output/customers.csv"
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} customers.")
    print(f"Saved to {output_path}")
    print("\nPreview:")
    print(df.head())
    