# Schémas Excalidraw

[`tableau-blanc.excalidraw`](tableau-blanc.excalidraw) regroupe les quatre schémas clés du cours, à projeter et **annoter en direct** :

1. l'application de vote (module 3, TP04) : à compléter avec les noms de Services, les réplicas, l'Ingress ;
2. la boucle de réconciliation (module 4, TP02) ;
3. le chemin d'une visite, du navigateur aux pods (module 5, TP04 et débriefing des pannes 2 et 3 du TP07) ;
4. la mise à jour progressive (module 6, TP06).

Pour l'ouvrir : [excalidraw.com](https://excalidraw.com), menu ☰ > **Ouvrir** (ou glisser-déposer le fichier dans la page). Les mêmes schémas existent en version propre dans les slides.

## Récap du jour 1 : de la VM à l'orchestrateur

[`recap-j1.excalidraw`](recap-j1.excalidraw) contient **7 cadres**, à présenter dans l'ordre (dans Excalidraw, chaque cadre se sélectionne et s'exporte séparément) :

| Cadre | Contenu |
|---|---|
| 1 | Scénario A : une seule VM qui fait tout (manuel de déploiement, scaling vertical / horizontal, snapshots, point unique de défaillance) |
| 2 | Scénario B (fictif) : une VM Linux + une VM Windows Server pour un ancien worker .NET Framework |
| 3 | A conteneurisé : registre d'images, `docker compose up`, réplicas sur une machine + reverse proxy |
| 4 | B conteneurisé : les composants Linux se regroupent ; une image Linux ne tourne que sur un hôte Linux |
| 5 | Le piège : Kubernetes sur un seul nœud = Compose avec d'autres commandes |
| 6 | Les vraies décisions : Rancher + RKE2 sur site, 3 nœuds de contrôle, pool Linux, nœud Windows (`nodeSelector`), Ingress, stockage, sauvegardes |
| 7 | Tableau récapitulatif VM / conteneurs / orchestrateur |

**Versions SVG** (autonomes, polices intégrées) : [`svg/`](svg/), un fichier par cadre. **Version HTML** : [`slides/recap-j1.html`](../slides/recap-j1.html), un schéma par slide, avec notes formateur ([en ligne](https://bngams.github.io/kube-overview-labs/slides/recap-j1.html)).

Les schémas sont générés par [`sources/gen-recap-j1.py`](sources/gen-recap-j1.py) (`python3 sources/gen-recap-j1.py` depuis ce dossier) : modifiez le script plutôt que le fichier, ou retouchez directement dans Excalidraw si c'est ponctuel.
