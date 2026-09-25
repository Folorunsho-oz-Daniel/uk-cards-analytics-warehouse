-- ============================================================
-- 02_create_raw_tables.sql
-- Creates the five raw tables, matching our CSV structures
-- exactly. These live in UK_CARDS_ANALYTICS.RAW.
-- ============================================================

USE WAREHOUSE UK_CARDS_WH;
USE DATABASE UK_CARDS_ANALYTICS;
USE SCHEMA RAW;

CREATE OR REPLACE TABLE CUSTOMERS (
    customer_id           VARCHAR,
    first_name            VARCHAR,
    last_name             VARCHAR,
    date_of_birth         DATE,
    email                 VARCHAR,
    phone_number          VARCHAR,
    address_line_1        VARCHAR,
    city                  VARCHAR,
    postcode              VARCHAR,
    employment_status     VARCHAR,
    annual_income_gbp     NUMBER(12,2),
    credit_score          NUMBER(5,0),
    customer_since_date   DATE
);

CREATE OR REPLACE TABLE ACCOUNTS (
    account_id            VARCHAR,
    customer_id           VARCHAR,
    product_type          VARCHAR,
    credit_limit_gbp      NUMBER(12,2),
    apr_percent           NUMBER(5,2),
    opening_date          DATE,
    account_status        VARCHAR
);

CREATE OR REPLACE TABLE TRANSACTIONS (
    transaction_id        VARCHAR,
    account_id            VARCHAR,
    transaction_date      DATE,
    transaction_type      VARCHAR,
    merchant_category     VARCHAR,
    amount_gbp            NUMBER(12,2)
);

CREATE OR REPLACE TABLE REPAYMENTS (
    repayment_id          VARCHAR,
    account_id            VARCHAR,
    due_date              DATE,
    repayment_date        DATE,
    repayment_type        VARCHAR,
    amount_paid_gbp       NUMBER(12,2)
);

CREATE OR REPLACE TABLE CREDIT_DECISIONS (
    decision_id                    VARCHAR,
    applicant_id                   VARCHAR,
    decision_date                  DATE,
    credit_score_at_application    NUMBER(5,0),
    annual_income_gbp              NUMBER(12,2),
    requested_credit_limit_gbp     NUMBER(12,2),
    decision_outcome               VARCHAR,
    decline_reason                 VARCHAR,
    approved_credit_limit_gbp      NUMBER(12,2)
);