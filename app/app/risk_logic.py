import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from app.schema import QuarterlyRiskInput

def assess_quarterly_risk(data: QuarterlyRiskInput):
    df = pd.DataFrame({
        'quarter': pd.PeriodIndex(data.quarters, freq='Q').to_timestamp(),
        'penalty': data.penalty_per_year,
        'late_pct': data.percent_returns_late
    }).set_index('quarter')

    penalty_model = ARIMA(df['penalty'], order=(1,1,1)).fit()
    penalty_forecast = penalty_model.forecast(steps=2)

    late_model = ARIMA(df['late_pct'], order=(1,1,1)).fit()
    late_forecast = late_model.forecast(steps=2)

    volatility_penalty = df['penalty'].pct_change().std()
    volatility_late = df['late_pct'].pct_change().std()

    risk_score = (volatility_penalty * 0.6) + (volatility_late * 0.4)
    risk_flag = risk_score > 0.25

    return {
        "penalty_forecast_next_2_quarters": penalty_forecast.tolist(),
        "late_pct_forecast_next_2_quarters": late_forecast.tolist(),
        "risk_score": round(risk_score, 3),
        "risk_flag": risk_flag
    }
