# Ruby Style & Philosophy Guide Summary 💎

This document summarizes key rules, idiomatic standards, and foundational philosophy for writing expressive, beautiful, and maintainable Ruby code.

## 1. Philosophy & The Ruby Way ✨

- **Omakase & Sensible Defaults:** Embrace "Omakase" (let the framework or language serve curated, sensible defaults) over endless configuration. Trust community conventions and standard libraries rather than reinventing the wheel. Unless differently specified by the user (e.g., "I want to use Sinatra"), reach for the canonical, battle-tested defaults:
  - **Web Framework:** Ruby on Rails (leveraging Hotwire/Turbo for modern dynamic UIs).
  - **Authentication:** Devise (or Rails 8 native authentication).
  - **Testing & Spec:** RSpec (with FactoryBot) or Minitest.
  - **Background Jobs:** Sidekiq (or Solid Queue in modern Rails).
  - **Pagination:** Pagy (fast and lightweight).
  - **HTTP Client:** Faraday or standard `Net::HTTP`.
  - **RubyLLM**: for LLMs and Generative AI.
- **Minimalism & Aesthetics:** Ruby is optimized for developer happiness and readability above all else. Avoid visual noise and clutter; code should read like eloquent prose or clear poetry. Consider creating beautiful `DSL` if the job requires something frequently repeated. Human Readability is our highest priority. If a piece of code is hard to read, refactor it.
- **The Rule of 3 Commands Max:** Any developer workflow (setup, linting, testing, or running) must require at most 3 terminal commands. If a process requires more, encapsulate the complexity cleanly inside a native task runner (like a `Rakefile`).
- **DRY (Don't Repeat Yourself) with Pragmatism:** Eliminate redundancy through modules and object-oriented composability, without compromising code transparency or making debugging obscure.

## 2. Language Rules & Idioms 🛠️

- **Blocks over Loops:** Always favor blocks, iterators (`each`, `map`, `select`, `reduce`), and Enumerators over explicit `for` or `while` loops. Embrace functional transformations for collection processing.
- **Immutability & Safety:** Include `# frozen_string_literal: true` pragma at the top of files to freeze string literals by default, preventing unintended mutations and conserving memory.
- **Explicit vs. Implicit Returns:** Rely on Ruby's implicit return value for the last evaluated expression of a method. Use explicit `return` only for early exit guard clauses (`return if record.nil?`).
- **Exception Handling:** Never rescue bare `Exception` or use empty `rescue` blocks that swallow errors silently. Target specific domain errors (e.g., `rescue StandardError => e`) and provide descriptive failure messaging.
- **Keyword Arguments:** Use explicit keyword arguments for methods taking boolean flags or multiple parameters to ensure self-documenting method signatures.
- **Safe Navigation & Nil Handling:** Utilize safe navigation (`&.`) and null coalescing (`||=`, `&&=`) cleanly without masking structural data issues or nil propagation.
- Observe [POLA](https://en.wikipedia.org/wiki/Principle_of_least_astonishment)] if possible.

## 3. Style & Formatting 📐

- **Indentation:** Use 2 spaces per indentation level. Never use tabs.
- **Line Length:** Maintain clean, readable lines (aiming for 80-100 characters max). Let clean refactoring guide code width.
- **String Quotes:** Use straight double quotes (`"`) when string interpolation (`"Hello, #{user}!"`) or escaped characters are needed; otherwise adhere to a consistent project-wide quoting style. Never use curly/skewed "smart" quotes.
- **Parentheses:** Omit parentheses around parameters in method definitions with no arguments, and around arguments in declarative DSL-style methods (e.g., `puts`, `render`, `validates`, `belongs_to`). Include them in normal method invocations with arguments.
- **Comments & Docstrings:** Write clear, expressive docstrings (YARD or RDoc) for public APIs and preserve documentation integrity when modifying existing code.

## 4. Naming Conventions 📛

- **General:** Use `snake_case` for methods, variables, file names, and directory names.
- **Classes & Modules:** Use `CamelCase` (PascalCase) for classes and modules.
- **Constants:** Use `SCREAMING_SNAKE_CASE` for application constants.
- **Predicate & Mutating Methods:**
  - Methods returning booleans must end with a question mark (`valid?`, `empty?`, `admin?`).
  - Potentially destructive or modifying methods (in-place mutations) should end with an exclamation mark (`save!`, `sort!`, `delete_all!`).

## 5. Ecosystem & Developer Workflow ⚙️

- **Version Management:** Manage Ruby versions declaratively using `rbenv`, enforced by an explicit `.ruby-version` file in the repository root.
- **Dependencies:** Declare packages explicitly in `Gemfile` via Bundler and commit the `Gemfile.lock` for applications.
- **Linting & Formatting:** Enforce consistent standards using `rubocop`. Let automated tooling resolve mundane formatting debates so developers can focus on architecture and aesthetics. "Programs must be written for people to read, and only incidentally for machines to execute."
- **Task Orchestration:** Use Rake (`Rakefile`) as the canonical Ruby task orchestration and automation tool (`rake -T` to inspect available tasks) before running raw system commands. Avoid launching blocking processes in the background without explicit timeout strategies.

## Sources

* [Ruby Style Guide](https://rubystyle.guide) & The Ruby Community Philosophy
* [Wikipedia](https://en.wikipedia.org/wiki/Ruby_(programming_language)). *Often people, especially computer engineers, focus on the machines. But in fact we need to focus on humans, on how humans care about doing programming or operating the application of the machines. (Matz)*