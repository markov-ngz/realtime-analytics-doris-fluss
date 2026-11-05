"""Command-line interface for send-sql-to-flink."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from send_sql_to_flink.flink_sql_gateway_handler import FlinkSqlGateWayHandler

logger = logging.getLogger(__name__)

_DEFAULT_LOG_FILE = ".logs"
_DEFAULT_LOG_LEVEL = "INFO"
_DEFAULT_HOST = "localhost"
_DEFAULT_PORT = 8083


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Kept separate from ``parse_args`` so callers (tests, other tools) can
    inspect or extend the parser without triggering a ``sys.exit``.
    """
    parser = argparse.ArgumentParser(
        prog="send-sql-to-flink",
        description="Submit a SQL script to a remote Flink SQL Gateway.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # --- required ---
    parser.add_argument(
        "--filepath",
        required=True,
        type=Path,
        metavar="PATH",
        help="Path to the SQL file to submit.",
    )

    # --- gateway connection ---
    gateway = parser.add_argument_group("gateway")
    gateway.add_argument(
        "--host",
        default=_DEFAULT_HOST,
        help="Flink SQL Gateway host.",
    )
    gateway.add_argument(
        "--port",
        default=_DEFAULT_PORT,
        type=int,
        help="Flink SQL Gateway port.",
    )

    # --- logging ---
    log_group = parser.add_argument_group("logging")
    log_group.add_argument(
        "--log-file",
        default=_DEFAULT_LOG_FILE,
        metavar="PATH",
        help="Append logs to this file.",
    )
    log_group.add_argument(
        "--log-level",
        default=_DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Minimum log level to emit.",
    )

    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse *argv* (defaults to ``sys.argv[1:]``)."""
    return build_parser().parse_args(argv)


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------


def configure_logging(log_file: str, log_level: str) -> None:
    """Configure the root logger.

    Called once inside ``main`` so that importing this module never has the
    side-effect of touching the logging system.

    Unlike ``logging.basicConfig``, this function always takes effect: it
    explicitly constructs and attaches a ``FileHandler`` rather than relying
    on ``basicConfig``, which is a no-op when handlers are already present
    (as is always the case inside a pytest session).
    """
    level = getattr(logging, log_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def read_file(filepath: Path) -> str:
    """Return the text content of *filepath*.

    Raises:
        FileNotFoundError: when the path does not exist.
        IsADirectoryError: when the path resolves to a directory.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"SQL file not found: {filepath}")
    if filepath.is_dir():
        raise IsADirectoryError(f"Expected a file, got a directory: {filepath}")

    return filepath.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint wired via ``pyproject.toml`` ``[project.scripts]``.

    Args:
        argv: argument list override (``None`` → ``sys.argv[1:]``).
              Injecting *argv* makes the entrypoint fully testable without
              monkeypatching ``sys.argv``.
    """
    args = parse_args(argv)

    configure_logging(args.log_file, args.log_level)

    logger.info(
        "Starting | file=%s | host=%s | port=%d",
        args.filepath,
        args.host,
        args.port,
    )

    try:
        sql_script = read_file(args.filepath)
    except (FileNotFoundError, IsADirectoryError) as exc:
        # User-facing error: no traceback, clean exit code 2 (misuse).
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    try:
        handler = FlinkSqlGateWayHandler(host=args.host, port=args.port)
        handler.execute_sql_script(sql_script)
    except Exception as exc:
        # Gateway / network / query errors: log with traceback, exit code 1.
        logger.exception("SQL execution failed")  # exc_info captured implicitly
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    logger.info("Done | file=%s", args.filepath)
