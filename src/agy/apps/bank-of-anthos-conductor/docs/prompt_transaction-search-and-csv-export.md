# Initial Prompt: Transaction Search, Filtering, and CSV Export

Help me add a bounded brownfield feature to the existing Bank of Anthos application: transaction search, credit/debit filtering, and CSV export on the authenticated home page.

Begin by reading the workspace `AGENTS.md` and inspecting the existing application before proposing changes. Use the installed Conductor specification-driven development workflow to clarify the requirements, identify significant design decisions, and produce an implementation plan before writing code. Preserve the existing architecture and conventions.

The customer must be able to search the already-loaded transaction history by partial counterparty account number or contact label, filter it by `All`, `Credit`, or `Debit`, combine search and type criteria, see the matching count, reset the controls, and see a clear no-match state. Filtering must be client-side and must not reload the page or request transaction data again.

Add an `Export CSV` action that downloads only the currently visible transactions in display order. Include `Date`, `Type`, `Account`, `Label`, and `Amount` columns; correctly escape CSV values; protect untrusted text from spreadsheet-formula execution; preserve legitimate numeric amounts; use a dated `bank-of-anthos-transactions` filename; and disable export when no rows are visible. Generate the export entirely in the browser.

Preserve the existing transaction loading and empty states, accessibility, responsive behavior, and visual language. Do not change backend APIs, ledger services, persistence, authentication, authorization, deployment configuration, or unrelated product behavior. Do not add a new frontend framework or runtime dependency. Use only synthetic demonstration data.

After the specification and plan are approved, implement only the agreed scope. Add focused verification for filtering and CSV behavior, run the relevant existing checks available in the workspace, and clearly report anything incomplete or unverified.
