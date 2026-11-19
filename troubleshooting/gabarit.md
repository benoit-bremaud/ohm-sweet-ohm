# Gabarit d'une fiche de dépannage

Copier ce fichier dans `troubleshooting/NN_composant/README.md`, remplacer chaque consigne en italique, garder l'ordre des sections et supprimer une section seulement si elle ne s'applique pas.

Les figures SVG sont générées : modifier `scripts/figures/guide_NN.py` (`guide_iN.py` pour une page d'appareil) puis lancer `just figures`, ne jamais retoucher un fichier `.svg` à la main (`just test` le refuse).

Les schémas Mermaid sont dessinés pour le site par `just trees` dans `arbre-N.svg` : le relancer après chaque modification d'un schéma (`just test` refuse un SVG périmé). Liens acceptés : `-->`, `-- texte -->`, `-.->`, `-. texte .->` ; toute autre forme fait échouer la construction.

## En bref

*Trois lignes au plus : ce qui tombe le plus souvent en panne sur ce composant, et la mesure qui tranche dans la majorité des cas.*

> **Sécurité** : mesures hors tension → carte débranchée, condensateurs déchargés ; mesures sous tension → alimentation limitée en courant, 50 V continu (25 V alternatif) au plus partout sur la carte (fiche 00). *Ajouter ici le risque propre au composant, s'il en a un.*

## Identifier le composant

*Boîtiers courants, marquage (code couleur, code CMS, référence), brochage, et où trouver sa valeur quand le marquage est illisible.*

## Modes de défaillance

Classés du plus fréquent au plus rare (consensus des réparateurs et notes de fabricants, voir Sources).

| Mode de défaillance | Fréquence | Cause typique | Ce que la panne implique ailleurs |
| --- | --- | --- | --- |
| *ex. ouvert* | *très fréquent, fréquent, occasionnel ou rare* | *…* | *composant en amont ou en aval à vérifier* |

## Niveau 1 — Inspection par les sens

*Indices visibles à l'œil ou à la loupe, odeur. Échauffement sous alimentation limitée : caméra thermique, alcool isopropylique qui s'évapore, ou dos du doigt approché brièvement (risque de brûlure, jamais au contact prolongé).*

## Niveau 2 — Mesure hors circuit

*Mode du multimètre, calibre, lecture attendue pour un composant sain, lecture pour chaque mode de défaillance, et pourquoi l'appareil réagit ainsi (renvoi vers la fiche 01).*

## Niveau 3 — Mesure en circuit

*Ce qui reste concluant en circuit, ce qui ne l'est pas, les pièges propres au composant (renvoi vers la fiche 02), et quand dessouder.*

## Niveau 4 — Méthodes avancées

*Instrument, méthode, ce qu'elle apporte de plus qu'un multimètre (renvoi vers sa page d'appareil, i1 à i8).*

## Arbre de décision

*Remplacer l'exemple par l'arbre du composant ; chaque feuille est un verdict ou une action.*

```mermaid
flowchart TD
  A[Composant suspect, carte hors tension] --> B{Indice visuel ?}
  B -- oui --> C[Chercher la cause en amont ou en aval, puis remplacer]
  B -- non --> D{Mesure en circuit concluante ?}
  D -- oui, défaut --> C
  D -- oui, sain --> E[Chercher ailleurs]
  D -- non --> F[Dessouder une patte et mesurer hors circuit]
  F --> G{Lecture conforme ?}
  G -- oui --> E
  G -- non --> C
```

## Remplacer le composant

*Critères d'équivalence (valeur, tolérance, puissance, tension, type), pièges du remplacement, et ce qu'il faut vérifier avant de remettre sous tension.*

## Aide-mémoire d'établi

*Dix lignes au plus, imprimables.*

## Mini-glossaire

*Facultatif : les quelques termes propres à ce composant, une ligne chacun, avec un renvoi à sa fiche de cours quand elle existe.*

## Sources

*Une source par affirmation non évidente : fiche technique, note d'application, fil de forum. Pas de citation longue ; reformuler.*
