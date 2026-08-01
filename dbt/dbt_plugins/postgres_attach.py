from typing import Any, Dict, Optional

from duckdb import DuckDBPyConnection

from dbt.adapters.duckdb.plugins import BasePlugin

PG_EXT = "postgres"


class Plugin(BasePlugin):
    """
    Versão corrigida do plugin `postgres` embutido no dbt-duckdb 1.10.1.

    O plugin original sobrescreve `__init__(self, name, plugin_config)` sem
    aceitar o argumento `credentials` que `BasePlugin.create()` sempre passa,
    o que quebra com `TypeError: Plugin.__init__() got an unexpected keyword
    argument 'credentials'`. Aqui não sobrescrevemos `__init__` — deixamos o
    da classe base (que já aceita `credentials` e chama `initialize()`
    corretamente) e só implementamos `initialize`/`configure_connection`,
    como o próprio `BasePlugin` documenta que subclasses devem fazer.
    """

    def initialize(self, config: Dict[str, Any]):
        self._dsn: str = config["dsn"]
        self._duckdb_alias: str = config.get("duckdb_alias", "postgres_db")
        self._pg_schema: Optional[str] = config.get("pg_schema")
        self._read_only: bool = config.get("read_only", False)

    def configure_connection(self, conn: DuckDBPyConnection):
        conn.install_extension(PG_EXT)
        conn.load_extension(PG_EXT)

        options = ["TYPE POSTGRES"]
        if self._pg_schema:
            options.append(f"SCHEMA '{self._pg_schema}'")
        if self._read_only:
            options.append("READ_ONLY")

        conn.execute(
            f"ATTACH '{self._dsn}' AS {self._duckdb_alias} ({', '.join(options)});"
        )
