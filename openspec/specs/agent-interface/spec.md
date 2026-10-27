# agent-interface Specification

## Purpose

Review one named file against the bundled checklist with a fresh-context reviewer and report through a file, not chat.

## Requirements

### Requirement: Review a named file
The skill SHALL review the file the user names against the bundled checklist using a fresh-context reviewer and SHALL write the findings to `agent-interface-report.md` instead of chat.

#### Scenario: File with a broken link
- **WHEN** the user asks to review a file that links to a missing file
- **THEN** the report file exists and marks the link item as failed
- **EVAL** evals/agent-interface/reviews-named-file

### Requirement: Stay out of unrelated requests
The skill SHALL NOT run for requests that do not ask for a file review.

#### Scenario: Arithmetic question
- **WHEN** the user asks an unrelated question
- **THEN** the agent answers directly and writes no report
- **EVAL** evals/agent-interface/ignores-unrelated-request
