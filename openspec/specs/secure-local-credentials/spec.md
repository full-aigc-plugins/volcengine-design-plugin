# secure-local-credentials Specification

## Purpose
TBD - created by archiving change harden-runtime-and-credentials. Update Purpose after archive.
## Requirements
### Requirement: Credential files are private

On POSIX systems, a credential file SHALL be owned by the current user and SHALL NOT grant group or other permissions.

#### Scenario: Credential file permissions are too broad

- **WHEN** the file mode contains any group or other permission
- **THEN** credential loading SHALL fail with the affected path and required mode

### Requirement: Configuration errors remain observable

Malformed JSON and I/O failures SHALL produce actionable errors instead of being treated as missing credentials.

#### Scenario: Configuration JSON is malformed

- **WHEN** credential loading cannot parse the file
- **THEN** the command SHALL report the file path and parsing reason

