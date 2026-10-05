# Slides

Deux présentations HTML (reveal.js), une par jour :

- [`jour1.html`](jour1.html) : des conteneurs à Kubernetes (modules 1 à 5, TP00 à TP03)
- [`jour2.html`](jour2.html) : Kubernetes dans la vraie vie (modules 5 à 8, TP04 à TP09)
- [`idees-infra-j1.html`](idees-infra-j1.html) : idées d'infrastructure du jour 1, de la VM à l'orchestrateur, en 7 schémas
- [`talk.html`](talk.html) : **présentation « conférence »** de 20 à 30 minutes, tout public (chiffres clés sourcés, conteneurs et agilité, limites, IA). Utilisable en ouverture de formation ou seule, devant un public non technique

## Ouvrir les slides

En ligne : [bngams.github.io/kube-overview-labs](https://bngams.github.io/kube-overview-labs/) ([jour 1](https://bngams.github.io/kube-overview-labs/slides/jour1.html), [jour 2](https://bngams.github.io/kube-overview-labs/slides/jour2.html), [conférence](https://bngams.github.io/kube-overview-labs/slides/talk.html)).

En local : double-cliquez sur le fichier : il s'ouvre dans le navigateur. Une connexion Internet est nécessaire (reveal.js et les polices viennent d'un CDN).

Si un navigateur bloque les fichiers locaux, servez le dossier :

```bash
python3 -m http.server 8000 --directory slides
```

puis ouvrez `http://localhost:8000/jour1.html`.

## Pendant la présentation

| Touche | Action |
|---|---|
| `→` / `Espace` | slide suivante (et apparitions successives) |
| `S` | **notes du formateur** dans une fenêtre séparée (déroulé, durées, réponses du quiz) |
| `F` | plein écran |
| `O` ou `Échap` | vue d'ensemble des slides |
| `B` | écran noir (pour une discussion) |

## Modifier

Le style commun est dans [`theme.css`](theme.css) (palette Excalidraw, police manuscrite *Kalam* pour les schémas). Les schémas sont en SVG directement dans le HTML : chaque boîte est un `<rect class="box f-blue" …>` suivi de son `<text>`, ce qui les rend faciles à retoucher. Les notes formateur sont dans les blocs `<aside class="notes">`.
