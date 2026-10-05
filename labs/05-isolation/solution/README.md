# Solution du TP05

> À n'ouvrir qu'en dernier recours 😉. Les commandes supposent que vous êtes dans le dossier `tp02`.

```bash
# Mode local uniquement : recréer minikube avec Calico
minikube delete
minikube start --driver=docker --cni=calico
minikube addons enable ingress

# 1. Ménage dans default (mode cloud), puis namespace vote-app par défaut
kubectl delete -f vote.ingress.yml -f vote.svc.yml -f vote.deploy.yml
kubectl delete -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/redis.yml
kubectl delete -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/db.yml
kubectl delete -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/worker.yml
kubectl delete -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/result.yml
kubectl create namespace vote-app
kubectl config set-context --current --namespace=vote-app
kubectl apply -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/redis.yml
kubectl apply -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/db.yml
kubectl apply -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/worker.yml
kubectl apply -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/result.yml
kubectl apply -f vote.deploy.yml -f vote.svc.yml -f vote.ingress.yml

# 2. Le constat : db et redis joignables par n'importe quel pod
kubectl run test --rm -i --restart=Never --image=ghcr.io/bngams/kube-busybox:1.37 -- sh -c "nc -z -w 3 db 5432 && echo db: ouvert || echo db: bloqué; nc -z -w 3 redis 6379 && echo redis: ouvert || echo redis: bloqué"

# 3. Quota
kubectl create quota pods-max --hard=pods=12
kubectl scale deployment vote --replicas=10
kubectl describe quota pods-max
kubectl apply -f vote.deploy.yml
kubectl delete quota pods-max

# 4. Règles réseau, puis relancer le pod de test : db et redis bloqués
kubectl apply -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/05-isolation/assets/vote-app.netpol.yml
```

Pour l'exercice de l'éditeur visuel, la règle attendue est la quatrième du fichier [`vote-app.netpol.yml`](../assets/vote-app.netpol.yml) (`db-pour-worker-et-result`).
