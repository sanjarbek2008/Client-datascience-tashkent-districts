import pandas as pd
import numpy as np
import statsmodels.api as sm

def run_modelling():
    print("Running Modelling Phase...")
    try:
        df = pd.read_csv('data/processed/cleaned_district_data.csv')
    except FileNotFoundError:
        print("Cleaned data not found.")
        return

    # 1. Regression Model
    # Predict Rent based on Transport and Jobs
    # Rent ~ Transport + Jobs
    print("\n--- Regression Analysis: Rent Price ~ Transport + Tech Jobs ---")
    X = df[['Transport_Score', 'Tech_Jobs_Count']]
    y = df['Rent_Price_USD']
    X = sm.add_constant(X)
    
    model = sm.OLS(y, X).fit()
    print(model.summary())
    
    # Save model summary to file for report
    with open('data/processed/model_summary.txt', 'w') as f:
        f.write(model.summary().as_text())
        
    # 2. Scoring System (0-10)
    print("\n--- Calculating Composite Scores ---")
    
    # We have normalized values (0-1). Multiply by 10 to get 0-10 score.
    # Factors:
    # - Transport Score (Higher is better)
    # - Job Availability (Higher is better)
    # - Cultural POIs (Higher is better)
    # - Rent Affordability (Higher is better, we created Rent_Affordability_Norm)
    
    df['Score_Transport'] = df['Transport_Score_Norm'] * 10
    df['Score_Jobs'] = df['Tech_Jobs_Count_Norm'] * 10
    df['Score_POI'] = df['Cultural_POI_Count_Norm'] * 10
    df['Score_Rent'] = df['Rent_Affordability_Norm'] * 10
    
    # Simple weighted average (Equal weights for now)
    df['Composite_Score'] = (
        df['Score_Transport'] + 
        df['Score_Jobs'] + 
        df['Score_POI'] + 
        df['Score_Rent']
    ) / 4
    
    # Sort by Composite Score
    ranked_df = df.sort_values('Composite_Score', ascending=False)
    
    print("\nTop 3 Recommended Districts:")
    print(ranked_df[['District', 'Composite_Score', 'Rent_Price_USD']].head(3))
    
    # Save Rankings
    ranked_df.to_csv('final_rankings.csv', index=False)
    print("\nSaved final_rankings.csv")
    print("Modelling phase complete.")

if __name__ == "__main__":
    run_modelling()
