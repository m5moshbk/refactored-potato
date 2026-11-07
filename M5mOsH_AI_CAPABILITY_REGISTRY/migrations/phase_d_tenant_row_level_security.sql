-- M5mOsH AI Capability Registry
-- Phase D: tenant isolation and row-level security.
-- PostgreSQL 14+; apply after Phases A, B, and C.
-- Fail closed on populated registries: tenant ownership must be explicitly mapped.

BEGIN;

DO $phase_d_preflight$
BEGIN
    IF EXISTS (SELECT 1 FROM technologies)
       OR EXISTS (SELECT 1 FROM technology_versions)
       OR EXISTS (SELECT 1 FROM capabilities)
       OR EXISTS (SELECT 1 FROM sources)
       OR EXISTS (SELECT 1 FROM evaluations)
       OR EXISTS (SELECT 1 FROM capability_evidence)
       OR EXISTS (SELECT 1 FROM integrations)
       OR EXISTS (SELECT 1 FROM decisions)
       OR EXISTS (SELECT 1 FROM audit_events)
       OR EXISTS (SELECT 1 FROM approval_evidence_snapshots) THEN
        RAISE EXCEPTION
            'Phase D migration blocked: populated registry requires an explicit tenant ownership mapping and reviewed backfill';
    END IF;
END;
$phase_d_preflight$;

CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    tenant_key TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT tenants_key_nonempty CHECK (length(trim(tenant_key)) > 0),
    CONSTRAINT tenants_name_nonempty CHECK (length(trim(display_name)) > 0)
);

-- Every registry row is assigned to exactly one tenant. The migration is
-- deliberately blocked above rather than guessing ownership for old rows.
ALTER TABLE technologies
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE technology_versions
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE capabilities
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE sources
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE evaluations
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE capability_evidence
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE integrations
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE decisions
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE audit_events
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE approval_evidence_snapshots
    ADD COLUMN tenant_id UUID NOT NULL
        REFERENCES tenants(id) ON DELETE RESTRICT;

-- Parent key used by composite tenant/technology foreign keys.
ALTER TABLE technologies
    ADD CONSTRAINT uq_technologies_tenant_id UNIQUE (tenant_id, id);

-- Canonical keys are unique within a tenant, not across unrelated tenants.
ALTER TABLE technologies
    DROP CONSTRAINT technologies_canonical_key_key;
ALTER TABLE technologies
    ADD CONSTRAINT uq_technologies_tenant_canonical_key
    UNIQUE (tenant_id, canonical_key);

-- Enforce tenant consistency on every technology-owned record.
ALTER TABLE technology_versions
    ADD CONSTRAINT fk_versions_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE capabilities
    ADD CONSTRAINT fk_capabilities_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE sources
    ADD CONSTRAINT fk_sources_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE evaluations
    ADD CONSTRAINT fk_evaluations_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE capability_evidence
    ADD CONSTRAINT fk_capability_evidence_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE integrations
    ADD CONSTRAINT fk_integrations_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE decisions
    ADD CONSTRAINT fk_decisions_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE audit_events
    ADD CONSTRAINT fk_audit_events_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;
ALTER TABLE approval_evidence_snapshots
    ADD CONSTRAINT fk_approval_snapshots_tenant_technology
    FOREIGN KEY (tenant_id, technology_id)
    REFERENCES technologies(tenant_id, id) ON DELETE RESTRICT;

-- Tenant-scoped indexes support policy filtering and common tenant lookups.
CREATE INDEX idx_technologies_tenant ON technologies(tenant_id);
CREATE INDEX idx_versions_tenant ON technology_versions(tenant_id);
CREATE INDEX idx_capabilities_tenant ON capabilities(tenant_id);
CREATE INDEX idx_sources_tenant ON sources(tenant_id);
CREATE INDEX idx_evaluations_tenant ON evaluations(tenant_id);
CREATE INDEX idx_capability_evidence_tenant ON capability_evidence(tenant_id);
CREATE INDEX idx_integrations_tenant ON integrations(tenant_id);
CREATE INDEX idx_decisions_tenant ON decisions(tenant_id);
CREATE INDEX idx_audit_events_tenant ON audit_events(tenant_id);
CREATE INDEX idx_approval_snapshots_tenant ON approval_evidence_snapshots(tenant_id);

-- A missing tenant context returns no rows and rejects writes. The application
-- must set this transaction-locally only after authenticating the tenant.
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_tenants ON tenants
    FOR ALL
    USING (id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE technologies ENABLE ROW LEVEL SECURITY;
ALTER TABLE technologies FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_technologies ON technologies
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE technology_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE technology_versions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_versions ON technology_versions
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE capabilities FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_capabilities ON capabilities
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_sources ON sources
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluations FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_evaluations ON evaluations
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE capability_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE capability_evidence FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_capability_evidence ON capability_evidence
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_integrations ON integrations
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_decisions ON decisions
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_audit_events ON audit_events
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

ALTER TABLE approval_evidence_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_evidence_snapshots FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_approval_snapshots ON approval_evidence_snapshots
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

COMMIT;
