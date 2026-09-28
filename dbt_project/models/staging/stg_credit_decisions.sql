with source as (

    select * from {{ source('raw', 'credit_decisions') }}

),

renamed as (

    select
        decision_id,
        applicant_id,
        decision_date,
        credit_score_at_application,
        annual_income_gbp,
        requested_credit_limit_gbp,
        trim(decision_outcome)             as decision_outcome,
        nullif(trim(decline_reason), '')   as decline_reason,
        approved_credit_limit_gbp

    from source

)

select * from renamed