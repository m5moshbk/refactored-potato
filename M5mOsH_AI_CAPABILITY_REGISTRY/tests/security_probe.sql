-- M5mOsH AI Capability Registry
-- Security discovery probes v1.0
-- Run ONLY against the disposable PostgreSQL database created by the CI workflow.
-- This script records observed gaps; expected findings do not fail the workflow.
-- All fixture changes, including a successful TRUNCATE probe, are rolled back.
\set ON_ERROR_STOP on

BEGIN;

INSERT INTO tenants (id, tenant_key, display_name)
VALUES ('90000000-0000-4000-8000-000000000001',
        'security-probe', 'Disposable Security Probe Tenant');
SELECT set_config('app.tenant_id', '90000000-0000-4000-8000-000000000001', true);

CREATE TEMP TABLE probe_findings (
    severity TEXT NOT NULL,
    probe TEXT NOT NULL,
    outcome TEXT NOT NULL,
    evidence TEXT NOT NULL
) ON COMMIT DROP;

CREATE FUNCTION pg_temp.record_probe(
    p_severity TEXT,
    p_probe TEXT,
    p_outcome TEXT,
    p_evidence TEXT
) RETURNS VOID
LANGUAGE SQL
AS $fn$
    INSERT INTO probe_findings(severity, probe, outcome, evidence)
    VALUES (p_severity, p_probe, p_outcome, p_evidence);
$fn$;

-- Fixtures: Alpha has a complete evidence chain and is approved.
INSERT INTO technologies (id, tenant_id, canonical_key, name, category)
VALUES
('91000000-0000-4000-8000-000000000001', '90000000-0000-4000-8000-000000000001',
 'probe.security.alpha', 'Security Probe Alpha', 'probe'),
('91000000-0000-4000-8000-000000000002', '90000000-0000-4000-8000-000000000001',
 'probe.security.beta', 'Security Probe Beta', 'probe');

INSERT INTO technology_versions
    (id, tenant_id, technology_id, version_name, support_status, verified_at)
VALUES
('92000000-0000-4000-8000-000000000001', '90000000-0000-4000-8000-000000000001',
 '91000000-0000-4000-8000-000000000001', '1.0', 'active', NOW());

INSERT INTO sources
    (id, tenant_id, technology_id, version_id, source_type, source_url,
     verification_status, checked_at)
VALUES
('93000000-0000-4000-8000-000000000001', '90000000-0000-4000-8000-000000000001',
 '91000000-0000-4000-8000-000000000001',
 '92000000-0000-4000-8000-000000000001',
 'official_documentation', 'https://example.invalid/probe/alpha',
 'verified', NOW());

INSERT INTO evaluations
    (id, tenant_id, technology_id, version_id, evaluation_type, test_status,
     critical_findings_count, tested_at)
VALUES
('94000000-0000-4000-8000-000000000001', '90000000-0000-4000-8000-000000000001',
 '91000000-0000-4000-8000-000000000001',
 '92000000-0000-4000-8000-000000000001',
 'security-probe', 'passed', 0, NOW());

INSERT INTO decisions (id, tenant_id, technology_id, decision, rationale)
VALUES
('95000000-0000-4000-8000-000000000001', '90000000-0000-4000-8000-000000000001',
 '91000000-0000-4000-8000-000000000001',
 'approve', 'Disposable security probe fixture');

UPDATE technologies SET lifecycle_status = 'verified'
WHERE id = '91000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'evaluated'
WHERE id = '91000000-0000-4000-8000-000000000001';
UPDATE technologies SET lifecycle_status = 'approved'
WHERE id = '91000000-0000-4000-8000-000000000001';

-- Probe 1: can the approval decision be deleted after approval?
DO $probe$
BEGIN
    BEGIN
        DELETE FROM decisions
        WHERE id = '95000000-0000-4000-8000-000000000001';
        PERFORM pg_temp.record_probe(
            'HIGH', 'approval-decision-immutability', 'FINDING',
            'DELETE succeeded after technology reached approved; no decision immutability guard.'
        );
    EXCEPTION WHEN OTHERS THEN
        PERFORM pg_temp.record_probe(
            'INFO', 'approval-decision-immutability', 'BLOCKED',
            'DELETE was rejected: ' || SQLERRM
        );
    END;
END;
$probe$;

-- Probe 2: can verified evidence be downgraded after approval?
DO $probe$
BEGIN
    BEGIN
        UPDATE sources SET verification_status = 'unverified'
        WHERE id = '93000000-0000-4000-8000-000000000001';
        PERFORM pg_temp.record_probe(
            'HIGH', 'approved-source-downgrade', 'FINDING',
            'Verified source was downgraded after approval without revalidation.'
        );
    EXCEPTION WHEN OTHERS THEN
        PERFORM pg_temp.record_probe(
            'INFO', 'approved-source-downgrade', 'BLOCKED',
            'Source downgrade was rejected: ' || SQLERRM
        );
    END;
END;
$probe$;

-- Probe 3: can the passing evaluation be changed after approval?
DO $probe$
BEGIN
    BEGIN
        UPDATE evaluations SET test_status = 'failed',
                               critical_findings_count = 1
        WHERE id = '94000000-0000-4000-8000-000000000001';
        PERFORM pg_temp.record_probe(
            'HIGH', 'approved-evaluation-downgrade', 'FINDING',
            'Passed evaluation was changed to failed with a critical finding after approval.'
        );
    EXCEPTION WHEN OTHERS THEN
        PERFORM pg_temp.record_probe(
            'INFO', 'approved-evaluation-downgrade', 'BLOCKED',
            'Evaluation downgrade was rejected: ' || SQLERRM
        );
    END;
END;
$probe$;

-- Probe 4: can the verified active version be marked unsupported?
DO $probe$
BEGIN
    BEGIN
        UPDATE technology_versions SET support_status = 'unsupported'
        WHERE id = '92000000-0000-4000-8000-000000000001';
        PERFORM pg_temp.record_probe(
            'HIGH', 'approved-version-downgrade', 'FINDING',
            'Approved technology version was marked unsupported without approval revalidation.'
        );
    EXCEPTION WHEN OTHERS THEN
        PERFORM pg_temp.record_probe(
            'INFO', 'approved-version-downgrade', 'BLOCKED',
            'Version downgrade was rejected: ' || SQLERRM
        );
    END;
END;
$probe$;

-- Probe 5: confirm that the approved lifecycle is backed by the unchanged snapshot chain.
DO $probe$
DECLARE
    still_approved BOOLEAN;
    snapshot_present BOOLEAN;
    source_verified BOOLEAN;
    evaluation_passed BOOLEAN;
    version_active BOOLEAN;
    approval_decision_present BOOLEAN;
BEGIN
    SELECT lifecycle_status = 'approved' INTO still_approved
    FROM technologies
    WHERE id = '91000000-0000-4000-8000-000000000001';

    SELECT EXISTS (
        SELECT 1 FROM approval_evidence_snapshots
        WHERE technology_id = '91000000-0000-4000-8000-000000000001'
          AND version_id = '92000000-0000-4000-8000-000000000001'
          AND source_id = '93000000-0000-4000-8000-000000000001'
          AND evaluation_id = '94000000-0000-4000-8000-000000000001'
          AND decision_id = '95000000-0000-4000-8000-000000000001'
    ) INTO snapshot_present;

    SELECT verification_status = 'verified' INTO source_verified
    FROM sources WHERE id = '93000000-0000-4000-8000-000000000001';

    SELECT test_status = 'passed' AND critical_findings_count = 0
    INTO evaluation_passed
    FROM evaluations WHERE id = '94000000-0000-4000-8000-000000000001';

    SELECT support_status = 'active' INTO version_active
    FROM technology_versions WHERE id = '92000000-0000-4000-8000-000000000001';

    SELECT EXISTS (
        SELECT 1 FROM decisions
        WHERE id = '95000000-0000-4000-8000-000000000001'
          AND decision = 'approve'
    ) INTO approval_decision_present;

    IF still_approved AND snapshot_present AND source_verified
       AND evaluation_passed AND version_active AND approval_decision_present THEN
        PERFORM pg_temp.record_probe(
            'INFO', 'approval-evidence-drift', 'BLOCKED',
            'Approval snapshot exists and every selected evidence row remains unchanged after rejected mutation attempts.'
        );
    ELSE
        PERFORM pg_temp.record_probe(
            'HIGH', 'approval-evidence-drift', 'FINDING',
            'Approval snapshot or one of its selected evidence records is missing or no longer matches the approved state.'
        );
    END IF;
END;
$probe$;

-- Probe 6: does the audit trigger also protect against TRUNCATE?
INSERT INTO audit_events (id, tenant_id, technology_id, event_type, actor)
VALUES
('96000000-0000-4000-8000-000000000001', '90000000-0000-4000-8000-000000000001',
 '91000000-0000-4000-8000-000000000001',
 'security_probe', 'security_probe');

DO $probe$
BEGIN
    BEGIN
        TRUNCATE TABLE audit_events;
        PERFORM pg_temp.record_probe(
            'HIGH', 'audit-truncate-protection', 'FINDING',
            'TRUNCATE succeeded for the current database role; row-level UPDATE/DELETE trigger does not cover TRUNCATE.'
        );
    EXCEPTION WHEN OTHERS THEN
        PERFORM pg_temp.record_probe(
            'INFO', 'audit-truncate-protection', 'BLOCKED',
            'TRUNCATE was rejected: ' || SQLERRM
        );
    END;
END;
$probe$;

-- Probe 7: can an integration reach integrated while its technology is not approved?
INSERT INTO integrations (id, tenant_id, technology_id, target_project)
VALUES
('97000000-0000-4000-8000-000000000001', '90000000-0000-4000-8000-000000000001',
 '91000000-0000-4000-8000-000000000002',
 'security-probe-project');

DO $probe$
BEGIN
    BEGIN
        UPDATE integrations SET integration_status = 'approved'
        WHERE id = '97000000-0000-4000-8000-000000000001';
        UPDATE integrations SET integration_status = 'in_progress'
        WHERE id = '97000000-0000-4000-8000-000000000001';
        UPDATE integrations SET integration_status = 'integrated'
        WHERE id = '97000000-0000-4000-8000-000000000001';

        PERFORM pg_temp.record_probe(
            'HIGH', 'integration-approval-coupling', 'FINDING',
            'Integration reached integrated while its technology lifecycle remained discovered.'
        );
    EXCEPTION WHEN OTHERS THEN
        PERFORM pg_temp.record_probe(
            'INFO', 'integration-approval-coupling', 'BLOCKED',
            'Integration activation was rejected: ' || SQLERRM
        );
    END;
END;
$probe$;

-- Probe 8: identify whether row-level security is enabled on registry tables.
DO $probe$
DECLARE
    protected_count INTEGER;
    registry_count INTEGER;
BEGIN
    SELECT count(*) FILTER (
               WHERE c.relrowsecurity
                 AND c.relforcerowsecurity
                 AND EXISTS (SELECT 1 FROM pg_policy p WHERE p.polrelid = c.oid)
           ),
           count(*)
    INTO protected_count, registry_count
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = current_schema()
      AND c.relkind = 'r'
      AND c.relname IN (
          'tenants', 'technologies', 'technology_versions', 'capabilities',
          'sources', 'evaluations', 'capability_evidence', 'integrations',
          'decisions', 'audit_events', 'approval_evidence_snapshots'
      );

    IF registry_count > 0 AND protected_count = 0 THEN
        PERFORM pg_temp.record_probe(
            'HIGH', 'tenant-row-level-security', 'FINDING',
            format('RLS is disabled on all %s registry tables in the current schema.', registry_count)
        );
    ELSIF protected_count < registry_count THEN
        PERFORM pg_temp.record_probe(
            'MEDIUM', 'tenant-row-level-security', 'FINDING',
            format('RLS is enabled on %s of %s registry tables.', protected_count, registry_count)
        );
    ELSE
        PERFORM pg_temp.record_probe(
            'INFO', 'tenant-row-level-security', 'PRESENT',
            format('RLS is enabled, forced, and policy-backed on all %s registry tables.', registry_count)
        );
    END IF;
END;
$probe$;

-- Phase E creates a non-login application role with explicit table grants.
-- Confirm its attributes, ownership, schema access, and destructive privileges.
DO $probe$
DECLARE
    app_role_oid OID;
    role_is_restricted BOOLEAN;
BEGIN
    SELECT oid INTO app_role_oid
    FROM pg_roles
    WHERE rolname = 'registry_app_test';

    IF app_role_oid IS NULL THEN
        PERFORM pg_temp.record_probe(
            'MEDIUM', 'least-privilege-test-context', 'LIMITATION',
            'Phase E application role was not present; application-role restrictions could not be confirmed.'
        );
    ELSE
        SELECT
            NOT r.rolsuper
            AND NOT r.rolcreatedb
            AND NOT r.rolcreaterole
            AND NOT r.rolbypassrls
            AND NOT r.rolcanlogin
            AND NOT r.rolinherit
            AND NOT has_schema_privilege('registry_app_test', 'public', 'CREATE')
            AND has_table_privilege('registry_app_test', 'technologies', 'SELECT')
            AND has_table_privilege('registry_app_test', 'technologies', 'INSERT')
            AND has_table_privilege('registry_app_test', 'technologies', 'UPDATE')
            AND NOT has_table_privilege('registry_app_test', 'technologies', 'DELETE')
            AND NOT has_table_privilege('registry_app_test', 'technologies', 'TRUNCATE')
            AND has_table_privilege('registry_app_test', 'audit_events', 'INSERT')
            AND NOT has_table_privilege('registry_app_test', 'audit_events', 'UPDATE')
            AND NOT has_table_privilege('registry_app_test', 'audit_events', 'DELETE')
            AND NOT has_table_privilege('registry_app_test', 'audit_events', 'TRUNCATE')
            AND NOT EXISTS (
                SELECT 1 FROM pg_class
                WHERE relkind IN ('r', 'p') AND relowner = r.oid
            )
            AND NOT EXISTS (
                SELECT 1 FROM pg_auth_members WHERE member = r.oid
            )
        INTO role_is_restricted
        FROM pg_roles r
        WHERE r.oid = app_role_oid;

        IF role_is_restricted THEN
            PERFORM pg_temp.record_probe(
                'INFO', 'least-privilege-test-context', 'PRESENT',
                'registry_app_test is NOLOGIN, NOBYPASSRLS, non-owner, has no elevated role membership or schema CREATE, and lacks DELETE/TRUNCATE and audit mutation privileges.'
            );
        ELSE
            PERFORM pg_temp.record_probe(
                'MEDIUM', 'least-privilege-test-context', 'FINDING',
                'registry_app_test exists but one or more least-privilege role, ownership, schema, or table-grant checks failed.'
            );
        END IF;
    END IF;
END;
$probe$;

\echo '--- SECURITY PROBE FINDINGS (expected findings do not fail CI) ---'
SELECT severity, probe, outcome, evidence
FROM probe_findings
ORDER BY CASE severity WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 WHEN 'INFO' THEN 3 ELSE 4 END,
         probe;

SELECT count(*) AS high_findings
FROM probe_findings
WHERE severity = 'HIGH' AND outcome = 'FINDING';

ROLLBACK;

\echo 'PASS: security discovery probes completed; all disposable fixtures rolled back.'
