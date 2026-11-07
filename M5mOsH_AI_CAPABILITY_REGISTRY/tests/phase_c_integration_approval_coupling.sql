-- M5mOsH AI Capability Registry
-- Phase C integration/technology approval coupling regression tests.
-- Run after schema.sql and Phase A, B, and C migrations.
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

-- Beta remains discovered: neither approval nor activation may proceed.
INSERT INTO technologies (id, canonical_key, name, category)
VALUES ('c1000000-0000-4000-8000-000000000002',
        'phase-c.beta', 'Phase C Discovered Technology', 'test');

INSERT INTO integrations (id, technology_id, target_project)
VALUES ('c7000000-0000-4000-8000-000000000002',
        'c1000000-0000-4000-8000-000000000002',
        'phase-c-negative-project');

SELECT pg_temp.assert_raises(
    $sql$UPDATE integrations
        SET integration_status = 'approved'
        WHERE id = 'c7000000-0000-4000-8000-000000000002'$sql$,
    'Integration activation requires technology lifecycle approved or integrated'
);

SELECT pg_temp.assert_true(
    (SELECT integration_status = 'proposed'
     FROM integrations
     WHERE id = 'c7000000-0000-4000-8000-000000000002'),
    'rejected activation leaves the integration proposed'
);

-- Alpha receives a valid approval evidence chain.
INSERT INTO technologies (id, canonical_key, name, category)
VALUES ('c1000000-0000-4000-8000-000000000001',
        'phase-c.alpha', 'Phase C Approved Technology', 'test');

INSERT INTO technology_versions
    (id, technology_id, version_name, support_status, verified_at)
VALUES ('c2000000-0000-4000-8000-000000000001',
        'c1000000-0000-4000-8000-000000000001',
        '1.0', 'active', NOW());

INSERT INTO sources
    (id, technology_id, version_id, source_type, source_url,
     verification_status, checked_at)
VALUES ('c3000000-0000-4000-8000-000000000001',
        'c1000000-0000-4000-8000-000000000001',
        'c2000000-0000-4000-8000-000000000001',
        'official_documentation', 'https://example.invalid/phase-c/alpha',
        'verified', NOW());

INSERT INTO evaluations
    (id, technology_id, version_id, evaluation_type, test_status,
     critical_findings_count, tested_at)
VALUES ('c4000000-0000-4000-8000-000000000001',
        'c1000000-0000-4000-8000-000000000001',
        'c2000000-0000-4000-8000-000000000001',
        'phase-c-regression', 'passed', 0, NOW());

INSERT INTO decisions (id, technology_id, decision, rationale)
VALUES ('c5000000-0000-4000-8000-000000000001',
        'c1000000-0000-4000-8000-000000000001',
        'approve', 'Phase C disposable approval fixture');

UPDATE technologies SET lifecycle_status = 'verified'
WHERE id = 'c1000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'evaluated'
WHERE id = 'c1000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'approved'
WHERE id = 'c1000000-0000-4000-8000-000000000001';

INSERT INTO integrations (id, technology_id, target_project)
VALUES ('c7000000-0000-4000-8000-000000000001',
        'c1000000-0000-4000-8000-000000000001',
        'phase-c-positive-project');

UPDATE integrations SET integration_status = 'approved'
WHERE id = 'c7000000-0000-4000-8000-000000000001';
UPDATE integrations SET integration_status = 'in_progress'
WHERE id = 'c7000000-0000-4000-8000-000000000001';
UPDATE integrations SET integration_status = 'integrated'
WHERE id = 'c7000000-0000-4000-8000-000000000001';

SELECT pg_temp.assert_true(
    (SELECT integration_status = 'integrated'
     FROM integrations
     WHERE id = 'c7000000-0000-4000-8000-000000000001'),
    'integration can reach integrated after technology approval'
);

SELECT pg_temp.assert_raises(
    $sql$UPDATE integrations
        SET technology_id = 'c1000000-0000-4000-8000-000000000002'
        WHERE id = 'c7000000-0000-4000-8000-000000000001'$sql$,
    'Integration activation requires technology lifecycle approved or integrated'
);

SELECT pg_temp.assert_true(
    (SELECT technology_id = 'c1000000-0000-4000-8000-000000000001'
     FROM integrations
     WHERE id = 'c7000000-0000-4000-8000-000000000001'),
    'integrated record cannot be reassigned to an unapproved technology'
);

ROLLBACK;

\echo 'PASS: Phase C integration approval coupling tests completed; fixtures rolled back.'
