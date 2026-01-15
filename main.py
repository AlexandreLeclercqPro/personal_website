from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from PIL import Image
import os

app = FastAPI(title="CV en ligne", description="Mon CV professionnel")

CV_PATH = "data/cv.pdf"

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

def resize_profile_photo(photo_path: str, size: tuple = (300, 300)):
    """Redimensionne automatiquement la photo de profil"""
    if not photo_path:
        return
    
    # Convertir le chemin web en chemin système
    if photo_path.startswith("/static/"):
        system_path = Path("static") / photo_path.replace("/static/", "")
    else:
        system_path = Path(photo_path)
    
    if not system_path.exists():
        print(f"⚠️  Photo introuvable: {system_path}")
        return
    
    try:
        # Ouvrir l'image
        img = Image.open(system_path)
        
        # Vérifier si l'image doit être redimensionnée
        if img.size != size:
            # Créer une image carrée en cropant si nécessaire
            width, height = img.size
            min_dimension = min(width, height)
            
            # Crop au centre pour avoir un carré
            left = (width - min_dimension) // 2
            top = (height - min_dimension) // 2
            right = left + min_dimension
            bottom = top + min_dimension
            
            img_cropped = img.crop((left, top, right, bottom))
            
            # Redimensionner à la taille souhaitée
            img_resized = img_cropped.resize(size, Image.Resampling.LANCZOS)
            
            # Sauvegarder l'image redimensionnée
            img_resized.save(system_path, quality=95, optimize=True)
            print(f"✓ Photo redimensionnée: {system_path} ({size[0]}x{size[1]}px)")
    
    except Exception as e:
        print(f"❌ Erreur lors du redimensionnement de la photo: {e}")

# Charger les données au démarrage
cv_data = load_cv_data()

# Redimensionner la photo de profil si elle existe
if "photo" in cv_data:
    resize_profile_photo(cv_data["photo"])

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
    
    # Redimensionner la photo si nécessaire
    if "photo" in cv_data:
        resize_profile_photo(cv_data["photo"])
    
    return {"message": "Données rechargées avec succès", "cv": cv_data}

@app.get("/download-cv")
def download_cv():
    if not os.path.exists(CV_PATH):
        return {"error": "CV introuvable"}
    return FileResponse(
        path=CV_PATH,
        filename="Mon_CV.pdf",
        media_type="application/pdf"
    )

