# GreenMove Logistics - Plateforme Télématique Edge Computing (GML-Edge)

Projet de pivot technique **Edge Computing** pour la flotte de 50 camions GreenMove Logistics. Cette solution embarquée sur tablette durcie IoT réunit le **Moteur ZFE (Geo)** et le **Moteur Safety (Physics)** pour garantir la conformité réglementaire ZFE et débloquer les 20% de remise sur la prime d'assurance avec *AssurezMoi*.

---

## 📐 Architecture & Périmètre des Modules

### 1. Module 1 : Conformité ZFE (`zfe_engine.py`)
- **Algorithme** :
  1. **Bounding Box (\\(O(1)\\))** : Filtrage ultra-rapide par enveloppe englobante pour rejeter instantanément les positions GPS hors zone.
  2. **Ray Casting (\\(O(V)\\))** : Calcul géométrique du franchissement de polygone pour la détection précise d'entrée en ZFE.
- **Performance** : Exécution streaming sans boucles imbriquées (\\(O(N^2)\\) proscrit), garantissant la fluidité sur processeur **Snapdragon 660** et une consommation RAM de ~15 Mo (plafond autorisé : 150 Mo).

### 2. Module 2 : Sécurité & Scoring Assurance (`safety_engine.py`)
- **Analyse Physique** : Traitement streaming du fichier accélérométrique `accelerometer_data.csv` (axe Y longitudinal).
- **Filtrage de Bruit & Seuil** : Détection des freinages violents pour toute décélération \\(> 2.5 \text{ m/s}^2\\) (\\(acc\_y < -2.5 \text{ m/s}^2\\)).
- **Exportation de Preuve** : Génération automatique du fichier `daily_score.json` contenant la note de conduite quotidienne et la liste horodatée des événements pour l'assureur.

---

## Arborescence du Dépôt Git

```text
code_moteur_saad/
├── zfe_engine.py          # Module 1 : Géofencing ZFE (Geo)
├── safety_engine.py       # Module 2 : Détection d'événements & Scoring (Physics)
├── main_engine.py         # Script principal réunissant les deux moteurs
├── lyon_polygon.json      # Polygone de la ZFE de Lyon (Annexe 3)
├── truck_gps.json         # Trace GPS du camion (Annexe 3)
├── accelerometer_data.csv # Données accélérométriques brutes (Annexe 3)
├── daily_score.json       # Rapport quotidien généré (Format AssurezMoi)
└── README.md              # Documentation technique et procédures



1. Tester le Module 1 (ZFE Geo)
python zfe_engine.py lyon_polygon.json truck_gps.json

2. Tester le Module 2 (Safety Physics)
python safety_engine.py accelerometer_data.csv daily_score.json

3. Exécuter la Plateforme Globale Unifiée
python main_engine.py


Résultat Attendu sur Console
======================================================================
   GREENMOVE LOGISTICS - PLATEFORME TÉLÉMATIQUE EMBARQUÉE (EDGE)   
======================================================================

---> EXECUTION MODULE 1 : CONFORMITÉ ZFE (GEO)
[STATUS OUT] ID 1 | 08:00:00 | Lat: 45.81, Lon: 4.75 -> Hors Bounding Box
[STATUS OUT] ID 2 | 08:00:10 | Lat: 45.8, Lon: 4.78 -> Hors Bounding Box
[STATUS OUT] ID 3 | 08:00:20 | Lat: 45.785, Lon: 4.805 -> Dans Bounding Box mais HORS ZFE (Attendu: IN (Bordure))
[ALERT ZFE] ID 4 | 08:00:30 | Lat: 45.76, Lon: 4.8357 -> VÉHICULE EN ZFE ! (Attendu: IN (Centre ZFE))
[ALERT ZFE] ID 5 | 08:00:40 | Lat: 45.75, Lon: 4.85 -> VÉHICULE EN ZFE ! (Attendu: IN)

---> EXECUTION MODULE 2 : SÉCURITÉ & SCORING ASSURANCE (PHYSICS)
[MODULE SAFETY] Analyse terminée : 10 enregistrements | 1 événement(s) détecté(s) | Score: 90/100
[MODULE SAFETY] Rapport exporté dans 'daily_score.json'

======================================================================
   SYNTHÈSE EMBARQUÉE DE LA SESSION DE CONDUITE
======================================================================
• Alertes ZFE franchies : 2 événement(s)
• Freinages violents (> 2.5 m/s²) : 1 événement(s)
• Score de conduite global : 90/100
• Éligibilité Bonus AssurezMoi (20%) : OUI
======================================================================