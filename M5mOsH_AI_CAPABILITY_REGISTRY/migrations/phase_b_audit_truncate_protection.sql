-- M5mOsH AI Capability Registry
-- Phase B: audit log TRUNCATE protection
-- PostgreSQL 14+; apply after schema.sql and Phase A.
-- This migration adds a statement-level guard; it does not configure roles.

BEGIN;

-- The base schema already defines prevent_audit_mutation() for row-level
-- UPDATE/DELETE protection. Reuse the same fail-closed function for TRUNCATE.
CREATE TRIGGER trg_audit_no_truncate
BEFORE TRUNCATE ON audit_events
FOR EACH STATEMENT
EXECUTE FUNCTION prevent_audit_mutation();

COMMENT ON TRIGGER trg_audit_no_truncate ON audit_events IS
    'Rejects TRUNCATE so the append-only audit log cannot be cleared by ordinary SQL statements.';

COMMIT;
