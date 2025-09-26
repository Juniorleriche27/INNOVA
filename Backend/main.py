from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

# Routers existants
from routers import domain, project, contributor, technology
# ➕ Chat-LAYA
from routers import chatlaya

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="INNOVA+ API",
    description="Backend de la plateforme INNOVA+",
    version="1.0.0",
)

# -------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://innova-qr1i.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,
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
#   POST /chatlaya/ask
#   GET  /chatlaya/search
#   POST /chatlaya/ingest
app.include_router(chatlaya.router, prefix="/chatlaya", tags=["chat-laya"])

# -------- Test Qdrant --------
from qdrant_client import QdrantClient

@app.get("/qdrant-test")
def qdrant_test():
    """Test simple de connexion à Qdrant (instanciation locale)."""
    try:
        qdrant_url = os.getenv("QDRANT_URL")
        if not qdrant_url:
            return {"error": "QDRANT_URL manquant"}
        client = QdrantClient(url=qdrant_url)
        info = client.get_collections()
        return {"collections": [c.name for c in info.collections]}
    except Exception as e:
        return {"error": str(e)}
