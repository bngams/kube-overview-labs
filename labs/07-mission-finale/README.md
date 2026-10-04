# 07 — Mission finale : mettre en production, puis réparer

> **Mission à réaliser en binôme, en autonomie.** Aux TPs précédents, vous avez été guidés pas à pas pour acquérir les bases. Place à la pratique : vous allez **mettre en production** l'application complète dans un nouveau namespace, à partir de vos propres fichiers, puis jouer à la **chasse aux pannes** : votre binôme casse l'application en secret, vous la diagnostiquez et la réparez. Moins de commandes toutes faites ici : appuyez-vous sur vos fichiers, sur le [catalogue des pannes du TP06](../06-mises-a-jour/README.md#le-catalogue-des-pannes) et sur les indices. Le dossier [`solution/`](solution/) contient les réponses, à n'ouvrir qu'en dernier recours 😉.
>
> 🎯 **Niveau :** débutant, en fin de parcours. On suppose les TPs [02](../02-premier-deployment/README.md) à [06](../06-mises-a-jour/README.md) terminés : votre dossier `tp02` contient `vote.deploy.yml` (v3 avec sondes), `vote.svc.yml`, `vote.ingress.yml`, `vote.config.yml` (avec `VOTE_TITLE`) et `db.secret.yml`.

## ✨ Objectifs

- Déployer une application complète, dans le bon ordre, dans un namespace dédié.
- Vérifier soi-même qu'un déploiement fonctionne de bout en bout (la « recette »).
- Diagnostiquer et réparer des pannes réelles avec une méthode, et les documenter.

## 🧹 0 — Faire place nette

Votre application tourne dans `default`. La production aura son propre namespace, `prod` : commencez par vider `default`, pour repartir d'une situation claire et éviter que deux Ingress se disputent la porte d'entrée.

Vérifiez d'abord qu'il ne reste pas de namespaces d'essai des TPs précédents : `kubectl get namespaces` ne doit montrer ni `recette`, ni `essai`, ni `quota` (supprimez-les avec `kubectl delete namespace <nom>` si besoin).

Dans le terminal 1, depuis le dossier `tp02`, supprimez vos propres objets. `kubectl delete -f` supprime **dans le cluster** les objets qu'un fichier décrit (vos fichiers, eux, restent intacts : vous en aurez besoin juste après). La commande accepte plusieurs fichiers :

```bash
kubectl delete -f vote.ingress.yml -f vote.svc.yml -f vote.deploy.yml -f vote.config.yml -f db.secret.yml
```

Puis les 4 morceaux fournis, depuis leurs adresses :

```bash
kubectl delete -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/redis.yml
kubectl delete -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/05-configuration/assets/db.yml
kubectl delete -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/worker.yml
kubectl delete -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/04-services/assets/result.yml
```

Si une commande affiche `NotFound` pour un objet déjà absent, ce n'est pas grave : elle supprime quand même les autres. Après une trentaine de secondes (la base met un peu de temps à s'arrêter), `kubectl get all` ne doit plus afficher que le Service `kubernetes`, qui appartient au cluster (son adresse et son âge varient) :

```
NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   5h
```

`kubectl get all` est un raccourci qui liste d'un coup les types d'objets les plus courants (pods, Services, Deployments, ReplicaSets).

## 🚀 1 — La mission : mettre en production

Voici le **cahier des charges** de la mise en production, tel qu'un chef de projet pourrait le rédiger :

| # | Exigence |
|---|---|
| 1 | Toute l'application vit dans un namespace nommé `prod` |
| 2 | Les 5 morceaux tournent : `vote`, `redis`, `worker`, `db`, `result` |
| 3 | `vote` tourne en **version 3.0**, en **3 réplicas**, avec ses **sondes de santé** et ses **réservations** de ressources |
| 4 | La question et le titre du vote viennent de la ConfigMap `vote-config` |
| 5 | Les identifiants de la base viennent du Secret `db-credentials` |
| 6 | La page de vote est accessible par la **porte d'entrée** (Ingress, port 8000) |
| 7 | Un vote apparaît sur la page des **résultats** |

🚧 **À vous de jouer.** Créez le namespace, puis déployez tout dedans. Tout ce qu'il faut existe déjà : vos fichiers dans `tp02`, et les 4 fichiers fournis, dont les adresses sont celles de la section 0 (attention : pour `db`, c'est bien la version du **TP05**, dans le dossier `05-configuration`, celle qui utilise le Secret). Pour envoyer un fichier dans un namespace, vous connaissez l'option depuis le TP05 : `-n prod`, à placer avant ou après `-f`, peu importe.

Avant de vous lancer, réfléchissez à l'**ordre** : quels objets les autres attendent-ils ?

<details>
<summary>💡 Indice 1 : par quoi commencer ?</summary>

Les pods de `vote` lisent la ConfigMap, ceux de `db` lisent le Secret. S'ils démarrent avant, ils restent en `CreateContainerConfigError` (TP05). Créez donc d'abord le namespace, puis la ConfigMap et le Secret, et seulement ensuite les Deployments.

</details>

<details>
<summary>💡 Indice 2 : la forme des commandes</summary>

Le namespace se crée avec `kubectl create namespace prod` (TP05). Ensuite, chaque commande ressemble à `kubectl apply -n prod -f <fichier ou adresse>`. Vous pouvez aussi donner plusieurs fichiers d'un coup : `kubectl apply -n prod -f db.secret.yml -f vote.config.yml`.

</details>

<details>
<summary>💡 Indice 3 : l'ordre complet</summary>

1. le namespace `prod` ;
2. le Secret et la ConfigMap ;
3. `redis`, `db` (version TP05), `worker`, `result` ;
4. `vote` (Deployment et Service) ;
5. l'Ingress.

</details>

> 🧠 **L'ordre est-il vraiment obligatoire ?** Pas tout à fait : grâce à la réconciliation, un pod qui démarre trop tôt finit par démarrer correctement une fois ce qu'il attend créé. Mais un bon ordre évite des erreurs transitoires et rend un déploiement **prévisible**. En entreprise, des outils comme **Helm** ou **Kustomize** regroupent tous ces fichiers en un seul paquet, installé d'une seule commande.

## ✅ 2 — La recette : vérifier soi-même

Un déploiement n'est terminé que lorsqu'on a **vérifié** qu'il fonctionne. Passez le cahier des charges en revue, exigence par exigence.

**Exigences 1 à 5 : les objets.** Une seule commande montre presque tout :

```bash
kubectl get all -n prod
```

Vous devez voir 7 pods `Running` (3 `vote`, 1 de chacun des autres), 4 Services (`db`, `redis`, `result`, `vote`), 5 Deployments tous complets (`1/1`, ou `3/3` pour `vote`) et leurs 5 ReplicaSets. Vérifiez aussi la ConfigMap, le Secret et l'Ingress, qui n'apparaissent pas dans `get all` :

```bash
kubectl get configmaps,secrets,ingress -n prod
```

La ConfigMap `vote-config` doit compter 3 réglages (colonne `DATA` : les deux options et `VOTE_TITLE`), le Secret `db-credentials` 2. Ignorez `kube-root-ca.crt`, créée automatiquement dans chaque namespace.

**Exigence 6 : la porte d'entrée.** Ouvrez la page de vote, comme au TP04 :

| Mode | Adresse | À faire avant |
|---|---|---|
| 🅰️ Local | `http://localhost:8000` | dans un **terminal 2**, le tunnel vers le contrôleur : `kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8000:80` |
| 🅱️ Cloud | `https://lab-kubeN-8000.deltavia.com` | rien |

Le badge doit indiquer **v3.0**, avec votre titre en haut de la page.

**Exigence 7 : les résultats.** Dans un **terminal 3**, ouvrez le tunnel vers les résultats. Attention, ils sont maintenant dans `prod` :

```bash
kubectl port-forward -n prod service/result 8081:80
```

Ouvrez `http://localhost:8081` (local) ou `https://lab-kubeN-8081.deltavia.com` (cloud), votez sur la page de vote : le résultat doit bouger.

> ⚠️ **Le tunnel répond `services "result" not found` ?** Vous avez sans doute oublié `-n prod` : sans lui, `kubectl` cherche dans `default`, qui est vide.
> **Il répond `error: timed out waiting for the condition` ?** Le Service `result` ne trouve aucun pod à servir : vérifiez que `result` tourne bien dans `prod` (`kubectl get pods -n prod`).
> **Les résultats ne bougent pas alors que tout est `Running` ?** `worker` ou `result` ont peut-être démarré avant la base : relancez-les avec `kubectl rollout restart deployment worker result -n prod`, puis relancez le tunnel du terminal 3.

🎉 Les 7 exigences sont remplies ? Votre application est en production. Appelez le formateur pour une « recette » officielle : il vérifiera avec vous le cahier des charges.

## 🔍 3 — La chasse aux pannes

L'application est en production… et les incidents commencent. Quatre pannes ont été préparées. Chacune remplace un de vos objets par une version sabotée, comme le ferait une erreur de manipulation ou une livraison ratée.

### Les règles du jeu

1. Le **copilote** choisit une panne **pas encore jouée** (1 à 4), sans dire laquelle, pendant que le pilote regarde ailleurs. Il ouvre un **terminal 4** (icône **Scinder le terminal**) et y applique la panne :
   ```bash
   kubectl apply -n prod -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/07-mission-finale/pannes/panne-1.yml
   ```
   (en remplaçant `panne-1` par le numéro choisi). Il **ferme ensuite ce terminal 4** (icône 🗑️) : la réponse de la commande trahirait l'objet saboté. **N'ouvrez pas** les fichiers de pannes : ce serait tricher 😉.
2. Le **pilote** constate le symptôme dans le navigateur, mène l'enquête avec `kubectl` (comptez une quinzaine de minutes avant d'ouvrir les indices), puis **répare** en réappliquant le bon fichier, choisi dans le tableau ci-dessous. Interdit de supprimer le namespace pour tout recommencer !
3. Ensemble, remplissez la **fiche d'incident** ci-dessous.
4. **Échangez les rôles**, et passez à une autre panne.

Pour réparer, il faut savoir quel fichier décrit le bon état de chaque objet :

| Objet | Fichier à réappliquer (avec `-n prod`) |
|---|---|
| Ingress `vote` | `vote.ingress.yml` |
| Service et Deployment `vote` | `vote.svc.yml`, `vote.deploy.yml` |
| ConfigMap `vote-config` | `vote.config.yml` |
| Secret `db-credentials` | `db.secret.yml` |
| `redis`, `worker`, `result` (Deployment et Service) | leurs adresses du TP04 (section 0) |
| `db` (Deployment et Service) | son adresse du TP05 (section 0) |

Laissez les tunnels des terminaux 2 (en local) et 3 ouverts : vous en aurez besoin pour observer les symptômes. Si l'un d'eux s'est arrêté (l'invite de commande est revenue), relancez simplement la même commande. Après chaque réparation, attendez quelques secondes et revérifiez les 7 exigences ; si les résultats ne bougent toujours pas, relancez `worker` et `result` comme indiqué à la section 2.

### La méthode d'enquête

Une bonne enquête va **du symptôme vers la cause**, en zoomant progressivement :

| Étape | Question | Outils |
|---|---|---|
| 1. Le symptôme | Que voit l'utilisateur ? Quelle page, quelle action ne marche plus ? | le navigateur |
| 2. Vue d'ensemble | Quel objet n'est pas dans son état normal ? | `kubectl get all -n prod`, `kubectl get ingress -n prod` |
| 3. Le détail | Que dit cet objet sur lui-même ? | `kubectl describe <type> <nom> -n prod`. Regardez notamment `Events` (l'historique), `Backends` pour un Ingress (où il envoie les visiteurs), `Selector` et `Endpoints` pour un Service (l'étiquette recherchée, et les pods effectivement servis) |
| 4. L'application | Que dit l'application ? | `kubectl logs <pod> -n prod` (copiez le nom du pod depuis `kubectl get pods -n prod` ; ajoutez `--previous` pour un pod en `CrashLoopBackOff`) |
| 5. La réparation | Quel fichier décrit le bon état ? | `kubectl apply -n prod -f …` |

> 💡 N'oubliez pas `-n prod` dans **toutes** vos commandes : sans lui, `kubectl` regarde dans `default`, qui est vide, et vous répond qu'il n'y a rien.

### La fiche d'incident

Pour chaque panne, remplissez une ligne. C'est exactement ce qu'on attend d'une équipe d'exploitation après un incident (on parle de *post-mortem*), et c'est souvent le chef de projet qui le présente.

| Panne | Symptôme (ce que voit l'utilisateur) | Cause (ce que vous avez trouvé, et avec quelle commande) | Réparation | Comment l'éviter à l'avenir ? |
|---|---|---|---|---|
| … | | | | |
| … | | | | |
| … | | | | |
| … | | | | |

### Les indices

Bloqués ? Les indices sont classés par **symptôme**, puisque vous ne savez pas quelle panne a été appliquée. Ouvrez-les **dans l'ordre**, un par un.

<details>
<summary>Symptôme : la page de vote s'affiche, mais cliquer pour voter donne une erreur (« Internal Server Error »)</summary>

- Quel morceau `vote` appelle-t-il quand on vote ? (Revoyez le schéma du TP04, section 4.)
- Regardez la colonne `READY` des Deployments : `kubectl get deployments -n prod`.
- Un Deployment peut être « réglé » pour n'avoir aucun pod (TP03, section 5).

</details>

<details>
<summary>Symptôme : la page de vote ne s'affiche plus du tout (erreur 503, ou 404 en mode cloud, sur le port 8000)</summary>

- Les pods `vote` tournent-ils ? Si oui, le problème est sur le **chemin** qui mène jusqu'à eux.
- Le chemin d'une visite : navigateur => contrôleur d'Ingress => **Ingress** => **Service** => pods. Suivez la chaîne depuis le début.
- Ce symptôme peut avoir **deux causes différentes**. Lisez la ligne `Backends` de `kubectl describe ingress vote -n prod` : vers quel Service l'Ingress envoie-t-il les visiteurs ? Ce Service existe-t-il, et sert-il des pods ?
- Pour un Service, comparez son `Selector` (l'étiquette recherchée) avec les étiquettes réelles des pods : `kubectl get pods -n prod --show-labels`. La ligne `Endpoints` doit lister des adresses de pods.

</details>

<details>
<summary>Symptôme : on peut voter (la coche apparaît), mais la page des résultats ne bouge plus</summary>

- Qui transporte les votes de `redis` vers `db` ? (TP04, section 4.)
- Regardez l'état des pods de ce morceau, puis décrivez celui qui est en échec.
- Le statut affiché fait partie du catalogue du TP06.

</details>

## 🎉 Challenge final

- [ ] L'application complète tourne dans le namespace `prod`, et les 7 exigences du cahier des charges sont vérifiées.
- [ ] Nous avons diagnostiqué et réparé les 4 pannes, sans supprimer le namespace.
- [ ] Notre fiche d'incident est remplie, avec pour chaque panne la commande qui a révélé la cause.
- [ ] Nous savons expliquer pourquoi les pannes 2 et 3 ont le même symptôme mais pas la même cause.

## 🔵 Pour aller plus loin

- **Inventez votre propre panne :** écrivez un fichier qui sabote un objet (une mauvaise étiquette, un mauvais port, une version inexistante…), faites-la diagnostiquer par un autre binôme, puis échangez.
- **Tout en une commande :** rangez tous les fichiers de la mission dans un même dossier, puis `kubectl apply -n prod -f .` les applique tous d'un coup (le `.` désigne le dossier courant). Vous découvrirez pourquoi l'ordre peut alors poser problème… et pourquoi des outils comme Helm ou Kustomize existent.
- **Nettoyage final :** à la fin de la formation, `kubectl delete namespace prod` supprime toute l'application en une commande.

## Récap

- Un déploiement complet, c'est un **ensemble de fichiers** appliqués dans un ordre réfléchi, dans un namespace dédié.
- Un déploiement n'est fini qu'une fois **vérifié** contre le cahier des charges.
- Face à un incident : **symptôme**, **vue d'ensemble** (`get`), **détail** (`describe`), **application** (`logs`), **réparation** (`apply` du bon fichier).
- Le même symptôme peut avoir des causes différentes : c'est l'enquête, pas l'intuition, qui tranche.
- Documenter chaque incident (la fiche) permet d'éviter qu'il se reproduise.

➡️ Pour terminer : [l'étude de cas « Kubernetes dans votre projet »](../08-etude-de-cas/README.md)
