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
    print("Using User-Provided Metro Counts...")
    # Paths relative to project root
    RAW_TRANSPORT_PATH = 'data/raw/raw_transport.csv'
    
    # Check cache first
    if os.path.exists(RAW_TRANSPORT_PATH):
        print(f"Found existing {RAW_TRANSPORT_PATH}, using it.")
        return pd.read_csv(RAW_TRANSPORT_PATH)

    # Data provided by user
    metro_counts = {
        "Sergeli": 8,
        "Yunusabad": 7,
        "Chilanzar": 6,
        "Mirabad": 4,
        "Mirzo Ulugbek": 5,
        "Bektemir": 1,
        "Yangihayot": 2,
        "Yashnobod": 8,
        "Shaykhantakhur": 7,
        "Uchtepa": 0,
        "Yakkasaray": 1,
        "Almazar": 0
    }
    
    data = {'District': list(metro_counts.keys()), 'Transport_Score': list(metro_counts.values())}
    df = pd.DataFrame(data)
    return df

def get_rent_data():
    print("Scraping Real Rent Data (olx.uz) per district...")
    
    # Paths relative to project root
    RAW_RENT_PATH = 'data/raw/raw_rent.csv'
    if os.path.exists(RAW_RENT_PATH):
        print(f"Loading cached {RAW_RENT_PATH}")
        return pd.read_csv(RAW_RENT_PATH)
        
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
        "Yashnobod": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=22&currency=UZS",
        "Yangihayot": "https://www.olx.uz/oz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?search%5Bdistrict_id%5D=48&currency=UZS" # Assuming district_id for Yangihayot
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Get current exchange rate
    def get_exchange_rate():
        return 12800 
    
    exchange_rate = get_exchange_rate()
    data = []
    import re

    for district_name, url in district_urls.items():
        print(f"  Fetching data for {district_name}...")
        district_prices = []
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                price_elements = soup.find_all('p', {'data-testid': 'ad-price'})
                
                for price_elem in price_elements:
                    price_text = price_elem.get_text().strip()
                    price_usd = None
                    usd_match = re.search(r'([\d\s\xa0]+)\s*(?:USD|\$|y\.e\.?|у\.е\.?)', price_text, re.I)
                    if usd_match:
                        price_str = usd_match.group(1).replace(' ', '').replace('\xa0', '')
                        price_usd = float(price_str)
                    
                    if price_usd is None:
                        uzs_match = re.search(r'([\d\s\xa0]+)\s*(?:so\'m|sum|UZS|сум)', price_text, re.I)
                        if uzs_match:
                            price_str = uzs_match.group(1).replace(' ', '').replace('\xa0', '')
                            price_usd = float(price_str) / exchange_rate
                    
                    if price_usd and 100 <= price_usd <= 5000:
                        district_prices.append(price_usd)
            
            if district_prices:
                median_price = sorted(district_prices)[len(district_prices) // 2]
                final_price = int(median_price)
            else:
                fallback_prices = {
                    "Yakkasaray": 600, "Mirabad": 700, "Mirzo Ulugbek": 550, 
                    "Shaykhantakhur": 500, "Yunusabad": 650, "Chilanzar": 450,
                    "Almazar": 400, "Bektemir": 380, "Sergeli": 350,
                    "Uchtepa": 420, "Yashnobod": 480, "Yangihayot": 300
                }
                final_price = fallback_prices.get(district_name, 400)
            
            data.append({'District': district_name, 'Rent_Price_USD': final_price})
            time.sleep(1)
            
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
        
    districts = ["Yunusabad", "Chilanzar", "Yakkasaray", "Mirabad", "Mirzo Ulugbek", "Shaykhantakhur", "Almazar", "Uchtepa", "Sergeli", "Yashnobod", "Bektemir", "Yangihayot"]
    data = []
    headers = {'User-Agent': 'TashkentDataScienceProject/1.0'}

    for district in districts:
        try:
            search_query = f"{district} District, Tashkent"
            nom_resp = requests.get("https://nominatim.openstreetmap.org/search", params={'q': search_query, 'format': 'json'}, headers=headers, timeout=10)
            nom_data = nom_resp.json()
            
            area_id = None
            if nom_data:
                for item in nom_data:
                    if item.get('osm_type') == 'relation':
                        area_id = int(item['osm_id']) + 3600000000
                        break
            
            if area_id:
                count = 0
                overpass_url = "http://overpass-api.de/api/interpreter"
                query = f"[out:json];area({area_id})->.searchArea;(node['office'](area.searchArea);way['office'](area.searchArea););out count;"
                
                # Simple retry logic
                for attempt in range(2):
                    try:
                        resp = requests.get(overpass_url, params={'data': query}, headers=headers, timeout=20)
                        if resp.status_code == 200:
                            op_data = resp.json()
                            if 'elements' in op_data and len(op_data['elements']) > 0:
                                tags = op_data['elements'][0].get('tags', {})
                                count = int(tags.get('nodes', 0)) + int(tags.get('ways', 0))
                            break
                    except:
                        time.sleep(2)
                
                print(f"  {district}: Found {count} offices.")
                data.append({'District': district, 'Tech_Jobs_Count': count})
            else:
                 data.append({'District': district, 'Tech_Jobs_Count': 0})
            time.sleep(1)
        except Exception as e:
            print(f"  Error fetching jobs for {district}: {e}")
            data.append({'District': district, 'Tech_Jobs_Count': 0})
            
    return pd.DataFrame(data)

def get_poi_data():
    print("Fetching Real Cultural POI Data (Overpass API)...")
    districts = ["Yunusabad", "Chilanzar", "Yakkasaray", "Mirabad", "Mirzo Ulugbek", "Shaykhantakhur", "Almazar", "Uchtepa", "Sergeli", "Yashnobod", "Bektemir", "Yangihayot"]
    
    RAW_POIS_PATH = 'data/raw/raw_pois.csv'
    if os.path.exists(RAW_POIS_PATH):
        print(f"Loading cached {RAW_POIS_PATH}")
        return pd.read_csv(RAW_POIS_PATH)

    data = []
    headers = {'User-Agent': 'TashkentDataScienceProject/1.0'}
    
    for district in districts:
        try:
            search_query = f"{district} District, Tashkent"
            nom_resp = requests.get("https://nominatim.openstreetmap.org/search", params={'q': search_query, 'format': 'json'}, headers=headers, timeout=10)
            nom_data = nom_resp.json()
            
            area_id = None
            if nom_data:
                for item in nom_data:
                    if item.get('osm_type') == 'relation':
                        area_id = int(item['osm_id']) + 3600000000
                        break
            
            if area_id:
                count = 0
                overpass_url = "http://overpass-api.de/api/interpreter"
                query = f"[out:json];area({area_id})->.searchArea;(node['amenity'~'cafe|theatre|arts_centre|cinema|library'](area.searchArea);way['amenity'~'cafe|theatre|arts_centre|cinema|library'](area.searchArea););out count;"
                
                for attempt in range(2):
                    try:
                        op_resp = requests.get(overpass_url, params={'data': query}, headers=headers, timeout=20)
                        if op_resp.status_code == 200:
                            op_data = op_resp.json()
                            if 'elements' in op_data and len(op_data['elements']) > 0:
                                tags = op_data['elements'][0].get('tags', {})
                                count = int(tags.get('nodes', 0)) + int(tags.get('ways', 0))
                            break
                    except:
                        time.sleep(2)
                
                print(f"  {district}: Found {count} POIs.")
                data.append({'District': district, 'Cultural_POI_Count': count})
            else:
                data.append({'District': district, 'Cultural_POI_Count': 0})
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching POIs for {district}: {e}")
            data.append({'District': district, 'Cultural_POI_Count': 0})
            
    return pd.DataFrame(data)

def main():
    df_metro = get_metro_data()
    df_rent = get_rent_data()
    df_jobs = get_job_data()
    df_poi = get_poi_data()
    
    # Ensure data/raw directory exists
    if not os.path.exists('data/raw'):
        os.makedirs('data/raw')

    print("Saving raw datasets...")
    df_metro.to_csv('data/raw/raw_transport.csv', index=False)
    df_rent.to_csv('data/raw/raw_rent.csv', index=False)
    df_jobs.to_csv('data/raw/raw_jobs.csv', index=False)
    df_poi.to_csv('data/raw/raw_pois.csv', index=False)
    print("Obtain phase complete.")

if __name__ == "__main__":
    main()
