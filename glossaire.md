# Glossaire Kubernetes

Les mots de la formation, expliqués simplement, avec le TP où vous les avez rencontrés. À garder sous la main en réunion projet.

## Les conteneurs

| Mot | En une phrase | TP |
|---|---|---|
| **Image** | Un paquet qui contient une application et tout ce dont elle a besoin pour tourner. Le « plat préparé » | 01 |
| **Conteneur** | Une image en train de tourner, isolée des autres. Le « plat servi » | 01 |
| **Dockerfile** | La recette qui décrit comment fabriquer une image | 01 |
| **Registre** | La bibliothèque en ligne où l'on range et télécharge les images (Docker Hub, ghcr.io…) | 01 |
| **Tag** | La version d'une image, après les deux-points : `kube-vote:2.0` | 01 |
| **Runtime** | Le programme qui crée réellement les conteneurs (containerd, runc). Kubernetes lui délègue ce travail | 01 |

## Le cluster

| Mot | En une phrase | TP |
|---|---|---|
| **Cluster** | Un ensemble de serveurs pilotés ensemble par Kubernetes. La « ville » | 00 |
| **Nœud** (*node*) | Un des serveurs du cluster, qui fait tourner des pods. Un « bâtiment » de la ville | 00, 03 |
| **kubectl** | La « télécommande » de Kubernetes : l'outil en ligne de commande qui lui parle | 00 |
| **Namespace** | Un espace de rangement dans le cluster, pour séparer environnements, équipes ou projets. Un « quartier » | 05 |
| **Control plane** | Le « cerveau » du cluster (API, ordonnanceur, base etcd…), géré par le fournisseur dans un Kubernetes managé | 09 |
| **Ordonnanceur** (*scheduler*) | Le composant qui choisit sur quel nœud placer chaque pod | 03 |

## Faire tourner une application

| Mot | En une phrase | TP |
|---|---|---|
| **Pod** | La plus petite unité que Kubernetes fait tourner : un ou plusieurs conteneurs. Un exemplaire de l'application. Un « appartement » | 02 |
| **Deployment** | L'objet qui maintient un nombre voulu de pods identiques et gère leurs mises à jour. Le « gestionnaire immobilier » | 02 |
| **ReplicaSet** | L'intermédiaire créé par le Deployment, qui maintient le nombre de pods d'une version donnée | 02, 03, 07 |
| **Réplica** | Une copie identique d'un pod. « 3 réplicas » = 3 exemplaires | 03 |
| **État souhaité** | Ce que l'on demande à Kubernetes (« 3 exemplaires de vote en v2 »), décrit dans un fichier YAML | 02 |
| **Réconciliation** | La boucle permanente par laquelle Kubernetes compare l'état souhaité à la réalité, et corrige l'écart. **L'idée centrale de Kubernetes** | 02 |
| **YAML** | Le format texte des fichiers Kubernetes : des lignes `clé: valeur`, organisées par indentation | 02 |
| **Label** (étiquette) | Un « post-it » collé sur un objet (`app: vote`), qui permet aux autres objets de le retrouver | 02, 04 |
| **Requests** (réservations) | La part de processeur et de mémoire réservée pour un conteneur. Base du dimensionnement et des coûts | 03 |
| **Limits** (plafonds) | Le maximum qu'un conteneur peut consommer. Au-delà de sa limite de mémoire, il est arrêté (`OOMKilled`) | 07 |

## Rendre une application joignable

| Mot | En une phrase | TP |
|---|---|---|
| **Service** | Un nom et une adresse stables pour un groupe de pods, qui répartit les requêtes entre eux. L'« adresse postale » ou le « standard téléphonique » | 04 |
| **ClusterIP** | Le type de Service par défaut, joignable seulement de l'intérieur du cluster | 04 |
| **DNS** | L'annuaire du cluster, qui traduit le nom d'un Service (`redis`, `db`) en adresse | 04 |
| **Ingress** | Les règles d'aiguillage des visites web venues de l'extérieur. La « porte d'entrée » | 04 |
| **Contrôleur d'Ingress** | Le programme qui reçoit réellement les visites et applique les règles d'Ingress (Traefik, NGINX…) | 04 |
| **Gateway API** | Le successeur de l'Ingress, plus riche, adopté par les nouveaux projets | 04 |

## Isoler et encadrer

| Mot | En une phrase | TP |
|---|---|---|
| **ResourceQuota** (quota) | Un plafond pour tout un namespace : nombre de pods, processeur, mémoire… | 05 |
| **LimitRange** | Des valeurs par défaut et des maximums pour chaque pod d'un namespace | 05 |
| **NetworkPolicy** | Une règle réseau : quels pods peuvent en contacter d'autres, et sur quel port. Bonne pratique : tout fermer, puis n'ouvrir que le nécessaire | 05 |
| **CNI** (Calico, Cilium…) | Le composant réseau du cluster ; c'est lui qui applique (ou non) les NetworkPolicies | 05 |
| **RBAC** | Les droits d'accès : qui a le droit de faire quoi, dans quel namespace | 05 |
| **Pod Security** | Le niveau de sécurité exigé des pods d'un namespace (interdire les conteneurs administrateurs…) | 05 |
| **Moteur de politiques** (*policy engine*) | Un garde-fou automatique : tout objet envoyé au cluster est vérifié par rapport aux règles de l'entreprise avant d'être accepté | 05 |
| **Kyverno** | Un moteur de politiques très utilisé, dont les règles s'écrivent en YAML. Il sait **valider** (refuser une image `:latest`, un pod sans réservations…), **modifier** (ajouter une étiquette, des réservations par défaut) et **générer** (donner à chaque nouveau namespace son quota et sa règle « tout fermer »). Projet diplômé de la CNCF en mars 2026 | 05 |
| **OPA Gatekeeper** | L'autre grand moteur de politiques, avec son propre langage de règles | 05 |
| « *Refusé par une policy* » | Un moteur de politiques a bloqué un fichier qui ne respectait pas une règle : c'est voulu | 05 |

## Configuration

| Mot | En une phrase | TP |
|---|---|---|
| **Variable d'environnement** | Un réglage donné à une application au démarrage (`OPTION_A=Montagne`) | 01, 06 |
| **ConfigMap** | Un objet qui range des réglages à part de l'image, pour réutiliser la même image partout | 06 |
| **Secret** | Un objet qui range des informations sensibles (mots de passe…). **Encodé, pas chiffré par défaut** : sa protection vient des droits d'accès. Le « coffre », à condition de bien le fermer | 06 |

## Mettre à jour et réparer

| Mot | En une phrase | TP |
|---|---|---|
| **Mise à jour progressive** (*rolling update*) | Le remplacement des pods un par un, sans coupure de service | 07 |
| **Rollback** (`rollout undo`) | Le retour à la version précédente, en quelques secondes | 07 |
| **Révision** | Une version du modèle de pod, gardée dans l'historique du Deployment | 07 |
| **Sonde de readiness** | « Es-tu prêt à recevoir des visiteurs ? » Sans réponse, le pod ne reçoit pas de trafic | 07 |
| **Sonde de liveness** | « Es-tu encore en vie ? » Sans réponse, le conteneur est redémarré | 07 |
| **Logs** | Le journal d'une application. Premier réflexe en cas d'incident | 01, 07 |
| **Post-mortem** | Le compte rendu d'un incident : symptôme, cause, réparation, prévention | 08 |

## Les statuts à reconnaître

| Statut | Ce qui se passe | Où chercher |
|---|---|---|
| `Running` | tout va bien… si la colonne `READY` est complète (`1/1`) | — |
| `Pending` | le pod attend une place sur un nœud | `kubectl describe pod` |
| `ContainerCreating` | l'image se télécharge, le conteneur démarre | patienter |
| `CreateContainerConfigError` | une ConfigMap ou un Secret attendu est introuvable | `kubectl describe pod` |
| `ErrImagePull` / `ImagePullBackOff` | l'image ne peut pas être téléchargée | `kubectl describe pod` |
| `CrashLoopBackOff` | l'application plante au démarrage, en boucle | `kubectl logs` |
| `OOMKilled` | l'application a dépassé sa limite de mémoire | `kubectl describe pod` |
| `Terminating` | le pod est en train de s'arrêter | patienter |

## Les commandes essentielles

| Commande | Rôle |
|---|---|
| `kubectl get pods` (ou `deployments`, `services`…) | lister des objets. `-o wide` pour plus de colonnes, `-n <namespace>` pour un autre namespace, `--watch` pour suivre en direct |
| `kubectl apply -f fichier.yml` | transmettre un état souhaité |
| `kubectl describe pod <nom>` | le détail d'un objet, avec ses événements |
| `kubectl logs <pod>` | le journal d'une application (`--previous` après un plantage) |
| `kubectl delete -f fichier.yml` | supprimer ce qu'un fichier décrit |
| `kubectl rollout status / history / undo deployment <nom>` | suivre, lister ou annuler une mise à jour |
| `kubectl port-forward service/<nom> 8080:80` | ouvrir un tunnel temporaire vers une application |

## L'écosystème (mots entendus en réunion)

| Mot | En une phrase |
|---|---|
| **Kubernetes managé** (EKS, GKE, AKS…) | un Kubernetes dont le fournisseur cloud gère le cœur |
| **OpenShift, Rancher** | des plateformes d'entreprise construites autour de Kubernetes |
| **k3s, minikube, kind, k3d** | des Kubernetes légers, pour apprendre, tester ou de petits serveurs |
| **Helm, Kustomize** | des outils pour regrouper et paramétrer les fichiers YAML d'une application |
| **GitOps** (Argo CD, Flux) | le cluster applique automatiquement ce qui est dans Git : « le fichier fait foi », poussé jusqu'au bout |
| **CI/CD** | la chaîne automatique qui construit, teste et livre une application |
| **FinOps** | la démarche de pilotage des coûts du cloud |
| **CNCF** | la fondation qui héberge Kubernetes et une grande partie de son écosystème |
