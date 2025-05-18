import bentoml
from bentoml.io import JSON
import pandas as pd
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import datetime

# JWT settings
JWT_SECRET = "your_secret_key"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600

# Load model from BentoML model store
model_ref = bentoml.sklearn.get("admissions_model:latest")
model_runner = model_ref.to_runner()

svc = bentoml.Service("admissions_prediction_service", runners=[model_runner])

security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@svc.api(input=JSON(), output=JSON())
def login(input_data: dict):
    username = input_data.get("username")
    password = input_data.get("password")
    # Simple check, replace with real user validation
    if username == "admin" and password == "password":
        payload = {
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return {"token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@svc.api(input=JSON(), output=JSON(), route="/predict")
async def predict(input_data: dict, payload=Depends(verify_jwt)):
    df = pd.DataFrame([input_data])
    result = await model_runner.predict.async_run(df)
    return {"chance_of_admit": float(result[0])}