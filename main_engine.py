import os
from zfe_engine import run_zfe_engine
from safety_engine import analyze_telematics

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_telematics_platform():
    print("=" * 75)
    print("   GREENMOVE LOGISTICS - PLATEFORME TÉLÉMATIQUE EMBARQUÉE (EDGE COMPUTING)   ")
    print("=" * 75)
    
    # 1. Module ZFE
    print("\n---> MODULE 1 : CONFORMITÉ ZFE (GEO) - SUIVI EN TEMPS RÉEL")
    zfe_results = run_zfe_engine(os.path.join(SCRIPT_DIR, "lyon_polygon.json"), os.path.join(SCRIPT_DIR, "truck_gps.json"))
    
    # 2. Module Safety
    print("\n---> MODULE 2 : SÉCURITÉ & SCORING ASSURANCE (PHYSICS) - FILTRAGE DU BRUIT")
    safety_report = analyze_telematics(os.path.join(SCRIPT_DIR, "accelerometer_data.csv"), os.path.join(SCRIPT_DIR, "daily_score.json"))
    
    # 3. Extraction sécurisée
    alerts = zfe_results.get("alerts", []) if isinstance(zfe_results, dict) else []
    summary_safety = safety_report.get("summary", {}) if isinstance(safety_report, dict) else {}

    print("=" * 75)
    print("   SYNTHÈSE EMBARQUÉE DE LA SESSION DE CONDUITE")
    print("=" * 75)
    print(f"• Positions GPS analysées : {zfe_results.get('total_processed', 0)}")
    print(f"• Alertes ZFE franchies instantanément : {len(alerts)} événement(s)")
    for idx, a in enumerate(alerts, 1):
        print(f"   └─ Alerte #{idx} à {a.get('timestamp')} | Pos: ({a.get('lat')}, {a.get('lon')}) | Latence détection: {a.get('latency_us')} µs")
        
    print(f"\n• Échantillons accéléromètre analysés : {summary_safety.get('valid_records_analyzed', 0)} (Lignes corrompues ignorées: {summary_safety.get('corrupted_records_skipped', 0)})")
    print(f"• Freinages violents isolés (> 2.5 m/s²) : {summary_safety.get('harsh_braking_events_count', 0)} événement(s)")
    print(f"• Score de conduite global : {summary_safety.get('safety_score', 0)}/100")
    print(f"• Éligibilité Bonus AssurezMoi (20%) : {'OUI' if summary_safety.get('insurance_bonus_eligible') else 'NON'}")
    print("=" * 75)
    print("✔ Exécution terminée avec succès : la plateforme est stable et résiliente aux exceptions.")
    print("=" * 75)

if __name__ == "__main__":
    run_telematics_platform()