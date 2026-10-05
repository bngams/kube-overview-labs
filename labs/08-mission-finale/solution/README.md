# Solution du TP08

> À n'ouvrir qu'en dernier recours 😉. Les commandes supposent que vous êtes dans le dossier `tp02`.

## La mise en production

```bash
kubectl delete namespace vote-app
kubectl config set-context --current --namespace=default
kubectl create namespace prod
kubectl apply -n prod -f db.secret.yml -f vote.config.yml
kubectl apply -n prod -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/redis.yml
kubectl apply -n prod -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/06-configuration/assets/db.yml
kubectl apply -n prod -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/worker.yml
kubectl apply -n prod -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/result.yml
kubectl apply -n prod -f vote.deploy.yml -f vote.svc.yml -f vote.ingress.yml
```

Les fichiers attendus dans `tp02` sont ceux des solutions précédentes : [`vote.deploy.yml`](../../07-mises-a-jour/solution/vote.deploy.yml) et [`vote.config.yml`](../../07-mises-a-jour/solution/vote.config.yml) du TP07, [`db.secret.yml`](../../06-configuration/solution/db.secret.yml) du TP06, [`vote.svc.yml`](../../04-services/solution/vote.svc.yml) et [`vote.ingress.yml`](../../04-services/solution/vote.ingress.yml) du TP04.

## Les pannes

| Panne | Symptôme | Cause | Commande qui la révèle | Réparation | Prévention |
|---|---|---|---|---|---|
| 1 | La page de vote s'affiche, mais voter renvoie `Internal Server Error` | `redis` a été mis à **0 réplica** : `vote` ne peut plus déposer les votes | `kubectl get deployments -n prod` => `redis 0/0` | `kubectl apply -n prod -f …/04-services/assets/redis.yml` | Le fichier fait foi (TP03) : modifications tracées dans Git, revue avant application |
| 2 | Port 8000 : `503` (NGINX, mode local) ou `404` (Traefik, mode cloud) | L'Ingress envoie vers un Service **qui n'existe pas** (`vote-frontend`) | `kubectl describe ingress vote -n prod` => `services "vote-frontend" not found` | `kubectl apply -n prod -f vote.ingress.yml` | Vérifier les noms à la relecture ; tester l'accès après chaque déploiement |
| 3 | Port 8000 : `503`, l'Ingress semble correct | Le **selector** du Service `vote` (`app: votes`) ne correspond à aucun pod (`app: vote`) | `kubectl describe service vote -n prod` => `Endpoints` vide | `kubectl apply -n prod -f vote.svc.yml` | Une étiquette mal recopiée suffit : outils de validation, tests automatiques après déploiement |
| 4 | On vote (la coche apparaît), mais les résultats ne bougent plus | `worker` déployé avec une **image inexistante** (`kube-worker:1.1`), et la stratégie `Recreate` a supprimé l'ancien pod avant de lancer le nouveau | `kubectl get pods -n prod` => `ImagePullBackOff`, puis `kubectl describe pod` => `manifest unknown` | `kubectl apply -n prod -f …/04-services/assets/worker.yml` | Vérifier que l'image est publiée avant de la déployer ; préférer la mise à jour progressive, qui aurait gardé l'ancien pod |

### À souligner lors du débriefing

- **Pannes 2 et 3** : même symptôme, causes différentes. Seule l'enquête le long de la chaîne (navigateur => contrôleur => Ingress => Service => pods) permet de trancher.
- **Panne 4** : les votes ne sont pas perdus ! Ils attendent dans la file `redis` (`kubectl exec -n prod deployment/redis -- redis-cli llen votes` les compte). Dès que `worker` revient, il les traite tous : c'est l'intérêt d'une file d'attente entre deux morceaux d'une application.
- **Panne 4 encore** : avec la stratégie par défaut (mise à jour progressive), cette panne aurait été invisible, puisque l'ancien pod aurait continué à tourner. La stratégie `Recreate` (« tout arrêter, puis redémarrer ») se justifie parfois, mais elle supprime ce filet de sécurité.
