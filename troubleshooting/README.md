# Dépannage électronique

Savoir, à l'établi, si un composant monté sur un PCB est mort ou vivant : des passifs aux circuits intégrés, avec le comportement du multimètre expliqué à chaque fois.

## Comment lire ces fiches

- **Public** : amateur débutant à intermédiaire. Un multimètre et une alimentation limitée en courant (fiche [00](00_securite/README.md)) suffisent pour les niveaux 1 à 3 ; le niveau 4 demande d'autres instruments (section [Appareils de mesure et de test](#appareils-de-mesure-et-de-test--84)).
- **Basse tension uniquement** : aucune tension supérieure à 50 V continu (25 V alternatif) **nulle part sur la carte**, pas seulement à l'entrée. Un appareil sur pile ou sur adaptateur peut en produire bien plus (flash photo vers 300 V, onduleur de rétroéclairage, PoE jusqu'à 57 V, batterie 48 V chargée à 54,6 V) : hors périmètre. Un appareil dont l'alimentation secteur est intégrée se confie à un professionnel, en attendant la fiche secteur et isolement.
- **Niveaux** dans chaque fiche de composant : 1 inspection par les sens (vue, odeur, échauffement), 2 mesure hors circuit, 3 mesure en circuit, 4 méthodes avancées.
- **Fréquence de panne** : un classement qualitatif (très fréquent, fréquent, occasionnel, rare) tiré du consensus des réparateurs et des notes de fabricants, sources citées dans chaque fiche. Ce n'est pas une statistique. Dans le menu, il dit à quelle fréquence ce composant est le coupable d'une panne ; dans une fiche, à quelle fréquence chaque mode de défaillance survient.
- Chaque fiche de composant (familles 1 à 8) suit le [gabarit](gabarit.md) ; les fiches de base (partie 0) et les fiches de techniques (partie 9) ont un plan propre, sans niveaux 1 à 4. Chaque fiche renvoie aux fiches de base de la partie 0 au lieu d'en répéter le contenu. Les pages d'appareils (dossiers `iN_nom`) ont un plan propre, sans gabarit (sauf sa règle des figures, `guide_iN.py`), et présentent un instrument : ce qu'il apporte par rapport au multimètre et quand il vaut la dépense.

## Menu

Du plus simple au plus complexe. Une ligne sans lien est une fiche à venir ; son issue la suit.

### 0. Bases (à lire en premier)

| Fiche | Contenu | Issue |
| --- | --- | --- |
| [00 Sécurité](00_securite/README.md) | Périmètre basse tension, hors tension, décharge des condensateurs, alimentation limitée en courant | #81 |
| [01 Comprendre son multimètre](01_multimetre/README.md) | Ce que chaque mode injecte ; pourquoi un condensateur bipe puis se tait, ce qu'affiche le mode diode | #82 |
| [02 Pièges de la mesure en circuit](02_pieges_en_circuit/README.md) | Chemins parallèles, jonctions qui conduisent, condensateurs qui se chargent, quand dessouder | #83 |
| [03 Méthode de dépannage d'une carte](03_methode/README.md) | Ordre de recherche d'une panne : symptôme, causes extérieures, inspection, rails hors tension, mise sous tension limitée, rails, réduction de la zone, contrôle après réparation | #144 |

### Appareils de mesure et de test — #84

Une page par instrument : ce qu'il est, comment le choisir et l'entretenir. Le comportement des modes du multimètre reste dans la fiche 01.

| Page | Contenu | Issue |
| --- | --- | --- |
| [i1 Le multimètre](i1_multimetre/README.md) | Anatomie, caractéristiques (points, précision, impédance, TRMS, CAT), types, choix, entretien et contrôle des fusibles | #103 |
| [i2 L'oscilloscope](i2_oscilloscope/README.md) | Ce qu'il apporte, anatomie, caractéristiques (bande passante, échantillonnage), sondes et compensation, pince de masse et terre, déclenchement, choix | #104 |
| i3 Vérificateur d'absence de tension (VAT) | — | #105 |
| i4 Pince ampèremétrique | — | #106 |
| i5 LCR-mètre et ESR-mètre | — | #107 |
| i6 Testeur de composants | — | #108 |
| i7 Alimentation de laboratoire | — | #109 |
| i8 Caméra thermique | — | #110 |

### 1. Résistifs — #85

| Fiche | Fréquence de panne |
| --- | --- |
| [10 Résistance](10_resistance/README.md) | fréquent |
| [11 Potentiomètre](11_potentiometre/README.md) | fréquent |
| [12 Thermistance CTN/CTP](12_thermistance/README.md) | occasionnel |
| [13 Résistance fusible et fusible](13_fusible/README.md) | fréquent |
| [14 Sonde à résistance de platine (PT1000)](14_sonde_platine/README.md) | rare |

### 2. Condensateurs — #86

| Fiche | Fréquence de panne |
| --- | --- |
| [20 Condensateur céramique (MLCC)](20_condensateur_ceramique/README.md) | fréquent |
| [21 Condensateur film](21_condensateur_film/README.md) | occasionnel |
| [22 Condensateur électrolytique aluminium](22_condensateur_electrolytique/README.md) | très fréquent |
| [23 Condensateur tantale](23_condensateur_tantale/README.md) | fréquent |
| [24 Supercondensateur](24_supercondensateur/README.md) | occasionnel |

### 3. Magnétiques — #87

| Fiche | Fréquence de panne |
| --- | --- |
| [30 Inductance](30_inductance/README.md) | rare |
| [31 Self de mode commun](31_self_de_mode_commun/README.md) | rare |
| [32 Transformateur](32_transformateur/README.md) | rare |
| [33 Relais](33_relais/README.md) | fréquent |

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

### 6. Circuits intégrés simples et quartz — #90

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

L'ordre dans lequel les employer est donné par la fiche [03](03_methode/README.md).

| Fiche | Contenu | Issue |
| --- | --- | --- |
| [90 Inspection visuelle](90_inspection_visuelle/README.md) | Joints de brasure, composants, connecteurs, interrupteurs, corrosion, pistes, contrôle mécanique | #93 |
| [91 Contrôle des rails d'alimentation](91_rails_alimentation/README.md) | Résistance des rails hors tension, première mise sous tension, tensions, ondulation, mesure de courant | #93 |
| [92 Recherche de court-circuit et injection de courant](92_court_circuit/README.md) | Division du rail, injection à courant limité, point chaud, suivi des millivolts | #93 |
| [93 Traçage de signal et comparaison avec une carte saine](93_tracage_signal/README.md) | Suivre un signal étage par étage, étage qui charge sa sortie, comparer point par point, échanger les éléments identiques | #93 |

## Index des techniques

Chaque technique renvoie aux fiches qui l'utilisent ; l'index se remplit avec les fiches.

| Technique | Fiche de base | Utilisée dans |
| --- | --- | --- |
| Décharge d'un condensateur | [00](00_securite/README.md) | [10](10_resistance/README.md), [11](11_potentiometre/README.md), [12](12_thermistance/README.md), [13](13_fusible/README.md), [14](14_sonde_platine/README.md), [20](20_condensateur_ceramique/README.md), [21](21_condensateur_film/README.md), [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md), [24](24_supercondensateur/README.md), [30](30_inductance/README.md), [31](31_self_de_mode_commun/README.md), [32](32_transformateur/README.md), [33](33_relais/README.md) |
| Alimentation limitée en courant | [00](00_securite/README.md) | [10](10_resistance/README.md), [11](11_potentiometre/README.md), [12](12_thermistance/README.md), [13](13_fusible/README.md), [14](14_sonde_platine/README.md), [20](20_condensateur_ceramique/README.md), [21](21_condensateur_film/README.md), [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md), [24](24_supercondensateur/README.md), [30](30_inductance/README.md), [31](31_self_de_mode_commun/README.md), [32](32_transformateur/README.md), [33](33_relais/README.md) |
| Voltmètre (tensions sous tension) | [01](01_multimetre/README.md) | [10](10_resistance/README.md), [11](11_potentiometre/README.md), [12](12_thermistance/README.md), [13](13_fusible/README.md), [14](14_sonde_platine/README.md), [20](20_condensateur_ceramique/README.md), [21](21_condensateur_film/README.md), [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md), [24](24_supercondensateur/README.md), [30](30_inductance/README.md), [31](31_self_de_mode_commun/README.md), [32](32_transformateur/README.md), [33](33_relais/README.md) |
| Ohmmètre | [01](01_multimetre/README.md) | [10](10_resistance/README.md), [11](11_potentiometre/README.md), [12](12_thermistance/README.md), [13](13_fusible/README.md), [14](14_sonde_platine/README.md), [20](20_condensateur_ceramique/README.md), [21](21_condensateur_film/README.md), [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md), [24](24_supercondensateur/README.md), [30](30_inductance/README.md), [31](31_self_de_mode_commun/README.md), [32](32_transformateur/README.md), [33](33_relais/README.md), [93](93_tracage_signal/README.md) |
| Bipeur (continuité) | [01](01_multimetre/README.md) | [10](10_resistance/README.md), [11](11_potentiometre/README.md), [12](12_thermistance/README.md), [13](13_fusible/README.md), [14](14_sonde_platine/README.md), [20](20_condensateur_ceramique/README.md), [21](21_condensateur_film/README.md), [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md), [24](24_supercondensateur/README.md), [90](90_inspection_visuelle/README.md) |
| Mode diode | [01](01_multimetre/README.md) | [13](13_fusible/README.md), [14](14_sonde_platine/README.md), [24](24_supercondensateur/README.md), [93](93_tracage_signal/README.md) |
| Capacimètre | [01](01_multimetre/README.md) | [20](20_condensateur_ceramique/README.md), [21](21_condensateur_film/README.md), [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md), [24](24_supercondensateur/README.md) |
| Lever une patte | [02](02_pieges_en_circuit/README.md) | [10](10_resistance/README.md), [11](11_potentiometre/README.md), [12](12_thermistance/README.md), [21](21_condensateur_film/README.md), [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md), [30](30_inductance/README.md), [93](93_tracage_signal/README.md) |
| Mesure ESR | i5 | [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md), [24](24_supercondensateur/README.md) |
| Chute de tension sous tension | [02](02_pieges_en_circuit/README.md) | [10](10_resistance/README.md), [12](12_thermistance/README.md), [13](13_fusible/README.md), [20](20_condensateur_ceramique/README.md), [23](23_condensateur_tantale/README.md), [33](33_relais/README.md) |
| Résistance d'un rail à la masse, hors tension | [91](91_rails_alimentation/README.md) | [03](03_methode/README.md), [10](10_resistance/README.md), [13](13_fusible/README.md), [20](20_condensateur_ceramique/README.md), [22](22_condensateur_electrolytique/README.md), [23](23_condensateur_tantale/README.md) |
| Mesure de courant | [91](91_rails_alimentation/README.md) | [03](03_methode/README.md), [13](13_fusible/README.md) |
| Injection de courant | [92](92_court_circuit/README.md) | [03](03_methode/README.md), [13](13_fusible/README.md), [20](20_condensateur_ceramique/README.md), [23](23_condensateur_tantale/README.md) |
| Inspection visuelle | [90](90_inspection_visuelle/README.md) | [03](03_methode/README.md), [92](92_court_circuit/README.md) |
| Traçage de signal, comparaison avec une carte saine | [93](93_tracage_signal/README.md) | [01](01_multimetre/README.md), [02](02_pieges_en_circuit/README.md), [03](03_methode/README.md), [14](14_sonde_platine/README.md), [20](20_condensateur_ceramique/README.md), [21](21_condensateur_film/README.md) |
| Mesure 4 fils (Kelvin) | [10](10_resistance/README.md) | [10](10_resistance/README.md), [30](30_inductance/README.md), [32](32_transformateur/README.md) |
| Test d'oscillation (spires en court-circuit) | [30](30_inductance/README.md) | [30](30_inductance/README.md), [32](32_transformateur/README.md) |
| Rapport de transformation | [32](32_transformateur/README.md) | [32](32_transformateur/README.md) |
| Chute de tension d'un contact sous courant | [33](33_relais/README.md) | [33](33_relais/README.md) |
| Pont LCR (inductance) | i5 | [30](30_inductance/README.md), [31](31_self_de_mode_commun/README.md), [32](32_transformateur/README.md) |
| Oscilloscope | [i2](i2_oscilloscope/README.md) | [11](11_potentiometre/README.md), [13](13_fusible/README.md), [14](14_sonde_platine/README.md), [20](20_condensateur_ceramique/README.md), [21](21_condensateur_film/README.md), [22](22_condensateur_electrolytique/README.md), [30](30_inductance/README.md), [31](31_self_de_mode_commun/README.md), [32](32_transformateur/README.md), [33](33_relais/README.md), [93](93_tracage_signal/README.md) |

## Licence

Ces fiches sont sous [CC BY-SA 4.0](LICENSE).
