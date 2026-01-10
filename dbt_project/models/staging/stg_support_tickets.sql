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
            '[^a-zA-Z0-9\s.,!?:;''-]',
            '',
            'g'
        )),
        ''
    ) as ticket_description,
    -- Message length of cleaned description
    char_length(
        nullif(
            trim(regexp_replace(
                regexp_replace(
                    ticket_description,
                    '<[^>]*>',
                    '',
                    'g'
                ),
                '[^a-zA-Z0-9\s.,!?:;''-]',
                '',
                'g'
            )),
            ''
        )
    ) as message_length,
    'english' as language,
    ticket_status,
    resolution,
    ticket_priority,
    ticket_channel,
    -- Normalize timestamps: convert to TIMESTAMP type, preserve nulls
    case
        when first_response_time is null or first_response_time = '' or first_response_time = 'NaN' then null
        else first_response_time::timestamp
    end as first_response_time,
    case
        when time_to_resolution is null or time_to_resolution = '' or time_to_resolution = 'NaN' then null
        else time_to_resolution::timestamp
    end as time_to_resolution,
    customer_satisfaction_rating,
    current_timestamp as loaded_at

from {{ source('raw', 'raw_support_tickets') }}

where ticket_id is not null
