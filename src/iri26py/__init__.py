from importlib.metadata import version

try:
    __version__ = version("iri26py")
except Exception:
    __version__ = "unknown"

from .download import check_files
from .base import Iri2026
from .utils import alt_grid
from . import settings
check_files()

__all__ = [
    "Iri2026", "settings",
    "alt_grid", "check_files",
    "__version__",
]
