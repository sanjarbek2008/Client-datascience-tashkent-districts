import json
import pandas as pd
import random
import os
import requests
import time
from bs4 import BeautifulSoup

# Ensure data directory exists
# We will just write to the current directory as per user workspace

def get_metro_data():
    print("Processing Metro Data...")
    # Paths relative to project root
    GEO_PATH = 'data/geo/export.geojson'
    METRO_COUNTS_PATH = 'data/processed/metro_counts.csv'
    
    try:
        # We need to make sure we look for files relative to where the script is run (project root)
        if os.path.exists(GEO_PATH):
            with open(GEO_PATH, 'r') as f:
                data = json.load(f)
        else:
             print(f"Warning: {GEO_PATH} not found.")

        
        # Districts approximation based on Metro station locations (simplification for assignment)
        # Realistically we would do a spatial join with district shapefiles.
        # For this assignment, we'll map known stations to districts or random assign if unknown
        # Actually, let's use the metro_counts.csv if it exists and is reliable, otherwise re-count similar to previous task
        
        # Checking if metro_counts.csv exists and is valid
        if os.path.exists(METRO_COUNTS_PATH):
            print(f"Found existing {METRO_COUNTS_PATH}, using it.")
            df = pd.read_csv(METRO_COUNTS_PATH)
            # standardized column names
            df.columns = ['District', 'Transport_Score']
            return df
        else:
            print("metro_counts.csv not found, generating mock transport scores.")
            districts = ["Yunusabad", "Chilanzar", "Yakkasaray", "Mirabad", "Mirzo Ulugbek", "Shaykhantakhur", "Almazar", "Uchtepa", "Sergeli", "Yashnobod", "Bektemir"]
            data = {'District': districts, 'Transport_Score': [random.randint(2, 10) for _ in districts]}
            return pd.DataFrame(data)

    except Exception as e:
        print(f"Error getting metro data: {e}")
        return pd.DataFrame()

def get_rent_data():
    print("Scraping Real Rent Data (olx.uz) per district...")
    
    # Paths relative to project root
    RAW_RENT_PATH = 'data/raw/raw_rent.csv'
        
    district_urls = {
        "Almazar": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=20&currency=UZS",
        "Bektemir": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=18&currency=UZS",
        "Mirabad": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=13&currency=UZS",
        "Mirzo Ulugbek": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=12&currency=UZS",
        "Sergeli": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=19&currency=UZS",
        "Uchtepa": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=21&currency=UZS",
        "Chilanzar": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=23&currency=UZS",
        "Shaykhantakhur": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=24&currency=UZS",
        "Yunusabad": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=25&currency=UZS",
        "Yakkasaray": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=26&currency=UZS",
        "Yashnobod": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=22&currency=UZS"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Get current exchange rate
    def get_exchange_rate():
        try:
            # You could use a live API, but for stability, use a reasonable estimate
            return 12800  # Update this periodically or fetch from API
        except:
            return 12800
    
    exchange_rate = get_exchange_rate()
    
    data = []
    import re

    for district_name, url in district_urls.items():
        print(f"  Fetching data for {district_name}...")
        district_prices = []
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Target price elements
                price_elements = soup.find_all('p', {'data-testid': 'ad-price'})
                if not price_elements:
                    price_elements = soup.find_all(['p', 'span', 'div'], 
                                                   class_=re.compile(r'price', re.I))
                
                print(f"    Found {len(price_elements)} price elements")
                if price_elements:
                    print(f"    Sample text: {price_elements[0].get_text().strip()}")

                for price_elem in price_elements:
                    price_text = price_elem.get_text().strip()
                    price_usd = None
                    
                    # Try USD first (y.e., USD, $)
                    usd_match = re.search(r'([\d\s\xa0]+)\s*(?:USD|\$|y\.e\.?|у\.е\.?)', price_text, re.I)
                    if usd_match:
                        price_str = usd_match.group(1).replace(' ', '').replace('\xa0', '')
                        try:
                            price_usd = float(price_str)
                        except ValueError:
                            continue
                    
                    # Try UZS if no USD found (so'm, sum, UZS)
                    if price_usd is None:
                        uzs_match = re.search(r'([\d\s\xa0]+)\s*(?:so\'m|sum|UZS|сум)', price_text, re.I)
                        if uzs_match:
                            price_str = uzs_match.group(1).replace(' ', '').replace('\xa0', '')
                            try:
                                price_uzs = float(price_str)
                                # Convert to USD
                                price_usd = price_uzs / exchange_rate
                            except ValueError:
                                continue
                    
                    # Validate: reasonable rental range in USD
                    if price_usd and 100 <= price_usd <= 5000:
                        district_prices.append(price_usd)
                    elif price_usd and price_usd > 5000:
                        # Likely UZS mistaken as USD - convert it
                        converted = price_usd / exchange_rate
                        if 100 <= converted <= 5000:
                            district_prices.append(converted)
            
            if district_prices:
                # Remove outliers
                sorted_prices = sorted(district_prices)
                if len(sorted_prices) >= 5:
                    # Remove top and bottom 15%
                    trim = max(1, len(sorted_prices) // 7)
                    trimmed = sorted_prices[trim:-trim]
                else:
                    trimmed = sorted_prices
                
                avg_price = sum(trimmed) / len(trimmed) if trimmed else sum(sorted_prices) / len(sorted_prices)
                median_price = sorted_prices[len(sorted_prices) // 2]
                
                print(f"    Validated {len(district_prices)} listings. Avg: ${int(avg_price)}, Median: ${int(median_price)}")
                
                # Use median instead of mean to avoid outlier influence
                final_price = int(median_price)
            else:
                print(f"    No valid listings for {district_name}, using fallback.")
                fallback_prices = {
                    "Yakkasaray": 600, "Mirabad": 700, "Mirzo Ulugbek": 550, 
                    "Shaykhantakhur": 500, "Yunusabad": 650, "Chilanzar": 450,
                    "Almazar": 400, "Bektemir": 380, "Sergeli": 350,
                    "Uchtepa": 420, "Yashnobod": 480
                }
                final_price = fallback_prices.get(district_name, 400)
            
            data.append({'District': district_name, 'Rent_Price_USD': final_price})
            time.sleep(2)
            
        except Exception as e:
            print(f"    Error scraping {district_name}: {e}")
            data.append({'District': district_name, 'Rent_Price_USD': 400})

    return pd.DataFrame(data)

def get_job_data():
    print("Fetching Real Job Data Proxy (Overpass 'office' count)...")
    
    RAW_JOBS_PATH = 'data/raw/raw_jobs.csv'
    if os.path.exists(RAW_JOBS_PATH):
        print(f"Loading cached {RAW_JOBS_PATH}")
        return pd.read_csv(RAW_JOBS_PATH)
        
    districts = ["Yunusabad", "Chilanzar", "Yakkasaray", "Mirabad", "Mirzo Ulugbek", "Shaykhantakhur", "Almazar", "Uchtepa", "Sergeli", "Yashnobod", "Bektemir"]
    data = []
    headers = {'User-Agent': 'TashkentDataScienceProject/1.0'}

    for district in districts:
        try:
            # Re-use logic for Area ID (in a real app, refactor to function)
            # For simplicity, we create a quick lookup or just fetch again (caching prevents spam)
            search_query = f"{district} District, Tashkent"
            if district == "Mirzo Ulugbek": search_query = "Mirzo Ulugbek District, Tashkent"
            
            nom_resp = requests.get("https://nominatim.openstreetmap.org/search", params={'q': search_query, 'format': 'json', 'polygon_geojson': 0}, headers=headers)
            nom_data = nom_resp.json()
            
            area_id = None
            if nom_data:
                for item in nom_data:
                    if item['osm_type'] == 'relation':
                        area_id = int(item['osm_id']) + 3600000000
                        break
            
            # Query for offices
            if area_id:
                count = 0
                overpass_url = "http://overpass-api.de/api/interpreter"
                query = f"""
                [out:json];
                area({area_id})->.searchArea;
                (
                  node["office"](area.searchArea);
                  way["office"](area.searchArea);
                );
                out count;
                """
                resp = requests.get(overpass_url, params={'data': query}, headers=headers)
                op_data = resp.json()
                if 'elements' in op_data and len(op_data['elements']) > 0:
                    tags = op_data['elements'][0].get('tags', {})
                    count = int(tags.get('nodes', 0)) + int(tags.get('ways', 0)) + int(tags.get('relations', 0))
                
                print(f"  {district}: Found {count} offices.")
                data.append({'District': district, 'Tech_Jobs_Count': count}) # Using office count as proxy
            else:
                 data.append({'District': district, 'Tech_Jobs_Count': 0})
                 
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error fetching jobs/office for {district}: {e}")
            data.append({'District': district, 'Tech_Jobs_Count': 0})
            
    return pd.DataFrame(data)

def get_poi_data():
    print("Fetching Real Cultural POI Data (Overpass API)...")
    districts = [
        "Yunusabad", "Chilanzar", "Yakkasaray", "Mirabad", "Mirzo Ulugbek", 
        "Shaykhantakhur", "Almazar", "Uchtepa", "Sergeli", "Yashnobod", "Bektemir"
    ]
    
    # Cache check
    RAW_POIS_PATH = 'data/raw/raw_pois.csv'
    if os.path.exists(RAW_POIS_PATH):
        print(f"Loading cached {RAW_POIS_PATH}")
        return pd.read_csv(RAW_POIS_PATH)

    data = []
    headers = {'User-Agent': 'TashkentDataScienceProject/1.0'}
    
    for district in districts:
        print(f"Querying for {district}...")
        try:
            # 1. Get Area ID
            search_query = f"{district} District, Tashkent"
            # Special case naming adjustments if needed
            if district == "Mirzo Ulugbek": search_query = "Mirzo Ulugbek District, Tashkent"
            
            nom_url = "https://nominatim.openstreetmap.org/search"
            nom_resp = requests.get(nom_url, params={'q': search_query, 'format': 'json', 'polygon_geojson': 0}, headers=headers)
            nom_data = nom_resp.json()
            
            area_id = None
            if nom_data:
                for item in nom_data:
                    if item['osm_type'] == 'relation':
                        area_id = int(item['osm_id']) + 3600000000
                        break
            
            if not area_id:
                print(f"Could not find OSM relation for {district}, skipping.")
                data.append({'District': district, 'Cultural_POI_Count': 0})
                continue
                
            # 2. Count POIs (Amenities: Cafe, School, Arts Centre, etc.)
            overpass_url = "http://overpass-api.de/api/interpreter"
            query = f"""
            [out:json];
            area({area_id})->.searchArea;
            (
              node["amenity"~"cafe|theatre|arts_centre|cinema|library"](area.searchArea);
              way["amenity"~"cafe|theatre|arts_centre|cinema|library"](area.searchArea);
            );
            out count;
            """
            op_resp = requests.get(overpass_url, params={'data': query}, headers=headers)
            op_data = op_resp.json()
            
            # Parse count
            # Structure: elements: [ { "type": "count", "tags": { "nodes": "...", "ways": "...", ... }, "count": "total" } ]
            # Note: 'out count' output structure varies. Usually 'elements' list with one item containing 'tags' with counts.
            count = 0
            if 'elements' in op_data and len(op_data['elements']) > 0:
                el = op_data['elements'][0]
                # sum nodes, ways, relations if broken down, or 'total' if available (sometimes different format)
                # simpler to just count nodes + ways
                tags = el.get('tags', {})
                count = int(tags.get('nodes', 0)) + int(tags.get('ways', 0)) + int(tags.get('relations', 0))
                # Alternatively look for 'count' key if specific OP settings used, but tags summation is safer for 'out count'
            
            print(f"  Found {count} POIs.")
            data.append({'District': district, 'Cultural_POI_Count': count})
            
            time.sleep(1) # Respect API rate limits
            
        except Exception as e:
            print(f"Error fetching data for {district}: {e}")
            data.append({'District': district, 'Cultural_POI_Count': 0})
            
    return pd.DataFrame(data)

def main():
    df_metro = get_metro_data()
    df_rent = get_rent_data()
    df_jobs = get_job_data()
    df_poi = get_poi_data()
    
    print("Saving raw datasets...")
    df_metro.to_csv('data/raw/raw_transport.csv', index=False)
    df_rent.to_csv('data/raw/raw_rent.csv', index=False)
    df_jobs.to_csv('data/raw/raw_jobs.csv', index=False)
    df_poi.to_csv('data/raw/raw_pois.csv', index=False)
    print("Obtain phase complete.")

if __name__ == "__main__":
    main()
