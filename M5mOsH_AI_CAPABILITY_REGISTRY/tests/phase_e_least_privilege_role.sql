-- M5mOsH AI Capability Registry
-- Phase E least-privilege application-role regression tests.
-- Run only in the disposable CI database after Phases A-D.
-- The NOLOGIN test role is intentionally retained for the following security probe;
-- the entire database is disposable and is destroyed with the CI job.

\set ON_ERROR_STOP on

CREATE ROLE registry_app_test
    NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;

GRANT USAGE ON SCHEMA public TO registry_app_test;

GRANT SELECT ON
    tenants, technologies, technology_versions, capabilities, sources,
    evaluations, capability_evidence, integrations, decisions,
    audit_events, approval_evidence_snapshots
TO registry_app_test;

-- Operational writes only. Tenant administration is separate.
GRANT INSERT ON
    technologies, technology_versions, capabilities, sources,
    evaluations, capability_evidence, integrations, decisions,
    audit_events, approval_evidence_snapshots
TO registry_app_test;

GRANT UPDATE ON
    technologies, technology_versions, capabilities, sources,
    evaluations, capability_evidence, integrations, decisions
TO registry_app_test;

BEGIN;

CREATE FUNCTION pg_temp.assert_true(condition BOOLEAN, assertion_name TEXT)
RETURNS VOID LANGUAGE plpgsql AS $assert_true$
BEGIN
    IF condition IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION 'ASSERTION FAILED: %', assertion_name;
    END IF;
END;
$assert_true$;

CREATE FUNCTION pg_temp.assert_raises(command_text TEXT, expected_message TEXT)
RETURNS VOID LANGUAGE plpgsql AS $assert_raises$
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
$assert_raises$;

-- Seed tenant rows outside the application role. The app role cannot create tenants.
INSERT INTO tenants (id, tenant_key, display_name)
VALUES
('e0000000-0000-4000-8000-000000000001', 'phase-e-app', 'Phase E App Tenant'),
('e0000000-0000-4000-8000-000000000002', 'phase-e-other', 'Phase E Other Tenant');

-- An unrelated tenant row exists but must remain invisible to the app role.
INSERT INTO technologies (id, tenant_id, canonical_key, name, category)
VALUES ('e1000000-0000-4000-8000-000000000002',
        'e0000000-0000-4000-8000-000000000002',
        'phase-e.other', 'Other Tenant Technology', 'test');

SET LOCAL ROLE registry_app_test;
SELECT set_config('app.tenant_id', 'e0000000-0000-4000-8000-000000000001', true);

SELECT pg_temp.assert_true(
    (SELECT count(*) = 0 FROM technologies),
    'application role cannot see another tenant technology'
);

-- Application role can create and update records within its authenticated tenant.
INSERT INTO technologies (id, tenant_id, canonical_key, name, category)
VALUES ('e1000000-0000-4000-8000-000000000001',
        'e0000000-0000-4000-8000-000000000001',
        'phase-e.app', 'Phase E Application Technology', 'test');

UPDATE technologies
SET name = 'Phase E Application Technology Updated'
WHERE id = 'e1000000-0000-4000-8000-000000000001';

INSERT INTO technology_versions
    (id, tenant_id, technology_id, version_name, support_status, verified_at)
VALUES ('e2000000-0000-4000-8000-000000000001',
        'e0000000-0000-4000-8000-000000000001',
        'e1000000-0000-4000-8000-000000000001',
        '1.0', 'active', NOW());

INSERT INTO sources
    (id, tenant_id, technology_id, version_id, source_type, source_url,
     verification_status, checked_at)
VALUES ('e3000000-0000-4000-8000-000000000001',
        'e0000000-0000-4000-8000-000000000001',
        'e1000000-0000-4000-8000-000000000001',
        'e2000000-0000-4000-8000-000000000001',
        'official_documentation', 'https://example.invalid/phase-e/app',
        'verified', NOW());

INSERT INTO evaluations
    (id, tenant_id, technology_id, version_id, evaluation_type, test_status,
     critical_findings_count, tested_at)
VALUES ('e4000000-0000-4000-8000-000000000001',
        'e0000000-0000-4000-8000-000000000001',
        'e1000000-0000-4000-8000-000000000001',
        'e2000000-0000-4000-8000-000000000001',
        'phase-e-app-role', 'passed', 0, NOW());

INSERT INTO decisions (id, tenant_id, technology_id, decision, rationale)
VALUES ('e5000000-0000-4000-8000-000000000001',
        'e0000000-0000-4000-8000-000000000001',
        'e1000000-0000-4000-8000-000000000001',
        'approve', 'Disposable Phase E role test');

UPDATE technologies SET lifecycle_status = 'verified'
WHERE id = 'e1000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'evaluated'
WHERE id = 'e1000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'approved'
WHERE id = 'e1000000-0000-4000-8000-000000000001';

SELECT pg_temp.assert_true(
    (SELECT count(*) = 1 FROM approval_evidence_snapshots),
    'application role can create an approval snapshot only through the approval lifecycle trigger'
);

INSERT INTO audit_events (id, tenant_id, technology_id, event_type, actor)
VALUES ('e6000000-0000-4000-8000-000000000001',
        'e0000000-0000-4000-8000-000000000001',
        'e1000000-0000-4000-8000-000000000001',
        'phase_e_application_insert', 'registry_app_test');

SELECT pg_temp.assert_true(
    (SELECT count(*) = 1 FROM technologies),
    'application role sees only its own tenant after permitted writes'
);

SELECT pg_temp.assert_raises(
    $sql$INSERT INTO technologies (id, tenant_id, canonical_key, name, category)
        VALUES ('e1000000-0000-4000-8000-000000000099',
                'e0000000-0000-4000-8000-000000000002',
                'phase-e.cross-tenant', 'Cross Tenant Attempt', 'test')$sql$,
    'row-level security policy'
);

SELECT pg_temp.assert_raises(
    $sql$INSERT INTO approval_evidence_snapshots
        (technology_id, tenant_id, version_id, source_id, evaluation_id, decision_id, evidence_snapshot)
        VALUES ('e1000000-0000-4000-8000-000000000001',
                'e0000000-0000-4000-8000-000000000001',
                'e2000000-0000-4000-8000-000000000001',
                'e3000000-0000-4000-8000-000000000001',
                'e4000000-0000-4000-8000-000000000001',
                'e5000000-0000-4000-8000-000000000001',
                '{}'::jsonb)$sql$,
    'approval snapshots may only be created by the approval lifecycle transition'
);

SELECT pg_temp.assert_raises(
    $sql$UPDATE audit_events SET actor = 'tampered'
        WHERE id = 'e6000000-0000-4000-8000-000000000001'$sql$,
    'permission denied'
);
SELECT pg_temp.assert_raises(
    $sql$DELETE FROM audit_events
        WHERE id = 'e6000000-0000-4000-8000-000000000001'$sql$,
    'permission denied'
);
SELECT pg_temp.assert_raises('TRUNCATE TABLE audit_events', 'permission denied');
SELECT pg_temp.assert_raises(
    $sql$DELETE FROM technologies
        WHERE id = 'e1000000-0000-4000-8000-000000000001'$sql$,
    'permission denied'
);
SELECT pg_temp.assert_raises(
    'ALTER TABLE audit_events ADD COLUMN phase_e_forbidden TEXT',
    'must be owner of table audit_events'
);
SELECT pg_temp.assert_raises(
    'CREATE TABLE public.phase_e_forbidden (id INTEGER)',
    'permission denied for schema public'
);

RESET ROLE;

SELECT pg_temp.assert_true(
    NOT (SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolbypassrls
         FROM pg_roles WHERE rolname = 'registry_app_test'),
    'application role has no superuser, database creation, role creation, or RLS bypass attributes'
);
SELECT pg_temp.assert_true(
    NOT has_schema_privilege('registry_app_test', 'public', 'CREATE'),
    'application role cannot create objects in the public schema'
);
SELECT pg_temp.assert_true(
    NOT has_table_privilege('registry_app_test', 'audit_events', 'UPDATE')
    AND NOT has_table_privilege('registry_app_test', 'audit_events', 'DELETE')
    AND NOT has_table_privilege('registry_app_test', 'audit_events', 'TRUNCATE'),
    'application role has no audit mutation or truncate privileges'
);
SELECT pg_temp.assert_true(
    NOT has_table_privilege('registry_app_test', 'technologies', 'DELETE')
    AND NOT has_table_privilege('registry_app_test', 'technologies', 'TRUNCATE'),
    'application role cannot delete or truncate technology records'
);
SELECT pg_temp.assert_true(
    NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relkind IN ('r', 'p')
          AND relowner = (SELECT oid FROM pg_roles WHERE rolname = 'registry_app_test')
    ),
    'application role owns no tables'
);
SELECT pg_temp.assert_true(
    NOT EXISTS (
        SELECT 1 FROM pg_auth_members
        WHERE member = (SELECT oid FROM pg_roles WHERE rolname = 'registry_app_test')
    ),
    'application role is not a member of any elevated role'
);

ROLLBACK;

\echo 'PASS: Phase E least-privilege application-role tests completed; data fixtures rolled back.'
