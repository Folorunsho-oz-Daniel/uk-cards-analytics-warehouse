-- fct_monthly_portfolio_summary.sql
--
-- Investor-reporting mart: a portfolio-level snapshot, summarized
-- by risk band and account status. This is the shape investors
-- actually want — aggregated totals, not individual account rows.
--
-- NOTE: report_date reflects when this model was last built, since
-- our dataset is a single point-in-time snapshot rather than true
-- historical data. In a production system, this model would run on
-- a schedule (e.g. daily/monthly) and each run would append a new
-- report_date, building up real history over time.

with portfolio as (

    select * from {{ ref('fct_portfolio_performance') }}

),

summarized as (

    select
        current_date()                                              as report_date,
        risk_band,
        account_status,
        count(*)                                                    as account_count,
        sum(credit_limit_gbp)                                       as total_credit_limit_gbp,
        sum(current_balance_gbp)                                    as total_current_balance_gbp,
        round(avg(credit_utilisation_pct), 2)                       as avg_utilisation_pct,
        sum(missed_payment_count)                                   as total_missed_payments,
        sum(case when delinquency_status != 'Current' then 1 else 0 end)  as delinquent_account_count,
        round(
            sum(case when delinquency_status != 'Current' then 1 else 0 end)
            / nullif(count(*), 0) * 100,
            2
        )                                                            as delinquency_rate_pct

    from portfolio
    group by risk_band, account_status

)

select * from summarized
order by risk_band, account_status