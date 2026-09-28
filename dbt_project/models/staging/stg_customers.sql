-- stg_customers.sql
--
-- Staging model for customers: light cleaning and standardization only.
-- No business logic here — that belongs in the intermediate layer.

with source as (

    select * from {{ source('raw', 'customers') }}

),

renamed as (

    select
        customer_id,
        first_name,
        last_name,
        date_of_birth,
        lower(trim(email))          as email,
        phone_number,
        address_line_1,
        city,
        postcode,
        employment_status,
        annual_income_gbp,
        credit_score,
        customer_since_date

    from source

)

select * from renamed