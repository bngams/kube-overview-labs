# Kubernetes : vue d'ensemble — labs

Supports pratiques d'une formation Kubernetes de 2 jours, pour un public mixte (profils techniques et chefs de projet). L'objectif est de **comprendre ce que fait Kubernetes et pourquoi on l'utilise**, pas d'administrer un cluster.

Fil rouge : Kubernetes compare en permanence **ce qu'on lui demande** (l'état souhaité) avec **ce qui tourne réellement**, et corrige l'écart.

## Les TPs

| TP | Sujet |
|---|---|
| [00 — Environnement](labs/00-environnement/README.md) | démarrer son cluster, en local (minikube) ou en cloud (k3d) |
| [01 — Les conteneurs](labs/01-conteneurs/README.md) | image, conteneur, Dockerfile, runtime… et pourquoi il faut un orchestrateur |
| [02 — Premier Deployment](labs/02-premier-deployment/README.md) | l'état souhaité, Kubernetes répare tout seul |
| 03 — Passer à l'échelle | *à venir* |

## L'application fil rouge

La [voting app](app/README.md) de Docker, avec notre version du service `vote` : [bngams/example-voting-app](https://github.com/bngams/example-voting-app).

## Pour le formateur

- [PLAN.md](PLAN.md) : déroulé des 2 jours.
- [infra/](infra/README.md) : l'environnement cloud (6 sessions VS Code + k3d sur un VPS).
