# CI/CD, Repository Hygiene, and Post-Leak Recovery

Code can be secure while **the pipeline that produces it** is wide open. The
pipeline has access to secrets and production; if it is compromised, code review
means nothing.

Read this file when you have access to the source repository and/or the CI
configuration.

---

## 1. REPOSITORY HYGIENE

- **Repository visibility:** public or private? If public, any `.env`, backup,
  value embedded in documentation, token in a screenshot, or secret in an
  issue/PR comment is **exposed to everyone.**
- **`.gitignore` coverage:** `.env*` (including `.env.local`, `.env.production`) ·
  `*.pem` `*.key` `*.p12` `*.jks` · `*.sqlite` `*.db` · `coverage/` `dist/` `build/` ·
  IDE and OS artifacts. **Listing only `.env` is not enough.**
- **Already-tracked file:** adding it to `.gitignore` does not untrack a file that
  was already committed. Measure: `git ls-files | grep -Ei '\.env|\.pem$|\.key$|\.p12$|\.jks$'`
- **History scan (HEAD is not enough):**
  `git log -p --all -S "<key pattern>" | head -50` ·
  `git rev-list --all --objects | git cat-file --batch-check` for large/suspicious blobs.
  Patterns: `AKIA` (AWS) · `sk_live_` (Stripe) · `ghp_`/`gho_` (GitHub) ·
  `eyJhbGciOi` (JWT) · `-----BEGIN .* PRIVATE KEY-----` · `service_role` ·
  `xox[baprs]-` (Slack) · `AIza` (Google).
- **Forks and clones:** if a secret has entered a public repository, forks and
  caches cannot be deleted → **rotation is the only fix** (§3).
- **Large files/backups:** a database dump, customer list, or log archive in the repo.

## 2. THE PIPELINE (CI/CD)

- **Branch protection:** is direct push to the main branch blocked; is review
  required; are force-push and branch deletion restricted?
- **Secret access from a fork PR — the single most dangerous setting:** on
  GitHub, the `pull_request_target` and `workflow_run` triggers can run **the
  fork's code** in a context that has access to the repository's secrets. If
  either trigger is present and the workflow checks out the **PR head** with
  `actions/checkout` → **CRITICAL** (anyone can open a PR and steal the secrets).
- **Third-party action/step pinning:** is `uses: some/action@v3` pinned by tag,
  or by **full SHA**? A tag is mutable; a SHA is not.
- **Secret logging:** `set -x`, `echo $SECRET`, dumping the environment in debug
  mode. CI's secret masking only masks an exact match; a base64-encoded or split
  secret is not masked.
- **Self-hosted runners:** on a shared/persistent runner, one job can read
  another job's leftovers; fork PRs should not run on self-hosted runners.
- **Deployment key scope:** how privileged is CI's production key — deploy-only,
  or full admin? Is there a separate key per environment?
- **Artifact integrity:** is the published artifact signed; is there a traceable
  link (provenance) between the release tag and the commit?
- **Dependency install:** `npm ci` / `--frozen-lockfile`, or `npm install`
  (version drift)? Are `postinstall` scripts disabled (`--ignore-scripts`)?
- **Environment separation:** does staging point at the same database as
  production; does staging hold real PII?

## 3. POST-LEAK RECOVERY — THE ORDER MATTERS

If a secret has leaked, **the first step is NOT deleting it from the file.**
Deleting it hides the leak but leaves the key valid. The correct order:

1. **REVOKE / ROTATE (this first).** Invalidate the key from the provider's
   console and issue a new one. As long as the key remains valid, deleting it
   from history achieves nothing.
2. **Check for abuse.** In the provider's access log, look for unexpected usage
   since the leak date: a new IP/region, unusual volume, a newly created
   sub-key or user. **Record this in the report in writing** — "checked, no
   anomaly through [date]" or "NOT MEASURED, no log access".
3. **Distribute the new key.** Environment variables, CI secrets, the team.
   Confirm the old key is left nowhere.
4. **Scrub history (optional, last).** Remove it from history with
   `git filter-repo` / BFG, then force-push. **Note:** forks, clones, CI caches,
   and search-engine caches are not cleaned — this step is cosmetic and does NOT
   replace step 1.
5. **Prevent a repeat.** Fix `.gitignore` · add a pre-commit secret scanner
   (pre-commit hook / CI step) · move the secret to the correct layer (see
   `kod-inceleme-guvenlik.md` §3).
6. **Is notification required?** If what leaked grants access to **personal
   data**, the data controller's notification obligation under KVKK (Turkey's
   Law on the Protection of Personal Data) may be triggered. This is a **legal
   determination** — the technical report states "notification may be required,
   seek legal advice" and does not decide it itself.

**Minimum line to record in the report:** what leaked · when it entered (first
commit date) · how long it was exposed · who could access it (public/private) ·
was it rotated (yes/no + date) · result of the abuse check.

---

## 4. DEPENDENCY CONFUSION

An internal package name is **unclaimed** on the public registry → an attacker
publishes it publicly, and the build pulls that instead of the internal one.
(Different from typosquatting: this comes from namespace/scope ownership, from
the **existence** of the internal package name.)

**Signature to look for:** internal/private package names · registry/scope
configuration · `.npmrc`/`pip.conf` source priority (is the private registry
checked first, or the public one) · is scope (`@org/package`) ownership
confirmed on the public registry.

**PoC/mutant:** search for the internal package name on the public registry
with a harmless name-check — if it is not registered, it means it **can be
claimed**, a finding. **Severity: CRITICAL** (build-time RCE).

## 5. CI OIDC → CLOUD TRUST MISCONFIGURATION

A workflow that authenticates to the cloud via OIDC has a trust policy whose
`sub` claim is **wildcarded** (`repo:*`, `ref:*`) → another repo/branch can
assume the cloud role.

**Signature to look for:** the cloud IAM trust policy
(`token.actions.githubusercontent.com`) · how narrow the `sub`/`aud` condition
is — pinned to a specific repo+branch, or a wildcard. **Severity: CRITICAL.**

## 6. CONTAINER & IaC HARDENING (T12)

- **Container:** running as root (no `USER`) · `latest` tag · a secret in a
  layer (a token embedded via `ARG`/`ENV` — it stays in the image layer,
  readable with `docker history`) · base-image CVEs · `--privileged` · mounting
  the Docker socket · unnecessary capabilities.
- **IaC:** a public S3/bucket · a `0.0.0.0/0` security group · an IAM `*:*`
  wildcard · an unencrypted disk/DB · a public snapshot · logging disabled.
  **K8s:** a privileged pod · `hostPath` mount · `allowPrivilegeEscalation` ·
  no network policy · a secret in plain env.
- **Tooling:** `trivy config`, `checkov`, `tfsec`, `kube-score` (the mechanical
  layer — used together with `kod-inceleme-guvenlik.md` §5; the output still
  passes through gedik's judgment, K2 is preserved).

---

## Quick close-out check

1. Was it proven, via `git ls-files`, that **no** tracked secret file exists?
2. Was history scanned across `--all` with at least five key patterns?
3. Is `pull_request_target` / `workflow_run` present; if so, is the PR head checked out?
4. Are third-party actions pinned by SHA?
5. Is main-branch protection and mandatory review turned on?
6. For every secret found, was the **was it rotated** question answered
   (deleted ≠ rotated)?
7. Was it measured whether internal package names are unclaimed on the public
   registry (dependency confusion, §4)?
8. For workflows that authenticate to the cloud via OIDC, is the trust policy's
   `sub`/`aud` condition narrow (§5)?
9. If T12 is YES (IaC/cloud): was container root/latest/secret and IaC hardening
   (public bucket, IAM wildcard, privileged K8s pod) measured (§6)?
