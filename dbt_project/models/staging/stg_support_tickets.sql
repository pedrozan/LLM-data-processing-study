-- Staging model for raw support tickets
-- This model cleans and standardizes the raw ticket data

{{ config(
    materialized='table',
    schema='analytics'
) }}

select
    ticket_id,
    customer_name,
    customer_email,
    customer_age,
    customer_gender,
    product_purchased,
    date_of_purchase::date as date_of_purchase,
    ticket_type,
    ticket_subject,
    ticket_description,
    ticket_status,
    resolution,
    ticket_priority,
    ticket_channel,
    first_response_time,
    time_to_resolution,
    customer_satisfaction_rating,
    current_timestamp as loaded_at

from {{ source('raw', 'raw_support_tickets') }}

where ticket_id is not null
