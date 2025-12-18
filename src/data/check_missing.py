import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
import time

districts = [
    "Yunusabad", "Chilanzar", "Yakkasaray", "Mirabad", "Mirzo Ulugbek", 
    "Shaykhantakhur", "Almazar", "Uchtepa", "Sergeli", "Yashnobod", "Bektemir"
]

def check_transport():
    METRO_COUNTS_PATH = 'data/processed/metro_counts.csv'
    GEO_PATH = 'data/geo/export.geojson'
    status = {}
    if os.path.exists(METRO_COUNTS_PATH):
        status['METRO_COUNTS_CSV'] = "Present (Real data from previous runs)"
    else:
        status['METRO_COUNTS_CSV'] = "MISSING"
    
    if os.path.exists(GEO_PATH):
        status['GEOJSON_SOURCE'] = "Present"
    else:
        status['GEOJSON_SOURCE'] = "MISSING (Cannot re-generate real counts)"
    return status

def check_rent():
    url = "https://www.olx.uz/d/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    results = {}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            cards = soup.find_all('div', attrs={'data-cy': 'l-card'})
            if not cards:
                cards = soup.find_all('div', class_=lambda x: x and 'card' in x.lower())
            
            district_counts = {d: 0 for d in districts}
            for card in cards:
                text = card.get_text()
                for d in districts:
                    check_list = [d, d.replace('abad', 'obod'), d.replace('bad', 'bod')]
                    if any(variant.lower() in text.lower() for variant in check_list):
                        district_counts[d] += 1
            
            for d in districts:
                results[d] = f"{district_counts[d]} listings found" if district_counts[d] > 0 else "MISSING (Using mock fallback)"
        else:
            return {"Error": f"OLX returned {response.status_code}"}
    except Exception as e:
        return {"Error": str(e)}
    return results

def check_osm_data(poi_type="office"):
    # Check a few districts as sample for OSM availability
    headers = {'User-Agent': 'TashkentDataScienceProject/1.0'}
    results = {}
    for d in districts[:3]: # Limit to first 3 to avoid long wait
        try:
            search_query = f"{d} District, Tashkent"
            nom_resp = requests.get("https://nominatim.openstreetmap.org/search", params={'q': search_query, 'format': 'json'}, headers=headers, timeout=5)
            nom_data = nom_resp.json()
            if nom_data:
                results[d] = "OSM Area Found"
            else:
                results[d] = "MISSING (Nominatim cannot find area)"
        except:
            results[d] = "Timeout/Error"
        time.sleep(1)
    return results

print("--- DIAGNOSTIC REPORT ---")
print("\n[Transport Status]")
print(check_transport())

print("\n[Rent Listings Status (Live Scrape Check)]")
rent_status = check_rent()
for d, status in rent_status.items():
    print(f"{d:15}: {status}")

print("\n[OSM/Jobs/POI Connectivity (Sample)]")
osm_status = check_osm_data()
for d, status in osm_status.items():
    print(f"{d:15}: {status}")

print("\nSummary: If 'MISSING' or 'Using mock fallback' appears above, that district lacks real data in the current pipeline.")
