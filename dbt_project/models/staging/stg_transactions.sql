with source as (

    select * from {{ source('raw', 'transactions') }}

),

renamed as (

    select
        transaction_id,
        account_id,
        transaction_date,
        trim(transaction_type)             as transaction_type,
        trim(merchant_category)            as merchant_category,
        amount_gbp

    from source

)

select * from renamed