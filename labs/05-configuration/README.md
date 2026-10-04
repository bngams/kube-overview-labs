# 05 — Configuration, secrets et namespaces

> **Scénario à réaliser en binôme.** Votre application tourne, mais ses réglages sont gravés dans l'image ou écrits en clair dans les fichiers. Vous allez changer la question du vote **sans reconstruire l'image** (ConfigMap), sortir le mot de passe de la base dans un **Secret** (et découvrir ce qu'un Secret protège vraiment), puis créer un environnement de recette à côté de votre application, dans un **namespace**. Les blocs marqués `# TODO` sont à compléter vous-mêmes. Le dossier [`solution/`](solution/) contient la réponse, à n'ouvrir qu'en cas de blocage 😉.
>
> 🎯 **Niveau :** débutant. On suppose le [TP04](../04-services/README.md) terminé : les 5 morceaux de l'application tournent, et vous savez ouvrir la page de vote par la porte d'entrée (port 8000).
>
> 🧑‍✈️ **En binôme :** le **pilote** tape les commandes, le **copilote** lit la consigne à voix haute et explique ce qu'on observe. **Échangez les rôles à la section 3.**

## ✨ Objectifs

- Séparer la **configuration** de l'application grâce à une **ConfigMap**.
- Comprendre pourquoi changer une configuration impose de **redémarrer** les pods.
- Ranger un mot de passe dans un **Secret**, et savoir ce qu'il protège… ou pas.
- Utiliser les **namespaces** pour séparer des environnements, et voir ce qui les isole.

## 📁 Point de départ

On continue dans le dossier `tp02`, ouvert dans VS Code. Ouvrez un terminal (**terminal 1**) et vérifiez que l'application est complète :

```bash
kubectl get deployments
```

```
NAME     READY   UP-TO-DATE   AVAILABLE   AGE
db       1/1     1            1           1h
redis    1/1     1            1           1h
result   1/1     1            1           1h
vote     3/3     3            3           2h
worker   1/1     1            1           1h
```

S'il manque des morceaux, reprenez la section 4 du TP04.

Pour voir la page de vote pendant ce TP, utilisez la porte d'entrée du TP04 :

| Mode | Adresse | À faire avant |
|---|---|---|
| 🅰️ Local | `http://localhost:8000` | relancer le tunnel vers le contrôleur dans un **terminal 2** : `kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8000:80` |
| 🅱️ Cloud | `https://lab-kubeN-8000.deltavia.com` | rien |

À la fin de ce TP, le dossier `tp02` contiendra deux nouveaux fichiers :

```
tp02/
├── vote.deploy.yml    <- modifié à la section 1
├── vote.svc.yml
├── vote.ingress.yml
├── vote.config.yml    <- section 1 : les réglages de vote
└── db.secret.yml      <- section 3 : les identifiants de la base
```

## ⚙️ 1 — La ConfigMap : des réglages à part

Au TP01, vous avez changé la question du vote avec `docker run -e OPTION_A=Thé -e OPTION_B=Café`. Ces **variables d'environnement** sont des réglages donnés à l'application au démarrage. Dans Kubernetes, on les range dans un objet dédié, la **ConfigMap** : une liste de paires `clé: valeur`, séparée de l'image **et** du Deployment.

> 🧠 **Pourquoi séparer ?** La même image doit pouvoir tourner en test, en recette et en production, avec des réglages différents. Si les réglages étaient dans l'image, il faudrait une image par environnement. Avec une ConfigMap par environnement, on garde **une seule image**, testée une fois.

### Étape 1 — Écrire la ConfigMap

🚧 **À compléter :** créez un fichier `vote.config.yml` dans le dossier `tp02` (icône **Nouveau fichier** de l'explorateur), collez-y le contenu suivant, remplacez les `# TODO`, puis enregistrez.

```yaml
# Les réglages de vote, rangés à part : on les change sans toucher à l'image ni au Deployment
apiVersion: v1
kind: ConfigMap
metadata:
  name: vote-config
data:
  OPTION_A: # TODO : la première option du vote, par exemple Montagne
  OPTION_B: # TODO : la seconde option, par exemple Mer
```

| Champ | Rôle |
|---|---|
| `kind: ConfigMap` | on décrit un ensemble de réglages |
| `metadata.name` | son nom, `vote-config`, que le Deployment utilisera pour la retrouver |
| `data` | les réglages, sous forme `clé: valeur`. Les clés `OPTION_A` et `OPTION_B` sont celles que l'application sait lire |

Appliquez-la :

```bash
kubectl apply -f vote.config.yml
kubectl get configmaps
```

```
configmap/vote-config created
NAME               DATA   AGE
kube-root-ca.crt   1      2h
vote-config        2      0s
```

La colonne `DATA` compte 2 réglages. `kube-root-ca.crt` est une ConfigMap créée automatiquement par Kubernetes : ignorez-la.

### Étape 2 — Brancher la ConfigMap sur vote

La ConfigMap existe, mais `vote` ne la lit pas encore : il faut le dire dans son Deployment.

🚧 **À compléter :** dans `vote.deploy.yml`, ajoutez les **3 lignes** suivantes juste après la ligne `- containerPort: 80`, en commençant `envFrom:` **exactement sous le `p` de `ports:`** (10 espaces), comme vous l'avez fait pour `resources` au TP03. Enregistrez.

```yaml
          ports:
            - containerPort: 80
          envFrom:              # <- nouvelle ligne : "prends des variables d'environnement…"
            - configMapRef:     # <- nouvelle ligne : "… dans une ConfigMap…"
                name: # TODO : "… qui s'appelle" (le nom de votre ConfigMap)
          resources:
            requests:
              cpu: 100m
              memory: 64Mi
```

Appliquez la nouvelle version du Deployment :

```bash
kubectl apply -f vote.deploy.yml
kubectl get pods -l app=vote
```

Comme au TP03, modifier le modèle de pod déclenche une **mise à jour progressive** : les pods sont remplacés un par un. Après quelques secondes, trois nouveaux pods tournent.

Rechargez la page de vote : la question est devenue « **Montagne ou Mer ?** » (ou les options que vous avez choisies). L'image n'a pas changé, seule la configuration a changé.

> ⚠️ **Symptôme :** les nouveaux pods restent en `CreateContainerConfigError`.
> **Cause :** le Deployment cherche une ConfigMap qui n'existe pas, par exemple parce que son nom est mal écrit, ou parce que la ConfigMap n'a pas été appliquée. `kubectl describe pod <nom-du-pod>` l'indique en bas : `Error: configmap "vote-config" not found`.
> **Correctif :** vérifiez le nom dans les deux fichiers, puis appliquez la ConfigMap (`kubectl apply -f vote.config.yml`). Les pods démarrent tout seuls quelques secondes plus tard. Pendant ce temps, les anciens pods continuent de servir la page.

> 💡 La page des **résultats** (port 8081) affiche toujours « Cats » et « Dogs » : elle n'a pas été prévue pour lire ces réglages.

## 🔄 2 — Changer un réglage… et redémarrer

Changeons de nouveau la question, cette fois en ne modifiant **que** la ConfigMap.

🚧 **À compléter :** dans `vote.config.yml`, remplacez les deux valeurs par de nouvelles options de votre choix (par exemple `Été` et `Hiver`), enregistrez, puis appliquez :

```bash
kubectl apply -f vote.config.yml
```

```
configmap/vote-config configured
```

Rechargez la page de vote : **la question n'a pas changé** !

> 🧠 **Pourquoi ?** Une variable d'environnement est lue **une seule fois**, au démarrage du conteneur. Les pods qui tournent ont démarré avec les anciennes valeurs, et la ConfigMap modifiée ne les concerne pas tant qu'ils ne redémarrent pas. Rien dans le Deployment n'a changé, donc Kubernetes n'a aucune raison de les remplacer.

Demandez explicitement le redémarrage progressif des pods de `vote` :

```bash
kubectl rollout restart deployment vote
```

```
deployment.apps/vote restarted
```

Les pods sont remplacés un par un, sans coupure. Rechargez la page après une quinzaine de secondes : la nouvelle question s'affiche.

Pour vérifier les valeurs qu'un pod a réellement reçues, affichez ses variables d'environnement. `kubectl exec` lance une commande **dans** un conteneur, comme `docker exec` au TP01 :

```bash
kubectl exec deployment/vote -- env
```

Parmi les nombreuses lignes affichées, vous retrouvez vos réglages :

```
OPTION_A=Été
OPTION_B=Hiver
```

> 🗣️ **En réunion projet.** « *On a changé la config, il faut redémarrer les pods* » : c'est exactement ce que vous venez de faire. Un changement de configuration se déploie donc comme une petite mise en production. Un mauvais réglage peut casser l'application aussi sûrement qu'un bug, d'où l'intérêt de versionner ces fichiers dans Git.

## 🔐 3 — Le Secret : ranger un mot de passe

🔄 **Échangez les rôles** : le copilote devient pilote.

Au TP04, le fichier `db.yml` contenait le mot de passe de la base **en clair**, une mauvaise pratique assumée. Les informations sensibles (mots de passe, clés d'accès, certificats) se rangent dans un objet dédié, le **Secret**. Il ressemble beaucoup à une ConfigMap, mais Kubernetes le traite à part : il peut réserver sa lecture à certaines personnes, ne l'affiche pas par défaut, et peut le chiffrer dans sa propre base.

### Étape 1 — Écrire le Secret

🚧 **À compléter :** créez un fichier `db.secret.yml` dans `tp02`, collez-y le contenu suivant, remplacez les `# TODO`, puis enregistrez.

```yaml
# Les identifiants de la base, rangés dans un Secret plutôt qu'en clair dans le Deployment
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:
  POSTGRES_USER: # TODO : le nom d'utilisateur de la base, postgres
  POSTGRES_PASSWORD: # TODO : son mot de passe, postgres
```

| Champ | Rôle |
|---|---|
| `kind: Secret` | on décrit une information sensible |
| `type: Opaque` | un Secret « générique », fait de paires `clé: valeur` |
| `stringData` | les valeurs, écrites en clair **dans ce fichier seulement** : Kubernetes les encode à l'enregistrement |

> ⚠️ **Pourquoi garder `postgres` comme mot de passe ?** Les programmes `worker` et `result` ont ce mot de passe écrit en dur dans leur code. Si vous le changiez, la base l'accepterait, mais eux ne pourraient plus s'y connecter. Une application bien conçue lit ses identifiants dans des variables d'environnement, précisément pour qu'on puisse les changer sans la reconstruire.

Appliquez le Secret, puis listez les Secrets :

```bash
kubectl apply -f db.secret.yml
kubectl get secrets
```

```
secret/db-credentials created
NAME             TYPE     DATA   AGE
db-credentials   Opaque   2      0s
```

### Étape 2 — Brancher le Secret sur la base

Une nouvelle version de `db.yml` vous est fournie : elle remplace les deux variables écrites en clair par une référence au Secret. Voici la partie qui change :

```yaml
          envFrom:
            - secretRef:
                name: db-credentials   # "prends toutes les variables du Secret db-credentials"
```

C'est le même principe que `configMapRef` à la section 1, appliqué à un Secret. Appliquez cette nouvelle version :

```bash
kubectl apply -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/05-configuration/assets/db.yml
```

```
deployment.apps/db configured
service/db unchanged
```

Le pod de la base est remplacé. Patientez une minute, puis regardez l'ensemble des pods :

```bash
kubectl get pods
```

```
NAME                      READY   STATUS    RESTARTS      AGE
db-78fb95db9-z4jgb        1/1     Running   0             48s
redis-6d8c4c97c8-gzjg9    1/1     Running   0             1h
result-795757c79d-52s5t   1/1     Running   1 (46s ago)   1h
vote-7b65bd444c-8jgpw     1/1     Running   0             10m
vote-7b65bd444c-dpf7v     1/1     Running   0             10m
vote-7b65bd444c-q726p     1/1     Running   0             10m
worker-59774dd7cd-277h4   1/1     Running   1 (45s ago)   1h
```

`worker` et `result` ont redémarré : ils ont perdu leur connexion à la base pendant son remplacement, ont planté, et Kubernetes les a relancés. Votez de nouveau : tout fonctionne. En revanche, **les votes précédents ont disparu** de la page des résultats. C'est la limite annoncée au TP04 : la base n'a pas de **volume persistant**, ses données vivaient dans le pod remplacé.

> 🗣️ **En réunion projet.** Voilà pourquoi une base de données dans Kubernetes demande des précautions : un volume persistant, des sauvegardes, et souvent un outil spécialisé. Beaucoup d'équipes préfèrent d'ailleurs une base **managée** par leur fournisseur cloud, hors du cluster.

### Étape 3 — Ce qu'un Secret protège… ou pas

Regardez maintenant le contenu du Secret tel que Kubernetes le stocke :

```bash
kubectl get secret db-credentials -o yaml
```

Parmi les lignes affichées, repérez la section `data` :

```
data:
  POSTGRES_PASSWORD: cG9zdGdyZXM=
  POSTGRES_USER: cG9zdGdyZXM=
```

Le mot de passe n'apparaît pas en clair… mais il est seulement **encodé** en *base64*, une simple transcription, pas un chiffrement. N'importe qui peut le décoder :

```bash
kubectl get secret db-credentials -o go-template="{{.data.POSTGRES_PASSWORD | base64decode}}"
```

```
postgres
```

> 🛡️ **À retenir.** Un Secret n'est pas un coffre-fort : sa protection vient des **droits d'accès** (qui a le droit de lire les Secrets du cluster ?) et du **chiffrement** de la base de Kubernetes, à activer par les administrateurs. Et surtout, un fichier comme `db.secret.yml` ne doit **jamais** être déposé tel quel dans Git. En entreprise, on utilise des outils dédiés (un coffre comme HashiCorp Vault ou celui du fournisseur cloud, ou des Secrets chiffrés dans Git) qui fournissent les Secrets au cluster.
>
> 📖 [ConfigMaps](https://kubernetes.io/fr/docs/concepts/configuration/configmap/) · [Secrets](https://kubernetes.io/fr/docs/concepts/configuration/secret/)

## 🗂️ 4 — Les namespaces : des espaces séparés

Jusqu'ici, tout ce que vous avez créé se trouve dans le namespace `default`, mentionné dans de nombreuses réponses depuis le TP02. Un **namespace** est un espace de rangement à l'intérieur du cluster : des objets de même nom peuvent exister dans deux namespaces différents sans se gêner. Listez ceux de votre cluster :

```bash
kubectl get namespaces
```

```
NAME              STATUS   AGE
default           Active   3h
ingress-nginx     Active   1h      <- en mode local seulement : le contrôleur d'Ingress du TP04
kube-node-lease   Active   3h
kube-public       Active   3h
kube-system       Active   3h
```

`kube-system` contient les composants de Kubernetes lui-même. Jetez-y un œil, avec l'option `-n` (*namespace*) :

```bash
kubectl get pods -n kube-system
```

Vous y reconnaîtrez quelques noms vus pendant la formation : `coredns`, l'annuaire DNS qui traduit les noms de Services (TP04). En mode local, vous verrez aussi `kube-apiserver` (celui qui reçoit vos commandes `kubectl`), `kube-scheduler` (l'ordonnanceur du TP03) et `etcd` (la base où Kubernetes range l'état souhaité). En mode cloud, k3s regroupe ces composants dans un seul programme, et vous verrez plutôt `traefik`, `metrics-server` et `local-path-provisioner`. **N'y touchez jamais.**

### Étape 1 — Créer un environnement de recette

Imaginons que l'équipe veuille un environnement de **recette** (de validation), à côté de l'application actuelle. Créez un namespace pour lui :

```bash
kubectl create namespace recette
```

```
namespace/recette created
```

Déployez-y `vote` et son Service, **avec les mêmes fichiers** : l'option `-n recette` suffit à les envoyer dans le nouveau namespace.

```bash
kubectl apply -f vote.deploy.yml -n recette
kubectl apply -f vote.svc.yml -n recette
kubectl get pods -n recette
```

```
deployment.apps/vote created
service/vote created
NAME                   READY   STATUS                       RESTARTS   AGE
vote-fb9787cdf-gp955   0/1     CreateContainerConfigError   0          8s
vote-fb9787cdf-pz4rc   0/1     CreateContainerConfigError   0          8s
vote-fb9787cdf-sc5hs   0/1     CreateContainerConfigError   0          8s
```

Le Deployment `vote` de recette a été créé sans conflit avec celui de `default`, mais ses pods ne démarrent pas. Vous connaissez ce symptôme (section 1) : la ConfigMap `vote-config` est introuvable. Elle existe pourtant… mais dans `default`.

> 🧠 **Les objets d'un namespace ne sont visibles que dans ce namespace.** Un Deployment de `recette` ne voit que les ConfigMaps et les Secrets de `recette`. C'est voulu : chaque environnement a **ses propres réglages**, sans risque de mélanger la recette et la production.

🚧 **À compléter :** appliquez votre ConfigMap dans le namespace `recette`, avec la même option que ci-dessus, puis vérifiez que les pods démarrent.

```bash
kubectl apply -f vote.config.yml # TODO : ajoutez l'option qui désigne le namespace recette
kubectl get pods -n recette
```

### Étape 2 — Qui voit qui ?

Les namespaces séparent aussi les **noms de Services**. Lancez un pod de test **dans** `recette`, qui essaie de joindre trois adresses :

```bash
kubectl run test -n recette --rm -i --restart=Never --image=ghcr.io/bngams/kube-busybox:1.37 -- sh -c "wget -qO- -T 3 http://redis:6379; wget -qO- http://vote/healthz; echo; wget -qO- http://vote.default/healthz"
```

Le terminal affiche (sur une seule ligne sous PowerShell, comme au TP04) :

```
wget: bad address 'redis:6379'
{"hostname":"vote-fb9787cdf-pz4rc","status":"ok","version":"1.0"}
{"hostname":"vote-7b65bd444c-dpf7v","status":"ok","version":"1.0"}
pod "test" deleted from recette namespace
```

| Adresse appelée | Résultat | Pourquoi |
|---|---|---|
| `http://redis:6379` | `bad address` | il n'y a pas de Service `redis` dans `recette` |
| `http://vote` | un pod `vote-fb9787cdf-…` | le nom court désigne le Service `vote` **du même namespace**, celui de recette |
| `http://vote.default` | un pod `vote-7b65bd444c-…` | en ajoutant le nom du namespace, on atteint le `vote` de `default` |

Le namespace sépare donc les **noms** et les **réglages**, mais il ne bloque pas les communications : en le nommant, on peut joindre un autre namespace. Pour interdire réellement ces échanges, il faut des règles réseau dédiées (des *NetworkPolicies*).

### Étape 3 — Supprimer un environnement d'un coup

L'environnement de recette n'est plus utile. Supprimer un namespace supprime **tout ce qu'il contient** :

```bash
kubectl delete namespace recette
```

```
namespace "recette" deleted
```

La commande peut prendre une vingtaine de secondes. Vérifiez avec `kubectl get namespaces` : `recette` a disparu, avec son Deployment, ses pods, son Service et sa ConfigMap. Votre application, dans `default`, n'a pas bougé.

> 🗣️ **En réunion projet.** Les namespaces servent à séparer des **environnements** (dev, recette…), des **équipes** ou des **projets** sur un même cluster. On y attache des **droits** (« l'équipe A ne gère que son namespace ») et des **quotas** (« ce namespace ne peut pas réserver plus de 4 processeurs »), utiles pour répartir les coûts. Beaucoup d'entreprises gardent en revanche la **production** sur un cluster séparé, pour une isolation plus forte.
>
> 📖 [Namespaces](https://kubernetes.io/fr/docs/concepts/overview/working-with-objects/namespaces/)

## 🔵 Pour aller plus loin

Ces pistes sont facultatives.

- **Changer de namespace par défaut :** `kubectl config set-context --current --namespace=recette` évite de taper `-n recette` à chaque commande. Revenez ensuite avec `--namespace=default`, sinon vos commandes suivantes viseront le mauvais namespace.
- **Tout voir d'un coup :** `kubectl get pods -A` (pour *all namespaces*) liste les pods de tous les namespaces.
- **Un quota :** créez un namespace, puis appliquez-y un *ResourceQuota* qui limite les réservations de processeur (`requests.cpu: "200m"`). Essayez d'y déployer `vote` avec 3 réplicas à `100m` chacun : seuls 2 pods sont créés. `kubectl describe replicaset -n <namespace>` explique pourquoi.
- **Un réglage sous forme de fichier :** une ConfigMap peut aussi contenir un fichier entier (une configuration NGINX, par exemple), monté dans le conteneur comme un vrai fichier. C'est l'autre façon courante de l'utiliser.

## 🎉 Challenge final

- [ ] La page de vote affiche nos propres options, lues dans la ConfigMap `vote-config`.
- [ ] Nous avons constaté qu'une ConfigMap modifiée n'est prise en compte qu'après `kubectl rollout restart`.
- [ ] La base lit ses identifiants dans le Secret `db-credentials`, et le vote fonctionne toujours.
- [ ] Nous avons décodé le mot de passe du Secret, et nous savons expliquer pourquoi ce n'est pas un coffre-fort.
- [ ] Dans le namespace `recette`, `vote` ne démarrait qu'une fois sa propre ConfigMap créée.
- [ ] Le namespace `recette` est supprimé, et l'application de `default` tourne toujours.

## Récap

- Une **ConfigMap** sépare les réglages de l'image : une seule image, des réglages par environnement.
- Les variables d'environnement sont lues **au démarrage** : après un changement de ConfigMap, il faut `kubectl rollout restart`.
- Un **Secret** range les informations sensibles. Il est **encodé, pas chiffré** : sa protection vient des droits d'accès, et il ne va jamais en clair dans Git.
- Un **namespace** sépare les noms, les réglages, les droits et les quotas. Le supprimer supprime tout ce qu'il contient.

➡️ Suite : [06 — Mettre à jour et réparer](../06-mises-a-jour/README.md)
