from pydantic import BaseSettings, AnyHttpUrl
from typing import Optional, Any, List
import os
import logging


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file.

    Use `Settings()` to access values. Secrets should be provided via
    environment variables (CI or host) or a secrets manager such as Vault.
    """

    APP_ENV: str = "production"
    DEBUG: bool = False
    SECRET_KEY: Optional[str] = None
    VAULT_ADDR: Optional[AnyHttpUrl] = None
    VAULT_TOKEN: Optional[str] = None
    GHCR_TOKEN: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_HOSTS: List[str] = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def get_env(name: str, default: Any = None) -> Any:
    """Return environment setting or provided default."""
    return os.getenv(name, getattr(settings, name, default))


def get_secret(name: str, vault_path: Optional[str] = None) -> Optional[str]:
    """Resolve a secret value.

    Resolution order:
    1. Environment variable (e.g. `SECRET_KEY`)
    2. Vault (if `VAULT_ADDR` and `VAULT_TOKEN` are configured)

    ``vault_path`` is optional and defaults to the lower-cased name.
    """
    # 1) environment variable
    v = os.getenv(name)
    if v:
        return v

    # 2) try Vault
    if settings.VAULT_ADDR and settings.VAULT_TOKEN:
        try:
            # import here to avoid circular imports when module is imported
            from .vault_client import fetch_secret

            path = vault_path or name.lower()
            data = fetch_secret(path)
            if isinstance(data, dict):
                # try exact key, common 'value', or first item
                return data.get(name) or data.get("value") or (next(iter(data.values())) if data else None)
            return data
        except Exception:
            # avoid raising at import time; callers can handle missing secrets
            return None

    return None


# Post-load resolution and sanity checks
# Try to resolve SECRET_KEY from environment or Vault if not provided,
# and enforce that production deployments have a SECRET_KEY set.
_logger = logging.getLogger(__name__)
if not settings.SECRET_KEY:
    _env_secret = os.getenv("SECRET_KEY")
    if _env_secret:
        try:
            setattr(settings, "SECRET_KEY", _env_secret)
        except Exception:
            _logger.warning(
                "Unable to assign SECRET_KEY from environment to settings")
    elif settings.VAULT_ADDR and settings.VAULT_TOKEN:
        try:
            from .vault_client import fetch_secret

            _vault_data = fetch_secret("SECRET_KEY")
            if isinstance(_vault_data, dict):
                _vault_secret = _vault_data.get("SECRET_KEY") or _vault_data.get(
                    "value") or (next(iter(_vault_data.values())) if _vault_data else None)
            else:
                _vault_secret = _vault_data
            if _vault_secret:
                try:
                    setattr(settings, "SECRET_KEY", _vault_secret)
                except Exception:
                    _logger.warning(
                        "Unable to assign SECRET_KEY from Vault to settings")
        except Exception:
            _logger.warning(
                "Vault lookup for SECRET_KEY failed; continuing without secret")

if settings.APP_ENV and settings.APP_ENV.lower() == "production" and not settings.SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY must be set in production (provide SECRET_KEY env var or configure Vault)")
