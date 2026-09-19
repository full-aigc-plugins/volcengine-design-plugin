## Context

The plugin contains deterministic Python clients but no CI. Existing error handling handles HTTP failures while leaving argument and lifecycle failures ambiguous.

## Goals / Non-Goals

**Goals:** deterministic ASR inputs, complete terminal-state handling, secure local credentials, host-manifest completeness, and offline regression coverage.

**Non-Goals:** invoke paid Volcengine endpoints in CI.

## Decisions

- Use argparse's required mutually-exclusive group for submit-only audio source arguments.
- Normalize provider statuses and maintain explicit success and failure terminal sets.
- Enforce owner-only permissions on POSIX; Windows will skip mode-bit enforcement.
- Raise precise configuration errors rather than swallowing exceptions.

## Risks / Trade-offs

Existing credential files with permissive modes will stop working until users run `chmod 600`, which is intentional fail-closed behavior.

## Migration Plan

Add failing unit tests, implement minimal corrections, validate offline, bump versions, and publish a tagged release.
