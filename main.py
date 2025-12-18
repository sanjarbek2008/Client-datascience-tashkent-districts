import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.data import obtain, scrub
from src.analysis import explore, model

def main():
    print("=== Starting Project Pipeline ===")
    
    # 1. Obtain Data
    print("\n--- Step 1: Obtain Data ---")
    obtain.main()
    
    # 2. Scrub Data
    print("\n--- Step 2: Scrub Data ---")
    transport, rent, jobs, pois = scrub.load_data()
    if transport is not None:
        final_df = scrub.clean_and_merge(transport, rent, jobs, pois)
        print("Saving cleaned data...")
        final_df.to_csv('data/processed/cleaned_district_data.csv', index=False)
    else:
        print("Failed to load data for scrubbing.")
        return

    # 3. Explore Data
    print("\n--- Step 3: Explore Data ---")
    explore.create_plots()
    
    # 4. Model Data
    print("\n--- Step 4: Model Data ---")
    model.run_modelling()
    
    print("\n=== Pipeline Complete ===")

if __name__ == "__main__":
    main()
