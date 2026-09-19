# reliable-asr-client Specification

## Purpose
Define deterministic ASR submission, polling, terminal-state, timeout, and recovery behavior for the Volcengine client.
## Requirements
### Requirement: Audio source is unambiguous

ASR submission SHALL require exactly one source: a public URL or a local file.

#### Scenario: No source or two sources are supplied

- **WHEN** the user invokes `submit` without exactly one source
- **THEN** argument parsing SHALL fail before reading files or calling the provider

### Requirement: All provider terminal states end polling

Completed, failed, rejected, and cancelled tasks SHALL stop polling immediately.

#### Scenario: Provider reports failure

- **WHEN** a query response contains a failure terminal state
- **THEN** the command SHALL report provider error details and return non-zero
