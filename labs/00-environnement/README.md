# 00 — Mise en place de l'environnement

> **Scénario à réaliser en binôme, au tout début de la formation.** Vous allez démarrer **votre propre cluster Kubernetes**, soit sur votre poste (mode **local**), soit sur une machine en ligne préparée par le formateur (mode **cloud**).
>
> 🎯 **Niveau :** débutant, aucun prérequis technique. Il suffit de savoir ouvrir un terminal et copier-coller une commande.
>
> 💡 **Le seul TP qui diffère selon le mode.** Une fois ce TP terminé, **toutes les commandes des TPs suivants sont identiques** en local et en cloud. Seule l'adresse pour ouvrir une application dans le navigateur change (voir la section 3).

## ✨ Objectifs

- Choisir un mode (local ou cloud) avec votre binôme.
- Démarrer un cluster Kubernetes et vérifier qu'il répond.
- Savoir ouvrir une application du cluster dans votre navigateur.

## 🧭 1 — Choisir son mode

Les deux modes donnent exactement le même résultat : un cluster Kubernetes **rien qu'à vous**. Ils diffèrent seulement par l'endroit où ce cluster tourne.

| | 🅰️ Mode local | 🅱️ Mode cloud |
|---|---|---|
| Où tourne le cluster ? | Sur votre poste, dans Docker Desktop, grâce à **minikube** | Sur un serveur de la formation, grâce à **k3d** |
| Ce qu'il faut sur le poste | Docker Desktop, minikube, kubectl | **Rien**, un navigateur suffit |
| Éditeur et terminal | VS Code installé sur le poste, terminal intégré | VS Code **dans le navigateur**, terminal intégré |
| Nombre de places | Illimité | **6 sessions**, une par binôme |
| Quand le choisir ? | Docker Desktop est déjà installé et fonctionne | Poste verrouillé, installation impossible ou trop lente |

> 🧠 **minikube, k3d… ce n'est pas « un autre Kubernetes » ?** Non. Ce sont deux façons d'installer **un vrai Kubernetes en miniature** (un seul serveur) pour apprendre ou tester. Les commandes `kubectl` que vous taperez ensuite sont les mêmes que sur un cluster de production chez AWS, Google ou Azure.

Une fois votre mode choisi, faites **uniquement** la section correspondante (2A ou 2B), puis passez à la section 3.

## 🅰️ 2A — Mode local : minikube

### Étape 1 — Vérifier Docker Desktop

minikube fait tourner Kubernetes **à l'intérieur de Docker**. Docker Desktop doit donc être lancé (icône de la baleine dans la barre des tâches) avant toute chose.

Ouvrez un terminal (PowerShell sous Windows, Terminal sous macOS) et tapez :

```bash
docker version
```

Vous devez voir deux blocs, `Client` et `Server`. Si le bloc `Server` affiche une erreur, Docker Desktop n'est pas démarré : lancez-le, attendez que la baleine arrête de clignoter, puis recommencez.

> ⚠️ Docker Desktop n'est pas installé ? Téléchargez-le depuis [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/), ou choisissez le mode cloud (section 2B).

### Étape 2 — Installer minikube et kubectl

Deux outils sont nécessaires :

| Outil | Rôle |
|---|---|
| `minikube` | **crée et démarre** le cluster sur votre poste |
| `kubectl` | **parle** au cluster : c'est la télécommande de Kubernetes, celle que vous utiliserez dans tous les TPs |

Sous **Windows** (PowerShell) :

```bash
winget install Kubernetes.minikube
winget install Kubernetes.kubectl
```

Sous **macOS** :

```bash
brew install minikube kubectl
```

Fermez puis rouvrez votre terminal pour que les nouvelles commandes soient reconnues. Si VS Code était ouvert, **fermez-le complètement et relancez-le** : son terminal intégré ne verrait pas encore `minikube` ni `kubectl`.

> 💡 **À partir du TP01, on travaille dans le terminal intégré de VS Code** (menu **Terminal > Nouveau terminal**), en mode local comme en mode cloud. Les consignes sont ainsi les mêmes pour tout le monde.

> 📖 En cas de souci (commande `winget` absente, poste sans droits d'installation…), suivez les pages officielles, qui proposent aussi des installateurs à télécharger : [Installer minikube](https://minikube.sigs.k8s.io/docs/start/) · [Installer kubectl](https://kubernetes.io/fr/docs/tasks/tools/). Si l'installation bloque, passez au mode cloud (section 2B).

### Étape 3 — Démarrer le cluster

```bash
minikube start --driver=docker
```

Le premier démarrage télécharge Kubernetes et prend quelques minutes. Il se termine par la ligne suivante :

```
Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

Passez maintenant à la section 3.

## 🅱️ 2B — Mode cloud : k3d

### Étape 1 — Se connecter à sa session

Le formateur attribue à chaque binôme un **numéro de session** (de 1 à 6) et un **mot de passe**. Dans tout le cours, remplacez `N` par votre numéro.

1. Ouvrez `https://lab-kubeN.deltavia.com` dans votre navigateur (par exemple `https://lab-kube3.deltavia.com` pour la session 3).
2. Saisissez le mot de passe. **VS Code s'ouvre dans le navigateur.**
3. Ouvrez un terminal : menu ☰ > **Terminal** > **New Terminal**.

Les outils sont déjà installés. Vérifiez-le :

```bash
kubectl version --client
k3d version
```

### Étape 2 — Vérifier son cluster (ou le créer)

En mode cloud, le formateur a normalement **déjà créé** votre cluster Kubernetes, nommé `tp`, dans le Docker de votre session (qui n'est partagé avec personne). Vérifiez-le :

```bash
k3d cluster list
```

Si le cluster existe, le terminal affiche une ligne `tp` :

```
NAME   SERVERS   AGENTS   LOADBALANCER
tp     1/1       0/0      true
```

Passez alors directement à la section 3.

Si la liste est vide, créez le cluster vous-mêmes :

```bash
k3d cluster create tp --port "8000:80@loadbalancer"
```

| Élément | Rôle |
|---|---|
| `cluster create tp` | crée un cluster nommé `tp` |
| `--port "8000:80@loadbalancer"` | ouvre la porte d'entrée du cluster sur le port 8000. **Elle ne servira qu'au TP04** (Ingress), mais elle doit être prévue dès la création |

La commande prend environ 30 secondes. Elle se termine par les lignes suivantes :

```
INFO[0032] Cluster 'tp' created successfully!
INFO[0032] You can now use it like this:
kubectl cluster-info
```

## ✅ 3 — Vérifier le cluster (identique pour les deux modes)

À partir d'ici, **tout est identique** en local et en cloud. Demandez à Kubernetes la liste de ses serveurs (on dit des **nœuds**, *nodes* en anglais) :

```bash
kubectl get nodes
```

Vous devez voir **un nœud** à l'état `Ready` :

```
NAME              STATUS   ROLES           AGE   VERSION
minikube          Ready    control-plane   1m    v1.34.0        <- en mode local
k3d-tp-server-0   Ready    control-plane   1m    v1.35.5+k3s1   <- en mode cloud
```

> 🧠 **Ce qui vient de se passer.** `kubectl` a envoyé une question au cluster (« quels sont tes nœuds ? ») et le cluster a répondu. Votre télécommande est branchée : vous êtes prêts.

### Ouvrir une application dans le navigateur

Dans les TPs, vous rendrez une application accessible avec une commande `kubectl port-forward … 8080:80`. L'adresse à ouvrir dans votre navigateur dépend alors du mode :

| Mode | Adresse de l'application |
|---|---|
| 🅰️ Local | `http://localhost:8080` |
| 🅱️ Cloud | `https://lab-kubeN-8080.deltavia.com` (à la première ouverture, le mot de passe de la session est redemandé) |

Le même principe vaut pour tous les ports : `8081` donne `http://localhost:8081` ou `https://lab-kubeN-8081.deltavia.com`.

> 💡 **Mode cloud :** vous pouvez aussi ouvrir l'application **dans** VS Code. Ouvrez l'onglet **PORTS** du panneau du bas, puis cliquez sur l'icône 🌐 du port voulu.

## 🔁 4 — Arrêter et redémarrer son cluster

Le cluster consomme de la mémoire. Arrêtez-le en fin de journée et redémarrez-le le lendemain matin : **votre travail est conservé**.

| | 🅰️ Local | 🅱️ Cloud |
|---|---|---|
| Arrêter | `minikube stop` | `k3d cluster stop tp` |
| Redémarrer | `minikube start` | `k3d cluster start tp` |
| Tout supprimer (fin de formation) | `minikube delete` | `k3d cluster delete tp` |

## 🎉 Checklist

- [ ] Notre binôme a choisi son mode : local ou cloud.
- [ ] `kubectl get nodes` affiche un nœud `Ready`.
- [ ] Nous savons quelle adresse ouvrir pour voir une application sur le port 8080.

➡️ Suite : [01 — Les conteneurs](../01-conteneurs/README.md)
