-- M5mOsH AI Capability Registry
-- PostgreSQL schema contract tests v1.0
-- READ THIS FIRST:
-- 1) Run ONLY against a disposable, isolated PostgreSQL test database.
-- 2) Apply M5mOsH_AI_CAPABILITY_REGISTRY/schema.sql to that database first.
-- 3) Run with psql -v ON_ERROR_STOP=1 -f schema_contract.sql.
-- 4) This script rolls back its fixture data at the end.
-- 5) It does not create a database, role, credential, or production change.
--
-- No pgTAP dependency. Uses PostgreSQL DO blocks and temporary assertion helpers.

\set ON_ERROR_STOP on

BEGIN;

CREATE FUNCTION pg_temp.assert_true(condition BOOLEAN, assertion_name TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    IF condition IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION 'ASSERTION FAILED: %', assertion_name;
    END IF;
END;
$$;

CREATE FUNCTION pg_temp.assert_raises(command_text TEXT, expected_message TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    actual_message TEXT;
BEGIN
    BEGIN
        EXECUTE command_text;
    EXCEPTION WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS actual_message = MESSAGE_TEXT;

        IF position(expected_message IN actual_message) = 0 THEN
            RAISE EXCEPTION
                'ASSERTION FAILED: expected error containing "%", got "%"',
                expected_message, actual_message;
        END IF;

        RETURN;
    END;

    RAISE EXCEPTION
        'ASSERTION FAILED: expected command to fail with message containing "%"',
        expected_message;
END;
$$;

-- Stable fixture IDs make failures reproducible.
-- Two technologies are used to test cross-technology reference isolation.
INSERT INTO technologies (id, canonical_key, name, category)
VALUES
(
    '10000000-0000-4000-8000-000000000001',
    'test.registry.alpha',
    'Registry Test Alpha',
    'test'
),
(
    '10000000-0000-4000-8000-000000000002',
    'test.registry.beta',
    'Registry Test Beta',
    'test'
);

-- Test 1: new technologies cannot bypass the discovered state.
SELECT pg_temp.assert_raises(
    $q$INSERT INTO technologies
       (id, canonical_key, name, category, lifecycle_status)
       VALUES
       ('10000000-0000-4000-8000-000000000003',
        'test.registry.direct-approved',
        'Direct Approved Test',
        'test',
        'approved')$q$,
    'New technologies must start in discovered state'
);

-- Test 2: duplicate canonical keys are rejected.
SELECT pg_temp.assert_raises(
    $q$INSERT INTO technologies
       (id, canonical_key, name, category)
       VALUES
       ('10000000-0000-4000-8000-000000000004',
        'test.registry.alpha',
        'Duplicate Key Test',
        'test')$q$,
    'duplicate key'
);

-- Create one version for each technology.
INSERT INTO technology_versions
    (id, technology_id, version_name, support_status, verified_at)
VALUES
(
    '20000000-0000-4000-8000-000000000001',
    '10000000-0000-4000-8000-000000000001',
    '1.0.0',
    'active',
    NOW()
),
(
    '20000000-0000-4000-8000-000000000002',
    '10000000-0000-4000-8000-000000000002',
    '2.0.0',
    'active',
    NOW()
);

-- Test 3: a source cannot point to a version owned by another technology.
SELECT pg_temp.assert_raises(
    $q$INSERT INTO sources
       (id, technology_id, version_id, source_type, source_url)
       VALUES
       ('30000000-0000-4000-8000-000000000001',
        '10000000-0000-4000-8000-000000000001',
        '20000000-0000-4000-8000-000000000002',
        'official_documentation',
        'https://example.invalid/cross-technology-version')$q$,
    'fk_source_version_same_technology'
);

-- Add valid source, capability, and evaluation evidence for Alpha.
INSERT INTO sources
    (id, technology_id, version_id, source_type, source_url,
     verification_status, checked_at)
VALUES
(
    '30000000-0000-4000-8000-000000000002',
    '10000000-0000-4000-8000-000000000001',
    '20000000-0000-4000-8000-000000000001',
    'official_documentation',
    'https://example.invalid/alpha/docs',
    'verified',
    NOW()
),
(
    '30000000-0000-4000-8000-000000000003',
    '10000000-0000-4000-8000-000000000002',
    '20000000-0000-4000-8000-000000000002',
    'official_documentation',
    'https://example.invalid/beta/docs',
    'verified',
    NOW()
);

INSERT INTO capabilities
    (id, technology_id, capability_key, capability_name)
VALUES
(
    '40000000-0000-4000-8000-000000000001',
    '10000000-0000-4000-8000-000000000001',
    'metadata.read',
    'Metadata Read'
);

-- Test 4: evidence cannot join a capability from Alpha to a source from Beta.
SELECT pg_temp.assert_raises(
    $q$INSERT INTO capability_evidence
       (technology_id, capability_id, source_id)
       VALUES
       ('10000000-0000-4000-8000-000000000001',
        '40000000-0000-4000-8000-000000000001',
        '30000000-0000-4000-8000-000000000003')$q$,
    'fk_evidence_source_same_technology'
);

-- Test 5: lifecycle shortcuts are rejected.
SELECT pg_temp.assert_raises(
    $q$UPDATE technologies
       SET lifecycle_status = 'evaluated'
       WHERE id = '10000000-0000-4000-8000-000000000001'$q$,
    'Invalid lifecycle transition'
);

-- Test 6: approval gate rejects approval without a passed evaluation.
UPDATE technologies
SET lifecycle_status = 'verified'
WHERE id = '10000000-0000-4000-8000-000000000002';

UPDATE technologies
SET lifecycle_status = 'evaluated'
WHERE id = '10000000-0000-4000-8000-000000000002';

INSERT INTO decisions
    (id, technology_id, decision, rationale)
VALUES
(
    '50000000-0000-4000-8000-000000000002',
    '10000000-0000-4000-8000-000000000002',
    'approve',
    'Negative test: approval must still be blocked without evaluation'
);

SELECT pg_temp.assert_raises(
    $q$UPDATE technologies
       SET lifecycle_status = 'approved'
       WHERE id = '10000000-0000-4000-8000-000000000002'$q$,
    'Approval requires a passed evaluation'
);

-- Test 7: a complete evidence chain permits the valid lifecycle path.
INSERT INTO evaluations
    (id, technology_id, version_id, evaluation_type,
     test_status, critical_findings_count, tested_at)
VALUES
(
    '60000000-0000-4000-8000-000000000001',
    '10000000-0000-4000-8000-000000000001',
    '20000000-0000-4000-8000-000000000001',
    'schema-contract',
    'passed',
    0,
    NOW()
);

INSERT INTO decisions
    (id, technology_id, decision, rationale)
VALUES
(
    '50000000-0000-4000-8000-000000000001',
    '10000000-0000-4000-8000-000000000001',
    'approve',
    'Positive test fixture with verified source, active version, and passed evaluation'
);

UPDATE technologies
SET lifecycle_status = 'verified'
WHERE id = '10000000-0000-4000-8000-000000000001';

UPDATE technologies
SET lifecycle_status = 'evaluated'
WHERE id = '10000000-0000-4000-8000-000000000001';

UPDATE technologies
SET lifecycle_status = 'approved'
WHERE id = '10000000-0000-4000-8000-000000000001';

SELECT pg_temp.assert_true(
    (SELECT lifecycle_status = 'approved'
     FROM technologies
     WHERE id = '10000000-0000-4000-8000-000000000001'),
    'valid approval path reaches approved'
);

-- Test 8: integrations must start proposed.
SELECT pg_temp.assert_raises(
    $q$INSERT INTO integrations
       (id, technology_id, target_project, integration_status)
       VALUES
       ('70000000-0000-4000-8000-000000000001',
        '10000000-0000-4000-8000-000000000001',
        'test-project-invalid',
        'integrated')$q$,
    'New integrations must start in proposed state'
);

-- Test 9: invalid integration state jumps are rejected.
INSERT INTO integrations
    (id, technology_id, target_project)
VALUES
(
    '70000000-0000-4000-8000-000000000002',
    '10000000-0000-4000-8000-000000000001',
    'test-project-valid'
);

SELECT pg_temp.assert_raises(
    $q$UPDATE integrations
       SET integration_status = 'integrated'
       WHERE id = '70000000-0000-4000-8000-000000000002'$q$,
    'Invalid integration transition'
);

-- Test 10: valid integration transitions are accepted.
UPDATE integrations
SET integration_status = 'approved'
WHERE id = '70000000-0000-4000-8000-000000000002';

UPDATE integrations
SET integration_status = 'in_progress'
WHERE id = '70000000-0000-4000-8000-000000000002';

UPDATE integrations
SET integration_status = 'integrated'
WHERE id = '70000000-0000-4000-8000-000000000002';

SELECT pg_temp.assert_true(
    (SELECT integration_status = 'integrated'
     FROM integrations
     WHERE id = '70000000-0000-4000-8000-000000000002'),
    'valid integration path reaches integrated'
);

-- Test 11: audit rows reject UPDATE and DELETE.
INSERT INTO audit_events
    (id, technology_id, event_type, actor)
VALUES
(
    '80000000-0000-4000-8000-000000000001',
    '10000000-0000-4000-8000-000000000001',
    'schema_test',
    'schema_contract_test'
);

SELECT pg_temp.assert_raises(
    $q$UPDATE audit_events
       SET actor = 'tampered'
       WHERE id = '80000000-0000-4000-8000-000000000001'$q$,
    'audit_events is append-only'
);

SELECT pg_temp.assert_raises(
    $q$DELETE FROM audit_events
       WHERE id = '80000000-0000-4000-8000-000000000001'$q$,
    'audit_events is append-only'
);

-- Test 12: numeric score bounds are enforced.
SELECT pg_temp.assert_raises(
    $q$INSERT INTO evaluations
       (id, technology_id, evaluation_type, quality_score)
       VALUES
       ('60000000-0000-4000-8000-000000000002',
        '10000000-0000-4000-8000-000000000001',
        'invalid-score',
        101)$q$,
    'quality_score'
);

-- Test 13: audit event remains present after rejected mutations.
SELECT pg_temp.assert_true(
    (SELECT count(*) = 1
     FROM audit_events
     WHERE id = '80000000-0000-4000-8000-000000000001'),
    'audit row remains after rejected UPDATE and DELETE'
);

-- All fixtures and temporary test effects are rolled back.
ROLLBACK;

\echo 'PASS: M5mOsH AI Capability Registry schema contract checks completed.'
