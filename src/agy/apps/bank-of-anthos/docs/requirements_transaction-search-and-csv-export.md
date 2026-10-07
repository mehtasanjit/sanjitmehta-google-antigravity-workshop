# Bank of Anthos Transaction Search, Filtering, and CSV Export Requirements

## Context

Bank of Anthos is an existing multi-service sample banking application. Its authenticated home page displays transaction history returned by the transaction-history service. This brownfield exercise adds a bounded customer-facing capability to that existing page without changing the service architecture.

## The need

A customer with many transactions needs a quick way to find relevant entries, distinguish incoming and outgoing activity, and export the narrowed result set for offline review.

## User

The user is an authenticated Bank of Anthos customer viewing their own transaction history on the existing home page.

## Required experience

### Search and filter

- Add a search input to the existing Transaction History card.
- Search must be case-insensitive and support partial matches against the displayed counterparty account number and contact label.
- Leading and trailing search whitespace must not affect results.
- Add a transaction-type filter with `All`, `Credit`, and `Debit` options.
- Search text and transaction type must combine using AND semantics.
- Filtering must happen against the transaction history already loaded in the page. It must not reload the page or make a new backend request.
- Show the number of matching transactions and provide a clear way to reset the controls.
- When no transaction matches the active criteria, show a clear `No matching transactions` state without replacing the user's controls.

### CSV export

- Add an `Export CSV` action to the Transaction History card.
- Export only the transactions currently visible after applying search and type filters, in their current display order.
- The CSV must contain a header row with `Date`, `Type`, `Account`, `Label`, and `Amount` columns.
- Exported values must reflect the values shown to the customer. Credits and debits must remain distinguishable, and amounts must retain their direction and decimal precision.
- Escape commas, quotation marks, and line breaks correctly.
- Prevent spreadsheet-formula execution for text values beginning with `=`, `+`, `-`, or `@` while preserving legitimate numeric amounts.
- Use a meaningful filename containing `bank-of-anthos-transactions` and the export date.
- Disable the export action when no transaction is visible.
- Generate the file in the browser. Do not send transaction data to another service.

### Existing states and accessibility

- Preserve the existing `Could Not Load Transactions` and `No Transactions Found` states.
- Do not show active search, filter, or export controls when transaction history failed to load or contains no transactions.
- Associate controls with accessible labels, support keyboard operation, and announce result-count changes through an appropriate live region.
- Keep the controls and table usable at the responsive widths supported by the current page.
- Follow the existing Bank of Anthos visual language rather than introducing a new design system.

## Scope constraints

- Limit implementation to the frontend service and its existing transaction-history presentation.
- Do not change the transaction-history API, ledger services, databases, authentication, authorization, Kubernetes manifests, or deployment topology.
- Do not add server-side reporting, scheduled exports, saved filters, pagination, analytics, or new external integrations.
- Do not introduce a new frontend framework or runtime dependency solely for this feature.
- Preserve existing payment, deposit, contact, balance, login, and signup behavior.
- Use only the application's synthetic demonstration data.

## Verification expectations

- Add focused automated coverage at the smallest practical seam supported by the repository's existing tooling.
- Verify search by account number and label, each transaction-type option, combined criteria, reset behavior, result count, and the no-match state.
- Verify that CSV output contains only visible rows in display order and correctly handles headers, quoting, special characters, and spreadsheet-formula-like text.
- Verify that export is disabled for empty results and that filtering and export do not initiate new network requests.
- Run the relevant existing frontend checks and record any check that cannot be run in the workshop environment.

## Success criteria

The feature is successful when an authenticated customer can quickly narrow the existing transaction table by counterparty information and credit/debit type, understand how many results remain, reset the view, and safely download exactly those visible results as a CSV without changing backend services or breaking existing frontend behavior.
