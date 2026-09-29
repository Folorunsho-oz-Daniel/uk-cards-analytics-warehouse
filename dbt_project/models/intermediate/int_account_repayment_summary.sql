-- Summarizes all repayment activity per account: how much they've
-- paid back, and how many payments they've missed.

with repayments as (

    select * from {{ ref('stg_repayments') }}

),

summarized as (

    select
        account_id,
        count(*)                                                               as repayment_count,
        sum(amount_paid_gbp)                                                   as total_repaid_gbp,
        sum(case when repayment_type = 'Missed Payment' then 1 else 0 end)     as missed_payment_count,
        max(repayment_date)                                                    as last_repayment_date

    from repayments
    group by account_id

)

select * from summarized