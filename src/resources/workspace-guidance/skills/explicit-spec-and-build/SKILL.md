---
name: explicit-spec-and-build
description: >
  Design and build software deliberately with the user: walk through it from the person's side,
  check it against how the system really behaves, settle every behaviour explicitly in plain
  words and scenario tables, write the decisions down, then build in small tested steps. Use
  whenever the user wants to design, specify, plan or start building a feature, command, setup
  flow, installer, integration or any behaviour other people will rely on — including casual
  asks like "how should X work?", "let's think this through", "spec this out", "before we
  build…" or "what happens when…". Also use when a design discussion is going in circles or the
  user seems confused by the terms being used.
---

# Explicit Spec and Build

The goal is software where every behaviour was chosen on purpose, not left to fall out of the
implementation. The user makes the decisions; your job is to make each decision visible, plain
and checkable, then build exactly what was decided.

This takes more back-and-forth up front. That is intended: it is far cheaper to change a table
in a conversation than behaviour that people already rely on.

## Principles

### 1. Start from the person, then check against the system

Begin with what the person does, step by step: "someone opens a new repo; what's the first thing
they do?" Zoom in from there. This decides *what* to build and keeps out anything no journey
needs.

Then check that journey against how the system actually behaves: the tools, file formats,
APIs and platforms involved. The system can veto a journey, and some requirements come only
from the system (correctness, durability, security). Go back and forth; don't let the design
harden before the system has had its say.

Remember there may be several people involved (the one running the tool, an admin, a consumer
of its output) and sometimes the "user" is another program. Name who you mean.

### 2. Use plain words, and question every term

Explain things in everyday language. Don't coin labels, and don't use a tool's jargon without
saying what it means. If a concept can't be explained simply, it isn't understood yet, or it
isn't needed.

When the user asks "what does X mean?", treat it as a design signal, not just a vocabulary
question: the name, or the concept, may need to change.

### 3. Choose the simplest thing that works, and say what's deferred

Build for the real need now. Prefer one file over two, one flag over three, one code path over
one per case. When something is deferred, write it down under "not covered yet" so it isn't
forgotten or built by accident.

Simplicity also means one shared implementation with thin, clearly separated adapters for the
parts that genuinely differ.

### 4. Make behaviour explicit and keep the user in control

- **Never assume the widest scope.** Default to the narrowest, least surprising option (this
  folder, just this person), and ask before anything machine-wide or shared.
- **Detect, then confirm.** Offer what you found as the default; let the person accept or
  change it. Every question should also have a flag, so it can run unattended.
- **Show everything before changing anything:** a summary of every decision and every file that
  will change, then a confirmation that defaults to *no*. Print the summary even in unattended
  runs, as a record.
- **Nothing silent.** An explicit input that's wrong is an error. A missing optional thing is a
  clear warning. Never silently ignore, skip or guess.
- **Say what will happen, in plain words, naming the files.** "Add the settings file to git?" is
  better than "share this setup?".

### 5. Pin down every case in one scenario table

When inputs interact (flags, detected state, interactive vs unattended), write a single table
with a row for every combination and exactly what happens. Don't split interacting inputs across
separate tables; the interactions are where the gaps hide.

Anything not in the table isn't designed yet. The table also turns directly into tests.

### 6. Verify against reality, not memory

Before building on an assumption about an external system, check it. Run a small probe in a
throwaway folder (never against real settings or data), log what actually happens, and compare
with any ground truth available. Record the versions you verified, because tools change under
you, sometimes silently.

Say plainly what was verified, what came only from docs, and what is still unknown.

### 7. Write decisions down, and keep the docs matching what's built

Record each decision in the spec as it's made, including rejected options when the reason
matters. Mark anything designed but not built as *(not built yet)*. When code changes behaviour,
update the doc in the same step. A doc that describes code that doesn't exist, or misses code
that does, is worse than no doc.

### 8. Build in small, tested steps, and check completeness first

Before each build step, review the spec for completeness: go through every piece of state and
ask "what could go wrong with this, and would we notice?" Then build one small piece with tests,
run them, and report plainly what was built, what wasn't, and what changed from the plan.

Tests should run in isolation (temporary folders, controlled environment) and can enforce the
structure itself, e.g. that shared code never depends on harness-specific code.

## Workflow

For a new feature, command or behaviour:

1. **Walk through it from the person's side.** Describe the journey step by step, from the very
   first thing they do. Name everyone involved.
2. **List the decisions**, each with the options, the trade-off and your recommendation. Raise
   them a few at a time, in the order they block each other, rather than all at once.
3. **Write the scenario table** for anything with interacting inputs.
4. **Probe the unknowns** against the real system before designing around them.
5. **Write the spec**: purpose, inputs, behaviour step by step, the scenario table, what gets
   created or changed, what's not covered yet, and the tests.
6. **Review for completeness** with the user before building.
7. **Build one small piece**, with tests. Run them.
8. **Update the docs** to match what was built.
9. **Report plainly**: what was built, what wasn't, anything that surprised you, and what's next.

Let the user set the pace. Don't push to start coding every turn; discussing until it's clear is
the point.

## Working with the user

- **Recommend, don't survey.** Give options with a recommendation and the reason, not a neutral
  list.
- **Show, don't describe.** Concrete examples of the prompt, the file, the command or the output
  beat abstract explanations.
- **When the user pushes back, reconsider honestly.** If they're right, change course and say so
  briefly. If you disagree, say why once, then follow their decision.
- **Correct yourself plainly** when you notice an earlier statement was wrong and it matters.
- **Keep answers short and scannable**: tables for comparisons and cases, short paragraphs for
  reasoning.

## Spec document outline

Use this shape for a design doc, adapting headings to the topic:

```markdown
# Design: <topic>

**Status:** <agreed / built on date>, except steps marked *(not built yet)*
**Code:** <folders>

## Purpose
## Inputs            (flags, detected values, defaults)
## Behaviour         (step by step, from the person's side)
## Scenarios         (one table covering every combination)
## What gets created or changed
## Not covered yet
## Tests
```
