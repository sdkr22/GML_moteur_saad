import sys
import os
import json
from zfe_engine import run_zfe_engine
from safety_engine import analyze_telematics

def run_telematics_platform(polygon_file="lyon_polygon.json", gps_file="truck_gps.json", accel_file="accelerometer_data.csv"):
    print("=" * 70)
    print("   GREENMOVE LOGISTICS - PLATEFORME TÉLÉMATIQUE EMBARQUÉE (EDGE)   ")
    print("=" * 70)
    
    # 1. Exécution du Module ZFE (Geo)
    print("\n---> EXECUTION MODULE 1 : CONFORMITÉ ZFE (GEO)")
    zfe_results = run_zfe_engine(polygon_file, gps_file)
    
    # 2. Exécution du Module Safety (Physics)
    print("\n---> EXECUTION MODULE 2 : SÉCURITÉ & SCORING ASSURANCE (PHYSICS)")
    safety_report = analyze_telematics(accel_file, "daily_score.json")
    
    # 3. Rapport Consolidé de la Session
    print("\n" + "=" * 70)
    print("   SYNTHÈSE EMBARQUÉE DE LA SESSION DE CONDUITE")
    print("=" * 70)
    zfe_count = len(zfe_results.get('alerts', [])) if zfe_results else 0
    print(f"• Alertes ZFE franchies : {zfe_count} événement(s)")
    print(f"• Freinages violents (> 2.5 m/s²) : {safety_report['summary']['harsh_braking_events_count']} événement(s)")
    print(f"• Score de conduite global : {safety_report['summary']['safety_score']}/100")
    print(f"• Éligibilité Bonus AssurezMoi (20%) : {'OUI' if safety_report['summary']['insurance_bonus_eligible'] else 'NON'}")
    print("=" * 70)

if __name__ == "__main__":
    run_telematics_platform()