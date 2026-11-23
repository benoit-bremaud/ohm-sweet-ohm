# 94 Voie d'entrée d'une sonde de température résistive

Diagnostiquer une voie qui lit une sonde PT1000 (ou toute sonde résistive) : séparer la sonde de la carte, puis suivre la voie jusqu'au convertisseur.

## En bref

Une carte annonce un « défaut sonde » alors que la sonde mesure bien hors circuit : la panne est **après la sonde**, dans la voie d'acquisition (connecteur, résistance de référence, filtre, multiplexeur, convertisseur du microcontrôleur). On le prouve en **remplaçant la sonde** par une résistance connue, puis on localise la panne en **comparant la voie suspecte à une voie jumelle** saine de la même carte.

> **Sécurité** : périmètre de la fiche [00](../00_securite/README.md), 50 V continu (25 V alternatif) au plus. Les mesures à l'ohmmètre, en mode diode et en continuité se font **hors tension**, carte déchargée. La substitution et l'observation à l'oscilloscope se font sous tension, alimentation limitée en courant, pince de masse sur le 0 V seulement (page [i2](../i2_oscilloscope/README.md)).

## La voie d'une PT1000

Une PT1000 vaut **1 000 Ω à 0 °C** et prend environ **3,85 Ω par °C** (norme IEC 60751, α = 0,00385). La carte la monte en général dans un **pont diviseur** avec une résistance de référence précise (souvent 1 kΩ à 0,1 %), ou l'alimente par une **source de courant** ; un condensateur filtre le point milieu, une diode ou un réseau protège l'entrée, un multiplexeur choisit la voie, le convertisseur du microcontrôleur lit la tension. Contrôler une PT1000 hors circuit : ohmmètre sur ses deux fils, environ 1 080 Ω à 20 °C (fiche [12](../12_thermistance/README.md) pour la méthode à froid et au chaud).

## 1. Remplacer la sonde par une résistance connue

![Une résistance de 1 000 Ω à 0,1 % est branchée à la place de la sonde PT1000 sur le connecteur 2 broches TEMP, carte sous tension. 1 000 Ω donne 0 °C, 1 100 Ω environ 26 °C, 1 385 Ω environ 100 °C. Lecture juste : la sonde ou son câble est en cause. Lecture fausse : la voie de la carte. Essai bref, élément chauffant débranché](substitution-sonde.svg)

Une boîte à décades, ou deux résistances fixes (1 kΩ et 1,1 kΩ), donnent une lecture attendue connue. Lecture juste : connecteur, câble ou contact de la sonde. Lecture fausse ou défaut maintenu : la carte. Essai bref, sous surveillance, élément chauffant débranché, **jamais** sur un pack ou un chargeur de batteries : la carte croit lire une température fixe et sa protection thermique est neutralisée pendant l'essai.

## 2. Repérer la masse du connecteur

![Multimètre en continuité, pointe noire sur un trou de fixation métallisé, pointe rouge sur chaque broche du connecteur TEMP 1 : la broche b bipe, c'est la masse ; la broche a est la broche de mesure](broche-de-masse.svg)

Le trou de fixation est souvent relié à la terre de protection, pas au 0 V logique : confirmer sur la broche GND d'un circuit intégré de la voie (le multiplexeur, par exemple). Si aucune broche ne bipe, la masse logique peut être isolée du châssis, ou la sonde montée entre l'entrée et une résistance de référence : c'est l'ohmmètre qui le montre (étape 3).

## 3. Mesurer chaque broche à la masse, hors tension

![Multimètre sur ohms, pointe rouge sur la broche puis sur la masse : 4,72 kΩ puis 1,18 kΩ. Deux lectures différentes signalent une jonction de protection en parallèle](ohm-deux-polarites.svg)

En circuit, l'ohmmètre voit tous les chemins en parallèle (fiche [02](../02_pieges_en_circuit/README.md)) : une diode de protection change la lecture selon le sens des pointes. Mesurer **dans les deux sens**, et comparer chaque sens à la même broche d'une voie jumelle, pas à une valeur théorique.

![Ohmmètre sur un nœud qui porte 100 kΩ et 10 µF : la lecture part de zéro, vaut 86,5 kΩ après 2 s et se stabilise à 100 kΩ. Le filtre d'une entrée de sonde se charge en moins d'une milliseconde](noeud-filtre-ohm.svg)

Le filtre d'une entrée de sonde (quelques nanofarads à un microfarad) se charge en moins d'une milliseconde : la lecture est immédiate. Une lecture qui **monte** pendant des secondes signale un gros condensateur sur le nœud (τ = R·C) : attendre qu'elle se stabilise avant de la noter, et chercher ce condensateur s'il n'a rien à faire là.

## 4. Contrôler la protection en mode diode

![Mode diode : rouge sur la masse, noire sur la broche, 0,58 V ; inversé, une valeur haute ou OL, comme sur la voie jumelle. Environ 0 V dans les deux sens signale une protection ou une entrée en court-circuit](mode-diode-entree.svg)

## 5. Suivre la piste jusqu'au multiplexeur

![Continuité entre la broche de mesure du connecteur TEMP 2 et les entrées d'un multiplexeur TS3A5017 : le bip sur 1S2, broche 5, désigne la voie](trace-multiplexeur.svg)

La continuité suit une piste ; le mode diode compare deux voies, parce qu'il voit aussi les jonctions. Pas de bip : passer sur ohms, une résistance série de protection (1 à 10 kΩ) entre le connecteur et le multiplexeur est normale. Un interrupteur du multiplexeur dégradé (résistance à l'état passant qui dérive, fuite) ne fausse qu'une voie : sondes saines, écart entre deux voies jumelles.

## 6. Observer l'excitation sous tension

![Multimètre sur volts continus : une valeur qui saute autour de 0,45 V ; oscilloscope : des impulsions d'environ 1,2 V pendant la mesure. Lire le plateau, pas la moyenne](excitation-pulsee.svg)

Beaucoup de cartes n'alimentent la sonde que pendant la conversion, ou commutent leur source de courant d'une voie à l'autre : le multimètre affiche une moyenne instable. Quand seul le multiplexeur commute, après le pont diviseur, la broche reste en continu. L'oscilloscope montre le plateau de l'impulsion, à comparer au plateau de la voie jumelle.

## 7. Comparer aux voies jumelles et localiser

![Carte nue hors tension, broche b à la masse sur quatre voies : TEMP 1 995 Ω, TEMP 2 1 071 Ω, TEMP 3 1 000 Ω, TEMP 4 1 025 Ω. TEMP 1 et TEMP 2 sondent le même tuyau : 76 Ω d'écart, environ 20 °C. TEMP 2 est l'intruse](comparaison-voies.svg)

Une carte qui lit plusieurs sondes identiques porte autant de voies identiques : chacune sert d'étalon aux autres. Noter la même mesure sur toutes les voies, dans le même sens, et chercher **l'intruse** plutôt qu'une valeur théorique. Deux voies qui doivent lire pareil (deux sondes d'un même tuyau, par exemple) et qui s'écartent désignent la panne, même quand chaque valeur paraît plausible.

![Test d'échange : cartes filtre TFB1 et TFB2 échangées, puis fiches TEMP 1 et TEMP 2 échangées. Le défaut qui suit l'élément désigne l'élément ; le défaut qui reste désigne la voie de la carte](test-echange.svg)

Quand deux cartes ou deux fiches sont identiques, l'échange tranche sans instrument : un seul échange à la fois, hors tension, fiches repérées et photographiées avant. Jamais sur une panne destructrice (court-circuit, fumée) : on la déplacerait sur la carte saine.

![Hypothèse de voie : source de courant, PT1000 entre a et b, résistance de référence R25 de b à la masse. R25 à 1 071 Ω au lieu de 1 000 Ω ajoute environ 18 °C à la lecture ; la voie saine à 995 Ω retire environ 1 °C ; l'écart de 20 °C déclenche « Temperature Mismatch »](derive-reference.svg)

Le schéma est une **hypothèse** reconstruite à l'ohmmètre, sans schéma constructeur : il suffit à chiffrer l'effet d'une dérive. Avec une source de courant, toute la dérive de la référence passe dans la lecture, à 3,85 Ω par °C. Avec un pont diviseur ratiométrique, le signe change mais l'ordre de grandeur reste.

![Entonnoir : connecteur, via, puis résistance. À chaque étape, la même mesure sur la voie suspecte et sur sa jumelle ; R25 à 1 071 Ω contre 994 Ω pour R82 et R24](entonnoir-voie.svg)

Resserrer la même mesure, du connecteur vers le composant, en comparant toujours à la jumelle : l'étape où l'écart apparaît désigne le composant ou la piste. Une résistance de précision qui a dérivé se remplace par la même valeur, la même tolérance et le même coefficient de température (fiche [10](../10_resistance/README.md)).

## Arbre de décision

```mermaid
flowchart TD
  A[Défaut sonde annoncé par la carte] --> B[Sonde hors circuit à l'ohmmètre : environ 1 000 Ω à 0 °C, 3,85 Ω par °C]
  B --> C{Valeur juste ?}
  C -- non --> C1[Remplacer la sonde ou son câble]
  C -- oui --> D[Sous tension : résistance connue à la place de la sonde]
  D --> E{Lecture juste ?}
  E -- oui --> E1[Connecteur, câble ou contact de la sonde]
  E -- non --> F[Hors tension : repérer la masse, puis chaque broche à la masse dans les deux sens]
  F --> G{Écart avec la voie jumelle ?}
  G -- oui --> H[Suivre la piste : résistance de référence, filtre, protection, multiplexeur]
  H --> H1[Composant désigné : sa fiche]
  G -- non --> I[Oscilloscope : plateau de l'excitation comparé à la voie jumelle]
  I --> J{Écart ?}
  J -- oui --> H
  J -- non --> K[Convertisseur ou logiciel : sonde de débogage, registres de l'ADC]
```

## Aide-mémoire d'établi

| Mesure | État | Lecture saine | Suspect |
| --- | --- | --- | --- |
| PT1000 hors circuit | hors tension | ≈ 1 000 Ω à 0 °C, + 3,85 Ω par °C | OL, ≈ 0 Ω, écart de plus de quelques degrés |
| Résistance connue à la place de la sonde | sous tension, essai bref, élément chauffant débranché | 1 000 Ω → 0 °C, 1 100 Ω → 26 °C | défaut maintenu : la carte |
| Broche → masse, deux sens | hors tension | même lecture que la voie jumelle | écart net avec la jumelle |
| Mode diode, rouge sur la masse | hors tension | 0,5 à 0,7 V | ≈ 0 V dans les deux sens |
| Plateau de l'excitation | sous tension, oscilloscope | même plateau que la voie jumelle | plateau absent ou décalé |
| Même mesure sur toutes les voies jumelles | hors tension | écarts de quelques ohms | une voie à part : 4 Ω ≈ 1 °C |

## Sources

- IEC 60751:2022, *Industrial platinum resistance thermometers and platinum temperature sensors* : 1 000 Ω à 0 °C, α = 0,00385 /°C.
- Texas Instruments, fiche technique TS3A5017 (SCDS221) : brochage TSSOP-16, 1S1–1S4 sur les broches 6 à 3, 2S1–2S4 sur les broches 10 à 13, GND broche 8.
