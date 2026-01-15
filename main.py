from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json

app = FastAPI(title="CV en ligne", description="Mon CV professionnel")

# Monter les fichiers statiques (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des templates Jinja2
templates = Jinja2Templates(directory="templates")

# Charger les données du CV depuis le fichier JSON
def load_cv_data():
    """Charge les données du CV depuis cv_data.json"""
    cv_file = Path("data/cv_data.json")
    if cv_file.exists():
        with open(cv_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Retourne des données par défaut si le fichier n'existe pas
        return {
            "nom": "Votre Nom",
            "titre": "Développeur Full Stack",
            "email": "votre.email@example.com",
            "telephone": "+33 6 12 34 56 78",
            "linkedin": "https://linkedin.com/in/votre-profil",
            "github": "https://github.com/votre-compte",
            "presentation": "Développeur passionné avec X années d'expérience.",
            "experiences": [],
            "formations": [],
            "competences": {},
            "projets": []
        }

# Charger les données au démarrage
cv_data = load_cv_data()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Page d'accueil avec le CV"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "cv": cv_data}
    )

@app.get("/api/cv")
async def get_cv():
    """API endpoint pour récupérer les données du CV en JSON"""
    return cv_data

@app.get("/api/contact")
async def get_contact():
    """API endpoint pour les informations de contact"""
    return {
        "nom": cv_data["nom"],
        "email": cv_data["email"],
        "telephone": cv_data["telephone"],
        "linkedin": cv_data["linkedin"],
        "github": cv_data["github"]
    }

@app.get("/api/reload")
async def reload_cv():
    """Endpoint pour recharger les données du CV"""
    global cv_data
    cv_data = load_cv_data()
    return {"message": "Données rechargées avec succès", "cv": cv_data}