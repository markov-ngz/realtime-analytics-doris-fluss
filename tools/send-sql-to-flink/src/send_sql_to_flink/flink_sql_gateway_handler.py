import logging
import re
import time

import requests

from send_sql_to_flink.exception import FailedQueryException

logger = logging.getLogger(__name__)


class FlinkSqlGateWayHandler:
    """Handle SQL script submission to Flink REST SQL Gateway."""

    STATEMENT_DELIMITER = ";"
    FETCH_RESULT_DELAY = 5
    SESSION_ENDPOINT = "/v4/sessions"
    OPERATION_ENDPOINT = "/v4/sessions/{session_handle}/statements"
    RESULT_ENDPOINT = (
        "/v4/sessions/{session_handle}/operations/{operation_handle}/result/0"
    )

    # Compiled once at class level for performance.
    # Matches, in priority order:
    #   1. Single-quoted string literals  : '...'  (with '' escape support)
    #   2. Block comments                 : /* ... */
    #   3. Single-line comments           : -- ...
    _SQL_TOKEN_RE = re.compile(
        r"('(?:''|[^'])*')"  # group 1 – string literal (must come first)
        r"|(/\*.*?\*/)"  # group 2 – block comment
        r"|(--[^\n]*)",  # group 3 – single-line comment
        re.DOTALL,
    )

    session_id: str

    def __init__(self, host: str = "localhost", port: int = 8083) -> None:
        self.base_url = f"http://{host}:{port}"

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @classmethod
    def sanitize_sql(cls, sql: str) -> str:
        """Return *sql* with all comments stripped and whitespace normalised.

        String literals are left untouched even when they contain comment-like
        sequences such as ``'hello -- world'`` or ``'/* not a comment */'``.

        The algorithm performs a single left-to-right scan via a compiled regex
        that matches (in priority order):

        * Single-quoted string literals ``'…'`` — reproduced verbatim.
        * Block comments ``/* … */`` — replaced with a single space so that
          tokens on either side of the comment remain separated.
        * Single-line comments ``-- …`` — removed entirely (the newline that
          terminates them is kept so that line-based formatting is preserved).

        After stripping, consecutive whitespace is collapsed to a single space
        and leading/trailing whitespace is removed.
        """

        def _replace(match: re.Match) -> str:
            if match.group(1):
                # String literal — keep as-is.
                return match.group(1)
            if match.group(2):
                # Block comment — replace with a space to avoid merging tokens.
                return " "
            # Single-line comment — drop it (group 3).
            return ""

        stripped = cls._SQL_TOKEN_RE.sub(_replace, sql)
        # Collapse runs of whitespace (spaces, tabs, newlines) to a single space.
        return re.sub(r"\s+", " ", stripped).strip()

    def split_statements(self, script_content: str) -> list[str]:
        """Split *script_content* on ``;`` and sanitize each statement."""
        return [
            sanitized
            for stmt in script_content.split(self.STATEMENT_DELIMITER)
            if (sanitized := self.sanitize_sql(stmt))
        ]

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def execute_sql_script(self, script_content: str) -> bool:
        statements = self.split_statements(script_content)
        logger.info("Starting SQL script execution | statements=%d", len(statements))

        self.open_session()

        try:
            for idx, statement in enumerate(statements, start=1):
                logger.info(
                    "Submitting statement | session=%s | index=%d | sql=%s",
                    self.session_id,
                    idx,
                    statement[:200],
                )

                operation_handle = self.submit_statement(statement)

                logger.info(
                    "Fetching result | session=%s | operation=%s",
                    self.session_id,
                    operation_handle,
                )

                result = self.fetch_result(operation_handle)

                logger.info(
                    "Result fetched | session=%s | operation=%s | result=%s",
                    self.session_id,
                    operation_handle,
                    result,
                )
        finally:
            self.close_session()
            logger.info("Session closed | session=%s", self.session_id)

        return True

    def open_session(self) -> None:
        url = self.base_url + self.SESSION_ENDPOINT
        logger.info("Opening session | url=%s", url)

        response = requests.post(url, json={})
        response.raise_for_status()

        data = response.json()
        self.session_id = data.get("sessionHandle")

        logger.info("Session opened | session=%s", self.session_id)
        logger.debug("Session response payload: %s", data)

    def submit_statement(self, statement: str) -> str:
        url = self.base_url + self.OPERATION_ENDPOINT.format(
            session_handle=self.session_id
        )

        start = time.time()
        response = requests.post(url, json={"statement": statement})
        response.raise_for_status()

        data = response.json()
        operation_handle = data.get("operationHandle")
        duration = time.time() - start

        logger.info(
            "Statement submitted | session=%s | operation=%s | duration=%.2fs",
            self.session_id,
            operation_handle,
            duration,
        )
        logger.debug("Submit response payload: %s", data)

        return operation_handle

    def fetch_result(self, operation_handle: str) -> dict:
        next_uri = self.RESULT_ENDPOINT.format(
            session_handle=self.session_id,
            operation_handle=operation_handle,
        )

        logger.info(
            "Start fetching results | session=%s | operation=%s",
            self.session_id,
            operation_handle,
        )

        result_data = None
        poll_count = 0

        while next_uri:
            poll_count += 1
            url = self.base_url + next_uri

            logger.debug(
                "Polling result | session=%s | operation=%s | attempt=%d",
                self.session_id,
                operation_handle,
                poll_count,
            )

            response = requests.get(url)
            data = response.json()

            if "errors" in data:
                logger.error(
                    "Query failed | session=%s | operation=%s | errors=%s",
                    self.session_id,
                    operation_handle,
                    data["errors"],
                )
                raise FailedQueryException(f"Query failed {operation_handle}")

            result_data = data
            next_uri = data.get("nextResultUri")

            if next_uri:
                time.sleep(self.FETCH_RESULT_DELAY)

        if result_data is None:
            logger.error(
                "No result returned | session=%s | operation=%s",
                self.session_id,
                operation_handle,
            )
            raise ValueError("Could not fetch any result data")

        logger.info(
            "Finished fetching results | session=%s | operation=%s | polls=%d",
            self.session_id,
            operation_handle,
            poll_count,
        )
        logger.debug("Final result payload: %s", result_data)

        return result_data

    def close_session(self) -> None:
        if not self.session_id:
            return

        url = self.base_url + f"{self.SESSION_ENDPOINT}/{self.session_id}"
        logger.info("Closing session | session=%s", self.session_id)

        response = requests.delete(url)

        if response.status_code >= 400:
            logger.warning(
                "Failed to close session cleanly | session=%s | status=%s",
                self.session_id,
                response.status_code,
            )

        self.session_id = ""
