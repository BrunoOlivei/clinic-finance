import json
import logging
import sys
import traceback

import psycopg
from loguru import logger
from psycopg.types.json import Jsonb

from src.core.config import Environment, settings


class InterceptHandler(logging.Handler):
    """
    Redireciona logs da stdlib (playwright, urllib3, etc.) para o loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_back and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class PostgresLogSink:
    """
    Sink do loguru que grava registros WARNING+ na tabela `logs`.

    Usa o texto de exceção montado via `traceback.format_exception` a partir
    do record cru (não da mensagem já formatada pelo loguru), então o dump de
    variáveis locais do `diagnose` nunca chega ao banco — evita persistir
    segredos (ex: settings.password) que por acaso estejam no escopo do erro.
    """

    TABLE_DDL = """
        CREATE TABLE IF NOT EXISTS logs (
            id BIGSERIAL PRIMARY KEY,
            time TIMESTAMPTZ NOT NULL,
            level VARCHAR(10) NOT NULL,
            logger_name TEXT NOT NULL,
            function TEXT NOT NULL,
            line INTEGER NOT NULL,
            message TEXT NOT NULL,
            exception TEXT,
            extra JSONB NOT NULL DEFAULT '{}'::jsonb
        );
        CREATE INDEX IF NOT EXISTS logs_time_idx ON logs (time DESC);
    """

    INSERT_SQL = """
        INSERT INTO logs
            (time, level, logger_name, function, line, message, exception, extra)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    @staticmethod
    def _dumps_extra(extra: dict) -> str:
        # `extra` vem de qualquer `logger.bind(...)` no código, não do
        # loguru — pode conter tipo não serializável em JSON (date, Path,
        # SecretStr...). `default=str` evita que isso derrube o insert
        # silenciosamente numa thread de background (enqueue=True).
        return json.dumps(extra, default=str)

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn = psycopg.connect(dsn, autocommit=True, connect_timeout=5)
        self._conn.execute(self.TABLE_DDL)

    def __call__(self, message) -> None:
        params = self._build_params(message.record)
        try:
            self._conn.execute(self.INSERT_SQL, params)
        except psycopg.OperationalError:
            self._conn = psycopg.connect(self._dsn, autocommit=True, connect_timeout=5)
            self._conn.execute(self.INSERT_SQL, params)

    @staticmethod
    def _build_params(record: dict) -> tuple:
        exception = None
        if record["exception"] is not None:
            exception = "".join(
                traceback.format_exception(
                    record["exception"].type,
                    record["exception"].value,
                    record["exception"].traceback,
                )
            )
        return (
            record["time"],
            record["level"].name,
            record["name"],
            record["function"],
            record["line"],
            record["message"],
            exception,
            Jsonb(record["extra"], dumps=PostgresLogSink._dumps_extra),
        )


class LoggerSetup:
    """
    Configura os sinks do loguru uma única vez, na importação do módulo:
    console legível para humanos + arquivos rotacionados em disco. Outros
    módulos não usam esta classe diretamente — importam `logger` já pronto.
    """

    CONSOLE_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    def __init__(self) -> None:
        self.is_dev = settings.environment is Environment.DEV
        logger.remove()
        self._add_console_sink()
        self._add_file_sink()
        self._add_error_sink()
        self._add_postgres_sink()
        self._intercept_stdlib_logging()

    def _add_console_sink(self) -> None:
        logger.add(
            sys.stderr,
            level=settings.log_level,
            format=self.CONSOLE_FORMAT,
            colorize=True,
            backtrace=self.is_dev,
            diagnose=self.is_dev,
        )

    def _add_file_sink(self) -> None:
        logger.add(
            settings.log_dir / "clinic_finance.log",
            level="DEBUG",
            rotation="10 MB",
            retention="14 days",
            compression="zip",
            enqueue=True,
            serialize=not self.is_dev,
            backtrace=self.is_dev,
            diagnose=self.is_dev,
        )

    def _add_error_sink(self) -> None:
        logger.add(
            settings.log_dir / "errors.log",
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=self.is_dev,
        )

    def _add_postgres_sink(self) -> None:
        try:
            sink = PostgresLogSink(settings.postgres_dsn)
        except psycopg.Error:
            logger.warning("Postgres indisponível — sink de log no banco desativado.")
            return

        logger.add(sink, level="WARNING", enqueue=True)

    @staticmethod
    def _intercept_stdlib_logging() -> None:
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


LoggerSetup()

__all__ = ["logger"]
