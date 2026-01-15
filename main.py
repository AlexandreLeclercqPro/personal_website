from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="CV en ligne", description="Mon CV professionnel")

# Créer les dossiers s'ils n'existent pas
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# Monter les fichiers statiques (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des templates Jinja2
templates = Jinja2Templates(directory="templates")

# Données du CV (à personnaliser)
cv_data = {
    "nom": "Votre Nom",
    "titre": "Développeur Full Stack",
    "email": "votre.email@example.com",
    "telephone": "+33 6 12 34 56 78",
    "linkedin": "https://linkedin.com/in/votre-profil",
    "github": "https://github.com/votre-compte",
    "presentation": "Développeur passionné avec X années d'expérience dans le développement web et la création d'applications performantes.",
    "experiences": [
        {
            "poste": "Développeur Full Stack",
            "entreprise": "Entreprise ABC",
            "periode": "2022 - Présent",
            "description": "Développement d'applications web avec Python, FastAPI et React. Mise en place d'architectures scalables et optimisation des performances."
        },
        {
            "poste": "Développeur Backend",
            "entreprise": "Startup XYZ",
            "periode": "2020 - 2022",
            "description": "Conception et développement d'APIs RESTful. Gestion de bases de données et intégration de services tiers."
        }
    ],
    "formations": [
        {
            "diplome": "Master Informatique",
            "etablissement": "Université de Paris",
            "annee": "2020"
        },
        {
            "diplome": "Licence Informatique",
            "etablissement": "Université de Lyon",
            "annee": "2018"
        }
    ],
    "competences": {
        "Langages": ["Python", "JavaScript", "TypeScript", "SQL"],
        "Frameworks": ["FastAPI", "Django", "React", "Vue.js"],
        "Outils": ["Docker", "Git", "PostgreSQL", "Redis"],
        "Autres": ["CI/CD", "Tests unitaires", "Agile/Scrum"]
    },
    "projets": [
        {
            "nom": "Projet Portfolio",
            "description": "Application de gestion de portfolio avec authentification et dashboard.",
            "technologies": ["FastAPI", "React", "PostgreSQL"],
            "lien": "https://github.com/votre-compte/projet"
        },
        {
            "nom": "API de Gestion",
            "description": "API RESTful complète pour la gestion de ressources avec documentation Swagger.",
            "technologies": ["Python", "FastAPI", "Docker"],
            "lien": "https://github.com/votre-compte/api"
        }
    ]
}

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