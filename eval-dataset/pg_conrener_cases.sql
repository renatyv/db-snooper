-- PostgreSQL test data generation script
-- One table per data type/volume requirement (a single table can't have
-- columns with different row counts).

-- ============================================================
-- Helper: random text of variable length in [min_len, max_len]
-- ============================================================
CREATE OR REPLACE FUNCTION random_text(min_len int, max_len int)
RETURNS text AS $$
DECLARE
    len int := min_len + floor(random() * (max_len - min_len + 1))::int;
BEGIN
    RETURN array_to_string(
        array(
            SELECT chr((65 + floor(random() * 26))::int)
            FROM generate_series(1, len)
        ),
        ''
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION random_name()
RETURNS text AS $$
BEGIN
    RETURN initcap(random_text(4, 8)) || ' ' || initcap(random_text(4, 10));
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION random_address()
RETURNS text AS $$
BEGIN
    RETURN (100 + floor(random() * 9900))::int || ' ' ||
           initcap(random_text(5, 10)) || ' St, ' ||
           initcap(random_text(4, 8)) || ' City';
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 1. 11M rows, int column, values 1-300, indexed
-- ============================================================
CREATE TABLE big_ints (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ival    int NOT NULL
);

INSERT INTO big_ints (ival)
SELECT (1 + floor(random() * 300))::int
FROM generate_series(1, 11000000);

CREATE INDEX idx_big_ints_ival ON big_ints (ival);

-- ============================================================
-- 2. 4M rows, float column, values 1-300, indexed
-- ============================================================
CREATE TABLE floats_ranged (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fval    double precision NOT NULL
);

INSERT INTO floats_ranged (fval)
SELECT 1 + random() * 299
FROM generate_series(1, 4000000);

CREATE INDEX idx_floats_ranged_fval ON floats_ranged (fval);

-- ============================================================
-- 3. 4M rows, float column, uniform distribution, no index
-- ============================================================
CREATE TABLE floats_uniform (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fval    double precision NOT NULL
);

INSERT INTO floats_uniform (fval)
SELECT random()
FROM generate_series(1, 4000000);

-- ============================================================
-- 4. 10 rows, jsonb column {"name": ..., "address": ...}
-- ============================================================
CREATE TABLE json_records (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data    jsonb NOT NULL
);

INSERT INTO json_records (data)
SELECT jsonb_build_object(
    'name', random_name(),
    'address', random_address()
)
FROM generate_series(1, 10);

-- ============================================================
-- 5. 100 rows, int[] column, variable length
-- ============================================================
CREATE TABLE int_arrays (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ints    int[] NOT NULL
);

INSERT INTO int_arrays (ints)
SELECT array(
    SELECT (1 + floor(random() * 1000))::int
    FROM generate_series(1, 1 + floor(random() * 20)::int)
)
FROM generate_series(1, 100);

-- ============================================================
-- 6. 100 rows, text[] column, variable length
-- ============================================================
CREATE TABLE string_arrays (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    strs    text[] NOT NULL
);

INSERT INTO string_arrays (strs)
SELECT array(
    SELECT random_text(3, 12)
    FROM generate_series(1, 1 + floor(random() * 20)::int)
)
FROM generate_series(1, 100);

-- ============================================================
-- 7. 1M rows, text column, random length 1-300 chars
-- ============================================================
CREATE TABLE random_texts (
    id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    txt     text NOT NULL
);

INSERT INTO random_texts (txt)
SELECT random_text(1, 300)
FROM generate_series(1, 1000000);

-- ============================================================
-- Optional cleanup of helper functions once data is loaded
-- ============================================================
-- DROP FUNCTION random_text(int, int);
-- DROP FUNCTION random_name();
-- DROP FUNCTION random_address();
