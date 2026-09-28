with source as (

    select * from {{ source('raw', 'accounts') }}

),

renamed as (

    select
        account_id,
        customer_id,
        trim(product_type)                 as product_type,
        credit_limit_gbp,
        apr_percent,
        opening_date,
        trim(account_status)               as account_status

    from source

)

select * from renamed
