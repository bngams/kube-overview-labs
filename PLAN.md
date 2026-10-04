# Kubernetes pour tous — plan de travail

> Public mixte : techs + non-techs (chefs de projet, PO…). **2 jours.**
> Objectif : **comprendre ce que fait Kubernetes, pourquoi on l'utilise, et ce qu'on voit dans un vrai projet**, pas administrer un cluster.
> Format repris du cours low-code/no-code qui a plu : quelques slides commentées (Excalidraw) + TPs très guidés sur un environnement **prêt à l'emploi** + ressources.

## Fil rouge

**Kubernetes compare en permanence ce qu'on lui demande (l'état souhaité) avec ce qui tourne réellement, et corrige l'écart.**

Une seule application tout au long du cours, la **voting app** (vote, redis, worker, db, result).
On la conteneurise, on la déploie, on la casse, on la répare, on la met à jour et on revient en arrière.

## Jour 1 — Des conteneurs à Kubernetes

| Horaire | Module | Pratique |
|---|---|---|
| 9h00 (30 min) | **0. Tour de table** : ce que vous savez déjà de Kube (« ça tourne sur Kube », « un pod redémarre »…) | Sondage |
| 9h30 (45 min) | **1. Pourquoi les conteneurs ?** : « ça marche sur ma machine », dépendances, reproductibilité | Démo formateur |
| 10h15 (1h15) | **2. Image, conteneur, runtime** : Dockerfile = recette, image = plat surgelé, conteneur = plat servi. Docker → containerd → runc, en restant léger | **TP1** : lancer, lister, arrêter un conteneur, lire un Dockerfile, construire et lancer l'image `vote` |
| 13h30 (30 min) | **3. Un conteneur ne fait pas une plateforme** : qui redémarre l'API ? et si le serveur tombe ? et pour passer à 5 instances ? | Schéma Excalidraw construit en direct |
| 14h00 (1h30) | **4. L'état souhaité** : boucle de réconciliation, métaphore de la ville, architecture (control plane / nodes) en 1 schéma | **TP2** : premier Deployment, on supprime un pod… il revient |
| 15h45 (1h) | **5a. Deployment → ReplicaSet → Pod** | **TP3** : scaler à 5, puis à 0, observer sur le visualiseur |
| 16h45 (15 min) | Récap du jour | Quiz express |

## Jour 2 — Kubernetes dans la vraie vie

| Horaire | Module | Pratique |
|---|---|---|
| 9h00 (15 min) | Rappel J1 | « Explique à ton voisin » |
| 9h15 (1h15) | **5b. Service et Ingress** : adresse stable, répartition de charge, porte d'entrée | **TP4** : exposer la voting app (5 composants), l'ouvrir dans son navigateur via son URL perso |
| 10h30 (45 min) | **5c. ConfigMap, Secret, Namespace** | **TP5** : changer le message d'accueil sans reconstruire l'image |
| 11h15 (1h15) | **6. Vivre avec Kube** : rolling update, rollback, probes, lire un incident (`CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled`, `Pending`) | **TP6** : déployer v2, déployer une v3 cassée, diagnostiquer, rollback |
| 13h30 (1h) | **7. Kubernetes dans votre projet** *(module « chef de projet »)* : qui fait quoi (dev / ops / plateforme), managé (EKS, GKE, AKS, OpenShift), coûts et FinOps, vocabulaire qu'on entend (Helm, GitOps/ArgoCD, CI/CD), quand **ne pas** utiliser Kube | Étude de cas en binôme : « Faut-il du Kube pour ce projet ? » |
| 14h45 (1h15) | **8. Mission finale** : déployer la voting app complète, puis **chasse aux pannes** : le formateur casse des choses dans chaque namespace, les binômes diagnostiquent | **TP7** |
| 16h15 (45 min) | **Synthèse** : ressources, fiche glossaire, évaluation | Quiz final |

## Deux niveaux dans chaque TP

- 🟢 **Mission** (tout le monde) : commandes à copier-coller, puis « qu'est-ce que vous observez ? ».
- 🔵 **Pour aller plus loin** (les techs) : écrire et modifier le YAML soi-même, utiliser `kubectl describe` ou les logs, ajouter des probes et des limites.
- Binômes mixtes tech + non-tech : le tech tape les commandes, le chef de projet lit la consigne et explique ce qu'on observe, puis on échange les rôles.

Structure d'un TP (même code emoji que les TPs n8n et NocoDB) :
🎯 Objectif · 🛠️ Prérequis · 🧱 Étape N · 👀 Aperçu (capture) · 🧠 « Ce qui vient de se passer » · ✅ Résultat attendu · 🔵 Bonus

## Environnement : deux modes, mêmes commandes

Décidé le 04/10/2026. Le **TP00** est le seul qui diffère : ensuite, toutes les commandes sont identiques (`kubectl` uniquement).

| | 🅰️ Local | 🅱️ Cloud |
|---|---|---|
| Cluster | minikube (driver Docker Desktop) | k3d dans le DinD de la session (**1 cluster par binôme**) |
| Accès | VS Code + terminal du poste | `https://lab-kubeN.deltavia.com` (code-server), N = 1..6 |
| App (`port-forward 8080`) | `http://localhost:8080` | `https://lab-kubeN-8080.deltavia.com` |
| TP1 Docker | Docker Desktop | Docker de la session (DinD) |

- 12 stagiaires = 6 binômes = 6 sessions cloud max. VPS 4 vCores / 16 Go : mesuré ~1 Go par session avec k3s + vote, environ 2 Go estimés avec la voting app complète.
- Infra dans `infra/`, adaptée de `2606-gitops/infra-formateur`. Une session a été validée en local ; le routage Caddy/Cloudflare reste à valider sur le VPS.
- Domaines à 1 niveau (`lab-kubeN`, `lab-kubeN-<port>`), car le 2 niveaux n'est pas couvert par l'Universal SSL Cloudflare.

## Application fil rouge : la voting app

Choisie le 04/10/2026. On utilise la voting app (vote Python, redis, worker .NET, db Postgres, result Node), avec **notre fork de `vote`** pour avoir des versions visibles (v1, v2, v3 cassée). WordPress viendra en complément, en démo ou en discussion sur la haute disponibilité et les données à conserver. Le détail est dans [app/README.md](app/README.md).

## Arborescence du dépôt

```
2610-kube/
├── README.md              # sommaire du cours (point d'entrée stagiaires)
├── PLAN.md
├── slides/                # présentations HTML (reveal.js), une par module
├── diagrams/              # .excalidraw sources + exports .svg
├── labs/
│   ├── 01-conteneurs/README.md
│   ├── 02-premier-deployment/README.md
│   ├── …
│   └── 07-mission-finale/{README.md, manifests/, solution/}
├── app/                   # voting app : fork de vote (v1, v2, v3 cassée) + workflow images
├── infra/                 # k3s, namespaces, RBAC, quotas, terminaux web, scripts
├── ressources.md
└── glossaire.md           # → exporté en fiche A4 PDF
```

## TPs : GitHub ou Google Docs ?

Recommandation : **GitHub comme source unique, et lecture directement sur GitHub.**
- Un dépôt public se lit sans compte, le Markdown y est bien rendu (images, tableaux, blocs de code copiables en un clic).
- Les commandes se copient proprement, alors que Google Docs transforme les guillemets et les tirets, ce qui casse les commandes.
- Corriger un TP pendant la formation = un commit, les stagiaires rafraîchissent.
- Si besoin d'un Google Doc (commentaires, habitude des stagiaires) : export `pandoc` md → docx → import Drive, généré par script. Mais **pas d'édition côté gdoc**, sinon deux versions divergent.

## Ressources à recommander (à vérifier et compléter)

- **The Illustrated Children's Guide to Kubernetes** et **Phippy Goes to the Zoo** (CNCF), idéal pour les non-techs
- **Kubernetes: The Documentary** (Honeypot, 2 épisodes sur YouTube) : l'histoire et le « pourquoi »
- **Kubernetes Patterns** (e-book gratuit de Red Hat)
- **CNCF Annual Survey** + **CNCF Landscape** : adoption et écosystème
- **Cloud Native Maturity Model** (CNCF), pour situer une organisation
- Livres blancs de la **FinOps Foundation** sur les coûts Kubernetes
- *Kubernetes: Up & Running* (O'Reilly), pour les techs

## Questions ouvertes

- [ ] Nombre de stagiaires (→ taille du VPS) et proportion techs / non-techs
- [ ] Les stagiaires utilisent-ils Kube dans leurs projets ? Si oui, quelle plateforme (OpenShift, AKS…) ?
- [ ] TP1 Docker : podman dans le terminal web ou VPS Docker partagé ?
- [ ] Domaine pour l'Ingress (wildcard DNS)
- [ ] Dépôt GitHub public ou privé ? Un dépôt privé impose un compte GitHub par stagiaire.

## État au 05/10/2026 (fin de préparation)

| Élément | État |
|---|---|
| TP00 à TP07 | ✅ écrits, validés en local (minikube) **et** en cloud (k3d sur le VPS), relus par un agent « regard neuf » puis corrigés |
| TP08 étude de cas | ✅ écrit (atelier sans ordinateur, éléments de réponse inclus) |
| Slides | ✅ `slides/jour1.html` (33 slides), `slides/jour2.html` (36 slides), notes formateur (touche `S`) |
| Tableau blanc | ✅ `diagrams/tableau-blanc.excalidraw` (4 schémas clés à annoter) |
| Glossaire, ressources | ✅ `glossaire.md`, `ressources.md` (liens vérifiés) |
| Application | ✅ fork `bngams/example-voting-app` ; images publiques sur ghcr.io (vote 1.0/2.0/3.0 + copies de worker, result, redis, postgres, busybox) |
| Infra cloud | ✅ VPS : Caddy + 6 sessions `lab-kube1…6`, clusters `tp` prêts, images importées (`prepare-sessions.sh`) |

## Découvertes pendant la préparation (intégrées aux TPs)

- Docker Hub très lent (80 Mo en ~4 min) : toutes les images sont servies par ghcr.io.
- Les tags officiels `before`/`after` de la voting app sont identiques : d'où le fork de `vote`.
- Sans sonde de readiness, une version qui plante au démarrage **retire des pods sains** : démonstration centrale du TP06.
- `kubectl get secret -o yaml` affiche le mot de passe **en clair** dans l'annotation `last-applied-configuration` : moment fort du TP05.
- Le cluster du TP00 apparaît dans `docker ps` (minikube / k3d) : le TP01 prévient de ne pas y toucher.
- minikube annonce tous les CPU du poste : l'exercice de saturation du TP03 utilise un pod de 64 CPU, identique pour tous.
- Pannes du TP07 : une mise à jour progressive **masque** une image cassée ; la panne 4 force `Recreate` pour être visible.

## À relire avant de démarrer

- [ ] Les slides (`slides/jour1.html`, `slides/jour2.html`), avec les notes (`S`).
- [ ] Les mots de passe des sessions : `/var/www/kube-overview-labs/infra/.env` sur le VPS (S1 à S6).
- [ ] Tester une session dans son navigateur : `https://lab-kube1.deltavia.com`, puis `k3d cluster list` (le cluster `tp` doit exister).
- [ ] Mode local : minikube et kubectl sur un poste de la salle (`winget`, ou les pages officielles).
- [ ] Disque du VPS : 40 Go libres (74 %). Récupérable si besoin : ~10 Go de volumes Docker anonymes inutilisés (anciens, sans doute du cours gitops) et ~9 Go de cache de construction.
- [ ] L'infra gitops et l'infra kube partagent le VPS et les ports 80/443 : une seule à la fois.

## Après la formation

- `RESET=1 ./prepare-sessions.sh` (sur le VPS, dans `infra/`) remet les 6 sessions à zéro.
- `./cloudflare-dns.sh --delete` supprime les 24 enregistrements DNS.
- `docker compose down -v` arrête et supprime l'infra.
