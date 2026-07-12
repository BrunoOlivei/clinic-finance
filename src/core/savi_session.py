from contextlib import contextmanager

from playwright.sync_api import (BrowserContext, Page, TimeoutError,
                                 sync_playwright)

from src.core.config import settings
from src.core.logger import logger


@contextmanager
def log_step(description: str):
    """
    Context manager que loga o resultado de um passo de interação com a
    página (sucesso ou falha) e relança a exceção original, se houver.
    """
    try:
        yield
    except TimeoutError:
        logger.exception("Falha ao {}", description)
        raise
    except Exception:
        logger.exception("Erro inesperado ao {}", description)
        raise
    else:
        logger.info("{} concluído", description)


class SaviSession:
    def __init__(self, user_data_dir: str = settings.user_data_dir):
        self.user_data_dir = user_data_dir
        self._playwright = None
        self._context: BrowserContext | None = None
        self.page: Page | None = None

    def open(self) -> None:
        """
        Starts Playwright and opens Chromium in headed mode with persistent session.
        """
        self._playwright = sync_playwright().start()
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=False,
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
        self.page = (
            self._context.pages[0] if self._context.pages else self._context.new_page()
        )

    def close(self) -> None:
        try:
            if self._context:
                self._context.close()
        finally:
            if self._playwright:
                self._playwright.stop()
            self._playwright = None
            self._context = None

    def __enter__(self) -> "SaviSession":
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            logger.warning(
                f"Sessão encerrada por exceção: {exc_type.__name__}: {exc_value}"
            )
        else:
            logger.info("Sessão encerrada normalmente.")
        self.close()

    def login(self) -> None:
        self.page.goto(settings.url_login)
        self.page.fill(settings.field_username, settings.username.get_secret_value())
        self.page.fill(settings.field_password, settings.password.get_secret_value())
        logger.info("Acesse o navegador e resolva o CAPTCHA.")
        logger.info("Quando estiver dentro do sistema, volte aqui.")
        input("Aperte Enter quando estiver logado... ")

    def _assert_logged_in(self) -> None:
        """
        Checks whether the session is still authenticated.

        Raises:
            RuntimeError: If the current URL contains "login", indicating the
                server redirected to the authentication screen.
        """
        if "login" in self.page.url:
            raise RuntimeError("Sessão expirada — rode novamente e faça o login.")
