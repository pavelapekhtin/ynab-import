# Python Style Rules

## Baseline

- Target Python 3.12 features and typing style.
- Match Ruff formatting defaults already configured in `pyproject.toml`.
- Keep imports explicit and module boundaries simple; this repo favors small utility functions over deep abstraction.

## Typing

- Preserve the repo’s “typed where practical” approach.
- Prefer concrete built-in generics like `list[str]`, `dict[str, str]`, and `Path`.
- Keep function return types explicit on public helpers and menu handlers.
- When pandas typing gets noisy, follow the existing local pattern rather than introducing a heavy wrapper abstraction just to satisfy types.

## Code Organization

- Keep CLI/prompt code in `src/ynab_import/cli/`.
- Keep transformation semantics in `src/ynab_import/core/`.
- Keep filesystem readers/writers in `src/ynab_import/file_rw/`.
- If a change affects both interactive flow and conversion semantics, keep orchestration in the CLI and reusable logic in core/file I/O modules.

## Implementation Preferences Seen In Repo

- Use straightforward functions instead of classes unless there is durable state to model.
- Use dataclasses for lightweight persisted structures like `Preset` and `Config`.
- Prefer `Path` over string path manipulation internally.
- Validate user-facing filesystem writes with explicit errors instead of failing silently.
- Preserve helpful CSV diagnostics; if a parser fallback is added, make the resulting error more actionable, not less.

## Error Handling and Logging

- Core pipeline functions log and re-raise rather than swallowing errors. Keep that behavior.
- CLI handlers catch exceptions to print user-facing messages and continue the interactive session.
- For malformed user inputs or files, prefer actionable messages over stack traces in the menu flow.

## Testing Style

- Add or update pytest coverage for any changed behavior.
- Treat tests as the executable contract for cleaning, conversion, config persistence, and CSV edge cases.
- When behavior changes intentionally, update tests in the same change so the new contract is explicit.

## Avoid

- Do not move business semantics into Rich/Questionary UI code.
- Do not silently broaden preset or config schemas without considering backward compatibility.
- Do not replace tolerant CSV parsing with a stricter implementation unless the product decision is explicit.
