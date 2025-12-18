import pandas as pd
import numpy as np

def load_data():
    print("Loading raw datasets...")
    try:
        transport = pd.read_csv('data/raw/raw_transport.csv')
        rent = pd.read_csv('data/raw/raw_rent.csv')
        jobs = pd.read_csv('data/raw/raw_jobs.csv')
        pois = pd.read_csv('data/raw/raw_pois.csv')

        return transport, rent, jobs, pois

    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        
        return None, None, None, None


def clean_and_merge(transport, rent, jobs, pois):
    print("Cleaning and Merging Data...")
    
    # Transport data might be in Cyrillic if it came from the CSV
    # Map Cyrillic to Latin to match other datasets
    name_map = {
        'Бектемир': 'Bektemir',
        'Чилонзор': 'Chilanzar',
        'Яшнобод': 'Yashnobod',
        'Яккасарой': 'Yakkasaray',
        'Мирзо Улуғбек': 'Mirzo Ulugbek',
        'Миробод': 'Mirabad',
        'Шайҳонтохур': 'Shaykhantakhur',
        'Олмазор': 'Almazar',
        'Учтепа': 'Uchtepa',
        'Сергели': 'Sergeli',
        'Юнусобод': 'Yunusabad',
        'Янгиҳаёт': 'Yangihayot' # Note: Yangihayot might not be in our mock lists, but good to handle
    }
    
    # helper to clean names
    def clean_name(name):
        return name_map.get(str(name).strip(), str(name).strip())

    if 'District' in transport.columns:
         transport['District'] = transport['District'].apply(clean_name)
    else:
        # If metro_counts csv had different column name
        pass # We handled column renaming in obtain_data.py

    # Merge
    # Start with transport dataframe as base
    df = transport.merge(rent, on='District', how='outer')
    df = df.merge(jobs, on='District', how='outer')
    df = df.merge(pois, on='District', how='outer')
    
    # Handle Missing Values
    # Handle Missing Values
    print("Handling missing values...")
    # Fill numeric columns with median or 0
    numeric_cols = ['Transport_Score', 'Rent_Price_USD', 'Tech_Jobs_Count', 'Cultural_POI_Count']
    for col in numeric_cols:
        if col in df.columns:
            # Treating 0 as missing for Jobs/Rent/POI because 0 is unlikely in these large districts
            # BUT Transport_Score 0 might be real (no metro).
            
            if col != 'Transport_Score':
                df[col] = df[col].replace(0, np.nan)
            
            # Fill NaN with median of the column
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"Filled missing/zero (if applicable) {col} with {median_val}")

    # Normalization (Min-Max Scaling) for later scoring
    # We will keep original values for display, and create new normalized columns for modelling
    print("Normalizing data for analysis...")
    for col in numeric_cols:
        min_val = df[col].min()
        max_val = df[col].max()
        if max_val - min_val != 0:
            df[f'{col}_Norm'] = (df[col] - min_val) / (max_val - min_val)
        else:
            df[f'{col}_Norm'] = 0.0
            
    # For Rent, lower is better, so we might want to invert the normalized score in the modelling phase,
    # or create a 'Rent_Score' here where 1 is best (cheapest) and 0 is worst (most expensive).
    # Let's create 'Rent_Affordability' where 1 = cheapest.
    # Formula: (Max - Value) / (Max - Min)
    min_rent = df['Rent_Price_USD'].min()
    max_rent = df['Rent_Price_USD'].max()
    if max_rent - min_rent != 0:
        df['Rent_Affordability_Norm'] = (max_rent - df['Rent_Price_USD']) / (max_rent - min_rent)
    else:
        df['Rent_Affordability_Norm'] = 0.5 # Neutral if all same
        
    return df

def main():
    transport, rent, jobs, pois = load_data()
    if transport is not None:
        final_df = clean_and_merge(transport, rent, jobs, pois)
        
        print("Saving cleaned data...")
        final_df.to_csv('data/processed/cleaned_district_data.csv', index=False)
        
        # Display sample
        print("\nCleaned Data Sample:")
        print(final_df.head(15))
        print("\nScrub phase complete.")
    else:
        print("Failed to load data.")

if __name__ == "__main__":
    main()
