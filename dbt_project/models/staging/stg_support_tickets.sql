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
    -- Clean description: remove HTML tags and special characters, keep plain text only
    nullif(
        trim(regexp_replace(
            regexp_replace(
                ticket_description,
                '<[^>]*>',
                '',
                'g'
            ),
            '[^\w\s\.\,\!\?\-\:\;\'\"]',
            '',
            'g'
        )),
        ''
    ) as ticket_description,
    ticket_status,
    resolution,
    ticket_priority,
    ticket_channel,
    -- Normalize timestamps: convert to TIMESTAMP type, preserve nulls
    case
        when first_response_time is null or first_response_time = '' then null
        else try_cast(first_response_time as timestamp)
    end as first_response_time,
    case
        when time_to_resolution is null or time_to_resolution = '' then null
        else try_cast(time_to_resolution as timestamp)
    end as time_to_resolution,
    customer_satisfaction_rating,
    current_timestamp as loaded_at

from {{ source('raw', 'raw_support_tickets') }}

where ticket_id is not null
