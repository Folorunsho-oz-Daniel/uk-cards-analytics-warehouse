with source as (

    select * from {{ source('raw', 'repayments') }}

),

renamed as (

    select
        repayment_id,
        account_id,
        due_date,
        repayment_date,
        trim(repayment_type)               as repayment_type,
        amount_paid_gbp

    from source

)

select * from renamed