import csv
import json
import os
import sys
from datetime import datetime, timezone

# Seuil de décélération pour freinage violent en m/s² (acc_y < -2.5 m/s²)
HARSH_BRAKING_THRESHOLD = -2.5

def analyze_telematics(csv_filepath="accelerometer_data.csv", output_json_path="daily_score.json"):
    """
    Analyse les données accélérométriques brutes et génère le rapport quotidien de sécurité.
    Complexité O(N) en streaming (O(1) espace mémoire) pour respecter la contrainte Snapdragon 660 / < 150 Mo RAM.
    """
    total_records = 0
    harsh_events = []
    
    if not os.path.exists(csv_filepath):
        print(f"Erreur : Le fichier {csv_filepath} est introuvable.")
        return None

    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_records += 1
            timestamp = int(row["timestamp"])
            acc_x = float(row["acc_x"])
            acc_y = float(row["acc_y"])
            acc_z = float(row["acc_z"])
            
            # Détection de freinage violent : décélération sur l'axe Y sous le seuil (-2.5 m/s²)
            if acc_y < HARSH_BRAKING_THRESHOLD:
                severity = "CRITICAL" if acc_y < -4.0 else "HIGH"
                harsh_events.append({
                    "event_type": "HARSH_BRAKING",
                    "timestamp": timestamp,
                    "formatted_time": datetime.fromtimestamp(timestamp, timezone.utc).strftime('%H:%M:%S UTC'),
                    "acc_x": acc_x,
                    "acc_y": acc_y,
                    "acc_z": acc_z,
                    "deceleration_m_s2": abs(acc_y),
                    "severity": severity
                })
    
    # Calcul du score de conduite (Score de base 100, pénalité de 10 pts par événement lourd)
    event_count = len(harsh_events)
    safety_score = max(0, 100 - (event_count * 10))
    
    if safety_score >= 90:
        score_category = "EXCELLENT (Bonus 20% Validé)"
    elif safety_score >= 75:
        score_category = "ACCEPTABLE (Bonus 10% Validé)"
    else:
        score_category = "A RISQUE (Pas de Bonus)"

    # Structure du rapport JSON conforme aux exigences de l'assureur AssurezMoi
    daily_report = {
        "metadata": {
            "device_id": "GML-TABLET-050",
            "driver_id": "CHAUFFEUR-LYON-01",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sampling_rate_hz": 1
        },
        "summary": {
            "total_records_analyzed": total_records,
            "harsh_braking_events_count": event_count,
            "safety_score": safety_score,
            "score_category": score_category,
            "insurance_bonus_eligible": safety_score >= 90
        },
        "detected_events": harsh_events
    }
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(daily_report, f, indent=2, ensure_ascii=False)
        
    print(f"[MODULE SAFETY] Analyse terminée : {total_records} enregistrements | {event_count} événement(s) détecté(s) | Score: {safety_score}/100")
    print(f"[MODULE SAFETY] Rapport exporté dans '{output_json_path}'")
    return daily_report

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "accelerometer_data.csv"
    json_out = sys.argv[2] if len(sys.argv) > 2 else "daily_score.json"
    analyze_telematics(csv_file, json_out)