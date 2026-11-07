-- M5mOsH AI Capability Registry
-- Phase A approval integrity regression tests.
-- Run only after schema.sql and migrations/phase_a_approval_integrity.sql.
-- All fixtures are rolled back.

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

-- Alpha: one coherent version/source/evaluation/decision chain.
INSERT INTO technologies (id, canonical_key, name, category)
VALUES ('a1000000-0000-4000-8000-000000000001',
        'phase-a.alpha', 'Phase A Alpha', 'test');

INSERT INTO technology_versions
    (id, technology_id, version_name, support_status, verified_at)
VALUES ('a2000000-0000-4000-8000-000000000001',
        'a1000000-0000-4000-8000-000000000001',
        '1.0', 'active', NOW());

INSERT INTO sources
    (id, technology_id, version_id, source_type, source_url,
     verification_status, checked_at)
VALUES ('a3000000-0000-4000-8000-000000000001',
        'a1000000-0000-4000-8000-000000000001',
        'a2000000-0000-4000-8000-000000000001',
        'official_documentation', 'https://example.invalid/phase-a/alpha',
        'verified', NOW());

INSERT INTO evaluations
    (id, technology_id, version_id, evaluation_type, test_status,
     critical_findings_count, tested_at)
VALUES ('a4000000-0000-4000-8000-000000000001',
        'a1000000-0000-4000-8000-000000000001',
        'a2000000-0000-4000-8000-000000000001',
        'phase-a-regression', 'passed', 0, NOW());

INSERT INTO decisions (id, technology_id, decision, rationale)
VALUES ('a5000000-0000-4000-8000-000000000001',
        'a1000000-0000-4000-8000-000000000001',
        'approve', 'Phase A disposable regression fixture');

UPDATE technologies SET lifecycle_status = 'verified'
WHERE id = 'a1000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'evaluated'
WHERE id = 'a1000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'approved'
WHERE id = 'a1000000-0000-4000-8000-000000000001';

SELECT pg_temp.assert_true(
    (SELECT count(*) = 1 FROM approval_evidence_snapshots
     WHERE technology_id = 'a1000000-0000-4000-8000-000000000001'),
    'approval creates exactly one evidence snapshot'
);

SELECT pg_temp.assert_true(
    (SELECT evidence_snapshot->'evaluation'->>'test_status' = 'passed'
       AND evidence_snapshot->'source'->>'verification_status' = 'verified'
       AND evidence_snapshot->'decision'->>'decision' = 'approve'
     FROM approval_evidence_snapshots
     WHERE technology_id = 'a1000000-0000-4000-8000-000000000001'),
    'snapshot stores the approved source, evaluation, and decision state'
);

-- The four evidence records selected at approval cannot be rewritten or removed.
SELECT pg_temp.assert_raises(
    $q$UPDATE sources SET verification_status = 'disputed'
       WHERE id = 'a3000000-0000-4000-8000-000000000001'$q$,
    'Approval evidence is immutable'
);
SELECT pg_temp.assert_raises(
    $q$DELETE FROM sources
       WHERE id = 'a3000000-0000-4000-8000-000000000001'$q$,
    'Approval evidence is immutable'
);
SELECT pg_temp.assert_raises(
    $q$UPDATE evaluations SET test_status = 'failed',
          critical_findings_count = 1
       WHERE id = 'a4000000-0000-4000-8000-000000000001'$q$,
    'Approval evidence is immutable'
);
SELECT pg_temp.assert_raises(
    $q$UPDATE technology_versions SET support_status = 'unsupported'
       WHERE id = 'a2000000-0000-4000-8000-000000000001'$q$,
    'Approval evidence is immutable'
);
SELECT pg_temp.assert_raises(
    $q$DELETE FROM decisions
       WHERE id = 'a5000000-0000-4000-8000-000000000001'$q$,
    'Approval evidence is immutable'
);
SELECT pg_temp.assert_raises(
    $q$UPDATE approval_evidence_snapshots
       SET evidence_snapshot = '{}'::jsonb
       WHERE technology_id = 'a1000000-0000-4000-8000-000000000001'$q$,
    'approval_evidence_snapshots is append-only'
);
SELECT pg_temp.assert_raises(
    $q$DELETE FROM approval_evidence_snapshots
       WHERE technology_id = 'a1000000-0000-4000-8000-000000000001'$q$,
    'approval_evidence_snapshots is append-only'
);
SELECT pg_temp.assert_raises(
    $q$TRUNCATE TABLE approval_evidence_snapshots$q$,
    'approval_evidence_snapshots is append-only'
);
SELECT pg_temp.assert_raises(
    $q$INSERT INTO approval_evidence_snapshots
       (technology_id, version_id, source_id, evaluation_id, decision_id, evidence_snapshot)
       VALUES
       ('a1000000-0000-4000-8000-000000000001',
        'a2000000-0000-4000-8000-000000000001',
        'a3000000-0000-4000-8000-000000000001',
        'a4000000-0000-4000-8000-000000000001',
        'a5000000-0000-4000-8000-000000000001',
        '{}'::jsonb)$q$,
    'approval snapshots may only be created by the approval lifecycle transition'
);

SELECT pg_temp.assert_true(
    (SELECT lifecycle_status = 'approved'
     FROM technologies
     WHERE id = 'a1000000-0000-4000-8000-000000000001'),
    'rejected evidence mutations leave the approved lifecycle intact'
);

-- Beta: individually valid records must not be mixed across versions.
INSERT INTO technologies (id, canonical_key, name, category)
VALUES ('b1000000-0000-4000-8000-000000000001',
        'phase-a.beta', 'Phase A Beta', 'test');

INSERT INTO technology_versions
    (id, technology_id, version_name, support_status, verified_at)
VALUES
('b2000000-0000-4000-8000-000000000001',
 'b1000000-0000-4000-8000-000000000001', '1.0', 'active', NOW()),
('b2000000-0000-4000-8000-000000000002',
 'b1000000-0000-4000-8000-000000000001', '2.0', 'active', NOW());

INSERT INTO sources
    (id, technology_id, version_id, source_type, source_url,
     verification_status, checked_at)
VALUES ('b3000000-0000-4000-8000-000000000001',
        'b1000000-0000-4000-8000-000000000001',
        'b2000000-0000-4000-8000-000000000001',
        'official_documentation', 'https://example.invalid/phase-a/beta',
        'verified', NOW());

INSERT INTO evaluations
    (id, technology_id, version_id, evaluation_type, test_status,
     critical_findings_count, tested_at)
VALUES ('b4000000-0000-4000-8000-000000000001',
        'b1000000-0000-4000-8000-000000000001',
        'b2000000-0000-4000-8000-000000000002',
        'phase-a-mismatched-version', 'passed', 0, NOW());

INSERT INTO decisions (id, technology_id, decision, rationale)
VALUES ('b5000000-0000-4000-8000-000000000001',
        'b1000000-0000-4000-8000-000000000001',
        'approve', 'Negative fixture: evidence belongs to different versions');

UPDATE technologies SET lifecycle_status = 'verified'
WHERE id = 'b1000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'evaluated'
WHERE id = 'b1000000-0000-4000-8000-000000000001';

SELECT pg_temp.assert_raises(
    $q$UPDATE technologies SET lifecycle_status = 'approved'
       WHERE id = 'b1000000-0000-4000-8000-000000000001'$q$,
    'Approval requires a passed zero-critical evaluation for the selected version'
);

SELECT pg_temp.assert_true(
    (SELECT count(*) = 0 FROM approval_evidence_snapshots
     WHERE technology_id = 'b1000000-0000-4000-8000-000000000001'),
    'mismatched version evidence cannot create an approval snapshot'
);

ROLLBACK;
\echo 'PASS: Phase A approval integrity tests completed; fixtures rolled back.'
