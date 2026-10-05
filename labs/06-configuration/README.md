# 06 — Configuration et secrets

> **Scénario à réaliser en binôme.** Votre application tourne, mais ses réglages sont gravés dans l'image ou écrits en clair dans les fichiers. Vous allez changer la question du vote **sans reconstruire l'image** (ConfigMap), sortir le mot de passe de la base dans un **Secret** (et découvrir ce qu'un Secret protège vraiment). Les blocs marqués `# TODO` sont à compléter vous-mêmes. Le dossier [`solution/`](solution/) contient la réponse, à n'ouvrir qu'en cas de blocage 😉.
>
> 🎯 **Niveau :** débutant. On suppose le [TP05](../05-isolation/README.md) terminé : les 5 morceaux de l'application tournent dans le namespace `vote-app` (votre namespace par défaut), et vous savez ouvrir la page de vote par la porte d'entrée (port 8000).
>
> 🧑‍✈️ **En binôme :** le **pilote** tape les commandes, le **copilote** lit la consigne à voix haute et explique ce qu'on observe. **Échangez les rôles à la section 3.**

## ✨ Objectifs

- Séparer la **configuration** de l'application grâce à une **ConfigMap**.
- Comprendre pourquoi changer une configuration impose de **redémarrer** les pods.
- Ranger un mot de passe dans un **Secret**, et savoir ce qu'il protège… ou pas.

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

Pendant ce TP, vous aurez besoin de la page de vote (par la porte d'entrée du TP04) et de la page des résultats. Ouvrez les tunnels nécessaires :

| Page | 🅰️ Local | 🅱️ Cloud |
|---|---|---|
| Vote | `http://localhost:8000`, après avoir lancé dans un **terminal 2** : `kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8000:80` | `https://lab-kubeN-8000.deltavia.com`, rien à lancer |
| Résultats | `http://localhost:8081`, après avoir lancé dans un **terminal 3** : `kubectl port-forward service/result 8081:80` | `https://lab-kubeN-8081.deltavia.com`, après avoir lancé la même commande dans un **terminal 3** |

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

🚧 **À compléter :** créez un fichier `vote.config.yml` dans le dossier `tp02` (icône **Nouveau fichier** de l'explorateur), collez-y le contenu suivant, puis remplacez chaque `# TODO` **et tout le texte qui le suit sur la ligne** par votre valeur, comme au TP04. Enregistrez.

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
| `data` | les réglages, sous forme `clé: valeur`. Les clés `OPTION_A` et `OPTION_B` sont celles que l'application sait lire. Si une valeur est un nombre ou un mot comme `Oui`, `Non`, `Yes` ou `No`, mettez-la entre guillemets (`"Oui"`) : sinon YAML la prend pour autre chose qu'un texte, et l'`apply` échoue |

Appliquez-la :

```bash
kubectl apply -f vote.config.yml
kubectl get configmaps
```

```
configmap/vote-config created
NAME               DATA   AGE
kube-root-ca.crt   1      3h
vote-config        2      0s
```

La colonne `DATA` compte 2 réglages. `kube-root-ca.crt` est une ConfigMap créée automatiquement par Kubernetes : ignorez-la.

### Étape 2 — Brancher la ConfigMap sur vote

La ConfigMap existe, mais `vote` ne la lit pas encore : il faut le dire dans son Deployment.

🚧 **À compléter :** dans `vote.deploy.yml`, ajoutez **3 lignes** entre la ligne `- containerPort: 80` et la ligne `resources:`. Voici où elles se placent, les lignes existantes étant reprises pour vous repérer :

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

Pour éviter les pièges d'indentation : placez le curseur **au tout début** de la ligne `resources:` (colonne 1), appuyez trois fois sur Entrée pour créer trois lignes vides au-dessus, puis tapez les 3 lignes. `envFrom:` doit commencer **exactement sous le `p` de `ports:`** (10 espaces), `- configMapRef:` a 2 espaces de plus, `name:` encore 4 de plus. Enregistrez.

> 💡 **`env` ou `envFrom` ?** Dans `db.yml` (TP04), chaque variable était listée une par une sous `env:`. `envFrom:` importe d'un coup **toutes** les clés d'une ConfigMap. Et l'ordre des champs (`ports`, `envFrom`, `resources`…) n'a aucune importance : seule l'indentation compte.

Appliquez la nouvelle version du Deployment :

```bash
kubectl apply -f vote.deploy.yml
kubectl get pods -l app=vote
```

Comme au TP03, modifier le modèle de pod déclenche une **mise à jour progressive** (*rollout*, en anglais) : les pods sont remplacés un par un. Après une quinzaine de secondes, relancez `kubectl get pods -l app=vote` : trois nouveaux pods tournent, avec un nouveau début de nom.

```
NAME                   READY   STATUS    RESTARTS   AGE
vote-fb9787cdf-b9lr4   1/1     Running   0          17s
vote-fb9787cdf-gm8xn   1/1     Running   0          2s
vote-fb9787cdf-wccwd   1/1     Running   0          1s
```

Rechargez la page de vote : la question est devenue « **Montagne ou Mer ?** » (ou les options que vous avez choisies). L'image n'a pas changé, seule la configuration a changé.

> ⚠️ **Symptôme :** les nouveaux pods restent en `CreateContainerConfigError`.
> **Cause :** le Deployment cherche une ConfigMap qui n'existe pas, par exemple parce que son nom est mal écrit, ou parce que la ConfigMap n'a pas été appliquée. `kubectl describe pod <nom-du-pod>` l'indique en bas : `Error: configmap "vote-config" not found`.
> **Correctif :** vérifiez le nom dans les deux fichiers, puis appliquez la ConfigMap (`kubectl apply -f vote.config.yml`). Les pods démarrent tout seuls quelques secondes plus tard. Pendant ce temps, les anciens pods continuent de servir la page.

> 💡 La page des **résultats** (port 8081) affiche toujours « Cats » et « Dogs » : elle n'a pas été prévue pour lire ces réglages. Les votes sont enregistrés comme « option A » ou « option B » : les anciens votes pour « Chats » comptent donc désormais pour « Montagne ».

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

Demandez explicitement le redémarrage progressif des pods de `vote` (`rollout restart` : « refais une mise à jour progressive, sans rien changer d'autre ») :

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

Au TP04, le fichier `db.yml` contenait le mot de passe de la base **en clair**, une mauvaise pratique assumée. Les informations sensibles (mots de passe, clés d'accès, certificats) se rangent dans un objet dédié, le **Secret**. Il ressemble beaucoup à une ConfigMap, mais c'est un type d'objet à part : on peut ainsi autoriser une personne à lire les ConfigMaps **sans** lui donner accès aux Secrets, et les administrateurs peuvent faire chiffrer les Secrets dans la base où Kubernetes range tout son état (vous la découvrirez à la section 4).

### Étape 1 — Écrire le Secret

🚧 **À compléter :** créez un fichier `db.secret.yml` dans `tp02`, collez-y le contenu suivant, remplacez chaque `# TODO` et tout le texte qui le suit sur la ligne, puis enregistrez.

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

> ⚠️ **Pourquoi garder `postgres` comme identifiants ?** Les programmes `worker` et `result` ont ces identifiants écrits en dur dans leur code. Si vous le changiez, la base l'accepterait, mais eux ne pourraient plus s'y connecter. Une application bien conçue lit ses identifiants dans des variables d'environnement, précisément pour qu'on puisse les changer sans la reconstruire.

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
kubectl apply -f https://raw.githubusercontent.com/bngams/kube-overview-labs/main/labs/06-configuration/assets/db.yml
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

`worker` et `result` ont probablement redémarré : ils ont perdu leur connexion à la base pendant son remplacement, ont planté, et Kubernetes les a relancés. Votez de nouveau : tout fonctionne. Si la page des résultats ne se met plus à jour, relancez-les vous-mêmes avec `kubectl rollout restart deployment worker result`, puis relancez le tunnel du terminal 3. En revanche, **les votes précédents ont disparu** de la page des résultats. C'est la limite annoncée au TP04 : la base n'a pas de **volume persistant**, ses données vivaient dans le pod remplacé.

> 🗣️ **En réunion projet.** Voilà pourquoi une base de données dans Kubernetes demande des précautions : un volume persistant, des sauvegardes, et souvent un outil spécialisé. Beaucoup d'équipes préfèrent d'ailleurs une base **managée** par leur fournisseur cloud, hors du cluster.

### Étape 3 — Ce qu'un Secret protège… ou pas

Regardez maintenant le contenu complet du Secret, au format YAML (`-o yaml`) :

```bash
kubectl get secret db-credentials -o yaml
```

Le début de la réponse ressemble à ceci :

```
apiVersion: v1
data:
  POSTGRES_PASSWORD: cG9zdGdyZXM=
  POSTGRES_USER: cG9zdGdyZXM=
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Secret",…,"stringData":{"POSTGRES_PASSWORD":"postgres","POSTGRES_USER":"postgres"},…}
```

Deux surprises dans ces quelques lignes :

- Dans `data`, le mot de passe est **encodé** en *base64*, une façon d'écrire n'importe quelle donnée avec des lettres et des chiffres. C'est une simple transcription, **pas un chiffrement** : n'importe qui peut la décoder.
- Juste en dessous, l'annotation `last-applied-configuration`, ajoutée par `kubectl apply` pour se souvenir du dernier fichier appliqué, contient le mot de passe… **en clair** !

Décodez tout de même le base64, pour vous en convaincre :

```bash
kubectl get secret db-credentials -o "go-template={{.data.POSTGRES_PASSWORD | base64decode}}"
```

| Élément | Rôle |
|---|---|
| `-o "go-template=…"` | met en forme la réponse selon un modèle, au lieu du YAML complet |
| `{{.data.POSTGRES_PASSWORD}}` | « prends la valeur `POSTGRES_PASSWORD` de la section `data` » |
| `\| base64decode` | « et décode-la » |

Le terminal affiche `postgres`, collé à l'invite de commande suivante (ou suivi d'un `%` sous macOS), car la réponse ne se termine pas par un retour à la ligne.

Enfin, toute personne qui peut entrer dans un pod le lit aussi, directement dans les variables d'environnement :

```bash
kubectl exec deployment/db -- env
```

Parmi les lignes affichées : `POSTGRES_PASSWORD=postgres`.

> 🛡️ **À retenir.** Un Secret n'est pas un coffre-fort : sa protection vient des **droits d'accès** (qui a le droit de lire les Secrets, ou d'entrer dans les pods ?) et du **chiffrement** de la base de Kubernetes, que les administrateurs doivent activer (il ne l'est pas par défaut). Et surtout, un fichier comme `db.secret.yml` ne doit **jamais** être déposé tel quel dans Git. En entreprise, on utilise des outils dédiés : un coffre comme HashiCorp Vault ou celui du fournisseur cloud, ou des outils qui chiffrent les Secrets avant de les ranger dans Git (Sealed Secrets, SOPS).
>
> 📖 [ConfigMaps](https://kubernetes.io/fr/docs/concepts/configuration/configmap/) · [Secrets](https://kubernetes.io/fr/docs/concepts/configuration/secret/)

## 🔵 Pour aller plus loin

Ces pistes sont facultatives.

- **Une configuration par environnement :** une ConfigMap n'est visible que dans son namespace. En créant un namespace `recette` avec sa propre `vote-config`, la même image et le même `vote.deploy.yml` y afficheraient d'autres options : c'est ainsi qu'on sépare recette et production.
- **Un réglage sous forme de fichier :** une ConfigMap peut aussi contenir un fichier entier (une configuration NGINX, par exemple), monté dans le conteneur comme un vrai fichier. C'est l'autre façon courante de l'utiliser, et elle a un avantage : quand la ConfigMap change, le fichier est mis à jour dans les pods au bout d'une minute environ, sans redémarrage (à condition que l'application relise son fichier).

## 🎉 Challenge final

- [ ] La page de vote affiche nos propres options, lues dans la ConfigMap `vote-config`.
- [ ] Nous avons constaté qu'une ConfigMap modifiée n'est prise en compte qu'après `kubectl rollout restart`.
- [ ] La base lit ses identifiants dans le Secret `db-credentials`, et le vote fonctionne toujours.
- [ ] Nous avons décodé le mot de passe du Secret, et nous savons expliquer pourquoi ce n'est pas un coffre-fort.

## Récap

- Une **ConfigMap** sépare les réglages de l'image : une seule image, des réglages par environnement.
- Les variables d'environnement sont lues **au démarrage** : après un changement de ConfigMap, il faut `kubectl rollout restart`.
- Un **Secret** range les informations sensibles. Il est **encodé, pas chiffré par défaut** : sa protection vient des droits d'accès, et il ne va jamais en clair dans Git.

➡️ Suite : [07 — Mettre à jour et réparer](../07-mises-a-jour/README.md)
