SELECT
    db.oid AS database_id,
    db.datname AS database_name,
    ns.oid::TEXT AS schema_id,
    ns.nspname AS schema_name,
    u.usename AS schema_owner,
    u.usesysid AS schema_owner_id,
    de.description AS "comment"
FROM pg_catalog.pg_namespace AS ns
    CROSS JOIN pg_catalog.pg_database AS db
    JOIN pg_catalog.pg_user AS u ON u.usesysid = ns.nspowner
    LEFT JOIN pg_catalog.pg_description AS de ON de.classoid = ns.oid
WHERE TRUE
    AND db.datname = CURRENT_DATABASE()
    AND ns.nspname NOT LIKE 'pg_%%'
    AND ns.nspname NOT IN ('catalog_history', 'information_schema')
