select
    cd_auth_password,
    cd_patient,
    nm_patient,
    cd_doctor,
    nm_doctor,
    cd_procedure,
    nm_procedure,
    dt_authorization,
    qt_authorized,
    qt_pending,
    tp_situation,
    ds_observation,
    dt_period,
    created_at
from {{ source('bronze', 'pending_reports') }}
