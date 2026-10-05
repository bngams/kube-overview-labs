# Kubernetes : vue d'ensemble — labs

Supports pratiques d'une formation Kubernetes de 2 jours, pour un public mixte (profils techniques et chefs de projet). L'objectif est de **comprendre ce que fait Kubernetes et pourquoi on l'utilise**, pas d'administrer un cluster.

Fil rouge : Kubernetes compare en permanence **ce qu'on lui demande** (l'état souhaité) avec **ce qui tourne réellement**, et corrige l'écart.

## Les TPs

| TP | Sujet | Jour |
|---|---|---|
| [00 — Environnement](labs/00-environnement/README.md) | démarrer son cluster, en local (minikube) ou en cloud (k3d) | J1 |
| [01 — Les conteneurs](labs/01-conteneurs/README.md) | image, conteneur, Dockerfile, runtime… et pourquoi il faut un orchestrateur | J1 |
| [02 — Premier Deployment](labs/02-premier-deployment/README.md) | l'état souhaité : Kubernetes répare tout seul | J1 |
| [03 — Passer à l'échelle](labs/03-scaling/README.md) | réplicas, « le fichier fait foi », 0 réplica, réservations et pods `Pending` | J1 |
| [04 — Services et Ingress](labs/04-services/README.md) | adresse stable, application complète, vote de bout en bout, porte d'entrée | J2 |
| [05 — Isoler et encadrer](labs/05-isolation/README.md) | namespaces, quotas, règles réseau (NetworkPolicies), ouverture sur Kyverno | J2 |
| [06 — Configuration et secrets](labs/06-configuration/README.md) | ConfigMap, Secret et ses limites | J2 |
| [07 — Mettre à jour et réparer](labs/07-mises-a-jour/README.md) | mise à jour sans coupure, pannes, retour arrière, sondes de santé | J2 |
| [08 — Mission finale](labs/08-mission-finale/README.md) | mise en production en autonomie, puis chasse aux pannes | J2 |
| [09 — Étude de cas](labs/09-etude-de-cas/README.md) | Kubernetes dans votre projet : quand, comment, combien, qui | J2 |

## Supports

- **En ligne** : [bngams.github.io/kube-overview-labs](https://bngams.github.io/kube-overview-labs/) (les trois présentations)
- [Slides du jour 1](slides/jour1.html) et [du jour 2](slides/jour2.html) (à ouvrir dans un navigateur, touche `S` pour les notes)
- [Présentation « conférence »](slides/talk.html) : Kubernetes en chiffres, pour tout public
- [Glossaire](glossaire.md) : les mots de la formation, à garder sous la main
- [Ressources](ressources.md) : lectures et vidéos recommandées

## L'application fil rouge

La [voting app](app/README.md) de Docker, avec notre version du service `vote` : [bngams/example-voting-app](https://github.com/bngams/example-voting-app).

## Pour le formateur

- [PLAN.md](PLAN.md) : déroulé des 2 jours.
- [infra/](infra/README.md) : l'environnement cloud (6 sessions VS Code + k3d sur un VPS).
