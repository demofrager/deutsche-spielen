# Deutsche Spielen

Milestone 1 scaffold for a German-learning games webapp.

## Features in Milestone 1
- FastAPI app bootstrap
- Page routes:
  - `/`
  - `/games`
  - `/games/satzbauwuerfeln`
- Shared base template with menu navigation
- Basic styling and project structure for future milestones

## Run locally
1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start server:
   - `uvicorn app.main:app --reload`
4. Open browser:
   - `http://127.0.0.1:8000`

## Run tests
- `pytest -q`

## Production Deployment

The project includes Docker and Kubernetes manifests under `k8s/`.

### Build and push image
- `./run.sh build`
- `./run.sh push`

By default this uses image `registry.plsdontspam.me/deutsche_spielen:latest`.

### Apply manifests
- `./run.sh apply`

This applies:
- Namespace: `web`
- Deployment: `deutsche-spielen`
- Service: `deutsche-spielen` (ClusterIP on port 80 -> container 8000)
- Istio Gateway + VirtualService for host `deutsche-spielen.local`

### Rollout restart
- `./run.sh rollout`

### Full deploy flow
- `./run.sh all`

### Delete manifests
- `./run.sh delete`
