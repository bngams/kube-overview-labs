# 03 — Passer à l'échelle : plusieurs exemplaires

> **Scénario à réaliser en binôme.** Au TP02, Kubernetes maintenait **un** exemplaire de `vote` en vie. Vous allez maintenant lui en demander plusieurs, les supprimer tous d'un coup, découvrir pourquoi « le fichier fait foi », éteindre l'application sans la supprimer, et voir ce qui se passe quand le cluster n'a plus de place. Les blocs marqués `# TODO` sont à compléter vous-mêmes. Le dossier [`solution/`](solution/) contient la réponse, à n'ouvrir qu'en cas de blocage 😉.
>
> 🎯 **Niveau :** débutant. On suppose le [TP02](../02-premier-deployment/README.md) terminé : vous savez écrire et appliquer `vote.deploy.yml`, et vous connaissez les notions de pod, de Deployment et de réconciliation.
>
> 🧑‍✈️ **En binôme :** le **pilote** tape les commandes, le **copilote** lit la consigne à voix haute et explique ce qu'on observe. **Échangez les rôles à la section 5.**

## ✨ Objectifs

- Faire passer une application de 1 à plusieurs exemplaires, puis à 0, en modifiant l'état souhaité.
- Comprendre pourquoi on modifie le **fichier** plutôt que de taper une commande de raccourci.
- Voir où Kubernetes place les pods, et ce qui se passe quand il n'y a plus de place.
- Découvrir les **réservations de ressources** (*requests*), base de la gestion de capacité et des coûts.

## 📁 Point de départ

On continue dans le dossier `tp02` du TP précédent, avec le même fichier `vote.deploy.yml`. Ouvrez VS Code sur ce dossier (**Fichier > Ouvrir le dossier…** > `tp02`, si ce n'est pas déjà le cas), puis ouvrez un terminal : ce sera le **terminal 1**, celui des commandes.

Vérifiez que le Deployment du TP02 est toujours là :

```bash
kubectl get deployments
```

Le terminal doit afficher `vote` avec `READY 1/1` :

```
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   1/1     1            1           25m
```

Si le terminal répond `No resources found`, remettez-le en place avec `kubectl apply -f vote.deploy.yml`. Si vous voyez `3/3` (vous aviez essayé la dernière piste « Pour aller plus loin » du TP02), remettez `replicas: 1` dans le fichier, enregistrez, puis lancez `kubectl apply -f vote.deploy.yml`. Si la commande échoue avec `connection refused`, votre cluster est arrêté : relancez-le comme au TP00 (`minikube start` ou `k3d cluster start tp`).

Ouvrez enfin un **terminal 2** avec l'icône **Scinder le terminal**, et lancez-y la surveillance des pods. Laissez-la tourner pendant tout le TP :

```bash
kubectl get pods --watch
```

> 💡 Au bout d'un long moment, la surveillance peut s'arrêter d'elle-même (l'invite de commande réapparaît). Relancez-la simplement : flèche ↑ puis Entrée. Si elle devient trop longue à lire, cliquez dans le terminal 2, faites Ctrl+C, puis relancez-la.

## 📈 1 — Demander 3 exemplaires

Pour avoir 3 exemplaires de `vote`, il suffit de **changer l'état souhaité** : c'est le champ `replicas` du fichier.

🚧 **À compléter :** dans `vote.deploy.yml`, repérez la ligne `replicas: 1`, vers le haut du fichier, sous le premier `spec:`. Remplacez **seulement le chiffre** pour demander 3 exemplaires, puis enregistrez (Ctrl+S). La ligne devient :

```yaml
  replicas: # TODO : 3 exemplaires
```

Transmettez le nouvel état souhaité au cluster, depuis le terminal 1 :

```bash
kubectl apply -f vote.deploy.yml
```

Cette fois, le terminal ne dit plus `created`, mais `configured` : le Deployment existait déjà, il a été **mis à jour**.

```
deployment.apps/vote configured
```

Regardez le terminal 2 : deux nouveaux pods apparaissent et passent par `Pending`, `ContainerCreating`, puis `Running`. Le premier pod, lui, n'a pas bougé.

```
NAME                    READY   STATUS              RESTARTS   AGE
vote-644d47956b-p8djv   1/1     Running             0          25m
vote-644d47956b-8cxb4   0/1     Pending             0          0s
vote-644d47956b-8q22g   0/1     Pending             0          0s
vote-644d47956b-8cxb4   0/1     ContainerCreating   0          0s
vote-644d47956b-8q22g   0/1     ContainerCreating   0          0s
vote-644d47956b-8q22g   1/1     Running             0          1s
vote-644d47956b-8cxb4   1/1     Running             0          1s
```

Vérifiez le résultat dans le terminal 1 :

```bash
kubectl get deployments
```

```
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   3/3     3            3           25m
```

> 🧠 **Ce qui vient de se passer.** C'est la **même boucle de réconciliation** qu'au TP02. Kubernetes a comparé l'état souhaité (3) avec la réalité (1), constaté qu'il en manquait 2, et les a créés. Vous n'avez pas dit « crée 2 pods », vous avez dit « je veux 3 pods » : c'est à lui de calculer ce qu'il faut faire.
>
> Les trois pods ont le même début de nom, `vote-644d47956b-` : ils sont fabriqués par **le même ReplicaSet**, à partir du même modèle. Ce sont des **réplicas**, des copies identiques et interchangeables.

## 🎯 2 — Qui répond ?

Trois exemplaires tournent. Mais lequel répond quand on ouvre l'application ? Ouvrez un **terminal 3** (icône **Scinder le terminal**) et créez le tunnel comme au TP02 :

```bash
kubectl port-forward deployment/vote 8080:80
```

Ouvrez l'application (`http://localhost:8080` en local, `https://lab-kubeN-8080.deltavia.com` en cloud, en remplaçant `N` par votre numéro de session ; le mot de passe peut vous être redemandé), puis rechargez la page plusieurs fois en regardant la ligne « Servi par ».

C'est **toujours le même pod** qui répond. `kubectl port-forward` choisit un pod au démarrage et s'y branche : les deux autres tournent, mais ne reçoivent aucun visiteur.

> 💡 **Il manque un répartiteur.** Pour que les visiteurs soient répartis entre les réplicas, il faut placer devant eux un **Service** : une adresse unique qui distribue les requêtes à tous les pods portant l'étiquette `app: vote`. C'est l'objet du TP04, où vous verrez le nom du pod changer d'un rechargement à l'autre.

Arrêtez le tunnel (**Ctrl+C** dans le terminal 3). Vous n'en aurez plus besoin dans ce TP.

## 💥 3 — Panne générale

Au TP02, vous avez supprimé **un** pod. Que se passe-t-il si **tous** les pods disparaissent en même temps, comme lors d'une grosse panne ? Plutôt que de copier trois noms, on va désigner les pods par leur **étiquette** :

```bash
kubectl delete pods -l app=vote
```

| Élément | Rôle |
|---|---|
| `delete pods` | supprimer des pods |
| `-l app=vote` | … tous ceux qui portent l'étiquette (*label*) `app: vote`, quel que soit leur nom. C'est le même post-it que celui utilisé par le Deployment pour reconnaître ses pods |

La commande liste les pods supprimés, puis rend la main au bout d'une dizaine de secondes, le temps que les applications s'arrêtent proprement :

```
pod "vote-644d47956b-8cxb4" deleted from default namespace
pod "vote-644d47956b-8q22g" deleted from default namespace
pod "vote-644d47956b-p8djv" deleted from default namespace
```

Dans le terminal 2, trois nouveaux pods sont apparus pendant que les anciens s'arrêtaient. Vérifiez dans le terminal 1 :

```bash
kubectl get pods
```

```
NAME                    READY   STATUS    RESTARTS   AGE
vote-644d47956b-6wbsl   1/1     Running   0          12s
vote-644d47956b-kgwrc   1/1     Running   0          12s
vote-644d47956b-pp95p   1/1     Running   0          12s
```

Trois pods, trois nouveaux noms : l'état souhaité est de nouveau respecté.

## ✂️ 4 — Le raccourci… et ses dangers

Modifier un fichier puis l'appliquer, c'est un peu long. Il existe un raccourci qui change directement le nombre de réplicas :

```bash
kubectl scale deployment vote --replicas=5
```

Le terminal confirme avec `deployment.apps/vote scaled`. Quelques secondes plus tard, vérifiez :

```bash
kubectl get deployments
```

```
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   5/5     5            5           38m
```

Si vous voyez `3/5` ou `4/5`, les nouveaux pods démarrent encore : relancez la commande. Ça fonctionne : 5 pods tournent. Mais ouvrez `vote.deploy.yml` : il indique toujours `replicas: 3`. **Le cluster et le fichier ne disent plus la même chose.** Imaginez maintenant qu'un collègue applique ce fichier demain, pour une toute autre raison. Jouez ce collègue : dans le terminal 1, lancez

```bash
kubectl apply -f vote.deploy.yml
kubectl get deployments
```

```
deployment.apps/vote configured
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   3/3     3            3           39m
```

Dans le terminal 2, deux pods passent en `Terminating`. Retour à 3 réplicas : le changement fait avec `kubectl scale` a été **effacé sans prévenir**. Kubernetes a simplement appliqué le dernier état souhaité qu'on lui a transmis.

> 🧠 **Le fichier fait foi.** En entreprise, les fichiers YAML sont rangés dans un outil de gestion de versions (Git) : on sait qui a changé quoi, quand et pourquoi, et l'on peut revenir en arrière. Certaines équipes vont jusqu'à interdire les modifications directes : un outil applique automatiquement ce qui est dans Git (c'est le principe du **GitOps**).
>
> ⚖️ `kubectl scale` reste utile en urgence, par exemple pour absorber un pic de visiteurs. Mais il faut **reporter ensuite la valeur dans le fichier**, sinon elle sera perdue au prochain `apply`.

## 🌙 5 — Éteindre sans supprimer

🔄 **Échangez les rôles** : le copilote devient pilote.

Au TP02, vous avez arrêté l'application en supprimant le Deployment. Il existe une solution plus douce : demander **zéro** réplica. Le Deployment reste alors en place dans le cluster, avec ses réglages et l'historique de ses versions, et les autres objets qui pointent vers lui (comme le Service du TP04) continuent de fonctionner. Pour rallumer, il suffit de changer un chiffre.

🚧 **À compléter :** dans `vote.deploy.yml`, la ligne indique `replicas: 3`. Remplacez le chiffre pour ne demander aucun exemplaire, enregistrez, puis appliquez.

```yaml
  replicas: # TODO : aucun exemplaire
```

```bash
kubectl apply -f vote.deploy.yml
kubectl get deployments
```

Le Deployment affiche aussitôt `0/0` :

```
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   0/0     0            0           40m
```

Dans le terminal 2, les trois pods passent en `Terminating`. Une dizaine de secondes plus tard, vérifiez :

```bash
kubectl get pods
```

```
No resources found in default namespace.
```

Plus aucun pod ne tourne, mais le Deployment est **toujours là**.

🚧 **À compléter :** rallumez l'application en remettant `3` dans la ligne `replicas`, enregistrez, puis appliquez de nouveau. Quelques secondes plus tard, `kubectl get deployments` doit afficher `3/3`.

> 🗣️ **En réunion projet.** « *On éteint les environnements de recette le soir et le week-end* » : c'est souvent exactement cela, des réplicas à 0. Dans le cloud, on paie les serveurs à l'heure : moins de pods, c'est moins de serveurs nécessaires, donc une facture plus légère, à condition que le cluster retire les serveurs devenus inutiles (beaucoup de clouds savent le faire automatiquement). Le lundi matin, on remet les réplicas, et tout redémarre à l'identique.

## 🗺️ 6 — Où tournent les pods ?

Un cluster Kubernetes est fait de plusieurs serveurs, les **nœuds**. Demandez à voir sur quel nœud tourne chaque pod, avec l'option `-o wide` (*output wide*, un affichage plus large) :

```bash
kubectl get pods -o wide
```

```
NAME                    READY   STATUS    RESTARTS   AGE   IP            NODE      NOMINATED NODE   READINESS GATES
vote-644d47956b-dzpr5   1/1     Running   0          5s    10.244.0.13   minikube   <none>           <none>
vote-644d47956b-h7jx2   1/1     Running   0          5s    10.244.0.11   minikube   <none>           <none>
vote-644d47956b-x7pcf   1/1     Running   0          5s    10.244.0.12   minikube   <none>           <none>
```

Cet exemple vient du mode local : en mode cloud, le nœud s'appelle `k3d-tp-server-0` et les adresses commencent par `10.42.`. Ignorez les deux dernières colonnes, qui servent à des cas avancés.

| Colonne | Ce qu'elle dit |
|---|---|
| `IP` | l'adresse du pod dans le réseau interne du cluster. Chaque pod a la sienne |
| `NODE` | le nœud sur lequel il tourne : `minikube` en local, `k3d-tp-server-0` en cloud |

Vos trois pods sont sur **le même nœud**, puisque votre cluster d'apprentissage n'en a qu'un.

> 🧠 **Sur un vrai cluster**, il y a plusieurs nœuds, souvent répartis dans plusieurs salles ou zones. Un composant de Kubernetes, l'**ordonnanceur** (*scheduler*), choisit pour chaque nouveau pod le nœud le plus adapté, et essaie par défaut de répartir les réplicas plutôt que de tout mettre au même endroit. Si un nœud tombe en panne, ses pods sont recréés sur les nœuds restants au bout de quelques minutes : c'est la même réconciliation qu'à la section 3, à l'échelle d'un serveur entier. C'est pour cela qu'on demande **au moins 2 ou 3 réplicas** pour une application importante : un seul réplica, c'est un seul point de panne.

## 🧱 7 — Quand il n'y a plus de place

Un nœud n'a pas des ressources infinies. Pour que l'ordonnanceur puisse bien placer les pods, chaque conteneur peut **réserver** une part de processeur (CPU) et de mémoire : ce sont les **requests**. Un pod n'est placé sur un nœud que si la somme des réservations déjà faites sur ce nœud lui laisse assez de place, **même si le nœud est en réalité peu utilisé** : l'ordonnanceur compte les réservations, pas la consommation réelle.

Les deux ressources se mesurent ainsi :

| Ressource | Unité | Exemples |
|---|---|---|
| `cpu` | en processeurs. `1` = un processeur entier, `100m` = un dixième de processeur (*m* pour millième) | `2`, `500m`, `100m` |
| `memory` | en octets, avec un suffixe. `Mi` = mébioctet, environ un million d'octets | `64Mi`, `512Mi`, `1Gi` |

Faisons une expérience : demandons des pods **démesurés**, qui réservent chacun **64 processeurs**. Aucun nœud de vos clusters d'apprentissage n'est aussi gros.

🚧 **À compléter :** dans `vote.deploy.yml`, vous allez ajouter **4 lignes** à la toute fin du fichier, après la ligne `- containerPort: 80`. Voici où elles se placent (les lignes existantes sont reprises pour vous repérer) :

```yaml
          ports:
            - containerPort: 80
          resources:              # <- nouvelle ligne
            requests:             # <- nouvelle ligne
              cpu: # TODO : 64 processeurs, écrit simplement 64
              memory: 64Mi        # <- nouvelle ligne
```

Pour éviter les pièges d'indentation : placez le curseur à la fin de la ligne `- containerPort: 80`, appuyez sur Entrée, puis **effacez tous les espaces** que VS Code ajoute automatiquement, pour être en tout début de ligne. Tapez alors les 4 lignes avec leurs espaces : `resources:` commence **exactement sous le `p` de `ports:`** (10 espaces), `requests:` a 2 espaces de plus, `cpu` et `memory` encore 2 de plus. Enregistrez.

| Message d'erreur au moment du `apply` | Cause probable |
|---|---|
| `did not find expected key` | un décalage d'indentation dans les nouvelles lignes |
| un long message illisible qui se termine par `strict decoding error: unknown field "spec.template.spec.containers[0].ports[0].resources"` | `resources:` est trop décalé vers la droite, sous `containerPort` au lieu de `ports` |

Appliquez, puis observez :

```bash
kubectl apply -f vote.deploy.yml
kubectl get pods
```

```
NAME                    READY   STATUS    RESTARTS   AGE
vote-584fbb796-wgswp    0/1     Pending   0          6s
vote-644d47956b-dzpr5   1/1     Running   0          25s
vote-644d47956b-h7jx2   1/1     Running   0          25s
vote-644d47956b-x7pcf   1/1     Running   0          25s
```

Deux choses se passent à la fois :

- **Un nouveau pod reste bloqué en `Pending`** : Kubernetes ne trouve aucun nœud assez grand pour lui. Le pod ne disparaît pas : il attend qu'une place se libère, ou qu'on ajoute un nœud.
- **Les trois anciens pods tournent toujours.** Modifier le modèle de pod revient à demander une **nouvelle version** de l'application. Kubernetes la déploie progressivement : avec ses réglages par défaut et 3 réplicas, il ne retire un ancien pod qu'une fois un nouveau prêt. Puisque le nouveau ne démarre pas, il garde les anciens : **l'application reste disponible**. Vous étudierez ce mécanisme, la *mise à jour progressive*, au TP06.

Le Deployment résume la situation :

```bash
kubectl get deployments
```

```
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
vote   3/3     1            3           44m
```

`READY 3/3` : trois pods servent toujours les visiteurs. `UP-TO-DATE 1` : un seul pod correspond à la nouvelle version demandée, et c'est celui qui attend. Au bout de 10 minutes, Kubernetes finira par signaler que la mise à jour n'avance pas, mais sans toucher aux pods qui fonctionnent.

Demandez à Kubernetes pourquoi le pod est bloqué. Copiez le nom de **votre** pod `Pending` (son début diffère des autres) :

```bash
kubectl describe pod vote-584fbb796-wgswp
```

Tout en bas, la section `Events` donne la raison :

```
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  6s    default-scheduler  0/1 nodes are available: 1 Insufficient cpu. ...
```

« *0 nœud disponible sur 1 : processeur insuffisant* ». Le message vient du `default-scheduler`, l'ordonnanceur de la section 6.

🚧 **À compléter :** corrigez la réservation avec une valeur réaliste pour notre petite application, un dixième de processeur. Dans le fichier, la ligne `cpu: 64` devient :

```yaml
              cpu: # TODO : un dixième de processeur, écrit 100m
```

Enregistrez, puis appliquez :

```bash
kubectl apply -f vote.deploy.yml
kubectl get pods
```

Kubernetes remplace les pods un par un : pendant quelques secondes, vous verrez des nouveaux pods `Running` à côté d'anciens `Terminating`. Relancez `kubectl get pods` jusqu'à ce qu'il ne reste que trois pods, tous avec un **nouveau début de nom** :

```
NAME                  READY   STATUS    RESTARTS   AGE
vote-fc57495c-27sbz   1/1     Running   0          10s
vote-fc57495c-9vtsj   1/1     Running   0          11s
vote-fc57495c-fqk5b   1/1     Running   0          12s
```

Pour comprendre ce changement de nom, listez les ReplicaSets :

```bash
kubectl get replicasets
```

```
NAME              DESIRED   CURRENT   READY   AGE
vote-584fbb796    0         0         0       2m
vote-644d47956b   0         0         0       45m
vote-fc57495c     3         3         3       1m
```

Chaque modification du modèle de pod a créé un **nouveau ReplicaSet** : `644d47956b` pour la version d'origine, `584fbb796` pour la version à 64 processeurs (jamais démarrée), `fc57495c` pour la version actuelle. Les anciens sont gardés à 0 : ils serviront à **revenir en arrière** au TP06. Remarquez qu'aux sections 1, 4 et 5, changer seulement le nombre de `replicas` n'avait **pas** créé de nouveau ReplicaSet : le modèle de pod n'avait pas changé, c'est le même ReplicaSet qui ajoutait ou retirait des pods.

> 🗣️ **En réunion projet.** Les *requests* sont la base du **dimensionnement** et des **coûts** : la somme des réservations dit combien de nœuds il faut, donc combien de serveurs payer. Un pod `Pending` en production signifie souvent « le cluster est plein » : il faut alors ajouter des nœuds (beaucoup de clouds le font automatiquement), ou revoir les réservations à la baisse.
>
> 📖 [Gestion des ressources des conteneurs](https://kubernetes.io/fr/docs/concepts/configuration/manage-resources-containers/)

## 🔵 Pour aller plus loin

Ces pistes sont facultatives.

- **Les vraies consommations :** `kubectl top pods` affiche le processeur et la mémoire réellement utilisés par chaque pod, à comparer aux réservations. En mode cloud, cela fonctionne directement. En mode local, activez d'abord le module de mesure avec `minikube addons enable metrics-server`. Dans les deux cas, si la commande répond `metrics not available yet`, attendez une minute et relancez-la.
- **Le passage à l'échelle automatique :** `kubectl autoscale deployment vote --cpu=50% --min=2 --max=6` crée un *HorizontalPodAutoscaler*, qui ajuste lui-même le nombre de réplicas selon la charge (il a besoin des *requests* de la section 7 pour calculer un pourcentage). En mode local, il a lui aussi besoin du module `metrics-server` (sinon la colonne `TARGETS` affiche `<unknown>`). Observez-le avec `kubectl get hpa`, puis supprimez-le avec `kubectl delete hpa vote` : sinon, il continuerait à décider du nombre de réplicas à la place de votre fichier. Comme l'application est peu sollicitée, il a pu réduire les réplicas à 2 : relancez `kubectl apply -f vote.deploy.yml` pour revenir à 3.
- **Une limite en plus de la réservation :** à côté de `requests`, le champ `limits` fixe un **plafond** que le conteneur ne peut pas dépasser. Un conteneur qui dépasse sa limite de mémoire est arrêté (`OOMKilled`). Vous le croiserez au TP06.
- **Mode cloud uniquement :** lancez `k9s` et tapez `:deploy` puis Entrée pour voir vos Deployments, ou `:rs` pour les ReplicaSets.

## 🎉 Challenge final

- [ ] `vote` est passé de 1 à 3 réplicas en modifiant le fichier.
- [ ] Après la suppression de tous les pods avec `-l app=vote`, trois nouveaux sont apparus.
- [ ] Nous avons constaté qu'un `kubectl scale` est effacé par le `kubectl apply` suivant.
- [ ] À 0 réplica, le Deployment existe toujours, sans aucun pod.
- [ ] Nous avons provoqué un pod `Pending` et lu sa raison dans `kubectl describe`.
- [ ] À la fin, `vote.deploy.yml` contient `replicas: 3` et une réservation de `100m` de processeur, et `kubectl get deployments` affiche `3/3`.

Pour terminer, arrêtez la surveillance (Ctrl+C dans le terminal 2), puis fermez les terminaux 2 et 3 (icône 🗑️ du panneau Terminal).

## Récap

- Le nombre d'exemplaires est un **état souhaité** comme un autre : on change `replicas`, Kubernetes calcule le reste.
- Les réplicas sont des **copies identiques**. Pour leur répartir les visiteurs, il faudra un **Service** (TP04).
- **Le fichier fait foi** : un raccourci comme `kubectl scale` est effacé par le prochain `apply`.
- **0 réplica** éteint l'application sans la supprimer : pratique pour économiser.
- Les **requests** réservent des ressources. Sans place disponible, un pod reste `Pending`. Lors d'une mise à jour, les anciens pods continuent alors de servir.
- Chaque modification du modèle de pod crée un **nouveau ReplicaSet**, ce qui prépare les mises à jour et les retours en arrière du TP06.

➡️ Suite : [04 — Services et Ingress](../04-services/README.md)
