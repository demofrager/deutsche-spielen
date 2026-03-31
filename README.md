# Deutsche Spielen

German-learning web app built with FastAPI and Jinja templates.

Current playable game:
- Satzbauwuerfeln

## Key Routes
- `/` home page
- `/games` game list
- `/games/satzbauwuerfeln` game UI
- `/api/games/satzbauwuerfeln/roll` roll endpoint
- `/api/games/satzbauwuerfeln/validate` validation endpoint

## Local Development (single distrobox workflow)

This project is set up to run inside one distrobox named `deutsche-spielen-toolbox`.

1. Bootstrap toolbox and dependencies:
   - `./run.sh setup`
2. Run app locally (starts LanguageTool in the same toolbox by default):
   - `./run.sh run_local`
3. Open app:
   - `http://127.0.0.1:8001`

### Optional LanguageTool behavior
- Grammar checks are enabled only when `LANGUAGETOOL_URL` is set.
- Local `run_local` exports `LANGUAGETOOL_URL=http://127.0.0.1:8081` after starting LanguageTool.
- If LanguageTool is unavailable, validation gracefully falls back to non-grammar checks.
- Validation also skips LanguageTool calls when blocking checks already failed (performance optimization).

### Run tests
- `./run.sh test_local`

## Dependencies

- Runtime dependencies: `requirements.txt`
- Development/test dependencies: `requirements-dev.txt`

## Kubernetes Deployment

Kubernetes manifests are in `k8s/`.

Apply all resources:
- `./run.sh apply`

Delete all resources:
- `./run.sh delete`

Restart app rollout:
- `./run.sh rollout`

Full deploy flow:
- `./run.sh all`

### Deployment architecture
- `k8s/deployment.yaml`: Deutsche Spielen app deployment
- `k8s/languagetool-deployment.yaml`: separate LanguageTool deployment + service
- App connects to LanguageTool via:
  - `LANGUAGETOOL_URL=http://languagetool.deutsche-spielen.svc.cluster.local:8010`
