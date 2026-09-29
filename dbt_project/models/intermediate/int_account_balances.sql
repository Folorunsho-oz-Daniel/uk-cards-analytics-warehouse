-- Combines account details with transaction and repayment summaries
-- to calculate a simplified current balance and credit utilisation.
--
-- NOTE: this is a simplified estimate (net spend minus repayments),
-- not a full accounting ledger with interest/fees applied.

with accounts as (

    select * from {{ ref('stg_accounts') }}

),

txn_summary as (

    select * from {{ ref('int_account_transaction_summary') }}

),

repayment_summary as (

    select * from {{ ref('int_account_repayment_summary') }}

),

combined as (

    select
        a.account_id,
        a.customer_id,
        a.product_type,
        a.credit_limit_gbp,
        a.apr_percent,
        a.account_status,
        a.opening_date,
        coalesce(t.net_transaction_amount_gbp, 0)                          as net_spend_gbp,
        coalesce(r.total_repaid_gbp, 0)                                    as total_repaid_gbp,
        coalesce(t.net_transaction_amount_gbp, 0) - coalesce(r.total_repaid_gbp, 0)  as current_balance_gbp,
        coalesce(r.missed_payment_count, 0)                                as missed_payment_count

    from accounts a
    left join txn_summary t on a.account_id = t.account_id
    left join repayment_summary r on a.account_id = r.account_id

)

select
    *,
    round(current_balance_gbp / nullif(credit_limit_gbp, 0) * 100, 2)      as credit_utilisation_pct

from combined