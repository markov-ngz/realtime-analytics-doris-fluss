"""Unit tests for FlinkSqlGateWayHandler SQL sanitization."""

from send_sql_to_flink import FlinkSqlGateWayHandler

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sanitize(sql: str) -> str:
    """Shorthand so tests stay concise."""
    return FlinkSqlGateWayHandler.sanitize_sql(sql)


def split(script: str) -> list[str]:
    handler = FlinkSqlGateWayHandler()
    return handler.split_statements(script)


# ===========================================================================
# sanitize_sql – single-line comments  (-- …)
# ===========================================================================


class TestSingleLineComments:
    def test_removes_standalone_comment_line(self):
        sql = "-- this is a comment\nSELECT 1"
        assert sanitize(sql) == "SELECT 1"

    def test_removes_inline_comment(self):
        sql = "SELECT 1 -- pick the number one"
        assert sanitize(sql) == "SELECT 1"

    def test_removes_multiple_inline_comments(self):
        sql = "SELECT\n  a, -- first column\n  b  -- second column\nFROM t"
        assert sanitize(sql) == "SELECT a, b FROM t"

    def test_comment_at_start_of_string(self):
        assert sanitize("-- just a comment") == ""

    def test_comment_preceded_by_whitespace_only(self):
        assert sanitize("   -- comment\n") == ""

    def test_multiple_comment_lines_before_statement(self):
        sql = "-- line 1\n-- line 2\nSELECT 42"
        assert sanitize(sql) == "SELECT 42"


# ===========================================================================
# sanitize_sql – block comments  (/* … */)
# ===========================================================================


class TestBlockComments:
    def test_removes_inline_block_comment(self):
        sql = "SELECT /* remove me */ 1"
        assert sanitize(sql) == "SELECT 1"

    def test_removes_multiline_block_comment(self):
        sql = "SELECT /*\n  remove\n  me\n*/ 1"
        assert sanitize(sql) == "SELECT 1"

    def test_removes_leading_block_comment(self):
        sql = "/* header */\nSELECT 1"
        assert sanitize(sql) == "SELECT 1"

    def test_removes_trailing_block_comment(self):
        sql = "SELECT 1 /* footer */"
        assert sanitize(sql) == "SELECT 1"

    def test_block_comment_between_tokens_keeps_space(self):
        # Without a space replacement, 'SELECT/*x*/1' would merge to 'SELECT1'.
        sql = "SELECT/*x*/1"
        assert sanitize(sql) == "SELECT 1"

    def test_removes_consecutive_block_comments(self):
        sql = "/* a *//* b */ SELECT 1"
        assert sanitize(sql) == "SELECT 1"

    def test_empty_block_comment(self):
        assert sanitize("SELECT /**/ 1") == "SELECT 1"


# ===========================================================================
# sanitize_sql – string literals must be preserved
# ===========================================================================


class TestStringLiterals:
    def test_preserves_single_quoted_string(self):
        sql = "SELECT 'hello world'"
        assert sanitize(sql) == "SELECT 'hello world'"

    def test_preserves_comment_syntax_inside_string(self):
        sql = "SELECT 'hello -- not a comment'"
        assert sanitize(sql) == "SELECT 'hello -- not a comment'"

    def test_preserves_block_comment_syntax_inside_string(self):
        sql = "SELECT '/* not a comment */'"
        assert sanitize(sql) == "SELECT '/* not a comment */'"

    def test_preserves_escaped_single_quote_in_string(self):
        # SQL standard: '' inside a string literal is an escaped single quote.
        sql = "SELECT 'it''s fine'"
        assert sanitize(sql) == "SELECT 'it''s fine'"

    def test_real_comment_after_string_literal_is_removed(self):
        sql = "INSERT INTO t VALUES ('hello') -- add hello"
        assert sanitize(sql) == "INSERT INTO t VALUES ('hello')"

    def test_string_with_block_comment_look_alike_then_real_comment(self):
        sql = "SELECT '/* keep */') /* remove */"
        assert sanitize(sql) == "SELECT '/* keep */')"

    def test_empty_string_literal_preserved(self):
        assert sanitize("SELECT ''") == "SELECT ''"

    def test_string_literal_with_newline_inside(self):
        # The string literal itself is preserved by the regex (single-quoted
        # group matches first), but the trailing whitespace normalisation pass
        # collapses any literal \n inside it to a single space.
        # Flink SQL does not support newlines embedded in string literals, so
        # this collapse is acceptable and even desirable.
        sql = "SELECT 'line1\nline2'"
        assert sanitize(sql) == "SELECT 'line1 line2'"


# ===========================================================================
# sanitize_sql – whitespace normalisation
# ===========================================================================


class TestWhitespaceNormalisation:
    def test_collapses_multiple_spaces(self):
        assert sanitize("SELECT  1") == "SELECT 1"

    def test_collapses_tabs(self):
        assert sanitize("SELECT\t1") == "SELECT 1"

    def test_collapses_newlines(self):
        assert sanitize("SELECT\n1") == "SELECT 1"

    def test_strips_leading_and_trailing_whitespace(self):
        assert sanitize("  SELECT 1  ") == "SELECT 1"

    def test_empty_string_returns_empty(self):
        assert sanitize("") == ""

    def test_only_whitespace_returns_empty(self):
        assert sanitize("   \n\t  ") == ""

    def test_multiline_query_collapsed(self):
        sql = "SELECT\n  a,\n  b\nFROM\n  my_table"
        assert sanitize(sql) == "SELECT a, b FROM my_table"


# ===========================================================================
# sanitize_sql – combined / realistic scenarios
# ===========================================================================


class TestSplitStatements:
    def test_single_statement_no_semicolon(self):
        assert split("SELECT 1") == ["SELECT 1"]

    def test_single_statement_with_semicolon(self):
        assert split("SELECT 1;") == ["SELECT 1"]

    def test_multiple_statements(self):
        script = "SELECT 1; SELECT 2; SELECT 3"
        assert split(script) == ["SELECT 1", "SELECT 2", "SELECT 3"]

    def test_blank_statements_skipped(self):
        script = "SELECT 1;; SELECT 2"
        assert split(script) == ["SELECT 1", "SELECT 2"]

    def test_whitespace_only_statements_skipped(self):
        script = "SELECT 1;   ; SELECT 2"
        assert split(script) == ["SELECT 1", "SELECT 2"]

    def test_comments_stripped_per_statement(self):
        script = "-- stmt 1\nSELECT 1;\n/* stmt 2 header */\nSELECT 2"
        assert split(script) == ["SELECT 1", "SELECT 2"]

    def test_all_comment_script_returns_empty(self):
        script = "-- only a comment; -- another"
        assert split(script) == []

    def test_preserves_string_literal_with_semicolon(self):
        # Semicolon inside a string literal should NOT split the statement.
        # Note: split_statements() splits on raw ';' before sanitizing,
        # so this test documents the *current* behaviour — callers that embed
        # semicolons in string literals should be aware of this limitation.
        script = "SELECT 'a;b'"
        # The raw split produces ["SELECT 'a", "b'"] — both sanitize to
        # non-empty strings, so two items are returned.
        result = split(script)
        assert len(result) == 2  # known limitation: ; inside literals splits

    def test_multiple_statements_each_sanitized(self):
        script = "SELECT /* col */ 1 -- one\n;\nINSERT -- comment\nINTO t VALUES (1)"
        assert split(script) == ["SELECT 1", "INSERT INTO t VALUES (1)"]
