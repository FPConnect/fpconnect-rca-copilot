# Tenant isolation: fail-closed slice and release blockers

**Status: not multi-tenant, not ready for commercial multi-customer use.**
The branch scopes the mounted customer-data routes, but remains unverified for
production. Authorization uses a role and status per organization membership.
Do not deploy or onboard customers based on this slice.

## Inventory of persisted models and paths

The SQLAlchemy models are `User`, `Machine`, `Ticket`, `TicketAttachment`,
`TicketLog`, `RCASuggestion`, `KBArticle`, `Playbook`, and `SLAContract`.
Machines, tickets, attachments, ticket logs, RCA suggestions, KB articles,
playbooks and SLA contracts have organization keys.
`User.email`, `Machine.code`, and attachment `object_key` have global uniqueness
semantics. The ticket's creator/assignee and children's foreign keys do not
enforce shared ownership. Knowledge articles may be shared or customer-owned;
that distinction is not modeled and must be decided before exposing them.

| Surface | Current access and required work |
| --- | --- |
| `/auth/register`, `/auth/register/verify`, `/auth/verification-code`, `/auth/login`, `/auth/refresh`, `/auth/me`, `/auth/password` | Authentication is based on user and token version, not organization. Registration creates a regular user; verified registration uses a verification flow. Neither registration nor login/refresh provisions or checks membership. Define trusted onboarding and revocation behavior. |
| `/users` list/create/patch | Scoped to selected organization. Creation atomically adds membership. Access changes modify only the target membership; global account identity is not disabled. |
| `/machines/` | Enabled, filtered by selected organization. NULL/unmapped rows are excluded. Device codes remain globally unique; decide tenant-specific uniqueness and references. Demo rows are no longer created during reads. |
| `/tickets/`, `/tickets/{id}`, create/patch/delete | Enabled and organization-scoped, including for privileged roles. Lower roles retain creator filtering. Device and assignee references are checked within the selected organization. Deletion returns 409 when any attachment, log or suggestion exists; retention/blob cleanup is not implemented. |
| `/tickets/{id}/analyze`, attachment list and upload | Ticket and attachment authorization use the scoped parent; attachment metadata is filtered and new object keys include the organization ID. Existing unowned attachment rows remain hidden. Review bucket privacy, blob lifecycle and already-issued URLs before production. |
| `/analyze`, `/analyze/{ticket_id}/confirm` | Ticket lookup and audit writes are scoped. Semantic retrieval filters `kb_articles` by organization before similarity ranking; actual pgvector execution still needs PostgreSQL tests. |
| `/playbooks/` and `/playbooks/{id}` | Enabled; list/create/update/delete filter by the selected organization. Any referenced external files require separate storage review. |
| `/contracts/`, `/contracts/alerts`, `/contracts/{id}` | Enabled; list/alerts/create/update/delete filter by the selected organization. |
| `/enterprise/reports/equipment/{equipment_code}` | Enabled; equipment and included tickets are scoped by organization, with tickets additionally filtered by creator. |
| `/enterprise/rca`, `/enterprise/rca/methods`, `/enterprise/predictive/risk`, `/enterprise/calibration/schedule`, `/enterprise/calibration/validate`, `/enterprise/compliance/anvisa-report` | Primarily request-derived/stateless calculations and PDF generation; validate any identifiers before introducing stored reads or writes and review external processing and logs. |
| `/notifications/sms` | Development-only preview uses the current user's phone; production returns unavailable. Future delivery, destinations and any persisted notifications require tenant-scoped authorization. Registration verification is a separate notification flow. |
| `scripts/seed_clinical.py`, `scripts/migrate_auth_schema.py`, `core/test_accounts.py`, migrations and startup | Maintenance and seed processes bypass HTTP authorization; startup invokes `create_all`. These paths need controlled operator access, tenant-aware provisioning and a migration-first deployment policy. Background jobs, data imports and direct CRUD/service callers must also be reviewed. |

`services/object_storage.py` uses S3-compatible storage, and attachment rows
store keys. A database-only filter is not sufficient if buckets are public,
credentials or keys are leaked, or existing signed links remain usable. No
storage policy, object copy or URL invalidation is implemented here.
New presigned URLs have a configured lifetime capped at 3,600 seconds; this
cap does not retroactively limit links issued by older deployments. Those links
remain valid until their originally configured expiration or signing credentials
are revoked. Determine the longest historical expiry and coordinate storage
credential rotation/invalidation with operations; no rotation was performed.

## What this slice implements

* `organizations` and `organization_memberships` have foreign keys, indexes,
  and a unique user/organization pair. Users may have multiple memberships.
* Revision 008 creates empty identity tables. It creates no organization and
  infers no membership or ownership for existing users, rows or blobs.
* Revisions 009–011, 013 and 014 give customer resources nullable
  organization keys. Existing rows remain NULL and are excluded from scoped
  operations. Revisions 012 and 015 extend mapping audit records.
* Revision 016 adds per-membership roles. Existing membership rows receive
  least-privileged `visitor`; operators must explicitly approve any elevation.
  Active membership and current role are checked on each protected request,
  even for existing tokens. User identity/account status is independent.
* This gate protects API routes, **not direct SQL, object storage access,
  previously issued presigned URLs, internal service calls or other deployments**.
  Unmapped database rows have NULL ownership and remain accessible to direct SQL;
  they are not physically quarantined. Secure storage and audit earlier signed URLs before
  any rollout. Public registration and seed accounts do not provision membership.

## Mobile/web API contract

1. `POST /auth/login` with `{"email":"...","password":"..."}` returns
   `{"access_token":"...","refresh_token":"...","token_type":"bearer"}`.
   Authentication is user-level and requires no organization selector.
2. `GET /auth/organizations` with `Authorization: Bearer <access_token>`
   returns `200` and `[{"id":1,"slug":"...","name":"..."}]`, containing
   only active memberships in active organizations. `[]` means no active
   membership; there is no automatic default. Invalid/revoked access token
   returns `401`.
3. Explicitly select or switch with `POST /auth/select-organization`, with
   Bearer access token and `X-Organization-Id: <positive integer>`. Success is
   `200 {"organization_id":1,"role":"user","access_level":2}`. This is a validation request; no selection is
   stored server-side. Missing/invalid selector returns `422`; inactive or
   unauthorized membership or organization returns `403`; invalid token `401`.
4. Send both headers on **every protected operation**, including after switching
   or refreshing. The organization ID is a selector, never authority: the server
   checks membership and organization state on every request. On revocation,
   the next protected request returns `403`. `GET /machines/` and `GET /tickets/`
   return filtered arrays; `POST /tickets/` derives organization from the selected
   active membership. A supplied `device_id` must match an equipment code in that
   organization or returns `404`. Role changes and deactivation affect only the
   selected membership. Ticket deletion with dependent records returns `409`.
5. `POST /auth/refresh` with `{"refresh_token":"..."}` returns the same
   token-pair schema as login, requires no selector, and changes no membership.
   Continue to send the selection on subsequent requests. Existing token-version
   revocation applies; issuing a new refresh token does not revoke the previous
   refresh token. `/auth/me` and `/auth/password` remain user-level operations;
   the legacy role in `/auth/me` is not a tenant authorization decision. Use
   the selected organization's role from `/auth/select-organization`.

## Operator bootstrap (restricted, experimental)

The CLI is not exposed over HTTP. Restrict its execution to trusted platform
operators via the host/CI job's OS authorization and a separately protected
database credential in `TENANT_PROVISION_DATABASE_URL`; ordinary application
users must have neither shell/job access nor that credential. The process does
not independently authenticate operators: the OS account recorded in the audit
table is an attribution, not proof of identity. Protect and export audit records
to a tamper-resistant system before production. Run from `apps/api`:

```
python -m scripts.provision_organization --slug site-a --name "Site A" --user-id 12 --role admin --machine-id 31 --machine-id 32 --change-reference CHG-123 --confirm CREATE_AND_MAP
```

It creates a **new** organization, adds one explicitly identified active existing
user, and maps only explicitly listed, currently unmapped machine, optional
ticket, playbook, contract and knowledge article IDs in
one transaction with a database audit row. It refuses nonexistent or already
mapped machines, duplicate IDs and existing slugs; it never infers ownership.
Optional `--ticket-id` may be repeated: it only maps tickets created by the
identified user, with no different assignee, whose device is among the selected
machines (or absent). The complete set of children must be explicitly supplied
using `--attachment-id`, `--log-id`, and `--suggestion-id`; uploader and log
actors must be the mapped user or (for logs) NULL. Suggestions with similar
incident references are rejected for manual review.
Ambiguous tickets abort the whole transaction. Use `--playbook-id`,
`--contract-id` and `--article-id` for additional explicitly approved mappings;
repeat each flag for multiple IDs. Stop concurrent writers during
mapping. No machine flag means no machine mappings. To grant an existing user a
membership in an existing organization, use `python -m scripts.grant_membership
--organization-id 1 --user-id 12 --role user --change-reference CHG-124
--confirm GRANT_MEMBERSHIP`. It is subject to the same OS/database restrictions
and writes an audit record. Mapping additional resources to an existing
organization, audited approvals, credential separation and operator identity
verification are not implemented.
The CLI should only be rehearsed on disposable databases for now.

## Migration and downgrade

Do not run this migration against production without an approved, tested
rollout. Back up the database, stop all application writers and seed jobs, and
rehearse on an isolated representative PostgreSQL copy with pgvector. Confirm
that the new tables are empty, inventory row/blob ownership and resolve
ambiguous data before tenant separation. The application startup currently calls
`create_all`; do not start an application instance against a database before
applying the approved migrations, or it can pre-create tables and conflict with
Alembic. `create_all` is not a substitute for Alembic. No production migration
has been performed.

Downgrading 016 discards membership roles, 015 discards resource mapping audit data, 014 discards history and
knowledge ownership (retaining newly created history tables), 013 discards
attachment ownership, 012 discards ticket mapping
audit data; downgrading 011 and 010
discards playbook, contract and ticket ownership; downgrading 009 discards
machine ownership and audit records; downgrading 008
then discards organization and membership data. Machines and users remain but
lose isolation metadata. Downgrading can also re-enable unsafe old application
behavior if old code is deployed. Export/backup and explicitly approve that
data loss first. Do not downgrade to resolve ownership ambiguity. Historical
migrations include PostgreSQL-specific pgvector operations, so SQLite-only
checks do not validate the full migration chain.

## Completion gates

Before multi-customer onboarding: complete authenticated and audited operator
provisioning and explicit mapping for all resource types; quarantine unmapped
users, rows and blobs behind enforced access checks, then design ownership and classification for every
table and blob; backfill and verify legacy rows; add appropriate non-null keys,
tenant-aware uniqueness, indexes and cross-tenant foreign-key constraints; make
provisioning transactional and server-controlled; scope every read, write,
delete, upload, download, search, export, cache and background path, regardless
of role; and test real endpoints adversarially across tenants, including
references and presigned URLs. Verify PostgreSQL upgrade/downgrade and existing
API behavior independently. Until then this is not an isolation boundary.
