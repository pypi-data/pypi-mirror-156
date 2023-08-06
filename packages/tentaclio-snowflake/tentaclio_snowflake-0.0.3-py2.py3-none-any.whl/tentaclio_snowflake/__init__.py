"""This package implements the tentaclio snowflake client """
from tentaclio import *  # noqa

from .clients.snowflake_client import SnowflakeClient


# Add DB registry
DB_REGISTRY.register("snowflake", SnowflakeClient)  # type: ignore
