"""send-sql-to-flink — submit SQL scripts to a Flink SQL Gateway."""

from send_sql_to_flink.cli import main
from send_sql_to_flink.flink_sql_gateway_handler import FlinkSqlGateWayHandler

__all__ = ["FailedQueryException", "FlinkSqlGateWayHandler", "main"]
