from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("db-snooper")
except PackageNotFoundError:
    # Keep this fallback aligned with pyproject.toml for source-tree execution.
    __version__ = "0.0.1"

from db_snooper.api import generate_profile, generate_schema_links
from db_snooper.profiler import ProfileOptions, profile_database
from db_snooper.schema_linker import SchemaLinkOptions, link_schema

__all__ = [
    "ProfileOptions",
    "SchemaLinkOptions",
    "__version__",
    "generate_profile",
    "generate_schema_links",
    "link_schema",
    "profile_database",
]
