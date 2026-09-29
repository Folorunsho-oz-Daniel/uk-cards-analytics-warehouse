-- int_account_delinquency.sql
--
-- Classifies each account's current delinquency status based on
-- its most recent repayments, mirroring how real credit risk teams
-- describe missed-payment severity (30 / 60 / 90+ days delinquent).

with repayments as (

    select * from {{ ref('stg_repayments') }}

),

-- Rank each account's repayments from most recent (1) to oldest.
-- This is a WINDOW FUNCTION: unlike GROUP BY, it doesn't collapse
-- rows together — every repayment row is kept, just labelled with
-- its rank within its own account.
ranked as (

    select
        *,
        row_number() over (
            partition by account_id
            order by due_date desc
        ) as recency_rank

    from repayments

),

-- Pull out just the 3 most recent repayments per account, and pivot
-- them into columns so we can compare them side by side in one row.
recent_three as (

    select
        account_id,
        max(case when recency_rank = 1 then repayment_type end) as most_recent_type,
        max(case when recency_rank = 2 then repayment_type end) as second_most_recent_type,
        max(case when recency_rank = 3 then repayment_type end) as third_most_recent_type

    from ranked
    where recency_rank <= 3
    group by account_id

),

flagged as (

    select
        *,
        case
            when most_recent_type = 'Missed Payment'
                and second_most_recent_type = 'Missed Payment'
                and third_most_recent_type = 'Missed Payment'
                then '90+ Days Delinquent'
            when most_recent_type = 'Missed Payment'
                and second_most_recent_type = 'Missed Payment'
                then '60+ Days Delinquent'
            when most_recent_type = 'Missed Payment'
                then '30+ Days Delinquent'
            else 'Current'
        end as delinquency_status

    from recent_three

),

-- Bring in the overall missed-payment rate for extra context,
-- reusing the summary model we already built.
final as (

    select
        f.account_id,
        f.most_recent_type,
        f.delinquency_status,
        rs.repayment_count,
        rs.missed_payment_count,
        round(rs.missed_payment_count / nullif(rs.repayment_count, 0) * 100, 2) as missed_payment_rate_pct

    from flagged f
    left join {{ ref('int_account_repayment_summary') }} rs
        on f.account_id = rs.account_id

)

select * from final