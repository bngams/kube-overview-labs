# Ressources et lectures recommandées

Une sélection de lectures et de vidéos pour prolonger la formation. La colonne « Pour qui » vous aide à choisir : 🟢 accessible à tous, 🔵 plutôt pour les profils techniques.

## Liens partagés pendant la formation

Les liens utiles notés au fil des séances, classés par thème.

| Thème | Ressource | Pourquoi |
|---|---|---|
| Introduction | [Présentation « Conteneurs et Kubernetes »](https://codemos.io/courses/k8s-lab/slides/talk.html) | La conférence d'ouverture, avec ses chiffres clés (aussi sur [GitHub Pages](https://bngams.github.io/kube-overview-labs/slides/talk.html)) |
| Registres d'images | [État de l'art des solutions de registry Docker](https://www.osaxis.fr/etat-de-lart-des-solutions-de-registry-docker/) (Osaxis) | Panorama des registres d'images, publics et privés |
| Registres d'images | [Exemple d'interface : Nexus](https://user-images.githubusercontent.com/12953323/109366876-d640dc80-7894-11eb-9a4f-10be67c000f4.png) | À quoi ressemble un registre d'entreprise |
| Écosystème | [Projets de la CNCF](https://www.cncf.io/projects/), classés par maturité · [CNCF Landscape](https://landscape.cncf.io/) | Les projets sandbox, en incubation et diplômés |
| Installation locale | [minikube](https://minikube.sigs.k8s.io/docs/) | La distribution utilisée en mode local (TP00) |
| Architecture | [Topologies d'un cluster haute disponibilité](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/ha-topology/) | Plusieurs nœuds de contrôle, etcd intégré ou séparé |
| Passage à l'échelle | [HPA avec des métriques personnalisées](https://www.nakamasato.com/kubernetes-training/autoscaler/hpa/custom-metrics/) | Aller plus loin que le CPU pour l'autoscaling (TP03) |
| Réseau | [Network Policy Editor](https://editor.networkpolicy.io/) | Dessiner des règles réseau (TP05) |
| Outillage | [Installer Helm](https://helm.sh/docs/intro/install) | Le gestionnaire de paquets de Kubernetes, utilisé pour installer l'observabilité |
| Outillage | [Lens](https://lenshq.io/) | Une interface graphique pour explorer un cluster |
| Observabilité | [Métriques et logs : Prometheus, Grafana, Loki](https://github.com/bngams/2604-intro-k8s-bis/tree/main/05-obs) | Le TP d'observabilité (fichiers de séance dans [`training/tp-obs`](training/tp-obs/)) |

## Pour comprendre sans technique

| Ressource | Format | Pour qui | Pourquoi |
|---|---|---|---|
| [The Illustrated Children's Guide to Kubernetes](https://www.cncf.io/phippy/the-childrens-illustrated-guide-to-kubernetes/) (CNCF) | livre illustré, 15 min | 🟢 | Les notions du cours (pod, Deployment, Service…) racontées comme un conte, avec la girafe Phippy. Idéal à partager avec une équipe |
| [Phippy and Friends](https://www.cncf.io/phippy/) (CNCF) | livres et vidéos courtes | 🟢 | La suite, dont *Phippy Goes to the Zoo* qui présente d'autres objets Kubernetes |
| [Kubernetes comic](https://cloud.google.com/kubernetes-engine/kubernetes-comic) (Google Cloud) | bande dessinée | 🟢 | Pourquoi Kubernetes existe, du point de vue d'une équipe qui livre des applications |
| [Kubernetes: The Documentary](https://www.youtube.com/watch?v=BE77h7dmoQU) (CultRepo) | documentaire, 2 épisodes d'environ 30 min | 🟢 | L'histoire de Kubernetes chez Google, et pourquoi il est devenu un standard. Le « pourquoi » plutôt que le « comment » |

## Pour situer Kubernetes dans son organisation

| Ressource | Format | Pour qui | Pourquoi |
|---|---|---|---|
| [Rapports et enquêtes de la CNCF](https://www.cncf.io/reports/) | rapports annuels (PDF) | 🟢 | L'adoption de Kubernetes et des conteneurs dans les entreprises, chiffres à l'appui : utile pour un argumentaire |
| [Cloud Native Maturity Model](https://maturitymodel.cncf.io/) (CNCF) | guide en ligne | 🟢 | Situer son organisation : personnes, processus, technique, coûts. Très parlant pour un chef de projet ou un manager |
| [CNCF Landscape](https://landscape.cncf.io/) | carte interactive | 🟢 🔵 | Tout l'écosystème autour de Kubernetes. Impressionnant, et une bonne illustration de sa richesse… et de sa complexité |
| [FinOps Foundation](https://www.finops.org/) | guides, livres blancs | 🟢 | Piloter les coûts du cloud, y compris ceux de Kubernetes (étude de cas, section 3) |

## Pour continuer à pratiquer

| Ressource | Format | Pour qui | Pourquoi |
|---|---|---|---|
| [Documentation officielle de Kubernetes](https://kubernetes.io/fr/docs/home/), en français | documentation | 🔵 | La référence. Les liens 📖 des TPs y renvoient |
| [Aide-mémoire kubectl](https://kubernetes.io/fr/docs/reference/kubectl/cheatsheet/) | page de référence | 🔵 | Les commandes du quotidien, à garder sous la main |
| [Killercoda, Kubernetes playgrounds](https://killercoda.com/playgrounds) | clusters dans le navigateur | 🔵 | Un cluster jetable gratuit, sans rien installer, pour refaire les TPs chez soi |
| Les TPs de cette formation | ce dépôt | 🟢 🔵 | Avec minikube (TP00, mode local), tous les TPs se refont sur votre poste |

## Isoler et sécuriser (TP05)

| Ressource | Format | Pour qui | Pourquoi |
|---|---|---|---|
| [Network Policy Editor](https://editor.networkpolicy.io/) (Isovalent) | outil visuel en ligne, avec tutoriel | 🟢 🔵 | Dessiner des règles réseau et voir le YAML se construire, sans cluster ni risque |
| [Kyverno](https://kyverno.io/) · [introduction](https://kyverno.io/docs/introduction/) | site officiel, documentation | 🟢 🔵 | Comprendre ce qu'est un moteur de politiques : valider, modifier, générer |
| [Bibliothèque de règles Kyverno](https://kyverno.io/policies/) | catalogue de règles prêtes à l'emploi | 🟢 🔵 | De nombreux exemples concrets (« interdire `:latest` », « exiger des réservations »…) : très parlant pour voir ce qu'une entreprise peut imposer |
| [Annonce du diplôme de Kyverno](https://www.cncf.io/announcements/2026/03/24/cloud-native-computing-foundation-announces-kyvernos-graduation/) (CNCF, mars 2026) | article | 🟢 | Qui l'utilise (Bloomberg, Spotify, Deutsche Telekom…) et pourquoi c'est devenu un standard |
| [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/website/) | documentation | 🔵 | L'alternative à Kyverno |
| [NetworkPolicies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) · [Pod Security](https://kubernetes.io/docs/concepts/security/pod-security-admission/) | documentation officielle | 🔵 | Les références sur les règles réseau et la sécurité des pods |

## Pour aller plus loin (profils techniques)

| Ressource | Format | Pour qui | Pourquoi |
|---|---|---|---|
| *Kubernetes: Up and Running* (B. Burns, J. Beda, K. Hightower, L. Evenson), O'Reilly | livre | 🔵 | Écrit par des créateurs de Kubernetes : la meilleure introduction approfondie |
| [*Kubernetes Patterns*](https://developers.redhat.com/e-books/kubernetes-patterns) (B. Ibryam, R. Huß), e-book offert par Red Hat (inscription requise) | livre | 🔵 | Les bonnes pratiques de conception d'applications pour Kubernetes (sondes, configuration, mises à jour…) |
| [Gateway API](https://gateway-api.sigs.k8s.io/) | documentation | 🔵 | Le successeur de l'Ingress (TP04) |
| [Fin de maintenance d'Ingress NGINX](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) (blog Kubernetes, nov. 2025) | article | 🔵 | Pourquoi le contrôleur NGINX historique n'est plus maintenu depuis mars 2026, et vers quoi migrer |

> 💡 Les liens ont été vérifiés le 6 octobre 2026. Les sites de Red Hat et d'O'Reilly bloquent les vérifications automatiques : si un lien ne fonctionne plus, une recherche du titre suffit à retrouver la ressource.
