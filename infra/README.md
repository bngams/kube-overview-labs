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

### 3. Préparer les sessions (la veille)

`prepare-sessions.sh` crée le cluster `tp` de chaque session et y importe les images des TPs Kubernetes (`kube-vote` 1.0/2.0/3.0, redis, postgres, worker, result). Les sessions sont traitées **une par une**, car en créer plusieurs en même temps sature le VPS. Les images du TP01 ne sont **pas** préchargées : leur téléchargement fait partie du TP.

```bash
./prepare-sessions.sh              # sessions 1 à 6 (environ 1 min 30 par session)
./prepare-sessions.sh 2 5          # seulement certaines sessions
RESET=1 ./prepare-sessions.sh 3    # remise à zéro complète d'une session, puis préparation
```

Les stagiaires trouvent alors leur cluster prêt à l'étape 2B du TP00 (`k3d cluster list` affiche `tp`).

## Côté stagiaire

Voir [labs/00-environnement](../labs/00-environnement/README.md), section 2B.

- `kubectl port-forward … 8080:80` donne l'app sur `https://lab-kubeN-8080.DOMAIN`, derrière le mot de passe de la session (un login par sous-domaine).
- `/proxy/<port>/` fonctionne aussi, mais casse les apps qui utilisent des chemins absolus (la page `vote` charge `/static/...`) : préférez le sous-domaine.

## Réinitialiser une session

```bash
RESET=1 ./prepare-sessions.sh N    # supprime cluster, conteneurs et fichiers du binôme, puis prépare
```

## Arrêt / nettoyage

```bash
docker compose down        # arrête tout (garde homes, clusters et certificats)
docker compose down -v     # supprime aussi les volumes
```

## Validé sur le VPS (04/10/2026)

Les tests ont été faits sur un VPS 4 vCores / 15 Go (Debian, Docker 29.8), avec les sessions 1 à 3 démarrées.

| Vérification | Résultat |
|---|---|
| `cloudflare-dns.sh` | 24 enregistrements créés |
| Caddy, DNS-01 | certificat `*.deltavia.com` obtenu en ~10 s |
| `https://lab-kube1…3.deltavia.com` | page de connexion code-server (302 vers `/login`) |
| `k3d cluster create` × 3 en parallèle | `Ready` en moins de 10 s chacun |
| TP02 × 3 en parallèle (pull ghcr réel) | pods `Running` en ~25 s |
| `https://lab-kube1-8080.deltavia.com` après connexion | page `vote`, CSS et `/healthz` OK |
| Mémoire au repos (k3s + vote) | 1,0 à 1,4 Go par dind, 70 à 120 Mo par code-server |
| CPU au repos | ~15 % d'un cœur par session |

> ⚠️ **Création des clusters :** la charge est montée à 8,6 (sur 4 cœurs) pendant 3 créations simultanées. Pour 6 binômes, **préchauffez la veille** (section 3).
>
> ℹ️ Le conteneur Caddy s'appelle `infra-caddy-1` (`docker logs infra-caddy-1`).
>
> ⚠️ Ce VPS héberge aussi l'infra du cours gitops (`/var/www/gitops-lab`) : les deux utilisent les ports 80/443, **une seule à la fois**.
