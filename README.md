# Tashkent Districts Data Science Project

This project evaluates different districts in Tashkent to help tech professionals find the best place to live based on various factors such as rent, proximity to points of interest (POIs), job opportunities, and transport accessibility.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [Git](https://git-scm.com/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd client-data-science
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have `geopandas`, `pandas`, `requests`, `beautifulsoup4`, `matplotlib`, `seaborn`, and `statsmodels` installed.)*

## 🛠 Usage

The project follows a modular pipeline. You can run the entire process—from data acquisition to modeling—using the main entry point:

```bash
python main.py
```

### Pipeline Steps:
1. **Obtain**: Scrapes rent data, metro stations, and POIs from various sources.
2. **Scrub**: Cleans and merges datasets into a unified structure.
3. **Explore**: Generates visualizations and exploratory analysis in the `plots/` directory.
4. **Model**: Applies a scoring model to rank districts and saves results to `final_rankings.csv`.

## 📂 Project Structure

- `src/`: Source code for each stage of the data science lifecycle.
  - `data/`: Modules for obtaining (`obtain.py`) and cleaning (`scrub.py`) data.
  - `analysis/`: Modules for exploration (`explore.py`) and modeling (`model.py`).
- `data/`: Raw and processed data files.
- `plots/`: Generated visualizations.
- `main.py`: The main script to execute the full pipeline.
- `report.md` & `academic_report.md`: Detailed findings and project documentation.

## 📊 Outputs

- **`final_rankings.csv`**: A list of districts ranked by their suitability score.
- **`model_summary.txt`**: Statistical summary of the modeling process.
- **`plots/`**: Maps and charts showing district comparisons.
s
