# Dépannage électronique

Savoir, à l'établi, si un composant monté sur un PCB est mort ou vivant : des passifs aux circuits intégrés, avec le comportement du multimètre expliqué à chaque fois.

## Comment lire ces fiches

- **Public** : amateur débutant à intermédiaire. Un multimètre suffit pour les niveaux 1 à 3 ; le niveau 4 demande d'autres instruments (fiche 03).
- **Basse tension uniquement** (50 V continu au plus). Le secteur et l'isolement auront leur propre fiche ; d'ici là, un appareil branché au secteur se confie à un professionnel.
- **Niveaux** dans chaque fiche : 1 inspection visuelle, 2 mesure hors circuit, 3 mesure en circuit, 4 méthodes avancées.
- **Fréquence de panne** : un classement qualitatif (très fréquent, fréquent, occasionnel, rare) tiré du consensus des réparateurs et des notes de fabricants, sources citées dans chaque fiche. Ce n'est pas une statistique.
- Chaque fiche suit le [gabarit](gabarit.md) et renvoie aux fiches de base de la partie 0 au lieu d'en répéter le contenu.

## Menu

Du plus simple au plus complexe. Une ligne sans lien est une fiche à venir ; son issue la suit.

### 0. Bases (à lire en premier)

| Fiche | Contenu | Issue |
| --- | --- | --- |
| 00 Sécurité | Hors tension, décharge des condensateurs, alimentation limitée en courant | #81 |
| 01 Comprendre son multimètre | Ce que chaque mode injecte ; pourquoi un condensateur bipe puis se tait, ce qu'affiche le mode diode | #82 |
| 02 Pièges de la mesure en circuit | Chemins parallèles, jonctions qui conduisent, condensateurs qui se chargent, quand dessouder | #83 |
| 03 Autres instruments | LCR/ESR, testeur de composants, alimentation de labo, oscilloscope, caméra thermique | #84 |

### 1. Résistifs — #85

| Fiche | Fréquence de panne |
| --- | --- |
| 10 Résistance | — |
| 11 Potentiomètre | — |
| 12 Thermistance CTN/CTP | — |
| 13 Résistance fusible et fusible | — |

### 2. Condensateurs — #86

| Fiche | Fréquence de panne |
| --- | --- |
| 20 Condensateur céramique (MLCC) | — |
| 21 Condensateur film | — |
| 22 Condensateur électrolytique aluminium | — |
| 23 Condensateur tantale | — |
| 24 Supercondensateur | — |

### 3. Magnétiques — #87

| Fiche | Fréquence de panne |
| --- | --- |
| 30 Inductance | — |
| 31 Self de mode commun | — |
| 32 Transformateur | — |
| 33 Relais | — |

### 4. Diodes — #88

| Fiche | Fréquence de panne |
| --- | --- |
| 40 Diode de redressement | — |
| 41 Diode Schottky | — |
| 42 Diode Zener | — |
| 43 LED | — |
| 44 Diode TVS | — |
| 45 Pont redresseur | — |
| 46 Varicap | — |

### 5. Transistors — #89

| Fiche | Fréquence de panne |
| --- | --- |
| 50 Transistor bipolaire NPN/PNP | — |
| 51 Darlington | — |
| 52 MOSFET canal N/P | — |
| 53 JFET | — |
| 54 IGBT | — |
| 55 Thyristor et triac | — |

### 6. Circuits intégrés simples — #90

| Fiche | Fréquence de panne |
| --- | --- |
| 60 Optocoupleur | — |
| 61 Régulateur linéaire (78xx, LDO) | — |
| 62 Référence TL431 | — |
| 63 Quartz et oscillateur | — |
| 64 NE555 | — |

### 7. Circuits intégrés analogiques et de puissance — #91

| Fiche | Fréquence de panne |
| --- | --- |
| 70 Amplificateur opérationnel | — |
| 71 Comparateur | — |
| 72 Régulateur à découpage | — |
| 73 Driver de MOSFET | — |

### 8. Circuits intégrés numériques et complexes — #92

| Fiche | Fréquence de panne |
| --- | --- |
| 80 Portes logiques | — |
| 81 EEPROM | — |
| 82 Microcontrôleur | — |
| 83 Boîtier BGA | — |

### 9. Techniques à l'échelle de la carte — #93

| Fiche | Fréquence de panne |
| --- | --- |
| 90 Inspection visuelle | — |
| 91 Contrôle des rails d'alimentation | — |
| 92 Recherche de court-circuit et injection de courant | — |
| 93 Traçage de signal et comparaison avec une carte saine | — |

## Index des techniques

Chaque technique renvoie aux fiches qui l'utilisent ; l'index se remplit avec les fiches.

| Technique | Fiche de base | Utilisée dans |
| --- | --- | --- |
| Ohmmètre | 01 | — |
| Bipeur (continuité) | 01 | — |
| Mode diode | 01 | — |
| Capacimètre | 01 | — |
| Lever une patte | 02 | — |
| Mesure ESR | 03 | — |
| Chute de tension sous tension | 02 | — |
| Injection de courant | 92 | — |

## Licence

Ces fiches sont sous [CC BY-SA 4.0](LICENSE).
