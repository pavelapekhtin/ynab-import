# Commit Rules

Use Conventional Commits as the default convention in this repo.

## Subject Line

Format:

`type(scope): short summary`

Scope is optional but encouraged when it adds clarity, for example:

- `feat(cli): add input folder prefill`
- `fix(core): preserve outflow split for signed amount column`
- `test(readers): cover malformed semicolon CSV`

Common types in this repo:

- `feat`
- `fix`
- `refactor`
- `test`
- `docs`
- `chore`
- `build`
- `ci`

## Commit Body

Prefer a meaningful body for any non-trivial change. Capture:

- why the change was needed
- user-visible behavior impact
- important files or layers touched
- assumptions, caveats, or follow-up work

## Repo-Specific Expectations

- If preset/config schema or storage paths change, say so explicitly.
- If conversion semantics change, document the behavioral difference in plain language.
- If a CLI/menu change affects user flow, mention how the interaction changed.
- If verification had gaps because of sandbox/tooling limits, note that in the body or PR description.

## Notes On Current History

- The repo contains some older inconsistent commit messages.
- `pyproject.toml` already configures Commitizen with conventional commits; follow that current intent rather than copying historical inconsistency.
