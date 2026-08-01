WITH 
producao AS (
  SELECT * FROM {{ ref('stg_production_reports') }}
)
, valores AS (
  SELECT * FROM {{ ref('tabela_valores_procedimentos_snapshot') }}
)
, valor_vigente AS (
  SELECT
    p.cd_auth_password,
    p.nr_guide,
    p.tp_service,
    p.nm_branch,
    p.dt_execution,
    p.cd_patient,
    p.nm_patient,
    p.cd_doctor,
    p.sg_doctor_state,
    p.nm_doctor,
    p.cd_procedure,
    p.nm_procedure,
    p.is_urgent,
    p.qt_authorized,
    p.dt_authorization,
    p.qt_executed,
    v.paid_value AS vl_unit_procedure,
    p.qt_executed * v.paid_value AS vl_procedure,
    CASE
      WHEN p.cd_procedure NOT IN ('00010014', '10101012')
      THEN TRUE
      ELSE FALSE
    END AS tx_room,
    CASE
      WHEN p.cd_procedure NOT IN ('00010014', '10101012')
        THEN (
          SELECT v2.paid_value
          FROM valores v2
          WHERE v2.savi_code = '80020470'
            AND v2.updated_at <= p.dt_execution
          ORDER BY v2.updated_at DESC
          LIMIT 1
      )
      ELSE 0
    END AS vl_room,
    p.qt_executed
    p.dt_period,
    p.created_at,
    p.updated_at,
    row_number() OVER (PARTITION BY p.nr_guide, p.cd_procedure ORDER BY v.updated_at DESC) AS rn
    FROM producao AS p
    LEFT JOIN valores AS v
        ON v.savi_code = p.cd_procedure
        AND v.updated_at <= p.dt_execution
)

select
    * exclude (rn),
    vl_procedure + vl_room as vl_total
from valor_vigente
where rn = 1