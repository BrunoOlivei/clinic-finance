import logging
import sys

from loguru import logger

from src.core.config import Environment, settings


class InterceptHandler(logging.Handler):
    """Redireciona logs da stdlib (playwright, urllib3, etc.) para o loguru."""

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


class LoggerSetup:
    """Configura os sinks do loguru uma única vez, na importação do módulo:
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

    @staticmethod
    def _intercept_stdlib_logging() -> None:
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


LoggerSetup()

__all__ = ["logger"]
