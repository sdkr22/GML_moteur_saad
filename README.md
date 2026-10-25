# GreenMove Logistics - Plateforme Télématique Edge Computing (GML-Edge)

Projet de pivot technique **Edge Computing** pour la flotte de 50 camions de **GreenMove Logistics**. 

Cette plateforme embarquée sur tablette durcie IoT réunit le **Moteur ZFE (Geo)** et le **Moteur Safety (Physics)** pour garantir la conformité réglementaire ZFE (évitement des amendes de 375 €) et débloquer **20 % de remise sur la prime d'assurance** avec *AssurezMoi* grâce à la preuve comportementale des chauffeurs.

---

##  Architecture & Périmètre des Modules

### 1. Module 1 : Conformité ZFE (`zfe_engine.py`)
* **Géofencing Autonome (100% Offline)** : Détection d'entrée en Zone à Faible Émission sans aucune dépendance au réseau 4G (ex: sortie du Tunnel de Fourvière).
* **Double Filtrage Géométrique** :
  1. **Bounding Box (\\(O(1)\\))** : Test instantané par enveloppe rectangulaire pour rejeter > 95% des positions hors-zone.
  2. **Ray Casting / Point in Polygon (\\(O(V)\\))** : Calcul vectoriel strict pour valider le franchissement du polygone ZFE.
* **Mesure de Latence Temps Réel** : Chronométrage haute précision via `time.perf_counter()` affichant la latence en microsecondes (ex. **7,30 µs**) au timestamp exact du franchissement (`08:00:30`).
* **Performance Matérielle** : Traitement streaming sans boucles imbriquées (complexité \\(O(N^2)\\) proscrite) pour préserver le processeur **Snapdragon 660** et maintenir une consommation RAM < 15 Mo (plafond : 150 Mo).

---

### 2. Module 2 : Sécurité & Scoring Assurance (`safety_engine.py`)
* **Filtrage du Bruit & Isolation de Signal** : Analyse continue de l'axe longitudinal Y (`acc_y`). L'algorithme filtre les vibrations ordinaires de la route (tolérance de -2.5 à +2.5 m/s²) pour isoler uniquement les pics de freinage violent (`acc_y < -2.5 m/s²`).
* **Exportation Certifiée (`daily_score.json`)** : Génération automatique d'un rapport quotidien structuré contenant la note de conduite sur 100 points. Un score \\(\ge 90/100\\) certifie la conduite prudente et valide l'éligibilité au rabais d'assurance de 20 %.

---

### 3. Résilience & Tolérance aux Pannes (*Crash-Free*)
* **Captation des Exceptions** : Blocs `try/except` protégeant l'application contre les interruptions de service.
* **Données Corrompues** : Les lignes de données invraisemblables ou corrompues (ex: `CORRUPTED_VAL`) sont identifiées, loggées comme avertissements et ignorées sans faire planter le système.
* **Mode Dégradé** : En cas d'absence d'un fichier de carte ou de trace GPS, le système intercepte l'erreur `FileNotFoundError` et informe l'opérateur tout en préservant la stabilité globale.

---

## Arborescence du Dépôt Git

```text
gml-edge-telematics/
├── zfe_engine.py          # Module 1 : Géofencing ZFE (Geo) & Mesure de latence
├── safety_engine.py       # Module 2 : Détection d'événements, Filtrage bruit & Scoring (Physics)
├── main_engine.py         # Orchestrateur principal & Synthèse globale
├── lyon_polygon.json      # Coordonnées du polygone ZFE de Lyon (Annexe 3)
├── truck_gps.json         # Trace GPS du camion avec timestamps (Annexe 3)
├── accelerometer_data.csv # Données accélérométriques brutes avec bruit et anomalies (Annexe 3)
├── daily_score.json       # Rapport quotidien exporté (Format certifié AssurezMoi)
└── README.md              # Documentation technique et guide d'exécution


2. Tester le Module ZFE (Geo)
python zfe_engine.py lyon_polygon.json truck_gps.json
3. Tester le Module Safety (Physics)
python safety_engine.py accelerometer_data.csv daily_score.json
4. Exécuter la Plateforme Globale Unifiée
python main_engine.py

Résultat d'Exécution Console Attendu
===========================================================================
   GREENMOVE LOGISTICS - PLATEFORME TÉLÉMATIQUE EMBARQUÉE (EDGE COMPUTING)   
===========================================================================

---> MODULE 1 : CONFORMITÉ ZFE (GEO) - SUIVI EN TEMPS RÉEL
[STATUS OUT] ID 1 | Timestamp: 08:00:00 | Lat: 45.81, Lon: 4.75 -> HORS ZFE (Hors Bounding Box | Temps: 12.15 µs)
[STATUS OUT] ID 2 | Timestamp: 08:00:10 | Lat: 45.8, Lon: 4.78 -> HORS ZFE (Hors Bounding Box | Temps: 1.93 µs)
[STATUS OUT] ID 3 | Timestamp: 08:00:20 | Lat: 45.785, Lon: 4.805 -> HORS ZFE (Dans Bounding Box mais Hors Polygon | Temps: 52.35 µs)
[ALERT ZFE INSTANTANÉE] ID 4 | Timestamp: 08:00:30 | Lat: 45.76, Lon: 4.8357 -> EN ZFE ! (Temps de détection: 7.30 µs | Attendu: IN (Centre ZFE))
[ALERT ZFE INSTANTANÉE] ID 5 | Timestamp: 08:00:40 | Lat: 45.75, Lon: 4.85 -> EN ZFE ! (Temps de détection: 7.00 µs | Attendu: IN)

---> MODULE 2 : SÉCURITÉ & SCORING ASSURANCE (PHYSICS) - FILTRAGE DU BRUIT

--- [MODULE SAFETY] DÉBUT DU TRAITEMENT DU FICHIER CSV BRUITÉ ---
  ░ [BRUIT / CONDUITE NORMALE] Ligne 1 | acc_y = +0.05 m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)
  ░ [BRUIT / CONDUITE NORMALE] Ligne 2 | acc_y = +0.02 m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)
  ░ [BRUIT / CONDUITE NORMALE] Ligne 3 | acc_y = -0.10 m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)
  ░ [BRUIT / CONDUITE NORMALE] Ligne 4 | acc_y = -0.50 m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)
  ░ [BRUIT / CONDUITE NORMALE] Ligne 5 | acc_y = -0.80 m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)
  ⚡ [SIGNAL ISOLÉ - FREINAGE VIOLENT] Ligne 6 | TS: 1678880005 (11:33:25 UTC) | acc_y = -3.45 m/s² (Décélération: 3.45 m/s² > Seuil 2.5) -> SÉVÉRITÉ: HIGH
  ░ [BRUIT / CONDUITE NORMALE] Ligne 7 | acc_y = -1.20 m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)
  ░ [BRUIT / CONDUITE NORMALE] Ligne 8 | acc_y = -0.10 m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)
  ⚠️ [EXCEPTION GÉRÉE] Ligne 9 ignorée (donnée corrompue/invalide) : could not convert string to float: 'CORRUPTED_VAL'
  ░ [BRUIT / CONDUITE NORMALE] Ligne 10 | acc_y = +0.02 m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)
--- [MODULE SAFETY] RAPPORT EXPORTÉ SANS ERREUR : 'daily_score.json' ---

===========================================================================
   SYNTHÈSE EMBARQUÉE DE LA SESSION DE CONDUITE
===========================================================================
• Positions GPS analysées : 5 (Ignorées/Invalides: 0)
• Alertes ZFE franchies instantanément : 2 événement(s)
   └─ Alerte #1 à 08:00:30 | Pos: (45.76, 4.8357) | Latence détection: 7.3 µs
   └─ Alerte #2 à 08:00:40 | Pos: (45.75, 4.85) | Latence détection: 7.0 µs

• Échantillons accéléromètre analysés : 9 (Lignes corrompues ignorées: 1)
• Freinages violents isolés (> 2.5 m/s²) : 1 événement(s)
• Score de conduite global : 90/100 (EXCELLENT (Bonus 20% Validé))
• Éligibilité Bonus AssurezMoi (20%) : OUI
===========================================================================
✔ Exécution terminée avec succès : la plateforme est stable et résiliente aux exceptions.
===========================================================================