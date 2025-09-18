from dotenv import load_dotenv
load_dotenv()  # charge les variables depuis .env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import domain, project, contributor, technology

app = FastAPI(
    title="INNOVA+ API",
    description="Backend de la plateforme INNOVA+",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://innova-qr1i.vercel.app",     # Front Vercel
        "http://localhost:3000",              # Dev local
        "https://innova-1-v3ab.onrender.com", # Remplace par ton URL Render exacte si différente
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bienvenue sur INNOVA+"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# Routes
app.include_router(project.router, prefix="/projects", tags=["projects"])
app.include_router(domain.router, prefix="/domains", tags=["domains"])
app.include_router(contributor.router, prefix="/contributors", tags=["contributors"])
app.include_router(technology.router, prefix="/technologies", tags=["technologies"])
