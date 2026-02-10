from dle.sql_parser import extract_lineage, parse_sql_statements


def test_create_table_as_select_with_join():
    sql = """
    CREATE TABLE target_table AS
    SELECT a.id, b.name
    FROM source_a a
    JOIN source_b b ON a.id = b.id;
    """
    statements = parse_sql_statements(sql, "postgres")
    lineage = extract_lineage(statements[0], "postgres")

    assert lineage.targets == {"target_table"}
    assert lineage.sources == {"source_a", "source_b"}


def test_cte_is_not_reported_as_source():
    sql = """
    WITH cte AS (
        SELECT * FROM raw_orders
    )
    INSERT INTO final_orders
    SELECT cte.id, dim.segment
    FROM cte
    JOIN dim_customers dim ON cte.id = dim.id;
    """
    statements = parse_sql_statements(sql, "postgres")
    lineage = extract_lineage(statements[0], "postgres")

    assert lineage.targets == {"final_orders"}
    assert lineage.sources == {"raw_orders", "dim_customers"}
