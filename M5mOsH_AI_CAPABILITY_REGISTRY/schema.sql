-- M5mOsH AI Capability Registry
-- Schema v1.0
-- PostgreSQL 14+
-- DESIGN ARTIFACT: creating this file does not execute it.
-- Application generates UUID values; no secrets belong in this registry.

BEGIN;

CREATE TABLE technologies (
    id UUID PRIMARY KEY,
    canonical_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    vendor TEXT,
    category TEXT NOT NULL,
    description TEXT,
    official_url TEXT,
    repository_url TEXT,
    lifecycle_status TEXT NOT NULL DEFAULT 'discovered'
        CHECK (lifecycle_status IN (
            'discovered', 'verified', 'evaluated',
            'approved', 'integrated', 'deprecated', 'rejected'
        )),
    security_status TEXT NOT NULL DEFAULT 'unverified'
        CHECK (security_status IN (
            'unverified', 'under_review', 'accepted',
            'restricted', 'rejected'
        )),
    pricing_model TEXT,
    privacy_notes TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(metadata) = 'object'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT technologies_name_nonempty CHECK (length(trim(name)) > 0),
    CONSTRAINT technologies_key_nonempty CHECK (length(trim(canonical_key)) > 0),
    CONSTRAINT technologies_category_nonempty CHECK (length(trim(category)) > 0)
);

CREATE TABLE technology_versions (
    id UUID PRIMARY KEY,
    technology_id UUID NOT NULL
        REFERENCES technologies(id) ON DELETE RESTRICT,
    version_name TEXT NOT NULL,
    release_date DATE,
    license_name TEXT,
    license_url TEXT,
    changelog_url TEXT,
    support_status TEXT NOT NULL DEFAULT 'unknown'
        CHECK (support_status IN (
            'active', 'maintenance', 'deprecated',
            'unsupported', 'unknown'
        )),
    verified_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(metadata) = 'object'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT technology_versions_name_nonempty
        CHECK (length(trim(version_name)) > 0),
    CONSTRAINT uq_technology_version_name UNIQUE (technology_id, version_name),
    CONSTRAINT uq_technology_version_pair UNIQUE (technology_id, id)
);

CREATE TABLE capabilities (
    id UUID PRIMARY KEY,
    technology_id UUID NOT NULL
        REFERENCES technologies(id) ON DELETE RESTRICT,
    capability_key TEXT NOT NULL,
    capability_name TEXT NOT NULL,
    description TEXT,
    use_cases JSONB NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(use_cases) = 'array'),
    limitations JSONB NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(limitations) = 'array'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT capabilities_key_nonempty
        CHECK (length(trim(capability_key)) > 0),
    CONSTRAINT capabilities_name_nonempty
        CHECK (length(trim(capability_name)) > 0),
    CONSTRAINT uq_capability_pair UNIQUE (technology_id, id),
    CONSTRAINT uq_capability_key UNIQUE (technology_id, capability_key)
);

CREATE TABLE sources (
    id UUID PRIMARY KEY,
    technology_id UUID NOT NULL
        REFERENCES technologies(id) ON DELETE RESTRICT,
    version_id UUID,
    source_type TEXT NOT NULL
        CHECK (source_type IN (
            'official_documentation', 'official_repository',
            'release_notes', 'license', 'security_advisory',
            'benchmark', 'research_paper', 'other'
        )),
    source_url TEXT NOT NULL,
    source_title TEXT,
    published_at TIMESTAMPTZ,
    checked_at TIMESTAMPTZ,
    verification_status TEXT NOT NULL DEFAULT 'unverified'
        CHECK (verification_status IN (
            'unverified', 'verified', 'outdated',
            'unavailable', 'disputed'
        )),
    evidence_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT sources_url_nonempty CHECK (length(trim(source_url)) > 0),
    CONSTRAINT uq_source_pair UNIQUE (technology_id, id),
    CONSTRAINT uq_source_url UNIQUE (technology_id, source_url),
    CONSTRAINT fk_source_version_same_technology
        FOREIGN KEY (technology_id, version_id)
        REFERENCES technology_versions(technology_id, id)
        ON DELETE RESTRICT
);

CREATE TABLE evaluations (
    id UUID PRIMARY KEY,
    technology_id UUID NOT NULL
        REFERENCES technologies(id) ON DELETE RESTRICT,
    version_id UUID,
    evaluation_type TEXT NOT NULL,
    test_environment TEXT,
    test_method TEXT,
    test_status TEXT NOT NULL DEFAULT 'not_tested'
        CHECK (test_status IN (
            'not_tested', 'planned', 'running',
            'passed', 'failed', 'blocked', 'inconclusive'
        )),
    quality_score NUMERIC CHECK (quality_score BETWEEN 0 AND 100),
    security_score NUMERIC CHECK (security_score BETWEEN 0 AND 100),
    privacy_score NUMERIC CHECK (privacy_score BETWEEN 0 AND 100),
    cost_score NUMERIC CHECK (cost_score BETWEEN 0 AND 100),
    critical_findings_count INTEGER NOT NULL DEFAULT 0
        CHECK (critical_findings_count >= 0),
    findings JSONB NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(findings) = 'array'),
    test_results JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(test_results) = 'object'),
    evidence_reference TEXT,
    tested_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_evaluation_version_same_technology
        FOREIGN KEY (technology_id, version_id)
        REFERENCES technology_versions(technology_id, id)
        ON DELETE RESTRICT
);

CREATE TABLE capability_evidence (
    technology_id UUID NOT NULL,
    capability_id UUID NOT NULL,
    source_id UUID NOT NULL,
    evidence_role TEXT NOT NULL DEFAULT 'supporting'
        CHECK (evidence_role IN ('primary', 'supporting', 'contradicting')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (capability_id, source_id),
    CONSTRAINT fk_evidence_capability_same_technology
        FOREIGN KEY (technology_id, capability_id)
        REFERENCES capabilities(technology_id, id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_evidence_source_same_technology
        FOREIGN KEY (technology_id, source_id)
        REFERENCES sources(technology_id, id)
        ON DELETE RESTRICT
);

CREATE TABLE integrations (
    id UUID PRIMARY KEY,
    technology_id UUID NOT NULL
        REFERENCES technologies(id) ON DELETE RESTRICT,
    target_project TEXT NOT NULL,
    integration_status TEXT NOT NULL DEFAULT 'proposed'
        CHECK (integration_status IN (
            'proposed', 'approved', 'in_progress',
            'integrated', 'blocked', 'rejected', 'removed'
        )),
    integration_scope TEXT,
    approval_reference TEXT,
    evidence_reference TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT integrations_project_nonempty
        CHECK (length(trim(target_project)) > 0),
    CONSTRAINT uq_technology_project UNIQUE (technology_id, target_project)
);

CREATE TABLE decisions (
    id UUID PRIMARY KEY,
    technology_id UUID NOT NULL
        REFERENCES technologies(id) ON DELETE RESTRICT,
    decision TEXT NOT NULL
        CHECK (decision IN ('approve', 'reject', 'defer', 'reassess', 'retire')),
    rationale TEXT NOT NULL,
    risk_level TEXT NOT NULL DEFAULT 'unknown'
        CHECK (risk_level IN ('low', 'medium', 'high', 'critical', 'unknown')),
    evidence_summary TEXT,
    approver_reference TEXT,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT decisions_rationale_nonempty
        CHECK (length(trim(rationale)) > 0)
);

CREATE TABLE audit_events (
    id UUID PRIMARY KEY,
    technology_id UUID
        REFERENCES technologies(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    event_details JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(event_details) = 'object'),
    evidence_reference TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT audit_event_type_nonempty CHECK (length(trim(event_type)) > 0),
    CONSTRAINT audit_actor_nonempty CHECK (length(trim(actor)) > 0)
);

-- Enforce the initial state as well as valid lifecycle transitions.
-- Direct INSERT into approved/integrated states is not permitted.
CREATE OR REPLACE FUNCTION enforce_technology_lifecycle_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.lifecycle_status <> 'discovered' THEN
            RAISE EXCEPTION 'New technologies must start in discovered state';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.lifecycle_status = OLD.lifecycle_status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.lifecycle_status = 'discovered'
            AND NEW.lifecycle_status IN ('verified', 'rejected', 'deprecated'))
        OR
        (OLD.lifecycle_status = 'verified'
            AND NEW.lifecycle_status IN ('evaluated', 'rejected', 'deprecated'))
        OR
        (OLD.lifecycle_status = 'evaluated'
            AND NEW.lifecycle_status IN ('approved', 'rejected', 'deprecated'))
        OR
        (OLD.lifecycle_status = 'approved'
            AND NEW.lifecycle_status IN ('integrated', 'deprecated'))
        OR
        (OLD.lifecycle_status = 'integrated'
            AND NEW.lifecycle_status = 'deprecated')
    ) THEN
        RAISE EXCEPTION 'Invalid lifecycle transition: % -> %',
            OLD.lifecycle_status, NEW.lifecycle_status;
    END IF;

    RETURN NEW;
END;
$;

CREATE TRIGGER trg_technology_lifecycle_transition
BEFORE INSERT OR UPDATE OF lifecycle_status ON technologies
FOR EACH ROW
EXECUTE FUNCTION enforce_technology_lifecycle_transition();

-- Approval requires verified evidence, an active verified version,
-- a passed evaluation with no critical findings, and an explicit approval decision.
CREATE OR REPLACE FUNCTION enforce_technology_approval_gate()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.lifecycle_status = 'approved'
       AND OLD.lifecycle_status IS DISTINCT FROM 'approved' THEN

        IF NOT EXISTS (
            SELECT 1
            FROM sources s
            WHERE s.technology_id = NEW.id
              AND s.verification_status = 'verified'
        ) THEN
            RAISE EXCEPTION 'Approval requires at least one verified source';
        END IF;

        IF NOT EXISTS (
            SELECT 1
            FROM technology_versions v
            WHERE v.technology_id = NEW.id
              AND v.support_status = 'active'
              AND v.verified_at IS NOT NULL
        ) THEN
            RAISE EXCEPTION 'Approval requires a verified active version';
        END IF;

        IF NOT EXISTS (
            SELECT 1
            FROM evaluations e
            WHERE e.technology_id = NEW.id
              AND e.test_status = 'passed'
              AND e.critical_findings_count = 0
              AND e.tested_at IS NOT NULL
        ) THEN
            RAISE EXCEPTION 'Approval requires a passed evaluation with zero critical findings';
        END IF;

        IF NOT EXISTS (
            SELECT 1
            FROM decisions d
            WHERE d.technology_id = NEW.id
              AND d.decision = 'approve'
        ) THEN
            RAISE EXCEPTION 'Approval requires an explicit approval decision record';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_technology_approval_gate
BEFORE UPDATE OF lifecycle_status ON technologies
FOR EACH ROW
EXECUTE FUNCTION enforce_technology_approval_gate();

-- An integration record starts as proposed; status changes are explicit.
CREATE OR REPLACE FUNCTION enforce_integration_status_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.integration_status <> 'proposed' THEN
            RAISE EXCEPTION 'New integrations must start in proposed state';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.integration_status = OLD.integration_status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.integration_status = 'proposed'
            AND NEW.integration_status IN ('approved', 'blocked', 'rejected'))
        OR
        (OLD.integration_status = 'approved'
            AND NEW.integration_status IN ('in_progress', 'blocked', 'rejected'))
        OR
        (OLD.integration_status = 'in_progress'
            AND NEW.integration_status IN ('integrated', 'blocked'))
        OR
        (OLD.integration_status = 'blocked'
            AND NEW.integration_status IN ('proposed', 'in_progress', 'rejected'))
        OR
        (OLD.integration_status = 'integrated'
            AND NEW.integration_status = 'removed')
    ) THEN
        RAISE EXCEPTION 'Invalid integration transition: % -> %',
            OLD.integration_status, NEW.integration_status;
    END IF;

    RETURN NEW;
END;
$;

CREATE TRIGGER trg_integration_status_transition
BEFORE INSERT OR UPDATE OF integration_status ON integrations
FOR EACH ROW
EXECUTE FUNCTION enforce_integration_status_transition();

-- Audit events are append-only for ordinary database roles.
CREATE OR REPLACE FUNCTION prevent_audit_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'audit_events is append-only';
END;
$$;

CREATE TRIGGER trg_audit_no_update_delete
BEFORE UPDATE OR DELETE ON audit_events
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_mutation();

-- Indexes for common lookups and review queues.
CREATE INDEX idx_technologies_category
    ON technologies(category);
CREATE INDEX idx_technologies_lifecycle
    ON technologies(lifecycle_status);
CREATE INDEX idx_technologies_security
    ON technologies(security_status);
CREATE INDEX idx_versions_technology
    ON technology_versions(technology_id);
CREATE INDEX idx_capabilities_technology
    ON capabilities(technology_id);
CREATE INDEX idx_sources_technology_status
    ON sources(technology_id, verification_status);
CREATE INDEX idx_evaluations_technology_status
    ON evaluations(technology_id, test_status);
CREATE INDEX idx_integrations_project_status
    ON integrations(target_project, integration_status);
CREATE INDEX idx_decisions_technology_date
    ON decisions(technology_id, decided_at DESC);
CREATE INDEX idx_audit_technology_date
    ON audit_events(technology_id, occurred_at DESC);

COMMIT;
