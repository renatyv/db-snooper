from __future__ import annotations

from sqlalchemy import create_engine, text

from db_snooper.schema_linker import SchemaLinkOptions, link_schema


def test_declared_foreign_key_links_are_reported() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table customers (id integer primary key, name text)"))
        conn.execute(
            text(
                "create table orders ("
                "id integer primary key, "
                "customer_id integer not null references customers(id))"
            )
        )

    output = link_schema(engine, SchemaLinkOptions())

    assert "## Declared PK/FK Links" in output
    assert "| orders.customer_id | customers.id | customer_id -> id | 1.00 | foreign key |" in output


def test_infers_customer_id_to_customer_id_link_without_foreign_key() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table customers (id integer primary key, name text)"))
        conn.execute(text("create table orders (id integer primary key, customer_id integer not null)"))
        for customer_id in range(1, 6):
            conn.execute(text("insert into customers values (:id, :name)"), {"id": customer_id, "name": f"c{customer_id}"})
        for order_id in range(1, 11):
            conn.execute(
                text("insert into orders values (:id, :customer_id)"),
                {"id": order_id, "customer_id": ((order_id - 1) % 5) + 1},
            )

    output = link_schema(engine, SchemaLinkOptions())

    assert "| orders.customer_id | customers.id | 1.00 |" in output
    assert "table-name id match" in output


def test_mismatched_types_are_skipped() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table customers (id integer primary key)"))
        conn.execute(text("create table orders (id integer primary key, customer_id text not null)"))
        conn.execute(text("insert into customers values (1)"))
        conn.execute(text("insert into orders values (1, '1')"))

    output = link_schema(engine, SchemaLinkOptions())

    assert "orders.customer_id | customers.id" not in output
    assert "No inferred links found." in output


def test_low_cardinality_columns_without_name_signal_are_suppressed() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table a (id integer primary key, status text not null)"))
        conn.execute(text("create table b (id integer primary key, state text not null)"))
        for row_id in range(1, 21):
            value = "open" if row_id % 2 else "closed"
            conn.execute(text("insert into a values (:id, :status)"), {"id": row_id, "status": value})
            conn.execute(text("insert into b values (:id, :state)"), {"id": row_id, "state": value})

    output = link_schema(engine, SchemaLinkOptions())

    assert "a.status | b.state" not in output


def test_include_and_exclude_tables() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("create table keep_parent (id integer primary key)"))
        conn.execute(text("create table keep_child (id integer primary key, parent_id integer references keep_parent(id))"))
        conn.execute(text("create table skip_child (id integer primary key, parent_id integer references keep_parent(id))"))

    output = link_schema(
        engine,
        SchemaLinkOptions(
            include_tables=frozenset({"keep_parent", "keep_child", "skip_child"}),
            exclude_tables=frozenset({"skip_child"}),
        ),
    )

    assert "keep_child.parent_id" in output
    assert "skip_child.parent_id" not in output
