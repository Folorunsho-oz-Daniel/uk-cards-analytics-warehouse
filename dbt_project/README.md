Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
## Known Limitations

- **Negative account balances**: `current_balance_gbp` (in `int_account_balances` and downstream marts) can occasionally be negative. This is a side-effect of generating transactions and repayments as two independent synthetic datasets — in reality, a customer's spending and repayment behavior are linked, but here they were generated separately. Rather than artificially floor the balance at £0 (which would hide the underlying data generation choice), this was left visible and is documented here. A production system would derive balance from a single authoritative ledger, not reconstruct it from two unrelated feeds.