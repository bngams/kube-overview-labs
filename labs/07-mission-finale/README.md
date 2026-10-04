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

Dans le terminal 1, depuis le dossier `tp02`, supprimez vos propres objets. `kubectl delete -f` supprime ce qu'un fichier décrit, et accepte plusieurs fichiers :

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

Après une quinzaine de secondes, `kubectl get all` ne doit plus afficher que le Service `kubernetes`, qui appartient au cluster :

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

🚧 **À vous de jouer.** Créez le namespace, puis déployez tout dedans. Tout ce qu'il faut existe déjà : vos fichiers dans `tp02`, et les 4 fichiers fournis aux TP04 et TP05 (attention : pour `db`, prenez la version du **TP05**, celle qui utilise le Secret). Pour envoyer un fichier dans un namespace, vous connaissez l'option depuis le TP05.

Avant de vous lancer, réfléchissez à l'**ordre** : quels objets les autres attendent-ils ?

<details>
<summary>💡 Indice 1 : par quoi commencer ?</summary>

Les pods de `vote` lisent la ConfigMap, ceux de `db` lisent le Secret. S'ils démarrent avant, ils restent en `CreateContainerConfigError` (TP05). Créez donc d'abord le namespace, puis la ConfigMap et le Secret, et seulement ensuite les Deployments.

</details>

<details>
<summary>💡 Indice 2 : la forme des commandes</summary>

Chaque commande ressemble à `kubectl apply -n prod -f <fichier ou adresse>`. Vous pouvez aussi donner plusieurs fichiers d'un coup : `kubectl apply -n prod -f db.secret.yml -f vote.config.yml`.

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

Vous devez voir 7 pods `Running` (3 `vote`, 1 de chacun des autres), 4 Services (`db`, `redis`, `result`, `vote`) et 5 Deployments, tous complets (`1/1`, ou `3/3` pour `vote`). Vérifiez aussi la ConfigMap, le Secret et l'Ingress, qui n'apparaissent pas dans `get all` :

```bash
kubectl get configmaps,secrets,ingress -n prod
```

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

> ⚠️ **Le tunnel répond `error: timed out waiting for the condition` ?** Le Service `result` ne trouve aucun pod à servir : vérifiez que `result` tourne bien dans `prod` (`kubectl get pods -n prod`).

🎉 Les 7 exigences sont remplies ? Votre application est en production. Appelez le formateur pour une « recette » officielle : il vérifiera avec vous le cahier des charges.

## 🔍 3 — La chasse aux pannes

L'application est en production… et les incidents commencent. Quatre pannes ont été préparées. Chacune remplace un de vos objets par une version sabotée, comme le ferait une erreur de manipulation ou une livraison ratée.

### Les règles du jeu

1. Le **copilote** choisit une panne au hasard (1 à 4), sans dire laquelle, et l'applique pendant que le pilote regarde ailleurs :
   ```bash
   kubectl apply -n prod -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/07-mission-finale/pannes/panne-1.yml
   ```
   (en remplaçant `panne-1` par le numéro choisi). **N'ouvrez pas** les fichiers de pannes : ce serait tricher 😉.
2. Le **pilote** constate le symptôme dans le navigateur, mène l'enquête avec `kubectl`, puis **répare** en réappliquant le bon fichier (le vôtre, ou le fichier fourni). Interdit de supprimer le namespace pour tout recommencer !
3. Ensemble, remplissez la **fiche d'incident** ci-dessous.
4. **Échangez les rôles**, et passez à une autre panne.

Laissez les tunnels des terminaux 2 (en local) et 3 ouverts : vous en aurez besoin pour observer les symptômes. Après chaque réparation, attendez quelques secondes et revérifiez les 7 exigences.

### La méthode d'enquête

Une bonne enquête va **du symptôme vers la cause**, en zoomant progressivement :

| Étape | Question | Outils |
|---|---|---|
| 1. Le symptôme | Que voit l'utilisateur ? Quelle page, quelle action ne marche plus ? | le navigateur |
| 2. Vue d'ensemble | Quel objet n'est pas dans son état normal ? | `kubectl get all -n prod`, `kubectl get ingress -n prod` |
| 3. Le détail | Que dit cet objet sur lui-même ? | `kubectl describe <type> <nom> -n prod` (regardez la fin : `Events`, `Endpoints`, `Backends`) |
| 4. L'application | Que dit l'application ? | `kubectl logs <pod> -n prod` |
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

Bloqués ? Ouvrez les indices **dans l'ordre**, un par un.

<details>
<summary>Indices pour la panne 1</summary>

- La page de vote s'affiche, mais **cliquer** sur une option renvoie une erreur `Internal Server Error`. Quel morceau `vote` appelle-t-il quand on vote ? (Revoyez le schéma du TP04, section 4.)
- Regardez la colonne `READY` des Deployments.
- Un Deployment peut être « réglé » pour n'avoir aucun pod (TP03, section 5).

</details>

<details>
<summary>Indices pour la panne 2</summary>

- La page de vote ne s'affiche plus du tout : erreur `503` (ou `404` en mode cloud) sur le port 8000. Pourtant, les pods `vote` tournent.
- Le chemin d'une visite : navigateur => contrôleur d'Ingress => **Ingress** => Service => pods. Commencez par le début de la chaîne.
- Lisez la ligne `Backends` de `kubectl describe ingress vote -n prod`.

</details>

<details>
<summary>Indices pour la panne 3</summary>

- Même symptôme que la panne 2… mais l'Ingress, lui, semble correct. Continuez le long de la chaîne.
- Lisez la ligne `Endpoints` de `kubectl describe service vote -n prod`. Combien de pods le Service sert-il ?
- Comparez le `Selector` du Service avec les étiquettes des pods (`kubectl get pods -n prod --show-labels`).

</details>

<details>
<summary>Indices pour la panne 4</summary>

- On peut voter (la coche apparaît), mais la page des **résultats** ne bouge plus. Qui transporte les votes de `redis` vers `db` ?
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
