# dbt project

The transformation layer for the UK Cards Analytics Warehouse. See the [main README](../README.md) for the full project overview.

## Layout

- `models/staging/`: light cleaning of each raw table (views)
- `models/intermediate/`: reusable calculations such as balances, utilisation and delinquency tiers (views)
- `models/marts/`: analysis-ready tables for portfolio performance and investor reporting
- Sources are defined in `models/staging/_sources.yml`; tests and descriptions live in the `_*_models.yml` files beside the models

## Commands

Run these from inside this folder: `dbt run`, `dbt test`, `dbt docs generate`, `dbt docs serve`.