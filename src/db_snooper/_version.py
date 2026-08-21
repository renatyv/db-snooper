from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("db-snooper")
except PackageNotFoundError:
    __version__ = "0.0.34"
