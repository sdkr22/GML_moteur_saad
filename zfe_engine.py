import json
import time
#import sys
import os

def compute_bounding_box(polygon):
    try:
        lats = [p["lat"] for p in polygon if "lat" in p and isinstance(p["lat"], (int, float))]
        lons = [p["lon"] for p in polygon if "lon" in p and isinstance(p["lon"], (int, float))]
        if not lats or not lons:
            raise ValueError("Polygone ZFE invalide ou vide.")
        return {
            "min_lat": min(lats), "max_lat": max(lats),
            "min_lon": min(lons), "max_lon": max(lons)
        }
    except Exception as e:
        print(f"[ERREUR CRITIQUE ZFE] Bounding Box impossible : {e}")
        return None

def is_in_bounding_box(lat, lon, bbox):
    if not bbox:
        return True
    return (bbox["min_lat"] <= lat <= bbox["max_lat"]) and (bbox["min_lon"] <= lon <= bbox["max_lon"])

def ray_casting_point_in_polygon(lat, lon, polygon):
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        try:
            yi, xi = float(polygon[i]["lat"]), float(polygon[i]["lon"])
            yj, xj = float(polygon[j]["lat"]), float(polygon[j]["lon"])
            intersect = ((yi > lat) != (yj > lat)) and \
                        (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi)
            if intersect:
                inside = not inside
            j = i
        except (KeyError, ValueError, ZeroDivisionError):
            continue
    return inside

def run_zfe_engine(polygon_file="lyon_polygon.json", gps_file="truck_gps.json"):
    alerts = []
    processed_count = 0
    error_count = 0

    # 1. Chargement sécurisé du polygone ZFE
    try:
        if not os.path.exists(polygon_file):
            raise FileNotFoundError(f"Fichier introuvable : {polygon_file}")
        with open(polygon_file, 'r', encoding='utf-8') as f:
            polygon = json.load(f)
    except Exception as e:
        print(f"[EXCEPTION GÉRÉE - ZFE] Erreur carte : {e}")
        return {"alerts": [], "total_processed": 0, "status": "ERROR"}

    bbox = compute_bounding_box(polygon)

    # 2. Chargement sécurisé des points GPS
    try:
        if not os.path.exists(gps_file):
            raise FileNotFoundError(f"Fichier GPS introuvable : {gps_file}")
        with open(gps_file, 'r', encoding='utf-8') as f:
            gps_points = json.load(f)
    except Exception as e:
        print(f"[EXCEPTION GÉRÉE - ZFE] Erreur GPS : {e}")
        return {"alerts": [], "total_processed": 0, "status": "ERROR"}

    # 3. Évaluation temps réel point par point
    for pt in gps_points:
        try:
            pt_id = pt.get("id", "N/A")
            timestamp = pt.get("timestamp", "00:00:00")
            expected = pt.get("expected", "Inconnu")
            
            if "lat" not in pt or "lon" not in pt:
                raise KeyError(f"Données manquantes pour l'ID {pt_id}")
                
            lat, lon = float(pt["lat"]), float(pt["lon"])
            processed_count += 1

            # Chronométrage de la latence de traitement
            start_time = time.perf_counter()
            in_bbox = is_in_bounding_box(lat, lon, bbox)
            is_inside = ray_casting_point_in_polygon(lat, lon, polygon) if in_bbox else False
            execution_time_us = (time.perf_counter() - start_time) * 1_000_000

            if is_inside:
                print(f"[ALERT ZFE INSTANTANÉE] ID {pt_id} | Timestamp: {timestamp} | Lat: {lat}, Lon: {lon} -> EN ZFE ! (Temps de détection: {execution_time_us:.2f} µs | Attendu: {expected})")
                alerts.append({
                    "id": pt_id, "timestamp": timestamp, "lat": lat, "lon": lon,
                    "latency_us": round(execution_time_us, 2)
                })
            else:
                bbox_str = "Dans Bounding Box mais Hors Polygon" if in_bbox else "Hors Bounding Box"
                print(f"[STATUS OUT] ID {pt_id} | Timestamp: {timestamp} | Lat: {lat}, Lon: {lon} -> HORS ZFE ({bbox_str} | Temps: {execution_time_us:.2f} µs)")

        except (KeyError, ValueError, TypeError) as e:
            error_count += 1
            print(f"[AVERTISSEMENT ZFE] Point GPS corrompu ignoré : {e}")
            continue

    return {"alerts": alerts, "total_processed": processed_count, "error_count": error_count, "status": "SUCCESS"}