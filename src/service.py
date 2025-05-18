import bentoml
from bentoml.io import JSON
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from datetime import datetime, timedelta
import pandas as pd
from starlette.exceptions import HTTPException

JWT_SECRET_KEY = "your_secret_key"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600

USERS = {
    "admin": "password"
}

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/predict":
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.lower().startswith("bearer "):
                return JSONResponse(status_code=401, content={"detail": "Missing token"})
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                exp = payload.get("exp")
                if exp and datetime.utcnow().timestamp() > exp:
                    return JSONResponse(status_code=401, content={"detail": "Token expired"})
                request.state.user = payload.get("username")
            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token expired"})
            except Exception:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        response = await call_next(request)
        return response

# Pydantic model for input validation
class PredictInput(BaseModel):
    GRE_Score: float
    TOEFL_Score: float
    University_Rating: float
    SOP: float
    LOR: float
    CGPA: float
    Research: int

model_ref = bentoml.sklearn.get("admissions_model:latest")
model_runner = model_ref.to_runner()
svc = bentoml.Service("admissions_prediction_service", runners=[model_runner])
svc.add_asgi_middleware(JWTAuthMiddleware)

def create_jwt_token(username: str):
    expiration = datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    payload = {
        "username": username,
        "exp": expiration.timestamp()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

@svc.api(input=JSON(), output=JSON())
async def login(credentials: dict, ctx: bentoml.Context):
    username = credentials.get("username")
    password = credentials.get("password")
    if not username or not password:
        ctx.response.status_code = 401
        return {"detail": "Missing username or password"}
    if username not in USERS or USERS[username] != password:
        ctx.response.status_code = 401
        return {"detail": "Invalid credentials"}
    token = create_jwt_token(username)
    return {"token": token}

@svc.api(
    input=JSON(pydantic_model=PredictInput),
    output=JSON(),
    route="/predict"
)
async def predict(input_data: PredictInput, ctx: bentoml.Context):
    # Convert input to DataFrame for model
    df = pd.DataFrame([input_data.dict()])
    result = await model_runner.predict.async_run(df)
    user = getattr(ctx.request.state, "user", None)
    return {
        "chance_of_admit": float(result[0]),
        "user": user
    }

try:
    app = svc.asgi_app
except Exception:
    app = None