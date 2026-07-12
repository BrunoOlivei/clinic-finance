from playwright.sync_api import sync_playwright, BrowserContext, Page
from src.core.config import settings


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

    def __enter__(self) -> "SaviSession":
        self.open()
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def login(self, username: str, password: str) -> None:
        self.page.goto(settings.url_login)
        # logger.info("Acesse o navegador, faça o login e resolva o CAPTCHA.")
        # logger.info("Quando estiver dentro do sistema, volte aqui.")
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
