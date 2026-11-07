-- M5mOsH AI Capability Registry
-- Phase D tenant-isolation regression tests.
-- Run after schema.sql and Phase A, B, C, and D migrations.
-- Fixtures are rolled back; the temporary test role is removed.

\set ON_ERROR_STOP on

CREATE ROLE registry_tenant_test NOLOGIN NOBYPASSRLS;
GRANT SELECT, INSERT ON
    tenants, technologies, technology_versions, capabilities, sources,
    evaluations, capability_evidence, integrations, decisions,
    audit_events, approval_evidence_snapshots
TO registry_tenant_test;

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

-- Two tenants with a complete but isolated registry fixture each.
INSERT INTO tenants (id, tenant_key, display_name)
VALUES
('d0000000-0000-4000-8000-000000000001', 'phase-d-alpha', 'Phase D Alpha'),
('d0000000-0000-4000-8000-000000000002', 'phase-d-beta', 'Phase D Beta');

INSERT INTO technologies (id, tenant_id, canonical_key, name, category)
VALUES
('d1000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'phase-d.alpha', 'Phase D Alpha Technology', 'test'),
('d1000000-0000-4000-8000-000000000002', 'd0000000-0000-4000-8000-000000000002', 'phase-d.beta', 'Phase D Beta Technology', 'test');

INSERT INTO technology_versions
    (id, tenant_id, technology_id, version_name, support_status, verified_at)
VALUES
('d2000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000001', '1.0', 'active', NOW()),
('d2000000-0000-4000-8000-000000000002', 'd0000000-0000-4000-8000-000000000002', 'd1000000-0000-4000-8000-000000000002', '1.0', 'active', NOW());

INSERT INTO capabilities
    (id, tenant_id, technology_id, capability_key, capability_name)
VALUES
('d3000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000001', 'phase-d.alpha', 'Alpha capability'),
('d3000000-0000-4000-8000-000000000002', 'd0000000-0000-4000-8000-000000000002', 'd1000000-0000-4000-8000-000000000002', 'phase-d.beta', 'Beta capability');

INSERT INTO sources
    (id, tenant_id, technology_id, version_id, source_type, source_url, verification_status, checked_at)
VALUES
('d4000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000001', 'd2000000-0000-4000-8000-000000000001', 'official_documentation', 'https://example.invalid/phase-d/alpha', 'verified', NOW()),
('d4000000-0000-4000-8000-000000000002', 'd0000000-0000-4000-8000-000000000002', 'd1000000-0000-4000-8000-000000000002', 'd2000000-0000-4000-8000-000000000002', 'official_documentation', 'https://example.invalid/phase-d/beta', 'verified', NOW());

INSERT INTO evaluations
    (id, tenant_id, technology_id, version_id, evaluation_type, test_status, critical_findings_count, tested_at)
VALUES
('d5000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000001', 'd2000000-0000-4000-8000-000000000001', 'phase-d', 'passed', 0, NOW()),
('d5000000-0000-4000-8000-000000000002', 'd00000000-0000-4000-8000-000000000002', 'd1000000-0000-4000-8000-000000000002', 'd2000000-0000-4000-8000-000000000002', 'phase-d', 'passed', 0, NOW());

INSERT INTO decisions (id, tenant_id, technology_id, decision, rationale)
VALUES
('d6000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000001', 'approve', 'Phase D fixture'),
('d6000000-0000-4000-8000-000000000002', 'd0000000-0000-4000-8000-000000000002', 'd1000000-0000-4000-8000-000000000002', 'approve', 'Phase D fixture');

INSERT INTO capability_evidence
    (tenant_id, technology_id, capability_id, source_id, evidence_role)
VALUES
('d0000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000001', 'd3000000-0000-4000-8000-000000000001', 'd4000000-0000-4000-8000-000000000001', 'primary'),
('d0000000-0000-4000-8000-000000000002', 'd1000000-0000-4000-8000-000000000002', 'd3000000-0000-4000-8000-000000000002', 'd4000000-0000-4000-8000-000000000002', 'primary');

INSERT INTO integrations (id, tenant_id, technology_id, target_project)
VALUES
('d7000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000001', 'phase-d-alpha'),
('d7000000-0000-4000-8000-000000000002', 'd0000000-0000-4000-8000-000000000002', 'd1000000-0000-4000-8000-000000000002', 'phase-d-beta');

INSERT INTO audit_events (id, tenant_id, technology_id, event_type, actor)
VALUES
('d8000000-0000-4000-8000-000000000001', 'd0000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000001', 'phase_d', 'phase_d_test'),
('d8000000-0000-4000-8000-000000000002', 'd0000000-0000-4000-8000-000000000002', 'd1000000-0000-4000-8000-000000000002', 'phase_d', 'phase_d_test');

-- Create one valid approval snapshot per tenant through the real lifecycle gate.
UPDATE technologies SET lifecycle_status = 'verified'
WHERE id IN ('d1000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000002');
UPDATE technologies SET lifecycle_status = 'evaluated'
WHERE id IN ('d1000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000002');
UPDATE technologies SET lifecycle_status = 'approved'
WHERE id IN ('d1000000-0000-4000-8000-000000000001', 'd1000000-0000-4000-8000-000000000002');

-- Non-owner, NOBYPASSRLS role: no tenant context means no visible rows.
SET LOCAL ROLE registry_tenant_test;
SELECT pg_temp.assert_true(
    (SELECT count(*) = 0 FROM technologies),
    'missing tenant context returns no technology rows'
);

-- Tenant Alpha sees exactly its own row from every tenant-scoped table.
SELECT set_config('app.tenant_id', 'd0000000-0000-4000-8000-000000000001', true);
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM tenants), 'tenant A sees only its tenant row');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM technologies), 'tenant A sees only its technologies');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM technology_versions), 'tenant A sees only its versions');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM capabilities), 'tenant A sees only its capabilities');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM sources), 'tenant A sees only its sources');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM evaluations), 'tenant A sees only its evaluations');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM capability_evidence), 'tenant A sees only its capability evidence');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM integrations), 'tenant A sees only its integrations');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM decisions), 'tenant A sees only its decisions');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM audit_events), 'tenant A sees only its audit events');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM approval_evidence_snapshots), 'tenant A sees only its approval snapshots');

SELECT pg_temp.assert_raises(
    $sql$INSERT INTO technologies (id, tenant_id, canonical_key, name, category)
        VALUES ('d1000000-0000-4000-8000-000000000099',
                'd0000000-0000-4000-8000-000000000002',
                'phase-d.cross-tenant', 'Cross Tenant Attempt', 'test')$sql$,
    'row-level security policy'
);

-- Switching the trusted transaction-local tenant context exposes only Beta.
SELECT set_config('app.tenant_id', 'd0000000-0000-4000-8000-000000000002', true);
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM tenants), 'tenant B sees only its tenant row');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM technologies), 'tenant B sees only its technologies');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM technology_versions), 'tenant B sees only its versions');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM capabilities), 'tenant B sees only its capabilities');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM sources), 'tenant B sees only its sources');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM evaluations), 'tenant B sees only its evaluations');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM capability_evidence), 'tenant B sees only its capability evidence');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM integrations), 'tenant B sees only its integrations');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM decisions), 'tenant B sees only its decisions');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM audit_events), 'tenant B sees only its audit events');
SELECT pg_temp.assert_true((SELECT count(*) = 1 FROM approval_evidence_snapshots), 'tenant B sees only its approval snapshots');

RESET ROLE;
ROLLBACK;

DROP OWNED BY registry_tenant_test;
DROP ROLE registry_tenant_test;

\echo 'PASS: Phase D tenant isolation tests completed; fixtures and test role removed.'
