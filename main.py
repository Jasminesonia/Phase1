from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from apis.social_media import router as social_router
from apis.auth import router as auth_router
from dotenv import load_dotenv
from jwt_config import get_jwt_config

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://front-end-eta-lake.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include the router
app.include_router(auth_router, prefix="/api",tags=["Authentication"])
app.include_router(social_router, prefix="/api",tags=["post"])


@app.get("/")
async def health_check():
    return {"status": "Health_check"}
