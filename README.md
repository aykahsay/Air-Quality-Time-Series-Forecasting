
# 🌍 Air Quality Time Series Forecasting (Nairobi CMR)

## 📌 Project Overview

This project aims to analyze and forecast PM2.5 air pollution levels in **Nairobi CMR** using time series techniques. It combines data wrangling, visualization, and multiple forecasting models (Linear Regression, Autoregressive, ARIMA, SARIMA).

---

## 📁 Project Structure

```
📦 AQI-Forecasting/
├── Data/
│   └── *.csv                      # Raw AQI data files
├── AQI_data_Nairobi_CMR.csv      # Cleaned and filtered data
├── src/
│   ├── combine_filter.py         # Combine and filter CSVs by location
│   └── wrangle_aqi.py            # Wrangle and resample data
├── notebooks/
│   └── AQI_Analysis.ipynb        # Main analysis and modeling notebook
└── README.md                     # Project overview and documentation
```

---

## 🔧 Setup Instructions

1. Clone this repo:

```bash
git clone https://github.com/your_username/AQI-Forecasting.git
cd AQI-Forecasting
```

2. Install dependencies:

```bash
pip install pandas matplotlib plotly scikit-learn statsmodels
```

3. Place your raw `.csv` AQI files in the `Data/` folder.

---

## 🧹 Data Preprocessing

* **combine\_and\_filter\_by\_location**:

  * Merges all `.csv` files from a folder.
  * Filters by location (`location_name == 'Nairobi CMR'`).
  * Saves combined data as `AQI_data_Nairobi_CMR.csv`.

* **wrangle\_aqi\_file**:

  * Filters for PM2.5 readings only.
  * Converts to hourly timestamps.
  * Aggregates and forward-fills missing values.

---

## 📊 Exploratory Data Analysis

* **Visualizations**:

  * Boxplot of PM2.5 distribution.
  * Hourly time series line plots.
  * Weekly rolling averages.
  * Lag plots & autocorrelation (ACF & PACF).

* **Observations**:

  * PM2.5 values show strong autocorrelation with lag = 1.
  * Some missing values handled via `ffill`.

---

## 🔁 Modeling Techniques

### ✅ Linear Regression

* Feature: `pm25.L1` (lag 1)
* MAE (Train): 3.57
* MAE (Test): 3.55

### 🔁 Autoregressive Model (AR)

* AR(26)
* MAE (Train): 3.29
* MAE (Test): 7.43

### 🔄 Walk-Forward Validation (AR)

* Dynamic AR(26) retrained at each step.
* MAE (Test): 3.46

### 📈 ARIMA Model

* Explored (p, d, q) from (0–24, 0, 0–2)
* Best: ARIMA(24, 0, 1) → MAE: 3.26

### 📆 SARIMA Model

* Order: (1, 1, 1), Seasonal: (1, 1, 1, 168)
* Forecasted PM2.5 for the next week (168 hours).

---

## 📉 Model Evaluation

* **Metrics**: Mean Absolute Error (MAE)
* **Baseline MAE**: 8.32 (mean prediction)
* **Best Model**: ARIMA(24, 0, 1) — MAE: 3.26

---

## 📈 Forecast Visualization

* Plotly interactive forecast line plots.
* Confidence intervals for SARIMA forecasts.

---

## 🧪 Stationarity Testing

* **ADF Test**: p-value < 0.05 ⇒ Reject H₀ ⇒ Series is stationary.

---

## 🛠 Future Improvements

* Incorporate exogenous features (temperature, humidity).
* Try LSTM or Prophet for advanced time series modeling.
* Automate retraining with updated AQI data.

---

## 📄 License

MIT License © 2025

---
