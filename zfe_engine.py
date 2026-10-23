import json ### pour la lecture des fichiers JSON
import sys ### pour la lecture des arguments de ligne de commande

def compute_bounding_box(polygon):
    """
    Calcule l'enveloppe rectangulaire (Bounding Box) [min_lat, max_lat, min_lon, max_lon].
    Complexité : O(V) exécutée une seule fois au chargement de la carte ZFE. ou V est le nombre de sommets du polygone ZFE.
    """
    lats = [p["lat"] for p in polygon]
    lons = [p["lon"] for p in polygon]
    return {
        "min_lat": min(lats),
        "max_lat": max(lats),
        "min_lon": min(lons),
        "max_lon": max(lons)
    }

def is_in_bounding_box(lat, lon, bbox):
    """
    Filtre rapide en O(1) : élimine instantanément les coordonnées hors de l'enveloppe. Return True si le point est dans la Bounding Box, sinon False.
    """
    return (bbox["min_lat"] <= lat <= bbox["max_lat"]) and (bbox["min_lon"] <= lon <= bbox["max_lon"])

def ray_casting_point_in_polygon(lat, lon, polygon):
    """
    Algorithme du Ray Casting (Point in Polygon).
    Complexité : O(V) où V est le nombre de sommets du polygone ZFE.
    lat et lon sont les coordonnées du point à tester.
    polygon est une liste de dictionnaires avec des clés "lat" et "lon" représentant les sommets du polygone.
    Return True si le point est à l'intérieur du polygone, sinon False.
    """
    inside = False
    n = len(polygon)
    j = n - 1
    
    for i in range(n):
        yi, xi = polygon[i]["lat"], polygon[i]["lon"]
        yj, xj = polygon[j]["lat"], polygon[j]["lon"]
        
        # Test de croisement du rayon horizontal tiré vers l'Est avec le segment (i, j)
        intersect = ((yi > lat) != (yj > lat)) and \
                    (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi)
        if intersect:
            inside = not inside
        j = i
        
    return inside

def run_zfe_engine(polygon_file="lyon_polygon.json", gps_file="truck_gps.json"):
    # 1. Chargement du polygone ZFE
    with open(polygon_file, 'r', encoding='utf-8') as f:
        polygon = json.load(f)
        
    # Pre-calcul de la Bounding Box O(V)
    bbox = compute_bounding_box(polygon)
    
    # 2. Traitement du flux GPS
    with open(gps_file, 'r', encoding='utf-8') as f:
        gps_points = json.load(f)

    alerts = []

    for pt in gps_points:
        pt_id = pt["id"]
        timestamp = pt["timestamp"]
        lat = pt["lat"]
        lon = pt["lon"]
        expected = pt.get("expected", "N/A")
        """
        On commence par vérifier si le point GPS est dans la Bounding Box. Si ce n'est pas le cas, on peut immédiatement conclure qu'il est hors de la ZFE.
        Si le point est dans la Bounding Box, on applique ensuite l'algorithme du Ray Casting pour déterminer s'il est à l'intérieur du polygone ZFE.
        """
        # Étape 1 : Filtre Bounding Box O(1)
        if not is_in_bounding_box(lat, lon, bbox):
            print(f"[STATUS OUT] ID {pt_id} | {timestamp} | Lat: {lat}, Lon: {lon} -> Hors Bounding Box")
            continue
            
        # Étape 2 : Ray Casting O(V)
        is_inside = ray_casting_point_in_polygon(lat, lon, polygon)
        
        if is_inside:
            print(f"[ALERT ZFE] ID {pt_id} | {timestamp} | Lat: {lat}, Lon: {lon} -> VÉHICULE EN ZFE ! (Attendu: {expected})")
            alerts.append(pt)  # On enregistre l'alerte
        else:
            print(f"[STATUS OUT] ID {pt_id} | {timestamp} | Lat: {lat}, Lon: {lon} -> Dans Bounding Box mais HORS ZFE (Attendu: {expected})")

    return {
        "alerts": alerts,
        "total_processed": len(gps_points)
    }        

if __name__ == "__main__":
    poly_path = sys.argv[1] if len(sys.argv) > 1 else "lyon_polygon.json"
    gps_path = sys.argv[2] if len(sys.argv) > 2 else "truck_gps.json"
    run_zfe_engine(poly_path, gps_path)
   