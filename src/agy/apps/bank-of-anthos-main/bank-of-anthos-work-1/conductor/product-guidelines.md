# Product Guidelines: Cymbal Bank (Bank of Anthos)

## 1. Branding & Identity
- **Brand Name:** Cymbal Bank (formerly Bank of Anthos).
- **Core Aesthetics:** Clean, professional, trustworthy, enterprise-grade financial portal.
- **Palette and Theme:** Deep corporate blues, slate grays, clean white backgrounds, and energetic teal/green highlights for success or interactive elements.
- **Typography:** Modern, highly legible sans-serif fonts suitable for dense financial tables and transactional lists.

## 2. Voice and Tone
- **Professional & Clear:** All copy should be concise, objective, and mathematically unambiguous.
- **Helpful & Reassuring:** Since banking platforms require high trust, error messages must be constructive, explaining *why* a transaction failed and how to rectify it (e.g., "Insufficient funds for this transaction" rather than "Error 500").
- **No Jargon Overload:** Keep actions intuitive (e.g., "Send Payment", "Deposit Funds", "Download Statement").

## 3. User Experience & Interaction Principles
- **Clarity First:** Financial data (balances, transaction histories, search queries) must always load with high visual hierarchy.
- **Dynamic Interaction:**
  - Fast, immediate client-side or server-side filtering.
  - Interactive credit/debit toggles that update the interface without full page reloads where possible.
  - Search inputs with helpful placeholder text (e.g., "Search by merchant, description, or amount...").
- **CSV Data Hygiene:**
  - Exported CSV filenames must be standardized (e.g., `cymbal_bank_statement_YYYYMMDD.csv`).
  - Fields must be consistently ordered: Date, Transaction ID, Type (Credit/Debit), Description, Amount, Ending Balance.
  - CSV formatting must correctly handle double quotes, commas, and negative numbers.
- **Accessibility:** Ensure high contrast, screen-reader compatible table headers, and fully keyboard-navigable search and export interfaces.
