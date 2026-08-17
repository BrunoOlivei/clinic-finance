-- Roda uma única vez, na primeira inicialização do volume do Postgres
-- (docker-entrypoint-initdb.d só executa em volume vazio). Cria um banco
-- separado para o metadata do Airflow, sem misturar com o schema gold do
-- dbt (que fica em clinic_finance).
CREATE DATABASE airflow OWNER clinic;
