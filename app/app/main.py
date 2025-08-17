from fastapi import FastAPI
from app.schema import QuarterlyRiskInput
from app.risk_logic import assess_quarterly_risk

app = FastAPI()

@app.post("/quarterly-risk")
def quarterly_risk(data: QuarterlyRiskInput):
    return assess_quarterly_risk(data)
