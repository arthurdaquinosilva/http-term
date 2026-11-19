# :http — notes for later

Snapshot from 2026-11-18 (v0.2.0 plus unreleased changes, classifier "Alpha"). This is a working list toward a "production grade" 1.0, most important first.

## State

- The youngest and smallest of the Python tools: 8 commits, about 2,200 lines in `src/`, about 370 lines of tests. **41 tests pass** locally (1 s). CI runs Ubuntu and macOS on Python 3.10–3.13 with pyflakes and pytest.
- No broad `except` handlers.
- **Docs are thin:** only `docs/releasing.md` and a screenshot. There's no features or configuration guide like the other tools have.
- `Dockerfile` only runs the tests (`pip install -e .[dev] && pytest`). It isn't a distribution image. Rename it or document what it's for.
- Uncommitted: `src/http_term/theme.py` (pitch palette tweak). Commit it and add it to CHANGELOG "Unreleased" (CHANGELOG also has two `## Unreleased` headings to merge).

## 1. Docs (biggest gap)

- [ ] `docs/features.md`: request syntax (curl-like flags), aliases, environments, the response view, history.
- [ ] `docs/configuration.md`: config file, per-project aliases and their file location, timeouts.
- [ ] README "Known limits" section, as in the other tools.

## 2. HTTP client correctness (what a production HTTP tool is judged on)

- [ ] **Secrets:** check whether `Authorization` headers, tokens and cookies end up in plain text in saved aliases or history. Redact them in the display and history, and support `$ENV` / `.env` variables for secrets so they're never written to project alias files that get committed.
- [ ] **Proxies and TLS:** `-k` (insecure) and timeouts exist. Check for and add proxy support (`HTTPS_PROXY` / `--proxy`), custom CA bundles (`--cacert`), client certificates and HTTP/2.
- [ ] Large and binary responses: stream them, cap what's shown, and allow saving to a file (`-o`).
- [ ] Redirects, retries, cookie jar persistence per project.
- [ ] Coverage of the curl flags that are accepted: test each flag in `request.py` and fail loudly on unsupported ones.
- [ ] Import and export: paste a curl command, and copy a request back out as curl.

## 3. Tests and code quality

- [ ] Grow the test suite: it's about 17% of the source size. Use an `httpx.MockTransport` or a local test server for end-to-end request and response tests.
- [ ] Replace pyflakes with ruff. Add a type checker and coverage with a threshold. Add `pythonpath = ["src"]` to the pytest config.
- [ ] Add Python 3.14 to CI.

## 4. Diagnosability

- [ ] Add `--debug` (log the raw request and response with secrets redacted), a crash report and `:http --doctor`.

## 5. Releases and distribution

- [ ] Use one source for the version. Tag-triggered release workflow. `install.sh` should default to the latest tag. Remove `twine` from dev extras.
- [ ] Move from "Alpha" to "Beta" once the docs and secrets handling are done.

## 6. Project hygiene

- [ ] Add CONTRIBUTING.md, SECURITY.md (important for a tool that handles credentials), templates and pre-commit hooks.

## Shared with the family

The pitch palette is copied into each repo, and the release, installer, logging and `--doctor` work is the same across all of them. Solve it once in :py and port it here.
