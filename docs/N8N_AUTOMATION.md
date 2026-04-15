# n8n Automation Plan

FPConnect can use n8n as the automation layer around operational events, while
the API remains the source of truth for users, tickets, assets, and audit logs.

## Current foundation

- `N8N_SLA_WORKFLOW_URL`: outbound webhook called by FPConnect when ticket/SLA
  automations are enabled.
- `N8N_SLA_API_KEY`: shared key for FPConnect -> n8n calls and n8n -> FPConnect
  callbacks.
- `N8N_SLA_TIMEOUT_SECONDS`: short timeout so automations never block API usage.
- `POST /notifications/sms`: sends SMS to the authenticated user's registered
  phone number.

## High-value workflows

1. Critical ticket escalation
   - Trigger: new ticket with `priority=critical`.
   - n8n actions: notify WhatsApp/Telegram/SMS/email, wait for acknowledgement,
     escalate to manager if no response.

2. SLA breach prevention
   - Trigger: open ticket age crosses thresholds.
   - n8n actions: calculate remaining time, update escalation level, create audit
     note, notify on-call technician.

3. Maintenance playbooks
   - Trigger: machine status changes to warning/offline.
   - n8n actions: create checklist, assign technician, request parts, schedule
     follow-up.

4. Daily operations digest
   - Trigger: scheduled cron in n8n.
   - n8n actions: query FPConnect metrics, summarize open risks, send digest to
     leadership.

5. Vendor handoff
   - Trigger: repeated incident or high-risk RCA result.
   - n8n actions: generate vendor packet, attach logs, open external ticket, track
     vendor response.

6. Compliance audit trail
   - Trigger: status, priority, assignment, or notification event.
   - n8n actions: write structured audit events back to FPConnect and optionally
     archive to Google Drive/SharePoint.

## Security rules

- Never send PHI in webhook payloads.
- Send identifiers and operational metadata only.
- Keep Twilio, OpenAI, and n8n secrets only in backend environment variables.
- Require `X-Internal-Key` on all n8n callbacks.
- Log automation decisions in FPConnect so users can see what happened.
