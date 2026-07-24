"""
Scraping des garages et ateliers mécaniques à Casablanca via l'API Overpass (OpenStreetMap).
Gratuit, sans clé API, sans quota.
"""
import csv
import os
import requests

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "garages_osm.csv")

# instance principale + miroir de secours si la principale est surchargee (504)
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# overpass-api.de rejette (406) les clients sans User-Agent descriptif ni Accept-Encoding
HEADERS = {
    "User-Agent": "AutoPlusMaroc-PFA/1.0 (contact: ayach.merouane23@gmail.com)",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
}

# bbox: (sud, ouest, nord, est)
CITY = "Casablanca"
BBOX = (33.45, -7.75, 33.65, -7.50)

QUERY_TEMPLATE = """
[out:json][timeout:60];
(
  node["shop"="car_repair"]({bbox});
  way["shop"="car_repair"]({bbox});
  node["craft"="car_repair"]({bbox});
  way["craft"="car_repair"]({bbox});
  node["amenity"="car_repair"]({bbox});
  way["amenity"="car_repair"]({bbox});
);
out center tags;
"""

FIELDNAMES = ["ville", "osm_id", "osm_type", "nom", "lat", "lon", "telephone", "horaires", "adresse"]


def fetch_city(bbox):
    bbox_str = ",".join(str(v) for v in bbox)
    query = QUERY_TEMPLATE.format(bbox=bbox_str)
    last_error = None
    for url in OVERPASS_URLS:
        try:
            resp = requests.post(url, data={"data": query}, headers=HEADERS, timeout=90)
            resp.raise_for_status()
            return resp.json().get("elements", [])
        except requests.exceptions.RequestException as e:
            print(f"  echec sur {url} ({e}), tentative suivante...")
            last_error = e
    raise last_error


def element_to_row(city, el):
    tags = el.get("tags", {})
    center = el.get("center", {})
    return {
        "ville": city,
        "osm_id": el.get("id"),
        "osm_type": el.get("type"),
        "nom": tags.get("name", ""),
        "lat": el.get("lat", center.get("lat")),
        "lon": el.get("lon", center.get("lon")),
        "telephone": tags.get("phone", tags.get("contact:phone", "")),
        "horaires": tags.get("opening_hours", ""),
        "adresse": " ".join(filter(None, [
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", ""),
        ])).strip(),
    }


def main():
    print(f"Recherche garages/ateliers a {CITY}...")
    elements = fetch_city(BBOX)
    print(f"  -> {len(elements)} resultats")
    rows = [element_to_row(CITY, el) for el in elements]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} garages/ateliers ecrits dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
