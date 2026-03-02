# Repository Guidelines

## Project Structure & Module Organization
- `apps/` houses deployable services (mostly Go), each with its own `Makefile`, `Dockerfile`, `cmd/`, and `pkg/`.
- `apps/pylib/` contains shared Python helpers used by some apps and automation.
- `pulumi/` contains infrastructure-as-code and environment configuration (Pulumi stacks, Python code, and scripts).
- `README.md` documents the high-level setup and deployment flow.

## Build, Test, and Development Commands
- `cd apps && make info` shows per-app image/registry/version metadata.
- `cd apps && make fmt` formats all apps (delegates to each app’s Makefile).
- `cd apps && make lint` runs `golangci-lint` for every Go app.
- `cd apps && make test` runs `go test -race -cover ./...` per app.
- `cd apps && make build` builds app images (runs tests first).
- `cd apps && make push` builds and pushes images to `registry.localdomain:32000` by default.
- `cd pulumi && make lint` runs `ruff` and `mypy` for infra code.
- `pulumi up` deploys the stack after editing `pulumi/Pulumi.prod.yaml` and `pulumi/subst_address.json`.

## Coding Style & Naming Conventions
- Go: standard `gofmt` formatting; package layout follows `cmd/<service>` and `pkg/<module>`.
- Tests: name files `*_test.go` and keep them alongside source packages.
- Docker images: tag as `${REGISTRY}/${PROJECT}:${VERSION}` (default version is a timestamp).
- Python (Pulumi): `ruff` for lint/format and `mypy` for typing.

## Testing Guidelines
- Primary test runner is `go test -race -cover ./...` (via `make test` in `apps/`).
- Prefer unit tests near the code under test; keep package names aligned.
- Run app tests before building/pushing images to catch regressions early.

## Commit & Pull Request Guidelines
- Commits are short, imperative summaries (e.g., “bump go”, “remove dead code”), sometimes with PR numbers.
- Keep commits focused by area (app vs infra).
- PRs should describe the change, note any config impacts (e.g., Pulumi stack files), and include validation notes (commands run).

## Configuration & Deployment Tips
- Ensure `registry.localdomain` resolves to your local registry as noted in `README.md`.
- Update `apps/switches/switches.json` when changing switch definitions.
