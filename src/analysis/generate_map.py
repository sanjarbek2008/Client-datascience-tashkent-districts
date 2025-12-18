import geopandas as gpd
import matplotlib.pyplot as plt
import os

def generate_district_map():
    print("Generating Tashkent District Map...")
    SHP_PATH = 'data/geo/Toshkent_chegara.shp'
    OUTPUT_PATH = 'plots/tashkent_districts_map.png'
    
    if not os.path.exists('plots'):
        os.makedirs('plots')
        
    try:
        gdf = gpd.read_file(SHP_PATH)
        
        # Plotting
        fig, ax = plt.subplots(figsize=(12, 10))
        gdf.boundary.plot(ax=ax, linewidth=1, color='black')
        gdf.plot(ax=ax, alpha=0.3, column='tuman', cmap='tab20')
        
        # Adding labels
        for x, y, label in zip(gdf.geometry.centroid.x, gdf.geometry.centroid.y, gdf.tuman):
            ax.text(x, y, label, fontsize=10, ha='center', weight='bold')
            
        plt.title('Tashkent City District Boundaries', fontsize=15)
        ax.set_axis_off()
        plt.tight_layout()
        plt.savefig(OUTPUT_PATH, dpi=300)
        print(f"Saved {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"Error generating map: {e}")

if __name__ == "__main__":
    generate_district_map()
