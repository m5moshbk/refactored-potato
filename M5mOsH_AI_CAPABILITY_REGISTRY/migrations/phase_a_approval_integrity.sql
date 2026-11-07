-- M5mOsH AI Capability Registry
-- Phase A: approval evidence integrity
-- PostgreSQL 14+; apply after schema.sql in a disposable/test database first.
-- This migration does not configure roles or tenant isolation.

BEGIN;

ALTER TABLE decisions
    ADD CONSTRAINT uq_decisions_technology_id UNIQUE (technology_id, id);

CREATE TABLE approval_evidence_snapshots (
    technology_id UUID PRIMARY KEY
        REFERENCES technologies(id) ON DELETE RESTRICT,
    version_id UUID NOT NULL,
    source_id UUID NOT NULL,
    evaluation_id UUID NOT NULL,
    decision_id UUID NOT NULL,
    evidence_snapshot JSONB NOT NULL
        CHECK (jsonb_typeof(evidence_snapshot) = 'object'),
    approved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_approval_snapshot_version
        FOREIGN KEY (technology_id, version_id)
        REFERENCES technology_versions(technology_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_approval_snapshot_source
        FOREIGN KEY (technology_id, source_id)
        REFERENCES sources(technology_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_approval_snapshot_evaluation
        FOREIGN KEY (technology_id, evaluation_id)
        REFERENCES evaluations(technology_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_approval_snapshot_decision
        FOREIGN KEY (technology_id, decision_id)
        REFERENCES decisions(technology_id, id) ON DELETE RESTRICT
);

COMMENT ON TABLE approval_evidence_snapshots IS
    'Immutable point-in-time evidence chain captured when a technology enters approved state.';

CREATE OR REPLACE FUNCTION enforce_technology_approval_gate()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    selected_version technology_versions%ROWTYPE;
    selected_source sources%ROWTYPE;
    selected_evaluation evaluations%ROWTYPE;
    selected_decision decisions%ROWTYPE;
BEGIN
    IF NEW.lifecycle_status = 'approved'
       AND OLD.lifecycle_status IS DISTINCT FROM 'approved' THEN

        SELECT *
        INTO selected_version
        FROM technology_versions v
        WHERE v.technology_id = NEW.id
          AND v.support_status = 'active'
          AND v.verified_at IS NOT NULL
        ORDER BY v.verified_at DESC, v.created_at DESC, v.id
        LIMIT 1;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Approval requires a verified active version';
        END IF;

        SELECT *
        INTO selected_source
        FROM sources s
        WHERE s.technology_id = NEW.id
          AND s.verification_status = 'verified'
          AND (s.version_id IS NULL OR s.version_id = selected_version.id)
        ORDER BY s.checked_at DESC NULLS LAST, s.created_at DESC, s.id
        LIMIT 1;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Approval requires verified source evidence for the selected version';
        END IF;

        SELECT *
        INTO selected_evaluation
        FROM evaluations e
        WHERE e.technology_id = NEW.id
          AND e.version_id = selected_version.id
          AND e.test_status = 'passed'
          AND e.critical_findings_count = 0
          AND e.tested_at IS NOT NULL
        ORDER BY e.tested_at DESC, e.created_at DESC, e.id
        LIMIT 1;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Approval requires a passed zero-critical evaluation for the selected version';
        END IF;

        SELECT *
        INTO selected_decision
        FROM decisions d
        WHERE d.technology_id = NEW.id
          AND d.decision = 'approve'
        ORDER BY d.decided_at DESC, d.id
        LIMIT 1;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Approval requires an explicit approval decision record';
        END IF;

        INSERT INTO approval_evidence_snapshots (
            technology_id,
            version_id,
            source_id,
            evaluation_id,
            decision_id,
            evidence_snapshot
        )
        VALUES (
            NEW.id,
            selected_version.id,
            selected_source.id,
            selected_evaluation.id,
            selected_decision.id,
            jsonb_build_object(
                'technology', to_jsonb(NEW),
                'version', to_jsonb(selected_version),
                'source', to_jsonb(selected_source),
                'evaluation', to_jsonb(selected_evaluation),
                'decision', to_jsonb(selected_decision)
            )
        );
    END IF;

    RETURN NEW;
END;
$$;

-- Serialize evidence mutations against approval creation, then protect every
-- evidence row captured by an approval snapshot from UPDATE or DELETE.
CREATE OR REPLACE FUNCTION prevent_approved_evidence_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    ignored_status TEXT;
    is_snapshotted BOOLEAN := FALSE;
BEGIN
    SELECT t.lifecycle_status
    INTO ignored_status
    FROM technologies t
    WHERE t.id = OLD.technology_id
    FOR UPDATE;

    IF TG_TABLE_NAME = 'technology_versions' THEN
        SELECT EXISTS (
            SELECT 1 FROM approval_evidence_snapshots a
            WHERE a.technology_id = OLD.technology_id
              AND a.version_id = OLD.id
        ) INTO is_snapshotted;
    ELSIF TG_TABLE_NAME = 'sources' THEN
        SELECT EXISTS (
            SELECT 1 FROM approval_evidence_snapshots a
            WHERE a.technology_id = OLD.technology_id
              AND a.source_id = OLD.id
        ) INTO is_snapshotted;
    ELSIF TG_TABLE_NAME = 'evaluations' THEN
        SELECT EXISTS (
            SELECT 1 FROM approval_evidence_snapshots a
            WHERE a.technology_id = OLD.technology_id
              AND a.evaluation_id = OLD.id
        ) INTO is_snapshotted;
    ELSIF TG_TABLE_NAME = 'decisions' THEN
        SELECT EXISTS (
            SELECT 1 FROM approval_evidence_snapshots a
            WHERE a.technology_id = OLD.technology_id
              AND a.decision_id = OLD.id
        ) INTO is_snapshotted;
    END IF;

    IF is_snapshotted THEN
        RAISE EXCEPTION
            'Approval evidence is immutable; create a new review instead of changing the approved evidence chain';
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_immutable_approved_version_evidence
BEFORE UPDATE OR DELETE ON technology_versions
FOR EACH ROW EXECUTE FUNCTION prevent_approved_evidence_mutation();

CREATE TRIGGER trg_immutable_approved_source_evidence
BEFORE UPDATE OR DELETE ON sources
FOR EACH ROW EXECUTE FUNCTION prevent_approved_evidence_mutation();

CREATE TRIGGER trg_immutable_approved_evaluation_evidence
BEFORE UPDATE OR DELETE ON evaluations
FOR EACH ROW EXECUTE FUNCTION prevent_approved_evidence_mutation();

CREATE TRIGGER trg_immutable_approved_decision_evidence
BEFORE UPDATE OR DELETE ON decisions
FOR EACH ROW EXECUTE FUNCTION prevent_approved_evidence_mutation();

CREATE OR REPLACE FUNCTION prevent_approval_snapshot_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'approval_evidence_snapshots is append-only';
END;
$$;

CREATE TRIGGER trg_approval_snapshot_no_update_delete
BEFORE UPDATE OR DELETE ON approval_evidence_snapshots
FOR EACH ROW EXECUTE FUNCTION prevent_approval_snapshot_mutation();

COMMIT;
