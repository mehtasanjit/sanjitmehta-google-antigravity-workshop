# Bank of Anthos — Conductor and Subagents

A brownfield software-development exercise with Google Antigravity. Each run clones the [Bank of Anthos fork](https://github.com/mehtasanjit/bank-of-anthos) at a pinned commit, then adds workspace guidance without changing the application baseline. This variant runs it with the Conductor plugin and the eight SDLC subagents: the agent gets the base `AGENTS.md` guidelines, the workspace memory rule, Conductor, and the subagents. There are no other skills or plugins. Without the subagents, see [Bank of Anthos — Conductor](../bank-of-anthos-conductor/); without Conductor, see [Bank of Anthos](../bank-of-anthos/).

Bank of Anthos is Google's sample multi-service banking application. The fork currently matches the official [GoogleCloudPlatform/bank-of-anthos](https://github.com/GoogleCloudPlatform/bank-of-anthos) repository, whose documentation and license remain authoritative for the application. This folder supplies only the workshop setup, feature requirement, and SDLC flow.

## Workshop objective

Participants inherit an unfamiliar application containing Python, Java, PostgreSQL, Kubernetes, and multiple services. They must understand the existing system before adding a bounded frontend feature: transaction search, credit/debit filtering, and safe CSV export.

```text
Clone a known application baseline
  → discover the architecture and current behaviour
  → assess the feature impact
  → clarify and approve the specification
  → approve the implementation plan
  → implement the bounded change
  → test, review, and verify regressions
  → present release-readiness evidence
```

## Project contents

```text
bank-of-anthos-conductor-subagents/
├── README.md
├── setup-workspace.sh
├── docs/
│   ├── prompt_transaction-search-and-csv-export.md
│   └── requirements_transaction-search-and-csv-export.md
├── .gitignore
└── bank-of-anthos-conductor-subagents-N/   # Generated nested Git clones
```

- [`requirements_transaction-search-and-csv-export.md`](docs/requirements_transaction-search-and-csv-export.md) defines the authoritative feature scope and acceptance criteria.
- [`prompt_transaction-search-and-csv-export.md`](docs/prompt_transaction-search-and-csv-export.md) is the self-contained initial request.
- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered brownfield workspace.
- `.gitignore` keeps the generated `bank-of-anthos-conductor-subagents-N/` clones out of the outer workshop repository.

## Create a brownfield workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `bank-of-anthos-conductor-subagents-1/`, `-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing run.

Use `--dry-run` to see the repository, commit, and next destination without cloning or changing files:

```bash
./setup-workspace.sh --dry-run
```

The setup needs Bash, Git, Python 3, and network access to GitHub. If cloning, copying, importing, or verification fails, the script removes only the newly reserved incomplete directory. Existing numbered clones are untouched.

## Reproducible baseline

The baseline is the fork's `main` branch, pinned to this commit (Bank of Anthos `release/v0.6.11`):

```text
db35fea9fd090150e2398106aadb475576f80d94
```

The commit was verified on 2026-10-07. The setup script fetches this exact commit rather than the moving branch, so runs stay repeatable after new changes land on the fork. To test another revision deliberately:

```bash
BANK_OF_ANTHOS_REF=<branch-tag-or-commit> ./setup-workspace.sh
```

To pin Conductor, set `CONDUCTOR_REF` to a commit on its `main` branch. Conductor's release tags use an older layout without `plugin.json` and do not work here:

```bash
CONDUCTOR_REF=6e8f9a860bcd ./setup-workspace.sh
```

Changing a pinned ref is a baseline change; revalidate the exercise before presenting it.

## What setup adds to the clone

The generated directory remains a nested Git clone of the fork. Setup adds:

```text
bank-of-anthos-conductor-subagents-N/
├── .git/                  # The fork's history at the pinned commit
├── AGENTS.md              # Copy of src/resources/workspace-guidance/agents/base.md
├── .agents/
│   ├── agents/            # Copy of the 8 SDLC subagents
│   ├── plugins/
│   │   └── conductor/     # Conductor plugin, downloaded at setup
│   └── rules/
│       └── workspace-memory.md
└── application files from the fork
```

`AGENTS.md`, `.agents/`, `.memory/`, and `.scratch/` are added to the clone's local `.git/info/exclude`. Antigravity can still use them, but they stay out of the application diff. Setup checks that the application baseline is clean before it finishes.

## Run the brownfield exercise

1. Create a numbered clone with `./setup-workspace.sh`.
2. Open the new `bank-of-anthos-conductor-subagents-N/` directory as the Antigravity workspace.
3. Confirm the baseline:

   ```bash
   git remote get-url origin
   git rev-parse HEAD
   git status --short
   ```
4. Submit the contents of [`docs/prompt_transaction-search-and-csv-export.md`](docs/prompt_transaction-search-and-csv-export.md).
5. Have the agent explore the repository without changing it: services, languages, transaction flow, frontend presentation, tests, and the likely change surface.
6. Establish the current test baseline and record checks that cannot run in the workshop environment.
7. Use `/conductor:conductor-setup` to establish product, technology, and workflow context.
8. Use `/conductor:conductor-new-track` to produce and review the feature specification, impact assessment, significant design decisions, and implementation plan.
9. Approve the frontend-only boundary and verification plan before implementation.
10. Use `/conductor:conductor-implement` for the approved scope, delegating bounded work to the subagents in `.agents/agents/` where they fit.
11. Verify the feature against [`docs/requirements_transaction-search-and-csv-export.md`](docs/requirements_transaction-search-and-csv-export.md), run relevant regression checks, and use `/conductor:conductor-review` for structured review.
12. Present the focused application diff, test results, browser evidence, review findings, risks, and anything incomplete as release-readiness evidence.

## Scope boundary

The workshop feature is frontend-only. It must not change ledger APIs, databases, authentication, authorization, Kubernetes manifests, deployment topology, or unrelated behaviour. It uses only the application's synthetic demonstration data.

Running the full Bank of Anthos platform may require Docker, Kubernetes, Google Cloud, and other upstream prerequisites. Environment creation, cloud deployment, IAM changes, and cost-bearing resources are separate activities that need explicit approval; the setup script does none of them.
