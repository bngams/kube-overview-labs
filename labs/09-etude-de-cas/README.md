# 09 — Étude de cas : Kubernetes dans votre projet

> **Atelier en binôme ou en petit groupe, sans ordinateur.** Vous savez maintenant ce que fait Kubernetes et ce qu'on voit dans un projet qui l'utilise. Reste la question que se pose tout chef de projet : **faut-il du Kubernetes pour *mon* projet ?** Et si oui, que faut-il prévoir, qui fait quoi, combien ça coûte ? Cet atelier vous donne une grille de lecture, puis vous l'appliquez à quatre projets fictifs.
>
> 🎯 **Pour qui :** tout le monde, et en particulier les profils non techniques. Les profils techniques jouent le rôle de l'équipe que le chef de projet interroge.
>
> ⏱️ **Durée :** environ 1 heure : 10 minutes de lecture de la grille, 30 minutes sur les cas, 20 minutes de restitution.

## ✨ Objectifs

- Savoir quand Kubernetes est pertinent… et quand il ne l'est pas.
- Connaître les grandes options : Kubernetes « managé » dans le cloud, installé chez soi, ou pas de Kubernetes du tout.
- Identifier les rôles, les coûts et les risques d'un projet sur Kubernetes.
- Repartir avec une liste de questions à poser à son équipe.

## 🧭 1 — La grille de lecture

### Ce que Kubernetes apporte

Vous l'avez vu pendant deux jours :

| Besoin du projet | Ce que Kubernetes apporte | Vu au |
|---|---|---|
| L'application doit rester disponible malgré les pannes | réparation automatique, plusieurs réplicas, répartition sur plusieurs serveurs | TP02, TP03 |
| La charge varie (pics, saisonnalité) | passage à l'échelle, manuel ou automatique | TP03 |
| On livre souvent, sans coupure | mises à jour progressives, retour arrière en quelques secondes | TP07 |
| L'application a plusieurs morceaux, dans plusieurs technologies | chaque morceau dans son conteneur, reliés par des Services | TP04 |
| Plusieurs environnements (dev, recette, prod), plusieurs équipes | namespaces, configuration séparée de l'image | TP05, TP06 |
| On veut éviter de dépendre d'un fournisseur | les mêmes fichiers YAML fonctionnent chez AWS, Google, Azure, OVH ou dans son propre datacenter | tout le cours |

### Ce que Kubernetes coûte

| Coût | En pratique |
|---|---|
| **Compétences** | Il faut des personnes formées pour l'exploiter : c'est souvent le coût principal. Une équipe sans compétence Kubernetes ne doit pas s'y lancer seule pour un projet critique |
| **Complexité** | Plus d'objets, plus de concepts, plus d'outils autour (supervision, sécurité, CI/CD). Une erreur de configuration peut tout bloquer (vous l'avez vu au TP08) |
| **Infrastructure** | Un cluster tourne en permanence, avec plusieurs nœuds pour la haute disponibilité, même quand l'application est peu utilisée |
| **Outillage** | Supervision, centralisation des logs, sauvegardes, sécurité des images… à prévoir et à financer |

### Quand Kubernetes n'est probablement **pas** le bon choix

- Un **site vitrine**, un blog, une petite application interne avec peu d'utilisateurs : un hébergement simple ou un service « serverless » suffit largement.
- Une **seule application monolithique**, rarement mise à jour, sans exigence forte de disponibilité.
- Une équipe **sans compétences** Kubernetes et sans budget pour en acquérir.
- Un **prototype** ou un MVP qui doit sortir vite : on pourra y venir plus tard, les conteneurs (TP01) facilitent la migration.

> 🧠 **La bonne question n'est pas « Kubernetes ou pas ? », mais « quel niveau de plateforme ? ».** Entre un simple serveur et un cluster Kubernetes géré en interne, il existe beaucoup d'intermédiaires : des plateformes qui font tourner des conteneurs sans exposer Kubernetes (Google Cloud Run, AWS App Runner, Azure Container Apps, Scaleway Serverless Containers…), ou un Kubernetes **managé**.

### Les grandes options

| Option | Qui gère quoi ? | Pour qui ? |
|---|---|---|
| **Pas de Kubernetes** : hébergement classique, PaaS, serverless | le fournisseur gère presque tout | petits projets, MVP, équipes réduites |
| **Kubernetes managé** : EKS (AWS), GKE (Google), AKS (Azure), OVHcloud, Scaleway… | le fournisseur gère le cœur du cluster (le *control plane*), l'équipe gère ses applications | la plupart des projets qui ont besoin de Kubernetes |
| **Plateforme d'entreprise** : OpenShift, Rancher, Tanzu… | un éditeur fournit Kubernetes + des outils + un support | grandes organisations, exigences de support et de conformité |
| **Kubernetes installé soi-même** | l'équipe gère tout, des serveurs à l'application | contraintes fortes (souveraineté, datacenter existant), équipe très compétente |

## 👥 2 — Qui fait quoi ?

Dans un projet sur Kubernetes, les responsabilités se répartissent souvent ainsi (les intitulés varient selon les organisations) :

| Rôle | Responsabilités | Ce que vous avez fait dans ce rôle |
|---|---|---|
| **Développeurs** | le code, le Dockerfile, les sondes de santé, la configuration attendue | TP01 (image), TP07 (sondes, `VOTE_TITLE`) |
| **DevOps / équipe applicative** | les fichiers YAML de l'application, la chaîne de livraison (CI/CD), les mises à jour | TP02 à TP07 |
| **Équipe plateforme / Ops / SRE** | le cluster lui-même, les nœuds, l'Ingress, la supervision, la sécurité, les sauvegardes | TP00 (en version miniature) |
| **Chef de projet / PO** | les exigences (disponibilité, performance, budget), le planning des mises en production, la communication en cas d'incident | TP08 (cahier des charges, fiche d'incident) |
| **Sécurité / RSSI** | les droits d'accès, les Secrets, la sécurité des images, la conformité | TP06 (Secrets) |

> 🗣️ La question « *qui est d'astreinte si le cluster tombe à 3 h du matin ?* » doit avoir une réponse **avant** la mise en production.

## 💶 3 — Les coûts, en pratique

Le coût d'un projet sur Kubernetes ne se résume pas à la facture des serveurs :

| Poste | Questions à poser |
|---|---|
| **Les nœuds** (les serveurs) | Combien ? De quelle taille ? Toujours allumés ? La somme des réservations (*requests*, TP03) détermine le nombre de nœuds nécessaires |
| **Le cluster managé** | Le fournisseur facture-t-il la gestion du cluster lui-même (souvent quelques dizaines d'euros par mois et par cluster) ? |
| **Les environnements** | Un cluster par environnement, ou des namespaces sur un cluster partagé (TP05) ? Peut-on éteindre la recette la nuit (0 réplica, TP03) ? |
| **Le stockage et le réseau** | Volumes persistants, sauvegardes, trafic sortant, répartiteurs de charge (*LoadBalancer*, TP04) |
| **L'outillage** | Supervision, logs, sécurité : outils open source à opérer, ou services payants |
| **Les personnes** | Formation, recrutement, astreintes : souvent le premier poste de dépense |

> 💡 La démarche **FinOps** (piloter les coûts du cloud) s'applique pleinement à Kubernetes : étiqueter les ressources par équipe ou projet, régler des réservations réalistes, éteindre ce qui ne sert pas, et suivre la facture régulièrement.

## 📋 4 — Les cas

Formez des groupes de 2 à 4 personnes, avec si possible un profil technique par groupe. Chaque groupe traite **un ou deux cas** et prépare une restitution de 5 minutes, en répondant aux questions de la section 5.

### Cas A — Le site de l'office de tourisme

Une collectivité veut refondre le site de son office de tourisme : des pages d'information, un agenda des événements, un formulaire de contact. Environ 2 000 visites par jour, un pic l'été. Le prestataire est une petite agence web de 5 personnes, sans compétence Kubernetes. Budget limité, mise en ligne dans 3 mois.

### Cas B — La plateforme de réservation

Une entreprise de transport régional lance une plateforme de réservation en ligne : recherche de trajets, paiement, billets électroniques, application mobile. Le trafic est très variable : faible la nuit, très fort aux heures de pointe et pendant les grèves des autres modes de transport. L'application compte une dizaine de services développés par trois équipes, avec des livraisons chaque semaine. Une indisponibilité coûte directement du chiffre d'affaires.

### Cas C — L'application métier interne

Un groupe industriel veut moderniser une application interne de gestion des maintenances, utilisée par 300 techniciens. C'est une application Java unique, avec une base de données. Elle est mise à jour deux fois par an. Le service informatique dispose déjà d'un cluster OpenShift, géré par une équipe plateforme, qui héberge d'autres applications du groupe.

### Cas D — Le service de données de santé

Une start-up développe un service d'analyse de données médicales pour des hôpitaux. Les données doivent rester hébergées en France, chez un hébergeur certifié pour les données de santé (HDS). L'équipe technique compte 4 développeurs, dont un qui a déjà utilisé Kubernetes. Les clients exigent une forte disponibilité, et chaque hôpital doit disposer d'un environnement isolé.

## ❓ 5 — Les questions à se poser

Pour chaque cas, répondez à ces questions :

1. **Besoin :** quels besoins du tableau de la section 1 ce projet a-t-il vraiment ?
2. **Décision :** Kubernetes, une plateforme plus simple, ou pas de conteneurs du tout ? Si Kubernetes : managé, plateforme d'entreprise ou installé soi-même ?
3. **Équipe :** qui ferait quoi (section 2) ? Quelles compétences manquent ?
4. **Coûts :** quels postes de la section 3 pèsent le plus ?
5. **Risques :** quels sont les deux principaux risques, et comment les réduire ?
6. **Questions à l'équipe technique :** quelles trois questions le chef de projet doit-il poser avant de valider le choix ?

## 🗒️ 6 — Les questions à poser à votre équipe

Voici une liste de questions à garder pour vos propres projets. Vous en comprenez maintenant le sens et les enjeux.

**Disponibilité et incidents**
- Combien de réplicas pour chaque application ? Sur combien de nœuds, dans combien de zones ?
- Nos applications ont-elles des **sondes de santé** ? (TP07)
- Comment revient-on en arrière si une mise en production se passe mal ? En combien de temps ? (TP07)
- Qui est d'astreinte ? Où voit-on les logs et les alertes ?

**Données**
- Où sont les données ? Sont-elles sur des **volumes persistants**, ou dans une base managée hors du cluster ? (TP04, TP06)
- Comment sont faites les **sauvegardes** ? A-t-on déjà testé une restauration ?

**Sécurité**
- Où sont rangés les **Secrets** ? Qui peut les lire ? Sont-ils dans Git ? (TP06)
- D'où viennent nos images ? Sont-elles analysées pour détecter les failles connues ?
- Qui a accès au cluster, et avec quels droits ?

**Livraison**
- Comment une nouvelle version arrive-t-elle en production ? Les fichiers YAML sont-ils dans Git ? (TP03)
- Les mêmes images sont-elles utilisées en recette et en production, avec seulement une configuration différente ? (TP06)

**Coûts**
- Combien coûte chaque environnement par mois ? Peut-on éteindre les environnements hors production la nuit ? (TP03)
- Les réservations (*requests*) sont-elles réalistes, ou surdimensionnées « par sécurité » ? (TP03)

## 🎤 7 — Restitution

Chaque groupe présente en 5 minutes son cas, sa décision et ses trois questions à l'équipe technique. Le formateur et les autres groupes challengent la décision.

<details>
<summary>Éléments de réponse pour le formateur</summary>

- **Cas A (office de tourisme) :** Kubernetes n'est pas pertinent. Un CMS hébergé, un hébergement mutualisé ou un PaaS suffisent ; l'agence n'a pas les compétences et le besoin de disponibilité reste modéré. Si l'agence travaille déjà avec des conteneurs, une plateforme serverless de conteneurs est une option.
- **Cas B (réservation) :** cas typique pour Kubernetes **managé** : beaucoup de services, plusieurs équipes, livraisons fréquentes, charge très variable (autoscaling), coût élevé des indisponibilités. Points d'attention : compétences, supervision, paiement (sécurité, conformité PCI-DSS), base de données probablement managée hors du cluster, tests de charge avant les pics.
- **Cas C (application interne) :** une application unique, rarement mise à jour, ne *nécessite* pas Kubernetes… mais le cluster OpenShift existe déjà, avec son équipe. L'héberger dessus peut être le choix le plus économique, si l'application est conteneurisée proprement. Bonne occasion de rappeler que la décision dépend aussi du **contexte existant**.
- **Cas D (données de santé) :** contrainte d'hébergement HDS en France => choisir un fournisseur certifié qui propose du Kubernetes managé, ou une offre dédiée. Les environnements isolés par hôpital plaident pour des namespaces (avec quotas, droits et NetworkPolicies) ou des clusters séparés selon le niveau d'isolation exigé. Le risque principal est la compétence : une seule personne connaît Kubernetes, ce qui fait d'elle un point unique de défaillance ; formation et accompagnement sont à prévoir.

</details>

## Récap

- Kubernetes répond à des besoins précis : **disponibilité**, **charge variable**, **livraisons fréquentes**, **applications à plusieurs morceaux**, **portabilité**.
- Son principal coût est **humain** : compétences, exploitation, astreintes.
- Entre « rien » et « Kubernetes installé soi-même », il existe de nombreux intermédiaires : le **Kubernetes managé** est le choix le plus courant.
- Un chef de projet n'a pas besoin de savoir écrire du YAML, mais il doit savoir **poser les bonnes questions** : vous avez maintenant la liste, et vous en comprenez le sens.

➡️ Pour aller plus loin : [ressources et lectures recommandées](../../ressources.md)
