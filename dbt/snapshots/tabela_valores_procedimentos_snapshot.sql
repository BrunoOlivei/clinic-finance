{% snapshot tabela_valores_procedimentos_snapshot %}

{{
    config(
        target_schema="snapshots",
        unique_key="savi_code",
        strategy="timestamp",
        updated_at="updated_at",
    )
}}

select *
from {{ ref('tabela_valores_procedimentos') }}

{% endsnapshot %}
