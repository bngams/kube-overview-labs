#!/usr/bin/env bash
# Crée (ou met à jour) les enregistrements DNS Cloudflare des sessions du cours Kubernetes :
#   lab-kube1 … lab-kubeN                 -> code-server de chaque session
#   lab-kubeN-<port> pour chaque port     -> apps des binômes (proxy code-server)
# Tous en A, proxifiés (orange), vers l'IP du VPS. Idempotent : relançable sans risque.
#
# Usage :
#   ./cloudflare-dns.sh <IP_VPS>                 # crée / met à jour
#   DRY_RUN=1 ./cloudflare-dns.sh <IP_VPS>       # affiche seulement ce qui serait fait
#   ./cloudflare-dns.sh --delete                 # supprime les enregistrements (fin de formation)
#   SESSIONS=7 EXTRA_HOSTS="lab-kube-vote lab-kube-result" ./cloudflare-dns.sh <IP>   # + session formateur et démo publique
#
# Lit DOMAIN et CLOUDFLARE_API_TOKEN dans .env (token : Zone > DNS > Edit sur la zone).
# Si le token ne peut pas lister les zones, fournir CF_ZONE_ID (Cloudflare > zone > Overview > API).
set -euo pipefail

cd "$(dirname "$0")"
[ -f .env ] && set -a && . ./.env && set +a

SESSIONS="${SESSIONS:-6}"
PORTS="${PORTS:-8080 8081 8000}"   # vote, result, Ingress (TP04)
API="https://api.cloudflare.com/client/v4"

MODE="upsert"
IP=""
case "${1:-}" in
  --delete) MODE="delete" ;;
  "") echo "Usage : $0 <IP_VPS> | --delete" >&2; exit 1 ;;
  *) IP="$1" ;;
esac

: "${DOMAIN:?DOMAIN manquant (.env)}"

names=()
for h in ${EXTRA_HOSTS:-}; do names+=("$h.$DOMAIN"); done   # ex : EXTRA_HOSTS="lab-kube-vote lab-kube-result"
for n in $(seq 1 "$SESSIONS"); do
  names+=("lab-kube$n.$DOMAIN")
  for p in $PORTS; do names+=("lab-kube$n-$p.$DOMAIN"); done
done

if [ "${DRY_RUN:-0}" = "1" ]; then
  for name in "${names[@]}"; do
    if [ "$MODE" = "delete" ]; then echo "[dry-run] supprimer $name"; else echo "[dry-run] $name A $IP (proxied)"; fi
  done
  echo "[dry-run] ${#names[@]} enregistrements"
  exit 0
fi

: "${CLOUDFLARE_API_TOKEN:?CLOUDFLARE_API_TOKEN manquant (.env)}"
command -v jq >/dev/null || { echo "jq requis" >&2; exit 1; }

cf() { # cf METHOD PATH [JSON]
  curl -fsS -X "$1" "$API$2" \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" ${3:+--data "$3"}
}

ZONE_ID="${CF_ZONE_ID:-$(cf GET "/zones?name=$DOMAIN" | jq -r '.result[0].id // empty')}"
[ -n "$ZONE_ID" ] || { echo "Zone $DOMAIN introuvable : définir CF_ZONE_ID" >&2; exit 1; }

for name in "${names[@]}"; do
  id=$(cf GET "/zones/$ZONE_ID/dns_records?type=A&name=$name" | jq -r '.result[0].id // empty')
  if [ "$MODE" = "delete" ]; then
    if [ -n "$id" ]; then cf DELETE "/zones/$ZONE_ID/dns_records/$id" >/dev/null && echo "supprimé  $name"; else echo "absent    $name"; fi
    continue
  fi
  body=$(jq -nc --arg n "$name" --arg ip "$IP" '{type:"A",name:$n,content:$ip,proxied:true,ttl:1}')
  if [ -n "$id" ]; then
    cf PUT "/zones/$ZONE_ID/dns_records/$id" "$body" >/dev/null && echo "mis à jour $name -> $IP"
  else
    cf POST "/zones/$ZONE_ID/dns_records" "$body" >/dev/null && echo "créé      $name -> $IP"
  fi
done
