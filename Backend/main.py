from dotenv import load_dotenv
load_dotenv()  # charge les variables depuis .env (utile en local et pour Render)

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

# Routers existants
from routers import domain, project, contributor, technology
# ➕ Chat-LAYA
from routers import chatlaya

# Swagger gère Bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="INNOVA+ API",
    description="Backend de la plateforme INNOVA+",
    version="1.0.0",
)

# -------- CORS ----------
# On garde tes origines actuelles ET on permet d’ajouter par variable d’env
default_origins = {
    "https://innova-qr1i.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

env_origin = os.getenv("CORS_ALLOW_ORIGIN", "").strip()
if env_origin:
    default_origins.add(env_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(default_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------

@app.get("/")
def root():
    return {"message": "Bienvenue sur INNOVA+"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# -------- Routers existants --------
app.include_router(project.router, prefix="/projects", tags=["projects"])
app.include_router(domain.router, prefix="/domains", tags=["domains"])
app.include_router(contributor.router, prefix="/contributors", tags=["contributors"])
app.include_router(technology.router, prefix="/technologies", tags=["technologies"])

# -------- Chat-LAYA --------
# Endpoints attendus:
#   POST /chatlaya/chat
#   POST /chatlaya/ingest
#   POST /chatlaya/feedback
app.include_router(chatlaya.router, prefix="/chatlaya", tags=["chat-laya"])


# -------- Test Qdrant --------
from services.rag_service import client

@app.get("/qdrant-test")
def qdrant_test():
    """
    Test de connexion à Qdrant Cloud.
    """
    try:
        info = client.get_collections()
        return {"collections": [c.name for c in info.collections]}
    except Exception as e:
        return {"error": str(e)}
