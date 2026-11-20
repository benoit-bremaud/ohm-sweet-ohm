# 02 Pièges de la mesure en circuit

Pourquoi un composant soudé sur la carte ne se mesure pas comme un composant seul, comment reconnaître une lecture faussée par le reste du circuit, et quand il faut lever une patte.

## En bref

En circuit, l'ohmmètre mesure le composant **et tout ce qui est branché en parallèle** : résistances, jonctions de semi-conducteurs, condensateurs. Ces chemins ne peuvent que **faire baisser** la lecture. D'où la règle centrale : une valeur stabilisée **au-dessus** de la valeur nominale (tolérance comprise), relevée sur des pattes propres et un circuit déchargé, est concluante : le composant est défectueux ; une valeur **en dessous** ne prouve rien tant qu'on n'a pas écarté les chemins parallèles. Pour trancher : inverser les pointes, monter d'un calibre, raisonner sur le schéma, comparer avec une carte saine, ou lever une patte. Sous tension, le voltmètre complète ces mesures par la chute de tension aux bornes des composants.

> **Sécurité** : ohmmètre, bipeur, mode diode et capacimètre se font **hors tension**, piles retirées, condensateurs déchargés et vérifiés au voltmètre ; les mesures sous tension se font par une alimentation limitée en courant, et seulement si aucune tension ne dépasse 50 V continu ni 25 V alternatif sur la carte (fiche [00](../00_securite/README.md)). Le fonctionnement de chaque mode du multimètre est expliqué en fiche [01](../01_multimetre/README.md).

## Les chemins parallèles : une lecture trop basse ne prouve rien

Les deux pointes touchent deux **nœuds** du circuit, pas deux pattes d'un composant isolé. Tout ce qui relie ces deux nœuds se retrouve en parallèle du composant mesuré, et deux résistances en parallèle donnent toujours une valeur plus faible que la plus faible des deux : *R = R1 × R2 / (R1 + R2)*.

![Multimètre sur Ω, calibre 20 kΩ : le courant de test se partage entre R1 et R2, l'appareil lit 5 kΩ pour une résistance de 10 kΩ saine ; la jonction est bloquée dans ce sens des pointes ; au-dessus de la nominale, la lecture est concluante, en dessous elle est ambiguë](chemins-paralleles.svg)

| Composant mesuré | En parallèle sur la carte | Lecture |
| --- | --- | --- |
| 10 kΩ | rien | 10 kΩ |
| 10 kΩ | 10 kΩ | 5 kΩ |
| 10 kΩ | 1 kΩ | 0,91 kΩ |
| 10 kΩ ouverte (coupée) | 22 kΩ | 22 kΩ |

La dernière ligne montre le piège inverse : une résistance coupée ne lit pas forcément « OL », elle lit le chemin parallèle. Ici sa lecture reste **au-dessus** de 10 kΩ, ce qui suffit à la condamner ; avec un chemin parallèle de 4,7 kΩ, la même résistance coupée lirait 4,7 kΩ et rien ne serait prouvé.

**Règle de lecture**. Elle vaut pour une valeur stabilisée et reproduite, multimètre vérifié, cordons soustraits sous 10 Ω, pointes posées sur le **métal propre des pattes** du composant (pas sur les pastilles, ni sur du flux ou du vernis), et quelques mV au plus entre les deux nœuds, contrôlés au voltmètre juste avant la mesure :

- **Au-dessus de la nominale plus la tolérance** (et la précision de l'appareil) : défaut, quel que soit le reste du circuit : composant coupé ou dérivé. C'est la seule conclusion ferme qu'une mesure en circuit donne. Un contact de pointe sale ou une charge résiduelle font aussi lire trop haut, d'où les conditions ci-dessus.
- **Proche de la nominale** : probablement sain, un chemin parallèle de valeur bien plus élevée ne changeant presque rien. Sauf si le schéma annonce une valeur plus basse : dans l'exemple du tableau, on attend 5 kΩ ; lire 10 kΩ voudrait dire que l'une des deux résistances est coupée.
- **En dessous de la nominale** : ambigu. Le composant peut être sain et shunté, ou bien en court-circuit. Suivre l'arbre de décision.

Une soudure fissurée ne se voit pas pointes sur les pattes : la contrôler au bipeur entre chaque patte et sa pastille.

**Raisonner sur le schéma** : quand on l'a, repérer tout ce qui relie les deux nœuds et calculer la valeur attendue en parallèle. Une lecture égale à ce calcul est normale.

## Les jonctions qui conduisent

Une diode, une jonction de transistor ou les diodes de protection internes d'un circuit intégré peuvent se trouver entre les deux nœuds. L'ohmmètre les fait conduire quand la tension à ses pointes, environ *I × R*, approche 0,4 à 0,5 V (le mécanisme et ses ordres de grandeur sont en fiche [01](../01_multimetre/README.md), « Ohmmètre »).

![Même montage, deux positions du sélecteur : sur le calibre 20 kΩ la jonction conduit vers 0,45 V et l'appareil lit 4,5 kΩ ; sur le calibre 200 kΩ la tension reste à 0,1 V et il lit 10 kΩ](jonction-calibre.svg)

Comment le reconnaître :

- **Inverser les pointes** : une résistance seule lit la même valeur dans les deux sens. Une lecture qui change avec la polarité signale une jonction (ou un condensateur qui se charge, section suivante). La lecture la plus haute des deux est la plus proche de la résistance seule, sans la garantir.
- **Monter d'un calibre** (touche RANGE ou sélecteur) : le courant de test est à peu près divisé par dix, la tension aux pointes aussi, et la jonction se bloque. Une lecture qui remonte vers la valeur attendue signale une jonction qui conduisait. Le calibre le plus bas qui affiche encore la valeur est celui qui applique la tension la plus haute : c'est le pire en circuit. On y perd un chiffre de résolution. Les valeurs de la figure sont des ordres de grandeur pour une diode de signal au silicium.
- **Mode diode entre les mêmes nœuds** : une lecture de 0,3 à 0,7 V dans un sens confirme qu'une jonction est en parallèle.

## Les condensateurs qui se chargent

Un condensateur entre les deux nœuds se charge sous le courant de l'ohmmètre : la lecture part bas et **monte** jusqu'à la valeur des chemins résistifs (fiche [01](../01_multimetre/README.md), « Ohmmètre » et « Bipeur »). La montée suit la constante de temps *τ = R × C* et demande 3 à 5 τ : 10 kΩ et 470 µF donnent τ ≈ 5 s, soit 15 à 25 s d'attente ; avec 100 kΩ, plusieurs minutes.

- **Attendre que la lecture se stabilise** avant de la comparer à quoi que ce soit ; une lecture qui monte n'est pas un court-circuit.
- Inverser les pointes recommence la montée : la première valeur lue après inversion n'a pas de sens.
- Le **capacimètre** en circuit lit la somme des condensateurs en parallèle, faussée par les résistances et les jonctions qui les déchargent : une valeur en circuit n'est qu'un indice. Une capacité nettement **inférieure** à celle du seul condensateur mesuré reste toutefois suspecte, car les autres condensateurs en parallèle ne peuvent que l'augmenter ; l'ESR se mesure à l'ESR-mètre (page i5).
- Décharger les condensateurs avant chaque série de mesures (fiche [00](../00_securite/README.md)) et viser quelques mV au voltmètre, pas seulement le seuil de sécurité : l'ohmmètre travaille sous quelques dixièmes de volt, une charge résiduelle de même ordre lui fait lire n'importe quoi. Une lecture négative, qui descend ou qui dérive très lentement en est le signe.

## Ohmmètre basse tension : la tension à pleine échelle

Pour mesurer une résistance sans faire conduire les jonctions, il faut que la tension aux pointes reste sous environ 0,3 V pendant la mesure. Deux caractéristiques comptent :

- la **tension à vide**, atteinte pointes en l'air ou sur une valeur hors calibre (relevée par l'exercice de la fiche [01](../01_multimetre/README.md)) ;
- la **tension à pleine échelle**, atteinte quand la résistance mesurée remplit le calibre. Pour la relever : une résistance vers 90 % du calibre entre les pointes (1,8 kΩ sur le calibre 2 kΩ, 18 kΩ sur 20 kΩ, 3,6 kΩ sur un calibre 4 kΩ) et un second multimètre en voltmètre continu à ses bornes. Un appareil dont la tension à pleine échelle reste sous 0,3 V ne fait pas conduire de jonction au silicium sur les calibres jusqu'à quelques dizaines de kΩ, tant que la lecture n'est pas hors calibre ; sur les calibres de centaines de kΩ et de MΩ, le courant de test est si faible que la fuite d'une jonction fausse encore la lecture, même sous 0,3 V.

Les appareils qui proposent un calibre « basse puissance » (*low power ohms*) ou qui limitent la tension à pleine échelle sont les plus fiables en circuit. Sur un appareil premier prix, passer en calibre manuel, monter d'un calibre au-dessus de celui que choisit le mode automatique et comparer les deux lectures, dans les deux polarités. Une diode Schottky ou une jonction au germanium conduit dès 0,15 à 0,2 V : même un ohmmètre basse tension peut la faire conduire.

## Quand lever une patte

Lever une patte (dessouder une seule broche pour isoler le composant) coûte du temps et fatigue la pastille. On le fait quand :

- la lecture est **en dessous** de la nominale et que ni l'inversion des pointes, ni le schéma, ni une carte saine ne permettent de trancher ;
- on veut une mesure qu'aucun chemin parallèle ne doit fausser : capacité ou ESR exacte, fuite d'un condensateur, gain d'un transistor ;
- plusieurs composants identiques sont en parallèle (condensateurs de découplage, MOSFET en parallèle) et on cherche lequel est en court-circuit : l'ohmmètre seul ne peut pas les distinguer. Avant de dessouder, essayer la chute de tension le long du rail (fiche [92](../92_court_circuit/README.md)).

**Quelle patte** : pour un composant à deux bornes, lever l'une ou l'autre suffit à couper la boucle ; choisir celle qui se dessoude le plus facilement, c'est-à-dire **pas celle reliée à un plan de masse ou d'alimentation**, qui absorbe la chaleur. Transistor bipolaire : lever la base isole les jonctions base-émetteur et base-collecteur (le trajet collecteur-émetteur reste en circuit). MOSFET : la grille n'a pas de jonction ; lever le drain ou la source (souvent la source : sur les boîtiers de puissance, le drain est la languette soudée au cuivre) pour tester le trajet drain-source et la diode interne, et relier un instant grille et source avant la mesure, car une grille en l'air peut rester chargée et rendre le canal passant : un MOSFET sain lirait alors comme un court-circuit. Un circuit intégré se teste sous tension ou se remplace, pas en levant ses broches.

![Multimètre sur Ω, calibre 20 kΩ. Avant : deux pattes soudées, 3,2 kΩ lus, la résistance en parallèle avec le circuit. Après : patte côté signal levée, 10 kΩ lus, la résistance seule](lever-une-patte.svg)

**Le geste** :

1. Carte hors tension, condensateurs déchargés (fiche [00](../00_securite/README.md)).
2. **Traversant** : retirer la soudure du côté pastille (pompe ou tresse), redresser la patte si elle est rabattue sous la carte, chauffer la pastille et soulever la patte de quelques millimètres avec une pince, sans tirer sur une pastille froide : elle s'arrache avec sa piste.
3. **CMS** (composant monté en surface, résistance 0603, 0805…) : chauffer une seule extrémité et la soulever à la pince, ou retirer le composant (deux fers, pince chauffante ou air chaud) et le mesurer seul. Un condensateur céramique se retire toujours entier, sans faire levier : le soulever par un bout risque de le fissurer (fiche [20](../20_condensateur_ceramique/README.md)).
4. Mesurer entre la patte levée et l'autre borne du composant, **pas** la pastille.
5. Ressouder, puis vérifier la continuité entre la patte et la piste.

## Mesurer la chute de tension sous tension

Le voltmètre est, avec l'ampèremètre (fiche [91](../91_rails_alimentation/README.md)), le seul mode qui se branche sur une carte alimentée (fiche [01](../01_multimetre/README.md)), et les chemins parallèles ne le gênent pas : il lit la tension qui existe réellement entre deux points. Carte alimentée par une alimentation limitée en courant (fiche [00](../00_securite/README.md)), une seule pointe tenue, l'autre fixée par un grippe-fil quand c'est possible pour qu'elle ne glisse pas entre deux broches :

![Multimètre sur V continu, pointes de part et d'autre d'un fusible parcouru par le courant : 12 mV lus, contact sain ; des centaines de mV signalent un contact résistant, toute la tension d'alimentation un fusible ouvert](chute-de-tension.svg)

| Où mesurer | Lecture attendue | Ce qu'un écart signale |
| --- | --- | --- |
| Aux bornes d'une résistance | *V = R × I*, à comparer au schéma ou à une carte saine | 0 V : aucun courant (circuit coupé en amont ou en aval, ou résistance en court-circuit) ; tension trop haute : trop de courant, résistance dérivée vers le haut, ou résistance coupée (toute la tension disponible à ses bornes) |
| Aux bornes d'un fusible, d'un interrupteur fermé, d'un connecteur | quelques mV à quelques dizaines de mV ; davantage pour un fusible de faible calibre ou réarmable (PTC) : comparer à sa fiche technique ou à une carte saine | Plusieurs centaines de mV : contact résistant ou fusible fatigué ; tension d'alimentation complète : ouvert |
| Le long d'une piste ou d'un plan de masse | quelques mV ; une piste longue et fine peut chuter 10 à 20 mV vers 100 mA en service normal | Nettement plus que sur la carte saine : un courant anormal y passe ; la tension diminue en approchant du court-circuit (fiche [92](../92_court_circuit/README.md)) |
| Base-émetteur d'un transistor bipolaire au silicium qui conduit | 0,6 à 0,7 V (1,2 à 1,4 V pour un Darlington) | Nettement plus haut : jonction ouverte ; 0 V alors qu'il devrait conduire : pas de commande, ou jonction en court-circuit |
| Aux bornes d'une diode qui conduit | 0,6 à 1 V (silicium), 0,2 à 0,5 V (Schottky) | Proche de 0 V : diode en court-circuit, ou aucun courant |

La chute de tension évite de dessouder un fil pour insérer un ampèremètre : le courant dans une résistance de valeur connue vaut *I = V / R*.

## Comparer avec une carte saine

Quand on dispose d'une carte identique qui fonctionne (ou d'un canal identique sur la même carte : voie gauche et voie droite d'un amplificateur, phases d'un régulateur), les mêmes chemins parallèles existent des deux côtés : la comparaison neutralise le piège. Mesurer les **mêmes points**, avec le **même appareil**, sur le **même calibre**, dans la **même polarité**, les deux cartes hors tension et déchargées. Un écart net (au-delà de quelques pour cent sur une résistance) désigne la zone à examiner. Méthode complète : fiche 93.

## Arbre de décision : que vaut cette lecture en circuit ?

```mermaid
flowchart TD
  A[Résistance mesurée en circuit, hors tension, condensateurs déchargés] --> B{La lecture est-elle stable ?}
  B -- non, elle monte --> C[Condensateur qui se charge : attendre 3 à 5 τ]
  C --> B
  B -- non, elle descend ou est négative --> M[Charge résiduelle : décharger, fiche 00, puis reprendre]
  M --> B
  B -- oui --> D{Comparée à la nominale plus tolérance}
  D -- au-dessus --> E[Composant défectueux : coupé ou dérivé]
  D -- proche --> N{Schéma ou carte saine disponible ?}
  N -- non --> F[Probablement sain]
  N -- oui --> I
  D -- en dessous --> G{Même valeur pointes inversées et sur le calibre au-dessus ?}
  G -- non --> H{Jonction en parallèle : lecture stable d'un calibre à l'autre en montant, ou à l'ohmmètre basse tension ?}
  H -- oui, reprendre avec cette lecture --> D
  H -- non --> J
  G -- oui --> I{Égale au calcul des chemins parallèles ou à la carte saine ?}
  I -- oui --> F
  I -- non ou impossible à savoir --> J[Lever une patte et mesurer le composant seul]
  J --> K{Lecture seule correcte ?}
  K -- oui --> L[Le défaut est ailleurs sur le nœud : chute de tension sous tension, fiche 92]
  K -- non --> O[Composant défectueux : en court-circuit, coupé ou dérivé]
```

## Aide-mémoire d'établi

- En circuit, l'ohmmètre mesure le nœud, pas le composant.
- Les chemins parallèles ne font que baisser la lecture : au-dessus de la nominale plus la tolérance, pointes sur des pattes propres = composant défectueux.
- En dessous de la nominale : rien de prouvé.
- Inverser les pointes : valeur différente = jonction ou condensateur.
- Lecture qui monte = condensateur qui se charge : attendre 3 à 5 τ. Lecture qui descend ou négative = charge résiduelle : décharger.
- Jonctions : monter d'un calibre, ou ohmmètre à tension à pleine échelle sous 0,3 V ; Schottky dès 0,15 V.
- Lever la patte la plus facile à dessouder, jamais tirer une pastille froide ; mesurer la patte, pas la pastille.
- Sous tension, sélecteur sur V continu : le voltmètre lit la vraie chute, *I = V / R*, quelques mV sur un contact fermé.
- Carte saine : mêmes points, même appareil, même calibre, même polarité.

## Sources

- Fluke, *How to measure resistance with a digital multimeter* (mesure hors tension, chemins parallèles, lever une patte) — <https://www.fluke.com/en-gb/learn/blog/digital-multimeters/how-to-measure-resistance>
- EEVblog forum, *Multimeters with low ohms function* (calibres basse puissance, tensions de test relevées sur divers appareils) — <https://www.eevblog.com/forum/testgear/multimeters-with-low-ohms-function/>
- HKJ (lygte-info.dk), *Multimeter and component testing* (tension à vide et tension à pleine échelle de nombreux appareils) — <https://lygte-info.dk/info/DMMComponentTesting%20UK.html>
- All About Circuits, *Lessons in Electric Circuits*, vol. 1, ch. 8 « Ohmmeter usage » (mesure hors tension, chemins parallèles) et vol. 3, ch. 3 « Meter check of a diode » — <https://www.allaboutcircuits.com/textbook/>
- Fluke, *Voltage drop testing*, note d'application (chute de tension aux bornes des contacts et des connexions sous charge) ; à chercher sous ce titre sur fluke.com.
- Diodes Inc. et Vishay, fiches techniques de diodes Schottky de signal (BAT54, BAT85 : tension directe d'environ 0,3 V à 1 mA).
