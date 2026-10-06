#!/usr/bin/env bash
# Prépare les sessions cloud AVANT la formation (la veille) :
#   1. crée le cluster k3d "tp" de chaque session (s'il n'existe pas) ;
#   2. importe dans le cluster les images des TPs Kubernetes (pas de téléchargement en classe).
# Les images du TP01 ne sont PAS pré-téléchargées dans le Docker de la session : le
# téléchargement (et ses couches "Already exists") fait partie de ce TP.
# Les sessions sont traitées UNE PAR UNE : créer 6 clusters en même temps sature un VPS 4 vCores.
#
# Usage (sur le VPS, dans infra/) :
#   ./prepare-sessions.sh            # sessions 1 à 6
#   ./prepare-sessions.sh 2 5        # seulement les sessions 2 et 5
#   RESET=1 ./prepare-sessions.sh 3  # supprime le cluster et le travail de la session 3, puis la prépare
set -euo pipefail

SESSIONS=("${@:-1 2 3 4 5 6}")
SESSIONS=(${SESSIONS[*]})

# TP02 et suivants : images lancées dans le cluster (importées dans k3d)
CLUSTER_IMAGES=(
  ghcr.io/bngams/kube-vote:1.0
  ghcr.io/bngams/kube-vote:2.0
  ghcr.io/bngams/kube-vote:3.0
  ghcr.io/bngams/kube-redis:8-alpine
  ghcr.io/bngams/kube-postgres:15-alpine
  ghcr.io/bngams/kube-worker:1.0
  ghcr.io/bngams/kube-result:1.0
  ghcr.io/bngams/kube-result:1.1
  ghcr.io/bngams/kube-busybox:1.37
)
# Toutes les images viennent de ghcr.io : Docker Hub s'est révélé très lent (cf. app/README.md).

for n in "${SESSIONS[@]}"; do
  echo "=== session $n"
  if ! docker ps --format '{{.Names}}' | grep -qx "student-$n"; then
    echo "student-$n ne tourne pas : docker compose up -d dind-$n student-$n" >&2
    continue
  fi
  docker exec -i \
    -e RESET="${RESET:-0}" \
    -e CLUSTER_IMAGES="${CLUSTER_IMAGES[*]}" \
    "student-$n" bash -l <<'EOS'
set -euo pipefail
until docker info >/dev/null 2>&1; do sleep 2; done
if [ "$RESET" = "1" ]; then
  echo "reset : suppression du cluster, des conteneurs et du travail"
  k3d cluster delete tp >/dev/null 2>&1 || true
  docker ps -aq | xargs -r docker rm -f >/dev/null
  # images des TPs (kube-vote, vote-perso, python…) : on ne garde que celles de k3d
  docker images --format '{{.Repository}}:{{.Tag}}' | grep -vE '^(rancher/k3s|ghcr.io/k3d-io/)' | xargs -r docker rmi -f >/dev/null 2>&1 || true
  docker builder prune -af >/dev/null 2>&1 || true
  find ~ -mindepth 1 -maxdepth 1 ! -name '.*' -exec rm -rf {} +
fi
if k3d cluster list tp >/dev/null 2>&1; then
  echo "cluster tp : déjà présent"
else
  k3d cluster create tp --port "8000:80@loadbalancer" >/dev/null 2>&1 && echo "cluster tp : créé"
fi
kubectl wait --for=condition=Ready node --all --timeout=120s >/dev/null && echo "nœud Ready"
for img in $CLUSTER_IMAGES; do docker pull -q "$img" >/dev/null; done
# k3d image import peut annoncer un succès sans rien importer : on vérifie, et on réessaie
missing() {
  local present; present=$(docker exec k3d-tp-server-0 crictl images | awk 'NR>1 {print $1":"$2}')
  for img in $CLUSTER_IMAGES; do
    case "$img" in *:*) ref="$img" ;; *) ref="$img:latest" ;; esac
    echo "$present" | grep -qE "(^|/)${ref}$" || echo "$img"
  done
}
for attempt in 1 2 3; do
  todo=$(missing)
  [ -z "$todo" ] && break
  k3d image import $todo -c tp >/dev/null 2>&1 || true
done
todo=$(missing)
if [ -n "$todo" ]; then echo "ÉCHEC import : $todo" >&2; exit 1; fi
echo "images importées dans le cluster (vérifiées)"
# on les retire du Docker de la session : le TP01 doit les télécharger lui-même
docker rmi -f $CLUSTER_IMAGES >/dev/null 2>&1 || true
docker image prune -f >/dev/null
echo "docker images : $(docker images --format '{{.Repository}}:{{.Tag}}' | sort | tr '\n' ' ')"
echo "dans le cluster : $(docker exec k3d-tp-server-0 crictl images -q | wc -l) images" 
EOS
done
