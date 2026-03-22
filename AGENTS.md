# AGENTS.md

Use the `.llm/` directory as the source of truth for repo-local agent context in this repository.

## Where To Start

- Read `.llm/prompts/system-base.xml` for the root repo instructions.
- Read `.llm/context/` for project purpose, architecture, and behavioral contracts.
- Read `.llm/rules/` for tooling, style, and commit expectations.
- Read the latest `.llm/summaries/` entry for recent handoff context.

## When To Update `.llm`

Update `.llm` files when you change:

- conversion semantics or presets
- config storage or paths
- CLI entrypoints or user workflow
- verification/tooling expectations
- any repo-specific rule that future agents should inherit

Keep this file thin; do not duplicate the `.llm/` content here.
