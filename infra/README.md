# infra — environnement « cloud » du cours Kubernetes (VPS)

Ce dossier contient le provisioning **côté formateur** : un VPS qui fournit à **6 binômes** une session prête à l'emploi (VS Code dans le navigateur), dans laquelle chaque binôme crée **son propre cluster Kubernetes** avec k3d.

> ⚠️ Ce dossier n'est **pas** un TP. Les secrets (`.env`) sont gitignorés.
> Adapté de `2606-gitops/infra-formateur` : même architecture (Cloudflare, Caddy, code-server, DinD), avec les outils Kubernetes à la place de Terraform et Ansible.

## Architecture

```
                 Internet
                    │
           ┌────────▼─────────┐
           │   Cloudflare     │  proxy + TLS edge (Universal SSL : *.DOMAIN, 1 seul niveau)
           └────────┬─────────┘
              ┌─────▼──────┐
              │   Caddy    │  routage par sous-domaine + cert wildcard (DNS-01 Cloudflare)
              └──┬──────┬──┘
   lab-kube1 ────┘      └──── lab-kube6        lab-kubeN-<port> => app du binôme N
        ┌──────────────────────────────────┐  (× 6)
        │ student-N : code-server          │  kubectl, k3d, k9s, docker CLI
        │      │ (même réseau, localhost)  │
        │ dind-N : Docker isolé            │
        │   └── k3d : cluster "tp"         │  k3s dans des conteneurs du DinD
        └──────────────────────────────────┘
```

| Choix | Raison |
|---|---|
| **1 cluster k3d par binôme** | chaque binôme « possède » son cluster, comme en mode local (minikube). Les commandes des TPs sont identiques, et une fausse manip ne gêne personne |
| **k3d dans le DinD du binôme** | le cluster vit dans un Docker isolé, jamais le socket de l'hôte (= root sur le VPS) |
| **code-server** | un vrai VS Code léger, avec terminal et éditeur YAML. Son proxy `--proxy-domain` sert les `kubectl port-forward` à la racine de `lab-kubeN-<port>.DOMAIN` |
| **`lab-kubeN` (1 niveau)** | `*.kube-labN.DOMAIN` (2 niveaux) n'est pas couvert par l'Universal SSL gratuit de Cloudflare |
| **Le binôme crée son cluster (TP00)** | symétrie avec le mode local (`minikube start` / `k3d cluster create`), et un cluster cassé se recrée en 30 s |

## Budget mesuré (VPS 4 vCores / 16 Go)

Les mesures ont été faites sur une session avec k3s et le Deployment `vote` du TP2 :

| Conteneur | Mémoire | CPU au repos |
|---|---|---|
| `dind-N` (Docker + k3s + vote) | ~1,0 Go | ~12 % d'un cœur |
| `student-N` (code-server, sans navigateur connecté) | ~140 Mo | ~0 % |

Avec la voting app complète (Postgres, Redis, worker, result) et code-server en usage, on peut compter **environ 2 Go par session**, soit **environ 12 Go pour 6 sessions** et moins d'un cœur au repos. Les `mem_limit` (2,5 Go pour dind, 768 Mo pour student) sont des garde-fous. Côté disque, chaque DinD garde ses images (environ 1 à 2 Go par session).

> 🧪 **À faire avant le jour J :** un test de charge avec les 6 sessions et la voting app complète déployée partout (`docker stats`).

## Mise en route

### 1. Cloudflare (DNS)

Les hôtes du cours gitops sont des enregistrements **explicites** (`lab1`, `lab10`… vers un autre VPS). On fait de même ici : 6 sessions × (1 hôte + 3 ports) = **24 enregistrements A proxifiés** vers l'IP du VPS. Le script `cloudflare-dns.sh` les crée, ou les met à jour s'ils existent déjà. Il utilise le même token que Caddy.

```bash
cp .env.example .env                       # DOMAIN + CLOUDFLARE_API_TOKEN au minimum
DRY_RUN=1 ./cloudflare-dns.sh <IP_VPS>     # aperçu, aucun appel à Cloudflare
./cloudflare-dns.sh <IP_VPS>               # création / mise à jour
./cloudflare-dns.sh --delete               # fin de formation : suppression
```

| Enregistrement | Sert à |
|---|---|
| `lab-kube1` … `lab-kube6` | VS Code (code-server) de chaque session |
| `lab-kubeN-8080` | `vote` (TP02 et suivants) |
| `lab-kubeN-8081` | `result` (TP04) |
| `lab-kubeN-8000` | l'Ingress (TP04) |

Variables optionnelles : `SESSIONS=3` (moins de sessions), `PORTS="8080 8081"`, `CF_ZONE_ID=…` (si le token ne peut pas lister les zones). Pour SSL/TLS, choisissez **Full (strict)**. La Page Rule `lab*.DOMAIN/*` existante couvre ces hôtes.

Le token API doit avoir le scope **Zone : DNS : Edit** sur la zone. Il sert aussi au challenge DNS-01 de Caddy.

### 2. Configuration et démarrage

```bash
cp .env.example .env      # DOMAIN, CLOUDFLARE_API_TOKEN, S1..S6_PASSWORD
docker compose up -d
docker compose ps
```

Les sessions sont accessibles à `https://lab-kube1.DOMAIN` … `lab-kube6.DOMAIN`.

### 3. Préchauffer les images (recommandé)

Pour éviter 6 téléchargements simultanés le jour J, vous pouvez créer les clusters et pré-télécharger les images dans chaque session :

```bash
for n in 1 2 3 4 5 6; do
  docker exec student-$n bash -lc 'k3d cluster create tp --port "8000:80@loadbalancer" && docker pull ghcr.io/bngams/kube-vote:1.0 && k3d image import ghcr.io/bngams/kube-vote:1.0 -c tp'
done
```

Les stagiaires sauteront alors l'étape 2 du TP00 (`k3d cluster create` répondra que le cluster existe déjà).

## Côté stagiaire

Voir [labs/00-environnement](../labs/00-environnement/README.md), section 2B.

- `kubectl port-forward … 8080:80` donne l'app sur `https://lab-kubeN-8080.DOMAIN`, derrière le mot de passe de la session (un login par sous-domaine).
- `/proxy/<port>/` fonctionne aussi, mais casse les apps qui utilisent des chemins absolus (la page `vote` charge `/static/...`) : préférez le sous-domaine.

## Réinitialiser une session

```bash
docker exec student-N bash -lc 'k3d cluster delete tp && k3d cluster create tp --port "8000:80@loadbalancer"'
```

## Arrêt / nettoyage

```bash
docker compose down        # arrête tout (garde homes, clusters et certificats)
docker compose down -v     # supprime aussi les volumes
```

## Validé en local

Le scénario complet d'une session (sans Caddy ni Cloudflare) a été testé sur Docker Desktop : `docker compose --env-file .env.example up -d dind-1 student-1`, `k3d cluster create` dans la session, TP2 complet, accès à l'app via le proxy code-server (`Host: lab-kube1-8080…`). Le routage Caddy/Cloudflare, lui, est repris tel quel du cours gitops et reste à valider sur le VPS.
