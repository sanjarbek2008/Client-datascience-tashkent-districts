import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_plots():
    print("Generating EDA plots...")
    if not os.path.exists('plots'):
        os.makedirs('plots')
        
    try:
        df = pd.read_csv('data/processed/cleaned_district_data.csv')
    except FileNotFoundError:
        print("Cleaned data not found. Please run src/data/scrub.py first.")
        return

    # 1. Bar Chart of Rent Prices
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df.sort_values('Rent_Price_USD'), x='Rent_Price_USD', y='District', palette='viridis')
    plt.title('Average Rental Price by District (USD)')
    plt.xlabel('Price (USD)')
    plt.tight_layout()
    plt.savefig('plots/rent_prices.png')
    print("Saved plots/rent_prices.png")

    # 2. Scatter Plot: Rent vs Transport
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Transport_Score', y='Rent_Price_USD', hue='District', s=100)
    
    # Add labels
    for i, row in df.iterrows():
        plt.text(row['Transport_Score']+0.1, row['Rent_Price_USD'], row['District'], fontsize=9)
        
    plt.title('Rent Price vs Transport Score')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('plots/rent_vs_transport.png')
    print("Saved plots/rent_vs_transport.png")

    # 3. Bar Chart of Tech Jobs
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df.sort_values('Tech_Jobs_Count', ascending=False), x='Tech_Jobs_Count', y='District', palette='magma')
    plt.title('Approximate Tech Job Availability by District')
    plt.tight_layout()
    plt.savefig('plots/tech_jobs.png')
    print("Saved plots/tech_jobs.png")
    
    # 4. Boxplots (Distribution of numeric variables)
    plt.figure(figsize=(12, 6))
    melted_df = df.melt(id_vars=['District'], value_vars=['Rent_Price_USD', 'Tech_Jobs_Count', 'Cultural_POI_Count'])
    sns.boxplot(data=melted_df, x='variable', y='value', palette='Set2')
    plt.title('Distribution and Outliers of Key Metrics')
    plt.yscale('log') # Log scale because counts and prices differ by orders of magnitude
    plt.tight_layout()
    plt.savefig('plots/boxplots.png')
    print("Saved plots/boxplots.png")

    # 5. Histograms (Distribution of Rent)
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Rent_Price_USD'], bins=8, kde=True, color='blue')
    plt.title('Distribution of Rental Prices across Districts')
    plt.xlabel('Price (USD)')
    plt.tight_layout()
    plt.savefig('plots/rent_histogram.png')
    print("Saved plots/rent_histogram.png")

    # 6. Correlation Heatmap
    plt.figure(figsize=(8, 6))
    numeric_cols = ['Transport_Score', 'Rent_Price_USD', 'Tech_Jobs_Count', 'Cultural_POI_Count']
    corr = df[numeric_cols].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.savefig('plots/correlation_matrix.png')
    print("Saved plots/correlation_matrix.png")
    
    print("EDA phase complete.")

if __name__ == "__main__":
    create_plots()
