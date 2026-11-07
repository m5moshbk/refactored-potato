-- M5mOsH AI Capability Registry
-- Phase B audit-log TRUNCATE protection regression tests.
-- Run only after schema.sql, Phase A, and migrations/phase_b_audit_truncate_protection.sql.
-- All fixture changes are rolled back.

\set ON_ERROR_STOP on
BEGIN;

CREATE FUNCTION pg_temp.assert_true(condition BOOLEAN, assertion_name TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    IF condition IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION 'ASSERTION FAILED: %', assertion_name;
    END IF;
END;
$$;

CREATE FUNCTION pg_temp.assert_raises(command_text TEXT, expected_message TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
    actual_message TEXT;
BEGIN
    BEGIN
        EXECUTE command_text;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS actual_message = MESSAGE_TEXT;
        IF position(expected_message IN actual_message) = 0 THEN
            RAISE EXCEPTION 'ASSERTION FAILED: expected "%", got "%"',
                expected_message, actual_message;
        END IF;
        RETURN;
    END;
    RAISE EXCEPTION 'ASSERTION FAILED: command unexpectedly succeeded: %',
        command_text;
END;
$$;

INSERT INTO audit_events (id, event_type, actor, event_details)
VALUES (
    'b6000000-0000-4000-8000-000000000001',
    'phase_b_truncate_regression',
    'phase_b_test',
    '{"fixture": true}'::jsonb
);

SELECT pg_temp.assert_true(
    EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgrelid = 'audit_events'::regclass
          AND tgname = 'trg_audit_no_truncate'
          AND NOT tgisinternal
          AND (tgtype & 32) = 32
          AND tgenabled <> 'D'
    ),
    'audit_events has an enabled statement-level TRUNCATE trigger'
);

SELECT pg_temp.assert_raises(
    'TRUNCATE TABLE audit_events',
    'audit_events is append-only'
);

SELECT pg_temp.assert_true(
    (SELECT count(*) = 1
     FROM audit_events
     WHERE id = 'b6000000-0000-4000-8000-000000000001'),
    'rejected TRUNCATE preserves the existing audit event'
);

ROLLBACK;

\echo 'PASS: Phase B audit TRUNCATE protection tests completed; fixtures rolled back.'
