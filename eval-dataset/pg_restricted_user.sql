\set restricted_user restricted_user
\set restricted_password db_snooper_restricted

SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L',
    :'restricted_user',
    :'restricted_password'
)
WHERE NOT EXISTS (
    SELECT FROM pg_catalog.pg_roles WHERE rolname = :'restricted_user'
)
\gexec

GRANT CONNECT ON DATABASE :"DBNAME" TO :"restricted_user";
GRANT USAGE ON SCHEMA corener_cases TO :"restricted_user";
GRANT SELECT ON ALL TABLES IN SCHEMA corener_cases TO :"restricted_user";
REVOKE SELECT ON corener_cases.reaction_compound_smiles_bbi_features
    FROM :"restricted_user";

-- PostgreSQL grants pg_stats to PUBLIC, and has no explicit DENY. This changes
-- the database-wide default; restore it later with:
-- GRANT SELECT ON pg_catalog.pg_stats TO PUBLIC;
REVOKE SELECT ON pg_catalog.pg_stats FROM PUBLIC;
