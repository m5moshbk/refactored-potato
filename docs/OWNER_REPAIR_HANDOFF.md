# M5mOsH Owner Repair Inbox Handoff

**Owner:** M5mOsH  
**Rights:** © M5mOsH All Rights Reserved  
**Mode:** Draft handoff; no autonomous execution.

## Purpose

The Nexus Owner Repair Environment prepares a structured repair request and opens a prefilled GitHub issue draft in the private repository:

- Repository: `m5moshbk/M5mOsH-Task-Orchestrator`
- Inbox: `https://github.com/m5moshbk/M5mOsH-Task-Orchestrator/issues`

## Owner flow

1. Select a project in Nexus and choose **تجهيز الإصلاح**.
2. Review the generated title and body in the ticket preview.
3. Choose **توجيه الطلب إلى صندوق المساعد**.
4. GitHub opens a prefilled issue form. The issue is not saved until the owner presses **Create new issue**.
5. Return to the existing ChatGPT conversation and provide the issue number or URL. The assistant can then retrieve the private issue through the connected GitHub account and begin evidence collection and branch-scoped work.

## Important limitation

The static Nexus page cannot send a message into an existing ChatGPT conversation. This handoff is therefore explicit, not a background push: the GitHub issue becomes the durable request record, and the owner supplies its link or number to the assistant.

The current Task Orchestrator is a proposal-only foundation. It has no trusted authentication, durable task store, worker, scheduler, or execution endpoint. Do not describe it as an autonomous repair executor until those components are implemented, threat-modeled, tested, and deployed with owner approval.

## Safety boundary

- Read-only diagnosis is the default.
- Repair changes must be bounded to a development branch and tested.
- Never include API keys, tokens, passwords, database URLs/DSNs, certificates, customer data, or other secrets in the issue.
- A GitHub issue is not authorization to change production.
- Separate explicit owner approval remains required for merges, deployments, restarts, database changes, secret rotation, account/permission changes, or deletion.
- The UI applies a conservative pattern check for common secret-like strings, but this is not a complete data-loss-prevention system. The owner must still review the ticket preview.
- The owner description is limited to 600 characters to keep the prefilled GitHub URL bounded. Overlong text is rejected rather than silently truncated; secret-pattern checks run on the full description before any handoff.

## Evidence and status language

The browser event `handoff_opened_not_submitted` means only that the handoff action was invoked. It does not prove GitHub saved the issue, that ChatGPT received it, or that repair work began.

© M5mOsH All Rights Reserved
