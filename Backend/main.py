from dotenv import load_dotenv
load_dotenv()  # charge les variables depuis .env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from routers import domain, project, contributor, technology

# Swagger saura gérer Bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="INNOVA+ API",
    description="Backend de la plateforme INNOVA+",
    version="1.0.0",
)

# CORS (ajoute ton front + éventuel domaine Render si besoin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://innova-qr1i.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
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
