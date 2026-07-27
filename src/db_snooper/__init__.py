from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("db-snooper")
except PackageNotFoundError:
    # Keep this fallback aligned with pyproject.toml for source-tree execution.
    __version__ = "0.0.1"

from db_snooper.api import generate_profile
from db_snooper.permissions import PermissionReport, check_permissions
from db_snooper.profiling import ProfileOptions, profile_database

__all__ = [
    "PermissionReport",
    "ProfileOptions",
    "__version__",
    "check_permissions",
    "generate_profile",
    "profile_database",
]
