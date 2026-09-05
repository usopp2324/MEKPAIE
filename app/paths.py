"""Application data paths with a Windows-safe fallback."""
import os
from pathlib import Path


def _create_app_dir() -> Path:
    """Return a writable application directory, preferring Documents."""
    candidates = [
        Path.home() / "Documents" / "MEKPAIE",
        Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MEKPAIE",
    ]

    last_error = None
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError as error:
            last_error = error

    raise OSError("Impossible de créer le dossier de données de MEKPAIE") from last_error


APP_DIR = _create_app_dir()
DATA_DIR = APP_DIR / "data"
BACKUP_DIR = APP_DIR / "Backups"
PDF_DIR = APP_DIR / "Bulletins"
LOGO_DIR = APP_DIR / "logos"