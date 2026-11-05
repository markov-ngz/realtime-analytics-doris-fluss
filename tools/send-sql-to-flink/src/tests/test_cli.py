"""Tests for send_sql_to_flink.cli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from send_sql_to_flink.cli import (
    _DEFAULT_HOST,
    _DEFAULT_LOG_FILE,
    _DEFAULT_LOG_LEVEL,
    _DEFAULT_PORT,
    build_parser,
    configure_logging,
    main,
    parse_args,
    read_file,
)

# ===========================================================================
# build_parser / parse_args
# ===========================================================================


class TestBuildParser:
    def test_returns_argument_parser(self):
        import argparse

        assert isinstance(build_parser(), argparse.ArgumentParser)

    def test_filepath_is_required(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args([])
        assert exc_info.value.code != 0

    def test_filepath_parsed_as_path(self):
        args = parse_args(["--filepath", "/tmp/job.sql"])
        assert isinstance(args.filepath, Path)
        assert args.filepath == Path("/tmp/job.sql")

    def test_defaults(self):
        args = parse_args(["--filepath", "job.sql"])
        assert args.host == _DEFAULT_HOST
        assert args.port == _DEFAULT_PORT
        assert args.log_file == _DEFAULT_LOG_FILE
        assert args.log_level == _DEFAULT_LOG_LEVEL

    def test_host_override(self):
        args = parse_args(["--filepath", "job.sql", "--host", "flink-gw"])
        assert args.host == "flink-gw"

    def test_port_override(self):
        args = parse_args(["--filepath", "job.sql", "--port", "9999"])
        assert args.port == 9999

    def test_port_must_be_integer(self):
        with pytest.raises(SystemExit):
            parse_args(["--filepath", "job.sql", "--port", "abc"])

    def test_log_level_choices(self):
        for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            args = parse_args(["--filepath", "job.sql", "--log-level", level])
            assert args.log_level == level

    def test_invalid_log_level_rejected(self):
        with pytest.raises(SystemExit):
            parse_args(["--filepath", "job.sql", "--log-level", "VERBOSE"])

    def test_log_file_override(self):
        args = parse_args(["--filepath", "job.sql", "--log-file", "my.log"])
        assert args.log_file == "my.log"


# ===========================================================================
# configure_logging
# ===========================================================================


class TestConfigureLogging:
    """``configure_logging`` uses an explicit FileHandler, not ``basicConfig``.

    ``basicConfig`` is a no-op when the root logger already has handlers
    (which is always true inside a pytest session). By constructing the handler
    explicitly, ``configure_logging`` always takes effect — and the tests can
    assert on the resulting root-logger state without fighting pytest's own
    log-capture machinery.

    Each test tears down the handler it added so the root logger is left in
    the same state it was found.
    """

    @pytest.fixture(autouse=True)
    def remove_added_handler(self):
        """Remove only the FileHandler that configure_logging adds."""
        import logging

        root = logging.getLogger()
        before = set(root.handlers)
        yield
        for h in set(root.handlers) - before:
            h.close()
            root.removeHandler(h)

    def test_sets_root_logger_level(self, tmp_path):
        import logging

        configure_logging(str(tmp_path / "test.log"), "DEBUG")
        assert logging.getLogger().level == logging.DEBUG

    def test_adds_file_handler(self, tmp_path):
        import logging

        log_file = str(tmp_path / "out.log")
        configure_logging(log_file, "INFO")
        file_handlers = [
            h
            for h in logging.getLogger().handlers
            if isinstance(h, logging.FileHandler) and h.baseFilename == log_file
        ]
        assert len(file_handlers) == 1

    def test_creates_log_file(self, tmp_path):
        import logging

        log_file = str(tmp_path / "out.log")
        configure_logging(log_file, "INFO")
        logging.getLogger("_test_configure_").info("hello")
        assert Path(log_file).exists()


# ===========================================================================
# read_file
# ===========================================================================


class TestReadFile:
    def test_reads_existing_file(self, tmp_path):
        f = tmp_path / "job.sql"
        f.write_text("SELECT 1", encoding="utf-8")
        assert read_file(f) == "SELECT 1"

    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="SQL file not found"):
            read_file(tmp_path / "missing.sql")

    def test_raises_is_a_directory(self, tmp_path):
        with pytest.raises(IsADirectoryError, match="Expected a file"):
            read_file(tmp_path)

    def test_reads_utf8_content(self, tmp_path):
        f = tmp_path / "job.sql"
        content = "SELECT 'héllo wörld'"
        f.write_text(content, encoding="utf-8")
        assert read_file(f) == content

    def test_reads_multiline_content(self, tmp_path):
        f = tmp_path / "job.sql"
        content = "SELECT 1;\nSELECT 2;\n"
        f.write_text(content, encoding="utf-8")
        assert read_file(f) == content


# ===========================================================================
# main — integration-level (handler mocked)
# ===========================================================================


class TestMain:
    """Tests for the top-level ``main`` entrypoint.

    ``FlinkSqlGateWayHandler`` is always mocked so these tests run without
    a live gateway.
    """

    _HANDLER_PATH = "send_sql_to_flink.cli.FlinkSqlGateWayHandler"

    def _write_sql(self, tmp_path: Path, content: str = "SELECT 1") -> Path:
        f = tmp_path / "job.sql"
        f.write_text(content, encoding="utf-8")
        return f

    # --- happy path ---

    def test_happy_path_calls_handler(self, tmp_path):
        sql_file = self._write_sql(tmp_path)
        mock_handler = MagicMock()

        with patch(self._HANDLER_PATH, return_value=mock_handler) as mock_cls:
            main(["--filepath", str(sql_file)])

        mock_cls.assert_called_once_with(host=_DEFAULT_HOST, port=_DEFAULT_PORT)
        mock_handler.execute_sql_script.assert_called_once_with("SELECT 1")

    def test_host_and_port_forwarded_to_handler(self, tmp_path):
        sql_file = self._write_sql(tmp_path)
        mock_handler = MagicMock()

        with patch(self._HANDLER_PATH, return_value=mock_handler) as mock_cls:
            main(["--filepath", str(sql_file), "--host", "remote", "--port", "9000"])

        mock_cls.assert_called_once_with(host="remote", port=9000)

    def test_file_content_passed_verbatim(self, tmp_path):
        content = "INSERT INTO t SELECT * FROM s"
        sql_file = self._write_sql(tmp_path, content)
        mock_handler = MagicMock()

        with patch(self._HANDLER_PATH, return_value=mock_handler):
            main(["--filepath", str(sql_file)])

        mock_handler.execute_sql_script.assert_called_once_with(content)

    # --- file errors → exit code 2 ---

    def test_missing_file_exits_2(self, tmp_path, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--filepath", str(tmp_path / "no_such.sql")])
        assert exc_info.value.code == 2

    def test_missing_file_prints_to_stderr(self, tmp_path, capsys):
        with pytest.raises(SystemExit):
            main(["--filepath", str(tmp_path / "no_such.sql")])
        assert "error:" in capsys.readouterr().err

    def test_directory_as_filepath_exits_2(self, tmp_path, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--filepath", str(tmp_path)])
        assert exc_info.value.code == 2

    # --- gateway errors → exit code 1 ---

    def test_gateway_exception_exits_1(self, tmp_path, capsys):
        sql_file = self._write_sql(tmp_path)
        mock_handler = MagicMock()
        mock_handler.execute_sql_script.side_effect = RuntimeError("gateway down")

        with (
            patch(self._HANDLER_PATH, return_value=mock_handler),
            pytest.raises(SystemExit) as exc_info,
        ):
            main(["--filepath", str(sql_file)])

        assert exc_info.value.code == 1

    def test_gateway_exception_prints_to_stderr(self, tmp_path, capsys):
        sql_file = self._write_sql(tmp_path)
        mock_handler = MagicMock()
        mock_handler.execute_sql_script.side_effect = RuntimeError("gateway down")

        with (
            patch(self._HANDLER_PATH, return_value=mock_handler),
            pytest.raises(SystemExit),
        ):
            main(["--filepath", str(sql_file)])

        assert "gateway down" in capsys.readouterr().err

    # --- no-arg call triggers argparse help/error ---

    def test_no_args_exits_nonzero(self):
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code != 0
