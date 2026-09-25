-- ============================================================
-- 01_create_warehouse_and_database.sql
-- Sets up the core Snowflake objects for the UK Cards Analytics
-- Warehouse project: a dedicated warehouse, database, and a
-- RAW schema to hold source data exactly as received.
-- ============================================================

-- A warehouse is Snowflake's compute engine — it's what actually
-- runs your queries. X-Small is the smallest/cheapest size, and
-- AUTO_SUSPEND = 60 means it automatically shuts off after 60
-- seconds of inactivity, so we don't burn credits sitting idle.
CREATE WAREHOUSE IF NOT EXISTS UK_CARDS_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for the UK Cards Analytics project';

-- The database is the top-level container for everything in
-- this project.
CREATE DATABASE IF NOT EXISTS UK_CARDS_ANALYTICS
  COMMENT = 'UK Cards Analytics Warehouse - production-style credit card analytics project';

-- The RAW schema holds data exactly as it arrives from source
-- systems — no cleaning, no transformation. dbt will read FROM
-- here and build cleaner layers on top (staging, intermediate, marts).
CREATE SCHEMA IF NOT EXISTS UK_CARDS_ANALYTICS.RAW
  COMMENT = 'Raw layer: source data as received, untransformed';

-- Switch into this warehouse/database/schema so the next script
-- runs in the right place.
USE WAREHOUSE UK_CARDS_WH;
USE DATABASE UK_CARDS_ANALYTICS;
USE SCHEMA RAW;