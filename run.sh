#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="$(basename "$SCRIPT_DIR")"
IMAGE="registry.plsdontspam.me/$APP_NAME"
TAG="latest"
NAMESPACE="deutsche-spielen"
DEPLOYMENT_NAME="deutsche-spielen"
BOX_NAME="deutsche-spielen-toolbox"

setup() {
  bash "$SCRIPT_DIR/scripts/bootstrap_toolbox.sh" "$BOX_NAME"
}

run_local() {
  bash "$SCRIPT_DIR/scripts/run_local_toolbox.sh" "$BOX_NAME"
}

test_local() {
  bash "$SCRIPT_DIR/scripts/test_local_toolbox.sh" "$BOX_NAME"
}

build() {
  docker build -t "$IMAGE:$TAG" "$SCRIPT_DIR"
}

push() {
  docker push "$IMAGE:$TAG"
}

rollout() {
  kubectl -n "$NAMESPACE" rollout restart deploy/"$DEPLOYMENT_NAME"
}

apply_k8s() {
  kubectl apply -f "$SCRIPT_DIR/k8s/namespace.yaml"
  kubectl apply -f "$SCRIPT_DIR/k8s/languagetool-deployment.yaml"
  kubectl apply -f "$SCRIPT_DIR/k8s/deployment.yaml"
  kubectl apply -f "$SCRIPT_DIR/k8s/service.yaml"
  kubectl apply -f "$SCRIPT_DIR/k8s/istio-gateway.yaml"
  kubectl apply -f "$SCRIPT_DIR/k8s/istio-virtual-service.yaml"
}

delete_k8s() {
  kubectl delete -f "$SCRIPT_DIR/k8s/istio-virtual-service.yaml" --ignore-not-found
  kubectl delete -f "$SCRIPT_DIR/k8s/istio-gateway.yaml" --ignore-not-found
  kubectl delete -f "$SCRIPT_DIR/k8s/service.yaml" --ignore-not-found
  kubectl delete -f "$SCRIPT_DIR/k8s/deployment.yaml" --ignore-not-found
  kubectl delete -f "$SCRIPT_DIR/k8s/languagetool-deployment.yaml" --ignore-not-found
  kubectl delete -f "$SCRIPT_DIR/k8s/namespace.yaml" --ignore-not-found
}

all() {
  build
  push
  apply_k8s
  rollout
}

usage() {
  cat <<'USAGE'
Usage: ./run.sh <command>

Commands:
  setup       Create the deutsche-spielen toolbox and install all dependencies
  run_local   Start the FastAPI dev server inside the distrobox
  test_local  Run Python tests inside the distrobox
  build       Build production Docker image
  push        Push production Docker image
  apply       Apply Kubernetes manifests
  delete      Delete Kubernetes manifests
  rollout     Restart Kubernetes deployment
  all         Build, push, apply, and rollout
USAGE
}

cmd="${1:-}"
case "$cmd" in
  setup)
    setup
    ;;
  run_local)
    run_local
    ;;
  test_local)
    test_local
    ;;
  build)
    build
    ;;
  push)
    push
    ;;
  apply)
    apply_k8s
    ;;
  delete)
    delete_k8s
    ;;
  rollout)
    rollout
    ;;
  all)
    all
    ;;
  -h|--help|help|"")
    usage
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    usage
    exit 1
    ;;
esac
