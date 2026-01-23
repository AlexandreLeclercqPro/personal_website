#!/bin/bash

# Charger les variables depuis .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Configuration
DOMAIN="${DOMAIN}"
EMAIL="${LETSENCRYPT_EMAIL:-}"  # Défini dans .env ou docker-compose
STAGING="${LETSENCRYPT_STAGING:-0}"  # 1 pour tester, 0 pour production
DATA_PATH="./certbot"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Vérifier si un email est fourni
if [ -z "$EMAIL" ]; then
    log_error "LETSENCRYPT_EMAIL non défini. Ajoutez-le dans votre fichier .env"
    exit 1
fi

# Créer les répertoires nécessaires
mkdir -p "$DATA_PATH/conf/live/$DOMAIN"
mkdir -p "$DATA_PATH/www"

# Télécharger les fichiers de configuration SSL recommandés si absents
if [ ! -f "$DATA_PATH/conf/options-ssl-nginx.conf" ]; then
    log_info "Téléchargement de options-ssl-nginx.conf..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
fi

if [ ! -f "$DATA_PATH/conf/ssl-dhparams.pem" ]; then
    log_info "Téléchargement de ssl-dhparams.pem..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"
fi

# Vérifier si des certificats valides existent déjà
check_existing_certs() {
    if [ -f "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" ]; then
        # Vérifier si c'est un vrai certificat Let's Encrypt (pas auto-signé)
        ISSUER=$(openssl x509 -in "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" -noout -issuer 2>/dev/null | grep -i "let's encrypt\|R3\|R10\|R11\|E5\|E6")
        if [ -n "$ISSUER" ]; then
            # Vérifier si le certificat est encore valide (plus de 7 jours)
            EXPIRY=$(openssl x509 -in "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" -noout -enddate 2>/dev/null | cut -d= -f2)
            EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null)
            NOW_EPOCH=$(date +%s)
            DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

            if [ "$DAYS_LEFT" -gt 7 ]; then
                log_info "Certificat Let's Encrypt valide trouvé (expire dans $DAYS_LEFT jours)"
                return 0
            fi
        fi
    fi
    return 1
}

# Si des certificats valides existent, ne rien faire
if check_existing_certs; then
    log_info "Certificats déjà valides, démarrage normal..."
    exit 0
fi

log_info "Création de certificats temporaires pour démarrer Nginx..."

# Créer des certificats auto-signés temporaires
openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout "$DATA_PATH/conf/live/$DOMAIN/privkey.pem" \
    -out "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=localhost" 2>/dev/null

log_info "Démarrage de Nginx avec certificats temporaires..."
docker compose up -d nginx

log_info "Attente que Nginx soit prêt..."
sleep 5

# Vérifier que nginx répond
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost/.well-known/acme-challenge/ | grep -q "403\|404"; then
    log_error "Nginx ne répond pas correctement sur le port 80"
    docker compose logs nginx
    exit 1
fi

log_info "Demande de certificat Let's Encrypt pour $DOMAIN..."

# Options de staging pour les tests
STAGING_ARG=""
if [ "$STAGING" = "1" ]; then
    STAGING_ARG="--staging"
    log_warn "Mode STAGING activé - certificats de test uniquement"
fi

# Demander le certificat via certbot
docker compose run --rm certbot certonly --webroot \
    -w /var/www/certbot \
    $STAGING_ARG \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d "$DOMAIN"

# Vérifier si la demande a réussi
if [ $? -eq 0 ]; then
    log_info "Certificat obtenu avec succès !"
    log_info "Rechargement de Nginx..."
    docker compose exec nginx nginx -s reload
    log_info "Configuration HTTPS terminée !"
else
    log_error "Échec de l'obtention du certificat."
    log_error "Vérifiez que :"
    log_error "  1. Le domaine $DOMAIN pointe vers ce serveur"
    log_error "  2. Le port 80 est accessible depuis Internet"
    log_error "  3. Aucun pare-feu ne bloque les requêtes"
    exit 1
fi
