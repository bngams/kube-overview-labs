# 01 — Les conteneurs : l'application dans une boîte

> **Scénario à réaliser en binôme.** Avant Kubernetes, il faut comprendre ce qu'il fait tourner : des **conteneurs**. Vous allez lancer l'application du cours dans un conteneur, en faire tourner deux versions côte à côte, construire votre propre image… puis la faire planter, pour découvrir pourquoi on a besoin d'un orchestrateur.
>
> 🎯 **Niveau :** débutant. Aucune connaissance en programmation n'est nécessaire.
> On suppose seulement que le [TP00](../00-environnement/README.md) est fait, en mode local ou cloud.
>
> 🧑‍✈️ **En binôme :** le **pilote** tape les commandes, le **copilote** lit la consigne à voix haute et explique ce qu'on observe. **Échangez les rôles à la section 5.**

## ✨ Objectifs

- Lancer, observer, arrêter et supprimer un conteneur.
- Distinguer le **Dockerfile** (la recette), l'**image** (le plat préparé) et le **conteneur** (le plat servi).
- Faire tourner deux versions d'une même application côte à côte, avec des réglages différents.
- Construire votre propre image à partir de sa recette.
- Constater qu'un conteneur planté **reste planté** : c'est le problème que Kubernetes résout au TP02.

## 📁 Point de départ

Ouvrez le terminal intégré de VS Code : menu **Terminal > Nouveau terminal** (*Terminal > New Terminal*). En mode cloud, c'est le VS Code de votre session `lab-kubeN`.

Vérifiez que Docker répond :

```bash
docker version
```

Vous devez voir deux blocs, `Client` et `Server`. En mode local, si le bloc `Server` affiche une erreur, Docker Desktop n'est pas démarré : lancez-le et attendez que la baleine arrête de clignoter. En mode cloud, Docker est déjà prêt.

> 🧠 **Pourquoi deux blocs ?** La commande `docker` que vous tapez est un simple **client** : elle transmet vos demandes à un **serveur**, le moteur Docker, qui fait le vrai travail. On appellera ce serveur la **machine Docker** : c'est votre poste en mode local, et votre session (isolée des autres binômes) en mode cloud.

Ce TP ne nécessite aucun dossier ni aucun fichier : tout se fait en ligne de commande.

## 🐳 1 — Premier conteneur

Une **image** est un paquet qui contient une application **et tout ce dont elle a besoin pour tourner** : le langage (ici Python), les bibliothèques, la configuration. Elle est rangée dans un **registre**, une sorte de bibliothèque d'images en ligne. Un **conteneur**, c'est une image **en train de tourner**.

Pour joindre l'application depuis le navigateur, on utilise un **port** : un numéro de « porte » sur une machine, derrière lequel une application attend les visiteurs. Un site web classique attend sur la porte 80.

Lancez l'application de vote du cours dans un conteneur :

```bash
docker run -d --name vote -p 8080:80 ghcr.io/bngams/kube-vote:1.0
```

| Élément | Rôle |
|---|---|
| `docker run` | crée un conteneur à partir d'une image et le démarre |
| `-d` | en arrière-plan (*detached*) : la commande rend la main tout de suite |
| `--name vote` | le nom qu'on donne au conteneur, pour le retrouver facilement |
| `-p 8080:80` | relie la porte **8080 de la machine Docker** à la porte **80 du conteneur**, celle où l'application attend |
| `ghcr.io/bngams/kube-vote:1.0` | l'image : `ghcr.io/bngams` est l'adresse du registre, `kube-vote` le nom de l'image, `1.0` sa **version** (on dit aussi son *tag*) |

Comme l'image n'est pas encore sur la machine Docker, celle-ci la télécharge d'abord. Le terminal affiche quelques lignes de progression, puis un long identifiant :

```
Unable to find image 'ghcr.io/bngams/kube-vote:1.0' locally
1.0: Pulling from bngams/kube-vote
...
Status: Downloaded newer image for ghcr.io/bngams/kube-vote:1.0
1b4ad01e646e2f0c51a9c6b0e1ff0bd0c0e7d64fe2a2a6f0e2bd0c1a4e8f7a21
```

Ouvrez l'application dans votre navigateur, à l'adresse correspondant à votre mode (en mode cloud, remplacez `N` par votre numéro de session ; le mot de passe peut vous être redemandé) :

| Mode | Adresse |
|---|---|
| 🅰️ Local | `http://localhost:8080` |
| 🅱️ Cloud | `https://lab-kubeN-8080.deltavia.com` |

Vous devez voir la page « Chats ou Chiens ? » avec un badge **v1.0** en haut à droite. **Ne cliquez pas sur les boutons** : l'application n'est pas complète, le vote déclencherait une erreur. En bas, la ligne « Servi par : **1b4ad01e646e** » affiche un identifiant. Le vôtre sera différent : gardez-le en tête pour la section suivante.

> 🧠 **Ce qui vient de se passer.** Vous n'avez installé ni Python ni aucune bibliothèque, et l'application tourne pourtant. Tout était **dans l'image**. C'est la promesse des conteneurs : la même image tourne de la même façon sur le poste d'un développeur, sur un serveur de test ou en production. Le fameux « *ça marche sur ma machine* » devient beaucoup plus rare.

> ⚠️ **Symptôme :** `Conflict. The container name "/vote" is already in use`.
> **Cause :** un conteneur portant ce nom existe déjà, par exemple parce que la commande a déjà été lancée une fois.
> **Correctif :** supprimez l'ancien avec `docker rm -f vote`, puis relancez la commande. Ce correctif vaut pour tous les noms de ce TP.

## 📋 2 — Observer ses conteneurs

Demandez à Docker la liste des conteneurs qui tournent :

```bash
docker ps
```

Le terminal affiche un tableau. Voici celui obtenu en mode cloud :

```
CONTAINER ID   IMAGE                            COMMAND                  CREATED         STATUS         PORTS                                     NAMES
1b4ad01e646e   ghcr.io/bngams/kube-vote:1.0     "gunicorn app:app -b…"   4 seconds ago   Up 3 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   vote
cec1ed6681b0   ghcr.io/k3d-io/k3d-proxy:5.9.0   "/bin/sh -c nginx-pr…"   2 hours ago     Up 2 hours     0.0.0.0:8000->80/tcp, …                   k3d-tp-serverlb
3a4f3c0c0210   rancher/k3s:v1.35.5-k3s1         "/bin/k3d-entrypoint…"   2 hours ago     Up 2 hours                                               k3d-tp-server-0
```

La première ligne est votre conteneur `vote`. Ses colonnes se lisent ainsi :

| Colonne | Ce qu'elle dit |
|---|---|
| `CONTAINER ID` | l'identifiant du conteneur. **C'est celui affiché en bas de la page web** : l'application affiche le nom de la « machine » qui la fait tourner, et pour elle, cette machine, c'est le conteneur |
| `IMAGE` | l'image à partir de laquelle il a été créé |
| `COMMAND` | le programme lancé dans le conteneur (ici `gunicorn`, le serveur web de l'application) |
| `CREATED` / `STATUS` | quand il a été créé ; `Up` indique qu'il tourne, et depuis combien de temps |
| `PORTS` | le branchement 8080 => 80 demandé avec `-p` (`0.0.0.0` et `[::]` signifient « accessible depuis toutes les adresses de la machine ») |
| `NAMES` | le nom donné avec `--name` |

> 🛑 **Et les autres lignes ?** Ce sont les conteneurs de **votre cluster Kubernetes** : `k3d-tp-…` en mode cloud, un conteneur nommé `minikube` en mode local. Eh oui, votre cluster du TP00 tourne lui-même dans des conteneurs ! **N'y touchez jamais** : les supprimer détruirait votre cluster. Dans la suite du TP, ignorez simplement ces lignes.

Regardez maintenant ce que l'application raconte, c'est-à-dire son **journal** (*logs*) :

```bash
docker logs vote
```

Le terminal affiche les messages de démarrage, puis une ligne par page visitée :

```
[2026-10-04 21:24:48 +0000] [1] [INFO] Starting gunicorn 26.2.0
...
[2026-10-04 21:24:48 +0000] [8] [INFO] Démarrage de vote version 1.0 sur 1b4ad01e646e
172.17.0.1 - - [04/Oct/2026:21:24:53 +0000] "GET / HTTP/1.1" 200 1020 "-" "Mozilla/5.0 …"
```

> 🗣️ **En réunion projet.** « *Tu peux regarder les logs ?* » est souvent la première question posée lors d'un incident. Les logs sont le premier endroit où une application explique ce qui ne va pas.

## 👯 3 — Deux versions côte à côte

Lançons maintenant la **version 2.0** de la même application, **en même temps** que la première. Elle ne peut pas utiliser la porte 8080, déjà prise : on la branche sur la **8081**. On en profite pour changer la question du vote, sans toucher à l'application, grâce à des **variables d'environnement** (`-e`) :

```bash
docker run -d --name vote-v2 -p 8081:80 -e OPTION_A=Thé -e OPTION_B=Café ghcr.io/bngams/kube-vote:2.0
```

| Élément | Rôle |
|---|---|
| `--name vote-v2` | un autre nom : deux conteneurs ne peuvent pas porter le même |
| `-p 8081:80` | une autre porte côté machine Docker. Dans le conteneur, l'application attend toujours sur la porte 80, sans conflit avec la première : chaque conteneur a ses propres portes |
| `-e OPTION_A=Thé -e OPTION_B=Café` | des réglages transmis à l'application au démarrage. Celle-ci est prévue pour lire `OPTION_A` et `OPTION_B` |
| `:2.0` | la version 2.0 de l'image |

Pendant le téléchargement, regardez bien les premières lignes :

```
2.0: Pulling from bngams/kube-vote
6b37362b3da7: Already exists
f64163c1b799: Already exists
295f1967d045: Already exists
48355dfcbf9e: Already exists
fefe22621c2f: Pulling fs layer
...
```

Une image est faite de **couches** (*layers*) empilées. Les quatre premières (le système et Python) sont identiques à celles de la version 1.0 : la machine Docker les a **déjà**, elle ne télécharge que ce qui change. C'est pour cela qu'une mise à jour est souvent bien plus rapide que la première installation.

Ouvrez la version 2.0 dans un nouvel onglet :

| Mode | Adresse |
|---|---|
| 🅰️ Local | `http://localhost:8081` |
| 🅱️ Cloud | `https://lab-kubeN-8081.deltavia.com` |

Vous voyez « **Thé ou Café ?** », avec un nouveau design et un badge **v2.0**. Dans l'autre onglet, la version 1.0 tourne toujours. Vérifiez-le avec `docker ps` : `vote` et `vote-v2` y figurent tous les deux, en plus des conteneurs du cluster.

> 🧠 **Ce qui vient de se passer.** Deux versions de la même application tournent **sur la même machine**, chacune dans sa boîte, sans se gêner. Et la seconde a été **configurée sans être modifiée** : la même image peut servir en test, en préproduction et en production, avec des réglages différents. Vous retrouverez cette idée au TP06 avec les ConfigMaps de Kubernetes.

## 📖 4 — D'où vient une image ? La recette

Une image est fabriquée à partir d'un fichier texte, le **Dockerfile**, qui décrit les étapes de sa construction. Voici un extrait légèrement simplifié de celui de l'application de vote (la version complète est [sur GitHub](https://github.com/bngams/example-voting-app/blob/main/vote/Dockerfile)) :

```dockerfile
FROM python:3.11-slim

WORKDIR /usr/local/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG APP_VERSION=1.0
ENV APP_VERSION=${APP_VERSION}

EXPOSE 80

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80"]
```

Chaque instruction se lit comme une étape de recette :

| Instruction | En clair |
|---|---|
| `FROM python:3.11-slim` | « partir d'une image qui contient déjà un petit Linux et Python 3.11 ». On ne part jamais de zéro |
| `WORKDIR /usr/local/app` | « se placer dans ce dossier » |
| `COPY requirements.txt ./` puis `RUN pip install …` | « copier la liste des bibliothèques nécessaires, puis les installer » |
| `COPY . .` | « copier le code de l'application » |
| `ARG APP_VERSION` / `ENV APP_VERSION` | « graver le numéro de version dans l'image ». C'est lui qui s'affiche dans le badge |
| `EXPOSE 80` | « l'application attendra sur la porte 80 » (une indication, pour information) |
| `CMD [...]` | « la commande à lancer quand un conteneur démarre » |

Listez les images présentes sur la machine Docker :

```bash
docker images
```

Vous retrouvez les deux versions téléchargées, à côté des images de votre cluster (`rancher/k3s`, `k3d-…` en cloud, `kicbase` en local), auxquelles il ne faut pas toucher non plus :

```
IMAGE                            ID             DISK USAGE   CONTENT SIZE   EXTRA
ghcr.io/bngams/kube-vote:1.0     c98a697efcee        157MB             0B
ghcr.io/bngams/kube-vote:2.0     db4a9c440555        157MB             0B
ghcr.io/k3d-io/k3d-proxy:5.9.0   403bc5ae3546       72.7MB             0B
rancher/k3s:v1.35.5-k3s1         e4a3cb95dae8        251MB             0B
...
```

Les colonnes peuvent légèrement varier selon votre version de Docker. Pour retenir les quatre notions, une analogie de cuisine :

| Notion | Analogie | Dans ce TP |
|---|---|---|
| **Dockerfile** | la recette | le fichier ci-dessus |
| **Image** | le plat préparé et surgelé, prêt à l'emploi | `ghcr.io/bngams/kube-vote:1.0` |
| **Conteneur** | le plat réchauffé et servi. On peut en servir plusieurs à partir du même plat surgelé | `vote`, `vote-v2` |
| **Registre** | le congélateur partagé, d'où chacun peut sortir les plats | `ghcr.io` |

## 🔨 5 — Construire sa propre image

🔄 **Échangez les rôles** : le copilote devient pilote.

À votre tour de fabriquer une image ! Vous allez reconstruire l'application de vote à partir de sa recette, en gravant **votre propre numéro de version**. Le code et la recette sont rangés dans un **dépôt** GitHub (un dossier de projet partagé en ligne, dont `main` est la version principale, appelée **branche**). Vous n'avez pas à les télécharger vous-mêmes : Docker sait construire directement depuis l'adresse du dépôt.

🚧 **À compléter :** dans la commande ci-dessous, remplacez les deux `XX` par les initiales du pilote, **en majuscules, sans espace ni accent** (par exemple `1.0-AB`), puis lancez-la.

```bash
docker build -t vote-perso:1.0-XX --build-arg APP_VERSION=1.0-XX "https://github.com/bngams/example-voting-app.git#main:vote"
```

| Élément | Rôle |
|---|---|
| `docker build` | construit une image en suivant un Dockerfile |
| `-t vote-perso:1.0-XX` | le nom et la version (*tag*) de la nouvelle image |
| `--build-arg APP_VERSION=1.0-XX` | la valeur donnée à l'instruction `ARG APP_VERSION` de la recette |
| `"https://…git#main:vote"` | où trouver la recette : le dépôt GitHub, branche `main`, dossier `vote` |

La construction déroule les étapes du Dockerfile une par une (`#1`, `#2`…) et se termine en moins d'une minute. Les dernières lignes ressemblent à celles-ci (elles peuvent varier selon votre version de Docker) :

```
#8 naming to docker.io/library/vote-perso:1.0-XX done
#8 DONE 0.3s
```

Pour lancer votre image, il faut une porte libre. La 8080 est encore occupée par le conteneur `vote` : arrêtez-le et supprimez-le d'abord.

```bash
docker stop vote
docker rm vote
```

| Commande | Rôle |
|---|---|
| `docker stop vote` | arrête le conteneur proprement. Il existe toujours, mais ne tourne plus |
| `docker rm vote` | supprime le conteneur arrêté. **L'image, elle, reste** : on pourra en relancer un quand on veut |

Lancez maintenant **votre** image sur la porte 8080, en remplaçant de nouveau `XX` par vos initiales :

```bash
docker run -d --name vote-perso -p 8080:80 vote-perso:1.0-XX
```

Rechargez l'onglet de la porte 8080 : le badge affiche **votre** version, par exemple **v1.0-AB**. Vous venez de suivre le cycle complet d'un développeur : recette, construction, lancement.

> ⚠️ **Symptôme :** `Bind for 0.0.0.0:8080 failed: port is already allocated`.
> **Cause :** un autre conteneur utilise déjà la porte 8080, probablement `vote` si vous ne l'avez pas supprimé. Le conteneur `vote-perso` a tout de même été créé, sans démarrer.
> **Correctif :** `docker rm -f vote vote-perso`, puis relancez la commande `docker run` ci-dessus.
>
> 📖 [docker build](https://docs.docker.com/reference/cli/docker/buildx/build/) · [Dockerfile, référence](https://docs.docker.com/reference/dockerfile/)

## ⚙️ 6 — Qui fait vraiment tourner le conteneur ?

On dit « Docker lance le conteneur », mais Docker délègue en réalité le travail à d'autres programmes. Demandez-lui lesquels :

```bash
docker info
```

La commande affiche beaucoup de lignes : remontez dans le terminal pour repérer celles-ci.

```
 Runtimes: io.containerd.runc.v2 runc
 Default Runtime: runc
```

Un conteneur est en fait un **programme ordinaire** du système Linux, que l'on a enfermé dans une boîte : il ne voit que ses propres fichiers et ses propres programmes, et l'on **peut** limiter la mémoire et le processeur qu'il utilise. Ces cloisons sont fournies par le cœur du système, le **noyau Linux**. Le travail est réparti en couches :

```
docker (le client, ce que vous tapez)
        │
        ▼
dockerd (le serveur Docker)                 Kubernetes
        │                                       │
        ▼                                       ▼
   containerd  <-- gère les images et la vie des conteneurs
        │
        ▼
      runc     <-- le "runtime" : crée la boîte et y lance le programme
        │
        ▼
  noyau Linux  <-- cloisonne le programme (fichiers, programmes, mémoire)
```

> 🧠 **Pourquoi c'est utile de le savoir ?** Kubernetes **n'a pas besoin de Docker** : il parle à un runtime à travers une interface standard (le *CRI*), le plus souvent `containerd`. C'est le cas de votre cluster k3d en mode cloud. En mode local, minikube passe encore par Docker, mais c'est un choix d'installation, pas une obligation. Dans tous les cas, **les images sont les mêmes** : une image construite avec Docker tourne telle quelle dans Kubernetes, c'est exactement ce que vous ferez au TP02. Retenez la répartition des rôles : **Kubernetes décide quoi lancer et où, le runtime sait comment le lancer.**
>
> En mode local sur Windows ou macOS, Docker Desktop fait tourner un petit Linux caché : c'est lui qui héberge vos conteneurs.

## 💥 7 — Et si l'application plante ?

Dernière expérience, la plus importante. Notre application contient une page spéciale, `/crash`, qui simule un plantage. Ouvrez-la sur **votre** conteneur, celui de la porte 8080 :

| Mode | Adresse |
|---|---|
| 🅰️ Local | `http://localhost:8080/crash` |
| 🅱️ Cloud | `https://lab-kubeN-8080.deltavia.com/crash` |

La page affiche un message avec l'identifiant de votre conteneur (le vôtre sera différent) :

```
💥 Le conteneur de 7baf710beaad va s'arrêter... Kubernetes va le redémarrer.
```

L'application promet que Kubernetes va la redémarrer… mais il n'y a **pas** de Kubernetes ici. Ouvrez la page d'accueil de la porte 8080 (l'adresse **sans** `/crash`) : **elle ne répond plus**. En mode local, le navigateur indique que la connexion a échoué ; en mode cloud, il affiche une erreur `502 Bad Gateway`.

Regardez l'état des conteneurs, y compris ceux qui sont arrêtés (`-a`, pour *all*) :

```bash
docker ps -a
```

Le terminal affiche (colonnes simplifiées, sans les conteneurs du cluster) :

```
CONTAINER ID   IMAGE                          STATUS                     NAMES
7baf710beaad   vote-perso:1.0-AB              Exited (0) 3 seconds ago   vote-perso
b061f124459a   ghcr.io/bngams/kube-vote:2.0   Up 12 minutes              vote-v2
```

Votre conteneur est `Exited` : il s'est arrêté, et **personne ne l'a relancé**. Il faut intervenir à la main :

```bash
docker start vote-perso
```

Ouvrez de nouveau la page d'accueil, toujours **sans** `/crash` (sinon vous replantez le conteneur) : elle répond.

> 🧠 **Le vrai problème.** Imaginez maintenant une application de 5 morceaux, avec plusieurs exemplaires de chacun, répartis sur plusieurs serveurs. Qui surveille tout cela la nuit ? Qui relance ce qui plante ? Qui déplace les conteneurs quand un serveur tombe ? Qui met à jour 10 exemplaires sans couper le service ?
>
> Docker sait **lancer** des conteneurs. Il manque quelqu'un pour les **surveiller et les maintenir en vie** : un **orchestrateur**. C'est le rôle de Kubernetes, que vous découvrez au TP02.
>
> ⚖️ Pour être précis, Docker propose une option `--restart always` qui relance un conteneur planté (vous pouvez l'essayer dans « Pour aller plus loin »). Mais elle s'arrête là : elle ne gère ni plusieurs serveurs, ni les mises à jour, ni la répartition de la charge.

## 🧹 8 — Faire le ménage

Supprimez les conteneurs du TP. L'option `-f` (*force*) arrête et supprime en une seule commande :

```bash
docker rm -f vote-perso vote-v2
docker ps -a
```

Il ne reste plus que les conteneurs de votre cluster (`k3d-tp-…` ou `minikube`), que vous gardez. Les portes 8080 et 8081 sont libres pour le TP02. Les **images**, elles, sont toujours là (`docker images`) : supprimer un conteneur ne supprime jamais l'image dont il est issu.

## 🔵 Pour aller plus loin

Ces pistes sont facultatives. Chacune lance son propre conteneur et le supprime à la fin.

- **Entrer dans un conteneur :** lancez-en un avec `docker run -d --name explo ghcr.io/bngams/kube-vote:1.0`, puis `docker exec -it explo sh`. Vous êtes **à l'intérieur** de la boîte : essayez `ls` (vous n'y voyez que les fichiers de l'application), `cat app.py` (son code) ou `env` (ses variables d'environnement, dont `APP_VERSION`). Tapez `exit` pour sortir, puis `docker rm -f explo`.
- **Les couches d'une image :** `docker history ghcr.io/bngams/kube-vote:1.0` liste les étapes de la recette, avec le poids de chacune. La couche la plus lourde (environ 79 Mo) est le petit Linux de base ; l'installation des bibliothèques (`pip install`) pèse environ 23 Mo, et le code de l'application quelques Ko seulement.
- **La consommation en direct :** `docker stats` affiche la mémoire et le processeur utilisés par chaque conteneur (Ctrl+C pour quitter).
- **Le redémarrage automatique selon Docker :** lancez `docker run -d --name auto --restart always -p 8080:80 ghcr.io/bngams/kube-vote:1.0`, ouvrez `/crash` sur la porte 8080, puis lancez `docker ps` quelques secondes plus tard : le conteneur est de nouveau `Up`, et `docker inspect -f "{{.RestartCount}}" auto` affiche `1`. Terminez par `docker rm -f auto`.

> 📖 [docker run, référence](https://docs.docker.com/reference/cli/docker/container/run/) · [Qu'est-ce qu'un conteneur ? (Docker)](https://www.docker.com/resources/what-container/)

## 🎉 Challenge final

- [ ] La page de vote v1.0 s'est affichée, et nous avons retrouvé l'identifiant de la page dans `docker ps`.
- [ ] Nous avons repéré les conteneurs de notre cluster dans `docker ps`, et nous n'y avons pas touché.
- [ ] Nous avons fait tourner les versions 1.0 et 2.0 en même temps, la seconde avec « Thé ou Café ? ».
- [ ] Nous savons expliquer la différence entre un Dockerfile, une image et un conteneur.
- [ ] Notre propre image `vote-perso` affiche notre version dans le badge.
- [ ] Après `/crash`, nous avons constaté que le conteneur restait arrêté, et nous l'avons relancé à la main.
- [ ] À la fin, `docker ps -a` ne montre plus que les conteneurs du cluster.

## Récap

- Une **image** contient l'application et tout ce dont elle a besoin. Elle se construit à partir d'un **Dockerfile** et se range dans un **registre**.
- Un **conteneur** est une image en train de tourner, cloisonnée des autres. On peut en lancer plusieurs à partir de la même image, avec des réglages différents (`-e`).
- Les images sont faites de **couches** partagées : une mise à jour ne télécharge que ce qui change.
- Docker délègue le lancement à **containerd** et **runc**. Kubernetes utilise les **mêmes images**, sans avoir besoin de Docker.
- Un conteneur planté **reste planté**. Il manque un **orchestrateur** pour surveiller et réparer : c'est Kubernetes.

➡️ Suite : [02 — Premier Deployment](../02-premier-deployment/README.md)
