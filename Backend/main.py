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
# Origines explicites (prod Vercel + local)
base_origins = {
    "https://innova-qr1i.vercel.app",  # domaine prod exact
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

# On autorise des origines supplémentaires via variables d'env :
# - CORS_ALLOW_ORIGIN : une seule origine
# - CORS_ORIGINS      : liste séparée par virgules
env_origin = os.getenv("CORS_ALLOW_ORIGIN", "").strip()
if env_origin:
    base_origins.add(env_origin)

env_origins_csv = os.getenv("CORS_ORIGINS", "").strip()
if env_origins_csv:
    for item in env_origins_csv.split(","):
        item = item.strip()
        if item:
            base_origins.add(item)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(base_origins),
    allow_origin_regex=r"https://.*\.vercel\.app",  # ✅ autorise toutes les previews Vercel
    allow_credentials=False,   # pas de cookies inter-origines
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------

@app.get("/")
def root():
    return {"message": "Bienvenue sur INNOVA+"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# -------- Routers existants --------
app.include_router(project.router, prefix="/projects", tags=["projects"])
app.include_router(domain.router, prefix="/domains", tags=["domains"])
app.include_router(contributor.router, prefix="/contributors", tags=["contributors"])
app.include_router(technology.router, prefix="/technologies", tags=["technologies"])

# -------- Chat-LAYA --------
# Endpoints exposés par le router :
#   POST /chatlaya/ask
#   GET  /chatlaya/search
#   POST /chatlaya/ingest
app.include_router(chatlaya.router, prefix="/chatlaya", tags=["chat-laya"])

# -------- Test Qdrant --------
# (Conserve ceci seulement si ton services/rag_service.py expose bien 'client')
from services.rag_service import client

@app.get("/qdrant-test")
def qdrant_test():
    """
    Test simple de connexion à Qdrant.
    """
    try:
        info = client.get_collections()
        return {"collections": [c.name for c in info.collections]}
    except Exception as e:
        return {"error": str(e)}
