import csv
import json
import os
import sys
from datetime import datetime, timezone

HARSH_BRAKING_THRESHOLD = -2.5

def analyze_telematics(csv_filepath="accelerometer_data.csv", output_json_path="daily_score.json"):
    total_records = 0
    valid_records = 0
    corrupted_records = 0
    harsh_events = []

    print(f"\n--- [MODULE SAFETY] DÉBUT DU TRAITEMENT DU FICHIER CSV BRUITÉ ---")

    try:
        if not os.path.exists(csv_filepath):
            raise FileNotFoundError(f"Fichier accéléromètre introuvable : {csv_filepath}")

        with open(csv_filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_idx, row in enumerate(reader, start=1):
                total_records += 1
                try:
                    ts = int(row["timestamp"])
                    acc_x = float(row["acc_x"])
                    acc_y = float(row["acc_y"])
                    acc_z = float(row["acc_z"])
                    valid_records += 1

                    deceleration = abs(acc_y) if acc_y < 0 else 0.0

                    if acc_y < HARSH_BRAKING_THRESHOLD:
                        severity = "CRITICAL" if acc_y < -4.0 else "HIGH"
                        formatted_time = datetime.fromtimestamp(ts, timezone.utc).strftime('%H:%M:%S UTC')
                        
                        print(f"  ⚡ [SIGNAL ISOLÉ - FREINAGE VIOLENT] Ligne {row_idx} | TS: {ts} ({formatted_time}) | acc_y = {acc_y} m/s² (Décélération: {deceleration:.2f} m/s² > Seuil 2.5) -> SÉVÉRITÉ: {severity}")
                        
                        harsh_events.append({
                            "event_type": "HARSH_BRAKING", "timestamp": ts, "formatted_time": formatted_time,
                            "acc_x": acc_x, "acc_y": acc_y, "acc_z": acc_z,
                            "deceleration_m_s2": round(deceleration, 2), "severity": severity
                        })
                    else:
                        print(f"  ░ [BRUIT / CONDUITE NORMALE] Ligne {row_idx} | acc_y = {acc_y:+.2f} m/s² | Dans la tolérance (-2.5 à +2.5 m/s²)")

                except (ValueError, TypeError, KeyError) as val_err:
                    corrupted_records += 1
                    print(f"  [EXCEPTION GÉRÉE] Ligne {row_idx} ignorée (donnée corrompue/invalide) : {val_err}")
                    continue

    except Exception as err:
        print(f"[EXCEPTION GÉRÉE - SAFETY] {err}")
        return {"summary": {"harsh_braking_events_count": 0, "safety_score": 0, "insurance_bonus_eligible": False}, "status": "ERROR"}

    event_count = len(harsh_events)
    safety_score = max(0, 100 - (event_count * 10))
    
    daily_report = {
        "metadata": {"device_id": "GML-TABLET-050", "driver_id": "CHAUFFEUR-LYON-01", "generated_at": datetime.now(timezone.utc).isoformat()},
        "summary": {
            "total_records_read": total_records, "valid_records_analyzed": valid_records,
            "corrupted_records_skipped": corrupted_records, "harsh_braking_events_count": event_count,
            "safety_score": safety_score, "insurance_bonus_eligible": safety_score >= 90
        },
        "detected_events": harsh_events
    }

    try:
        with open(output_json_path, 'w', encoding='utf-8') as f_out:
            json.dump(daily_report, f_out, indent=2, ensure_ascii=False)
        print(f"--- [MODULE SAFETY] RAPPORT EXPORTÉ SANS ERREUR : '{output_json_path}' ---\n")
    except Exception as e:
        print(f"[EXCEPTION GÉRÉE - SAFETY] Erreur écriture JSON : {e}")

    return daily_report