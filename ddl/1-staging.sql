USE CATALOG fluss_paimon ;

CREATE DATABASE IF NOT EXISTS staging;

USE staging ;

CREATE TABLE  IF NOT EXISTS staging.search_event (

    -- Unique event identification
    event_id              STRING,
    event_type            STRING,
    event_time            BIGINT,

    -- User and session context
    user_id               STRING,
    session_id            STRING,
    device_type           STRING,
    channel               STRING,
    region                STRING,

    -- Search context
    search_id             STRING,
    search_text           STRING,

    -- Product context (nullable for events without a SKU)
    sku_id                STRING,
    product_id            STRING,
    category_id           STRING,
    brand_id              STRING,
    merchant_id           STRING,

    -- A/B experiment context
    experiment_id         STRING,
    experiment_variant    STRING,

    -- Event-specific attributes
    search_rank           INT,
    quantity              INT,
    order_id              STRING,
    revenue               DECIMAL(18, 2),

    -- Ingestion metadata
    source_system         STRING,
    ingestion_time        BIGINT

) WITH (
      'table.datalake.enabled' = 'true',
      'table.datalake.freshness' = '300s'
    );

CREATE TABLE  IF NOT EXISTS staging.sale_order (

    -- Unique order identification
  order_id                STRING,
  order_status            STRING, -- e.g., 'COMPLETED', 'CANCELLED'
  order_time              BIGINT,

    -- User and session context (matches search events for attribution joins)
  user_id                 STRING,
  session_id              STRING,
  device_type             STRING,
  channel                 STRING,
  region                  STRING,

    -- Financial & basket metrics
  total_items             INT,
  revenue                 DECIMAL(18, 2),
  currency                STRING, -- e.g., 'PLN'

    -- Ingestion metadata
  source_system           STRING,
  ingestion_time          BIGINT

) WITH (
      'table.datalake.enabled' = 'true',
      'table.datalake.freshness' = '300s'
);
