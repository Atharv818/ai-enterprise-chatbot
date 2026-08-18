from app.services.sql_safety import is_safe_select, references_only_tenant_tables


def test_allows_simple_select():
    assert is_safe_select("SELECT * FROM doc_abc123;") is True


def test_blocks_delete():
    assert is_safe_select("DELETE FROM doc_abc123;") is False


def test_blocks_drop_table():
    assert is_safe_select("DROP TABLE doc_abc123;") is False


def test_blocks_update():
    assert is_safe_select("UPDATE doc_abc123 SET x = 1;") is False


def test_blocks_multiple_statements():
    assert is_safe_select("SELECT * FROM doc_abc123; DROP TABLE doc_abc123;") is False


def test_blocks_non_select_start():
    assert is_safe_select("EXPLAIN SELECT * FROM doc_abc123;") is False


def test_allowed_table_reference_passes():
    sql = "SELECT * FROM doc_c15bea7b_04b2_46dd_b341_37fe8b129e1c;"
    allowed = ["doc_c15bea7b_04b2_46dd_b341_37fe8b129e1c"]
    assert references_only_tenant_tables(sql, allowed) is True


def test_disallowed_table_reference_blocked():
    sql = "SELECT * FROM doc_c15bea7b_04b2_46dd_b341_37fe8b129e1c;"
    allowed = ["doc_c0ff046c_612f_4554_83ab_df52129eddc7"]
    assert references_only_tenant_tables(sql, allowed) is False

    