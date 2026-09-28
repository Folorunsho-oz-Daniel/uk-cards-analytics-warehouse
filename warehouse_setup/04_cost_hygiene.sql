-- ============================================================
-- 04_cost_hygiene.sql
-- Keeps Snowflake credit usage under control:
--   1. Makes the trial's default warehouse auto-suspend quickly,
--      so it can't be left running by accident.
--   2. Makes the project warehouse the default for new sessions.
-- ============================================================

ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;

ALTER USER DATAGIRL SET DEFAULT_WAREHOUSE = UK_CARDS_WH;