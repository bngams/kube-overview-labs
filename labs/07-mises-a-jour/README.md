# 07 — Mettre à jour et réparer

> **Scénario à réaliser en binôme.** L'équipe de développement livre deux nouvelles versions de `vote` : une **v2** avec un nouveau design, puis une **v3**… qui exige un réglage que personne n'a pensé à livrer. Vous allez déployer la v2 **sans coupure**, voir la v3 planter, **diagnostiquer** la panne comme le ferait une équipe d'exploitation, **revenir en arrière** en une commande, puis protéger l'application avec des **sondes de santé** pour que la prochaine erreur ne touche plus les utilisateurs. Les blocs marqués `# TODO` sont à compléter vous-mêmes. Le dossier [`solution/`](solution/) contient la réponse, à n'ouvrir qu'en cas de blocage 😉.
>
> 🎯 **Niveau :** débutant. On suppose le [TP06](../06-configuration/README.md) terminé : l'application complète tourne, `vote` lit ses réglages dans la ConfigMap `vote-config`.
>
> 🧑‍✈️ **En binôme :** le **pilote** tape les commandes, le **copilote** lit la consigne à voix haute et explique ce qu'on observe. **Échangez les rôles à la section 4.**

## ✨ Objectifs

- Déployer une nouvelle version **sans interruption de service** (mise à jour progressive).
- Reconnaître et diagnostiquer les pannes les plus courantes : `CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled`.
- **Revenir en arrière** en une commande, puis remettre le fichier en cohérence.
- Ajouter des **sondes de santé** et comprendre comment elles protègent les utilisateurs.

## 📁 Point de départ

On continue dans le dossier `tp02`, ouvert dans VS Code. Si le tunnel des résultats du TP06 tourne encore dans le terminal 3, arrêtez-le (Ctrl+C) : ce terminal va servir à la surveillance. Voici le rôle de chaque terminal :

| Terminal | Rôle | 🅰️ Local | 🅱️ Cloud |
|---|---|---|---|
| 1 | les commandes | | |
| 2 | la porte d'entrée (page de vote) | `kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8000:80`, puis `http://localhost:8000` | rien à lancer : `https://lab-kubeN-8000.deltavia.com` |
| 3 | la surveillance des pods `vote` | `kubectl get pods -l app=vote --watch` | `kubectl get pods -l app=vote --watch` |

L'option `-l app=vote` de la surveillance limite l'affichage aux pods de `vote`, ceux qui vont changer. Dans le terminal 1, vérifiez que `vote` est en version 1.0 avec 3 réplicas :

```bash
kubectl get deployments vote
```

```
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   3/3     3            3           3h
```

Ouvrez la page de vote : le badge en haut à droite indique **v1.0**.

## 🚀 1 — Déployer la v2 sans coupure

La v2 apporte un nouveau design. Déployer une nouvelle version, c'est **changer l'image** dans l'état souhaité, plus précisément dans le **modèle de pod** (le bloc `template` du Deployment, à partir duquel chaque pod est fabriqué).

🚧 **À compléter :** dans `vote.deploy.yml`, repérez la ligne `image: ghcr.io/bngams/kube-vote:1.0` et changez **seulement les chiffres de la fin** pour passer en version 2.0, puis enregistrez.

```yaml
          image: ghcr.io/bngams/kube-vote:1.0    # TODO : seule la version, après les deux-points, change
```

Appliquez, puis **rechargez sans arrêt la page de vote** pendant une quinzaine de secondes en regardant le badge :

```bash
kubectl apply -f vote.deploy.yml
```

Pendant quelques secondes, la page affiche tantôt **v1.0**, tantôt **v2.0** (avec le nouveau design), puis seulement **v2.0**. À aucun moment elle n'a cessé de répondre. Dans le terminal 3, les pods ont été remplacés **un par un** :

```
NAME                    READY   STATUS              RESTARTS   AGE
vote-66c68b9c99-4pgqv   1/1     Running             0          3h
vote-66c68b9c99-jfztn   1/1     Running             0          3h
vote-66c68b9c99-wbtvj   1/1     Running             0          3h
vote-5cfb967bbd-7z9cf   0/1     Pending             0          0s
vote-5cfb967bbd-7z9cf   0/1     ContainerCreating   0          0s
vote-5cfb967bbd-7z9cf   1/1     Running             0          5s
vote-66c68b9c99-jfztn   1/1     Terminating         0          3h
vote-5cfb967bbd-bm56g   0/1     Pending             0          0s
...
```

Pour suivre une mise à jour jusqu'au bout, Kubernetes propose une commande dédiée. Lancez-la dans le terminal 1 :

```bash
kubectl rollout status deployment vote
```

```
deployment "vote" successfully rolled out
```

> 🧠 **La mise à jour progressive** (*rolling update*). Avec 3 réplicas et les réglages par défaut, Kubernetes crée **un** pod de la nouvelle version, attend qu'il soit prêt, retire **un** pod de l'ancienne, et recommence. Il y a toujours assez de pods pour servir les visiteurs : c'est ce qui permet de livrer en pleine journée, sans « fenêtre de maintenance ». Pendant quelques secondes, les deux versions cohabitent : les équipes de développement doivent en tenir compte (par exemple pour les changements de base de données).

## 📜 2 — L'historique des versions

Au TP03, vous avez vu que chaque modification du modèle de pod créait un nouveau **ReplicaSet** (le « gardien du nombre » de pods, vu au TP02), l'ancien étant gardé à 0 pod. Kubernetes s'en sert comme d'un **historique** :

```bash
kubectl rollout history deployment vote
```

```
deployment.apps/vote
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         <none>
4         <none>
5         <none>
```

Chaque ligne est une **révision**, c'est-à-dire une version du modèle de pod : celles du TP03 (réservations), du TP06 (ConfigMap, puis `rollout restart`) et la v2 que vous venez de déployer. Votre liste peut être plus ou moins longue selon votre parcours ; la dernière ligne est toujours la version en cours. La colonne `CHANGE-CAUSE` est vide : en entreprise, on l'alimente avec une annotation pour savoir **pourquoi** chaque version a été déployée.

## 💥 3 — La v3 plante

L'équipe livre maintenant la v3, qui ajoute un titre personnalisable. Déployez-la comme la v2.

🚧 **À compléter :** dans `vote.deploy.yml`, passez l'image en version `3.0` (même ligne, seuls les chiffres de la fin changent), enregistrez, puis appliquez.

```bash
kubectl apply -f vote.deploy.yml
```

Observez le terminal 3 pendant une minute. Un nouveau pod apparaît, passe brièvement `Running`, puis `Error`, puis `CrashLoopBackOff`, et sa colonne `RESTARTS` augmente. Puis un deuxième pod v3 fait de même. Dans le terminal 1, regardez le résultat :

```bash
kubectl get pods -l app=vote
kubectl get deployments vote
```

```
NAME                    READY   STATUS             RESTARTS      AGE
vote-5587f69d7c-bcqqs   0/1     CrashLoopBackOff   2 (23s ago)   45s
vote-5587f69d7c-pxhdh   0/1     Error              2 (21s ago)   23s
vote-5cfb967bbd-7z9cf   1/1     Running            0             5m
vote-5cfb967bbd-cbh8m   1/1     Running            0             5m

NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   2/3     2            2           3h
```

L'application répond toujours (rechargez la page : **v2.0**), mais il ne reste que **2 pods v2 sur 3** : un pod sain a été retiré ! Si vous attendez plus longtemps, il peut même en disparaître un deuxième. Gardez ce constat en tête, on y reviendra à la section 5.

| Statut | Signification |
|---|---|
| `Error` | le conteneur vient de s'arrêter en erreur |
| `CrashLoopBackOff` | le conteneur plante en boucle. Kubernetes le relance, mais en **attendant de plus en plus longtemps** entre deux essais (10 s, 20 s, 40 s… jusqu'à 5 minutes), pour ne pas épuiser le nœud |

### Diagnostiquer

Face à un pod en échec, on suit toujours la même démarche : **décrire**, puis **lire les logs**. Dans les commandes qui suivent, remplacez le nom du pod par celui de **votre** pod en `CrashLoopBackOff` (copiez-le depuis le terminal 3). Demandez d'abord sa description :

```bash
kubectl describe pod vote-5587f69d7c-bcqqs
```

Parmi les nombreuses lignes, deux passages sont utiles. L'état du conteneur, vers le milieu :

```
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
    Restart Count:  2
```

Et les événements, tout en bas :

```
  Warning  BackOff    8s (x4 over 40s)   kubelet   Back-off restarting failed container vote in pod vote-5587f69d7c-bcqqs_default(…)
```

`describe` confirme que **le conteneur s'arrête en erreur** (code de sortie `1`), mais pas pourquoi. La raison, c'est l'application qui la donne, dans ses **logs** :

```bash
kubectl logs vote-5587f69d7c-bcqqs
```

Si la réponse est vide (le conteneur vient juste de redémarrer), ajoutez l'option `--previous`, qui affiche les logs du conteneur **précédent**, celui qui vient de planter. Sinon, la réponse fait une centaine de lignes, et la **fin** n'est pas très parlante :

```
gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.' 3>
```

La vraie cause se trouve **plus haut**. Remontez dans le terminal, ou ne gardez que les lignes qui contiennent le mot `KeyError` (une erreur fréquente en Python : « clé introuvable »). Sous Windows (PowerShell) :

```bash
kubectl logs vote-5587f69d7c-bcqqs | Select-String KeyError
```

Sous macOS et en mode cloud :

```bash
kubectl logs vote-5587f69d7c-bcqqs | grep KeyError
```

Le terminal affiche la même ligne, deux fois (une par processus de l'application) :

```
KeyError: 'VOTE_TITLE'
KeyError: 'VOTE_TITLE'
```

Voilà le coupable : la v3 attend un réglage `VOTE_TITLE` que personne ne lui a donné. C'est le titre personnalisable annoncé par l'équipe, mais elle a oublié de le dire à l'exploitation.

> 🗣️ **En réunion projet.** Vous savez maintenant ce que signifie « *le pod est en CrashLoopBackOff* » : l'application plante au démarrage, Kubernetes la relance en boucle. Ce n'est **pas** un problème de Kubernetes, mais de l'application ou de sa configuration. Et la première question à poser est : « *qu'est-ce que disent les logs ?* »

## ⏪ 4 — Revenir en arrière

🔄 **Échangez les rôles** : le copilote devient pilote.

En production, quand une nouvelle version pose problème, la priorité est de **rétablir le service**, avant même de corriger le bug. Kubernetes garde l'historique : revenir à la révision précédente tient en une commande.

```bash
kubectl rollout undo deployment vote
kubectl rollout status deployment vote
```

```
deployment.apps/vote rolled back
deployment "vote" successfully rolled out
```

En mode cloud (et avec les versions récentes de `kubectl`), la première ligne est précédée d'un avertissement : `Warning: resource deployments/vote was previously managed with 'kubectl apply'. Rolling back will not update the kubectl.kubernetes.io/last-applied-configuration annotation…`. Kubernetes vous prévient lui-même du problème expliqué juste après.

> ⚠️ **Une seule fois !** Lancez `kubectl rollout undo` **une seule fois** : un second `undo` reviendrait à la révision d'avant… c'est-à-dire la v3 cassée. En cas de doute, `kubectl rollout history deployment vote` montre où vous en êtes.

Dans le terminal 3, les pods v3 disparaissent et un troisième pod v2 est recréé. Vérifiez :

```bash
kubectl get deployments vote
```

```
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   3/3     3            3           3h
```

Retour à 3 pods sains en v2, en quelques secondes.

> ⚠️ **Le fichier ne fait plus foi !** `kubectl rollout undo` a modifié le cluster **sans toucher à votre fichier** : `vote.deploy.yml` indique toujours `3.0`. C'est la même dérive qu'avec `kubectl scale` au TP03. Au prochain `kubectl apply`, la v3 cassée reviendrait.

🚧 **À compléter :** remettez le fichier en cohérence avec le cluster : repassez l'image en version `2.0`, celle qui tourne réellement, enregistrez, puis appliquez (le terminal répond `configured`, mais rien ne change puisque le cluster est déjà en v2).

```bash
kubectl apply -f vote.deploy.yml
```

> 🗣️ **En réunion projet.** « *On a fait un rollback* » : on est revenu à la version précédente. C'est un geste normal, qui doit être **rapide** (quelques secondes ici) et **prévu à l'avance**. La question à poser avant chaque mise en production : « *comment revient-on en arrière si ça se passe mal ?* ». Attention toutefois : on ne revient facilement en arrière que sur le **code** ; si la nouvelle version a modifié des données, c'est une autre histoire.

## 🩺 5 — Les sondes de santé

Revenons au constat de la section 3 : pendant la mise à jour vers la v3, Kubernetes a **retiré un pod sain** alors que les nouveaux pods plantaient. Pourquoi ? Parce qu'il les a crus **prêts** : sans autre information, un pod est considéré comme prêt dès que son conteneur démarre… une fraction de seconde avant que la v3 ne plante. La mise à jour a donc continué sur une version cassée.

Pour éviter cela, on donne à Kubernetes un moyen de vérifier lui-même la santé de l'application : des **sondes** (*probes*). Notre application a justement une page prévue pour cela, `/healthz`, qui répond `ok` quand tout va bien.

| Sonde | Question posée régulièrement | Si la réponse est non |
|---|---|---|
| `readinessProbe` (**prêt ?**) | « peux-tu recevoir des visiteurs ? » | le pod est **retiré du Service** (il ne reçoit plus de visiteurs) et, pendant une mise à jour, il n'est **pas compté comme prêt** : la mise à jour attend |
| `livenessProbe` (**vivant ?**) | « es-tu encore en vie ? » | Kubernetes **redémarre** le conteneur (utile si l'application est bloquée sans avoir planté) |

🚧 **À compléter :** dans `vote.deploy.yml`, ajoutez les deux sondes **entre** le bloc `envFrom` et la ligne `resources:`, au même niveau qu'eux (10 espaces avant `readinessProbe:`), puis enregistrez.

```yaml
          envFrom:
            - configMapRef:
                name: vote-config
          readinessProbe:          # <- nouveau bloc : "es-tu prêt ?"
            httpGet:
              path: # TODO : la page de santé de l'application
              port: 80
            periodSeconds: 5       # toutes les 5 secondes
          livenessProbe:           # <- nouveau bloc : "es-tu vivant ?"
            httpGet:
              path: # TODO : la même page
              port: 80
            periodSeconds: 10      # toutes les 10 secondes
          resources:
            requests:
              cpu: 100m
              memory: 64Mi
```

Comme pour `envFrom` au TP06 : placez le curseur au tout début de la ligne `resources:` (colonne 1), appuyez **dix fois** sur Entrée pour créer dix lignes vides au-dessus, puis tapez les dix lignes du bloc en respectant les espaces. Les commentaires `# <-` et `# toutes les…` sont facultatifs.

Appliquez, puis vérifiez que les sondes sont en place :

```bash
kubectl apply -f vote.deploy.yml
kubectl rollout status deployment vote
kubectl describe pod -l app=vote
```

L'option `-l app=vote` décrit tous les pods de `vote` d'un coup. Dans la réponse, repérez ces deux lignes (une fois par pod) :

```
    Liveness:   http-get http://:80/healthz delay=0s timeout=1s period=10s #success=1 #failure=3
    Readiness:  http-get http://:80/healthz delay=0s timeout=1s period=5s #success=1 #failure=3
```

`#failure=3` : il faut **3 échecs de suite** pour que Kubernetes réagisse, ce qui évite de redémarrer un conteneur pour un simple ralentissement passager.

### La v3, avec les sondes

Rejouez maintenant l'erreur de la section 3 : repassez l'image en `3.0`, enregistrez, appliquez, et observez une minute.

```bash
kubectl apply -f vote.deploy.yml
kubectl get pods -l app=vote
kubectl get deployments vote
```

```
NAME                    READY   STATUS             RESTARTS      AGE
vote-544f44c7b6-6kz4p   1/1     Running            0             51s
vote-544f44c7b6-h97w8   1/1     Running            0             53s
vote-544f44c7b6-nhn6c   1/1     Running            0             52s
vote-5f6bf777c7-h2hdk   0/1     CrashLoopBackOff   2 (20s ago)   45s

NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   3/3     1            3           3h
```

Cette fois, **les 3 pods v2 sont intacts** (`3/3`) : le pod v3 n'a jamais répondu à la sonde de *readiness*, il n'a donc jamais été compté comme prêt, et la mise à jour s'est arrêtée là. Les utilisateurs ne voient rien. Il ne reste qu'à revenir en arrière, une seule fois :

```bash
kubectl rollout undo deployment vote
```

> ⚠️ **Cette fois, laissez `3.0` dans le fichier.** Le cluster est revenu en v2, mais on va réparer la v3 à la section suivante : votre fichier est déjà prêt pour cela.

> 🧠 **Les sondes sont le filet de sécurité des mises à jour.** Sans elles, Kubernetes ne sait qu'une chose : « le programme a démarré ». Avec elles, il sait « l'application répond correctement ». C'est l'une des premières choses à vérifier dans un projet : *nos applications ont-elles des sondes de santé ?*

## 🔧 6 — Corriger la v3 pour de bon

Le service est rétabli, il reste à livrer la v3 **correctement**. Le diagnostic l'a montré : la v3 a besoin d'un réglage `VOTE_TITLE`. Vous savez où ranger un réglage depuis le TP06 : dans la ConfigMap.

🚧 **À compléter :** dans `vote.config.yml`, gardez vos deux options telles quelles et ajoutez une ligne `VOTE_TITLE` en dessous (au même niveau qu'elles), avec le titre de votre choix entre guillemets, puis enregistrez.

```yaml
data:
  OPTION_A: …          # vos options du TP06, inchangées
  OPTION_B: …
  VOTE_TITLE: # TODO : un titre entre guillemets, par exemple "Votre destination de vacances ?"
```

Appliquez la ConfigMap **d'abord**, puis la v3 (votre fichier `vote.deploy.yml` indique `3.0` depuis la section 5, mais le cluster est revenu en v2 avec le `undo`) :

```bash
kubectl apply -f vote.config.yml
kubectl apply -f vote.deploy.yml
kubectl rollout status deployment vote
```

```
configmap/vote-config configured
deployment.apps/vote configured
deployment "vote" successfully rolled out
```

Rechargez la page : badge **v3.0**, et votre titre en haut de la page. La v3 était donc saine : il lui manquait seulement sa configuration. Le fichier et le cluster sont cohérents (tous deux en `3.0`).

> 🗣️ **En réunion projet.** Ce scénario est un grand classique : une nouvelle version exige un nouveau réglage, et le réglage n'a pas été livré avec. D'où l'intérêt de livrer **ensemble** le code et sa configuration, et de décrire les réglages requis dans les notes de version.

## 🧪 7 — Deux pannes express

Pour compléter votre catalogue, provoquez deux autres pannes très courantes. Grâce aux sondes, aucune ne touchera les utilisateurs. Pour chacune : modifiez le fichier, appliquez, observez **une minute**, lisez la cause, puis annulez avec `kubectl rollout undo deployment vote` (une seule fois) **et remettez le fichier dans son état de référence** : version `3.0`, sondes en place, réservation de mémoire à `64Mi`, pas de bloc `limits`. Inutile de réappliquer ensuite : le cluster est déjà revenu en arrière.

**Panne 1 — une image introuvable.** Passez l'image en version `4.0`, qui n'existe pas.

```
NAME                    READY   STATUS             RESTARTS   AGE
vote-6d8b4d6c9f-8t6z9   0/1     ImagePullBackOff   0          25s
```

Le statut passe d'abord par `ErrImagePull`, puis `ImagePullBackOff` (Kubernetes réessaie, en espaçant les tentatives). `kubectl describe pod <nom-du-pod>` en donne la cause, tout en bas : `Failed to pull image "ghcr.io/bngams/kube-vote:4.0": … manifest unknown`. L'image n'existe pas dans le registre : une faute de frappe dans la version, ou une image pas encore publiée. Annulez, puis remettez `3.0` dans le fichier.

**Panne 2 — trop peu de mémoire.** Dans le bloc `resources`, donnez au conteneur une **limite** de mémoire trop basse pour lui. Une limite ne peut pas être inférieure à la réservation : baissez aussi la réservation.

```yaml
          resources:
            requests:
              cpu: 100m
              memory: 16Mi      # <- réservation baissée (était 64Mi)
            limits:             # <- nouveau : un plafond…
              memory: 20Mi      # <- … bien trop bas pour l'application
```

```
NAME                    READY   STATUS             RESTARTS      AGE
vote-6b7d5b679-npmvv    0/1     CrashLoopBackOff   2 (15s ago)   41s
```

Selon l'instant, la colonne `STATUS` affiche `OOMKilled` ou `CrashLoopBackOff`. Dans les deux cas, `kubectl describe pod <nom-du-pod>` révèle la cause :

```
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
```

*OOM* signifie *Out Of Memory* : l'application a dépassé son plafond de mémoire, et le système l'a arrêtée net. Il faut alors relever la limite, ou chercher pourquoi l'application consomme autant.

N'oubliez pas, après chaque panne : `kubectl rollout undo deployment vote`, puis remettez `vote.deploy.yml` comme il était (version `3.0`, sans bloc `limits`, réservation à `64Mi`).

### Le catalogue des pannes

Voici les statuts rencontrés pendant la formation, à garder sous la main :

| Statut | Ce qui se passe | Où chercher | Vu au |
|---|---|---|---|
| `Pending` | le pod attend une place sur un nœud | `kubectl describe pod` (événements) | TP03 |
| `CreateContainerConfigError` | une ConfigMap ou un Secret attendu est introuvable | `kubectl describe pod` | TP06 |
| `ImagePullBackOff` / `ErrImagePull` | l'image ne peut pas être téléchargée (nom, version, droits d'accès) | `kubectl describe pod` | TP07 |
| `CrashLoopBackOff` | l'application plante au démarrage, en boucle | `kubectl logs` (et `--previous`) | TP07 |
| `OOMKilled` | l'application a dépassé sa limite de mémoire (souvent visible dans `Last State` plutôt que dans `STATUS`) | `kubectl describe pod` (`Last State`) | TP07 |
| `Running` mais `0/1` | l'application tourne, mais sa sonde de *readiness* échoue | `kubectl describe pod` (événements `Unhealthy`) | TP07, « Pour aller plus loin » |

> 📖 [Mettre à jour un Deployment](https://kubernetes.io/fr/docs/concepts/workloads/controllers/deployment/#mise-%C3%A0-jour-d-un-d%C3%A9ploiement) · [Sondes de santé](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) · [Déboguer un pod](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)

## 🔵 Pour aller plus loin

Ces pistes sont facultatives.

- **Revenir à une révision précise :** listez l'historique (`kubectl rollout history deployment vote`), examinez une révision avec `kubectl rollout history deployment vote --revision=N` (remplacez `N` par son numéro), puis `kubectl rollout undo deployment vote --to-revision=N` y revient directement. Kubernetes ne garde que les 10 dernières révisions. Pensez ensuite à remettre le fichier en cohérence.
- **Documenter les versions :** juste après un `apply`, `kubectl annotate deployment vote kubernetes.io/change-cause="passage en v3 avec titre"` remplit la colonne `CHANGE-CAUSE` de l'historique pour la révision en cours. Attention : la même cause sera recopiée sur les révisions suivantes tant que vous ne la changez pas.
- **Régler la mise à jour progressive :** dans `vote.deploy.yml`, sous `spec:` (au même niveau que `replicas`), ajoutez le bloc suivant pour aller plus vite (`maxSurge` : combien de pods en plus pendant la mise à jour) ou plus prudemment (`maxUnavailable` : combien de pods en moins) :

  ```yaml
    strategy:
      rollingUpdate:
        maxSurge: 1
        maxUnavailable: 0
  ```
- **Une sonde qui échoue :** changez le `path` de la `readinessProbe` en `/nexistepas`, appliquez, et observez : les nouveaux pods restent `Running` mais `0/1`, et la mise à jour s'arrête. `kubectl describe pod` montre des événements `Unhealthy`. Annulez ensuite.

## 🎉 Challenge final

- [ ] La v2 a été déployée sans que la page cesse de répondre.
- [ ] Nous avons trouvé la cause de la panne de la v3 dans les logs (`KeyError: 'VOTE_TITLE'`).
- [ ] Nous sommes revenus en arrière avec `kubectl rollout undo`, puis nous avons remis le fichier en cohérence.
- [ ] Avec les sondes, la v3 cassée n'a retiré aucun pod sain.
- [ ] La v3 tourne avec notre titre, lu dans la ConfigMap.
- [ ] Nous avons provoqué et identifié un `ImagePullBackOff` et un `OOMKilled`.
- [ ] À la fin, `vote.deploy.yml` (version `3.0`, avec les sondes) correspond exactement à ce qui tourne.

Arrêtez la surveillance (Ctrl+C dans le terminal 3). Laissez l'application en place pour le TP08.

## Récap

- Changer l'image dans le fichier suffit à déployer une nouvelle version : Kubernetes fait une **mise à jour progressive**, sans coupure.
- Face à une panne : **`describe`** pour l'état et les événements, **`logs`** pour la cause côté application.
- **`kubectl rollout undo`** rétablit la version précédente en quelques secondes. Ensuite, on remet le **fichier** en cohérence.
- Les **sondes** (*readiness*, *liveness*) disent à Kubernetes si l'application va vraiment bien. Sans elles, une version cassée peut remplacer des pods sains.
- `CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled` : vous savez maintenant ce que ces mots veulent dire, et où chercher.

➡️ Suite : [08 — Mission finale](../08-mission-finale/README.md)
