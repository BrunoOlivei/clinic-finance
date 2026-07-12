from enum import StrEnum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Environment(StrEnum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    environment: Environment = Environment.DEV
    log_level: str = "INFO"

    # URLs do SAVI
    url_login: str
    url_producao: str
    url_solicitacoes: str
    url_pendencias: str

    # Seletores do formulário de produção
    sel_mes: str
    sel_dia_de: str
    sel_dia_ate: str
    sel_pesquisar: str

    # Seletores do relatório de pendências
    # IMPORTANT: JSF IDs (j_idt*) are server-generated and may change after a
    # SAVI update. Verify every selector below by inspecting the live page
    # before running.
    pend_sel_user_code: str
    pend_sel_search_user: str
    pend_sel_mes: str
    pend_sel_situacao: str
    pend_sel_pesquisar: str
    pend_sel_pagination: str
    pend_sel_total: str
    pend_exec_pendente: str

    # Diretórios / arquivos
    user_data_dir: Path = BASE_DIR / "user-data"
    landing_dir: Path = BASE_DIR / "data" / "landing"
    warehouse_path: Path = BASE_DIR / "data" / "warehouse.duckdb"
    tabela_valores_path: Path = BASE_DIR / "data" / "reference" / "tabela_valores.csv"

    # Camada gold (PostgreSQL) — serving layer para BI/consultas, alimentada a
    # partir do warehouse DuckDB (bronze/silver).
    postgres_dsn: str = "postgresql://clinic:clinic@localhost:5432/clinic_finance"

    def model_post_init(self, __context) -> None:
        for directory in (
            self.user_data_dir,
            self.landing_dir,
            self.warehouse_path.parent,
            self.tabela_valores_path.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
