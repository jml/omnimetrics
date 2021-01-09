{{ config(materialized="ephemeral") }}

with source as (

    select
        *
      , _partitiondate as partition_date
    from {{ source('omnifocus', 'raw_tasks') }}

),

renamed as (

    select
        partition_date as date_loaded,
        id as task_id,
        name,
        is_effectively_completed,
        is_blocked,
        is_dropped,
        is_completed_by_children,
        is_completed,
        is_flagged,
        is_sequential,
        is_effectively_dropped,
        is_next,
        is_in_inbox,
        primary_tag,
        containing_project,
        estimated_minutes,
        num_available_tasks,
        num_tasks,
        num_completed_tasks,
        parent_task,
        next_due_date,
        effective_defer_date,
        completion_date,
        creation_date,
        next_defer_date,
        defer_date,
        effective_due_date,
        dropped_date,
        modification_date,
        due_date
    from source

),

with_primary_key as (

    select
        farm_fingerprint(to_json_string([cast(date_loaded as string), cast(task_id as string)])) as raw_task_id
      , *
    from renamed

)

select * from with_primary_key
