# Product Definition: Bank of Anthos - Antigravity Brownfield Workshop

## 1. Product Vision
Bank of Anthos is a realistic, multi-service payment processing network simulator designed to replicate an enterprise-grade banking application. The goal of this Antigravity Brownfield Workshop is to build upon the existing microservices architecture to introduce robust user-facing financial history utilities, specifically:
- Advanced transaction search and query capabilities.
- Dynamic filtering by credit/debit types.
- Transaction record exporting in standard CSV format.

These features will be implemented across the Python-based Frontend and Java-based Ledger/Transaction services, demonstrating how to evolve a complex, polyglot application safely using Spec-Driven Development (SDD).

## 2. Core Features & Capabilities
- **Mock Account Management:** User registration, profile authentication, and secure JWT-based session state.
- **Payment Processing:** Sending and depositing funds to registered contacts or external accounts.
- **Transaction History:** Auditing ledger balances and historical transactions with real-time balance calculations.
- **Advanced Search & Filter (New):** Querying transaction history by text, date, and transaction types (Credit/Debit).
- **Data Export (New):** Downloading transaction summaries as formatted CSV files for offline analysis.

## 3. Architecture & High-Level Design
The system is structured as a collection of distributed microservices communicating via HTTP and gRPC, persisting data across PostgreSQL databases:
- **Frontend (Python/Flask):** Serves the UI, handles routing, and proxies requests to backend services.
- **User Service (Python/Flask) & Contacts (Python/Flask):** Handle account lookup and recipient contact lists.
- **Ledger Writer (Java/Spring Boot):** Validates and registers new payment transactions.
- **Balance Reader (Java/Spring Boot) & Transaction History (Java/Spring Boot):** Query and cache balances and transaction history.
- **Databases (PostgreSQL):** `accounts-db` for user data and `ledger-db` for transaction history.
- **Load Generator (Python/Locust):** Simulates background user actions.

## 4. User Experience & Value
Users gain absolute clarity and transparency over their mock transaction histories, replicating real-world online banking tools. Features are designed to be fast, responsive, and intuitive, matching modern consumer bank standards.
