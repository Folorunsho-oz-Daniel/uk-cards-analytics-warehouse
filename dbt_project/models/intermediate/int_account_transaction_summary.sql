-- Summarizes all transaction activity per account: how much they've
-- spent, withdrawn, and been refunded, over the whole dataset.

with transactions as (

    select * from {{ ref('stg_transactions') }}

),

summarized as (

    select
        account_id,
        count(*)                                                              as transaction_count,
        sum(case when transaction_type = 'Purchase' then amount_gbp else 0 end)          as total_purchases_gbp,
        sum(case when transaction_type = 'Cash Withdrawal' then amount_gbp else 0 end)   as total_cash_withdrawals_gbp,
        sum(case when transaction_type = 'Refund' then amount_gbp else 0 end)            as total_refunds_gbp,
        sum(amount_gbp)                                                       as net_transaction_amount_gbp,
        max(transaction_date)                                                 as last_transaction_date

    from transactions
    group by account_id

)

select * from summarized