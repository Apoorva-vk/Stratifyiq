import os


def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    """Runtime settings read from environment variables.

    DATABASE_URL defaults to SQLite for local development. Set it to a
    PostgreSQL URL (postgresql+psycopg2://user:pass@host/db) for production.

    AI_PROVIDER chooses the assistant's brain: none (default), ollama, or anthropic.

    Email: set SMTP_HOST, SMTP_FROM and usually SMTP_USER / SMTP_PASSWORD to send real
    invitation and password-reset emails. Without SMTP the email is printed in the
    backend window instead. EMAIL_DEV_FALLBACK=true also returns the link or token in
    the API response so the flow can be tested; turn it off in production.
    """

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./stratifyiq.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-only-change-me-to-a-32-plus-character-secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))

    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "none")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")

    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:5173")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "")
    EMAIL_DEV_FALLBACK: bool = _flag("EMAIL_DEV_FALLBACK", "true")

    # Jira Cloud. The API token is read from the environment only; never put it in code.
    JIRA_BASE_URL: str = os.getenv("JIRA_BASE_URL", "")
    JIRA_EMAIL: str = os.getenv("JIRA_EMAIL", "")
    JIRA_API_TOKEN: str = os.getenv("JIRA_API_TOKEN", "")


settings = Settings()
