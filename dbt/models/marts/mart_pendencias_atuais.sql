with pendencias as (
    select * from {{ ref('stg_pending_reports') }}
),

mais_recente as (
    select
        *,
        row_number() over (
            partition by cd_patient, cd_doctor, cd_procedure
            order by created_at desc
        ) as rn
    from pendencias
)

select * exclude (rn)
from mais_recente
where rn = 1