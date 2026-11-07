-- M5mOsH AI Capability Registry
-- Phase C: couple integration activation to technology approval.
-- PostgreSQL 14+; apply after Phase A and Phase B.
-- This migration changes only the integration status trigger function.

BEGIN;

CREATE OR REPLACE FUNCTION enforce_integration_status_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    technology_lifecycle TEXT;
BEGIN
    -- Lock the parent technology row before checking its lifecycle. This
    -- serializes activation against concurrent lifecycle changes.
    IF NEW.integration_status IN ('approved', 'integrated') THEN
        SELECT lifecycle_status
        INTO technology_lifecycle
        FROM technologies
        WHERE id = NEW.technology_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Integration requires an existing technology';
        END IF;

        IF technology_lifecycle NOT IN ('approved', 'integrated') THEN
            RAISE EXCEPTION
                'Integration activation requires technology lifecycle approved or integrated; current status is %',
                technology_lifecycle;
        END IF;
    END IF;

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

-- Reassignment of an already-approved/integrated record must also re-run
-- the parent lifecycle check, even when integration_status itself is unchanged.
DROP TRIGGER trg_integration_status_transition ON integrations;

CREATE TRIGGER trg_integration_status_transition
BEFORE INSERT OR UPDATE OF integration_status, technology_id ON integrations
FOR EACH ROW
EXECUTE FUNCTION enforce_integration_status_transition();

COMMIT;
