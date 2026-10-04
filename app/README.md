# L'application fil rouge : la voting app

Le cours utilise l'[example-voting-app](https://github.com/dockersamples/example-voting-app) de Docker (licence Apache 2.0) : 5 composants hétérogènes, visuels et parlants pour un public non technique.

| Composant | Techno | Image utilisée |
|---|---|---|
| `vote` | Python / Flask | **`ghcr.io/bngams/kube-vote:{1.0,2.0,3.0}`**, notre fork (voir ci-dessous) |
| `redis` | Redis | `redis:alpine` |
| `worker` | .NET | `dockersamples/examplevotingapp_worker` |
| `db` | PostgreSQL | `postgres:15-alpine` |
| `result` | Node.js | `dockersamples/examplevotingapp_result` |

## Pourquoi un fork de `vote` ?

Les tags officiels `before`, `after` et `latest` de `examplevotingapp_vote` pointent vers **la même image** (même digest, vérifié le 04/10/2026) : impossible de montrer une mise à jour visible. Notre fork **[bngams/example-voting-app](https://github.com/bngams/example-voting-app)** (dossier `vote/`, seul service modifié) ajoute :

| Ajout | Sert au |
|---|---|
| `APP_VERSION` (build arg) affiché dans un badge en haut à droite | TP6 (rolling update visible) |
| design **v2** (dégradé violet, boutons arrondis) | TP6 |
| **v3 cassée** : exige `VOTE_TITLE` sans valeur par défaut => `KeyError` au démarrage, `CrashLoopBackOff` | TP6 (diagnostic + rollback) et TP5 (la corriger par ConfigMap) |
| « Servi par : *nom du pod* » | TP2 et TP3 (on voit quel pod répond) |
| `/healthz` | TP6 (probes) |
| `/crash` (arrête le PID 1) | TP2 (conteneur redémarré vs pod recréé) |
| interface en français, plus de jQuery en `http://` (contenu mixte bloqué en HTTPS) | tous |

## Construire en local

```bash
git clone https://github.com/bngams/example-voting-app && cd example-voting-app/vote
for v in 1.0 2.0 3.0; do docker build --build-arg APP_VERSION=$v -t ghcr.io/bngams/kube-vote:$v . ; done
docker run --rm -p 8080:80 ghcr.io/bngams/kube-vote:2.0             # http://localhost:8080
docker run --rm ghcr.io/bngams/kube-vote:3.0                        # plante : KeyError: 'VOTE_TITLE'
docker run --rm -p 8080:80 -e VOTE_TITLE="Quel animal ?" ghcr.io/bngams/kube-vote:3.0   # OK
```

## Publication

Un push sur `main` qui touche `vote/**` déclenche le workflow `.github/workflows/vote-images.yml` du fork. Il publie `ghcr.io/bngams/kube-vote:{1.0,2.0,3.0}` en amd64 et arm64. Le paquet est **public** (pull anonyme vérifié le 04/10/2026). Les workflows d'origine, qui publiaient sur le Docker Hub de dockersamples, ont été retirés du fork.
