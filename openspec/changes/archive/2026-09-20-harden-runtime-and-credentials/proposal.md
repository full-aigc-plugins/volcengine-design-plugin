## Why

The ASR client accepts ambiguous audio inputs, fails to terminate promptly for failed or cancelled tasks, and silently ignores malformed or weakly protected credential files. These behaviors make failures slow, unsafe, and difficult to diagnose.

## What Changes

- Require exactly one of `--url` or `--file` for ASR submission.
- Treat provider failure and cancellation states as terminal and report provider errors.
- Validate credential-file ownership and permissions and preserve actionable parse errors.
- Add an OpenAI/Codex interface manifest and automated tests/CI.

## Capabilities

### New Capabilities

- `reliable-asr-client`: Defines deterministic submission and terminal-state behavior.
- `secure-local-credentials`: Defines local credential-file safety and diagnostics.

### Modified Capabilities

None.

## Impact

Affected files include Volcengine Python clients, credential loading, Codex manifest metadata, tests, CI, and release metadata.
