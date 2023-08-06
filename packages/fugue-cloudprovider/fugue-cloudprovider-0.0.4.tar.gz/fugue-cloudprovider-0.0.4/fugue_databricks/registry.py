from .execution_engine import DatabricksExecutionEngine
from fugue import register_execution_engine


def register() -> None:
    register_execution_engine(
        "db",
        lambda conf: DatabricksExecutionEngine(conf=conf),
        on_dup="ignore",
    )
    register_execution_engine(
        "databricks",
        lambda conf: DatabricksExecutionEngine(conf=conf),
        on_dup="ignore",
    )
