select
    nr_guide,
    cd_procedure,
    cd_auth_password,
    count(*) as qtd_linhas
from {{ ref('mart_faturamento') }}
group by nr_guide, cd_procedure, cd_auth_password
having count(*) > 1