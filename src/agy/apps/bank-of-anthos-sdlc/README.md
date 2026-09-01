# Bank of Anthos SDLC Workshop

This project demonstrates a governed, end-to-end brownfield software-development lifecycle with Google Antigravity. Each workshop run starts by cloning the official [GoogleCloudPlatform/bank-of-anthos](https://github.com/GoogleCloudPlatform/bank-of-anthos) repository at an immutable revision, then adds workspace guidance and delivery tooling without changing the cloned application baseline.

Bank of Anthos is Google's sample multi-service banking application. The upstream repository, documentation, and license remain authoritative for the application itself. This project supplies only the workshop setup, feature requirement, prompt, and SDLC flow.

## Workshop objective

Participants inherit an unfamiliar application containing Python, Java, PostgreSQL, Kubernetes, and multiple services. They must understand the existing system before adding a bounded frontend feature: transaction search, credit/debit filtering, and safe CSV export.

The exercise demonstrates:

```text
Clone a known application baseline
  → discover the architecture and current behavior
  → assess the feature impact
  → clarify and approve the specification
  → approve the implementation plan
  → implement the bounded change
  → test, review, and verify regressions
  → present release-readiness evidence
```

## Project contents

```text
bank-of-anthos-sdlc/
├── README.md
├── docs/
│   ├── prompt_transaction-search-and-csv-export.md
│   └── requirements_transaction-search-and-csv-export.md
├── scripts/
│   └── setup-workspace.sh
└── demo/
    ├── .gitignore
    └── bank-of-anthos-sdlc-N/  # Generated nested Git clones
```

- [`requirements_transaction-search-and-csv-export.md`](docs/requirements_transaction-search-and-csv-export.md) defines the authoritative feature scope and acceptance criteria.
- [`prompt_transaction-search-and-csv-export.md`](docs/prompt_transaction-search-and-csv-export.md) is the self-contained initial request.
- [`setup-workspace.sh`](scripts/setup-workspace.sh) creates the next available numbered brownfield workspace.
- `demo/` contains local generated runs and ignores them from the outer workshop repository.

## Create a brownfield workspace

From `src/agy/apps/bank-of-anthos-sdlc/`, run:

```bash
./scripts/setup-workspace.sh
```

The script checks `demo/bank-of-anthos-sdlc-1/`, `-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing run.

Use `--dry-run` to inspect the source, revision, and next destination without cloning or changing files:

```bash
./scripts/setup-workspace.sh --dry-run
```

The setup requires Bash, Git, Python 3, and network access to the official GitHub repositories used by the clone and tooling importers.

## Reproducible upstream baseline

The workshop baseline is the official [`release/v0.6.10`](https://github.com/GoogleCloudPlatform/bank-of-anthos/tree/release/v0.6.10) branch, pinned to its resolved immutable commit:

```text
674d9fea755df9938bc9563b559fbbbb6358b6f3
```

The branch-to-commit mapping was verified on September 1, 2026. The setup script fetches the immutable commit rather than the moving branch name so workshop runs remain repeatable if the release branch changes later.

An explicit branch, tag, or commit can be supplied when intentionally testing another revision:

```bash
BANK_OF_ANTHOS_REF=<ref> ./scripts/setup-workspace.sh
```

Google Agents CLI and Conductor refs can also be pinned:

```bash
AGENTS_CLI_REF=<ref> CONDUCTOR_REF=<ref> ./scripts/setup-workspace.sh
```

Changing any pinned ref should be treated as a workshop-baseline change and revalidated before presentation.

## What setup adds to the clone

The generated directory remains a nested Git clone of the upstream application. Setup adds:

```text
demo/bank-of-anthos-sdlc-N/
├── .git/                  # Retained upstream history and baseline
├── AGENTS.md             # Workspace contract
├── .agents/
│   ├── agents/          # Reusable SDLC subagents
│   ├── plugins/
│   │   └── conductor/   # Specification-driven workflow
│   ├── rules/           # Environment and memory rules
│   └── skills/          # Environment and Agents CLI skills
└── upstream application files
```

`AGENTS.md`, `.agents/`, and `.memory/` are added to the clone's local `.git/info/exclude`. They remain available to Antigravity but do not pollute the application diff. Setup verifies that the application baseline is clean before completing.

If cloning, seeding, importing, or verification fails, the script removes only the newly reserved incomplete directory. Existing numbered clones are untouched.

## Run the full brownfield SDLC exercise

1. Create a numbered clone with `./scripts/setup-workspace.sh`.
2. Open the new `demo/bank-of-anthos-sdlc-N/` directory as the Antigravity workspace.
3. Read `AGENTS.md` and apply the relevant rules and skills.
4. Confirm the upstream baseline:

   ```bash
   git remote get-url origin
   git rev-parse HEAD
   git status --short
   ```

5. Submit the contents of [`docs/prompt_transaction-search-and-csv-export.md`](docs/prompt_transaction-search-and-csv-export.md).
6. Perform read-only repository discovery: map services, languages, transaction flow, frontend presentation, tests, and likely change surface.
7. Establish the current test baseline and record checks that cannot run in the workshop environment.
8. Use `/conductor:conductor-setup` to establish product, technology, and workflow context.
9. Use `/conductor:conductor-new-track` to produce and review the feature specification, impact assessment, significant design decisions, and implementation plan.
10. Approve the frontend-only boundary and verification plan before implementation.
11. Use `/conductor:conductor-implement` for the approved scope.
12. Verify the feature against [`docs/requirements_transaction-search-and-csv-export.md`](docs/requirements_transaction-search-and-csv-export.md), run relevant regression checks, and use `/conductor:conductor-review` for structured review.
13. Present the focused application diff, test results, browser evidence, review findings, risks, and anything incomplete as release-readiness evidence.

## Scope boundary

The workshop feature is frontend-only. It must not change ledger APIs, databases, authentication, authorization, Kubernetes manifests, deployment topology, or unrelated behavior. It uses only the application's synthetic demonstration data.

Running the full Bank of Anthos platform may require Docker, Kubernetes, Google Cloud, and other upstream prerequisites. Environment creation, cloud deployment, IAM changes, and cost-bearing resources are separate activities requiring explicit approval; they are not performed by the setup script.
