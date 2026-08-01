select
    cd_patient,
    cd_doctor,
    cd_procedure,
    dt_authorization,
    count(*) as qtd_linhas
from {{ ref('mart_pendencias_atuais') }}
group by cd_patient, cd_doctor, cd_procedure, dt_authorization
having count(*) > 1