-- fct_portfolio_performance.sql
--
-- The portfolio performance mart: one row per account, combining
-- balances, utilisation, delinquency status, and customer risk
-- profile into a single analysis-ready table. This is what an
-- analyst (or Power BI) would query directly for portfolio reporting.

with balances as (

    select * from {{ ref('int_account_balances') }}

),

delinquency as (

    select * from {{ ref('int_account_delinquency') }}

),

customers as (

    select * from {{ ref('stg_customers') }}

),

joined as (

    select
        b.account_id,
        b.customer_id,
        b.product_type,
        b.credit_limit_gbp,
        b.apr_percent,
        b.account_status,
        b.opening_date,
        b.net_spend_gbp,
        b.total_repaid_gbp,
        b.current_balance_gbp,
        b.credit_utilisation_pct,
        b.missed_payment_count,
        d.delinquency_status,
        d.missed_payment_rate_pct,
        c.credit_score,
        c.employment_status,
        c.annual_income_gbp,

        -- Risk band: a standard way lenders group customers by
        -- creditworthiness, from A (best) to E (worst).
        case
            when c.credit_score >= 750 then 'A - Excellent'
            when c.credit_score >= 650 then 'B - Good'
            when c.credit_score >= 550 then 'C - Fair'
            when c.credit_score >= 450 then 'D - Poor'
            else 'E - Very Poor'
        end as risk_band

    from balances b
    left join delinquency d on b.account_id = d.account_id
    left join customers c on b.customer_id = c.customer_id

)

select * from joined