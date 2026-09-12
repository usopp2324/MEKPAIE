"""Application data paths."""
from pathlib import Path


def _create_app_dir() -> Path:
    """Return the writable application directory in the user's Documents folder."""
    candidates = [
        Path.home() / "Documents",
        Path.home() / "OneDrive" / "Documents",
    ]

    for docs_dir in candidates:
        try:
            docs_dir.mkdir(parents=True, exist_ok=True)
            app_dir = docs_dir / "MEKPAIE"
            app_dir.mkdir(parents=True, exist_ok=True)
            return app_dir
        except OSError:
            continue

    fallback = Path.home() / "MEKPAIE"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


APP_DIR = _create_app_dir()
DATA_DIR = APP_DIR / "data"
BACKUP_DIR = APP_DIR / "Backups"
PDF_DIR = APP_DIR / "Bulletins"
LOGO_DIR = APP_DIR / "logos"