# Gold Release

## Added
- GitHub Actions CI for Python compilation and smoke tests.
- `h!about` / `h!version` build information using Render commit metadata.
- `h!privacy` for temporary-memory and data-handling transparency.
- `h!diagnose` for staff production diagnostics.
- Gold release smoke test.

## Security
- Removed the local `.env` from the distributable package.
- `.gitignore` explicitly prevents accidental `.env` commits.

## Render
- Kept `main` + `autoDeployTrigger: commit` for automatic deployment.
- Documented the Render GitHub App repository-access requirement.
