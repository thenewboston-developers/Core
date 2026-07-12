# Codex review: a mycelium control plane for Core

## Executive summary

The four repositories already contain the beginnings of the intended economic model:

- A **Core** is a small, independently operated currency ledger. It accepts signed blocks, moves balances atomically, and delivers blocks to recipients over authenticated WebSockets.
- **thenewboston-Backend** is a registry and bridge. A `Currency.domain` identifies an external Core, and hosted wallets can deposit to and withdraw from it. The backend already has Redis, Channels, Celery workers, Celery Beat, health checks, and Sentry integration.
- **tnbOS** treats multiple Cores as networks. Its apps put `pid`, `fn`, and `params` into signed block payloads, which is already a simple application protocol carried over a currency network.
- **thenewboston-Frontend** exposes currencies and bridge wallets and has Sentry reporting plus a WebSocket-to-polling deployment notification fallback.

What does **not** exist today is Core-to-Core communication, durable peer membership, structured telemetry, release management, or any agent capable of diagnosis and repair. The current Core `set_peers` RPC only lets a connected account ask one Core to track whether other accounts are online on that same Core. It is not server discovery or federation.

The recommended design is a separate **mycelium control plane** beside the financial data plane. Cores exchange signed, redacted, content-addressed observations and repair outcomes. AI can cluster failures, produce diagnoses, and propose patches, but it must never be able to mutate a peer directly. A repair moves through evidence, reproduction, tests, policy checks, operator approval, a signed release, canary deployment, health verification, and automatic rollback. Each Core remains sovereign and chooses its peers, disclosure policy, trust policy, and update policy.

This is a practical route to a self-healing and self-improving network without creating a remote-code-execution mesh or allowing a popularity contest to rewrite monetary rules.

## What the code supports today

### Core: one sovereign ledger, not yet a network of servers

Relevant code:

- `core/blocks/serializers/block.py` verifies an Ed25519 signature and locks the sender account with `select_for_update()`.
- `core/blocks/views/block.py` applies the debit, credit, and transaction fee inside Django's `ATOMIC_REQUESTS` transaction.
- `core/accounts/consumers.py` authenticates a WebSocket with a signed, expiring token and uses Channels groups for blocks, balance changes, and presence.
- `core/config/models.py` gives a Core one owner account and one transaction fee configuration.
- `core/project/settings/logging.py` writes conventional text logs only to the console.
- `docker-compose.yml` runs one Core API, PostgreSQL, Redis, nginx, and certificate renewal.
- `scripts/deploy.sh` pulls mutable `latest` images and recreates services; it has no signed manifest, canary, health gate, or rollback state.

The ledger has valuable foundations: public-key identity, signed messages, database transactions, immutable-by-API blocks, Redis-backed fan-out, and per-Core ownership. However, the block model is not a hash-linked blockchain and Cores do not replicate ledger state. A Core is currently the authority for its own balances. The control-plane design should be honest about this and should not imply Byzantine consensus that is not present.

There are also production issues to resolve before autonomous operations are considered:

- `Block.save()` only logs a warning if an existing block is modified. Immutability must be enforced at the API, model/service, and preferably database layers.
- The Core uses one owner account for configuration but has no distinct node identity, operator identity, or release-signing identity.
- WebSocket RPC authorization checks `self.account_number` rather than authenticated state in `rpc_set_peers()` and `rpc_get_peers()`. Because the number is set from the URL during `connect()`, these methods need an explicit authenticated flag before more powerful RPCs are added.
- Request-body debug logging can disclose payload content. Raw logs must never become the peer-sharing format.
- `ALLOWED_HOSTS = ['*']`, permissive CORS, mutable image tags, old base images, dependency versions, and deployment-time migrations all increase the blast radius of automatic repair.
- There is no Celery worker in Core. Redis is currently a Channels transport, not a durable job or event system.

### Backend: registry, economic bridge, and useful job infrastructure

Relevant code:

- `thenewboston/currencies/models/currency.py` associates an external currency with a unique domain.
- `thenewboston/api/accounts.py` fetches Core balances and submits signed blocks.
- `thenewboston/wallets/models/wallet.py` creates a deposit key pair for an external currency.
- `thenewboston/wallets/views/wallet.py` bridges deposits and withdrawals between backend balances and an external Core.
- `thenewboston/project/celery.py` and `thenewboston/project/settings/celery.py` provide Redis-backed workers and periodic jobs.
- `thenewboston/project/settings/sentry.py` provides centralized error ingestion for the legacy service.
- Channels consumers and the frontend-deployment endpoint demonstrate real-time fan-out with client polling as a fallback.

This makes the backend a good **bootstrap directory and compatibility bridge**, but it must not become the permanent root of trust for the new network. It can publish an initial list of Core descriptors and aggregate public health, while Cores retain signed descriptors and continue operating if the backend is unavailable.

Bridge operations currently make synchronous network calls during HTTP requests, use broad exceptions, and do not show idempotent reconciliation around the external transfer and local balance update. Before the system depends on the bridge during failures, deposits and withdrawals should become durable state machines processed by Celery with idempotency keys, timeouts, retry policy, and reconciliation jobs. Private deposit signing keys also deserve envelope encryption or a dedicated signing service.

### tnbOS: the strongest prototype for a multi-Core application protocol

Relevant code:

- `src/system/store/networks.ts` stores multiple network descriptors.
- `src/system/components/WebSocket/index.tsx` opens and authenticates one WebSocket per network.
- `src/system/components/NetworkPeerSyncManager/index.tsx` synchronizes account presence.
- `src/system/core/blocks.ts` submits signed blocks to a selected network.
- `src/system/routers/blockRouter.ts` dispatches a received block according to `payload.pid`.
- Individual apps implement `pid` / `fn` / `params` payloads, validation, routing, receipts, retries, and business state.

This is a useful model for versioned control messages, but tnbOS is an Electron client with locally persisted signing keys and application state. It should be an observer/operator console for the control plane, not a privileged repair executor. The existing app registry is compiled into the client; it is not yet an isolated third-party application runtime despite the platform goal.

### Frontend: public visibility and operator workflow

The frontend already has currency discovery, wallet bridging, Sentry, Redux event handling, and deployment-update UX. It is the right place for public Core health and incident transparency, while privileged approvals should require strong operator authentication and signed actions rather than an ordinary browser session.

## The architectural boundary

The system needs two planes with different rules:

| Plane | Carries | Availability goal | Mutation authority |
| --- | --- | --- | --- |
| Financial data plane | blocks, balances, account notifications, application payloads | remain small and deterministic | the Core's ledger rules and signed account actions |
| Mycelium control plane | node descriptors, health observations, incident fingerprints, repair proposals, attestations, release notices, outcomes | may degrade without stopping payments | local operator policy only |

Control traffic should not be hidden in ordinary paid blocks. Doing so couples incident response to balances and transaction fees, pollutes the financial history, exposes telemetry to application recipients, and makes overload in one plane damage the other. Reuse the cryptographic concepts and schema style, but provide dedicated `/control/v1/...` HTTP endpoints and `/ws/control/v1` events. A later transport can use libp2p, QUIC, or a message broker without changing the signed envelope.

The backend bridge remains a third component: it translates between legacy hosted balances and sovereign Cores. It observes both planes but does not decide a Core's ledger or releases.

## Identity, discovery, and trust

### Separate keys by purpose

Do not use one account signing key for every authority. Each operator should have:

1. An **offline owner key** that delegates or revokes node and release keys.
2. A rotating **node key** used for mutual authentication and signed control events.
3. A **release key** held by CI/release infrastructure, ideally hardware-backed.
4. Existing **account keys** used only for financial blocks and client authentication.

A signed Core descriptor can contain:

```json
{
  "schema": "tnb.core-descriptor/1",
  "core_id": "sha256-of-offline-owner-key",
  "owner_key": "...",
  "node_keys": [{"key": "...", "not_before": "...", "not_after": "..."}],
  "endpoints": {"data": "https://currency.example", "control": "https://currency.example/control/v1"},
  "currency": {"ticker": "EXM"},
  "software": {"release_digest": "sha256:...", "protocols": ["tnb-control/1"]},
  "disclosure_policy": "public-fingerprints",
  "sequence": 42,
  "expires_at": "...",
  "signature": "..."
}
```

The backend can serve descriptors for discovery. Nodes should cache them, verify the owner signature, reject expired or decreasing sequence numbers, and learn additional peers through signed introductions. DNS is a locator, not identity. Peer sets should be bounded and diverse across operator, hosting provider, geography, software version, and network prefix to reduce eclipse and Sybil attacks.

Trust is local policy, not a universal score. A Core can choose to accept observations from open peers, accept repair attestations only from named maintainers, and auto-install only releases signed by its configured release quorum. Reputation may help prioritize evidence, but it must not grant direct execution rights.

## The shared language: structured observations, not shared raw logs

Every Core should first produce structured local telemetry using OpenTelemetry-compatible traces, metrics, and JSON log records. Add a logging handler that converts selected events to a stable `Observation` schema. It must redact before persistence and before any network call.

An observation should contain:

- event ID, schema version, Core ID, software digest, protocol version, and timestamp;
- severity and component (`api`, `database`, `redis`, `websocket`, `ledger`, `bridge`);
- a normalized fingerprint from exception type, scrubbed stack-frame symbols, error code, and release digest;
- symptoms such as rate, latency, queue depth, resource pressure, and affected endpoint class;
- bounded, redacted diagnostic fields;
- a content hash, previous event hash or local sequence, expiry, and node signature.

It must not contain signing keys, authorization headers, cookies, request bodies, block payloads, user identifiers, raw account numbers, environment variables, database values, or source snippets by default. Account numbers can be locally salted and bucketed when correlation is necessary. Stack traces stay local unless an operator explicitly raises the disclosure level.

Peers normally exchange compact **fingerprint summaries** using a gossip protocol. A receiving peer requests more evidence only if its policy permits it. Use deterministic IDs, deduplication, TTLs, hop limits, per-peer quotas, and backpressure. Store the durable event/outbox in PostgreSQL; Redis Pub/Sub and Channels may notify local processes but must not be the only copy because they do not provide the required delivery semantics.

Example envelope:

```json
{
  "schema": "tnb.observation/1",
  "id": "uuid",
  "core_id": "...",
  "sequence": 1042,
  "observed_at": "...",
  "expires_at": "...",
  "release_digest": "sha256:...",
  "component": "websocket",
  "severity": "error",
  "fingerprint": "sha256:...",
  "symptoms": {"events_5m": 81, "p95_ms": 2400},
  "evidence_digest": "sha256:...",
  "signature": "..."
}
```

Signed does not mean true. A signature provides provenance; independent observations, local reproduction, and tests provide confidence.

## The self-healing loop

The loop should be explicit and auditable:

```text
observe -> redact -> fingerprint -> correlate -> diagnose -> reproduce
        -> propose -> verify -> approve -> canary -> evaluate -> promote/rollback -> learn
```

### 1. Observe locally

Health probes cover the API, PostgreSQL, Redis/Channels, certificate lifetime, disk, memory, migrations, block acceptance latency, WebSocket delivery, worker backlog, and bridge reconciliation. Synthetic probes use dedicated zero-value or test accounts and never mutate production monetary state unexpectedly.

### 2. Correlate across the mycelium

A local incident is promoted when a fingerprint exceeds a local threshold. Peer summaries answer questions such as:

- Is the failure local to one host or present across operators?
- Did it begin after the same release digest?
- Is it limited to one dependency, database version, protocol version, or traffic pattern?
- Have peers already mitigated it, and what happened afterward?

Clustering should happen on fingerprints and bounded features, not on raw log aggregation. The node records dissent and counterexamples rather than collapsing them into one confident story.

### 3. Diagnose with constrained AI

An AI diagnostician receives a read-only incident bundle: sanitized evidence, exact source revision, dependency lockfiles, relevant tests, configuration schema, and previous repair outcomes. It has no production credentials and no direct control-plane send capability. Its output is a structured `Diagnosis` with hypotheses, confidence, evidence for and against each hypothesis, missing evidence, proposed experiments, and risk classification.

Use deterministic tools before an LLM wherever possible: schema validation, dependency advisories, static analysis, test failure clustering, `git bisect`, query plans, resource thresholds, and known-runbook matching. The model is a hypothesis generator and code author, not an oracle.

### 4. Reproduce in isolation

The repair worker creates an ephemeral environment pinned to the exact failing release and sanitized replay fixture. Network egress is denied by default, secrets are synthetic, CPU/time/output are limited, and the filesystem is disposable. A proposal cannot advance without a reproducible test or an explicit operator waiver for an operational mitigation.

### 5. Produce a repair proposal

A proposal is a normal source patch plus machine-readable metadata:

- incident and evidence digests;
- base commit and resulting source digest;
- files and permissions changed;
- tests added and commands run;
- data-migration and protocol-compatibility impact;
- predicted benefit, blast radius, rollback procedure, and expiry;
- AI/tool provenance and human authorship/approval attestations.

Peers share proposal hashes, test recipes, and outcomes. Source can be fetched from a content-addressed store or the normal Git forge. Never send a shell command for a peer to execute.

### 6. Verify in layers

Verification should include unit and integration tests, lint/type checks, migration checks, property tests for ledger invariants, fuzzing of signed envelopes and payloads, dependency and secret scanning, container/SBOM generation, reproducible build checks, and protocol compatibility against the current and previous supported versions.

Financial invariants require an especially strong gate:

- no negative balances;
- debit equals credit plus the configured fee;
- duplicate block IDs cannot apply twice;
- a rejected block changes no state;
- blocks cannot be mutated after creation;
- signatures cover a versioned canonical encoding;
- database commit and externally visible notifications remain ordered correctly.

Any change to signatures, balance arithmetic, fees, ownership, migrations, key handling, authentication, disclosure policy, or update policy is **never eligible for unattended deployment**.

### 7. Approve by policy

Suggested automation classes:

| Class | Examples | Maximum automatic action |
| --- | --- | --- |
| A: reversible operations | restart a crashed worker, reconnect Redis, clear an explicitly disposable cache | local runbook with cooldown and audit event |
| B: bounded configuration | reduce concurrency, disable a feature flag, route around an unhealthy peer | signed policy, range limits, canary, automatic rollback |
| C: ordinary code | parser bug, memory leak, retry correction | human-reviewed signed release, then canary automation |
| D: critical/economic | ledger, auth, keys, migrations, protocol, update system | multi-party human approval and scheduled rollout only |

Quorum means signatures from identities configured by the local operator, not “most Cores on the internet.” Small operators can subscribe to a maintainer release channel; larger operators can require their own signature as well.

### 8. Canary and rollback

Build immutable images referenced by digest, sign them, attach an SBOM and provenance, and retain the previous image and database compatibility state. Deploy first to a shadow or canary instance. Replay sanitized traffic, then direct a small bounded fraction of production reads or synthetic requests. Compare error rate, latency, resource use, ledger invariants, and peer compatibility against a baseline.

Promotion requires a stable observation window. Regression triggers rollback automatically. Database changes use expand/contract migrations so both old and new code can run during the window; destructive migrations are never autonomous. A watchdog outside the application must be able to restore the previous known-good digest if the application or its agent is unhealthy.

### 9. Learn from outcomes

Every repair ends with a signed `RepairOutcome`: attempted digest, environment, metrics before and after, duration, rollback status, and operator assessment. Peers use outcomes to update confidence in a proposal for comparable environments. The network improves because evidence and verified remedies accumulate, not because models rewrite themselves in production.

Model and prompt updates follow the same release process as code. Evaluation suites should measure diagnosis accuracy, false-remediation rate, secret leakage, unsafe-command generation, and abstention. There should be no online weight training from untrusted peer content.

## Proposed Core modules

Keep the first implementation inside the Core repository but separated into Django apps and worker processes:

```text
core/
  telemetry/       structured local observations, redaction, fingerprints, health probes
  federation/      descriptors, peer policy, signed envelopes, gossip, quotas
  incidents/       correlation, evidence bundles, state machine, audit history
  repairs/         proposals, attestations, outcomes, policy decisions
  releases/        signed manifests, canary state, promotion and rollback records
  agents/          adapters to isolated diagnosis and repair workers
```

Core will need Celery and Celery Beat (or an equivalent durable worker system), a PostgreSQL outbox, and separate queues for health, federation, analysis, and deployment. Reuse the backend's `run_task_on_commit()` pattern and periodic-task structure, but do not share a Redis instance or database across sovereign Cores. Channels remains suitable for local UI notifications.

Important persisted models include `NodeIdentity`, `OwnerDelegation`, `Peer`, `PeerPolicy`, `Observation`, `OutboxEvent`, `Incident`, `EvidenceBundle`, `Diagnosis`, `RepairProposal`, `Attestation`, `ReleaseManifest`, `DeploymentAttempt`, `RepairOutcome`, and append-only `AuditEvent`. Large evidence blobs live in encrypted object storage referenced by digest and retention policy.

The incident state machine should permit only explicit transitions:

```text
observed -> investigating -> reproduced -> proposed -> verified -> approved
         -> canarying -> promoted -> resolved
                         \-> rejected
                         \-> rolled_back
```

Every transition records actor, policy decision, input hashes, timestamp, and signature. AI services can request `Diagnosis` and `RepairProposal` creation but cannot write approval, promotion, or policy records.

## Protocol and implementation rules

1. Define schemas first using JSON Schema or Protocol Buffers and include a version in every signed object.
2. Replace implicit JSON ordering with a specified canonical encoding such as RFC 8785 JSON Canonicalization Scheme, with cross-language test vectors for Python and TypeScript.
3. Use mutual TLS for transport plus Ed25519 envelope signatures for durable provenance. Prevent replay with sequence numbers, timestamps, expiry, and stored deduplication IDs.
4. Make all handlers idempotent. Assume duplicates, reordering, partitions, slow peers, and malicious payloads.
5. Bound every input: body size, nesting, string length, decompression ratio, evidence size, rate, fan-out, and retention.
6. Use an allowlist of message types and schema versions. Unknown messages are quarantined, not dynamically dispatched to code.
7. Separate public health, peer-only evidence, and operator-private detail. Redaction occurs at the source.
8. Treat peer observations and all AI text as hostile input. They can influence analysis but never form shell commands, file paths, SQL, prompts, or deployment manifests without structural validation and policy gates.
9. Maintain an append-only audit trail and export it so an operator can reconstruct why every action occurred.
10. Provide a physical or configuration-level kill switch that disables federation, AI analysis, and automatic operations independently while payments continue.

## Threat model

The design must expect:

- **Sybil and eclipse attacks:** require owner-rooted identity, bounded peer sets, diversity, and locally configured trust.
- **Poisoned telemetry and prompt injection:** sanitize structured fields, isolate untrusted text, require corroboration and local reproduction, and never give the diagnostician production tools.
- **Malicious repair proposals:** verify source diff, tests, provenance, signatures, permissions, and local policy; build locally or reproduce the build.
- **Secret and personal-data leakage:** source redaction, data classification, encryption, minimal retention, and no raw-log gossip.
- **Compromised node keys:** short-lived delegation, rotation, revocation, and offline owner recovery.
- **Compromised release infrastructure:** threshold approval for critical releases, reproducible builds, independent attestations, canaries, and external rollback.
- **Cascading bad updates:** randomized rollout windows, cohort limits, version diversity, health gates, and circuit breakers.
- **Control-plane denial of service:** quotas, priorities, TTLs, bounded queues, peer scoring, and complete isolation from financial request capacity.
- **AI monoculture:** multiple diagnostics, explicit uncertainty, deterministic tests, dissent retention, and no requirement that all nodes run one model or accept one proposal.
- **Governance capture:** transparent signed policies and outcomes, operator choice, forkability, and no global majority with authority over a sovereign Core.

## Staged roadmap

### Phase 0: harden the organism before connecting it

- Enforce block immutability and add ledger invariant/property tests.
- Fix WebSocket authenticated-state checks and add RPC authorization tests.
- Pin production images by digest, upgrade the build base and dependencies, add health checks to Core, and make rollback explicit.
- Define canonical signed encodings with Python/TypeScript test vectors.
- Add structured logging and source redaction; remove request bodies from production diagnostics.
- Add durable, reconciled, idempotent bridge jobs in the backend.

Exit criterion: one Core can fail, recover, and roll back deterministically without federation or AI.

### Phase 1: nervous system

- Add health probes, metrics, `Observation`, incidents, audit events, Celery workers, and an outbox.
- Build a local operator dashboard and public read-only health endpoint.
- Implement Class A runbooks only, with cooldowns and audit records.

Exit criterion: the Core detects known failures, performs bounded local recovery, and proves what it did.

### Phase 2: mycelium federation

- Add owner/node identities, descriptors, peer policy, signed envelopes, and bootstrap discovery through the backend.
- Gossip only synthetic incidents and redacted fingerprints at first.
- Test partitions, replay, equivocation, Sybils, large payloads, clock skew, and compromised peers.

Exit criterion: a hostile peer cannot change financial state, exhaust the data plane, leak local secrets, or trigger an operation.

### Phase 3: collective diagnosis

- Correlate incidents across releases and environments.
- Add isolated AI diagnosis with read-only evidence bundles and deterministic tools.
- Share diagnoses, reproduction recipes, proposal hashes, and outcomes.
- Keep all code deployment human-approved.

Exit criterion: cross-Core evidence measurably reduces mean time to diagnosis without raising data leakage or false-remediation rates.

### Phase 4: verified repair pipeline

- Generate patches in disposable sandboxes, add tests, build signed immutable artifacts, and create attestations.
- Implement shadow/canary deployment and external automatic rollback.
- Allow policy-approved Class B configuration changes; retain human approval for code.

Exit criterion: intentionally seeded failures can be reproduced, repaired, canaried, and rolled back with a complete audit chain.

### Phase 5: cautious self-improvement

- Permit unattended promotion only for narrowly defined, reversible, repeatedly proven repair classes.
- Federate evaluation results for prompts/models and promote them through the same release gates.
- Expand automation one policy at a time based on measured false-positive and rollback rates.

There should be no phase called “unrestricted autonomous code execution.” Increasing intelligence should increase the quality of proposals and evidence, not erase authority boundaries.

## How the repositories fit together

| Repository | Near-term responsibility |
| --- | --- |
| Core | sovereign ledger; local telemetry; federation; incident and repair state; local policy enforcement; canary/rollback hooks |
| thenewboston-Backend | currency/Core bootstrap directory; legacy wallet bridge; durable reconciliation jobs; optional aggregation of public health |
| tnbOS | multi-network user client; application payloads; optional operator/observer console for incidents and signed approvals |
| thenewboston-Frontend | public network status, currency health, bridge status, incident transparency, and non-sensitive update UX |

The backend and frontend should label degraded Cores and pause new bridge actions when reconciliation is unsafe, while allowing users to see existing status. tnbOS should continue connecting directly to chosen Cores. None of these clients should receive node private keys or bypass Core policy.

## Measures of success

Track outcomes rather than an abstract “intelligence” score:

- mean time to detect, correlate, diagnose, mitigate, recover, and roll back;
- percentage of incidents reproduced before a repair is proposed;
- false diagnosis, false remediation, rollback, and operator-override rates;
- percentage of observations redacted locally and number of disclosure violations (target: zero);
- data-plane latency/error impact caused by the control plane (target: negligible and capped);
- bridge reconciliation age and unmatched-transfer count;
- peer diversity and fraction of incidents with independent corroboration;
- reproducible-build and attestation coverage;
- percentage of automated actions that are bounded, idempotent, and reversible;
- survival of payment traffic during backend, federation, AI-provider, and peer outages.

## Recommended first vertical slice

Start with one deliberately mundane failure: Redis/Channels becomes unavailable, causing recipient WebSocket delivery to fail while PostgreSQL and the ledger remain healthy.

1. A Core emits a redacted structured observation and creates an incident.
2. A local Class A runbook checks Redis, restarts only the local Redis/worker service if policy allows, and applies a cooldown.
3. The Core records before/after probes and a signed outcome.
4. Two test peers exchange only the incident fingerprint and outcome summary.
5. A peer with the same fingerprint can suggest the known runbook, but the receiving Core independently checks preconditions and applies its own policy.
6. The operator dashboard shows the evidence, action, and result.

This slice exercises identity, redaction, durable events, gossip, policy, recovery, and auditability without allowing AI-written code or risking ledger arithmetic. Once it is reliable under adversarial tests, add AI-generated diagnosis in shadow mode, then patch proposals, and only much later canary deployment.

The mycelium metaphor is strongest when implemented as **shared sensing, shared memory, and locally governed adaptation**. Each Core contributes evidence to the network and benefits from verified experience, but retains its own boundary, keys, currency, and final authority. That is the architecture most likely to remain useful under the exact conditions this system is meant to survive: institutional failure, unreliable infrastructure, adversarial participants, and loss of central coordination.
