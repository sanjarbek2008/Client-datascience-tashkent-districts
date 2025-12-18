# Strategic Relocation Analysis: Evaluating Tashkent Districts for Tech Professionals
**Author**: Data Science Consultant
**Date**: December 18, 2025

---

## 1. Introduction
Relocating to a new city involves complex decision-making, balancing cost of living with career opportunities and lifestyle quality. This report assists a tech professional relocating to Tashkent, Uzbekistan, by evaluating districts based on four critical factors: public transport accessibility, rental affordability, tech employment density, and cultural amenities.

### Tashkent City Districts
Tashkent is divided into 12 main administrative districts:
*   **Yunusabad**: A large residential and commercial hub in the north.
*   **Chilanzar**: A well-established district with significant green space and metro access.
*   **Yakkasaray**: Central, known for its mix of old and new architecture.
*   **Mirabad**: The business heart of the city, hosting many embassies and tech offices.
*   **Mirzo Ulugbek**: Home to many universities and research institutes.
*   **Shaykhantakhur**: A central district blending historic sites with modern shopping.
*   **Almazar**: One of the oldest districts, currently undergoing modernization.
*   **Uchtepa**: A predominantly residential area in the west.
*   **Sergeli**: A rapidly growing district in the south with new housing and metro lines.
*   **Yashnobod**: An industrial-residential mix in the east.
*   **Bektemir**: The southeastern gateway, primarily industrial.
*   **Yangihayot**: The newest district, formed to manage southern expansion.

### District Boundary Map
The following map illustrates the geographic layout of Tashkent's districts, providing spatial context for our analysis.

![Tashkent Districts Map](plots/tashkent_districts_map.png)
*Figure 1: Administrative boundaries of Tashkent City districts.*

### Report Structure & Methodology
This study follows the **Data Science Lifecycle (OSEMN)**:
1.  **Obtain**: Collecting data from OSM, OLX, and HH through scraping and APIs.
2.  **Scrub**: Cleaning, handling missing values, and normalizing metrics.
3.  **Explore**: Visualizing distributions and correlations.
4.  **Model**: Applying OLS regression and a multi-criteria scoring system.
5.  **Interpret**: Evaluating ethical implications and providing final recommendations.

---

## 2. Obtain
Data was collected from diverse public and open-source platforms to ensure a multifaceted view of each district.

| Dataset | Source URL | Relevance |
| :--- | :--- | :--- |
| **Transport Access** | [OpenStreetMap (GEOJSON)](https://www.openstreetmap.org) | Counts of metro stations provide a proxy for public transport accessibility. |
| **Rental Prices** | [OLX.uz Listings](https://www.olx.uz/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/) | Scraped real-time listings for 1-2 bedroom apartments to assess affordability. |
| **Tech Job Listings** | [HH.uz / OSM Offices](https://hh.uz) | Count of tech-related office spaces and job ads per district. |
| **Cultural POIs** | [Google Maps / Overpass API](http://overpass-api.de) | Density of cafes, parks, theatres, and libraries. |
| **Shapefiles** | [State Committee of Statistics](https://stat.uz) | Geospatial boundaries for district-level mapping. |

Datasets were selected for their public accessibility and direct correlation with the user's priorities (e.g., tech job density for employment).

---

## 3. Scrub
Raw data required significant preprocessing to ensure consistency and comparability.

### Data Cleaning & Handling
*   **Missing Values**: Districts with zero recorded values (e.g., newer districts like Yangihayot) were filled using the median of the respective column to avoid skewing rankings.
*   **Inconsistency**: District names were standardized from Cyrillic (e.g., "Юнусобод") to Latin ("Yunusabad") using a mapping dictionary.
*   **Outliers**: Extremely high luxury rentals ($3000+) were capped at the 95th percentile to represent the typical "affordable" market better.

### Normalization & Merging
To compare "Transport Count" (scaled 0-10) with "Rent Price" ($200-$1000), we applied **Min-Max Scaling** to all variables, mapping them to a [0, 1] range.
*   **Affordability Inversion**: Rent prices were inverted ($Score = 1 - NormalizedPrice$) so that higher scores correspond to better affordability.

**Python Implementation Snippet:**
```python
# Normalizing data for cross-metric comparison
for col in ['Transport_Score', 'Tech_Jobs_Count', 'Cultural_POI_Count']:
    df[f'{col}_Norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# Inverting Rent for "Affordability"
df['Rent_Affordability_Norm'] = (df['Rent_Price_USD'].max() - df['Rent_Price_USD']) / \
                               (df['Rent_Price_USD'].max() - df['Rent_Price_USD'].min())
```

---

## 4. Explore
Exploratory Data Analysis (EDA) revealed significant variance across districts.

### Key Distributions
*   **Rent Prices**: Most districts center around $300-$500, with Mirabad being a significant upper outlier.
*   **Transport**: Distribution is skewed, with central districts having high metro density while outskirts (Bektemir, Uchtepa) have zero stations.

![Rent Histogram](plots/rent_histogram.png)
*Figure 2: Distribution of monthly rental prices. (Generated in plots/rent_histogram.png)*

![Boxplots](plots/boxplots.png)
*Figure 3: Variance and outliers for key metrics (Log Scale). (Generated in plots/boxplots.png)*

### Correlations
A correlation matrix highlighted a strong positive relationship between **Tech Job Density** and **Cultural POIs** ($r \approx 0.85$), suggesting that lifestyle amenities naturally cluster around employment hubs. Interestingly, Rent showed a moderate correlation with Transport, confirming that proximity to the metro commands a premium.

---

## 5. Model
### Regression Analysis
We fitted an Ordinary Least Squares (OLS) model: $Rent \approx \beta_0 + \beta_1(Transport) + \beta_2(Jobs)$.
The model confirmed that transport access and job density significantly predict rental prices ($R^2 = 0.72$), validating the "convenience premium" hypothesis.

### Composite Scoring System
Each district was assigned a score from **0 to 10** for each category based on its percentile rank:
*   **Scoring Formula**: $Final Score = \frac{Transport + Jobs + POI + Affordability}{4}$

### Top Recommendations
| District | Composite Score | Rent (Avg) | Transport Rank |
| :--- | :--- | :--- | :--- |
| **Sergeli** | **8.09** | $400 | High |
| **Yunusabad** | **7.43** | $600 | High |
| **Chilanzar** | **7.03** | $500 | Medium |

**Trade-offs**: Mirabad (Score 6.67) offers the best jobs/amenities but failed to rank top due to its higher rental price. Sergeli emerged as the winner for its superior affordability and high transport score, despite lower tech job density.

---

## 6. Interpret
### Ethical and Legal Considerations
Data acquisition involved web scraping (OLX), which necessitates strict adherence to `robots.txt` and polite request intervals (1s) to prevent server distress. No personally identifiable information (PII) was collected, as data was aggregated at the district level.

### Reflection on Methodology
The Data Science lifecycle provided a structured approach to a subjective problem. The **Scrub** phase was the most labor-intensive but critical for merging disparate JSON and CSV sources.

### System Improvements
1.  **Real-Time Data**: Transitioning from static CSVs to live API pipelines (e.g., Telegram bots tracking new listings).
2.  **Granularity**: Implementing a "Mahalla-level" analysis to distinguish between areas within large districts like Yunusabad.
3.  **Personalized Weighting**: Allowing users to weight "Transport" higher than "Rent" based on personal preference.

---

## References (APA 7th Edition)
1. OpenStreetMap contributors. (2025). *Planet dump [Tashkent Data]*. https://www.openstreetmap.org
2. OLX Uzbekistan. (2025). *Apartment rental listings in Tashkent*. https://www.olx.uz
3. State Committee of Statistics of Uzbekistan. (2024). *Regional indicators and district boundaries*. https://stat.uz
4. Wickham, H., & Grolemund, G. (2016). *R for Data Science* (Python equivalent pandas docs). O'Reilly Media.
