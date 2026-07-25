from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("db-snooper")
except PackageNotFoundError:
    # Keep this fallback aligned with pyproject.toml for source-tree execution.
    __version__ = "0.0.1"

from db_snooper.api import generate_profile, generate_schema_links
from db_snooper.linking import SchemaLinkOptions, link_schema
from db_snooper.permissions import PermissionReport, check_permissions
from db_snooper.profiling import ProfileOptions, profile_database

__all__ = [
    "PermissionReport",
    "ProfileOptions",
    "SchemaLinkOptions",
    "__version__",
    "check_permissions",
    "generate_profile",
    "generate_schema_links",
    "link_schema",
    "profile_database",
]
