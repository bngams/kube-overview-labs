#!/usr/bin/env bash
# Prépare les sessions cloud AVANT la formation (la veille) :
#   1. crée le cluster k3d "tp" de chaque session (s'il n'existe pas) ;
#   2. pré-télécharge dans le Docker de la session les images du TP01 ;
#   3. importe dans le cluster les images des TPs Kubernetes (pas de téléchargement en classe).
# Les sessions sont traitées UNE PAR UNE : créer 6 clusters en même temps sature un VPS 4 vCores.
#
# Usage (sur le VPS, dans infra/) :
#   ./prepare-sessions.sh            # sessions 1 à 6
#   ./prepare-sessions.sh 2 5        # seulement les sessions 2 et 5
#   RESET=1 ./prepare-sessions.sh 3  # supprime le cluster et le travail de la session 3, puis la prépare
set -euo pipefail

SESSIONS=("${@:-1 2 3 4 5 6}")
SESSIONS=(${SESSIONS[*]})

# TP01 : images utilisées avec docker run / docker build (dans le Docker de la session)
DOCKER_IMAGES=(
  ghcr.io/bngams/kube-vote:1.0
  ghcr.io/bngams/kube-vote:2.0
  python:3.11-slim
)
# TP02 et suivants : images lancées dans le cluster (importées dans k3d)
CLUSTER_IMAGES=(
  ghcr.io/bngams/kube-vote:1.0
  ghcr.io/bngams/kube-vote:2.0
  ghcr.io/bngams/kube-vote:3.0
  redis:alpine
  postgres:15-alpine
  dockersamples/examplevotingapp_worker
  dockersamples/examplevotingapp_result
)

for n in "${SESSIONS[@]}"; do
  echo "=== session $n"
  if ! docker ps --format '{{.Names}}' | grep -qx "student-$n"; then
    echo "student-$n ne tourne pas : docker compose up -d dind-$n student-$n" >&2
    continue
  fi
  docker exec -i \
    -e RESET="${RESET:-0}" \
    -e DOCKER_IMAGES="${DOCKER_IMAGES[*]}" \
    -e CLUSTER_IMAGES="${CLUSTER_IMAGES[*]}" \
    "student-$n" bash -l <<'EOS'
set -euo pipefail
until docker info >/dev/null 2>&1; do sleep 2; done
if [ "$RESET" = "1" ]; then
  echo "reset : suppression du cluster, des conteneurs et du travail"
  k3d cluster delete tp >/dev/null 2>&1 || true
  docker ps -aq | xargs -r docker rm -f >/dev/null
  find ~ -mindepth 1 -maxdepth 1 ! -name '.*' -exec rm -rf {} +
fi
if k3d cluster list tp >/dev/null 2>&1; then
  echo "cluster tp : déjà présent"
else
  k3d cluster create tp --port "8000:80@loadbalancer" >/dev/null 2>&1 && echo "cluster tp : créé"
fi
kubectl wait --for=condition=Ready node --all --timeout=120s >/dev/null && echo "nœud Ready"
for img in $DOCKER_IMAGES $CLUSTER_IMAGES; do docker pull -q "$img" >/dev/null; done
echo "images téléchargées dans le Docker de la session"
k3d image import $CLUSTER_IMAGES -c tp >/dev/null 2>&1 && echo "images importées dans le cluster"
# les images seulement utiles au cluster n'encombrent pas le docker images du TP01
for img in $CLUSTER_IMAGES; do
  case " $DOCKER_IMAGES " in *" $img "*) ;; *) docker rmi -f "$img" >/dev/null 2>&1 || true ;; esac
done
docker images --format '{{.Repository}}:{{.Tag}}' | sort | tr '\n' ' '; echo
EOS
done
